#!/usr/bin/env python3
"""
generate_toniot_plots.py — Figures for DT-Guard IEEE paper (ToN-IoT Dataset)
============================================================================
Mirrors plots/paper/generate_paper_plots.py but reads from results/ton_iot/.
Produces the same 3+1 figures for the second dataset validation.

  Fig. 2 (Gap 1) — Accuracy + Detection Rate @ 50%       [single-col]
  Fig. 3 (Gap 2) — FPR heatmap @ 50%                     [single-col]
  Fig. 4 (Gap 3) — Weight distribution per client         [double-col]
  Fig. 5          — Overhead: latency + memory (2-panel)  [single-col]

Usage:
    python generate_toniot_plots.py                  # all figures
    python generate_toniot_plots.py --only fig2      # Gap 1 only
    python generate_toniot_plots.py --only fig3      # Gap 2 only
    python generate_toniot_plots.py --only fig4      # Gap 3 only
    python generate_toniot_plots.py --only fig5      # Overhead only
    python generate_toniot_plots.py --fmt png --dpi 600
    python generate_toniot_plots.py --inline         # print numbers for prose
"""

import argparse
import json
import sys
import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import LinearSegmentedColormap
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

# ── Paths ──
SCRIPT_DIR  = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # DT-Guard-FL/

RESULTS = PROJECT_ROOT / 'results' / 'ton_iot'
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

DEFENSE_ORDER = [
    'DT-Guard', 'LUP', 'PoC', 'ClipCluster', 'SignGuard',
    'GeoMed', 'Krum', 'Trimmed Mean', 'Median', 'FedAvg',
]


def _load(name):
    p = RESULTS / name
    if not p.exists():
        print(f"    ⚠ {p} not found — run ToN-IoT experiments first.")
        return None
    with open(p) as f:
        return json.load(f)


# ═══════════════════════════════════════════════════════════════════════
#  FIG. 2 — Defense Robustness at 50% Malicious (Gap 1)
#
#  Two-panel figure, single-column:
#    (a) Accuracy per attack (5 groups × 10 defense bars)
#    (b) Detection Rate per attack (same layout)
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
    """Fig. 2 — Accuracy + Detection Rate at 50% malicious (Gap 1)."""
    res = _load_expA_50()
    if res is None:
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(IEEE_COL_W, 4.2))

    # Panel (a): Accuracy
    _draw_grouped_bars(ax1, res, 'accuracy', ATTACKS_5, SHOW_DEFS, DEF_COLORS)
    ax1.set_ylabel('Accuracy (%)', fontsize=6.5)
    ax1.set_title('(a) ToN-IoT', fontsize=7.5, fontweight='bold', pad=3, loc='left')
    ax1.legend(fontsize=4.5, loc='lower left', ncol=5, framealpha=0.9,
               columnspacing=0.3, handletextpad=0.2, handlelength=1.0)

    # Panel (b): Detection Rate
    _draw_grouped_bars(ax2, res, 'detection_rate', ATTACKS_5, SHOW_DEFS, DEF_COLORS)
    ax2.set_ylabel('Detection Rate (%)', fontsize=6.5)
    ax2.set_title('(b) ToN-IoT', fontsize=7.5, fontweight='bold', pad=3, loc='left')
    ax2.set_ylim(0, 109)

    plt.tight_layout(h_pad=0.8)
    out = FIGDIR / f'fig2_degradation.{fmt}'
    plt.savefig(out)
    plt.close()
    print(f"    ✓ {out}")


