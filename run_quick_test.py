#!/usr/bin/env python3
"""
DT-GUARD: QUICK TEST - Reduced configuration for fast testing
"""

import torch
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime

from dtguard.config import Config, AttackType
from dtguard.data import load_data, create_federated_dataset
from dtguard.models import IoTAttackNet, GANGenerator, PersonalizedIoTModel
from dtguard.security import DigitalTwinVerifier, ReputationSystem, apply_attack
from dtguard.fl import run_federated_learning
from dtguard.fl.async_aggregation import run_async_federated_learning
from dtguard.fl.baselines import krum_aggregation, median_aggregation, trimmed_mean_aggregation, federated_averaging
from dtguard.fl.aggregation import compute_verification_stats
from dtguard.models.ids_model import get_parameters, set_parameters, train_model, evaluate_model


def run_baseline_defense(defense_name, train_df, test_df, feature_cols, config, device):
    """Run baseline defense (Krum/Median/Trimmed Mean/FedAvg)."""
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

        # Local training
        for i, model in enumerate(client_models):
            set_parameters(model, get_parameters(global_model))
            train_model(model, X_clients[i], y_clients[i], epochs=config.local_epochs, device=device)
            weights = get_parameters(model)
            
            # Apply attack to last client if malicious
            if config.num_malicious > 0 and i >= config.num_clients - config.num_malicious:
                attack_type_str = config.attack_type if isinstance(config.attack_type, str) else config.attack_type.value
                weights = apply_attack(weights, attack_type_str, config.attack_scale)
            
            client_weights.append(weights)
        
        # Aggregate based on defense
        if defense_name == 'Krum':
            aggregated, rejected = krum_aggregation(client_weights, f=1)
        elif defense_name == 'Median':
            aggregated, rejected = median_aggregation(client_weights)
        elif defense_name == 'Trimmed Mean':
            aggregated, rejected = trimmed_mean_aggregation(client_weights, trim_ratio=0.2)
        else:  # FedAvg
            aggregated, rejected = federated_averaging(client_weights)

        # Compute verification stats (same as run_experiments.py)
        verification_results = [i not in rejected for i in range(config.num_clients)]
        malicious_indices = list(range(config.num_clients - config.num_malicious, config.num_clients)) if config.num_malicious > 0 else []
        stats = compute_verification_stats(
            config.num_clients,
            malicious_indices,
            verification_results
        )
        total_detected += stats['tp']
        fp_total += stats['fp']
        tn_total += stats['tn']

        set_parameters(global_model, aggregated)
        accuracy = evaluate_model(global_model, X_test, y_test, device=device)
        accuracies.append(accuracy)
    
    detection_rate = total_detected / (config.num_rounds * max(1, config.num_malicious))
    false_positive_rate = fp_total / (fp_total + tn_total) if (fp_total + tn_total) > 0 else 0.0
    return {
        'accuracy': accuracies[-1],
        'detection': detection_rate,
        'false_positive_rate': false_positive_rate,
        'accuracy_history': accuracies  # Track round-by-round accuracy
    }


def experiment1_defense_comparison(train_df, test_df, feature_cols, device):
    """Experiment 1: DT-Guard vs Baselines (QUICK TEST)."""
    print("\n" + "="*80)
    print("EXPERIMENT 1: DEFENSE COMPARISON (QUICK TEST)")
    print("="*80)
    
    # Test NO_ATTACK + 1 attack for speed (matching run_experiments.py structure)
    attacks = [
        AttackType.GRADIENT_ASCENT
    ]
    defenses = ['DT-Guard', 'FedAvg']  # Only 2 defenses for speed

    results = {defense: {} for defense in defenses}
    
    for attack in attacks:
        print(f"\n{'='*60}")
        print(f"Attack: {attack.value if attack else 'NO_ATTACK'}")
        print(f"{'='*60}")
        
        config = Config(
            num_clients=3,
            num_malicious=0 if attack is None else 1,  # Match run_experiments.py
            num_rounds=3,
            local_epochs=2,
            gan_epochs=60,
            dirichlet_alpha=0.5,
            attack_type=attack if attack else AttackType.MODEL_POISONING,  # Dummy for NO_ATTACK
            attack_scale=10.0,
            use_async=True,
            use_committee=True,
            committee_size=2,
            dt_threshold=0.30  # Increased from 0.20 to reject high FPR clients
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
                verifier = DigitalTwinVerifier(gan, threshold=config.dt_threshold)
                
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
                    'accuracy': metrics['accuracy'][-1],
                    'detection': metrics['verification_stats'][-1]['detection_rate'],
                    'false_positive_rate': metrics['verification_stats'][-1]['false_positive_rate'],
                    # Track history for plots
                    'accuracy_history': metrics['accuracy'],
                    'verification_history': metrics['verification_stats'],
                    'shapley_history': metrics.get('shapley_history', [])
                }
            else:
                result = run_baseline_defense(defense, train_df, test_df, feature_cols, config, device)
            
            results[defense][attack.value if attack else 'NO_ATTACK'] = result
            print(f"  Accuracy: {result['accuracy']:.4f}")
            print(f"  Detection: {result['detection']:.2%}")
    
    return results


