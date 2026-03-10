#!/usr/bin/env python3
"""
QUICK TEST FOR EXPERIMENT 3
============================
Runs a lightweight version to verify that ALL attacks × ALL defenses work
end-to-end before committing to the full experiment.

Key differences from the full experiment:
  - 10 clients / 5 malicious (50%, same ratio as LUP paper)
  - 5 rounds / 2 local epochs  (fast but enough to see attack impact)
  - Data loaded and split ONCE, reused for every (defense, attack) pair

Usage:
    python run_quick_experiment3.py
"""

import torch
import numpy as np
import time
import traceback
from datetime import datetime

from dtguard.config import Config, AttackType
from dtguard.data import load_data, create_federated_dataset
from dtguard.models import IoTAttackNet, GANGenerator
from dtguard.models.ids_model import get_parameters, set_parameters, train_model, evaluate_model
from dtguard.security import DigitalTwinVerifier, apply_attack
from dtguard.fl.aggregation import compute_verification_stats
from dtguard.fl.baselines import (
    federated_averaging, krum_aggregation, median_aggregation,
    trimmed_mean_aggregation, lup_aggregation, clipcluster_aggregation,
    signguard_aggregation, poc_aggregation, geomed_aggregation,
)

# ---- Settings: fast but meaningful ----
NUM_CLIENTS   = 6
NUM_MALICIOUS = 3       # 50% — same as LUP paper
NUM_ROUNDS    = 10
LOCAL_EPOCHS  = 3
BATCH_SIZE    = 256
LR            = 0.001
DIRICHLET     = 0.5
ATTACK_SCALE  = 10.0
GAN_EPOCHS    = 20
SEED          = 42

ATTACKS = {
    "No Attack":  None,
    "Backdoor":   AttackType.BACKDOOR,
    "LIE":        AttackType.LIE,
    "Min-Max":    AttackType.MIN_MAX,
    "Min-Sum":    AttackType.MIN_SUM,
    "MPAF":       AttackType.MPAF,
}

DEFENSES = [
    "DT-Guard", "LUP", "ClipCluster", "SignGuard", "GeoMed",
    "PoC", "FedAvg", "Krum", "Median", "Trimmed Mean",
]
# DEFENSES = [
#     "DT-Guard", "LUP", "ClipCluster", "SignGuard", "GeoMed",
#     "PoC",
# ]


