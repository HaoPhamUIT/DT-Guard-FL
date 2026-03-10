#!/usr/bin/env python3
"""
Generate publication-quality plots for all 3 thesis scenarios.

Scenario 1 (Exp6): Data Generator A/B Testing
Scenario 2 (Exp3/7): Defense Comparison under 5 attacks × 3 malicious ratios
Scenario 3 (Exp4/5): Non-IID Robustness + Shapley Ablation

Usage:
    python generate_plots.py                   # All available plots
    python generate_plots.py --scenario 2      # Only scenario 2
"""

import argparse
import json
import pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Style
plt.rcParams.update({
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 12,
    'legend.fontsize': 9,
    'figure.figsize': (10, 6),
})
sns.set_palette("husl")

RESULTS_DIR = Path('results/paper')
FIGURE_DIR = RESULTS_DIR / 'figures'

DEFENSE_COLORS = {
    'DT-Guard': '#e74c3c',
    'LUP': '#3498db',
    'ClipCluster': '#2ecc71',
    'SignGuard': '#9b59b6',
    'GeoMed': '#f39c12',
    'PoC': '#1abc9c',
    'FedAvg': '#95a5a6',
    'Krum': '#e67e22',
    'Median': '#34495e',
    'Trimmed Mean': '#7f8c8d',
}


# =============================================================================
# Scenario 1: Data Generator A/B Testing (Exp6)
# =============================================================================

