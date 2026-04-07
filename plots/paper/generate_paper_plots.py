#!/usr/bin/env python3
"""
generate_paper_plots.py — 3 Figures for DT-Guard IEEE paper (6 pages)
======================================================================
One figure per research gap. Nothing more.

  Fig. 2 (Gap 1) — Accuracy degradation vs malicious ratio   [single-col]
  Fig. 3 (Gap 2) — FPR under Non-IID: α=0.1 vs α=0.5        [single-col]
  Fig. 4 (Gap 3) — Weight distribution per client (4 panels)  [double-col]

  Table II (defense accuracy matrix) stays in LaTeX — not a plot.
  Table III (fairness) + Overhead → inline prose.

Space budget (~1.5 pages for Experiments):
  Setup text  : ~25 lines
  Table II    : ~15 lines
  Fig. 2      : ~20 lines  (single-col)
  Fig. 3      : ~20 lines  (single-col, can float beside Fig. 2)
  Fig. 4      : ~22 lines  (double-col, short height)
  Analysis    : ~10 lines  (inline numbers)
  Total       : ~112 lines ≈ 1.5 pages ✓

Usage:
    python generate_paper_plots.py                  # all 3 figures
    python generate_paper_plots.py --only fig2      # Gap 1 only
    python generate_paper_plots.py --only fig3      # Gap 2 only
    python generate_paper_plots.py --only fig4      # Gap 3 only
    python generate_paper_plots.py --fmt png --dpi 600
    python generate_paper_plots.py --inline         # print numbers for prose
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
FIGDIR  = RESULTS / 'figures'

COLORS = {
    'DT-Guard': '#D32F2F', 'LUP': '#1976D2', 'ClipCluster': '#388E3C',
    'SignGuard': '#F57C00', 'GeoMed': '#7B1FA2', 'PoC': '#00838F',
    'FedAvg': '#9E9E9E', 'Krum': '#5D4037', 'Median': '#AFB42B',
    'Trimmed Mean': '#C2185B',
}
ATTACKS_5 = ['Backdoor', 'LIE', 'Min-Max', 'Min-Sum', 'MPAF']


def _load(name):
    p = RESULTS / name
    if not p.exists():
        print(f"    ⚠ {p} not found — run 'python run_paper_experiments.py' first.")
        return None
    with open(p) as f:
        return json.load(f)


# ═══════════════════════════════════════════════════════════════════════
#  FIG. 2 — Defense Robustness at 50% Malicious (Gap 1)
#
#  Two-panel figure, single-column:
#    (a) Accuracy per attack (5 groups × 10 defense bars)
#    (b) Detection Rate per attack (same layout)
#  Data from paper_expA_50.json or paper_expA.json → 50%.
# ═══════════════════════════════════════════════════════════════════════
def _load_expA_50():
    """Load 50% results from merged or single-ratio file."""
    data = _load('paper_expA.json')
    if data and 'ratios' in data and '50%' in data['ratios']:
        return data['ratios']['50%']['results']
    data = _load('paper_expA_50.json')
    if data is not None:
        return data['results']
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

            # Annotate zero bars with "0" so they are visible
            if val < 0.5:
                ax.text(x_pos, 1.0, '0', ha='center', va='bottom',
                        fontsize=3.5, color='#999', rotation=90)

    centers = [ai * (n_d * bar_w + group_gap) for ai in range(n_a)]
    ax.set_xticks(centers)
    ax.set_xticklabels(attacks, fontsize=5.5, rotation=0)
    ax.grid(axis='y', alpha=0.25, linewidth=0.3)


def plot_fig2(fmt='pdf'):
    res = _load_expA_50()
    if res is None:
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(IEEE_COL_W, 4.2))

    # Panel (a): Accuracy
    _draw_grouped_bars(ax1, res, 'accuracy', ATTACKS_5, SHOW_DEFS, DEF_COLORS)
    ax1.set_ylabel('Accuracy (%)', fontsize=6.5)
    ax1.set_title('(a)', fontsize=7.5, fontweight='bold', pad=3, loc='left')
    ax1.legend(fontsize=4.5, loc='lower left', ncol=5, framealpha=0.9,
               columnspacing=0.3, handletextpad=0.2, handlelength=1.0)

    # Panel (b): Detection Rate
    _draw_grouped_bars(ax2, res, 'detection_rate', ATTACKS_5, SHOW_DEFS, DEF_COLORS)
    ax2.set_ylabel('Detection Rate (%)', fontsize=6.5)
    ax2.set_title('(b)', fontsize=7.5, fontweight='bold', pad=3, loc='left')
    ax2.set_ylim(0, 109)

    plt.tight_layout(h_pad=0.8)
    out = FIGDIR / f'fig2_degradation.{fmt}'
    plt.savefig(out)
    plt.close()
    print(f"    ✓ {out}")


# ═══════════════════════════════════════════════════════════════════════
#  FIG. 3 — False Positive Rate at 50% Malicious (Gap 2)
#
#  Heatmap (matrix) format: rows = defenses, cols = attacks.
#  Each cell shows the FPR value annotated. 0% cells are clearly
#  visible with a distinct light color. Much easier to read than
#  grouped bars when many values are zero.
#  Data from same paper_expA_50.json.
# ═══════════════════════════════════════════════════════════════════════
def plot_fig3(fmt='pdf'):
    res = _load_expA_50()
    if res is None:
        return

    from matplotlib.colors import LinearSegmentedColormap

    attacks = ATTACKS_5
    defenses = SHOW_DEFS

    # Build FPR matrix: rows=defenses, cols=attacks
    matrix = np.zeros((len(defenses), len(attacks)))
    for di, d in enumerate(defenses):
        for ai, a in enumerate(attacks):
            matrix[di, ai] = res.get(d, {}).get(a, {}).get('fpr', 0) * 100

    # Add average column
    avg_col = matrix.mean(axis=1, keepdims=True)
    matrix_ext = np.hstack([matrix, avg_col])
    col_labels = attacks + ['Avg']

    # Custom colormap: 0%=white → low=light green → high=dark red
    cmap = LinearSegmentedColormap.from_list(
        'fpr_cmap',
        [(0.0, '#FFFFFF'),      # 0% → white
         (0.01, '#E8F5E9'),     # near-0 → very light green
         (0.10, '#A5D6A7'),     # ~8% → light green
         (0.30, '#FFF9C4'),     # ~25% → light yellow
         (0.50, '#FFE082'),     # ~40% → amber
         (0.75, '#FF8A65'),     # ~60% → orange
         (1.0, '#C62828')],     # 80%+ → dark red
        N=256)

    vmax = max(matrix_ext.max(), 5)  # at least 5 so color scale is useful

    fig, ax = plt.subplots(figsize=(IEEE_COL_W, 3.0))

    im = ax.imshow(matrix_ext, cmap=cmap, aspect='auto',
                   vmin=0, vmax=vmax, interpolation='nearest')

    # Annotate each cell with the FPR value
    for di in range(len(defenses)):
        for ci in range(len(col_labels)):
            val = matrix_ext[di, ci]
            # Use bold for DT-Guard row
            weight = 'bold' if defenses[di] == 'DT-Guard' else 'normal'
            # Dark text on light cells, white text on dark cells
            text_color = 'white' if val > vmax * 0.6 else 'black'
            # Show "0.0" explicitly for zero values
            txt = f'{val:.1f}' if val > 0 else '0.0'
            ax.text(ci, di, txt, ha='center', va='center',
                    fontsize=6, fontweight=weight, color=text_color)

    # Axes
    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels, fontsize=6.5)
    ax.set_yticks(range(len(defenses)))
    # Mark DT-Guard with bold
    ylabels = []
    for d in defenses:
        if d == 'DT-Guard':
            ylabels.append(f'{d} (Ours)')
        else:
            ylabels.append(d)
    ax.set_yticklabels(ylabels, fontsize=6)

    # Bold the DT-Guard label
    for label in ax.get_yticklabels():
        if 'DT-Guard' in label.get_text():
            label.set_fontweight('bold')
            label.set_color('#D32F2F')

    ax.set_title('')  # caption handles title in paper

    # Add thin grid lines between cells
    for i in range(len(defenses) + 1):
        ax.axhline(i - 0.5, color='#BDBDBD', linewidth=0.4)
    for j in range(len(col_labels) + 1):
        ax.axvline(j - 0.5, color='#BDBDBD', linewidth=0.4)

    # Separator line before Avg column
    ax.axvline(len(attacks) - 0.5, color='black', linewidth=0.8)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02, aspect=25)
    cbar.set_label('False Positive Rate (%)', fontsize=6)
    cbar.ax.tick_params(labelsize=5.5)

    ax.set_xlabel('Attack Type', fontsize=7, labelpad=3)

    plt.tight_layout()
    out = FIGDIR / f'fig3_fpr.{fmt}'
    plt.savefig(out)
    plt.close()
    print(f"    ✓ {out}")


# ═══════════════════════════════════════════════════════════════════════
#  FIG. 4 — Weight Distribution per Client  (Gap 3)
#
#  4 subplots: DT-PW / Trust-Score / Uniform / FedAvg.
#  Story: "Only DT-PW suppresses free-rider weights to near zero;
#          Trust-Score actually REWARDS them."
#  Double-column, short height → ~22 lines.
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
    # 2×2 grid, single-column width
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

        # Only bottom row gets x-label
        if idx >= ncols:
            ax.set_xlabel('Client ID', fontsize=6)
        # Only left column gets y-label
        if idx % ncols == 0:
            ax.set_ylabel('Aggregation Weight', fontsize=6)

    # Hide any unused subplots
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
#  HELPER — Print inline numbers for paper prose
# ═══════════════════════════════════════════════════════════════════════
def print_inline_numbers():
    """Print numbers for paper prose — matches \\DTfill{} placeholders in LaTeX."""

    # ── Table II: Defense accuracy at 50% malicious (Gap 1) ──
    expA = _load('paper_expA.json')
    if expA and 'ratios' in expA and '50%' in expA['ratios']:
        print("\n    ══ TABLE II — Accuracy (%) at 50% Malicious ══")
        print("    Copy these into \\DTfill{} cells in tab:defense:\n")
        res = expA['ratios']['50%']['results']
        attacks = ['Backdoor', 'LIE', 'Min-Max', 'Min-Sum', 'MPAF']
        defs = ['FedAvg', 'Krum', 'Median', 'Trimmed Mean', 'GeoMed',
                'SignGuard', 'ClipCluster', 'LUP', 'PoC', 'DT-Guard']
        hdr = f"    {'Defense':<15}"
        for a in attacks:
            hdr += f"  {a:>7}"
        hdr += f"  {'Avg':>7}"
        print(hdr)
        print("    " + "─" * len(hdr))
        for d in defs:
            row = f"    {d:<15}"
            vals = []
            for a in attacks:
                v = res.get(d, {}).get(a, {}).get('accuracy', 0) * 100
                vals.append(v)
                row += f"  {v:>6.1f}%"
            row += f"  {np.mean(vals):>6.1f}%"
            print(row)

        # Fig. 2 inline numbers
        print("\n    ══ FIG. 2(a) — Accuracy degradation ══")
        ratios = list(expA['ratios'].keys())
        for d in ['DT-Guard', 'LUP', 'ClipCluster', 'SignGuard', 'PoC', 'FedAvg']:
            avgs = []
            for r in ratios:
                rr = expA['ratios'][r]['results']
                avgs.append(np.mean([rr.get(d, {}).get(a, {}).get('accuracy', 0) * 100
                                     for a in attacks]))
            drop = avgs[0] - avgs[-1]
            print(f"    {d:15s}  10%→50%: {avgs[0]:.1f}% → {avgs[-1]:.1f}%  (drop {drop:.1f}%)")

        print("\n    ══ FIG. 2(b) — Detection Rate ══")
        for d in ['DT-Guard', 'LUP', 'ClipCluster', 'SignGuard', 'GeoMed', 'PoC', 'FedAvg']:
            dets = []
            for r in ratios:
                rr = expA['ratios'][r]['results']
                dets.append(np.mean([rr.get(d, {}).get(a, {}).get('detection_rate', 0) * 100
                                     for a in attacks]))
            print(f"    {d:15s}  10%: {dets[0]:.1f}%  20%: {dets[1]:.1f}%  "
                  f"40%: {dets[2]:.1f}%  50%: {dets[3]:.1f}%")

        print("    → \\DTfill{gap1-drop} = DT-Guard accuracy drop above")
        print("    → \\DTfill{gap1-baseline-drop} = best baseline accuracy drop above")
        print("    → \\DTfill{gap1-dtguard-det} = DT-Guard avg detection rate at 50%")

    # ── Gap 2: FPR at 50% malicious (Fig. 3 inline) ──
    res50 = None
    if expA and 'ratios' in expA and '50%' in expA['ratios']:
        res50 = expA['ratios']['50%']['results']
    else:
        expA50 = _load('paper_expA_50.json')
        if expA50:
            res50 = expA50['results']

    if res50:
        print("\n    ══ FIG. 3 — FPR at 50% Malicious (Gap 2) ══")
        attacks = ['Backdoor', 'LIE', 'Min-Max', 'Min-Sum', 'MPAF']
        defs = ['DT-Guard', 'LUP', 'ClipCluster', 'SignGuard', 'GeoMed',
                'PoC', 'FedAvg', 'Krum', 'Median', 'Trimmed Mean']
        for d in defs:
            fprs = [res50.get(d, {}).get(a, {}).get('fpr', 0) * 100
                    for a in attacks]
            avg_fpr = np.mean(fprs)
            print(f"    {d:15s}  " +
                  "  ".join(f"{a[:3]}={f:.1f}%" for a, f in zip(attacks, fprs)) +
                  f"  Avg={avg_fpr:.1f}%")
        dtg_avg_fpr = np.mean([res50.get('DT-Guard', {}).get(a, {}).get('fpr', 0) * 100
                                for a in attacks])
        baseline_avg_fprs = {d: np.mean([res50.get(d, {}).get(a, {}).get('fpr', 0) * 100
                                          for a in attacks])
                              for d in defs if d != 'DT-Guard'}
        worst_baseline = max(baseline_avg_fprs, key=baseline_avg_fprs.get)
        print(f"\n    → \\DTfill{{gap2-dtguard-fpr}} = {dtg_avg_fpr:.1f}")
        print(f"    → \\DTfill{{gap2-worst-fpr}} = {baseline_avg_fprs[worst_baseline]:.1f} ({worst_baseline})")

    # ── Gap 3: Fairness + Overhead (Fig. 4 inline) ──
    expC = _load('paper_expC.json')
    if expC and 'table' in expC:
        print("\n    ══ FIG. 4 — Fairness inline numbers ══")
        for s, d in expC['table'].items():
            print(f"    {s:15s}  Normal={d['normal_weight']:.4f}  "
                  f"FR={d['freerider_weight']:.4f}  "
                  f"Det={d['fr_detected']}  Acc={d['accuracy']*100:.1f}%")
        dtpw = expC['table'].get('DT-PW', {})
        trust = expC['table'].get('Trust-Score', {})
        print(f"\n    → \\DTfill{{gap3-dtpw-fr}} = {dtpw.get('freerider_weight', 0):.4f}")
        print(f"    → \\DTfill{{gap3-dtpw-normal}} = {dtpw.get('normal_weight', 0):.4f}")
        print(f"    → \\DTfill{{gap3-trust-fr}} = {trust.get('freerider_weight', 0):.4f}")
        print(f"    → \\DTfill{{gap3-trust-normal}} = {trust.get('normal_weight', 0):.4f}")

    if expC and 'overhead' in expC:
        oh = expC['overhead']
        print(f"\n    ══ OVERHEAD inline numbers ══")
        print(f"    → \\DTfill{{overhead-pct}} = {oh['overhead_pct']}")
        print(f"    → \\DTfill{{overhead-dtpw}} = {oh['dtpw_seconds']}")
        print(f"    → \\DTfill{{overhead-fedavg}} = {oh['fedavg_seconds']}")
        print(f"    → \\DTfill{{overhead-ram}} = {oh['memory_delta_mb']}")


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════
PLOT_REGISTRY = {
    'fig2': ('Fig. 2 — Accuracy + Detection Rate @ 50% (Gap 1)', plot_fig2),
    'fig3': ('Fig. 3 — False Positive Rate @ 50% (Gap 2)',       plot_fig3),
    'fig4': ('Fig. 4 — Weight distribution per client (Gap 3)',  plot_fig4),
}


def main():
    parser = argparse.ArgumentParser(
        description='Generate 3 figures for DT-Guard IEEE paper (6 pages)')
    parser.add_argument('--only', nargs='*', choices=list(PLOT_REGISTRY.keys()),
                        help='Generate specific figures only')
    parser.add_argument('--fmt', default='png', choices=['pdf', 'png', 'svg'],
                        help='Output format (default: png)')
    parser.add_argument('--dpi', type=int, default=300)
    parser.add_argument('--inline', action='store_true',
                        help='Print inline numbers for paper prose')
    args = parser.parse_args()

    rcParams['savefig.dpi'] = args.dpi
    FIGDIR.mkdir(parents=True, exist_ok=True)

    targets = args.only if args.only else list(PLOT_REGISTRY.keys())

    print("┌──────────────────────────────────────────────────────────┐")
    print("│  DT-Guard — 3 Paper Figures                             │")
    print("│  Fig.2 (Gap 1)  Acc + DetRate @ 50%     [single-col]    │")
    print("│  Fig.3 (Gap 2)  FPR @ 50%               [single-col]    │")
    print("│  Fig.4 (Gap 3)  Weight distribution     [double-col]    │")
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

    print(f"\n  Done! 3 figures in {FIGDIR}/")


if __name__ == '__main__':
    main()