def run_one(defense_name, attack_type,
            X_clients, y_clients, X_test, y_test,
            input_dim, num_classes, device,
            cached_verifier=None):
    """Run a single (defense, attack) combo. Data is passed in, not re-created."""

    n_mal = 0 if attack_type is None else NUM_MALICIOUS
    malicious_indices = list(range(NUM_CLIENTS - n_mal, NUM_CLIENTS))

    # Fresh models every run (same init via seed)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    global_model = IoTAttackNet(input_dim, num_classes)
    client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(NUM_CLIENTS)]

    # Per-defense state
    lup_trust = np.zeros((NUM_CLIENTS, 1))
    poc_history = np.ones(NUM_CLIENTS) * 0.5

    # DT-Guard verifier — reuse cached one (GAN already trained)
    verifier = cached_verifier if defense_name == "DT-Guard" else None
    if verifier is not None:
        verifier.client_history = {}  # Reset between attacks

    accuracies = []
    total_tp = total_fp = total_tn = total_fn = 0

    for rnd in range(NUM_ROUNDS):
        global_weights = get_parameters(global_model)
        client_weights = []

        # Local training
        for i, model in enumerate(client_models):
            set_parameters(model, global_weights)
            train_model(model, X_clients[i], y_clients[i],
                        epochs=LOCAL_EPOCHS, batch_size=BATCH_SIZE,
                        lr=LR, device=device)
            client_weights.append(get_parameters(model))

        # Apply attack to malicious clients
        if n_mal > 0 and attack_type is not None:
            atk_str = attack_type.value
            for mi in malicious_indices:
                client_weights[mi] = apply_attack(
                    client_weights[mi], atk_str, ATTACK_SCALE,
                    all_client_weights=client_weights,
                    malicious_indices=malicious_indices)

        # ---- Aggregation ----
        rejected = []

        if defense_name == "DT-Guard":
            from dtguard.security import calculate_shapley_values, calculate_weighted_shapley, CommitteeSelector
            from dtguard.fl.aggregation import weighted_federated_averaging as wfa

            verified_w, verified_idx, v_scores = [], [], []
            verification_results = []
            selector = CommitteeSelector(num_clients=NUM_CLIENTS, committee_size=1)
            seeds = selector.committee_seeds(rnd + 1)
            for i in range(NUM_CLIENTS):
                set_parameters(client_models[i], client_weights[i])
                sc_list, pass_list = [], []
                for seed in seeds:
                    res = verifier.verify(client_models[i], device,
                                          global_model=global_model,
                                          client_id=i, challenge_seed=seed,
                                          round_num=rnd + 1,
                                          data_size=len(X_clients[i]))
                    sc_list.append(res['score'])
                    pass_list.append(res['passed'])
                passed = sum(pass_list) >= (len(pass_list) // 2 + 1)
                verification_results.append(passed)
                if passed:
                    verified_w.append(client_weights[i])
                    verified_idx.append(i)
                    v_scores.append(float(np.mean(sc_list)))

            if verified_w:
                vm = [client_models[i] for i in verified_idx]
                sv = calculate_shapley_values(vm, verified_w, X_test, y_test, device,
                                              n_samples=3, eval_subsample=500)
                aw = calculate_weighted_shapley(sv, v_scores)
                aggregated = wfa(verified_w, aw)
            else:
                aggregated, _ = federated_averaging(client_weights)
                verification_results = [True] * NUM_CLIENTS
            rejected = [i for i in range(NUM_CLIENTS) if not verification_results[i]]

        elif defense_name == "FedAvg":
            aggregated, rejected = federated_averaging(client_weights)
        elif defense_name == "Krum":
            aggregated, rejected = krum_aggregation(client_weights, f=n_mal)
        elif defense_name == "Median":
            aggregated, rejected = median_aggregation(client_weights)
        elif defense_name == "Trimmed Mean":
            aggregated, rejected = trimmed_mean_aggregation(client_weights, trim_ratio=0.2)
        elif defense_name == "LUP":
            aggregated, rejected = lup_aggregation(
                client_weights, global_weights=global_weights, trust_scores=lup_trust)
            for idx in range(NUM_CLIENTS):
                if idx not in rejected:
                    lup_trust[idx, 0] += 1.0
        elif defense_name == "ClipCluster":
            aggregated, rejected = clipcluster_aggregation(
                client_weights, global_weights=global_weights)
        elif defense_name == "GeoMed":
            aggregated, rejected = geomed_aggregation(
                client_weights, global_weights=global_weights)
        elif defense_name == "SignGuard":
            aggregated, rejected = signguard_aggregation(
                client_weights, global_weights=global_weights)
        elif defense_name == "PoC":
            data_sizes = [len(X_clients[i]) for i in range(NUM_CLIENTS)]
            aggregated, rejected = poc_aggregation(
                client_weights, global_weights=global_weights,
                client_data_sizes=data_sizes, contribution_history=poc_history)
            for idx in range(NUM_CLIENTS):
                poc_history[idx] += (0.1 if idx not in rejected else -0.2)
                poc_history[idx] = float(np.clip(poc_history[idx], 0, 1))
        else:
            aggregated, rejected = federated_averaging(client_weights)

        # Stats
        vr = [i not in rejected for i in range(NUM_CLIENTS)]
        stats = compute_verification_stats(NUM_CLIENTS, malicious_indices, vr)
        total_tp += stats['tp']; total_fp += stats['fp']
        total_tn += stats['tn']; total_fn += stats['fn']

        set_parameters(global_model, aggregated)
        acc = evaluate_model(global_model, X_test, y_test, device=device)
        accuracies.append(acc)

    det = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    fpr = total_fp / (total_fp + total_tn) if (total_fp + total_tn) > 0 else 0.0
    return accuracies[-1], det, fpr


def main():
    start = datetime.now()
    print("=" * 95)
    print("  QUICK TEST: Experiment 3  (10 defenses × 6 attacks)")
    print("=" * 95)
    print(f"  Start:   {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Setup:   {NUM_CLIENTS} clients, {NUM_MALICIOUS} malicious (50%), "
          f"{NUM_ROUNDS} rounds, {LOCAL_EPOCHS} epochs/round")
    print(f"  Attacks: {list(ATTACKS.keys())}")
    print(f"  Defenses:{DEFENSES}")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"  Device:  {device}\n")

    # ---- Load data ONCE ----
    print("  Loading CIC-IoT-2023 data...")
    cfg = Config(dataset_dir="data/CICIoT2023")
    train_df, test_df, feature_cols = load_data(cfg)

    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df['Label'].values.astype(np.int64)
    input_dim = len(feature_cols)
    num_classes = len(np.unique(y_test))
    print(f"  Features: {input_dim}, Classes: {num_classes}, "
          f"Train: {len(train_df)}, Test: {len(test_df)}")

    # ---- Split data ONCE with fixed seed ----
    np.random.seed(SEED)
    split_cfg = Config(num_clients=NUM_CLIENTS, dirichlet_alpha=DIRICHLET)
    X_clients, y_clients = create_federated_dataset(
        train_df, feature_cols, split_cfg, verbose=True,
        max_samples_per_client=10_000)  # Cap data per client for speed
    print()

    # ---- Pre-train GAN ONCE for DT-Guard (biggest speedup) ----
    print("  Training GAN for DT-Guard (one-time)...", end=" ", flush=True)
    t0 = time.time()
    gan = GANGenerator(latent_dim=100, output_dim=input_dim)
    # Use all non-malicious clients' data for GAN
    benign_X = [X_clients[i] for i in range(NUM_CLIENTS - NUM_MALICIOUS)]
    benign_y = [y_clients[i] for i in range(NUM_CLIENTS - NUM_MALICIOUS)]
    gan.train_gan(benign_X, benign_y, epochs=GAN_EPOCHS, device=device)
    cached_verifier = DigitalTwinVerifier(gan, threshold=0.65, challenge_samples=100)
    print(f"done ({time.time() - t0:.1f}s)\n")

    atk_names = list(ATTACKS.keys())
    passed_count = 0
    failed_count = 0
    total = len(DEFENSES) * len(ATTACKS)

    # Header
    hdr = f"  {'Defense':<15}"
    for a in atk_names:
        hdr += f" {a:>10}"
    hdr += "   Time  Status"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))

    for defense in DEFENSES:
        row = f"  {defense:<15}"
        defense_ok = True
        t_defense = 0.0

        for atk_name, atk_type in ATTACKS.items():
            try:
                t0 = time.time()
                acc, det, fpr = run_one(
                    defense, atk_type,
                    X_clients, y_clients, X_test, y_test,
                    input_dim, num_classes, device,
                    cached_verifier=cached_verifier if defense == "DT-Guard" else None)
                elapsed = time.time() - t0
                t_defense += elapsed
                row += f" {acc * 100:>9.1f}%"
                passed_count += 1
            except Exception:
                row += f"  {'FAIL':>9}"
                defense_ok = False
                failed_count += 1
                traceback.print_exc()

        row += f"  {t_defense:>5.0f}s  {'✅' if defense_ok else '❌'}"
        print(row)

    end = datetime.now()
    print(f"\n{'=' * 95}")
    print(f"  Results:  {passed_count}/{total} passed, {failed_count}/{total} failed")
    print(f"  Duration: {end - start}")
    if failed_count == 0:
        print("  ✅ ALL TESTS PASSED — safe to run full experiment3!")
    else:
        print("  ❌ SOME TESTS FAILED — fix before running full experiment3!")
    print(f"{'=' * 95}")


if __name__ == "__main__":
    main()

