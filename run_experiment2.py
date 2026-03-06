#!/usr/bin/env python3
"""
EXPERIMENT 2: ABLATION STUDY
Component Contributions Analysis
"""

import torch
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime

from dtguard.config import Config, AttackType
from dtguard.data import load_data, create_federated_dataset
from dtguard.models import IoTAttackNet, GANGenerator, PersonalizedIoTModel
from dtguard.security import DigitalTwinVerifier, ReputationSystem
from dtguard.fl.async_aggregation import run_async_federated_learning
from dtguard.fl import run_federated_learning


def main():
    print("="*80)
    print("EXPERIMENT 2: ABLATION STUDY")
    print("="*80)
    print(f"\nStart: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")
    
    print("\nLoading data...")
    config = Config(dataset_dir="data/CICIoT2023")
    train_df, test_df, feature_cols = load_data(config)
    print(f"Features: {len(feature_cols)}, Train: {len(train_df)}, Test: {len(test_df)}")
    
    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df['Label'].values.astype(np.int64)
    input_dim = len(feature_cols)
    num_classes = len(np.unique(y_test))
    
    variants = [
        ('Full', True, True, True, False),
        ('w/o_DT', False, True, True, False),
        ('w/o_Shapley', True, False, True, False),
        ('w/o_Reputation', True, True, False, False),
        ('w/o_PFL', True, True, True, False),
        ('Baseline', False, False, False, False),
    ]
    
    results = {}
    
    for name, use_dt, use_shapley, use_reputation, use_pfl in variants:
        print(f"\n{'='*60}")
        print(f"Variant: {name}")
        print(f"{'='*60}")
        
        config = Config(
            num_clients=5,
            num_malicious=1,
            num_rounds=5,
            local_epochs=3,
            gan_epochs=100 if use_dt else 10,
            dirichlet_alpha=0.5,
            attack_type=AttackType.GRADIENT_ASCENT,
            attack_scale=10.0,
            dt_threshold=0.5 if use_dt else 0.0,
            use_committee=use_dt,
            committee_size=3 if use_dt else 0
        )
        
        X_clients, y_clients = create_federated_dataset(train_df, feature_cols, config)
        
        if use_pfl:
            client_models = [PersonalizedIoTModel(input_dim, num_classes) for _ in range(config.num_clients)]
            global_model = PersonalizedIoTModel(input_dim, num_classes)
        else:
            client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(config.num_clients)]
            global_model = IoTAttackNet(input_dim, num_classes)
        
        if use_dt:
            gan = GANGenerator(latent_dim=100, output_dim=input_dim)
            benign_X = [X_clients[i] for i in range(config.num_clients - config.num_malicious)]
            benign_y = [y_clients[i] for i in range(config.num_clients - config.num_malicious)]
            gan.train_gan(benign_X, benign_y, epochs=config.gan_epochs, device=device)
            verifier = DigitalTwinVerifier(gan, threshold=config.dt_threshold, challenge_samples=config.challenge_samples)
        else:
            verifier = None

        reputation = ReputationSystem(config.num_clients) if use_reputation else None
        
        metrics = run_async_federated_learning(
            global_model, client_models, X_clients, y_clients,
            X_test, y_test, verifier, config, device=device,
            use_shapley=use_shapley, reputation_system=reputation,
            alpha=config.async_alpha, buffer_size=config.async_buffer_size
        ) if config.use_async else run_federated_learning(
            global_model, client_models, X_clients, y_clients,
            X_test, y_test, verifier, config, device=device,
            use_shapley=use_shapley, reputation_system=reputation
        )

        results[name] = {
            'final_accuracy': metrics['accuracy'][-1],
            'detection': metrics['verification_stats'][-1]['detection_rate'],
            'accuracy_history': metrics['accuracy']
        }
        
        print(f"  Accuracy: {results[name]['final_accuracy']:.4f}")
        print(f"  Detection: {results[name]['detection']:.2%}")
    
    results_dir = Path('results/paper_experiments')
    results_dir.mkdir(parents=True, exist_ok=True)
    
    with open(results_dir / 'exp2_ablation_study.pkl', 'wb') as f:
        pickle.dump(results, f)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    full_acc = results['Full']['final_accuracy']
    print(f"\n{'Variant':<20} {'Accuracy':<12} {'Detection':<12} {'Contribution'}")
    print("-" * 60)
    for variant, result in results.items():
        contrib = "Baseline" if variant == 'Full' else f"{(full_acc - result['final_accuracy'])*100:+.1f}%"
        print(f"{variant:<20} {result['final_accuracy']:<12.4f} {result['detection']:<12.2%} {contrib}")
    
    print(f"\n✅ Experiment 2 completed!")
    print(f"Results saved: {results_dir / 'exp2_ablation_study.pkl'}")
    print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
