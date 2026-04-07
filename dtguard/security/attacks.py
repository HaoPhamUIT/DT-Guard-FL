"""Attack implementations for FL.

Faithful reimplementation of attacks from the LUP repository
(https://github.com/UNSW-Canberra-2023/LUP) adapted to work with
numpy weight arrays used in DT-Guard's FL pipeline.

Classic attacks:
  - Model Poisoning, Gradient Ascent, Byzantine, Backdoor, Label Flipping, Noise

Advanced attacks (from DT-BFL paper / LUP repo):
  - Sign-Flip  [naive.py → signflip_attack]
  - LIE         [lie.py  → little_is_enough_attack]
  - Min-Max     [max_sum.py → minmax_attack]
  - Min-Sum     [max_sum.py → minsum_attack]
  - MPAF        [MPAF.py → MPAF]
  - ByzMean     [byzMean.py → byzMean_attack]
"""

import numpy as np
from typing import List, Optional


def apply_attack(weights: List[np.ndarray], attack_type: str, scale_factor: float = 15.0,
                 all_client_weights: Optional[List[List[np.ndarray]]] = None,
                 malicious_indices: Optional[List[int]] = None) -> List[np.ndarray]:
    """
    Apply attack to model weights.

    For optimisation-based attacks (LIE, MIN_MAX, MIN_SUM, MPAF, BYZMEAN)
    ``all_client_weights`` should contain *all* clients' **trained** weights
    (before poisoning) so the attacker can compute statistics over benign
    updates.  ``malicious_indices`` tells which entries belong to attackers.

    Args:
        weights: Model parameters of the malicious client (post-training, pre-poison)
        attack_type: Type of attack string
        scale_factor: Attack strength
        all_client_weights: All clients' weights list (needed for advanced attacks)
        malicious_indices: Indices of malicious clients in all_client_weights
    Returns:
        Poisoned weights
    """
    # ---- Classic attacks (weight-space) ------------------------------------
    if attack_type == "MODEL_POISONING":
        return [w * scale_factor for w in weights]

    elif attack_type == "GRADIENT_ASCENT":
        return [-w * scale_factor for w in weights]

    elif attack_type == "BYZANTINE_ATTACK":
        poisoned = []
        for w in weights:
            strategy = np.random.choice(['random', 'opposite', 'extreme'])
            if strategy == 'random':
                poisoned.append(_randn_like(w) * np.std(w) * scale_factor * 0.5)
            elif strategy == 'opposite':
                poisoned.append(-w * (scale_factor * 0.8))
            else:
                poisoned.append(w * scale_factor + _randn_like(w) * scale_factor * 0.3)
        return poisoned

    elif attack_type == "BACKDOOR":
        poisoned = []
        for i, w in enumerate(weights):
            if i >= len(weights) - 2:
                if w.ndim == 2:
                    perturbation = np.zeros_like(w)
                    for _ in range(3):
                        direction = np.random.randn(w.shape[1])
                        direction = direction / (np.linalg.norm(direction) + 1e-10)
                        perturbation += np.outer(np.random.randn(w.shape[0]), direction)
                    poisoned.append(w + perturbation * 1.2)
                else:
                    poisoned.append(w + _randn_like(w) * 2.5)
            elif i < len(weights) // 3:
                poisoned.append(w + _randn_like(w) * 0.25)
            else:
                poisoned.append(w + _randn_like(w) * 0.02)
        return poisoned

    elif attack_type == "LABEL_FLIPPING":
        return weights

    elif attack_type == "NOISE_INJECTION":
        poisoned = []
        for i, w in enumerate(weights):
            if i % 2 == 0:
                noise = np.random.normal(0, scale_factor * 0.1, w.shape if w.ndim > 0 else (1,))
                if w.ndim == 0:
                    noise = np.array(noise.item(), dtype=w.dtype)
                poisoned.append(w + noise)
            else:
                poisoned.append(w)
        return poisoned

    # ---- Advanced attacks (faithful to LUP repo) ---------------------------

    elif attack_type == "SIGN_FLIP":
        # LUP/attacks/naive.py → signflip_attack: return [-1.0 * x for x in byz_grads]
        return [-1.0 * w for w in weights]

    elif attack_type == "LIE":
        return _lie_attack(weights, all_client_weights, malicious_indices, scale_factor)

    elif attack_type == "MIN_MAX":
        return _minmax_attack(weights, all_client_weights, malicious_indices)

    elif attack_type == "MIN_SUM":
        return _minsum_attack(weights, all_client_weights, malicious_indices)

    elif attack_type == "MPAF":
        return _mpaf_attack(weights)

    elif attack_type == "BYZMEAN":
        return _byzmean_attack(weights, all_client_weights, malicious_indices)

    else:
        return weights


