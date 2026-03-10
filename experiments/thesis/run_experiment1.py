#!/usr/bin/env python3
"""
EXPERIMENT 1: DEFENSE COMPARISON
DT-Guard vs Krum/Multi-Krum/Median/Trimmed Mean/FedAvg
"""

import torch
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime

from dtguard.config import Config, AttackType
from dtguard.data import load_data, create_federated_dataset
from dtguard.models import IoTAttackNet, GANGenerator
from dtguard.security import DigitalTwinVerifier, apply_attack
from dtguard.fl.async_aggregation import run_async_federated_learning
from dtguard.fl import run_federated_learning
from dtguard.fl.baselines import krum_aggregation, median_aggregation, trimmed_mean_aggregation, federated_averaging, multi_krum_aggregation
from dtguard.fl.aggregation import compute_verification_stats
from dtguard.models.ids_model import get_parameters, set_parameters, train_model, evaluate_model


def run_baseline_defense(defense_name, train_df, test_df, feature_cols, config, device):
    """Run baseline defense."""
    X_clients, y_clients = create_federated_dataset(train_df, feature_cols, config)
    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df['Label'].values.astype(np.int64)
    
    input_dim = len(feature_cols)
    num_classes = len(np.unique(y_test))
    
    client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(config.num_clients)]
    global_model = IoTAttackNet(input_dim, num_classes)
    
    accuracies = []
    total_detected = 0
    fp_total = 0
    tn_total = 0

    for round_num in range(config.num_rounds):
        client_weights = []
        rejected = []

        for i, model in enumerate(client_models):
            set_parameters(model, get_parameters(global_model))
            train_model(model, X_clients[i], y_clients[i], epochs=config.local_epochs, device=device)
            weights = get_parameters(model)
            
            if config.num_malicious > 0 and i >= config.num_clients - config.num_malicious:
                attack_type_str = config.attack_type if isinstance(config.attack_type, str) else config.attack_type.value
                weights = apply_attack(weights, attack_type_str, config.attack_scale)
            
            client_weights.append(weights)
        
        if defense_name == 'Krum':
            aggregated, rejected = krum_aggregation(client_weights, f=1)
        elif defense_name == 'Multi-Krum':
            aggregated, rejected = multi_krum_aggregation(client_weights, f=1, m=2)
        elif defense_name == 'Median':
            aggregated, rejected = median_aggregation(client_weights)
        elif defense_name == 'Trimmed Mean':
            aggregated, rejected = trimmed_mean_aggregation(client_weights, trim_ratio=0.2)
        else:
            aggregated, rejected = federated_averaging(client_weights)

        verification_results = [i not in rejected for i in range(config.num_clients)]
        malicious_indices = list(range(config.num_clients - config.num_malicious, config.num_clients)) if config.num_malicious > 0 else []
        stats = compute_verification_stats(config.num_clients, malicious_indices, verification_results)
        total_detected += stats['tp']
        fp_total += stats['fp']
        tn_total += stats['tn']

        set_parameters(global_model, aggregated)
        accuracy = evaluate_model(global_model, X_test, y_test, device=device)
        accuracies.append(accuracy)
    
    detection_rate = total_detected / (config.num_rounds * max(1, config.num_malicious)) if config.num_malicious > 0 else 0.0
    false_positive_rate = fp_total / (fp_total + tn_total) if (fp_total + tn_total) > 0 else 0.0
    return {
        'final_accuracy': accuracies[-1],
        'detection': detection_rate,
        'false_positive_rate': false_positive_rate,
        'accuracy_history': accuracies
    }