# ═══════════════════════════════════════════════════════════════════════
#  FIG. 3 — False Positive Rate Heatmap at 50% Malicious (Gap 2)
# ═══════════════════════════════════════════════════════════════════════
def plot_fig3(fmt='pdf'):
    """Fig. 3 — FPR heatmap at 50% malicious (Gap 2)."""
    res = _load_expA_50()
    if res is None:
        return

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

    # Custom colormap
    cmap = LinearSegmentedColormap.from_list(
        'fpr_cmap',
        [(0.0, '#FFFFFF'), (0.01, '#E8F5E9'), (0.10, '#A5D6A7'),
         (0.30, '#FFF9C4'), (0.50, '#FFE082'), (0.75, '#FF8A65'),
         (1.0, '#C62828')], N=256)

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
    ylabels = [f'{d} (Ours)' if d == 'DT-Guard' else d for d in defenses]
    ax.set_yticklabels(ylabels, fontsize=6)

    for label in ax.get_yticklabels():
        if 'DT-Guard' in label.get_text():
            label.set_fontweight('bold')
            label.set_color('#D32F2F')

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
    out = FIGDIR / f'fig3_fpr.{fmt}'
    plt.savefig(out)
    plt.close()
    print(f"    ✓ {out}")


# ═══════════════════════════════════════════════════════════════════════
#  FIG. 3B — Non-IID FPR comparison (from EXP-B data)
#  Optional: only generated if paper_expB.json exists.
# ═══════════════════════════════════════════════════════════════════════
def plot_fig3b(fmt='pdf'):
    """Fig. 3b — Non-IID FPR comparison α=0.1 vs α=0.5."""
    data = _load('paper_expB.json')
    if data is None:
        return

    ALPHAS = ['0.1', '0.5']
    DEFENSES = ['DT-Guard', 'LUP', 'ClipCluster', 'SignGuard', 'GeoMed', 'PoC']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(IEEE_COL_W, 2.4), sharey=True)

    x = np.arange(len(DEFENSES))
    width = 0.35
    colors_bar = [COLORS.get(d, '#888') for d in DEFENSES]

    for ax, alpha_str, title in [(ax1, '0.1', 'α = 0.1 (Extreme Non-IID)'),
                                  (ax2, '0.5', 'α = 0.5 (Moderate)')]:
        if alpha_str not in data:
            continue

        # No Attack FPR
        fpr_noatk = [data[alpha_str].get('No Attack', {}).get(d, {}).get('fpr', 0) * 100
                     for d in DEFENSES]
        # LIE FPR
        fpr_lie = [data[alpha_str].get('LIE', {}).get(d, {}).get('fpr', 0) * 100
                   for d in DEFENSES]

        bars1 = ax.bar(x - width/2, fpr_noatk, width, label='No Attack',
                       color=colors_bar, edgecolor='black', linewidth=0.3, alpha=0.85)
        bars2 = ax.bar(x + width/2, fpr_lie, width, label='LIE Attack',
                       color=colors_bar, edgecolor='black', linewidth=0.3,
                       alpha=0.5, hatch='///')

        ax.set_title(title, fontsize=6.5, fontweight='bold', pad=3)
        ax.set_xticks(x)
        ax.set_xticklabels([d.replace('ClipCluster', 'ClipCl.') for d in DEFENSES],
                           fontsize=5, rotation=45, ha='right')
        ax.set_ylabel('FPR (%)', fontsize=6)
        ax.grid(axis='y', alpha=0.25, linewidth=0.3)

        # Annotate values on bars
        for i, (v1, v2) in enumerate(zip(fpr_noatk, fpr_lie)):
            if v1 > 0.5:
                ax.text(x[i] - width/2, v1 + 0.5, f'{v1:.0f}', ha='center',
                        va='bottom', fontsize=4.5)
            if v2 > 0.5:
                ax.text(x[i] + width/2, v2 + 0.5, f'{v2:.0f}', ha='center',
                        va='bottom', fontsize=4.5)

    ax1.legend(fontsize=5, loc='upper right')

    plt.tight_layout()
    out = FIGDIR / f'fig3b_noniid_fpr.{fmt}'
    plt.savefig(out)
    plt.close()
    print(f"    ✓ {out}")


