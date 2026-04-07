#!/usr/bin/env python3
"""
generate_paper_plots_20.py — 3 Figures for DT-Guard IEEE paper @ 20% malicious
================================================================================
Same layout as generate_paper_plots.py but uses 20% malicious ratio data.

  Fig. 2 (Gap 1) — Accuracy + Detection Rate 20%   [single-col]
  Fig. 3 (Gap 2) — FPR 20%                         [single-col]
  Fig. 4 (Gap 3) — Weight distribution per client     [double-col]

Usage:
    python generate_paper_plots_20.py                  # all 3 figures
    python generate_paper_plots_20.py --only fig2      # Gap 1 only
    python generate_paper_plots_20.py --only fig3      # Gap 2 only
    python generate_paper_plots_20.py --only fig4      # Gap 3 only
    python generate_paper_plots_20.py --fmt png --dpi 600
    python generate_paper_plots_20.py --inline         # print numbers for prose
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

RESULTS = Path('results/paper')
FIGDIR  = RESULTS / 'figures_20pct'

COLORS = {
    'DT-Guard': '#D32F2F', 'LUP': '#1976D2', 'ClipCluster': '#388E3C',
    'SignGuard': '#F57C00', 'GeoMed': '#7B1FA2', 'PoC': '#00838F',
    'FedAvg': '#9E9E9E', 'Krum': '#5D4037', 'Median': '#AFB42B',
    'Trimmed Mean': '#C2185B',
}
ATTACKS_5 = ['Backdoor', 'LIE', 'Min-Max', 'Min-Sum', 'MPAF']

TARGET_RATIO = '20%'


def _load(name):
    p = RESULTS / name
    if not p.exists():
        print(f"    ⚠ {p} not found — run 'python run_paper_experiments.py' first.")
        return None
    with open(p) as f:
        return json.load(f)


# ═══════════════════════════════════════════════════════════════════════
#  FIG. 2 — Defense Robustness at 20% Malicious (Gap 1)
# ═══════════════════════════════════════════════════════════════════════
def _load_expA_20():
    """Load 20% results from merged file."""
    data = _load('paper_expA.json')
    if data and 'ratios' in data and TARGET_RATIO in data['ratios']:
        return data['ratios'][TARGET_RATIO]['results']
    return None

SHOW_DEFS = ['DT-Guard', 'LUP', 'ClipCluster', 'SignGuard', 'GeoMed',
             'PoC', 'FedAvg', 'Krum', 'Median', 'Trimmed Mean']
DEF_COLORS = [COLORS.get(d, '#888') for d in SHOW_DEFS]


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


def plot_fig2(fmt='pdf'):
    res = _load_expA_20()
    if res is None:
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(IEEE_COL_W, 4.2))

    # Panel (a): Accuracy
    _draw_grouped_bars(ax1, res, 'accuracy', ATTACKS_5, SHOW_DEFS, DEF_COLORS)
    ax1.set_ylabel('Accuracy (%)', fontsize=6.5)
    ax1.set_title(f'(a) Accuracy @ {TARGET_RATIO} malicious', fontsize=7.5,
                  fontweight='bold', pad=3, loc='left')
    ax1.legend(fontsize=4.5, loc='lower left', ncol=5, framealpha=0.9,
               columnspacing=0.3, handletextpad=0.2, handlelength=1.0)

    # Panel (b): Detection Rate
    _draw_grouped_bars(ax2, res, 'detection_rate', ATTACKS_5, SHOW_DEFS, DEF_COLORS)
    ax2.set_ylabel('Detection Rate (%)', fontsize=6.5)
    ax2.set_title(f'(b) Detection Rate @ {TARGET_RATIO} malicious', fontsize=7.5,
                  fontweight='bold', pad=3, loc='left')
    ax2.set_ylim(0, 109)

    plt.tight_layout(h_pad=0.8)
    out = FIGDIR / f'fig2_degradation_20pct.{fmt}'
    plt.savefig(out)
    plt.close()
    print(f"    ✓ {out}")


# ═══════════════════════════════════════════════════════════════════════
#  FIG. 3 — False Positive Rate at 20% Malicious (Gap 2)
# ═══════════════════════════════════════════════════════════════════════
def plot_fig3(fmt='pdf'):
    res = _load_expA_20()
    if res is None:
        return

    from matplotlib.colors import LinearSegmentedColormap

    attacks = ATTACKS_5
    defenses = SHOW_DEFS

    matrix = np.zeros((len(defenses), len(attacks)))
    for di, d in enumerate(defenses):
        for ai, a in enumerate(attacks):
            matrix[di, ai] = res.get(d, {}).get(a, {}).get('fpr', 0) * 100

    avg_col = matrix.mean(axis=1, keepdims=True)
    matrix_ext = np.hstack([matrix, avg_col])
    col_labels = attacks + ['Avg']

    cmap = LinearSegmentedColormap.from_list(
        'fpr_cmap',
        [(0.0, '#FFFFFF'),
         (0.01, '#E8F5E9'),
         (0.10, '#A5D6A7'),
         (0.30, '#FFF9C4'),
         (0.50, '#FFE082'),
         (0.75, '#FF8A65'),
         (1.0, '#C62828')],
        N=256)

    vmax = max(matrix_ext.max(), 5)

    fig, ax = plt.subplots(figsize=(IEEE_COL_W, 3.0))

    im = ax.imshow(matrix_ext, cmap=cmap, aspect='auto',
                   vmin=0, vmax=vmax, interpolation='nearest')

    for di in range(len(defenses)):
        for ci in range(len(col_labels)):
            val = matrix_ext[di, ci]
            weight = 'bold' if defenses[di] == 'DT-Guard' else 'normal'
            text_color = 'white' if val > vmax * 0.6 else 'black'
            txt = f'{val:.1f}' if val > 0 else '0.0'
            ax.text(ci, di, txt, ha='center', va='center',
                    fontsize=6, fontweight=weight, color=text_color)

    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels, fontsize=6.5)
    ax.set_yticks(range(len(defenses)))
    ylabels = []
    for d in defenses:
        if d == 'DT-Guard':
            ylabels.append(f'{d} (Ours)')
        else:
            ylabels.append(d)
    ax.set_yticklabels(ylabels, fontsize=6)

    for label in ax.get_yticklabels():
        if 'DT-Guard' in label.get_text():
            label.set_fontweight('bold')
            label.set_color('#D32F2F')

    ax.set_title(f'FPR @ {TARGET_RATIO} malicious', fontsize=8, pad=4)

    for i in range(len(defenses) + 1):
        ax.axhline(i - 0.5, color='#BDBDBD', linewidth=0.4)
    for j in range(len(col_labels) + 1):
        ax.axvline(j - 0.5, color='#BDBDBD', linewidth=0.4)

    ax.axvline(len(attacks) - 0.5, color='black', linewidth=0.8)

    cbar = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02, aspect=25)
    cbar.set_label('False Positive Rate (%)', fontsize=6)
    cbar.ax.tick_params(labelsize=5.5)

    ax.set_xlabel('Attack Type', fontsize=7, labelpad=3)

    plt.tight_layout()
    out = FIGDIR / f'fig3_fpr_20pct.{fmt}'
    plt.savefig(out)
    plt.close()
    print(f"    ✓ {out}")


# ═══════════════════════════════════════════════════════════════════════
#  FIG. 4 — Weight Distribution per Client (Gap 3)
#  (same as original — independent of malicious ratio)
# ═══════════════════════════════════════════════════════════════════════
def plot_fig4(fmt='pdf'):
    data = _load('paper_expC.json')
    if data is None:
        return

    cfg = data['config']
    nc = cfg['num_clients']
    roles = cfg['roles']
    strategies = list(data['weight_history'].keys())
    last_n = 5

    C_N, C_F = '#4285F4', '#EA4335'
    cc = [C_N if roles[str(i)] == 'Normal' else C_F for i in range(nc)]

    ns = len(strategies)
    nrows, ncols = 2, 2
    fig, axes = plt.subplots(nrows, ncols, figsize=(IEEE_COL_W, 3.6),
                             sharey=True, sharex=True)
    axes_flat = axes.flatten()

    for idx, (ax, sname) in enumerate(zip(axes_flat, strategies)):
        wh = np.array(data['weight_history'][sname])
        w_avg = wh[-last_n:].mean(axis=0)

        ax.bar(range(nc), w_avg, color=cc,
               edgecolor='black', linewidth=0.15, width=0.7)
        ax.axhline(y=1.0 / nc, color='gray', ls='--', lw=0.5, alpha=0.5)
        ax.set_title(sname, fontsize=7, fontweight='bold', pad=3)
        ax.set_xticks(range(0, nc, 4))
        ax.set_xlim(-0.6, nc - 0.4)
        ax.tick_params(axis='both', labelsize=5.5)

        if idx >= ncols:
            ax.set_xlabel('Client ID', fontsize=6)
        if idx % ncols == 0:
            ax.set_ylabel('Aggregation Weight', fontsize=6)

    for idx in range(ns, nrows * ncols):
        axes_flat[idx].set_visible(False)

    fig.legend(
        handles=[
            Patch(facecolor=C_N, edgecolor='black', lw=0.3, label='Normal'),
            Patch(facecolor=C_F, edgecolor='black', lw=0.3, label='Free-Rider'),
        ],
        loc='lower center', ncol=2, fontsize=6,
        bbox_to_anchor=(0.5, -0.02), handletextpad=0.3, columnspacing=1.0)

    plt.tight_layout(rect=[0, 0.04, 1, 1], h_pad=0.6, w_pad=0.3)

    out = FIGDIR / f'fig4_weights.{fmt}'
    plt.savefig(out)
    plt.close()
    print(f"    ✓ {out}")


# ═══════════════════════════════════════════════════════════════════════
#  HELPER — Print inline numbers for paper prose (20% focus)
# ═══════════════════════════════════════════════════════════════════════
def print_inline_numbers():
    expA = _load('paper_expA.json')
    if not expA or 'ratios' not in expA or TARGET_RATIO not in expA['ratios']:
        print(f"    ⚠ No {TARGET_RATIO} data found.")
        return

    res = expA['ratios'][TARGET_RATIO]['results']
    attacks = ['Backdoor', 'LIE', 'Min-Max', 'Min-Sum', 'MPAF']
    defs = ['FedAvg', 'Krum', 'Median', 'Trimmed Mean', 'GeoMed',
            'SignGuard', 'ClipCluster', 'LUP', 'PoC', 'DT-Guard']

    # ── Accuracy table ──
    print(f"\n    ══ TABLE — Accuracy (%) at {TARGET_RATIO} Malicious ══\n")
    hdr = f"    {'Defense':<15}"
    for a in attacks:
        hdr += f"  {a:>8}"
    hdr += f"  {'Avg':>8}"
    print(hdr)
    print("    " + "─" * len(hdr))
    for d in defs:
        row = f"    {d:<15}"
        vals = []
        for a in attacks:
            v = res.get(d, {}).get(a, {}).get('accuracy', 0) * 100
            vals.append(v)
            row += f"  {v:>7.1f}%"
        row += f"  {np.mean(vals):>7.1f}%"
        print(row)

    # ── Detection Rate ──
    print(f"\n    ══ Detection Rate (%) at {TARGET_RATIO} Malicious ══\n")
    for d in defs:
        vals = [res.get(d, {}).get(a, {}).get('detection_rate', 0) * 100
                for a in attacks]
        avg = np.mean(vals)
        print(f"    {d:<15}  " +
              "  ".join(f"{a[:4]}={v:.1f}%" for a, v in zip(attacks, vals)) +
              f"  Avg={avg:.1f}%")

    # ── FPR ──
    print(f"\n    ══ FPR (%) at {TARGET_RATIO} Malicious ══\n")
    for d in defs:
        fprs = [res.get(d, {}).get(a, {}).get('fpr', 0) * 100
                for a in attacks]
        avg_fpr = np.mean(fprs)
        print(f"    {d:<15}  " +
              "  ".join(f"{a[:4]}={f:.1f}%" for a, f in zip(attacks, fprs)) +
              f"  Avg={avg_fpr:.1f}%")

    # ── Summary for DT-Guard ──
    dtg_acc = np.mean([res['DT-Guard'][a]['accuracy'] * 100 for a in attacks])
    dtg_det = np.mean([res['DT-Guard'][a]['detection_rate'] * 100 for a in attacks])
    dtg_fpr = np.mean([res['DT-Guard'][a]['fpr'] * 100 for a in attacks])
    print(f"\n    ── DT-Guard @ {TARGET_RATIO} Summary ──")
    print(f"    Avg Accuracy:       {dtg_acc:.1f}%")
    print(f"    Avg Detection Rate: {dtg_det:.1f}%")
    print(f"    Avg FPR:            {dtg_fpr:.1f}%")


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════
PLOT_REGISTRY = {
    'fig2': (f'Fig. 2 — Accuracy + Detection Rate @ {TARGET_RATIO} (Gap 1)', plot_fig2),
    'fig3': (f'Fig. 3 — False Positive Rate @ {TARGET_RATIO} (Gap 2)',       plot_fig3),
    'fig4': ('Fig. 4 — Weight distribution per client (Gap 3)',               plot_fig4),
}


def main():
    parser = argparse.ArgumentParser(
        description=f'Generate 3 figures for DT-Guard IEEE paper @ {TARGET_RATIO} malicious')
    parser.add_argument('--only', nargs='*', choices=list(PLOT_REGISTRY.keys()),
                        help='Generate specific figures only')
    parser.add_argument('--fmt', default='pdf', choices=['pdf', 'png', 'svg'],
                        help='Output format (default: pdf)')
    parser.add_argument('--dpi', type=int, default=300)
    parser.add_argument('--inline', action='store_true',
                        help='Print inline numbers for paper prose')
    args = parser.parse_args()

    rcParams['savefig.dpi'] = args.dpi
    FIGDIR.mkdir(parents=True, exist_ok=True)

    targets = args.only if args.only else list(PLOT_REGISTRY.keys())

    print("┌──────────────────────────────────────────────────────────┐")
    print(f"│  DT-Guard — 3 Paper Figures @ {TARGET_RATIO} malicious             │")
    print("│  Fig.2 (Gap 1)  Acc + DetRate            [single-col]    │")
    print("│  Fig.3 (Gap 2)  FPR                      [single-col]    │")
    print("│  Fig.4 (Gap 3)  Weight distribution      [double-col]    │")
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

    if args.inline:
        print_inline_numbers()

    print(f"\n  Done! Figures in {FIGDIR}/")


if __name__ == '__main__':
    main()

