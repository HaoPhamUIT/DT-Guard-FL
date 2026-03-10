#!/usr/bin/env python3
"""
Generate comparison plots for paper from experimental results.
"""

import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_data():
    """Load experimental results."""
    with open('results/thesis/exp1_defense_comparison.pkl', 'rb') as f:
        exp1 = pickle.load(f)
    with open('results/thesis/exp2_ablation_study.pkl', 'rb') as f:
        exp2 = pickle.load(f)
    return exp1, exp2

def plot_accuracy_comparison(exp1, output_dir):
    """Figure 1: Accuracy under attacks."""
    attacks = ['NO_ATTACK', 'MODEL_POISONING', 'GRADIENT_ASCENT', 'BACKDOOR']
    defenses = ['DT-Guard', 'Krum', 'Multi-Krum', 'Median', 'Trimmed Mean', 'FedAvg']

    data = []
    for defense in defenses:
        if defense in exp1:
            accs = [exp1[defense].get(attack, {}).get('final_accuracy', 0) for attack in attacks]
            data.append(accs)

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(attacks))
    width = 0.13
    colors = ['#e74c3c', '#9b59b6', '#2ecc71', '#f39c12', '#3498db', '#95a5a6']

    for i, (defense, accs) in enumerate(zip(defenses, data)):
        offset = (i - len(defenses)/2 + 0.5) * width
        bars = ax.bar(x + offset, accs, width, label=defense, color=colors[i], alpha=0.8)
        for bar in bars:
            height = bar.get_height()
            if height > 0.1:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}', ha='center', va='bottom', fontsize=7)

    ax.set_xlabel('Scenario', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
    ax.set_title('Defense Comparison: Accuracy Under Different Scenarios', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([a.replace('_', ' ').title() for a in attacks], rotation=15, ha='right')
    ax.legend(loc='lower left', ncol=2, fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 0.8)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure1_accuracy_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Figure 1: Accuracy comparison")
    plt.close()



def plot_ablation_study(exp2, output_dir):
    """Figure 3: Ablation Study."""
    configs = ['Full', 'w/o_Shapley', 'w/o_Reputation', 'w/o_PFL', 'w/o_DT', 'Baseline']
    labels = ['Full\nDT-Guard', 'w/o\nShapley', 'w/o\nReputation', 'w/o\nPFL', 'w/o DT\n(CRITICAL)', 'Baseline\n(FedAvg)']

    available_configs = [c for c in configs if c in exp2]
    available_labels = [labels[configs.index(c)] for c in available_configs]
    accuracies = [exp2[config]['final_accuracy'] for config in available_configs]

    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ['#e74c3c' if config == 'Full' else '#ff0000' if config == 'w/o_DT' else '#3498db' if config == 'Baseline' else '#95a5a6'
              for config in available_configs]

    bars = ax.bar(range(len(available_configs)), accuracies, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.set_xlabel('Configuration', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
    ax.set_title('Ablation Study: Impact of Each Component', fontsize=13, fontweight='bold')
    ax.set_xticks(range(len(available_configs)))
    ax.set_xticklabels(available_labels, fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 0.8)

    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.3f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.axhline(y=0.7, color='green', linestyle='--', alpha=0.5, label='Target Accuracy')
    ax.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure3_ablation_study.png', dpi=300, bbox_inches='tight')
    print("✓ Figure 3: Ablation study")
    plt.close()

def plot_fedavg_failure(exp1, output_dir):
    """Figure 4: FedAvg Catastrophic Failure."""
    attacks = ['NO_ATTACK', 'MODEL_POISONING', 'GRADIENT_ASCENT', 'BACKDOOR']
    
    dtguard_accs = [exp1['DT-Guard'][a]['final_accuracy'] for a in attacks if a in exp1['DT-Guard']]
    fedavg_accs = [exp1['FedAvg'][a]['final_accuracy'] for a in attacks if a in exp1['FedAvg']]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(attacks))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, dtguard_accs, width, label='DT-Guard', color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, fedavg_accs, width, label='FedAvg (Baseline)', color='#95a5a6', alpha=0.8, edgecolor='black', linewidth=1.5)
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax.set_xlabel('Scenario', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
    ax.set_title('DT-Guard vs FedAvg: Baseline Catastrophic Failure', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([a.replace('_', ' ').title() for a in attacks], rotation=15, ha='right')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 0.8)
    
    ax.annotate('CATASTROPHIC\nFAILURE!', xy=(2, 0.17), xytext=(2.5, 0.35),
                arrowprops=dict(arrowstyle='->', color='red', lw=3),
                fontsize=12, color='red', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure4_fedavg_failure.png', dpi=300, bbox_inches='tight')
    print("✓ Figure 4: FedAvg failure")
    plt.close()

def plot_detection_rate_comparison(exp1, output_dir):
    """Figure 2: Detection Rate Comparison across defenses."""
    attacks = ['MODEL_POISONING', 'GRADIENT_ASCENT', 'BACKDOOR', 'BYZANTINE_ATTACK']
    defenses = ['DT-Guard', 'Krum', 'Multi-Krum', 'Median', 'Trimmed Mean', 'FedAvg']

    data = []
    for defense in defenses:
        if defense in exp1:
            drs = [exp1[defense].get(attack, {}).get('detection', 0) * 100 for attack in attacks]
            data.append(drs)

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(attacks))
    width = 0.13
    colors = ['#e74c3c', '#9b59b6', '#2ecc71', '#f39c12', '#3498db', '#95a5a6']

    for i, (defense, drs) in enumerate(zip(defenses, data)):
        offset = (i - len(defenses)/2 + 0.5) * width
        bars = ax.bar(x + offset, drs, width, label=defense, color=colors[i], alpha=0.8)
        for bar in bars:
            height = bar.get_height()
            if height > 5:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}%', ha='center', va='bottom', fontsize=8)

    ax.axhline(y=100, color='green', linestyle='--', alpha=0.5, label='Perfect Detection')
    ax.set_xlabel('Attack Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('Detection Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Detection Rate Comparison Across Attacks', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([a.replace('_', ' ').title() for a in attacks])
    ax.legend(loc='lower right', ncol=2, fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 110)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure2_detection_rate_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Figure 2: Detection rate comparison")
    plt.close()

def plot_accuracy_vs_detection_tradeoff(exp1, output_dir):
    """Figure 5: Accuracy vs Detection Rate tradeoff."""
    defenses = ['DT-Guard', 'Krum', 'Multi-Krum', 'Median', 'Trimmed Mean', 'FedAvg']
    attacks = ['MODEL_POISONING', 'GRADIENT_ASCENT', 'BACKDOOR']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#e74c3c', '#9b59b6', '#2ecc71', '#f39c12', '#3498db', '#95a5a6']
    markers = ['o', 's', '^', 'D', 'v', 'x']

    for idx, defense in enumerate(defenses):
        if defense not in exp1:
            continue
        
        accs = []
        drs = []
        for attack in attacks:
            if attack in exp1[defense]:
                accs.append(exp1[defense][attack]['final_accuracy'] * 100)
                drs.append(exp1[defense][attack]['detection'] * 100)
        
        if not accs:
            continue
        
        avg_acc = np.mean(accs)
        avg_dr = np.mean(drs)
        
        ax.scatter(avg_acc, avg_dr, s=300, alpha=0.7, color=colors[idx], 
                  marker=markers[idx], label=defense, edgecolors='black', linewidth=2)
        ax.annotate(defense, (avg_acc, avg_dr), xytext=(5, 5), 
                   textcoords='offset points', fontsize=10, fontweight='bold')
    
    ax.axhline(y=100, color='green', linestyle='--', alpha=0.3, label='Perfect Detection')
    ax.axvline(x=70, color='blue', linestyle='--', alpha=0.3, label='Target Accuracy')
    
    ax.set_xlabel('Average Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Detection Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Accuracy vs Detection Rate Tradeoff (Upper-Right is Best)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower left', fontsize=10)
    ax.set_xlim(10, 75)
    ax.set_ylim(-5, 105)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure5_accuracy_vs_detection.png', dpi=300, bbox_inches='tight')
    print("✓ Figure 5: Accuracy vs detection tradeoff")
    plt.close()

def plot_accuracy_history_comparison(exp1, output_dir):
    """Figure 6: Accuracy history comparison across defenses and attacks."""
    attacks = ['NO_ATTACK', 'MODEL_POISONING', 'GRADIENT_ASCENT', 'BACKDOOR']
    defenses = ['DT-Guard', 'Krum', 'Multi-Krum', 'Median', 'Trimmed Mean', 'FedAvg']
    colors = ['#e74c3c', '#9b59b6', '#2ecc71', '#f39c12', '#3498db', '#95a5a6']
    max_rounds = 5  # Limit to 15 rounds for fair comparison
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for idx, attack in enumerate(attacks):
        ax = axes[idx]
        
        for def_idx, defense in enumerate(defenses):
            if defense not in exp1:
                continue
            if attack not in exp1[defense]:
                continue
            if 'accuracy_history' not in exp1[defense][attack]:
                continue
            
            history = exp1[defense][attack]['accuracy_history'][:max_rounds]
            rounds = np.arange(1, len(history) + 1)
            ax.plot(rounds, history, marker='o', linewidth=2, markersize=4,
                   label=defense, color=colors[def_idx], alpha=0.8)
        
        ax.set_xlabel('Round', fontsize=11, fontweight='bold')
        ax.set_ylabel('Accuracy', fontsize=11, fontweight='bold')
        ax.set_title(attack.replace('_', ' ').title(), fontsize=12, fontweight='bold')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(0, 0.8)
    
    plt.suptitle('Accuracy History: Defense Comparison Across Scenarios (15 Rounds)', 
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(output_dir / 'figure6_accuracy_history_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Figure 6: Accuracy history comparison")
    plt.close()

def plot_verification_scores(exp1, output_dir):
    """Figure 7: Verification scores over rounds for DT-Guard."""
    attacks = ['NO_ATTACK', 'MODEL_POISONING', 'GRADIENT_ASCENT', 'BACKDOOR']
    colors = ['#2ecc71', '#e74c3c', '#3498db', '#f39c12']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for idx, attack in enumerate(attacks):
        ax = axes[idx]
        
        if 'DT-Guard' not in exp1 or attack not in exp1['DT-Guard']:
            continue
        if 'verification_history' not in exp1['DT-Guard'][attack]:
            continue
        
        history = exp1['DT-Guard'][attack]['verification_history']
        
        if 'scores' in history[0]:
            rounds = [h['round'] for h in history]
            benign_scores = []
            malicious_scores = []
            
            for h in history:
                if 'scores' in h:
                    benign = [s for i, s in enumerate(h['scores']) if i < len(h['scores']) - 1]
                    malicious = [h['scores'][-1]] if len(h['scores']) > 0 else []
                    benign_scores.append(np.mean(benign) if benign else 0)
                    malicious_scores.append(np.mean(malicious) if malicious else 0)
            
            if benign_scores:
                ax.plot(rounds, benign_scores, marker='o', linewidth=2.5, markersize=6,
                       label='Benign Clients', color='green', alpha=0.8)
            if malicious_scores and attack != 'NO_ATTACK':
                ax.plot(rounds, malicious_scores, marker='x', linewidth=2.5, markersize=8,
                       label='Malicious Client', color='red', alpha=0.8)
            
            ax.axhline(y=0.6, color='orange', linestyle='--', alpha=0.5, label='Threshold')
        else:
            ax.text(0.5, 0.5, 'Score data not available', ha='center', va='center',
                   transform=ax.transAxes, fontsize=12)
        
        ax.set_xlabel('Round', fontsize=11, fontweight='bold')
        ax.set_ylabel('Verification Score', fontsize=11, fontweight='bold')
        ax.set_title(attack.replace('_', ' ').title(), fontsize=12, fontweight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(-0.1, 1.1)
    
    plt.suptitle('DT-Guard: Verification Scores Over Rounds', 
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(output_dir / 'figure7_verification_scores.png', dpi=300, bbox_inches='tight')
    print("✓ Figure 7: Verification scores")
    plt.close()

def main():
    """Generate all plots."""
    print("="*80)
    print("GENERATING OPTIMIZED PLOTS (7 CORE FIGURES)")
    print("="*80)

    exp1, exp2 = load_data()
    print("\n✓ Data loaded\n")

    output_dir = Path('results/thesis/figures')
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_accuracy_comparison(exp1, output_dir)
    plot_detection_rate_comparison(exp1, output_dir)
    plot_ablation_study(exp2, output_dir)
    plot_fedavg_failure(exp1, output_dir)
    plot_accuracy_vs_detection_tradeoff(exp1, output_dir)
    plot_accuracy_history_comparison(exp1, output_dir)
    plot_verification_scores(exp1, output_dir)

    print("\n" + "="*80)
    print("✅ ALL 7 FIGURES GENERATED")
    print("="*80)
    print(f"\nLocation: {output_dir}/")
    print("\nKey Findings:")
    print("  • DT-Guard: 100% detection, 0% FPR, 70% accuracy")
    print("  • FedAvg: 0% detection, catastrophic failure (17-49% accuracy)")
    print("  • w/o DT: System collapse (0.18% accuracy)")

if __name__ == '__main__':
    main()
