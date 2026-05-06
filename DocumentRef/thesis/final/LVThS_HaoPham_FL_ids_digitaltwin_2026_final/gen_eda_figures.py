#!/usr/bin/env python3
"""Generate EDA figures for Chapter 3: feature distributions & Dirichlet split visualization."""

import sys, os
sys.path.insert(0, "/Users/hao.pham/PycharmProjects/DTGuardFL/DT-Guard-FL")

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from dtguard.config import Config, AttackType, DefenseType

OUT = Path(__file__).parent / "Figures"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.dpi": 150,
})


# ─── Helper: Dirichlet split ───
def dirichlet_split(y, num_clients, alpha, seed=42):
    """Return list of index arrays, one per client."""
    rng = np.random.RandomState(seed)
    class_indices = {c: np.where(y == c)[0] for c in np.unique(y)}
    client_indices = [[] for _ in range(num_clients)]
    for c, idxs in class_indices.items():
        rng.shuffle(idxs)
        props = rng.dirichlet([alpha] * num_clients)
        splits = (props * len(idxs)).astype(int)
        while splits.sum() < len(idxs):
            splits[np.argmax(props)] += 1
        while splits.sum() > len(idxs):
            splits[np.argmax(splits)] -= 1
        start = 0
        for i, s in enumerate(splits):
            client_indices[i].extend(idxs[start:start + s])
            start += s
    return client_indices


def plot_dirichlet(y, num_clients, alphas, dataset_name, filename,
                   class_names=None, group_categories=None):
    """Stacked bar chart: class distribution per client for each alpha.

    Args:
        class_names: dict mapping class value -> display name
        group_categories: if provided, dict mapping class value -> category name
            (groups many classes into fewer categories for cleaner legend)
    """
    unique = np.unique(y)

    # Optionally group by category
    if group_categories is not None:
        cats = sorted(set(group_categories.get(c, str(c)) for c in unique))
        n_cls = len(cats)
        cat_to_idx = {c: i for i, c in enumerate(cats)}

        # Build grouped y
        y_grouped = np.array([group_categories.get(v, str(v)) for v in y])
        unique_grp = np.array(cats)
    else:
        unique_grp = unique
        n_cls = len(unique_grp)

    # Use class names for legend
    if class_names is None:
        class_names = {c: str(c) for c in unique_grp}

    fig_w = 7 * len(alphas) if n_cls > 15 else 6 * len(alphas)
    fig, axes = plt.subplots(1, len(alphas), figsize=(fig_w, 4.5), sharey=True)
    if len(alphas) == 1:
        axes = [axes]

    # Better color palette
    if n_cls <= 10:
        cmap = plt.cm.get_cmap("tab10", n_cls)
    elif n_cls <= 20:
        cmap = plt.cm.get_cmap("tab20", n_cls)
    else:
        cmap = plt.cm.get_cmap("tab20b", n_cls)
    colors = [cmap(i) for i in range(n_cls)]

    for ax, alpha in zip(axes, alphas):
        client_indices = dirichlet_split(y, num_clients, alpha)
        # Build label-per-client matrix (using grouped labels)
        matrix = np.zeros((num_clients, n_cls))
        if group_categories is not None:
            lookup = {v: group_categories.get(v, str(v)) for v in unique}
        for i, idxs in enumerate(client_indices):
            if group_categories is not None:
                labels_grp = np.array([group_categories.get(v, str(v)) for v in y[idxs]])
            else:
                labels_grp = y[idxs]
            for ci, c in enumerate(unique_grp):
                matrix[i, ci] = (labels_grp == c).sum()
        # Normalize to ratios
        row_sums = matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        ratios = matrix / row_sums

        bottoms = np.zeros(num_clients)
        x = np.arange(num_clients)
        for ci, c in enumerate(unique_grp):
            display = class_names.get(c, str(c))
            ax.bar(x, ratios[:, ci], bottom=bottoms, color=colors[ci],
                   label=display, width=0.7, edgecolor="white", linewidth=0.3)
            bottoms += ratios[:, ci]

        ax.set_xlabel("Client ID")
        ax.set_title(f"α = {alpha}")
        ax.set_xticks(x)
        ax.set_xticklabels([str(i) for i in range(num_clients)], fontsize=9)

    axes[0].set_ylabel("Tỷ lệ lớp")
    # Legend outside
    handles, labels = axes[-1].get_legend_handles_labels()
    if n_cls <= 10:
        ncol, fs = 1, 8
    elif n_cls <= 20:
        ncol, fs = 2, 7
    else:
        ncol, fs = 2, 5.5
    fig.legend(handles, labels, loc="center left", bbox_to_anchor=(1.0, 0.5),
               fontsize=fs, frameon=False, ncol=ncol)
    fig.suptitle(f"Phân phối nhãn trên {num_clients} client – {dataset_name}", fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / filename, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"✓ Saved {filename}")


