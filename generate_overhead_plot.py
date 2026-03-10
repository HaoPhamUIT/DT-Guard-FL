#!/usr/bin/env python3
"""
generate_overhead_plot.py — Fig. 5: Computational Overhead (single compact figure)
===================================================================================
Two-panel single-column figure showing ALL overhead metrics from benchmark JSON:
  (a) Per-round total time breakdown: training vs server-side aggregation
  (b) Server-side overhead detail (ms) with accuracy and peak memory annotations

Reads from results/paper_experiments/overhead_benchmark.json (real data only).
Run 'python run_experiment_overhead.py' first to generate the data.

Output:
  results/fig5_overhead.{pdf,png}

Usage:
    python generate_overhead_plot.py
    python generate_overhead_plot.py --fmt png --dpi 600
"""

import argparse
import json
import sys
import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ── IEEE single-column style ──
IEEE_COL_W = 3.5

rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
    'font.size': 8,
    'axes.titlesize': 9,
    'axes.labelsize': 8,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 6,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.03,
    'axes.linewidth': 0.6,
})

SEARCH_PATHS = [
    Path('results/paper_experiments/overhead_benchmark.json'),
    Path('results/overhead_benchmark.json'),
]

FIGDIR = Path('results')

COLORS = {
    'DT-Guard': '#D32F2F', 'LUP': '#1976D2', 'ClipCluster': '#388E3C',
    'SignGuard': '#F57C00', 'GeoMed': '#7B1FA2', 'PoC': '#00838F',
    'FedAvg': '#9E9E9E', 'Krum': '#5D4037', 'Median': '#AFB42B',
    'Trimmed Mean': '#C2185B',
}

DEFENSE_ORDER = [
    'DT-Guard', 'LUP', 'PoC', 'ClipCluster', 'SignGuard',
    'GeoMed', 'Krum', 'Trimmed Mean', 'Median', 'FedAvg',
]


def load_overhead_data():
    """Load benchmark results from JSON. Exits if no file found."""
    for p in SEARCH_PATHS:
        if p.exists():
            print(f"  Loading results from {p}")
            with open(p) as f:
                raw = json.load(f)
            data = {}
            for r in raw['results']:
                data[r['defense']] = {
                    'total_time_s': r['total_time_s'],
                    'per_round_s': r['per_round_s'],
                    'train_per_round_s': r['train_per_round_s'],
                    'agg_per_round_s': r['agg_per_round_s'],
                    'peak_mem_mb': r['peak_mem_mb'],
                    'mem_overhead_mb': r['mem_overhead_mb'],
                    'accuracy': r['accuracy'],
                    'dt_verify_per_round_s': r.get('dt_verify_per_round_s', 0),
                    'dt_pw_per_round_s': r.get('dt_pw_per_round_s', 0),
                }
            return data, raw.get('config', {})

    print("  ✗ No benchmark data found. Searched:")
    for p in SEARCH_PATHS:
        print(f"    - {p}")
    print("\n  Run 'python run_experiment_overhead.py' first to generate real data.")
    sys.exit(1)


