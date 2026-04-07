#!/usr/bin/env python3
"""
generate_paper_plots_multi-ratio.py — Multi-ratio Figures for DT-Guard IEEE paper
================================================================================
Extension of generate_paper_plots.py with figures showing 4 attack ratios.

  Fig. 2 (Gap 1) — Accuracy + Detection @ 4 ratios (10%,20%,40%,50%) [2×4 grid]
  Fig. 3 (Gap 2) — FPR heatmap @ 4 ratios (10%,20%,40%,50%)       [1×4 grid]

Usage:
    python generate_paper_plots_multi-ratio.py              # all figures
    python generate_paper_plots_multi-ratio.py --only fig2 # Gap 1 only
    python generate_paper_plots_multi-ratio.py --only fig3 # Gap 2 only
    python generate_paper_plots_multi-ratio.py --fmt png --dpi 600
"""

import argparse
import json
import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib import rcParams
from matplotlib.colors import LinearSegmentedColormap

# ═══════════════════════════════════════════════════════════════════════
#  IEEE STYLE
# ═══════════════════════════════════════════════════════════════════════
IEEE_COL_W = 3.5
IEEE_DBL_W = 7.16

rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
    'font.size': 8,
    'axes.titlesize': 9,
    'axes.labelsize': 8,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.03,
    'axes.grid': True,
    'grid.alpha': 0.25,
    'grid.linewidth': 0.4,
    'axes.linewidth': 0.6,
    'lines.linewidth': 1.2,
    'lines.markersize': 4,
})

# ── Paths ──
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # DT-Guard-FL/
RESULTS = PROJECT_ROOT / 'results' / 'paper'
FIGDIR  = RESULTS / 'figures'

COLORS = {
    'DT-Guard': '#D32F2F', 'LUP': '#1976D2', 'ClipCluster': '#388E3C',
    'SignGuard': '#F57C00', 'GeoMed': '#7B1FA2', 'PoC': '#00838F',
    'FedAvg': '#9E9E9E', 'Krum': '#5D4037', 'Median': '#AFB42B',
    'Trimmed Mean': '#C2185B',
}
ATTACKS_5 = ['Backdoor', 'LIE', 'Min-Max', 'Min-Sum', 'MPAF']

SHOW_DEFS = ['DT-Guard', 'LUP', 'ClipCluster', 'SignGuard', 'GeoMed',
             'PoC', 'FedAvg', 'Krum', 'Median', 'Trimmed Mean']
DEF_COLORS = [COLORS.get(d, '#888') for d in SHOW_DEFS]


def _load(name):
    p = RESULTS / name
    if not p.exists():
        print(f"    ⚠ {p} not found — run 'python run_paper_experiments.py' first.")
        return None
    with open(p) as f:
        return json.load(f)


def _load_expA_all_ratios():
    """Load all ratio results from merged file."""
    data = _load('paper_expA.json')
    if data and 'ratios' in data:
        return data['ratios']
    return None


def _draw_grouped_bars(ax, res, metric, attacks, show, colors):
    """Draw grouped bar chart: groups=attacks, bars=defenses."""
    n_a = len(attacks)
    n_d = len(show)
    bar_w = 0.08
    group_gap = 0.15

    for ai, atk in enumerate(attacks):
        x_center = ai * (n_d * bar_w + group_gap)
        for bi, d in enumerate(show):
            val = res.get(d, {}).get(atk, {}).get(metric, 0) * 100
            x_pos = x_center + (bi - n_d / 2 + 0.5) * bar_w

            edgec = 'black' if d == 'DT-Guard' else 'none'
            edgew = 0.9 if d == 'DT-Guard' else 0.2
            label = None
            if ai == 0:
                label = f'{d} (Ours)' if d == 'DT-Guard' else d

            ax.bar(x_pos, val, bar_w * 0.88,
                   color=colors[bi], edgecolor=edgec, linewidth=edgew,
                   label=label, zorder=3)

            if val < 0.5:
                ax.text(x_pos, 1.0, '0', ha='center', va='bottom',
                        fontsize=3.5, color='#999', rotation=90)

    centers = [ai * (n_d * bar_w + group_gap) for ai in range(n_a)]
    ax.set_xticks(centers)
    ax.set_xticklabels(attacks, fontsize=5.5, rotation=0)
    ax.grid(axis='y', alpha=0.25, linewidth=0.3)


