#!/usr/bin/env python3
"""
Single figure justifying TabDDPM selection for 6-page IEEE paper.
Radar chart covering 4 criterion groups from đề cương §3 Kịch bản 1:
  Fidelity, Coverage & Diversity, Conditional Control, Efficiency.

Reads:  results/thesis/exp6_summary.json
Saves:  results/thesis/figures/fig2_generator_selection.png / .pdf
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from pathlib import Path

# ── Paths ──
BASE = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = BASE / 'results' / 'thesis'
FIGURE_DIR = RESULTS_DIR / 'figures'
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

# ── Load ──
with open(RESULTS_DIR / 'exp6_summary.json') as f:
    raw = json.load(f)

GEN_ORDER = ['TabDDPM', 'TabSyn', 'ForestDiffusion', 'CTGAN', 'WGAN-GP']

def M(g, k):
    return raw[g].get(k, 0)

# ── Colors — Diffusion = blue tones, GAN = red tones ──
CMAP = {
    'TabDDPM':         '#1a5276',
    'TabSyn':          '#5dade2',
    'ForestDiffusion': '#85c1e9',
    'CTGAN':           '#cb4335',
    'WGAN-GP':         '#f1948a',
}

# ── Style ──
plt.rcParams.update({
    'savefig.dpi': 300,
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'legend.fontsize': 8,
})

# ====================================================================
# Radar metrics — 8 axes, 4 criterion groups (đề cương §3)
# ====================================================================
radar_defs = [
    # ── Fidelity ──
    ('custom_tstr',                    'TSTR',          False),
    ('stats.wasserstein_dist.joint',   '1/Wasserstein', True),
    # ── Coverage & Diversity ──
    ('stats.prdc.recall',              'Recall',        False),
    ('stats.prdc.coverage',            'Coverage',      False),
    # ── Conditional Control ──
    ('oracle_label_accuracy',          'Oracle Acc',    False),
    ('dt_guard_separation',            'DT-Sep',        False),
    # ── Efficiency ──
    ('train_gen_time',                 '1/Time',        True),
    ('peak_ram_mb',                    '1/RAM',         True),
]

N_ax = len(radar_defs)
angles = np.linspace(0, 2 * np.pi, N_ax, endpoint=False).tolist()
angles += angles[:1]

# Collect raw (invert lower-is-better)
raw_v = {}
for g in GEN_ORDER:
    v = []
    for key, _, inv in radar_defs:
        val = M(g, key)
        if inv:
            val = 1.0 / (abs(val) + 1e-6)
        v.append(val)
    raw_v[g] = np.array(v)

arr = np.stack([raw_v[g] for g in GEN_ORDER])
lo, hi = arr.min(0), arr.max(0)
span = hi - lo
span[span < 1e-10] = 1.0

# ── Composite score (for annotation) ──
high_keys = [
    'custom_tstr', 'stats.prdc.precision', 'stats.prdc.recall',
    'stats.prdc.coverage', 'stats.alpha_precision.authenticity_OC',
    'dt_guard_separation', 'oracle_label_accuracy',
]
low_keys = [
    'stats.wasserstein_dist.joint',
    'stats.jensenshannon_dist.marginal',
    'sanity.nearest_syn_neighbor_distance.mean',
    'train_gen_time',
    'peak_ram_mb',
]
scores = {g: 0.0 for g in GEN_ORDER}
n_crit = 0
for key in high_keys:
    vs = np.array([M(g, key) for g in GEN_ORDER])
    mn, mx = vs.min(), vs.max()
    r = max(mx - mn, 1e-10)
    for i, g in enumerate(GEN_ORDER):
        scores[g] += (vs[i] - mn) / r
    n_crit += 1
for key in low_keys:
    vs = np.array([M(g, key) for g in GEN_ORDER])
    mn, mx = vs.min(), vs.max()
    r = max(mx - mn, 1e-10)
    for i, g in enumerate(GEN_ORDER):
        scores[g] += 1.0 - (vs[i] - mn) / r
    n_crit += 1
for g in GEN_ORDER:
    scores[g] = scores[g] / n_crit * 10

# ====================================================================
# Figure — single radar
# ====================================================================
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

# Sector shading to label the 4 groups
group_ranges = [
    (0, 2, 'Fidelity',           '#e8f6f3'),
    (2, 4, 'Coverage',           '#fef9e7'),
    (4, 6, 'Cond. Control',     '#fdedec'),
    (6, 8, 'Efficiency',         '#eaf2f8'),
]
for start, end, label, color in group_ranges:
    a0 = angles[start]
    a1 = angles[end] if end < N_ax else angles[0] + 2 * np.pi
    theta = np.linspace(a0, a1, 50)
    ax.fill_between(theta, 0, 1.12, alpha=0.25, color=color, zorder=0)
    mid_angle = (a0 + a1) / 2
    ax.text(mid_angle, 1.28, label, ha='center', va='center',
            fontsize=7, fontstyle='italic', color='#555', fontweight='bold')

# Plot each generator
for g in GEN_ORDER:
    normed = ((raw_v[g] - lo) / span).tolist()
    normed += normed[:1]
    lw   = 2.8 if g == 'TabDDPM' else 1.2
    ms   = 6   if g == 'TabDDPM' else 3
    afil = 0.15 if g == 'TabDDPM' else 0.02
    zord = 4   if g == 'TabDDPM' else 2
    ax.plot(angles, normed, 'o-', lw=lw, label=g,
            color=CMAP[g], markersize=ms, zorder=zord)
    ax.fill(angles, normed, alpha=afil, color=CMAP[g])

ax.set_xticks(angles[:-1])
ax.set_xticklabels([lbl for _, lbl, _ in radar_defs], fontsize=9)
ax.set_ylim(0, 1.12)
ax.set_yticks([0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(['0.25', '0.50', '0.75', '1.00'], fontsize=6.5, alpha=0.4)

# Legend with composite score
ranked = sorted(GEN_ORDER, key=lambda g: scores[g], reverse=True)
legend_labels = [f'{g}  (score {scores[g]:.1f})' for g in ranked]
handles = [plt.Line2D([0], [0], color=CMAP[g], lw=2.8 if g == 'TabDDPM' else 1.2,
                       marker='o', markersize=5)
           for g in ranked]
ax.legend(handles, legend_labels, loc='upper left', bbox_to_anchor=(-0.25, -0.05),
          fontsize=8, framealpha=0.95, title='Generator (composite score 0-10)',
          title_fontsize=8.5)

ax.set_title('Challenge Data Generator Comparison\n(min-max normalized across 4 criterion groups)',
             fontweight='bold', pad=25, fontsize=11)

# ── Save ──
for ext in ('png', 'pdf'):
    out = FIGURE_DIR / f'fig_generator_selection.{ext}'
    fig.savefig(out, bbox_inches='tight', facecolor='white')
    print(f'  Saved {out}')

plt.close()
print('  Done.')

