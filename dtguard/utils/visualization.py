"""Visualization utilities for DT-Guard POC."""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.set_style('whitegrid')


def plot_poc_results(metrics, save_path=None):
    """
    Plot POC results: Accuracy, Detection Rate, and Shapley Values.
    
    Args:
        metrics: Dictionary with 'round', 'accuracy', 'malicious_detected', 'shapley_history'
        save_path: Optional path to save figure
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    rounds = metrics['round']
    
    # Plot 1: Global Accuracy
    axes[0].plot(rounds, metrics['accuracy'], marker='o', linewidth=2, color='#2E86AB')
    axes[0].set_xlabel('Round', fontsize=11)
    axes[0].set_ylabel('Accuracy', fontsize=11)
    axes[0].set_title('Global Model Accuracy', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim([0, 1])
    
    # Plot 2: Malicious Detection
    axes[1].bar(rounds, metrics['malicious_detected'], color='#A23B72', alpha=0.7)
    axes[1].set_xlabel('Round', fontsize=11)
    axes[1].set_ylabel('Malicious Clients Detected', fontsize=11)
    axes[1].set_title('DT-Guard Detection Performance', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Shapley Values Evolution
    if 'shapley_history' in metrics and len(metrics['shapley_history']) > 0:
        shapley_array = np.array(metrics['shapley_history'])
        n_clients = shapley_array.shape[1]
        
        colors = ['#06A77D', '#F18F01', '#C73E1D']
        for i in range(n_clients):
            label = f'Client {i}' + (' (Malicious)' if i == n_clients - 1 else ' (Benign)')
            axes[2].plot(rounds, shapley_array[:, i], marker='o', linewidth=2, 
                        label=label, color=colors[i % len(colors)])
        
        axes[2].set_xlabel('Round', fontsize=11)
        axes[2].set_ylabel('Shapley Value', fontsize=11)
        axes[2].set_title('Client Contribution (Shapley)', fontsize=12, fontweight='bold')
        axes[2].legend(fontsize=9)
        axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Figure saved to {save_path}")
    
    plt.show()


def print_summary_table(metrics, config):
    """Print summary table of POC results."""
    print("\n" + "=" * 70)
    print("DT-GUARD POC - SUMMARY RESULTS")
    print("=" * 70)
    
    print(f"\n{'Configuration:':<30}")
    print(f"  {'Clients:':<28} {config.num_clients} ({config.num_malicious} malicious)")
    print(f"  {'Rounds:':<28} {config.num_rounds}")
    print(f"  {'Attack Type:':<28} {config.attack_type.value}")
    print(f"  {'Attack Scale:':<28} {config.attack_scale}")
    print(f"  {'DT Threshold:':<28} {config.dt_threshold}")
    
    print(f"\n{'Performance Metrics:':<30}")
    print(f"  {'Initial Accuracy:':<28} {metrics['accuracy'][0]:.4f}")
    print(f"  {'Final Accuracy:':<28} {metrics['accuracy'][-1]:.4f}")
    print(f"  {'Accuracy Improvement:':<28} {(metrics['accuracy'][-1] - metrics['accuracy'][0]):.4f}")
    
    total_detections = sum(metrics['malicious_detected'])
    detection_rate = (total_detections / config.num_rounds) * 100
    print(f"\n{'Detection Performance:':<30}")
    print(f"  {'Total Detections:':<28} {total_detections}/{config.num_rounds} rounds")
    print(f"  {'Detection Rate:':<28} {detection_rate:.1f}%")
    
    if 'shapley_history' in metrics and len(metrics['shapley_history']) > 0:
        final_shapley = metrics['shapley_history'][-1]
        print(f"\n{'Final Shapley Values:':<30}")
        for i, sv in enumerate(final_shapley):
            client_type = "(Malicious)" if i == config.num_clients - 1 else "(Benign)"
            print(f"  {'Client ' + str(i) + ' ' + client_type:<28} {sv:.4f}")
    
    print("\n" + "=" * 70)


def plot_verification_scores(verification_history, save_path=None):
    """
    Plot DT verification scores over rounds.
    
    Args:
        verification_history: List of dicts with 'round', 'client_id', 'score', 'passed'
        save_path: Optional path to save figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Group by client
    clients = {}
    for record in verification_history:
        cid = record['client_id']
        if cid not in clients:
            clients[cid] = {'rounds': [], 'scores': [], 'passed': []}
        clients[cid]['rounds'].append(record['round'])
        clients[cid]['scores'].append(record['score'])
        clients[cid]['passed'].append(record['passed'])
    
    # Plot each client
    colors = ['#06A77D', '#F18F01', '#C73E1D']
    for cid, data in clients.items():
        label = f'Client {cid}'
        color = colors[cid % len(colors)]
        
        # Plot line
        ax.plot(data['rounds'], data['scores'], marker='o', linewidth=2, 
               label=label, color=color)
        
        # Mark failed verifications
        failed_rounds = [r for r, p in zip(data['rounds'], data['passed']) if not p]
        failed_scores = [s for s, p in zip(data['scores'], data['passed']) if not p]
        if failed_rounds:
            ax.scatter(failed_rounds, failed_scores, color='red', s=100, 
                      marker='x', linewidths=3, zorder=5)
    
    # Threshold line
    ax.axhline(y=0.5, color='gray', linestyle='--', linewidth=1.5, 
              label='Threshold', alpha=0.7)
    
    ax.set_xlabel('Round', fontsize=12)
    ax.set_ylabel('Verification Score', fontsize=12)
    ax.set_title('DT Verification Scores Over Time', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Figure saved to {save_path}")
    
    plt.show()


def plot_loss_accuracy_comparison(metrics_dict, save_path=None):
    """
    Vẽ biểu đồ so sánh loss và accuracy giữa các phương pháp.
    
    Args:
        metrics_dict: Dict {method_name: {'rounds': [], 'loss': [], 'accuracy': []}}
        save_path: Đường dẫn lưu file
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#06A77D', '#C73E1D']
    
    # Plot Loss
    for idx, (method, data) in enumerate(metrics_dict.items()):
        color = colors[idx % len(colors)]
        ax1.plot(data['rounds'], data['loss'], marker='o', linewidth=2.5, 
                label=method, color=color, markersize=6)
    
    ax1.set_xlabel('Round', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Loss', fontsize=13, fontweight='bold')
    ax1.set_title('Training Loss Comparison', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11, loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Plot Accuracy
    for idx, (method, data) in enumerate(metrics_dict.items()):
        color = colors[idx % len(colors)]
        ax2.plot(data['rounds'], data['accuracy'], marker='s', linewidth=2.5,
                label=method, color=color, markersize=6)
    
    ax2.set_xlabel('Round', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Accuracy', fontsize=13, fontweight='bold')
    ax2.set_title('Test Accuracy Comparison', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11, loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 1])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Biểu đồ đã lưu tại {save_path}")
    
    plt.show()


def plot_training_curves(history, save_path=None):
    """
    Vẽ biểu đồ loss và accuracy cho một phương pháp.
    
    Args:
        history: Dict {'rounds': [], 'train_loss': [], 'train_acc': [], 'test_acc': []}
        save_path: Đường dẫn lưu file
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    rounds = history['rounds']
    
    # Plot Loss
    ax1.plot(rounds, history['train_loss'], marker='o', linewidth=2.5,
            label='Training Loss', color='#2E86AB', markersize=7)
    ax1.set_xlabel('Round', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Loss', fontsize=13, fontweight='bold')
    ax1.set_title('Training Loss', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # Plot Accuracy
    if 'train_acc' in history:
        ax2.plot(rounds, history['train_acc'], marker='o', linewidth=2.5,
                label='Training Accuracy', color='#06A77D', markersize=7)
    ax2.plot(rounds, history['test_acc'], marker='s', linewidth=2.5,
            label='Test Accuracy', color='#A23B72', markersize=7)
    ax2.set_xlabel('Round', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Accuracy', fontsize=13, fontweight='bold')
    ax2.set_title('Accuracy', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 1])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Biểu đồ đã lưu tại {save_path}")
    
    plt.show()


def plot_multi_metric_comparison(metrics_dict, save_path=None):
    """
    Vẽ biểu đồ so sánh nhiều metrics: Loss, Accuracy, Detection Rate.
    
    Args:
        metrics_dict: Dict {method: {'rounds': [], 'loss': [], 'accuracy': [], 'detection_rate': []}}
        save_path: Đường dẫn lưu file
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#06A77D', '#C73E1D']
    
    # Loss
    for idx, (method, data) in enumerate(metrics_dict.items()):
        axes[0, 0].plot(data['rounds'], data['loss'], marker='o', linewidth=2,
                       label=method, color=colors[idx % len(colors)])
    axes[0, 0].set_xlabel('Round', fontsize=11)
    axes[0, 0].set_ylabel('Loss', fontsize=11)
    axes[0, 0].set_title('Training Loss', fontsize=12, fontweight='bold')
    axes[0, 0].legend(fontsize=9)
    axes[0, 0].grid(True, alpha=0.3)
    
    # Accuracy
    for idx, (method, data) in enumerate(metrics_dict.items()):
        axes[0, 1].plot(data['rounds'], data['accuracy'], marker='s', linewidth=2,
                       label=method, color=colors[idx % len(colors)])
    axes[0, 1].set_xlabel('Round', fontsize=11)
    axes[0, 1].set_ylabel('Accuracy', fontsize=11)
    axes[0, 1].set_title('Test Accuracy', fontsize=12, fontweight='bold')
    axes[0, 1].legend(fontsize=9)
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].set_ylim([0, 1])
    
    # Detection Rate (nếu có)
    has_detection = any('detection_rate' in data for data in metrics_dict.values())
    if has_detection:
        for idx, (method, data) in enumerate(metrics_dict.items()):
            if 'detection_rate' in data:
                axes[1, 0].plot(data['rounds'], data['detection_rate'], marker='^', linewidth=2,
                               label=method, color=colors[idx % len(colors)])
        axes[1, 0].set_xlabel('Round', fontsize=11)
        axes[1, 0].set_ylabel('Detection Rate', fontsize=11)
        axes[1, 0].set_title('Malicious Detection Rate', fontsize=12, fontweight='bold')
        axes[1, 0].legend(fontsize=9)
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_ylim([0, 1])
    
    # Final comparison bar chart
    methods = list(metrics_dict.keys())
    final_acc = [data['accuracy'][-1] for data in metrics_dict.values()]
    
    bars = axes[1, 1].bar(methods, final_acc, color=colors[:len(methods)], alpha=0.7)
    axes[1, 1].set_ylabel('Final Accuracy', fontsize=11)
    axes[1, 1].set_title('Final Accuracy Comparison', fontsize=12, fontweight='bold')
    axes[1, 1].set_ylim([0, 1])
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        axes[1, 1].text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Biểu đồ đã lưu tại {save_path}")
    
    plt.show()
