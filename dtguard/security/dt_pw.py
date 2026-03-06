"""DT-Driven Performance Weighting (DT-PW).

Simple principle:
  - Free-rider sends global model + noise → predictions ≈ global → disagree < 2%
  - Trained client sends updated model → predictions ≠ global → disagree > 2%

Score = prediction disagreement rate with global model.
Free-rider: disagree < 2% → score = 0 → weight = 0.
Trained:    disagree > 2% → score = disagree → weight ∝ disagree.
"""

import numpy as np
import torch
from dtguard.models import evaluate_model


def dt_performance_weighting(client_models, client_weights, X_test, y_test,
                             device='cpu', n_samples=100, eval_subsample=2000,
                             global_weights=None, challenge_gen=None,
                             client_data_sizes=None, debug=False):
    """
    Score each client by prediction disagreement with global model.

    Free-rider: model ≈ global → disagree < 2% → weight = 0.
    Trained:    model ≠ global → disagree > 2% → weight ∝ disagree.
    """
    n_clients = len(client_models)
    from dtguard.models import IoTAttackNet, set_parameters

    # Subsample eval data
    if eval_subsample > 0 and len(X_test) > eval_subsample:
        X_eval, y_eval = _stratified_subsample(X_test, y_test, eval_subsample)
    else:
        X_eval, y_eval = X_test, y_test

    # Build global model
    g_model = None
    if global_weights is not None:
        first = client_models[0]
        g_model = IoTAttackNet(first.fc1.in_features, first.fc4.out_features)
        set_parameters(g_model, global_weights)

    # Generate challenge data from DT (if available)
    ch_X = None
    if challenge_gen is not None:
        try:
            ch_X, ch_y = challenge_gen.generate_challenge_set(n_samples=500, device=device)
            if len(ch_X) == 0:
                ch_X = None
        except Exception:
            ch_X = None

    # Score
    if g_model is not None:
        scores = _disagree_scoring(g_model, client_models,
                                   ch_X if ch_X is not None else None,
                                   ch_y if ch_X is not None else None,
                                   X_eval, y_eval, device, client_data_sizes, debug)
    else:
        scores = np.ones(n_clients)

    # Normalize to sum=1
    total = scores.sum()
    if total > 0:
        contribution = scores / total
    else:
        contribution = np.ones(n_clients) / n_clients

    if debug:
        print(f"\n  [DT-PW] Final weights:")
        for i in range(n_clients):
            print(f"    Client {i}: {contribution[i]:.4f}")

    return contribution


def _disagree_scoring(g_model, client_models, ch_X, ch_y,
                      val_X, val_y, device, client_data_sizes=None, debug=False):
    """
    Score = prediction disagreement rate with global model.
    If disagree < 2% → 0 (free-rider). Otherwise → disagree as score.
    """
    n_clients = len(client_models)
    scores = np.zeros(n_clients)

    # Build eval set: challenge + stratified validation
    parts_X, parts_y = [], []
    if ch_X is not None:
        parts_X.append(ch_X)
        parts_y.append(ch_y)

    # Add stratified validation sample
    val_classes = np.unique(val_y)
    counts = [(val_y == c).sum() for c in val_classes if (val_y == c).sum() > 0]
    n_per_class = min(100, min(counts)) if counts else 100
    idx = []
    for c in val_classes:
        c_idx = np.where(val_y == c)[0]
        if len(c_idx) > 0:
            chosen = np.random.choice(c_idx, min(n_per_class, len(c_idx)), replace=False)
            idx.extend(chosen)
    parts_X.append(val_X[idx])
    parts_y.append(val_y[idx])

    eval_X = np.vstack(parts_X)
    eval_y = np.concatenate(parts_y)
    eval_t = torch.FloatTensor(eval_X).to(device)
    N = len(eval_y)

    # Global predictions
    g_model.eval(); g_model.to(device)
    with torch.no_grad():
        g_preds = g_model(eval_t).argmax(1).cpu().numpy()

    if debug:
        print(f"\n  [DT-PW] Eval samples: {N}")

    # Score each client
    for i in range(n_clients):
        client_models[i].eval(); client_models[i].to(device)
        with torch.no_grad():
            c_preds = client_models[i](eval_t).argmax(1).cpu().numpy()

        disagree = (c_preds != g_preds).sum() / N

        if disagree < 0.02:
            scores[i] = 0.0  # free-rider
        else:
            scores[i] = disagree

        if debug:
            size = client_data_sizes[i] if client_data_sizes and i < len(client_data_sizes) else '?'
            status = "FREE-RIDER" if disagree < 0.02 else f"score={disagree:.4f}"
            print(f"    Client {i} ({size} samples): disagree={disagree:.4f} → {status}")

    return scores


