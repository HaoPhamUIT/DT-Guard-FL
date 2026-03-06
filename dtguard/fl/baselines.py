"""Baseline defense mechanisms for comparison.

Faithful reimplementations from the LUP repository
(https://github.com/UNSW-Canberra-2023/LUP) adapted for numpy weight arrays:
  - LUP (Local Updates Purify) [aggregators/LUP.py]
  - ClipCluster [aggregators/Clippedclustering.py]
  - SignGuard [aggregators/signguard.py]

Plus PoC (Proof of Contribution) from the PPSG paper
[Zhang et al., IEEE Trans. Smart Grid 2025].
"""

import numpy as np
from typing import List, Optional
from scipy.stats import kurtosis as scipy_kurtosis, skew as scipy_skew
from sklearn.cluster import AgglomerativeClustering, MeanShift, estimate_bandwidth


# =============================================================================
# Classic baselines (unchanged)
# =============================================================================

def krum_aggregation(weights_list: List[List[np.ndarray]], f: int = 1) -> tuple:
    """
    Krum: Select the most representative model.
    """
    n = len(weights_list)
    if n <= 2 * f:
        avg_weights, _ = federated_averaging(weights_list)
        return avg_weights, []

    flattened = [np.concatenate([w.flatten() for w in weights]) for weights in weights_list]

    scores = []
    for i in range(n):
        distances = []
        for j in range(n):
            if i != j:
                dist = np.linalg.norm(flattened[i] - flattened[j])
                distances.append(dist)
        distances.sort()
        score = sum(distances[:n - f - 2])
        scores.append(score)

    selected_idx = np.argmin(scores)

    median_score = np.median(scores)
    threshold = median_score * 2.0
    rejected = [i for i, s in enumerate(scores) if s > threshold]

    return weights_list[selected_idx], rejected


def multi_krum_aggregation(weights_list: List[List[np.ndarray]], f: int = 1, m: int = 2) -> tuple:
    """
    Multi-Krum: Select m representative models and average them.
    """
    n = len(weights_list)
    if n == 0:
        return [], []
    if n <= 2 * f + 2 or m <= 1:
        return krum_aggregation(weights_list, f=f)

    flattened = [np.concatenate([w.flatten() for w in weights]) for weights in weights_list]

    scores = []
    for i in range(n):
        distances = []
        for j in range(n):
            if i != j:
                distances.append(np.linalg.norm(flattened[i] - flattened[j]))
        distances.sort()
        scores.append(sum(distances[: n - f - 2]))

    ranked = np.argsort(scores)
    selected = ranked[: min(m, n)].tolist()
    rejected = [i for i in range(n) if i not in selected]

    aggregated = []
    for layer_idx in range(len(weights_list[0])):
        layer_weights = np.array([weights_list[i][layer_idx] for i in selected])
        aggregated.append(np.mean(layer_weights, axis=0))

    return aggregated, rejected


def median_aggregation(weights_list: List[List[np.ndarray]]) -> tuple:
    """
    Coordinate-wise median aggregation.
    """
    if not weights_list:
        return [], []

    flattened = [np.concatenate([w.flatten() for w in weights]) for weights in weights_list]
    median_flat = np.median(flattened, axis=0)

    distances = [np.linalg.norm(f - median_flat) for f in flattened]
    threshold = np.median(distances) * 2.5
    rejected = [i for i, d in enumerate(distances) if d > threshold]

    aggregated = []
    for layer_idx in range(len(weights_list[0])):
        layer_weights = np.array([w[layer_idx] for w in weights_list])
        aggregated.append(np.median(layer_weights, axis=0))

    return aggregated, rejected


def trimmed_mean_aggregation(weights_list: List[List[np.ndarray]], trim_ratio: float = 0.1) -> tuple:
    """
    Trimmed mean: Remove top and bottom values before averaging.
    """
    if not weights_list:
        return [], []

    n = len(weights_list)
    trim_count = max(1, int(n * trim_ratio))

    norms = [np.linalg.norm(np.concatenate([w.flatten() for w in weights])) for weights in weights_list]
    sorted_indices = np.argsort(norms)
    rejected = list(sorted_indices[-trim_count:])

    aggregated = []
    for layer_idx in range(len(weights_list[0])):
        layer_weights = np.array([w[layer_idx] for w in weights_list])
        sorted_weights = np.sort(layer_weights, axis=0)
        if trim_count > 0:
            trimmed = sorted_weights[trim_count:-trim_count]
        else:
            trimmed = sorted_weights
        aggregated.append(np.mean(trimmed, axis=0))

    return aggregated, rejected


