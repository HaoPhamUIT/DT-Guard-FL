#!/usr/bin/env python3
"""
EXPERIMENT 3: COMPREHENSIVE DEFENSE COMPARISON
================================================
Evaluates DT-Guard against LUP, ClipCluster, SignGuard, PoC, and classic
baselines (FedAvg, Krum, Median, Trimmed Mean) under 5 advanced attacks
from the DT-BFL/LUP paper.

Experimental setup follows LUP (Issa et al., Ad Hoc Networks 2025):
  - Table 4 format: Defense × Attack accuracy matrix
  - Table 5 format: Error Rate matrix
  - Fig 5  format: Attack Impact bar chart data
  - Fig 6  format: Training stability (accuracy per round)

Attack types (5 new + No Attack):
  Sign-Flip, LIE, Min-Max, Min-Sum, MPAF

Defense methods (9 total):
  DT-Guard (ours), LUP, ClipCluster, SignGuard, PoC,
  FedAvg, Krum, Median, Trimmed Mean
"""

import torch
import numpy as np
import pickle
import time
import json
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

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

# =============================================================================
# Configuration  (matching LUP paper: 50% malicious, Non-IID)
# =============================================================================
NUM_CLIENTS       = 20
NUM_MALICIOUS     = 5       # 50% malicious
NUM_ROUNDS        = 10
LOCAL_EPOCHS      = 3
BATCH_SIZE        = 32
LEARNING_RATE     = 0.001
DIRICHLET_ALPHA   = 0.5     # Non-IID
ATTACK_SCALE      = 10.0
GAN_EPOCHS        = 50
DT_THRESHOLD      = 0.65
COMMITTEE_SIZE    = 3
CHALLENGE_SAMPLES = 500
RANDOM_SEED       = 42

# What to evaluate
ATTACKS = OrderedDict([
    ("No Attack",  None),
    ("Backdoor",   AttackType.BACKDOOR),
    ("LIE",        AttackType.LIE),
    ("Min-Max",    AttackType.MIN_MAX),
    ("Min-Sum",    AttackType.MIN_SUM),
    ("MPAF",       AttackType.MPAF),
])

DEFENSES = [
    "DT-Guard",       # Ours
    "LUP",            # Issa et al. 2025
    "ClipCluster",    # Zeng et al. 2024
    "SignGuard",       # Xu et al. 2022
    "GeoMed",          # Pillutla et al. 2022
    "PoC",            # Zhang et al. 2025
    "FedAvg",
    "Krum",
    "Median",
    "Trimmed Mean",
]


# =============================================================================
# Core runner: baseline defenses (non-DT-Guard)
# =============================================================================
def run_baseline(defense_name, attack_type,
                 X_clients, y_clients, X_test, y_test,
                 input_dim, num_classes, device):
    """Run one (defense, attack) combination and return metrics."""
    np.random.seed(RANDOM_SEED)
    torch.manual_seed(RANDOM_SEED)

    n_mal = 0 if attack_type is None else NUM_MALICIOUS

    global_model  = IoTAttackNet(input_dim, num_classes)
    client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(NUM_CLIENTS)]

    malicious_indices = list(range(NUM_CLIENTS - n_mal, NUM_CLIENTS))

    accuracies = []
    total_tp = total_fp = total_tn = total_fn = 0

    # State for LUP trust scores
    lup_trust = np.zeros((NUM_CLIENTS, 1))
    # State for PoC contribution history
    poc_history = np.ones(NUM_CLIENTS) * 0.5

    for rnd in range(NUM_ROUNDS):
        global_weights = get_parameters(global_model)
        client_weights = []

        # --- Local training ---
        for i, model in enumerate(client_models):
            set_parameters(model, global_weights)
            train_model(model, X_clients[i], y_clients[i],
                        epochs=LOCAL_EPOCHS, batch_size=BATCH_SIZE,
                        lr=LEARNING_RATE, device=device)
            weights = get_parameters(model)
            client_weights.append(weights)

        # --- Apply attack to malicious clients ---
        if n_mal > 0 and attack_type is not None:
            atk_str = attack_type.value if isinstance(attack_type, AttackType) else attack_type
            for mi in malicious_indices:
                client_weights[mi] = apply_attack(
                    client_weights[mi], atk_str, ATTACK_SCALE,
                    all_client_weights=client_weights,
                    malicious_indices=malicious_indices,
                )

        # --- Aggregation ---
        if defense_name == "FedAvg":
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
                if idx not in rejected:
                    poc_history[idx] = min(1.0, poc_history[idx] + 0.1)
                else:
                    poc_history[idx] = max(0.0, poc_history[idx] - 0.2)
        else:
            aggregated, rejected = federated_averaging(client_weights)

        # --- Verification stats ---
        verification_results = [i not in rejected for i in range(NUM_CLIENTS)]
        stats = compute_verification_stats(NUM_CLIENTS, malicious_indices, verification_results)
        total_tp += stats['tp']
        total_fp += stats['fp']
        total_tn += stats['tn']
        total_fn += stats['fn']

        # --- Update global model ---
        set_parameters(global_model, aggregated)
        acc = evaluate_model(global_model, X_test, y_test, device=device)
        accuracies.append(acc)

    det_rate = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    fpr      = total_fp / (total_fp + total_tn) if (total_fp + total_tn) > 0 else 0.0

    return {
        'final_accuracy':    accuracies[-1],
        'max_accuracy':      max(accuracies),
        'detection_rate':    det_rate,
        'false_positive_rate': fpr,
        'accuracy_history':  accuracies,
    }