def main():
    print("="*80)
    print("EXPERIMENT 1: DEFENSE COMPARISON")
    print("="*80)
    print(f"\nStart: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")
    
    print("\nLoading data...")
    config = Config(dataset_dir="data/CICIoT2023")
    train_df, test_df, feature_cols = load_data(config)
    print(f"Features: {len(feature_cols)}, Train: {len(train_df)}, Test: {len(test_df)}")
    
    attacks = [        AttackType.BACKDOOR,
        AttackType.MODEL_POISONING,
        AttackType.GRADIENT_ASCENT,
        None]
    defenses = ['DT-Guard', 'Krum', 'Median', 'Trimmed Mean', 'FedAvg']
    results = {defense: {} for defense in defenses}
    
    for attack in attacks:
        print(f"\n{'='*60}")
        print(f"Attack: {attack.value if attack else 'NO_ATTACK'}")
        print(f"{'='*60}")
        
        config = Config(
            num_clients=5,
            num_malicious=0 if attack is None else 1,
            num_rounds=10,
            local_epochs=3,
            gan_epochs=100,
            dirichlet_alpha=0.5,
            attack_type=attack,
            attack_scale=10.0,
            use_async=True,
            use_committee=True,
            committee_size=3,
            dt_threshold=0.65
        )
        
        for defense in defenses:
            print(f"\n--- {defense} ---")
            
            if defense == 'DT-Guard':
                X_clients, y_clients = create_federated_dataset(train_df, feature_cols, config)
                X_test = test_df[feature_cols].values.astype(np.float32)
                y_test = test_df['Label'].values.astype(np.int64)
                
                input_dim = len(feature_cols)
                num_classes = len(np.unique(y_test))
                
                gan = GANGenerator(latent_dim=100, output_dim=input_dim)
                benign_X = [X_clients[i] for i in range(config.num_clients - config.num_malicious)]
                benign_y = [y_clients[i] for i in range(config.num_clients - config.num_malicious)]
                gan.train_gan(benign_X, benign_y, epochs=config.gan_epochs, device=device)
                verifier = DigitalTwinVerifier(gan, threshold=config.dt_threshold, challenge_samples=config.challenge_samples)

                client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(config.num_clients)]
                global_model = IoTAttackNet(input_dim, num_classes)
                
                metrics = run_async_federated_learning(
                    global_model, client_models, X_clients, y_clients,
                    X_test, y_test, verifier, config, device=device,
                    use_shapley=True, reputation_system=None,
                    alpha=config.async_alpha, buffer_size=config.async_buffer_size
                ) if config.use_async else run_federated_learning(
                    global_model, client_models, X_clients, y_clients,
                    X_test, y_test, verifier, config, device=device, use_shapley=True
                )

                result = {
                    'final_accuracy': metrics['accuracy'][-1],
                    'detection': metrics['verification_stats'][-1]['detection_rate'],
                    'false_positive_rate': metrics['verification_stats'][-1]['false_positive_rate'],
                    'accuracy_history': metrics['accuracy'],
                    'verification_history': metrics['verification_stats']
                }
            else:
                result = run_baseline_defense(defense, train_df, test_df, feature_cols, config, device)
            
            results[defense][attack.value if attack else 'NO_ATTACK'] = result
            print(f"  Accuracy: {result['final_accuracy']:.4f}")
            print(f"  Detection: {result['detection']:.2%}")
    
    results_dir = Path('results/thesis')
    results_dir.mkdir(parents=True, exist_ok=True)
    
    with open(results_dir / 'exp1_defense_comparison.pkl', 'wb') as f:
        pickle.dump(results, f)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n{'Defense':<15} {'NO_ATTACK':<18} {'MODEL_POISONING':<18} {'GRADIENT_ASCENT':<18} {'BACKDOOR':<18}")
    print("-" * 90)
    for defense, attacks_dict in results.items():
        accs = [attacks_dict.get('NO_ATTACK', {}).get('final_accuracy', 0.0)] + \
               [attacks_dict[a.value]['final_accuracy'] for a in [AttackType.MODEL_POISONING, AttackType.GRADIENT_ASCENT, AttackType.BACKDOOR]]
        print(f"{defense:<15} {accs[0]:<18.4f} {accs[1]:<18.4f} {accs[2]:<18.4f} {accs[3]:<18.4f}")
    
    print(f"\n✅ Experiment 1 completed!")
    print(f"Results saved: {results_dir / 'exp1_defense_comparison.pkl'}")
    print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