def plot_scenario1():
    """Plots for Kịch bản 1 — Generator comparison.
    Reads from exp6_summary.json (output of run_experiment6_datagen.py)."""

    # Try exp6_summary.json first (new format), then exp6_datagen.json (old)
    data_path = RESULTS_DIR / 'exp6_summary.json'
    if not data_path.exists():
        data_path = RESULTS_DIR / 'exp6_datagen.json'
    if not data_path.exists():
        print("  ⚠ No exp6 results found — run run_experiment6_datagen.py first")
        return

    with open(data_path) as f:
        raw = json.load(f)

    # Normalize keys: map from exp6_summary.json format to plot-friendly names
    # Detect format by checking if first generator has 'custom_tstr' key
    first_gen = next((k for k in raw if k != 'trtr_baseline'), None)
    if first_gen is None:
        print("  ⚠ No generator data found in exp6 results")
        return

    is_new_format = 'custom_tstr' in raw.get(first_gen, {})

    if is_new_format:
        trtr = raw[first_gen].get('trtr_baseline', 0.75)
        gen_names = [k for k in raw.keys()]
        data = {}
        for g in gen_names:
            r = raw[g]
            data[g] = {
                'family':     r.get('family', ''),
                'year':       r.get('year', 0),
                'tstr':       r.get('custom_tstr', 0),
                'wasserstein': r.get('stats.wasserstein_dist.joint', 0),
                'jsd':        r.get('stats.jensenshannon_dist.marginal', 0),
                'dcr':        r.get('sanity.nearest_syn_neighbor_distance.mean', 0),
                'precision':  r.get('stats.prdc.precision', 0),
                'recall':     r.get('stats.prdc.recall', 0),
                'coverage':   r.get('stats.prdc.coverage', 0),
                'authenticity': r.get('stats.alpha_precision.authenticity_OC', 0),
                'oracle_acc': r.get('oracle_label_accuracy', 0),
                'dt_sep':     r.get('dt_guard_separation', 0),
                'train_time': r.get('train_gen_time', 0),
                'peak_ram':   r.get('peak_ram_mb', 0),
            }
    else:
        # Old format fallback
        trtr = raw.pop('trtr_baseline', 0.7)
        gen_names = list(raw.keys())
        data = {}
        for g in gen_names:
            r = raw[g]
            data[g] = {
                'family':     'GAN' if 'GAN' in g else 'Diffusion',
                'year':       0,
                'tstr':       r.get('tstr_mean', 0),
                'wasserstein': r.get('wasserstein', 0),
                'jsd':        r.get('tvd', 0),
                'dcr':        r.get('dcr', 0),
                'precision':  0,
                'recall':     0,
                'coverage':   0,
                'authenticity': 0,
                'oracle_acc': r.get('label_accuracy', 0),
                'dt_sep':     r.get('dt_separation', 0),
                'train_time': r.get('train_time', 0),
                'peak_ram':   r.get('vram_mb', 0),
            }

    colors_gen = sns.color_palette("Set2", len(gen_names))
    family_colors = {'Diffusion': '#3498db', 'GAN': '#e74c3c'}

    # ---- Fig 1: TSTR Comparison (Bar chart) ----
    fig, ax = plt.subplots(figsize=(10, 5))
    tstr_vals = [data[g]['tstr'] * 100 for g in gen_names]
    bar_colors = [family_colors.get(data[g]['family'], '#95a5a6') for g in gen_names]

    bars = ax.bar(gen_names, tstr_vals, color=bar_colors,
                  edgecolor='black', linewidth=0.8, alpha=0.9, zorder=3)
    ax.axhline(y=trtr * 100, color='red', linestyle='--', linewidth=2,
               label=f'TRTR baseline ({trtr*100:.1f}%)', zorder=2)
    ax.set_ylabel('TSTR Accuracy (%)')
    ax.set_title('Fig 1: Generator Fidelity — Train on Synthetic, Test on Real')

    # Legend with family colors
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#3498db', edgecolor='black', label='Diffusion'),
        Patch(facecolor='#e74c3c', edgecolor='black', label='GAN'),
        plt.Line2D([0], [0], color='red', linestyle='--', linewidth=2, label=f'TRTR ({trtr*100:.1f}%)')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    y_max = max(tstr_vals + [trtr*100])
    ax.set_ylim(-y_max*0.05, y_max * 1.15)  # Start below 0 to show 0 values
    ax.grid(axis='y', alpha=0.3, zorder=1)
    for bar, val in zip(bars, tstr_vals):
        y_pos = max(bar.get_height(), y_max*0.02) + y_max*0.01
        ax.text(bar.get_x() + bar.get_width()/2, y_pos,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold', zorder=4)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / 'fig_s1_tstr_comparison.png', bbox_inches='tight')
    plt.close()
    print("  ✓ fig_s1_tstr_comparison.png")

    # ---- Fig 2: Radar chart — multi-metric ----
    # Higher-is-better metrics (raw), and lower-is-better (inverted for radar)
    radar_metrics = [
        ('tstr',       'TSTR',          False),
        ('precision',  'Precision',     False),
        ('recall',     'Recall',        False),
        ('coverage',   'Coverage',      False),
        ('authenticity','Authenticity',  False),
        ('oracle_acc', 'Oracle Acc',    False),
        ('dt_sep',     'DT-Guard Sep',  False),
        ('wasserstein','1/Wasserstein', True),   # invert
        ('jsd',        '1/JSD',         True),   # invert
        ('train_time', '1/Time',        True),   # invert
    ]

    N = len(radar_metrics)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    # Collect raw values for normalization
    raw_vals = {g: [] for g in gen_names}
    for g in gen_names:
        for key, _, invert in radar_metrics:
            v = data[g].get(key, 0)
            if invert:
                v = 1.0 / (abs(v) + 1e-6)
            raw_vals[g].append(v)

    # Min-max normalize across generators for each metric
    n_metrics = len(radar_metrics)
    all_raw = np.array([raw_vals[g] for g in gen_names])  # (n_gen, n_metrics)
    mins = all_raw.min(axis=0)
    maxs = all_raw.max(axis=0)
    ranges = maxs - mins
    ranges[ranges < 1e-10] = 1.0  # avoid div by zero

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
    for i, g in enumerate(gen_names):
        normed = ((np.array(raw_vals[g]) - mins) / ranges).tolist()
        normed += normed[:1]
        ax.plot(angles, normed, 'o-', linewidth=2, label=g, color=colors_gen[i])
        ax.fill(angles, normed, alpha=0.08, color=colors_gen[i])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([lbl for _, lbl, _ in radar_metrics], fontsize=9)
    ax.set_ylim(0, 1.1)
    ax.set_title('Fig 2: Multi-Metric Generator Comparison', fontsize=14, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1))
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / 'fig_s1_radar_generators.png', bbox_inches='tight')
    plt.close()
    print("  ✓ fig_s1_radar_generators.png")

    # ---- Fig 3: Cost comparison (Time + RAM) ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    train_times = [data[g]['train_time'] for g in gen_names]
    ram_vals = [data[g]['peak_ram'] for g in gen_names]

    ax1.barh(gen_names, train_times, color=bar_colors, edgecolor='black', alpha=0.9, zorder=3)
    ax1.set_xlabel('Training + Generation Time (s)')
    ax1.set_title('Training Cost')
    ax1.grid(axis='x', alpha=0.3, zorder=1)
    max_time = max(train_times) if train_times else 1
    ax1.set_xlim(-max_time*0.05, max_time*1.15)
    for i, v in enumerate(train_times):
        x_pos = max(v, max_time*0.02) + max_time*0.02
        ax1.text(x_pos, i, f'{v:.1f}s', va='center', fontsize=10, zorder=4)

    ax2.barh(gen_names, ram_vals, color=bar_colors, edgecolor='black', alpha=0.9, zorder=3)
    ax2.set_xlabel('Peak RAM (MB)')
    ax2.set_title('Memory Usage')
    ax2.grid(axis='x', alpha=0.3, zorder=1)
    max_ram = max(ram_vals) if ram_vals else 1
    ax2.set_xlim(-max_ram*0.05, max_ram*1.15)
    for i, v in enumerate(ram_vals):
        x_pos = max(v, max_ram*0.02) + max_ram*0.02
        ax2.text(x_pos, i, f'{v:.1f}MB', va='center', fontsize=10, zorder=4)

    plt.suptitle('Fig 3: Computational Cost Comparison', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / 'fig_s1_cost_comparison.png', bbox_inches='tight')
    plt.close()
    print("  ✓ fig_s1_cost_comparison.png")

    # ---- Fig 4: DT-Guard Integration (Oracle Acc + DT-Guard Separation) ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    oracle_vals = [data[g]['oracle_acc'] * 100 for g in gen_names]
    dt_sep_vals = [data[g]['dt_sep'] for g in gen_names]

    bars1 = ax1.bar(gen_names, oracle_vals, color=bar_colors,
                    edgecolor='black', alpha=0.9, zorder=3)
    ax1.set_ylabel('Oracle Label Accuracy (%)')
    ax1.set_title('Conditional Control')
    y_max1 = max(oracle_vals) if oracle_vals else 1
    ax1.set_ylim(-y_max1*0.05, y_max1 * 1.2)
    ax1.grid(axis='y', alpha=0.3, zorder=1)
    for bar, val in zip(bars1, oracle_vals):
        y_pos = max(bar.get_height(), y_max1*0.02) + y_max1*0.01
        ax1.text(bar.get_x() + bar.get_width()/2, y_pos,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold', zorder=4)

    bars2 = ax2.bar(gen_names, dt_sep_vals, color=bar_colors,
                    edgecolor='black', alpha=0.9, zorder=3)
    ax2.set_ylabel('DT-Guard Separation Score')
    ax2.set_title('DT-Guard Integration')
    y_max2 = max(max(dt_sep_vals), 0.01) if dt_sep_vals else 0.01
    ax2.set_ylim(-y_max2*0.05, y_max2 * 1.3)
    ax2.grid(axis='y', alpha=0.3, zorder=1)
    for bar, val in zip(bars2, dt_sep_vals):
        y_pos = max(bar.get_height(), y_max2*0.02) + y_max2*0.01
        ax2.text(bar.get_x() + bar.get_width()/2, y_pos,
                f'{val:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold', zorder=4)

    plt.suptitle('Fig 4: Conditional Control & DT-Guard Integration',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / 'fig_s1_dtguard_integration.png', bbox_inches='tight')
    plt.close()
    print("  ✓ fig_s1_dtguard_integration.png")


# =============================================================================
# Scenario 2: Defense Comparison (Exp3 / Exp7)
# =============================================================================

def plot_scenario2():
    """Plots for Kịch bản 2 — Defense performance."""
    # Try unified first, then single exp3
    unified_path = RESULTS_DIR / 'exp7_unified.json'
    single_path = RESULTS_DIR / 'exp3_summary.json'

    if unified_path.exists():
        with open(unified_path) as f:
            data = json.load(f)
        ratios = sorted([int(r) for r in data.keys()])
    elif single_path.exists():
        with open(single_path) as f:
            single = json.load(f)
        data = {'50': single}
        ratios = [50]
    else:
        # Try pickle
        pkl_path = RESULTS_DIR / 'exp3_comprehensive.pkl'
        if pkl_path.exists():
            with open(pkl_path, 'rb') as f:
                raw = pickle.load(f)
            results = raw['results']
            data = {'50': {}}
            for d, atks in results.items():
                data['50'][d] = {}
                for a, r in atks.items():
                    data['50'][d][a] = {
                        'accuracy': round(r.get('final_accuracy', 0), 4),
                        'detection_rate': round(r.get('detection_rate', 0), 4),
                        'fpr': round(r.get('false_positive_rate', 0), 4),
                    }
            ratios = [50]
        else:
            print("  ⚠ No exp3/exp7 results found")
            return

    attacks = ['Backdoor', 'LIE', 'Min-Max', 'Min-Sum', 'MPAF']
    defenses = list(data[str(ratios[0])].keys())

    # Fig 4: Accuracy heatmap per ratio
    for ratio in ratios:
        fig, ax = plt.subplots(figsize=(12, max(6, len(defenses) * 0.5)))
        rd = data[str(ratio)]
        matrix = []
        d_names = []
        for d in defenses:
            if d not in rd:
                continue
            row = []
            for a in ['No Attack'] + attacks:
                row.append(rd[d].get(a, {}).get('accuracy', 0) * 100)
            matrix.append(row)
            d_names.append(d)

        matrix = np.array(matrix)
        sns.heatmap(matrix, annot=True, fmt='.1f', cmap='RdYlGn',
                    xticklabels=['No Attack'] + attacks, yticklabels=d_names,
                    vmin=0, vmax=100, ax=ax, linewidths=0.5,
                    cbar_kws={'label': 'Accuracy (%)'})
        ax.set_title(f'Accuracy Under Attacks ({ratio}% Malicious)', fontweight='bold')
        ax.set_ylabel('Defense Method')
        plt.tight_layout()
        plt.savefig(FIGURE_DIR / f'fig_s2_accuracy_heatmap_{ratio}pct.png', bbox_inches='tight')
        plt.close()
        print(f"  ✓ fig_s2_accuracy_heatmap_{ratio}pct.png")

    # Fig 5: Grouped bar chart — DT-Guard vs top baselines
    if len(ratios) >= 2:
        fig, axes = plt.subplots(1, len(ratios), figsize=(6 * len(ratios), 6), sharey=True)
        if len(ratios) == 1:
            axes = [axes]
        top_defenses = ['DT-Guard', 'LUP', 'ClipCluster', 'SignGuard', 'GeoMed']
        top_defenses = [d for d in top_defenses if d in defenses]

        for ax_idx, ratio in enumerate(ratios):
            ax = axes[ax_idx]
            rd = data[str(ratio)]
            x = np.arange(len(attacks))
            width = 0.8 / len(top_defenses)
            for i, d in enumerate(top_defenses):
                accs = [rd.get(d, {}).get(a, {}).get('accuracy', 0) * 100 for a in attacks]
                offset = (i - len(top_defenses)/2 + 0.5) * width
                bars = ax.bar(x + offset, accs, width, label=d,
                       color=DEFENSE_COLORS.get(d, '#999'), alpha=0.85, edgecolor='black', linewidth=0.5, zorder=3)
                # Add value labels for bars
                for bar_idx, (bar, val) in enumerate(zip(bars, accs)):
                    if val > 0 or bar.get_height() == 0:
                        y_pos = max(bar.get_height(), 1) + 1
                        ax.text(bar.get_x() + bar.get_width()/2, y_pos,
                               f'{val:.0f}', ha='center', va='bottom', fontsize=7, zorder=4)
            ax.set_xticks(x)
            ax.set_xticklabels(attacks, rotation=30, ha='right')
            ax.set_title(f'{ratio}% Malicious')
            ax.set_ylabel('Accuracy (%)')
            ax.set_ylim(-5, 105)  # Start below 0 to show 0 values
            ax.grid(axis='y', alpha=0.3, zorder=1)
            if ax_idx == 0:
                ax.legend(fontsize=8)

        plt.suptitle('Defense Accuracy Across Malicious Ratios', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(FIGURE_DIR / 'fig_s2_accuracy_multi_ratio.png', bbox_inches='tight')
        plt.close()
        print("  ✓ fig_s2_accuracy_multi_ratio.png")

    # Fig 6: Error Rate (degradation) bar chart
    ratio_key = str(ratios[-1])  # Use highest ratio
    rd = data[ratio_key]
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(attacks))
    top_d = [d for d in ['DT-Guard', 'LUP', 'ClipCluster', 'SignGuard', 'GeoMed', 'PoC']
             if d in rd]
    width = 0.8 / len(top_d)
    for i, d in enumerate(top_d):
        no_atk = rd.get(d, {}).get('No Attack', {}).get('accuracy', 1)
        ers = []
        for a in attacks:
            atk_acc = rd.get(d, {}).get(a, {}).get('accuracy', 0)
            er = (1 - atk_acc / no_atk) * 100 if no_atk > 0 else 100
            ers.append(max(0, er))
        offset = (i - len(top_d)/2 + 0.5) * width
        bars = ax.bar(x + offset, ers, width, label=d,
               color=DEFENSE_COLORS.get(d, '#999'), alpha=0.85, edgecolor='black', linewidth=0.5, zorder=3)
        # Add value labels
        for bar, val in zip(bars, ers):
            if val >= 0:
                y_pos = max(bar.get_height(), 0.5) + 0.5
                ax.text(bar.get_x() + bar.get_width()/2, y_pos,
                       f'{val:.1f}', ha='center', va='bottom', fontsize=7, zorder=4)
    ax.set_xticks(x)
    ax.set_xticklabels(attacks, rotation=15, ha='right')
    ax.set_ylabel('Error Rate (%)')
    ax.set_title(f'Error Rate Under Attacks ({ratios[-1]}% Malicious) — Lower is Better', fontweight='bold')
    ax.legend()
    ax.set_ylim(-2, None)  # Start below 0
    ax.grid(axis='y', alpha=0.3, zorder=1)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / 'fig_s2_error_rate.png', bbox_inches='tight')
    plt.close()
    print("  ✓ fig_s2_error_rate.png")

    # Fig 7: Detection Rate + FPR side-by-side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Add small jitter to avoid overlapping lines
    jitter_scale = 0.03
    # Sort to draw DT-Guard last (highest zorder)
    plot_order = [d for d in top_d if d != 'DT-Guard'] + (['DT-Guard'] if 'DT-Guard' in top_d else [])
    
    for idx, d in enumerate(plot_order):
        is_dtguard = (d == 'DT-Guard')
        jitter = (idx - len(plot_order)/2) * jitter_scale
        x_pos = np.arange(len(attacks)) + jitter
        
        # DT-Guard gets special styling
        lw = 3.5 if is_dtguard else 2.5
        ms = 10 if is_dtguard else 8
        mew = 2.0 if is_dtguard else 1.5
        zo = 100 if is_dtguard else 3 + idx
        
        det_vals = [rd.get(d, {}).get(a, {}).get('detection_rate', 0) * 100 for a in attacks]
        ax1.plot(x_pos, det_vals, 'o-', linewidth=lw, label=d,
                 color=DEFENSE_COLORS.get(d, '#999'), markersize=ms, 
                 markeredgecolor='white', markeredgewidth=mew, zorder=zo, alpha=0.9)
        
        fpr_vals = [rd.get(d, {}).get(a, {}).get('fpr', 0) * 100 for a in attacks]
        ax2.plot(x_pos, fpr_vals, 'o-', linewidth=lw, label=d,
                 color=DEFENSE_COLORS.get(d, '#999'), markersize=ms,
                 markeredgecolor='white', markeredgewidth=mew, zorder=zo, alpha=0.9)

    ax1.set_xticks(range(len(attacks)))
    ax1.set_xticklabels(attacks, rotation=20, ha='right')
    ax1.set_ylabel('Detection Rate (%)')
    ax1.set_title('Detection Rate (higher = better)')
    ax1.legend(fontsize=8)
    ax1.set_ylim(-5, 105)
    ax1.grid(axis='y', alpha=0.3, zorder=1)

    ax2.set_xticks(range(len(attacks)))
    ax2.set_xticklabels(attacks, rotation=20, ha='right')
    ax2.set_ylabel('False Positive Rate (%)')
    ax2.set_title('FPR (lower = better)')
    ax2.legend(fontsize=8)
    ax2.set_ylim(-2, None)
    ax2.grid(axis='y', alpha=0.3, zorder=1)

    plt.suptitle(f'Detection & FPR ({ratios[-1]}% Malicious)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / 'fig_s2_detection_fpr.png', bbox_inches='tight')
    plt.close()
    print("  ✓ fig_s2_detection_fpr.png")


# =============================================================================
# Scenario 3: Ablation — Non-IID + Shapley (Exp4 + Exp5)
# =============================================================================

def plot_scenario3():
    """Plots for Kịch bản 3 — Free-rider detection (Gap 3).

    3 figures to prove DT-PW detects free-riders:
      Fig 1: Per-client weight bars — DT-PW vs Shapley vs Trust-Score vs Uniform
      Fig 2: Convergence curves — 5 strategies × 2 scenarios
      Fig 3: Grouped bar — avg weight Normal vs FreeRider per strategy
    """
    exp5_path = RESULTS_DIR / 'exp5_dtpw.json'
    if not exp5_path.exists():
        print("  ⚠ No exp5 results — skipping Gap 3 plots")
        return

    with open(exp5_path) as f:
        d = json.load(f)

    cfg = d['config']
    wh = d.get('weight_history', {})
    ah = d.get('accuracy_history', {})
    n = cfg.get('num_clients', 20)
    fr = cfg.get('free_rider_idx', [])
    nr = cfg.get('normal_idx', [])

    # Role lookup & colors
    role = {}
    for i in nr: role[i] = 'Normal'
    for i in fr: role[i] = 'FreeRider'
    RC = {'Normal': '#4C72B0', 'FreeRider': '#8C8C8C'}

    # Helper: get last-5-round average weights
    def avg_weights(strat_key):
        if strat_key not in wh or 'No Attack' not in wh[strat_key]:
            return np.zeros(n)
        w = np.array(wh[strat_key]['No Attack'])
        return w[-5:].mean(axis=0) if len(w) >= 5 else w.mean(axis=0)

    strats = [
        ('DT-PW (Ours)',      'DT-PW (Ours)'),
        ('Shapley',           'Shapley'),
        ('Trust-Score (LUP)', 'Trust-Score (LUP)'),
        ('Uniform',           'Uniform'),
    ]

    # =================================================================
    # Fig 1: TABLE B as line plot - Weight evolution over rounds
    # =================================================================
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()
    
    for ax_idx, (label, key) in enumerate(strats):
        ax = axes[ax_idx]
        if key not in wh or 'No Attack' not in wh[key]:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(label, fontweight='bold')
            continue
        
        w_hist = np.array(wh[key]['No Attack'])
        rounds = np.arange(1, len(w_hist) + 1)
        
        # Plot Normal clients (thin lines)
        for i in nr:
            ax.plot(rounds, w_hist[:, i], '-', linewidth=0.8, color='#4C72B0', alpha=0.3)
        
        # Plot FreeRider clients (thick lines)
        for i in fr:
            ax.plot(rounds, w_hist[:, i], '-', linewidth=2, color='#8C8C8C', alpha=0.8)
        
        # Add mean lines
        if nr:
            normal_mean = w_hist[:, nr].mean(axis=1)
            ax.plot(rounds, normal_mean, '-', linewidth=3, color='#4C72B0', 
                   label=f'Normal (avg)', zorder=10)
        if fr:
            fr_mean = w_hist[:, fr].mean(axis=1)
            ax.plot(rounds, fr_mean, '-', linewidth=3, color='#8C8C8C', 
                   label=f'FreeRider (avg)', zorder=10)
        
        ax.set_xlabel('FL Round')
        ax.set_ylabel('Aggregation Weight')
        ax.set_title(label, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('TABLE B: Weight Evolution Over Rounds\n'
                 'Only DT-PW consistently assigns zero weight to free-riders (gray)',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / 'fig_s3_table_b_lines.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ fig_s3_table_b_lines.png")

    # =================================================================
    # Fig 2: DT-PW score by role over rounds (line plot)
    # =================================================================
    score_data = d.get('score_history', {}).get('DT-PW (Ours)', {}).get('No Attack', [])
    if score_data:
        sh_arr = np.array(score_data)
        rounds = np.arange(1, len(sh_arr) + 1)

        fig, ax = plt.subplots(figsize=(10, 6))
        for role_name, color in [('Normal', '#4C72B0'), ('FreeRider', '#8C8C8C')]:
            idx_list = [i for i, r in role.items() if r == role_name]
            if not idx_list: continue
            role_mean = sh_arr[:, idx_list].mean(axis=1)
            role_std = sh_arr[:, idx_list].std(axis=1)
            ax.plot(rounds, role_mean, '-o', linewidth=2, markersize=4,
                    color=color, label=f'{role_name} ({len(idx_list)} clients)')
            ax.fill_between(rounds, role_mean - role_std, role_mean + role_std,
                            alpha=0.15, color=color)

        ax.set_xlabel('FL Round')
        ax.set_ylabel('Average DT-PW Score')
        ax.set_title('DT-PW Contribution Score by Client Role\n'
                     '(Free-riders correctly receive near-zero contribution)',
                     fontweight='bold')
        ax.legend(); ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(FIGURE_DIR / 'fig_s3_dtpw_by_role.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ fig_s3_dtpw_by_role.png")

    # =================================================================
    # Fig 3: Per-client weight — 4 panels side by side
    # =================================================================
    fig, axes = plt.subplots(1, 4, figsize=(20, 4.5), sharey=True)
    for ax_i, (label, key) in enumerate(strats):
        w = avg_weights(key)
        colors = [RC.get(role.get(i, 'Normal'), '#4C72B0') for i in range(n)]
        axes[ax_i].bar(range(n), w, color=colors, edgecolor='black',
                       linewidth=0.4, width=0.7)
        axes[ax_i].set_xlabel('Client ID')
        axes[ax_i].set_title(label, fontweight='bold')
        axes[ax_i].set_xticks(range(0, n, 4))
        axes[ax_i].grid(axis='y', alpha=0.3)
        if fr:
            axes[ax_i].axvspan(min(fr)-0.5, max(fr)+0.5, alpha=0.08, color='red')
    axes[0].set_ylabel('Aggregation Weight')

    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(fc=c, ec='black', label=r) for r, c in RC.items()],
               loc='lower center', ncol=3, fontsize=11, bbox_to_anchor=(0.5, -0.04))
    plt.suptitle('Weight Assignment — Only DT-PW Suppresses Free-Riders (gray)',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / 'fig_s3_weight_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ fig_s3_weight_comparison.png")

    # =================================================================
    # Fig 4: Convergence — No Attack
    # =================================================================
    styles = {
        'DT-PW (Ours)':      ('o-', '#2CA02C', 'DT-PW'),
        'Shapley':            ('D-', '#FF7F0E', 'Shapley'),
        'Trust-Score (LUP)':  ('s-', '#D62728', 'Trust-Score'),
        'Uniform':            ('^-', '#9467BD', 'Uniform'),
        'FedAvg':             ('x-', '#8C564B', 'FedAvg'),
    }
    scn_list = [s for s in ['No Attack']
                if any(s in ah.get(k, {}) for k in styles)]

    if scn_list:
        fig, axes = plt.subplots(1, len(scn_list), figsize=(7*len(scn_list), 5),
                                 squeeze=False)
        for ax_i, scn in enumerate(scn_list):
            ax = axes[0][ax_i]
            for k, (sty, clr, lbl) in styles.items():
                if k in ah and scn in ah[k]:
                    h = ah[k][scn]
                    ax.plot(range(1, len(h)+1), [v*100 for v in h],
                            sty, lw=2, ms=5, color=clr, label=lbl)
            ax.set_xlabel('FL Round'); ax.set_ylabel('Accuracy (%)')
            ax.set_title(scn, fontweight='bold')
            ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
        plt.suptitle('Convergence with Free-Riders', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(FIGURE_DIR / 'fig_s3_convergence.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ fig_s3_convergence.png")
    else:
        print("  ⚠ No accuracy_history — skipping convergence plot")

    # =================================================================
    # Fig 5: Grouped bar — avg weight Normal vs FreeRider
    # =================================================================
    labels = ['DT-PW\n(Ours)', 'Shapley', 'Trust-\nScore', 'Uniform']
    keys   = [k for _, k in strats]
    w_normal, w_freerider = [], []
    for k in keys:
        w = avg_weights(k)
        w_normal.append(np.mean([w[i] for i in nr]) if nr else 0)
        w_freerider.append(np.mean([w[i] for i in fr]) if fr else 0)

    x = np.arange(len(keys))
    bw = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    b1 = ax.bar(x - bw/2, w_normal,    bw, label='Normal',    color='#4C72B0', ec='black', lw=0.5)
    b2 = ax.bar(x + bw/2, w_freerider, bw, label='FreeRider', color='#8C8C8C', ec='black', lw=0.5)
    for bars in [b1, b2]:
        for bar in bars:
            h = bar.get_height()
            txt = f'{h:.3f}' if h > 0.001 else '0'
            clr = 'black' if h > 0.001 else 'red'
            ax.text(bar.get_x() + bar.get_width()/2, max(h, 0.002) + 0.002,
                    txt, ha='center', va='bottom', fontsize=9, fontweight='bold', color=clr)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('Average Weight')
    ax.set_title('Average Weight by Role — DT-PW: Free-Rider = 0', fontweight='bold')
    ax.legend(fontsize=10); ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / 'fig_s3_role_weight.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ fig_s3_role_weight.png")


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Generate thesis plots')
    parser.add_argument('--scenario', type=int, default=0,
                        help='1, 2, or 3. 0=all.')
    args = parser.parse_args()

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("  GENERATING THESIS PLOTS")
    print("=" * 80)

    if args.scenario in (0, 1):
        print("\n  --- Scenario 1: Data Generator A/B Testing ---")
        plot_scenario1()

    if args.scenario in (0, 2):
        print("\n  --- Scenario 2: Defense Comparison ---")
        plot_scenario2()

    if args.scenario in (0, 3):
        print("\n  --- Scenario 3: Ablation Studies ---")
        plot_scenario3()

    print(f"\n  ✅ All plots saved to {FIGURE_DIR}/")


if __name__ == '__main__':
    main()