def plot_feature_distributions(X, feature_names, dataset_name, filename, n_features=8, n_samples=50000):
    """Histogram + KDE for top features."""
    rng = np.random.default_rng(42)
    n = min(n_samples, len(X))
    idx = rng.choice(len(X), n, replace=False)
    Xs = X[idx]

    # Pick subset of features
    sel = feature_names[:n_features]
    Xsel = Xs[:, :n_features]

    ncols = 4
    nrows = (n_features + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 3.2 * nrows))
    axes = axes.flatten()

    for i, (ax, fname) in enumerate(zip(axes, sel)):
        col = Xsel[:, i]
        col = col[np.isfinite(col)]
        ax.hist(col, bins=60, density=True, alpha=0.7, color="steelblue", edgecolor="white", linewidth=0.3)
        ax.set_title(fname, fontsize=10)
        ax.tick_params(labelsize=8)
        ax.set_xlim(np.percentile(col, 0.5), np.percentile(col, 99.5))

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(f"Phân phối giá trị đặc trưng – {dataset_name}", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / filename, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"✓ Saved {filename}")


# ────────────────────────────────────────────
#  MAIN
# ────────────────────────────────────────────
NUM_CLIENTS = 10

print("=" * 50)
print("Part 1: ToN-IoT (smaller, runs fast)")
print("=" * 50)

from dtguard.data.loader import load_ton_iot_data

ton_cfg = Config(
    dataset_type="ToN-IoT",
    dataset_dir="data/ToN-IoT_Data",
    num_clients=NUM_CLIENTS,
    dirichlet_alpha=0.5,
)

# Load ToN-IoT
project_root = "/Users/hao.pham/PycharmProjects/DTGuardFL/DT-Guard-FL"
ton_dir = os.path.join(project_root, "data", "ToN-IoT_Data")
train_ton, test_ton, feat_ton = load_ton_iot_data(data_dir=ton_dir)

y_ton = train_ton["Label"].values
X_ton = train_ton[feat_ton].values.astype(np.float32)

# Replace inf/nan
X_ton = np.nan_to_num(X_ton, nan=0.0, posinf=0.0, neginf=0.0)

print(f"\nToN-IoT: {len(train_ton)} train samples, {len(feat_ton)} features, {len(np.unique(y_ton))} classes")

# Figure: Feature distributions - ToN-IoT
ton_feat_display = [f"F{i}" for i in range(len(feat_ton))]
plot_feature_distributions(X_ton, ton_feat_display, "ToN-IoT",
                           "fig_5_2_ton_iot_feature_dist.png", n_features=10)

# ToN-IoT label mapping
ton_label_names = {
    0: "Normal", 1: "Scanning", 2: "DoS", 3: "DDoS", 4: "Ransomware",
    5: "MITM", 6: "Backdoor", 7: "Injection", 8: "XSS", 9: "Password",
}

# Figure: Dirichlet split - ToN-IoT
plot_dirichlet(y_ton, NUM_CLIENTS, [0.1, 0.5], "ToN-IoT",
               "fig_5_4_ton_iot_dirichlet_split.png",
               class_names=ton_label_names)

print("\n" + "=" * 50)
print("Part 2: CIC-IoT-2023")
print("=" * 50)

import pandas as pd
from sklearn.model_selection import train_test_split

cic_csv = os.path.join(project_root, "data", "CICIoT2023", "Merged01.csv")
cic_cache = os.path.join(project_root, "data", "cic_iot_2023_cache.pkl")

if os.path.exists(cic_cache):
    print(f"Loading CIC-IoT-2023 from cache...")
    full_df = pd.read_pickle(cic_cache)
    train_cic, test_cic = train_test_split(
        full_df, test_size=0.2, random_state=42, stratify=full_df["Label"]
    )
    feat_cic = [c for c in train_cic.columns if c != "Label"]
elif os.path.exists(cic_csv):
    print(f"Loading CIC-IoT-2023 from {cic_csv}...")
    full_df = pd.read_csv(cic_csv)
    train_cic, test_cic = train_test_split(
        full_df, test_size=0.2, random_state=42, stratify=full_df["Label"]
    )
    feat_cic = [c for c in train_cic.columns if c != "Label"]
else:
    raise FileNotFoundError(f"CIC-IoT-2023 not found at {cic_csv}")

y_cic = train_cic["Label"].values
X_cic = train_cic[feat_cic].values.astype(np.float32)
X_cic = np.nan_to_num(X_cic, nan=0.0, posinf=0.0, neginf=0.0)

print(f"\nCIC-IoT-2023: {len(train_cic)} train samples, {len(feat_cic)} features, {len(np.unique(y_cic))} classes")

# Pick 8 representative features (skip binary flags/protocols with near-zero std)
_sel_idx = [feat_cic.index(f) for f in ["Rate", "Header_Length", "Time_To_Live", "Tot sum", "AVG", "Std", "Variance", "IAT"] if f in feat_cic]
if len(_sel_idx) == 8:
    X_sel = X_cic[:, _sel_idx]
    sel_names = [feat_cic[i] for i in _sel_idx]
    plot_feature_distributions(X_sel, sel_names, "CIC-IoT-2023",
                               "fig_5_1_cic_iot_feature_dist.png", n_features=8, n_samples=100000)
else:
    plot_feature_distributions(X_cic, feat_cic, "CIC-IoT-2023",
                               "fig_5_1_cic_iot_feature_dist.png", n_features=8, n_samples=100000)

# Figure: Dirichlet split - CIC-IoT-2023 (show all 34 classes)
plot_dirichlet(y_cic, NUM_CLIENTS, [0.1, 0.5], "CIC-IoT-2023",
               "fig_5_3_cic_iot_dirichlet_split.png")

print("\n✅ All EDA figures generated!")
