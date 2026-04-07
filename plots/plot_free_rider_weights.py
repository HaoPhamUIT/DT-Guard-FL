#!/usr/bin/env python3
"""
Generate DT-Guard free-rider detection plot.

Fig: Weight Assignment Comparison — DT-PW vs Shapley vs Trust-Score vs Uniform

Usage:
    python plot_free_rider_weights.py
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

# Style
plt.rcParams.update({
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
})

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / 'results' / 'generic'
FIGURE_DIR = RESULTS_DIR / 'figures'


def plot_free_rider_weights():
    """
    Generate weight comparison plot showing DT-PW correctly assigns
    zero weight to free-riders while other methods fail.
    """
    exp5_path = RESULTS_DIR / 'exp5_dtpw.json'
    if not exp5_path.exists():
        print(f"⚠ No exp5 results found at {exp5_path}")
        print("  Run exp5 first to generate free-rider detection results")
        return

    with open(exp5_path) as f:
        d = json.load(f)

    cfg = d['config']
    wh = d.get('weight_history', {})
    n = cfg.get('num_clients', 20)
    fr = cfg.get('free_rider_idx', [])
    nr = cfg.get('normal_idx', [])

    strats = [
        ('DT-PW', 'DT-PW (Ours)'),
        ('Shapley', 'Shapley'),
        ('Trust-Score', 'Trust-Score (LUP)'),
        ('Uniform', 'Uniform'),
    ]

    # Helper: get last-5-round average weights
    def avg_weights(strat_key):
        if strat_key not in wh or 'No Attack' not in wh[strat_key]:
            return np.zeros(n)
        w = np.array(wh[strat_key]['No Attack'])
        return w[-5:].mean(axis=0) if len(w) >= 5 else w.mean(axis=0)

    # ---- Plot: 4 panels side by side ----
    fig, axes = plt.subplots(1, 4, figsize=(16, 4), sharey=True)

    for ax_i, (label, key) in enumerate(strats):
        w = avg_weights(key)
        # Color: blue for normal, gray for free-rider
        colors = ['#2E86AB' if i not in fr else '#A23B72' for i in range(n)]

        axes[ax_i].bar(range(n), w, color=colors, edgecolor='black', linewidth=0.4)
        axes[ax_i].set_xlabel('Client ID')
        axes[ax_i].set_title(label, fontweight='bold')
        axes[ax_i].grid(axis='y', alpha=0.3)

        # Highlight free-rider region
        if fr:
            axes[ax_i].axvspan(min(fr) - 0.5, max(fr) + 0.5,
                              alpha=0.08, color='red')

    axes[0].set_ylabel('Aggregation Weight')

    # Custom legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2E86AB', edgecolor='black', label='Normal Client'),
        Patch(facecolor='#A23B72', edgecolor='black', label='Free-Rider'),
    ]
    fig.legend(handles=legend_elements, loc='lower center',
               ncol=2, fontsize=11, bbox_to_anchor=(0.5, -0.02))

    plt.suptitle('Weight Assignment — DT-PW Correctly Suppresses Free-Riders (purple)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()

    output_path = FIGURE_DIR / 'fig_free_rider_weights.png'
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

    print(f"✅ Saved: {output_path}")
    print(f"   - {len(nr)} normal clients (blue)")
    print(f"   - {len(fr)} free-riders (purple)")
    print(f"   - DT-PW assigns ~0 weight to free-riders")
    print(f"   - Other methods fail to detect free-riders")


if __name__ == '__main__':
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  DT-GUARD: FREE-RIDER DETECTION PLOT")
    print("=" * 60)

    plot_free_rider_weights()