# =============================================================================
# Helpers
# =============================================================================

def _randn_like(w: np.ndarray) -> np.ndarray:
    """Random normal array matching shape of w, safe for 0-d (scalar) params."""
    if w.ndim == 0:
        return np.array(np.random.randn(), dtype=w.dtype)
    return np.random.randn(*w.shape).astype(w.dtype)


def _flatten(weights: List[np.ndarray]) -> np.ndarray:
    return np.concatenate([w.flatten() for w in weights])


def _unflatten(flat: np.ndarray, shapes: List[tuple]) -> List[np.ndarray]:
    result, offset = [], 0
    for shape in shapes:
        size = int(np.prod(shape))
        result.append(flat[offset:offset + size].reshape(shape))
        offset += size
    return result


def _get_all_flat(all_client_weights, malicious_indices):
    """Return (all_flat, benign_flat, byz_flat, shapes)."""
    if all_client_weights is None:
        return None, None, None, None
    mal_set = set(malicious_indices or [])
    shapes = [w.shape for w in all_client_weights[0]]
    all_flat = np.stack([_flatten(cw) for cw in all_client_weights])
    benign_flat = np.stack([_flatten(all_client_weights[i])
                            for i in range(len(all_client_weights)) if i not in mal_set])
    byz_flat = np.stack([_flatten(all_client_weights[i])
                         for i in range(len(all_client_weights)) if i in mal_set])
    return all_flat, benign_flat, byz_flat, shapes


# =============================================================================
# LIE – A Little Is Enough  (LUP/attacks/lie.py)
#
# Original:
#   est_grads = torch.stack(byz_grads + benign_grads)
#   mu  = torch.mean(est_grads, dim=0)
#   sigma = torch.std(est_grads, dim=0)
#   z = 1.0
#   lie_grad = mu - z * sigma
#   return [lie_grad] * num_byzs
# =============================================================================

def _lie_attack(weights, all_client_weights, malicious_indices, scale_factor=10.0):
    all_flat, benign_flat, byz_flat, shapes = _get_all_flat(all_client_weights, malicious_indices)
    if all_flat is None:
        flat = _flatten(weights)
        shapes = [w.shape for w in weights]
        return _unflatten(flat - np.std(flat) * 1.0, shapes)

    # Use *all* gradients (byz + benign), matching the original
    est_grads = all_flat  # shape (N, d)
    mu = np.mean(est_grads, axis=0)
    sigma = np.std(est_grads, axis=0)
    # z scales with attack strength: z=1.0 at default scale_factor=10,
    # higher scale → larger deviation from mean → stronger attack
    z = max(1.0, scale_factor / 10.0)
    lie_grad = mu - z * sigma
    return _unflatten(lie_grad, shapes)


# =============================================================================
# Min-Max Attack  (LUP/attacks/max_sum.py → minmax_attack)
#
# Original:
#   grad_b = mean(est_grads)
#   grad_p = -1.0 * std(est_grads)
#   Binary-search gamma so that max_distance(est, grad_m) <= max_pairwise_distance(est)
#   return grad_b + gamma_succ * grad_p
# =============================================================================

def _max_distance(data, point):
    """Max L2 distance from point to any row in data."""
    return float(np.max(np.linalg.norm(data - point, axis=1)))


def _max_pairwise_distance(data):
    """Max pairwise L2 distance among rows of data."""
    n = data.shape[0]
    max_d = 0.0
    for i in range(n - 1):
        dists = np.linalg.norm(data[i + 1:] - data[i], axis=1)
        max_d = max(max_d, float(np.max(dists)))
    return max_d