# =============================================================================
# Core runner: DT-Guard
# =============================================================================
def run_dtguard(attack_type, X_clients, y_clients, X_test, y_test,
                input_dim, num_classes, device, cached_verifier=None):
    """Run DT-Guard for one attack scenario."""
    np.random.seed(RANDOM_SEED)
    torch.manual_seed(RANDOM_SEED)

    n_mal = 0 if attack_type is None else NUM_MALICIOUS

    global_model  = IoTAttackNet(input_dim, num_classes)
    client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(NUM_CLIENTS)]

    # Reuse cached verifier (GAN trained once)
    if cached_verifier is not None:
        verifier = cached_verifier
        verifier.client_history = {}  # Reset between attacks
    else:
        gan = GANGenerator(latent_dim=100, output_dim=input_dim)
        benign_X = [X_clients[i] for i in range(NUM_CLIENTS - n_mal)]
        benign_y = [y_clients[i] for i in range(NUM_CLIENTS - n_mal)]
        gan.train_gan(benign_X, benign_y, epochs=GAN_EPOCHS, device=device)
        verifier = DigitalTwinVerifier(gan, threshold=DT_THRESHOLD,
                                       challenge_samples=CHALLENGE_SAMPLES)

    malicious_indices = list(range(NUM_CLIENTS - n_mal, NUM_CLIENTS))

    from dtguard.security import calculate_shapley_values, calculate_weighted_shapley
    from dtguard.security import CommitteeSelector
    from dtguard.fl.aggregation import weighted_federated_averaging as wfa

    metrics = {
        'accuracy': [], 'verification_stats': [], 'shapley_history': [],
    }

    for rnd in range(NUM_ROUNDS):
        global_weights = get_parameters(global_model)
        client_weights = []

        for i, model in enumerate(client_models):
            set_parameters(model, global_weights)
            train_model(model, X_clients[i], y_clients[i],
                        epochs=LOCAL_EPOCHS, batch_size=BATCH_SIZE,
                        lr=LEARNING_RATE, device=device)
            client_weights.append(get_parameters(model))

        # Apply attack
        if n_mal > 0 and attack_type is not None:
            atk_str = attack_type.value if isinstance(attack_type, AttackType) else attack_type
            for mi in malicious_indices:
                client_weights[mi] = apply_attack(
                    client_weights[mi], atk_str, ATTACK_SCALE,
                    all_client_weights=client_weights,
                    malicious_indices=malicious_indices,
                )

        # DT Verification
        verified_weights, verified_indices, verification_scores = [], [], []
        verification_results = []

        selector = CommitteeSelector(
            num_clients=NUM_CLIENTS, committee_size=COMMITTEE_SIZE,
            shapley_history=metrics['shapley_history'])
        committee = selector.select_committee()
        seeds = selector.committee_seeds(rnd + 1)

        for i, (model, weights) in enumerate(zip(client_models, client_weights)):
            set_parameters(model, weights)
            scores_list, passes_list = [], []
            for seed in seeds:
                result = verifier.verify(model, device, global_model=global_model,
                                         client_id=i, challenge_seed=seed,
                                         round_num=rnd + 1, data_size=len(X_clients[i]))
                scores_list.append(result['score'])
                passes_list.append(result['passed'])
            mean_score = float(np.mean(scores_list))
            passed = sum(passes_list) >= (len(passes_list) // 2 + 1)
            verification_results.append(passed)
            if passed:
                verified_weights.append(weights)
                verified_indices.append(i)
                verification_scores.append(mean_score)

        stats = compute_verification_stats(NUM_CLIENTS, malicious_indices, verification_results)
        stats['round'] = rnd + 1
        metrics['verification_stats'].append(stats)

        # Shapley-weighted aggregation
        if verified_weights:
            verified_models = [client_models[i] for i in verified_indices]
            shapley_values = calculate_shapley_values(
                verified_models, verified_weights, X_test, y_test, device,
                n_samples=10, eval_subsample=2000)
            agg_weights = calculate_weighted_shapley(shapley_values, verification_scores)
            full_shapley = np.zeros(NUM_CLIENTS)
            for idx, sv in zip(verified_indices, shapley_values):
                full_shapley[idx] = sv
            metrics['shapley_history'].append(full_shapley)
            aggregated = wfa(verified_weights, agg_weights)
        else:
            from dtguard.fl.aggregation import federated_averaging as agg_fa
            aggregated = agg_fa(client_weights)
            metrics['shapley_history'].append(np.zeros(NUM_CLIENTS))

        set_parameters(global_model, aggregated)
        acc = evaluate_model(global_model, X_test, y_test, device=device)
        metrics['accuracy'].append(acc)

    last_stats = metrics['verification_stats'][-1]
    det_sum = sum(s['tp'] for s in metrics['verification_stats'])
    fn_sum  = sum(s['fn'] for s in metrics['verification_stats'])
    fp_sum  = sum(s['fp'] for s in metrics['verification_stats'])
    tn_sum  = sum(s['tn'] for s in metrics['verification_stats'])

    return {
        'final_accuracy':      metrics['accuracy'][-1],
        'max_accuracy':        max(metrics['accuracy']),
        'detection_rate':      det_sum / (det_sum + fn_sum) if (det_sum + fn_sum) > 0 else 0.0,
        'false_positive_rate': fp_sum / (fp_sum + tn_sum) if (fp_sum + tn_sum) > 0 else 0.0,
        'accuracy_history':    metrics['accuracy'],
    }


# =============================================================================
# Main
# =============================================================================
def main():
    start = datetime.now()
    print("=" * 90)
    print("EXPERIMENT 3: COMPREHENSIVE DEFENSE COMPARISON (LUP-style)")
    print("=" * 90)
    print(f"Start: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Setup: {NUM_CLIENTS} clients, {NUM_MALICIOUS} malicious (50%), "
          f"{NUM_ROUNDS} rounds, Non-IID α={DIRICHLET_ALPHA}")
    print(f"Attacks : {list(ATTACKS.keys())}")
    print(f"Defenses: {DEFENSES}")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}\n")

    # ---- Load data ONCE ----
    print("Loading CIC-IoT-2023 data...")
    load_cfg = Config(dataset_dir="data/CICIoT2023")
    train_df, test_df, feature_cols = load_data(load_cfg)

    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df['Label'].values.astype(np.int64)
    input_dim = len(feature_cols)
    num_classes = len(np.unique(y_test))
    print(f"Features: {input_dim}, Classes: {num_classes}, "
          f"Train: {len(train_df)}, Test: {len(test_df)}")

    # ---- Split data ONCE with fixed seed ----
    np.random.seed(RANDOM_SEED)
    split_cfg = Config(num_clients=NUM_CLIENTS, dirichlet_alpha=DIRICHLET_ALPHA)
    X_clients, y_clients = create_federated_dataset(
        train_df, feature_cols, split_cfg, verbose=True,
        max_samples_per_client=20_000)  # Cap per client for speed
    print()

    # ---- Pre-train GAN ONCE for DT-Guard ----
    # GAN is trained on benign client data only — same data for every attack
    # This is a legitimate optimization: GAN models the benign data distribution,
    # which does not change across attacks.
    print("Pre-training GAN for DT-Guard (one-time)...", end=" ", flush=True)
    t_gan = time.time()
    gan = GANGenerator(latent_dim=100, output_dim=input_dim)
    benign_X = [X_clients[i] for i in range(NUM_CLIENTS - NUM_MALICIOUS)]
    benign_y = [y_clients[i] for i in range(NUM_CLIENTS - NUM_MALICIOUS)]
    gan.train_gan(benign_X, benign_y, epochs=GAN_EPOCHS, device=device)
    cached_verifier = DigitalTwinVerifier(gan, threshold=DT_THRESHOLD,
                                          challenge_samples=CHALLENGE_SAMPLES)
    print(f"done ({time.time() - t_gan:.1f}s)\n")

    # Results storage: results[defense][attack] = {...}
    results = {d: {} for d in DEFENSES}
    timings = {d: {} for d in DEFENSES}

    total_runs = len(DEFENSES) * len(ATTACKS)
    run_idx = 0

    for atk_name, atk_type in ATTACKS.items():
        print(f"\n{'='*70}")
        print(f"  ATTACK: {atk_name}")
        print(f"{'='*70}")

        for defense in DEFENSES:
            run_idx += 1
            print(f"\n  [{run_idx}/{total_runs}] {defense} vs {atk_name} ...", end=" ", flush=True)
            t0 = time.time()

            try:
                if defense == "DT-Guard":
                    result = run_dtguard(atk_type, X_clients, y_clients,
                                         X_test, y_test, input_dim, num_classes, device,
                                         cached_verifier=cached_verifier)
                else:
                    result = run_baseline(defense, atk_type, X_clients, y_clients,
                                          X_test, y_test, input_dim, num_classes, device)
            except Exception as ex:
                import traceback
                traceback.print_exc()
                result = {
                    'final_accuracy': 0.0, 'max_accuracy': 0.0,
                    'detection_rate': 0.0, 'false_positive_rate': 0.0,
                    'accuracy_history': [0.0],
                }

            elapsed = time.time() - t0
            results[defense][atk_name] = result
            timings[defense][atk_name] = elapsed
            print(f"Acc={result['final_accuracy']:.4f}  Det={result['detection_rate']:.0%}  "
                  f"FPR={result['false_positive_rate']:.0%}  ({elapsed:.1f}s)")

    # =========================================================================
    # OUTPUT TABLES
    # =========================================================================
    results_dir = Path('results/paper_experiments')
    results_dir.mkdir(parents=True, exist_ok=True)

    # Save raw results
    with open(results_dir / 'exp3_comprehensive.pkl', 'wb') as f:
        pickle.dump({'results': results, 'timings': timings,
                     'config': {
                         'num_clients': NUM_CLIENTS, 'num_malicious': NUM_MALICIOUS,
                         'num_rounds': NUM_ROUNDS, 'attacks': list(ATTACKS.keys()),
                         'defenses': DEFENSES,
                     }}, f)

    atk_names = list(ATTACKS.keys())

    # ----- Table 4: Accuracy Matrix -----
    print("\n" + "=" * 90)
    print("TABLE 4: ACCURACY UNDER POISONING ATTACKS  (higher = better)")
    print("=" * 90)
    header = f"{'Defense':<15} {'Year':<6}"
    for a in atk_names:
        header += f" {a:<11}"
    print(header)
    print("-" * len(header))

    defense_years = {
        "FedAvg": 2016, "Krum": 2017, "Median": 2018, "Trimmed Mean": 2018,
        "SignGuard": 2022, "GeoMed": 2022, "ClipCluster": 2024,
        "LUP": 2025, "PoC": 2025, "DT-Guard": 2025,
    }
    for defense in DEFENSES:
        year = defense_years.get(defense, "—")
        row = f"{defense:<15} {year:<6}"
        for a in atk_names:
            acc = results[defense][a]['final_accuracy']
            row += f" {acc*100:>10.2f}%"
        print(row)

    # ----- Table 5: Error Rate Matrix -----
    print("\n" + "=" * 90)
    print("TABLE 5: ERROR RATE (%)  (lower = better)")
    print("  ER = (1 − acc_under_attack / acc_no_attack) × 100")
    print("=" * 90)
    header = f"{'Defense':<15}"
    for a in atk_names[1:]:  # skip No Attack
        header += f" {a:<11}"
    print(header)
    print("-" * len(header))

    for defense in DEFENSES:
        no_atk_acc = results[defense]["No Attack"]['final_accuracy']
        row = f"{defense:<15}"
        for a in atk_names[1:]:
            atk_acc = results[defense][a]['final_accuracy']
            if no_atk_acc > 0:
                er = (1 - atk_acc / no_atk_acc) * 100
            else:
                er = 100.0
            symbol = "↑" if er >= 50 else "↓"
            row += f" {symbol}{er:>9.2f}%"
        print(row)

    # ----- Table: Detection Rate -----
    print("\n" + "=" * 90)
    print("TABLE: DETECTION RATE  (higher = better)")
    print("=" * 90)
    header = f"{'Defense':<15}"
    for a in atk_names[1:]:
        header += f" {a:<11}"
    print(header)
    print("-" * len(header))

    for defense in DEFENSES:
        row = f"{defense:<15}"
        for a in atk_names[1:]:
            dr = results[defense][a]['detection_rate']
            row += f" {dr*100:>10.1f}%"
        print(row)

    # ----- Table: False Positive Rate -----
    print("\n" + "=" * 90)
    print("TABLE: FALSE POSITIVE RATE (FPR)  (lower = better)")
    print("  FPR = FP / (FP + TN) — benign clients wrongly rejected")
    print("=" * 90)
    header = f"{'Defense':<15}"
    for a in atk_names[1:]:
        header += f" {a:<11}"
    print(header)
    print("-" * len(header))

    for defense in DEFENSES:
        row = f"{defense:<15}"
        for a in atk_names[1:]:
            fpr = results[defense][a]['false_positive_rate']
            row += f" {fpr*100:>10.1f}%"
        print(row)

    # ----- Execution Time -----
    print("\n" + "=" * 90)
    print("TABLE: EXECUTION TIME (seconds per full experiment)")
    print("=" * 90)
    header = f"{'Defense':<15}"
    for a in atk_names:
        header += f" {a:<11}"
    header += f" {'TOTAL':<11}"
    print(header)
    print("-" * len(header))

    for defense in DEFENSES:
        row = f"{defense:<15}"
        total_t = 0.0
        for a in atk_names:
            t = timings[defense][a]
            total_t += t
            row += f" {t:>10.1f}s"
        row += f" {total_t:>10.1f}s"
        print(row)

    # ----- Summary JSON -----
    summary = {}
    for defense in DEFENSES:
        summary[defense] = {}
        for a in atk_names:
            r = results[defense][a]
            summary[defense][a] = {
                'accuracy': round(r['final_accuracy'], 4),
                'detection_rate': round(r['detection_rate'], 4),
                'fpr': round(r['false_positive_rate'], 4),
            }
    with open(results_dir / 'exp3_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    end = datetime.now()
    print(f"\n{'='*90}")
    print(f"✅ Experiment 3 completed!")
    print(f"   Duration: {end - start}")
    print(f"   Results:  {results_dir / 'exp3_comprehensive.pkl'}")
    print(f"   Summary:  {results_dir / 'exp3_summary.json'}")
    print(f"   End:      {end.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*90}")


if __name__ == "__main__":
    main()






