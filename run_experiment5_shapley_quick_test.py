#!/usr/bin/env python3
"""
QUICK TEST: DT-PW Free-Rider Suppression
==========================================
Minimal test to verify DT-PW correctly suppresses free-riders.
No TabDDPM, no verification, just pure DT-PW scoring.
"""
import torch
import numpy as np
from dtguard.config import Config
from dtguard.data import load_data, create_federated_dataset
from dtguard.models import IoTAttackNet
from dtguard.models.ids_model import get_parameters, set_parameters, train_model, evaluate_model
from dtguard.security.shapley import dt_performance_weighting

# ---- Minimal settings ----
NUM_CLIENTS = 20
NUM_ROUNDS = 5  # Quick test with more stability
LOCAL_EPOCHS = 2
SEED = 42

# Client roles
NUM_FREE_RIDERS = 3
NUM_NOISY_LABEL = 3
NUM_HIGH_QUALITY = 2
NUM_MALICIOUS = 4
NUM_NORMAL = 8

NORMAL_IDX = list(range(0, NUM_NORMAL))
MALICIOUS_IDX = list(range(NUM_NORMAL, NUM_NORMAL + NUM_MALICIOUS))
HIGH_QUALITY_IDX = list(range(NUM_NORMAL + NUM_MALICIOUS,
                              NUM_NORMAL + NUM_MALICIOUS + NUM_HIGH_QUALITY))
NOISY_LABEL_IDX = list(range(NUM_NORMAL + NUM_MALICIOUS + NUM_HIGH_QUALITY,
                               NUM_NORMAL + NUM_MALICIOUS + NUM_HIGH_QUALITY + NUM_NOISY_LABEL))
FREE_RIDER_IDX = list(range(NUM_CLIENTS - NUM_FREE_RIDERS, NUM_CLIENTS))

CLIENT_ROLES = {}
for i in NORMAL_IDX: CLIENT_ROLES[i] = "Normal"
for i in MALICIOUS_IDX: CLIENT_ROLES[i] = "Malicious"
for i in HIGH_QUALITY_IDX: CLIENT_ROLES[i] = "HighQuality"
for i in NOISY_LABEL_IDX: CLIENT_ROLES[i] = "NoisyLabel"
for i in FREE_RIDER_IDX: CLIENT_ROLES[i] = "FreeRider"


def prepare_client_data(X_clients, y_clients, num_classes):
    """Modify client data to simulate different roles."""
    rng = np.random.default_rng(SEED)
    
    # High-quality: rare classes only, small data
    for i in HIGH_QUALITY_IDX:
        rare_mask = y_clients[i] > 5
        if rare_mask.sum() > 100:
            X_clients[i] = X_clients[i][rare_mask][:500]
            y_clients[i] = y_clients[i][rare_mask][:500]
        else:
            X_clients[i] = X_clients[i][:500]
            y_clients[i] = y_clients[i][:500]
    
    # Noisy-label: 50% corrupted
    for i in NOISY_LABEL_IDX:
        n = len(y_clients[i])
        n_corrupt = int(n * 0.5)
        corrupt_idx = rng.choice(n, n_corrupt, replace=False)
        y_clients[i][corrupt_idx] = rng.integers(0, num_classes, n_corrupt)
    
    return X_clients, y_clients


def _local_train_or_freerider(model, global_weights, client_idx, X, y, device):
    """Train or free-ride."""
    if client_idx in FREE_RIDER_IDX:
        # Free-rider: copy global + tiny noise (NO training)
        noisy_w = []
        for w in global_weights:
            noise = np.random.normal(0, 0.0001, w.shape).astype(w.dtype)
            noisy_w.append(w + noise)
        return noisy_w
    else:
        set_parameters(model, global_weights)
        train_model(model, X, y, epochs=LOCAL_EPOCHS, batch_size=512, lr=0.001, device=device)
        return get_parameters(model)