# ═══════════════════════════════════════════════════════════════════════
#  FIG. 4 — Weight Distribution per Client (Gap 3)
# ═══════════════════════════════════════════════════════════════════════
def plot_fig4(fmt='pdf'):
    """Fig. 4 — Weight distribution per client (Gap 3)."""
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

    for idx in range(len(strategies), nrows * ncols):
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
#  FIG. 4B — Convergence Curves (from EXP-C data)
# ═══════════════════════════════════════════════════════════════════════
def plot_fig4b(fmt='pdf'):
    """Fig. 4b — Convergence with free-riders."""
    data = _load('paper_expC.json')
    if data is None:
        return

    strategies = list(data['accuracy_history'].keys())
    markers = {'DT-PW': '-o', 'Trust-Score': '-s', 'Uniform': '-^', 'FedAvg': '-x'}
    strat_colors = {'DT-PW': '#D32F2F', 'Trust-Score': '#1976D2',
                    'Uniform': '#388E3C', 'FedAvg': '#9E9E9E'}

    fig, ax = plt.subplots(figsize=(IEEE_COL_W, 2.5))

    for sname in strategies:
        hist = data['accuracy_history'][sname]
        n_rounds = len(hist)
        ax.plot(range(1, n_rounds + 1), [v * 100 for v in hist],
                markers.get(sname, '-o'), linewidth=1.2, markersize=3,
                color=strat_colors.get(sname, '#888'), label=sname)

    ax.set_xlabel('Round', fontsize=7)
    ax.set_ylabel('Accuracy (%)', fontsize=7)
    ax.set_title('Convergence with 20% Free-Riders [ToN-IoT]',
                 fontsize=7.5, fontweight='bold')
    ax.legend(fontsize=6, loc='lower right')
    ax.grid(True, alpha=0.25)

    plt.tight_layout()
    out = FIGDIR / f'fig4b_convergence.{fmt}'
    plt.savefig(out)
    plt.close()
    print(f"    ✓ {out}")