# ═══════════════════════════════════════════════════════════════════════
#  FIG. 2 — Accuracy + Detection Rate at 4 Attack Ratios (Gap 1)
# ═══════════════════════════════════════════════════════════════════════
def plot_fig2(fmt='pdf'):
    """Fig. 2 — Accuracy + Detection Rate at 4 attack ratios: 10%, 20%, 40%, 50%."""
    ratios_data = _load_expA_all_ratios()
    if ratios_data is None:
        print("    ⚠ No multi-ratio data found")
        return

    RATIOS = ['10%', '20%', '40%', '50%']
    available_ratios = [r for r in RATIOS if r in ratios_data]

    if len(available_ratios) == 0:
        print("    ⚠ No ratio data available")
        return

    fig, axes = plt.subplots(len(available_ratios), 2,
                            figsize=(IEEE_DBL_W, 2.2 * len(available_ratios)))

    if len(available_ratios) == 1:
        axes = axes.reshape(1, -1)

    for idx, ratio in enumerate(available_ratios):
        res = ratios_data[ratio]['results']
        ax_acc = axes[idx, 0]
        ax_det = axes[idx, 1]

        _draw_grouped_bars(ax_acc, res, 'accuracy', ATTACKS_5, SHOW_DEFS, DEF_COLORS)
        ax_acc.set_ylabel('Accuracy (%)', fontsize=6.5)
        ax_acc.set_title(f'({chr(97+idx*2)}) {ratio} Malicious', fontsize=7, fontweight='bold', pad=2)

        if idx == 0:
            ax_acc.legend(fontsize=4.5, loc='lower left', ncol=5, framealpha=0.9,
                         columnspacing=0.3, handletextpad=0.2, handlelength=1.0)
        else:
            ax_acc.legend().set_visible(False)

        _draw_grouped_bars(ax_det, res, 'detection_rate', ATTACKS_5, SHOW_DEFS, DEF_COLORS)
        ax_det.set_ylabel('Detection Rate (%)', fontsize=6.5)
        ax_det.set_title(f'({chr(97+idx*2+1)}) {ratio} Malicious', fontsize=7, fontweight='bold', pad=2)
        ax_det.set_ylim(0, 109)

        if idx < len(available_ratios) - 1:
            ax_acc.set_xticklabels([])
            ax_det.set_xticklabels([])
        else:
            ax_acc.set_xlabel('Attack Type', fontsize=6.5)
            ax_det.set_xlabel('Attack Type', fontsize=6.5)

    plt.tight_layout(h_pad=0.6, w_pad=0.3)
    out = FIGDIR / f'fig2_degradation_multi_ratio.{fmt}'
    plt.savefig(out)
    plt.close()
    print(f"    ✓ {out}")