def _stratified_subsample(X, y, n_samples):
    """Stratified subsample preserving class proportions."""
    classes, counts = np.unique(y, return_counts=True)
    total = len(y)
    indices = []
    for cls, cnt in zip(classes, counts):
        cls_idx = np.where(y == cls)[0]
        n_cls = max(1, min(int(round(n_samples * cnt / total)), len(cls_idx)))
        indices.extend(np.random.choice(cls_idx, n_cls, replace=False))
    np.random.shuffle(indices)
    return X[indices], y[indices]


def combine_dtpw_verification(dtpw_values, verification_scores):
    """
    Combine DT-PW scores with verification scores.
    Free-riders (dtpw=0) stay at 0 regardless of verification.
    """
    dtpw = np.array(dtpw_values)
    v = np.array(verification_scores)
    if v.max() > 0:
        v = v / v.max()

    combined = np.where(dtpw > 1e-6, 0.7 * dtpw + 0.3 * v, 0.0)

    total = combined.sum()
    if total > 0:
        return combined / total
    return np.ones(len(dtpw)) / len(dtpw)


# =====================================================================
# Classic Monte-Carlo Shapley (for comparison only)
# =====================================================================

def classic_shapley_values(client_models, client_weights, X_test, y_test,
                           device='cpu', n_samples=30, eval_subsample=2000):
    """Standard Monte-Carlo Shapley estimation for comparison."""
    n_clients = len(client_models)
    sv = np.zeros(n_clients)

    if eval_subsample > 0 and len(X_test) > eval_subsample:
        X_eval, y_eval = _stratified_subsample(X_test, y_test, eval_subsample)
    else:
        X_eval, y_eval = X_test, y_test

    cache = {}
    for _ in range(n_samples):
        perm = np.random.permutation(n_clients)
        prev = 0.0
        for i, cidx in enumerate(perm):
            key = tuple(sorted(perm[:i + 1]))
            if key not in cache:
                cache[key] = _evaluate_coalition(key, client_models, client_weights,
                                                 X_eval, y_eval, device)
            cur = cache[key]
            sv[cidx] += (cur - prev)
            prev = cur
    sv /= n_samples

    # Normalize
    if sv.max() > sv.min():
        centered = sv - np.median(sv)
        exp_sv = np.exp(np.clip(centered * 10.0, -50, 50))
        return exp_sv / exp_sv.sum()
    return np.ones(n_clients) / n_clients


def _evaluate_coalition(indices, client_models, client_weights, X_test, y_test, device):
    """Evaluate accuracy of a coalition of clients."""
    if len(indices) == 0:
        return 0.0
    from dtguard.fl import federated_averaging
    from dtguard.models import set_parameters, IoTAttackNet

    weights = [client_weights[i] for i in indices]
    avg_w = federated_averaging(weights)
    m = client_models[0]
    model = IoTAttackNet(m.fc1.in_features, m.fc4.out_features)
    set_parameters(model, avg_w)
    return evaluate_model(model, X_test, y_test, batch_size=512, device=device)


# Backward-compatible aliases
calculate_shapley_values = dt_performance_weighting
calculate_weighted_shapley = combine_dtpw_verification