def plot_overhead(data, config, fmt='pdf', dpi=300):
    FIGDIR.mkdir(parents=True, exist_ok=True)

    defenses = [d for d in DEFENSE_ORDER if d in data]
    n = len(defenses)

    train_s    = [data[d]['train_per_round_s'] for d in defenses]
    agg_s      = [data[d]['agg_per_round_s'] for d in defenses]
    agg_ms     = [a * 1000 for a in agg_s]
    total_s    = [data[d]['total_time_s'] for d in defenses]
    accuracies = [data[d]['accuracy'] * 100 for d in defenses]
    peak_mems  = [data[d]['peak_mem_mb'] for d in defenses]
    colors     = [COLORS.get(d, '#888') for d in defenses]

    dtg_verify_ms = data.get('DT-Guard', {}).get('dt_verify_per_round_s', 0) * 1000
    dtg_pw_ms     = data.get('DT-Guard', {}).get('dt_pw_per_round_s', 0) * 1000
    dtg_i = defenses.index('DT-Guard') if 'DT-Guard' in defenses else -1

    num_rounds = config.get('num_rounds', 20)
    num_clients = config.get('num_clients', 20)
    attack = config.get('attack', 'LIE')

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(IEEE_COL_W, 4.8),
                                    gridspec_kw={'height_ratios': [1, 1.2]})
    fig.subplots_adjust(hspace=0.50)

    y = np.arange(n)
    bar_h = 0.50

    # ═══════════════════════════════════════════════════════════════
    # Panel (a): Per-round total time = Training (stacked) + Agg
    # ═══════════════════════════════════════════════════════════════
    bars_train = ax1.barh(y, train_s, bar_h,
                          color='#BBDEFB', edgecolor='#1565C0', linewidth=0.4,
                          label='Client training')

    for i in range(n):
        if i == dtg_i and dtg_verify_ms > 0:
            ax1.barh(y[i], dtg_verify_ms / 1000, bar_h, left=train_s[i],
                     color='#EF5350', edgecolor='#333', linewidth=0.3)
            ax1.barh(y[i], dtg_pw_ms / 1000, bar_h,
                     left=train_s[i] + dtg_verify_ms / 1000,
                     color='#FF8A65', edgecolor='#333', linewidth=0.3)
        else:
            ax1.barh(y[i], agg_s[i], bar_h, left=train_s[i],
                     color=colors[i], edgecolor='#333', linewidth=0.3)

    # Annotate total time at end of each bar
    max_total = max(t + a for t, a in zip(train_s, agg_s))
    for i in range(n):
        total_i = train_s[i] + agg_s[i]
        ax1.text(total_i + max_total * 0.01, y[i],
                 f'{total_s[i]:.0f}s total',
                 va='center', ha='left', fontsize=5, color='#555')

    ax1.set_yticks(y)
    ax1.set_yticklabels(defenses, fontsize=6.5)
    ax1.set_xlabel('Per-round time (s)')
    ax1.invert_yaxis()
    ax1.set_xlim(0, max_total * 1.22)
    ax1.grid(axis='x', alpha=0.2)
    ax1.grid(axis='y', visible=False)
    ax1.set_title(f'(a) Per-round latency breakdown ({num_clients} clients, {attack} attack)',
                  fontsize=7.5, pad=5)

    # Legend for panel (a)
    from matplotlib.patches import Patch
    legend_a = [
        Patch(facecolor='#BBDEFB', edgecolor='#1565C0', label='Client training'),
        Patch(facecolor='#EF5350', edgecolor='#333', label='DT Verification'),
        Patch(facecolor='#FF8A65', edgecolor='#333', label='DT-PW Scoring'),
        Patch(facecolor='#9E9E9E', edgecolor='#333', label='Baseline agg.'),
    ]
    ax1.legend(handles=legend_a, loc='lower right', framealpha=0.9,
               fontsize=5.5, ncol=2, borderpad=0.3, handlelength=1.0)

    # ═══════════════════════════════════════════════════════════════
    # Panel (b): Server-side overhead (ms) + accuracy + memory
    # ═══════════════════════════════════════════════════════════════
    for i in range(n):
        if i == dtg_i and dtg_verify_ms > 0:
            ax2.barh(y[i], dtg_verify_ms, bar_h,
                     color='#EF5350', edgecolor='#333', linewidth=0.4)
            ax2.barh(y[i], dtg_pw_ms, bar_h, left=dtg_verify_ms,
                     color='#FF8A65', edgecolor='#333', linewidth=0.4)
        else:
            ax2.barh(y[i], agg_ms[i], bar_h,
                     color=colors[i], edgecolor='#333', linewidth=0.4)

    max_ms = max(agg_ms)
    for i in range(n):
        # Accuracy + memory annotation at end of bar
        label = f'{accuracies[i]:.1f}% | {peak_mems[i]:.0f} MB'
        x_pos = agg_ms[i] + max_ms * 0.03
        ax2.text(x_pos, y[i], label, va='center', ha='left',
                 fontsize=5.5, color='#333')

        # Overhead value inside bar (if wide enough)
        if agg_ms[i] > max_ms * 0.15:
            ax2.text(agg_ms[i] * 0.5, y[i], f'{agg_ms[i]:.1f}',
                     va='center', ha='center', fontsize=5.5, color='white',
                     fontweight='bold')
        else:
            ax2.text(max(agg_ms[i], 0.5) + max_ms * 0.005, y[i] + bar_h * 0.55,
                     f'{agg_ms[i]:.1f}',
                     va='bottom', ha='left', fontsize=4.5, color='#888')

    ax2.set_yticks(y)
    ax2.set_yticklabels(defenses, fontsize=6.5)
    ax2.set_xlabel('Server-side aggregation overhead (ms)')
    ax2.invert_yaxis()
    ax2.set_xlim(0, max_ms * 1.65)
    ax2.grid(axis='x', alpha=0.2)
    ax2.grid(axis='y', visible=False)
    ax2.set_title('(b) Server-side overhead with accuracy and peak memory',
                  fontsize=7.5, pad=5)

    # Annotation column headers
    ax2.text(max_ms * 1.30, -0.7, 'Acc. | Peak RSS',
             va='center', ha='center', fontsize=5.5, color='#666',
             fontstyle='italic')

    # ─── Save ───
    for ext in (['pdf', 'png'] if fmt == 'pdf' else [fmt]):
        out = FIGDIR / f'fig5_overhead.{ext}'
        fig.savefig(out, dpi=dpi, format=ext)
        print(f"  Saved: {out}")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fmt', default='pdf', choices=['pdf', 'png'])
    parser.add_argument('--dpi', type=int, default=300)
    args = parser.parse_args()

    print("=" * 60)
    print("  Fig. 5: Overhead plot for DT-Guard paper")
    print("=" * 60)

    data, config = load_overhead_data()
    plot_overhead(data, config, fmt=args.fmt, dpi=args.dpi)
    print("  Done.")


if __name__ == '__main__':
    main()