# ═══════════════════════════════════════════════════════════════════════
#  FIG. 3 — FPR Heatmap at 4 Attack Ratios (Gap 2)
# ═══════════════════════════════════════════════════════════════════════
def plot_fig3(fmt='pdf'):
    """Fig. 3 — FPR heatmap at 4 attack ratios: 10%, 20%, 40%, 50%."""
    ratios_data = _load_expA_all_ratios()
    if ratios_data is None:
        print("    ⚠ No multi-ratio data found")
        return

    RATIOS = ['10%', '20%', '40%', '50%']
    available_ratios = [r for r in RATIOS if r in ratios_data]

    if len(available_ratios) == 0:
        print("    ⚠ No ratio data available")
        return

    attacks = ATTACKS_5
    defenses = SHOW_DEFS

    fig, axes = plt.subplots(1, len(available_ratios),
                            figsize=(IEEE_DBL_W, 2.8), sharey=True)

    if len(available_ratios) == 1:
        axes = [axes]

    cmap = LinearSegmentedColormap.from_list(
        'fpr_cmap',
        [(0.0, '#FFFFFF'), (0.01, '#E8F5E9'), (0.10, '#A5D6A7'),
         (0.30, '#FFF9C4'), (0.50, '#FFE082'), (0.75, '#FF8A65'),
         (1.0, '#C62828')], N=256)

    # Global vmax for consistent color scale
    all_vmax = 0
    for ratio in available_ratios:
        res = ratios_data[ratio]['results']
        for d in defenses:
            for a in attacks:
                val = res.get(d, {}).get(a, {}).get('fpr', 0) * 100
                all_vmax = max(all_vmax, val)
    vmax = max(all_vmax, 5)

    for idx, ratio in enumerate(available_ratios):
        ax = axes[idx]
        res = ratios_data[ratio]['results']

        # Build FPR matrix
        matrix = np.zeros((len(defenses), len(attacks)))
        for di, d in enumerate(defenses):
            for ai, a in enumerate(attacks):
                matrix[di, ai] = res.get(d, {}).get(a, {}).get('fpr', 0) * 100

        # Add average column
        avg_col = matrix.mean(axis=1, keepdims=True)
        matrix_ext = np.hstack([matrix, avg_col])
        col_labels = attacks + ['Avg']

        im = ax.imshow(matrix_ext, cmap=cmap, aspect='auto',
                       vmin=0, vmax=vmax, interpolation='nearest')

        # Annotate cells
        for di in range(len(defenses)):
            for ci in range(len(col_labels)):
                val = matrix_ext[di, ci]
                weight = 'bold' if defenses[di] == 'DT-Guard' else 'normal'
                text_color = 'white' if val > vmax * 0.6 else 'black'
                txt = f'{val:.1f}' if val > 0 else '0.0'
                ax.text(ci, di, txt, ha='center', va='center',
                        fontsize=5, fontweight=weight, color=text_color)

        ax.set_xticks(range(len(col_labels)))
        ax.set_xticklabels(col_labels, fontsize=6, rotation=45, ha='right')
        ax.set_title(f'{ratio}', fontsize=8, fontweight='bold')
        ax.set_yticks(range(len(defenses)))
        ax.set_yticklabels([d if d != 'DT-Guard' else f'{d}\n(Ours)' for d in defenses], fontsize=6)

        # Bold DT-Guard label
        for label in ax.get_yticklabels():
            if 'DT-Guard' in label.get_text():
                label.set_fontweight('bold')
                label.set_color('#D32F2F')

        # Grid lines
        for i in range(len(defenses) + 1):
            ax.axhline(i - 0.5, color='#BDBDBD', linewidth=0.3)
        for j in range(len(col_labels) + 1):
            ax.axvline(j - 0.5, color='#BDBDBD', linewidth=0.3)
        ax.axvline(len(attacks) - 0.5, color='black', linewidth=0.6)

        if idx == 0:
            ax.set_ylabel('Defense', fontsize=7)

    fig.subplots_adjust(bottom=0.15, right=0.92, wspace=0.3)
    cbar_ax = fig.add_axes([0.94, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label('FPR (%)', fontsize=6)
    cbar.ax.tick_params(labelsize=5)

    plt.suptitle('False Positive Rate across Attack Ratios', fontsize=9, fontweight='bold', y=0.98)

    out = FIGDIR / f'fig3_fpr_multi_ratio.{fmt}'
    plt.savefig(out, bbox_inches='tight')
    plt.close()
    print(f"    ✓ {out}")


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════
PLOT_REGISTRY = {
    'fig2': ('Fig. 2 — Multi-ratio Accuracy + Detection (Gap 1)', plot_fig2),
    'fig3': ('Fig. 3 — Multi-ratio FPR (Gap 2)', plot_fig3),
}


def main():
    parser = argparse.ArgumentParser(
        description='Generate multi-ratio figures for DT-Guard IEEE paper')
    parser.add_argument('--only', nargs='*', choices=list(PLOT_REGISTRY.keys()),
                        help='Generate specific figures only')
    parser.add_argument('--fmt', default='png', choices=['pdf', 'png', 'svg'],
                        help='Output format (default: png)')
    parser.add_argument('--dpi', type=int, default=300)
    args = parser.parse_args()

    rcParams['savefig.dpi'] = args.dpi
    FIGDIR.mkdir(parents=True, exist_ok=True)

    targets = args.only if args.only else list(PLOT_REGISTRY.keys())

    print("┌──────────────────────────────────────────────────────────┐")
    print("│  DT-Guard — Multi-Ratio Paper Figures                     │")
    print("│  Fig.2 (Gap 1)  Acc + DetRate @ 4 ratios      [2×4 grid]   │")
    print("│  Fig.3 (Gap 2)  FPR heatmap @ 4 ratios         [1×4 grid]   │")
    print("└──────────────────────────────────────────────────────────┘")
    print(f"  Format: {args.fmt.upper()}  |  DPI: {args.dpi}")
    print(f"  Output: {FIGDIR}/\n")

    for key in targets:
        desc, fn = PLOT_REGISTRY[key]
        print(f"  [{key}] {desc}")
        try:
            fn(fmt=args.fmt)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"    ✗ Error: {e}")

    print(f"\n  Done! Multi-ratio figures in {FIGDIR}/")


if __name__ == '__main__':
    main()