def federated_averaging(weights_list: List[List[np.ndarray]]) -> tuple:
    """Standard FedAvg."""
    if not weights_list:
        return [], []

    averaged = []
    for layer_idx in range(len(weights_list[0])):
        layer_weights = [w[layer_idx] for w in weights_list]
        averaged.append(np.mean(layer_weights, axis=0))

    return averaged, []


# =============================================================================
# LUP – Local Updates Purify
# Faithful to LUP/aggregators/LUP.py
#
# Two-stage filtering:
#   Stage 1 – MAD-based norm bounding: keep clients whose L2 norm
#             is within [median − MAD, median + MAD].
#             Then apply "genuine criterion" (trust score, kurtosis,
#             distance similarity, deviation-from-global) to decide
#             which of the two sets (inside/outside MAD) is honest.
#   Stage 2 – Agglomerative Clustering on statistical features of the
#             remaining set → pick the genuine cluster using the same
#             criterion.
#   Final – Norm-clip the selected gradients, then average.
# =============================================================================

def lup_aggregation(weights_list: List[List[np.ndarray]],
                    global_weights: Optional[List[np.ndarray]] = None,
                    trust_scores: Optional[np.ndarray] = None) -> tuple:
    """
    LUP aggregation faithful to the original.

    Args:
        weights_list: list of per-client weight arrays
        global_weights: previous-round global weights (used as ``previous_grads``)
        trust_scores: cumulative score_matrix_client (n_clients, 1)
    Returns:
        (aggregated_weights, rejected_indices)
    """
    n = len(weights_list)
    if not weights_list:
        return [], []
    if n <= 2:
        return federated_averaging(weights_list)

    # Flatten
    flattened = np.stack([np.concatenate([w.flatten() for w in cw]) for cw in weights_list])
    flattened = np.nan_to_num(flattened, nan=0.0)

    if trust_scores is None:
        trust_scores = np.zeros((n, 1))

    # previous_grads (global model from last round)
    if global_weights is not None:
        prev_flat = np.concatenate([w.flatten() for w in global_weights])
        prev_flat = np.nan_to_num(prev_flat, nan=0.0)
    else:
        prev_flat = np.zeros(flattened.shape[1])

    # ---------- Stage 1: MAD-based norm bounding ----------
    grad_l2norm = np.linalg.norm(flattened, axis=1)
    median_population = np.median(grad_l2norm)
    deviations = np.abs(grad_l2norm - median_population)
    scaling_factor = np.median(deviations)

    upper_bound = median_population + scaling_factor
    lower_bound = median_population - scaling_factor

    filtered_indices = np.where((grad_l2norm >= lower_bound) & (grad_l2norm <= upper_bound))[0].tolist()
    filtered_indices_other = [i for i in range(n) if i not in filtered_indices]

    # Compute per-client features needed for genuine criterion
    # Pairwise distance → keep top-half sum (like LUP repo)
    half = max(1, n // 2)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dist_matrix[i, j] = np.linalg.norm(flattened[i] - flattened[j])
    dist_sorted = np.sort(dist_matrix, axis=1)
    dist_score = dist_sorted[:, :half].sum(axis=1)  # grads_sim

    # Per-client std (used as "kurtosis" in original code: kurt_all[i,0] = np.std)
    kurt_all = np.array([np.std(flattened[i]) for i in range(n)])

    # Per-client deviation from global model
    dev_all = np.array([np.mean(np.abs(flattened[i] - prev_flat)) for i in range(n)])

    # ---- Genuine criterion for Stage 1 ----
    if filtered_indices_other and filtered_indices:
        # Compare the two sets
        grad_sim_v1 = np.mean(dist_score[filtered_indices])
        grad_sim_v2 = np.mean(dist_score[filtered_indices_other]) if filtered_indices_other else 0
        kurt_1 = np.mean(kurt_all[filtered_indices])
        kurt_2 = np.mean(kurt_all[filtered_indices_other]) if filtered_indices_other else 0
        dev_1_v = np.mean(dev_all[filtered_indices])
        dev_2_v = np.mean(dev_all[filtered_indices_other]) if filtered_indices_other else float('inf')
        ts_1 = np.sum(trust_scores[filtered_indices])
        ts_2 = np.sum(trust_scores[filtered_indices_other]) if filtered_indices_other else 0

        if ts_2 >= ts_1 and filtered_indices_other:
            # Check genuine criterion (matching LUP repo conditions)
            if ((grad_sim_v2 > grad_sim_v1 and kurt_2 > kurt_1 and dev_2_v < dev_1_v) or
                (dev_2_v < dev_1_v and grad_sim_v2 > grad_sim_v1 and kurt_2 > kurt_1) or
                (grad_sim_v2 < grad_sim_v1 and dev_2_v < dev_1_v) or
                (grad_sim_v2 > grad_sim_v1 and dev_2_v < dev_1_v and kurt_2 > kurt_1)):
                filtered_indices = filtered_indices_other

    if not filtered_indices:
        filtered_indices = list(range(n))

    # ---------- Stage 2: Agglomerative Clustering ----------
    # Build feature vectors for filtered clients
    features_list = []
    for idx in filtered_indices:
        vec = flattened[idx]
        positive_count = np.sum(vec > 0)
        negative_count = np.sum(vec < 0)
        zero_count = np.sum(vec == 0)
        kurt = scipy_kurtosis(vec, fisher=True)
        skewness = scipy_skew(vec)
        absolute_deviation = np.mean(np.abs(vec - prev_flat))
        norm_v = np.linalg.norm(vec)
        features_list.append([
            positive_count, negative_count, zero_count,
            kurt, skewness, absolute_deviation, norm_v
        ])

    features_arr = np.array(features_list, dtype=np.float64)
    features_arr = np.nan_to_num(features_arr, nan=0.0, posinf=1.0, neginf=-1.0)

    if len(features_arr) >= 2:
        agg_clustering = AgglomerativeClustering(n_clusters=2)
        labels = agg_clustering.fit_predict(features_arr)

        cluster_0 = [filtered_indices[i] for i in range(len(labels)) if labels[i] == 0]
        cluster_1 = [filtered_indices[i] for i in range(len(labels)) if labels[i] == 1]

        # Genuine criterion for Stage 2
        if cluster_0 and cluster_1:
            sc0 = np.sum(trust_scores[cluster_0])
            sc1 = np.sum(trust_scores[cluster_1])
            sim0 = np.mean(dist_score[cluster_0])
            sim1 = np.mean(dist_score[cluster_1])
            d0 = np.mean(dev_all[cluster_0])
            d1 = np.mean(dev_all[cluster_1])
            k0 = np.mean(kurt_all[cluster_0])
            k1 = np.mean(kurt_all[cluster_1])

            benign_indices = cluster_0
            if sc1 >= sc0:
                if ((sim1 > sim0 and k1 > k0 and d1 < d0) or
                    (d1 < d0 and sim1 > sim0 and k1 > k0) or
                    (sim1 < sim0 and d1 < d0) or
                    (sim1 > sim0 and d1 < d0 and k1 > k0)):
                    benign_indices = cluster_1
        else:
            benign_indices = cluster_0 if cluster_0 else cluster_1
    else:
        benign_indices = filtered_indices

    rejected = [i for i in range(n) if i not in benign_indices]

    if not benign_indices:
        return federated_averaging(weights_list)

    # ---------- Final: Norm-clip and average (matching LUP repo) ----------
    selected = flattened[benign_indices]
    grad_norm = np.linalg.norm(selected, axis=1, keepdims=True)
    norm_clip = float(np.median(grad_norm))
    grad_norm_clipped = np.clip(grad_norm, a_min=None, a_max=norm_clip)
    # Avoid division by zero
    safe_norm = np.where(grad_norm > 0, grad_norm, 1.0)
    clipped = (selected / safe_norm) * grad_norm_clipped
    global_flat = np.mean(clipped, axis=0)

    # Unflatten
    shapes = [w.shape for w in weights_list[0]]
    aggregated, offset = [], 0
    for shape in shapes:
        size = int(np.prod(shape))
        aggregated.append(global_flat[offset:offset + size].reshape(shape))
        offset += size

    return aggregated, rejected


# =============================================================================
# ClipCluster – Clipped Clustering
# Faithful to LUP/aggregators/Clippedclustering.py
#
# 1. Norm-clip each update to median norm
# 2. Compute cosine-distance matrix
# 3. Agglomerative Clustering (2 clusters, average linkage)
# 4. Select the majority cluster
# 5. Average the selected updates
# =============================================================================

def clipcluster_aggregation(weights_list: List[List[np.ndarray]],
                            global_weights: Optional[List[np.ndarray]] = None) -> tuple:
    """
    ClipCluster aggregation faithful to the original.
    """
    n = len(weights_list)
    if not weights_list:
        return [], []
    if n <= 2:
        return federated_averaging(weights_list)

    # Flatten
    flattened = np.stack([np.concatenate([w.flatten() for w in cw]) for cw in weights_list])

    # Step 1: Norm clipping
    l2norms = np.linalg.norm(flattened, axis=1)
    threshold = float(np.median(l2norms))

    updates = flattened.copy()
    for i in range(n):
        if l2norms[i] > threshold:
            updates[i] = updates[i] * (threshold / (l2norms[i] + 1e-6))

    # Step 2: Cosine distance matrix
    dis_max = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            # cosine distance = 1 - cosine_similarity
            dot = np.dot(updates[i], updates[j])
            norm_i = np.linalg.norm(updates[i])
            norm_j = np.linalg.norm(updates[j])
            cos_sim = dot / (norm_i * norm_j + 1e-10)
            d = 1.0 - cos_sim
            # Clamp to valid range
            d = np.clip(d, 0.0, 2.0)
            if not np.isfinite(d):
                d = 2.0
            dis_max[i, j] = d
            dis_max[j, i] = d

    # Step 3: Agglomerative Clustering
    clustering = AgglomerativeClustering(n_clusters=2, linkage='average',
                                         metric='precomputed')
    clustering.fit(dis_max)

    # Step 4: Select majority cluster
    flag = 1 if np.sum(clustering.labels_) > n // 2 else 0
    selected_idxs = [i for i, label in enumerate(clustering.labels_) if label == flag]
    rejected = [i for i in range(n) if i not in selected_idxs]

    if not selected_idxs:
        selected_idxs = list(range(n))
        rejected = []

    # Step 5: Average
    aggregated = []
    for layer_idx in range(len(weights_list[0])):
        layer_weights = np.array([weights_list[i][layer_idx] for i in selected_idxs])
        aggregated.append(np.mean(layer_weights, axis=0))

    return aggregated, rejected


# =============================================================================
# SignGuard – Sign-based Byzantine-tolerant defense
# Faithful to LUP/aggregators/signguard.py → signguard_multiclass
#
# 1. L2-norm filtering: keep clients with norm in [0.1*median, 3.0*median]
# 2. Sign-gradient clustering: compute sign features (pos/neg/zero fractions)
#    on a random sparse subset, cluster with MeanShift
# 3. Intersect the two filtered sets
# 4. Norm-clip and average
# =============================================================================

def signguard_aggregation(weights_list: List[List[np.ndarray]],
                          global_weights: Optional[List[np.ndarray]] = None) -> tuple:
    """
    SignGuard aggregation faithful to the original.
    """
    n = len(weights_list)
    if not weights_list:
        return [], []
    if n <= 2:
        return federated_averaging(weights_list)

    # Flatten
    flattened = np.stack([np.concatenate([w.flatten() for w in cw]) for cw in weights_list])
    flattened = np.nan_to_num(flattened, nan=0.0)

    all_set = set(range(n))

    # ---- Step 1: L2-norm filtering ----
    grad_l2norm = np.linalg.norm(flattened, axis=1)
    norm_med = np.median(grad_l2norm)

    benign_idx1 = set()
    for i in range(n):
        if grad_l2norm[i] > 0.1 * norm_med and grad_l2norm[i] < 3.0 * norm_med:
            benign_idx1.add(i)
    if not benign_idx1:
        benign_idx1 = all_set.copy()

    # ---- Step 2: Sign-gradient clustering ----
    num_param = flattened.shape[1]
    num_spars = max(1, int(0.1 * num_param))
    benign_idx2 = all_set.copy()

    idx_start = np.random.randint(0, max(1, num_param - num_spars))
    sparse_grads = flattened[:, idx_start:idx_start + num_spars]
    sign_grads = np.sign(sparse_grads)

    sign_pos = np.mean(sign_grads == 1.0, axis=1)
    sign_zero = np.mean(sign_grads == 0.0, axis=1)
    sign_neg = np.mean(sign_grads == -1.0, axis=1)

    pos_max = sign_pos.max() if sign_pos.max() > 0 else 1e-8
    zero_max = sign_zero.max() if sign_zero.max() > 0 else 1e-8
    neg_max = sign_neg.max() if sign_neg.max() > 0 else 1e-8

    sign_feat = np.column_stack([
        sign_pos / pos_max,
        sign_zero / zero_max,
        sign_neg / neg_max
    ])

    try:
        bandwidth = estimate_bandwidth(sign_feat, quantile=0.5, n_samples=min(50, n))
        if bandwidth <= 0:
            bandwidth = 0.5
        ms = MeanShift(bandwidth=bandwidth, bin_seeding=True, cluster_all=False)
        ms.fit(sign_feat)
        labels = ms.labels_
        unique_labels = [l for l in np.unique(labels) if l >= 0]
        if unique_labels:
            num_class = [np.sum(labels == l) for l in unique_labels]
            benign_class = unique_labels[np.argmax(num_class)]
            benign_idx2 = set(int(i) for i in np.where(labels == benign_class)[0])
        else:
            benign_idx2 = all_set.copy()
    except Exception:
        # Fallback if MeanShift fails
        benign_idx2 = all_set.copy()

    # Step 3: Intersection
    benign_idx = sorted(benign_idx2.intersection(benign_idx1))
    if not benign_idx:
        benign_idx = sorted(benign_idx1)
    if not benign_idx:
        benign_idx = list(range(n))

    rejected = [i for i in range(n) if i not in benign_idx]

    # Step 4: Norm-clip and average
    selected = flattened[benign_idx]
    grad_norm = np.linalg.norm(selected, axis=1, keepdims=True)
    norm_clip = float(np.median(grad_norm))
    grad_norm_clipped = np.clip(grad_norm, a_min=None, a_max=norm_clip)
    safe_norm = np.where(grad_norm > 0, grad_norm, 1.0)
    clipped = (selected / safe_norm) * grad_norm_clipped
    global_flat = np.mean(clipped, axis=0)

    # Unflatten
    shapes = [w.shape for w in weights_list[0]]
    aggregated, offset = [], 0
    for shape in shapes:
        size = int(np.prod(shape))
        aggregated.append(global_flat[offset:offset + size].reshape(shape))
        offset += size

    return aggregated, rejected


# =============================================================================
# PoC – Proof of Contribution
# Based on PPSG [Zhang et al., IEEE Trans. Smart Grid 2025]
#
# Contribution = quality (MMD²) × trust (history) × capability (data size)
# Block low-contribution clients, weight by contribution.
# =============================================================================

def poc_aggregation(weights_list: List[List[np.ndarray]],
                    global_weights: Optional[List[np.ndarray]] = None,
                    client_data_sizes: Optional[List[int]] = None,
                    contribution_history: Optional[np.ndarray] = None) -> tuple:
    """
    PoC (Proof of Contribution) aggregation.
    """
    n = len(weights_list)
    if not weights_list:
        return [], []
    if n <= 2:
        return federated_averaging(weights_list)

    flattened = np.stack([np.concatenate([w.flatten() for w in cw]) for cw in weights_list])

    # 1. MMD² deviation from global model
    if global_weights is not None:
        global_flat = np.concatenate([w.flatten() for w in global_weights])
        mmd_scores = np.array([np.linalg.norm(f - global_flat) ** 2 for f in flattened])
    else:
        median_flat = np.median(flattened, axis=0)
        mmd_scores = np.array([np.linalg.norm(f - median_flat) ** 2 for f in flattened])

    max_mmd = mmd_scores.max() if mmd_scores.max() > 0 else 1.0
    quality_scores = 1.0 - (mmd_scores / max_mmd)

    # 2. Historical trust
    if contribution_history is not None:
        hist_normalized = np.clip(contribution_history, 0, 1)
        trust_scores = 0.5 + 0.5 * hist_normalized
    else:
        trust_scores = np.ones(n) * 0.8

    # 3. Data capability
    if client_data_sizes is not None:
        total_data = sum(client_data_sizes)
        capability_scores = np.array([s / total_data for s in client_data_sizes])
    else:
        capability_scores = np.ones(n) / n

    # Combined contribution (Eq.13 from PPSG)
    contribution_scores = quality_scores * trust_scores * capability_scores
    max_contrib = contribution_scores.max() if contribution_scores.max() > 0 else 1.0
    contribution_scores = contribution_scores / max_contrib

    # Block low-contribution
    mean_contrib = np.mean(contribution_scores)
    std_contrib = np.std(contribution_scores)
    threshold = max(0.1, mean_contrib - 1.0 * std_contrib)

    honest_indices = [i for i in range(n) if contribution_scores[i] >= threshold]
    rejected = [i for i in range(n) if i not in honest_indices]

    if not honest_indices:
        honest_indices = np.argsort(contribution_scores)[-max(1, n // 2):].tolist()
        rejected = [i for i in range(n) if i not in honest_indices]

    # Weighted aggregation
    contrib_honest = np.array([contribution_scores[i] for i in honest_indices])
    weights_norm = contrib_honest / (contrib_honest.sum() + 1e-10)

    aggregated = []
    for layer_idx in range(len(weights_list[0])):
        weighted_sum = sum(
            weights_list[i][layer_idx] * w
            for i, w in zip(honest_indices, weights_norm)
        )
        aggregated.append(weighted_sum)

    return aggregated, rejected


# =============================================================================
# GeoMed – Geometric Median aggregation
# Faithful to LUP/aggregators/GeoMed.py
#
# Weiszfeld's iteratively-reweighted algorithm:
#   1. Start with uniform weights
#   2. Compute weighted geometric median
#   3. Re-weight: w_i *= exp(-||g_i - gm||)
#   4. Repeat 2–3 twice
# =============================================================================

def _geometric_median_weiszfeld(points: np.ndarray,
                                 weights: np.ndarray,
                                 max_iter: int = 50,
                                 tol: float = 1e-6) -> np.ndarray:
    """Weiszfeld algorithm for weighted geometric median."""
    w = weights / (weights.sum() + 1e-10)
    gm = (points * w[:, None]).sum(axis=0)

    for _ in range(max_iter):
        dists = np.linalg.norm(points - gm, axis=1)
        dists = np.maximum(dists, 1e-10)
        inv_dists = weights / dists
        total = inv_dists.sum()
        if total < 1e-15:
            break
        gm_new = (points * inv_dists[:, None]).sum(axis=0) / total
        if np.linalg.norm(gm_new - gm) < tol:
            gm = gm_new
            break
        gm = gm_new
    return gm


def geomed_aggregation(weights_list: List[List[np.ndarray]],
                       global_weights: Optional[List[np.ndarray]] = None) -> tuple:
    """
    GeoMed – Geometric Median [Pillutla et al., IEEE TSP 2022].
    Iteratively reweighted geometric median (matching LUP repo).
    """
    n = len(weights_list)
    if not weights_list:
        return [], []
    if n <= 2:
        return federated_averaging(weights_list)

    flattened = np.stack([np.concatenate([w.flatten() for w in cw])
                          for cw in weights_list])

    weights = np.ones(n, dtype=np.float64)

    gm = _geometric_median_weiszfeld(flattened, weights)
    for _ in range(2):
        dists = np.linalg.norm(flattened - gm, axis=1)
        weights = weights * np.exp(-dists)
        weights = np.maximum(weights, 1e-15)
        gm = _geometric_median_weiszfeld(flattened, weights)

    final_dists = np.linalg.norm(flattened - gm, axis=1)
    med_dist = np.median(final_dists)
    rejected = [i for i in range(n) if final_dists[i] > 3.0 * med_dist]

    shapes = [w.shape for w in weights_list[0]]
    aggregated, offset = [], 0
    for shape in shapes:
        size = int(np.prod(shape))
        aggregated.append(gm[offset:offset + size].reshape(shape))
        offset += size

    return aggregated, rejected