def _sum_distance(data, point):
    """Sum of L2 distances from point to every row in data."""
    return float(np.sum(np.linalg.norm(data - point, axis=1)))


def _max_sum_distance(data):
    """Max sum-of-distances across all rows treated as centres."""
    n = data.shape[0]
    best = 0.0
    for i in range(n):
        s = float(np.sum(np.linalg.norm(data - data[i], axis=1)))
        best = max(best, s)
    return best


def _minmax_attack(weights, all_client_weights, malicious_indices):
    all_flat, benign_flat, byz_flat, shapes = _get_all_flat(all_client_weights, malicious_indices)
    if all_flat is None:
        return [w * 0.5 for w in weights]

    est_grads = all_flat
    grad_b = np.mean(est_grads, axis=0)
    grad_p = -1.0 * np.std(est_grads, axis=0)

    # Binary search for optimal gamma (faithful to LUP repo)
    gamma_init = 2.0
    e = 0.02
    step = gamma_init / 2.0
    gamma = gamma_init
    gamma_succ = 0.0

    max_pair_d = _max_pairwise_distance(est_grads)

    while abs(gamma_succ - gamma) > e:
        grad_m = grad_b + gamma * grad_p
        max_dist_m = _max_distance(est_grads, grad_m)
        if max_dist_m <= max_pair_d:
            gamma_succ = gamma
            gamma += step / 2.0
        else:
            gamma -= step / 2.0
        step = max(step / 2.0, 0.1)

    poisoned = grad_b + gamma_succ * grad_p
    return _unflatten(poisoned, shapes)


# =============================================================================
# Min-Sum Attack  (LUP/attacks/max_sum.py → minsum_attack)
#
# Same structure as minmax but constraint is sum_distance <= max_sum_distance
# =============================================================================

def _minsum_attack(weights, all_client_weights, malicious_indices):
    all_flat, benign_flat, byz_flat, shapes = _get_all_flat(all_client_weights, malicious_indices)
    if all_flat is None:
        return [w * 0.3 for w in weights]

    est_grads = all_flat
    grad_b = np.mean(est_grads, axis=0)
    grad_p = -1.0 * np.std(est_grads, axis=0)

    gamma_init = 2.0
    e = 0.02
    step = gamma_init / 2.0
    gamma = gamma_init
    gamma_succ = 0.0

    max_sum_d = _max_sum_distance(est_grads)

    while abs(gamma_succ - gamma) > e:
        grad_m = grad_b + gamma * grad_p
        sum_dist_m = _sum_distance(est_grads, grad_m)
        if sum_dist_m <= max_sum_d:
            gamma_succ = gamma
            gamma += step / 2.0
        else:
            gamma -= step / 2.0
        step = max(step / 2.0, 0.1)

    poisoned = grad_b + gamma_succ * grad_p
    return _unflatten(poisoned, shapes)


# =============================================================================
# MPAF – Model Poisoning Attack on FL  (LUP/attacks/MPAF.py)
#
# Original:
#   mp_lambda = 10.0
#   w_base = randn_like(byz_grad)
#   tmp = (byz_grad - w_base) * mp_lambda
# =============================================================================

def _mpaf_attack(weights):
    mp_lambda = 10.0
    poisoned = []
    for w in weights:
        w_base = _randn_like(w)
        tmp = (w - w_base) * mp_lambda
        poisoned.append(tmp)
    return poisoned


# =============================================================================
# ByzMean  (LUP/attacks/byzMean.py)
#
# Original:
#   mu = mean(all); sigma = std(all); z=0.5
#   byz_grad = mu - z * sigma
# =============================================================================

def _byzmean_attack(weights, all_client_weights, malicious_indices):
    all_flat, benign_flat, byz_flat, shapes = _get_all_flat(all_client_weights, malicious_indices)
    if all_flat is None:
        flat = _flatten(weights)
        shapes = [w.shape for w in weights]
        return _unflatten(-flat * 0.5, shapes)

    est_grads = all_flat
    mu = np.mean(est_grads, axis=0)
    sigma = np.std(est_grads, axis=0)
    z = 0.5
    byz_grad = mu - z * sigma
    return _unflatten(byz_grad, shapes)
