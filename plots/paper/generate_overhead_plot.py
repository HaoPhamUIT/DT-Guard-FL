#!/usr/bin/env python3
"""
generate_overhead_plot.py — Performance Summary (2-panel figure)
=======================================================================
Two-panel single-column figure combining:
  (a) Per-round total time breakdown: training vs server-side aggregation
  (b) Memory efficiency comparison across defense mechanisms

Output:
  results/fig9_performance_summary.{pdf,png}

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
from matplotlib.patches import Patch

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

SCRIPT_DIR = Path(__file__).parent.parent.parent
SEARCH_PATHS = [
    Path('results/paper/overhead_benchmark.json'),
    Path('results/overhead_benchmark.json'),
    SCRIPT_DIR / 'results' / 'paper' / 'overhead_benchmark.json',
    SCRIPT_DIR / 'results' / 'overhead_benchmark.json',
]

FIGDIR = Path('results/paper/figures')

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
    """Load benchmark results from JSON."""
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
    sys.exit(1)


def plot_performance_summary(data, config, fmt='pdf', dpi=300):
    """Create 2-panel performance summary figure."""
    FIGDIR.mkdir(parents=True, exist_ok=True)

    defenses = [d for d in DEFENSE_ORDER if d in data]
    n = len(defenses)
    num_rounds = config.get('num_rounds', 20)
    num_clients = config.get('num_clients', 20)
    attack = config.get('attack', 'LIE')

    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(IEEE_COL_W, 5.5),
                                    gridspec_kw={'height_ratios': [1, 1.1]})
    fig.subplots_adjust(hspace=0.45, left=0.12, right=0.96, top=0.95, bottom=0.08)

    # ═══════════════════════════════════════════════════════════════
    # Panel (a): Per-round total time breakdown
    # ═══════════════════════════════════════════════════════════════
    train_s = [data[d]['train_per_round_s'] for d in defenses]
    agg_s = [data[d]['agg_per_round_s'] for d in defenses]
    agg_ms = [a * 1000 for a in agg_s]
    total_s = [data[d]['total_time_s'] for d in defenses]
    colors = [COLORS.get(d, '#888') for d in defenses]

    dtg_verify_ms = data.get('DT-Guard', {}).get('dt_verify_per_round_s', 0) * 1000
    dtg_pw_ms = data.get('DT-Guard', {}).get('dt_pw_per_round_s', 0) * 1000
    dtg_i = defenses.index('DT-Guard') if 'DT-Guard' in defenses else -1

    y = np.arange(n)
    bar_h = 0.50

    # Training bars (bottom layer)
    bars_train = ax1.barh(y, train_s, bar_h,
                          color='#BBDEFB', edgecolor='#1565C0', linewidth=0.4,
                          label='Client training')

    # Aggregation bars (top layer)
    for i in range(n):
        if i == dtg_i and dtg_verify_ms > 0:
            # DT-Guard with components
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
                 f'{total_s[i]:.0f}s',
                 va='center', ha='left', fontsize=5, color='#555')

    ax1.set_yticks(y)
    ax1.set_yticklabels(defenses, fontsize=6.5)
    ax1.set_xlabel('Per-round time (s)')
    ax1.invert_yaxis()
    ax1.set_xlim(0, max_total * 1.18)
    ax1.grid(axis='x', alpha=0.2)
    ax1.grid(axis='y', visible=False)
    ax1.set_title(f'(a) Per-round latency breakdown ({num_clients} clients)',
                  fontsize=8, pad=5, fontweight='bold')

    # Legend for panel (a)
    legend_a = [
        Patch(facecolor='#BBDEFB', edgecolor='#1565C0', label='Training'),
        Patch(facecolor='#EF5350', edgecolor='#333', label='DT Verif.'),
        Patch(facecolor='#FF8A65', edgecolor='#333', label='DT-PW'),
        Patch(facecolor='#9E9E9E', edgecolor='#333', label='Agg.'),
    ]
    ax1.legend(handles=legend_a, loc='lower right', framealpha=0.9,
               fontsize=5.5, ncol=2, borderpad=0.3, handlelength=1.0)

    # ═══════════════════════════════════════════════════════════════
    # Panel (b): Memory efficiency comparison
    # ═══════════════════════════════════════════════════════════════
    peak_mems = np.array([data[d]['peak_mem_mb'] for d in defenses])
    mem_overheads = np.array([data[d]['mem_overhead_mb'] for d in defenses])

    x = np.arange(n)
    bar_width = 0.35

    # Peak memory bars (left)
    bars1 = ax2.bar(x - bar_width/2, peak_mems, bar_width,
                   label='Peak memory',
                   color=[c if d != 'DT-Guard' else '#D32F2F' for c, d in zip(colors, defenses)],
                   edgecolor=['#B71C1C' if d == 'DT-Guard' else '#333' for d in defenses],
                   linewidth=[1.5 if d == 'DT-Guard' else 0.6 for d in defenses],
                   alpha=0.85)

    # Memory overhead bars (right) - with hatch pattern
    bars2 = ax2.bar(x + bar_width/2, mem_overheads, bar_width,
                   label='Mem. overhead',
                   color='#E0E0E0',
                   edgecolor='#616161',
                   linewidth=0.6,
                   hatch='///',
                   alpha=0.7)

    # Add value labels on bars
    for i in range(n):
        # Peak memory labels
        ax2.text(x[i] - bar_width/2, peak_mems[i] + 8,
               f'{peak_mems[i]:.0f}',
               ha='center', va='bottom', fontsize=5.5,
               fontweight='bold' if defenses[i] == 'DT-Guard' else 'normal',
               color='#D32F2F' if defenses[i] == 'DT-Guard' else '#424242')

        # Memory overhead labels (only if > 0)
        if mem_overheads[i] > 0:
            ax2.text(x[i] + bar_width/2, mem_overheads[i] + 3,
                   f'{mem_overheads[i]:.1f}',
                   ha='center', va='bottom', fontsize=5, color='#424242')

    # Labels and title
    ax2.set_xlabel('Defense mechanism', fontsize=8)
    ax2.set_ylabel('Memory (MB)', fontsize=8)
    ax2.set_title('(b) Memory efficiency comparison',
                  fontsize=8, pad=5, fontweight='bold')

    # X-axis labels (rotated for readability)
    ax2.set_xticks(x)
    ax2.set_xticklabels(defenses, rotation=45, ha='right', fontsize=6.5)

    # Grid
    ax2.grid(axis='y', alpha=0.2, linestyle='-', linewidth=0.5)
    ax2.set_axisbelow(True)

    # Legend
    ax2.legend(loc='upper right', fontsize=5.5, framealpha=0.95,
              borderpad=0.3, handlelength=0.8)

    # Set y-axis limit
    ax2.set_ylim(0, max(peak_mems) * 1.12)

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
    print("  Fig. 5: Performance Summary (2-panel)")
    print("=" * 60)

    data, config = load_overhead_data()
    plot_performance_summary(data, config, fmt=args.fmt, dpi=args.dpi)
    print("  Done.")


if __name__ == '__main__':
    main()