def main():
    print("=" * 80)
    print("  QUICK TEST: DT-PW Free-Rider Suppression")
    print("=" * 80)
    
    device = torch.device('cpu')  # Force CPU for speed
    
    # Load data
    cfg = Config(dataset_dir="data/CICIoT2023")
    train_df, test_df, feature_cols = load_data(cfg)
    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df['Label'].values.astype(np.int64)
    input_dim = len(feature_cols)
    num_classes = len(np.unique(y_test))
    
    # Create federated data
    np.random.seed(SEED)
    split_cfg = Config(num_clients=NUM_CLIENTS, dirichlet_alpha=0.5)
    X_clients, y_clients = create_federated_dataset(
        train_df, feature_cols, split_cfg, verbose=False,
        max_samples_per_client=10_000)
    
    X_clients, y_clients = prepare_client_data(X_clients, y_clients, num_classes)
    
    print(f"\n  Setup: {NUM_CLIENTS} clients, {NUM_ROUNDS} rounds (quick test)")
    print(f"  Roles: {NUM_NORMAL} normal, {NUM_NOISY_LABEL} noisy, {NUM_FREE_RIDERS} free-riders\n")
    
    # Initialize models
    global_model = IoTAttackNet(input_dim, num_classes)
    client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(NUM_CLIENTS)]
    
    # Run FL rounds
    all_weights = []
    for rnd in range(NUM_ROUNDS):
        print(f"  Round {rnd+1}/{NUM_ROUNDS}...", end=" ", flush=True)
        
        gw = get_parameters(global_model)
        cw = [_local_train_or_freerider(client_models[i], gw, i,
              X_clients[i], y_clients[i], device) for i in range(NUM_CLIENTS)]
        
        # Run DT-PW (no verification, just scoring)
        for i in range(NUM_CLIENTS):
            set_parameters(client_models[i], cw[i])
        
        pw = dt_performance_weighting(
            client_models, cw, X_test, y_test, device,
            eval_subsample=2000, global_weights=gw, challenge_gen=None,
            client_data_sizes=[len(X_clients[i]) for i in range(NUM_CLIENTS)],
            debug=(rnd == NUM_ROUNDS - 1))  # Debug on last round
        
        all_weights.append(pw)
        
        # Simple FedAvg aggregation
        from dtguard.fl.baselines import federated_averaging
        aggregated, _ = federated_averaging(cw)
        set_parameters(global_model, aggregated)
        
        acc = evaluate_model(global_model, X_test, y_test, device=device)
        print(f"acc={acc*100:.1f}%")
    
    # Analyze final weights
    print("\n" + "=" * 80)
    print("  RESULTS: DT-PW Weights (averaged over last 2 rounds)")
    print("=" * 80)
    
    final_weights = np.mean(all_weights[-3:], axis=0)  # Average last 3 rounds for stability
    
    print(f"\n  {'ID':<5} {'Role':<12} {'Samples':<8} {'DT-PW Weight':>12}  {'Status'}")
    print("  " + "-" * 60)
    
    for i in range(NUM_CLIENTS):
        role = CLIENT_ROLES[i]
        w = final_weights[i]
        
        if role == "FreeRider":
            status = "✅ SUPPRESSED" if w < 0.01 else "❌ NOT SUPPRESSED"
        elif role == "NoisyLabel":
            status = "✓ penalized" if w < 0.045 else "—"
        elif role == "HighQuality":
            status = "★ boosted" if w > 0.03 else "⚠ too low"
        else:
            status = ""
        
        print(f"  {i:<5} {role:<12} {len(X_clients[i]):<8} {w:>11.4f}  {status}")
    
    # Summary
    print("\n  Summary by role:")
    print("  " + "-" * 40)
    
    avg_normal = np.mean([final_weights[i] for i in NORMAL_IDX])
    avg_highquality = np.mean([final_weights[i] for i in HIGH_QUALITY_IDX])
    avg_noisy = np.mean([final_weights[i] for i in NOISY_LABEL_IDX])
    avg_freerider = np.mean([final_weights[i] for i in FREE_RIDER_IDX])
    
    print(f"  Normal:       {avg_normal:.4f}")
    print(f"  HighQuality:  {avg_highquality:.4f}")
    print(f"  Noisy:        {avg_noisy:.4f}")
    print(f"  Free-rider:   {avg_freerider:.4f}")
    
    ratio = avg_freerider / avg_normal if avg_normal > 0 else float('inf')
    print(f"\n  Ratio FR/Normal: {ratio:.4f}")
    
    if ratio < 0.2:
        print(f"  ✅✅✅ SUCCESS: Free-riders suppressed to {ratio:.1%} of normal weight!")
    elif ratio < 0.5:
        print(f"  ⚠ PARTIAL: Free-riders at {ratio:.1%} (target < 20%)")
    else:
        print(f"  ❌ FAILED: Free-riders NOT suppressed (ratio={ratio:.1%})")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