def experiment2_ablation_study(train_df, test_df, feature_cols, device):
    """Experiment 2: Ablation Study (QUICK TEST)."""
    print("\n" + "="*80)
    print("EXPERIMENT 2: ABLATION STUDY (QUICK TEST)")
    print("="*80)
    
    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df['Label'].values.astype(np.int64)
    input_dim = len(feature_cols)
    num_classes = len(np.unique(y_test))
    
    # Test only 3 variants
    variants = [
        ('Full', True, True),
        ('w/o_DT', False, True),
        ('Baseline', False, False),
    ]
    
    results = {}
    
    for name, use_dt, use_shapley in variants:
        print(f"\n{'='*60}")
        print(f"Variant: {name}")
        print(f"{'='*60}")
        
        config = Config(
            num_clients=3,
            num_malicious=1,
            num_rounds=3,
            local_epochs=2,
            gan_epochs=50 if use_dt else 10,  # Increased from 30
            dirichlet_alpha=0.5,
            attack_type=AttackType.GRADIENT_ASCENT,
            attack_scale=10.0,
            dt_threshold=0.30 if use_dt else 0.0  # Increased from 0.20
        )
        
        X_clients, y_clients = create_federated_dataset(train_df, feature_cols, config)
        
        client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(config.num_clients)]
        global_model = IoTAttackNet(input_dim, num_classes)
        
        if use_dt:
            gan = GANGenerator(latent_dim=100, output_dim=input_dim)
            benign_X = [X_clients[i] for i in range(config.num_clients - config.num_malicious)]
            benign_y = [y_clients[i] for i in range(config.num_clients - config.num_malicious)]
            gan.train_gan(benign_X, benign_y, epochs=config.gan_epochs, device=device)
            verifier = DigitalTwinVerifier(gan, threshold=config.dt_threshold)
        else:
            verifier = None  # Disable completely
        
        metrics = run_async_federated_learning(
            global_model, client_models, X_clients, y_clients,
            X_test, y_test, verifier, config, device=device,
            use_shapley=use_shapley, reputation_system=None,
            alpha=config.async_alpha, buffer_size=config.async_buffer_size
        ) if config.use_async else run_federated_learning(
            global_model, client_models, X_clients, y_clients,
            X_test, y_test, verifier, config, device=device, use_shapley=use_shapley
        )
        
        results[name] = {
            'accuracy': metrics['accuracy'][-1],
            'detection': metrics['verification_stats'][-1]['detection_rate'] if 'verification_stats' in metrics else 0.0,
            'accuracy_history': metrics['accuracy'],
            'verification_history': metrics.get('verification_stats', [])
        }
        
        print(f"  Accuracy: {results[name]['accuracy']:.4f}")
        print(f"  Detection: {results[name]['detection']:.2%}")
    
    return results


def main():
    """Run quick test experiments."""
    print("="*80)
    print("DT-GUARD: QUICK TEST EXPERIMENTS")
    print("Config: 3 clients, 3 rounds, 60 GAN epochs, threshold=0.30")
    print("="*80)
    print(f"\nStart: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")
    
    # Load data
    print("\nLoading data...")
    config = Config(dataset_dir="data/CICIoT2023")
    train_df, test_df, feature_cols = load_data(config)
    print(f"Features: {len(feature_cols)}, Train: {len(train_df)}, Test: {len(test_df)}")
    
    # Create results directory
    results_dir = Path('results/quick_test')
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Experiment 1
    print("\n" + "="*80)
    print("RUNNING EXPERIMENT 1...")
    print("="*80)
    exp1_results = experiment1_defense_comparison(train_df, test_df, feature_cols, device)
    
    with open(results_dir / 'exp1_defense_comparison.pkl', 'wb') as f:
        pickle.dump(exp1_results, f)
    print("\n✓ Experiment 1 completed")
    
    # Experiment 2
    print("\n" + "="*80)
    print("RUNNING EXPERIMENT 2...")
    print("="*80)
    exp2_results = experiment2_ablation_study(train_df, test_df, feature_cols, device)
    
    with open(results_dir / 'exp2_ablation_study.pkl', 'wb') as f:
        pickle.dump(exp2_results, f)
    print("\n✓ Experiment 2 completed")
    
    # Summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    print("\n📊 Experiment 1 - Defense Comparison:")
    print(f"{'Defense':<15} {'NO_ATTACK':<15} {'GRADIENT_ASCENT':<20} {'Detection':<15}")
    print("-" * 70)
    for defense, attacks in exp1_results.items():
        no_attack_acc = attacks.get('NO_ATTACK', {}).get('accuracy', 0)
        ga_result = attacks.get('GRADIENT_ASCENT', {})
        ga_acc = ga_result.get('accuracy', 0)
        ga_det = ga_result.get('detection', 0)
        print(f"{defense:<15} {no_attack_acc:<15.4f} {ga_acc:<20.4f} {ga_det:<15.2%}")

    print("\n🔬 Experiment 2 - Ablation Study:")
    full_acc = exp2_results['Full']['accuracy']
    print(f"{'Variant':<20} {'Accuracy':<12} {'Detection':<12} {'Contribution'}")
    print("-" * 60)
    for variant, result in exp2_results.items():
        contrib = "Baseline" if variant == 'Full' else f"{(full_acc - result['accuracy'])*100:+.1f}%"
        print(f"{variant:<20} {result['accuracy']:<12.4f} {result['detection']:<12.2%} {contrib}")
    
    # Calculate gains
    dt_guard_acc = exp1_results['DT-Guard']['GRADIENT_ASCENT']['accuracy']
    fedavg_acc = exp1_results['FedAvg']['GRADIENT_ASCENT']['accuracy']
    gain = (dt_guard_acc - fedavg_acc) * 100
    
    print(f"\n🎯 KEY FINDINGS:")
    print(f"  DT-Guard vs FedAvg: {gain:+.1f}% accuracy gain")
    print(f"  DT contribution: {(full_acc - exp2_results['w/o_DT']['accuracy'])*100:+.1f}%")
    print(f"  Shapley contribution: {(full_acc - exp2_results['Baseline']['accuracy'])*100:+.1f}%")
    
    print(f"\n✅ Quick test completed!")
    print(f"Results saved in: {results_dir}")
    print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
