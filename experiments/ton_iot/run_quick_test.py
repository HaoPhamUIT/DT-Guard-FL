#!/usr/bin/env python3
"""
Quick test for ToN-IoT dataset loader and basic experiment.
"""

import torch
import numpy as np
from pathlib import Path

from dtguard.data import load_ton_iot_data, create_federated_dataset
from dtguard.config import Config
from dtguard.models import IoTAttackNet, TabDDPMChallengeGenerator
from dtguard.models.ids_model import get_parameters, set_parameters, train_model, evaluate_model
from dtguard.security import DigitalTwinVerifier, CommitteeSelector
from dtguard.security import dt_performance_weighting, combine_dtpw_verification
from dtguard.fl.aggregation import weighted_federated_averaging
from dtguard.fl.baselines import federated_averaging


def main():
    print("="*80)
    print("QUICK TEST - ToN-IoT Dataset")
    print("="*80)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")

    # Load ToN-IoT data
    print("\n1. Loading ToN-IoT dataset...")
    train_df, test_df, feature_cols = load_ton_iot_data(
        data_dir="data/ToN-IoT_Data",
        random_seed=42
    )

    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df['Label'].values.astype(np.int64)
    input_dim = len(feature_cols)
    num_classes = len(np.unique(y_test))

    print(f"   Input dim: {input_dim}, Classes: {num_classes}")

    # Create federated dataset (small for quick test)
    print("\n2. Creating federated dataset...")
    config = Config(
        num_clients=5,
        dirichlet_alpha=0.5,
        random_seed=42
    )
    X_clients, y_clients = create_federated_dataset(
        train_df, feature_cols, config,
        verbose=True,
        max_samples_per_client=2000
    )

    # Initialize models
    print("\n3. Initializing models...")
    global_model = IoTAttackNet(input_dim, num_classes).to(device)
    client_models = [IoTAttackNet(input_dim, num_classes).to(device) for _ in range(5)]

    # Quick FL training (2 rounds)
    print("\n4. Running 2 rounds of FL...")
    for rnd in range(2):
        print(f"   Round {rnd + 1}/2")

        global_weights = get_parameters(global_model)
        client_weights = []

        for i in range(5):
            set_parameters(client_models[i], global_weights)
            train_model(client_models[i], X_clients[i], y_clients[i],
                       epochs=1, batch_size=128, lr=0.001, device=device)
            client_weights.append(get_parameters(client_models[i]))

        # FedAvg aggregation
        aggregated, _ = federated_averaging(client_weights)
        set_parameters(global_model, aggregated)

        # Evaluate
        acc = evaluate_model(global_model, X_test, y_test, device=device)
        print(f"   Accuracy: {acc*100:.2f}%")

    # Train TabDDPM generator
    print("\n5. Training TabDDPM generator...")
    X_benign = np.vstack([X_clients[i] for i in range(4)])  # First 4 clients
    y_benign = np.concatenate([y_clients[i] for i in range(4)])

    if len(X_benign) > 5000:
        idx = np.random.choice(len(X_benign), 5000, replace=False)
        X_benign, y_benign = X_benign[idx], y_benign[idx]

    tabddpm_gen = TabDDPMChallengeGenerator(
        input_dim=input_dim, n_classes=num_classes,
        T=100, d_hidden=128, n_epochs=50, batch_size=256
    )
    tabddpm_gen.train_gan(X_benign, y_benign, device=device)

    # Test generation
    print("\n6. Testing generation...")
    X_syn, y_syn = tabddpm_gen.generate_challenge_set(100, device=device)
    print(f"   Generated: X shape={X_syn.shape}, y shape={y_syn.shape}")
    print(f"   Unique labels in synthetic: {np.unique(y_syn)}")

    # Test Digital Twin verifier
    print("\n7. Testing Digital Twin verifier...")
    verifier = DigitalTwinVerifier(tabddpm_gen, threshold=0.6, challenge_samples=50)

    # Verify client 0 (should pass)
    set_parameters(client_models[0], get_parameters(client_models[0]))
    res = verifier.verify(client_models[0], device, global_model=global_model, client_id=0)
    print(f"   Client 0 verification: score={res['score']:.4f}, passed={res['passed']}")

    print("\n" + "="*80)
    print("QUICK TEST COMPLETED SUCCESSFULLY!")
    print("="*80)


if __name__ == "__main__":
    main()