# ═══════════════════════════════════════════════════════════════════════
#  FIG. 5 — Overhead: Latency + Memory (2-panel)
# ═══════════════════════════════════════════════════════════════════════
def _load_overhead():
    """Load overhead benchmark data."""
    data = _load('overhead_benchmark.json')
    if data is None:
        return None, {}
    result_map = {}
    for r in data['results']:
        result_map[r['defense']] = {
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
    return result_map, data.get('config', {})


def plot_fig5(fmt='pdf'):
    """Fig. 5 — Overhead: latency breakdown + memory comparison."""
    data, config = _load_overhead()
    if data is None:
        return

    defenses = [d for d in DEFENSE_ORDER if d in data]
    n = len(defenses)
    num_rounds = config.get('num_rounds', 20)
    num_clients = config.get('num_clients', 20)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(IEEE_COL_W, 5.5),
                                    gridspec_kw={'height_ratios': [1, 1.1]})
    fig.subplots_adjust(hspace=0.45, left=0.12, right=0.96, top=0.95, bottom=0.08)

    # ── Panel (a): Per-round latency breakdown ──
    train_s = [data[d]['train_per_round_s'] for d in defenses]
    agg_s = [data[d]['agg_per_round_s'] for d in defenses]
    total_s = [data[d]['total_time_s'] for d in defenses]
    colors_bar = [COLORS.get(d, '#888') for d in defenses]

    dtg_verify_ms = data.get('DT-Guard', {}).get('dt_verify_per_round_s', 0) * 1000
    dtg_pw_ms = data.get('DT-Guard', {}).get('dt_pw_per_round_s', 0) * 1000
    dtg_i = defenses.index('DT-Guard') if 'DT-Guard' in defenses else -1

    y = np.arange(n)
    bar_h = 0.50

    ax1.barh(y, train_s, bar_h,
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
                     color=colors_bar[i], edgecolor='#333', linewidth=0.3)

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
    ax1.set_title(f'(a) Per-round latency breakdown [ToN-IoT, {num_clients} clients]',
                  fontsize=8, pad=5, fontweight='bold')

    legend_a = [
        Patch(facecolor='#BBDEFB', edgecolor='#1565C0', label='Training'),
        Patch(facecolor='#EF5350', edgecolor='#333', label='DT Verif.'),
        Patch(facecolor='#FF8A65', edgecolor='#333', label='DT-PW'),
        Patch(facecolor='#9E9E9E', edgecolor='#333', label='Agg.'),
    ]
    ax1.legend(handles=legend_a, loc='lower right', framealpha=0.9,
               fontsize=5.5, ncol=2, borderpad=0.3, handlelength=1.0)

    # ── Panel (b): Memory efficiency ──
    peak_mems = np.array([data[d]['peak_mem_mb'] for d in defenses])
    mem_overheads = np.array([data[d]['mem_overhead_mb'] for d in defenses])

    x = np.arange(n)
    bar_width = 0.35

    bars1 = ax2.bar(x - bar_width/2, peak_mems, bar_width,
                    label='Peak memory',
                    color=[c if d != 'DT-Guard' else '#D32F2F'
                           for c, d in zip(colors_bar, defenses)],
                    edgecolor=['#B71C1C' if d == 'DT-Guard' else '#333'
                               for d in defenses],
                    linewidth=[1.5 if d == 'DT-Guard' else 0.6 for d in defenses],
                    alpha=0.85)

    bars2 = ax2.bar(x + bar_width/2, mem_overheads, bar_width,
                    label='Mem. overhead',
                    color='#E0E0E0', edgecolor='#616161', linewidth=0.6,
                    hatch='///', alpha=0.7)

    for i in range(n):
        ax2.text(x[i] - bar_width/2, peak_mems[i] + 8,
                 f'{peak_mems[i]:.0f}',
                 ha='center', va='bottom', fontsize=5.5,
                 fontweight='bold' if defenses[i] == 'DT-Guard' else 'normal',
                 color='#D32F2F' if defenses[i] == 'DT-Guard' else '#424242')
        if mem_overheads[i] > 0:
            ax2.text(x[i] + bar_width/2, mem_overheads[i] + 3,
                     f'{mem_overheads[i]:.1f}',
                     ha='center', va='bottom', fontsize=5, color='#424242')

    ax2.set_xlabel('Defense mechanism', fontsize=8)
    ax2.set_ylabel('Memory (MB)', fontsize=8)
    ax2.set_title('(b) Memory efficiency comparison [ToN-IoT]',
                  fontsize=8, pad=5, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(defenses, rotation=45, ha='right', fontsize=6.5)
    ax2.grid(axis='y', alpha=0.2, linestyle='-', linewidth=0.5)
    ax2.set_axisbelow(True)
    ax2.legend(loc='upper right', fontsize=5.5, framealpha=0.95,
               borderpad=0.3, handlelength=0.8)
    ax2.set_ylim(0, max(peak_mems) * 1.12 if len(peak_mems) > 0 else 100)

    for ext in (['pdf', 'png'] if fmt == 'pdf' else [fmt]):
        out = FIGDIR / f'fig5_overhead.{ext}'
        fig.savefig(out, dpi=rcParams['savefig.dpi'], format=ext)
        print(f"    ✓ {out}")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════
#  HELPER — Print inline numbers for paper prose
# ═══════════════════════════════════════════════════════════════════════
def print_inline_numbers():
    """Print numbers referenced in the paper text."""

    # ── Table II: Defense accuracy at 50% malicious ──
    expA = _load('paper_expA.json')
    if expA and 'ratios' in expA and '50%' in expA['ratios']:
        print("\n    ══ TABLE II — Accuracy (%) at 50% Malicious [ToN-IoT] ══")
        res = expA['ratios']['50%']['results']
        attacks = ATTACKS_5
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

        # Accuracy degradation across ratios
        ratios = list(expA['ratios'].keys())
        print("\n    ══ Accuracy degradation across ratios [ToN-IoT] ══")
        for d in ['DT-Guard', 'LUP', 'ClipCluster', 'SignGuard', 'PoC', 'FedAvg']:
            avgs = []
            for r in ratios:
                rr = expA['ratios'][r]['results']
                avgs.append(np.mean([rr.get(d, {}).get(a, {}).get('accuracy', 0) * 100
                                     for a in attacks]))
            drop = avgs[0] - avgs[-1]
            print(f"    {d:15s}  10%→50%: {avgs[0]:.1f}% → {avgs[-1]:.1f}%  (drop {drop:.1f}%)")

    # ── Gap 2: FPR ──
    res50 = _load_expA_50()
    if res50:
        print("\n    ══ FPR at 50% Malicious [ToN-IoT] ══")
        for d in SHOW_DEFS:
            fprs = [res50.get(d, {}).get(a, {}).get('fpr', 0) * 100
                    for a in ATTACKS_5]
            avg_fpr = np.mean(fprs)
            print(f"    {d:15s}  " +
                  "  ".join(f"{a[:3]}={f:.1f}%" for a, f in zip(ATTACKS_5, fprs)) +
                  f"  Avg={avg_fpr:.1f}%")

    # ── Non-IID EXP-B numbers ──
    expB = _load('paper_expB.json')
    if expB:
        print("\n    ══ Non-IID FPR [ToN-IoT] ══")
        for alpha in ['0.1', '0.5']:
            if alpha not in expB:
                continue
            print(f"    α = {alpha}:")
            for scn in ['No Attack', 'LIE']:
                if scn not in expB[alpha]:
                    continue
                for d in ['DT-Guard', 'LUP', 'ClipCluster', 'SignGuard',
                          'GeoMed', 'PoC']:
                    r = expB[alpha][scn].get(d, {})
                    print(f"      {d:15s} vs {scn:10s}  "
                          f"Acc={r.get('accuracy',0)*100:.1f}%  "
                          f"FPR={r.get('fpr',0)*100:.1f}%")

    # ── Gap 3: Fairness ──
    expC = _load('paper_expC.json')
    if expC and 'table' in expC:
        print("\n    ══ Fairness [ToN-IoT] ══")
        for s, d in expC['table'].items():
            print(f"    {s:15s}  Normal={d['normal_weight']:.4f}  "
                  f"FR={d['freerider_weight']:.4f}  "
                  f"Det={d['fr_detected']}  Acc={d['accuracy']*100:.1f}%")

    if expC and 'overhead' in expC:
        oh = expC['overhead']
        print(f"\n    ══ OVERHEAD [ToN-IoT] ══")
        print(f"    DT-PW:  {oh['dtpw_seconds']}s")
        print(f"    FedAvg: {oh['fedavg_seconds']}s")
        print(f"    Overhead: {oh['overhead_pct']}%")
        print(f"    Memory Δ: {oh['memory_delta_mb']} MB")


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════
PLOT_REGISTRY = {
    'fig2':  ('Fig. 2 — Accuracy + Detection Rate @ 50% (Gap 1)', plot_fig2),
    'fig3':  ('Fig. 3 — FPR heatmap @ 50% (Gap 2)',               plot_fig3),
    'fig3b': ('Fig. 3b — Non-IID FPR comparison (Gap 2)',         plot_fig3b),
    'fig4':  ('Fig. 4 — Weight distribution per client (Gap 3)',  plot_fig4),
    'fig4b': ('Fig. 4b — Convergence with free-riders (Gap 3)',   plot_fig4b),
    'fig5':  ('Fig. 5 — Overhead: latency + memory',             plot_fig5),
}


def main():
    parser = argparse.ArgumentParser(
        description='Generate figures for DT-Guard (ToN-IoT dataset)')
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

    print("┌──────────────────────────────────────────────────────────────┐")
    print("│  DT-Guard — ToN-IoT Paper Figures                          │")
    print("│  Fig.2  (Gap 1)  Acc + DetRate @ 50%       [single-col]    │")
    print("│  Fig.3  (Gap 2)  FPR heatmap @ 50%         [single-col]    │")
    print("│  Fig.3b (Gap 2)  Non-IID FPR comparison    [single-col]    │")
    print("│  Fig.4  (Gap 3)  Weight distribution        [2×2 grid]     │")
    print("│  Fig.4b (Gap 3)  Convergence curves         [single-col]   │")
    print("│  Fig.5           Overhead latency + memory  [2-panel]      │")
    print("└──────────────────────────────────────────────────────────────┘")
    print(f"  Format: {args.fmt.upper()}  |  DPI: {args.dpi}")
    print(f"  Data:   {RESULTS}/")
    print(f"  Output: {FIGDIR}/\n")

    for key in targets:
        if key not in PLOT_REGISTRY:
            continue
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

