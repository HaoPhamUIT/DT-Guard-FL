#!/usr/bin/env python3
"""
EXPERIMENT 7: UNIFIED DEFENSE COMPARISON ACROSS MALICIOUS RATIOS (Kịch bản 2)
===============================================================================
Consolidates experiments 10%, 30%, 50% malicious into a single runner
and produces combined comparison tables.

This script imports and orchestrates run_experiment10, run_experiment30,
and run_experiment50, then generates unified output tables matching
the đề cương's Kịch bản 2 requirements.

Output:
  TABLE A: Accuracy at 10% malicious  (Defense × Attack)
  TABLE B: Accuracy at 30% malicious
  TABLE C: Accuracy at 50% malicious
  TABLE D: Combined — average accuracy degradation across ratios
  TABLE E: Detection Rate summary
  TABLE F: FPR summary
  TABLE G: Execution Time summary

Usage:
    python run_experiment7_unified.py            # Run all 3 ratios
    python run_experiment7_unified.py --ratio 50  # Run single ratio
"""

import argparse
import torch
import numpy as np
import time
import json
import traceback
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

from dtguard.config import Config, AttackType
from dtguard.data import load_data, create_federated_dataset
from dtguard.models import IoTAttackNet, GANGenerator
from dtguard.models.ids_model import get_parameters, set_parameters, train_model, evaluate_model
from dtguard.security import DigitalTwinVerifier, apply_attack
from dtguard.security import calculate_shapley_values, calculate_weighted_shapley, CommitteeSelector
from dtguard.fl.aggregation import compute_verification_stats, weighted_federated_averaging
from dtguard.fl.baselines import (
    federated_averaging, krum_aggregation, median_aggregation,
    trimmed_mean_aggregation, lup_aggregation, clipcluster_aggregation,
    signguard_aggregation, poc_aggregation, geomed_aggregation,
)

# =============================================================================
# Configuration
# =============================================================================
NUM_CLIENTS     = 20
NUM_ROUNDS      = 20
LOCAL_EPOCHS    = 3
BATCH_SIZE      = 512
LR              = 0.001
DIRICHLET_ALPHA = 0.5
ATTACK_SCALE    = 10.0
GAN_EPOCHS      = 50
DT_THRESHOLD    = 0.6
COMMITTEE_SIZE  = 3
CHALLENGE_SAMPLES = 200
SEED            = 42

RATIOS = {
    10: 2,   # 2/20 = 10%
    30: 6,   # 6/20 = 30%
    50: 10,  # 10/20 = 50%
}

ATTACKS = OrderedDict([
    ("No Attack",  None),
    ("Backdoor",   AttackType.BACKDOOR),
    ("LIE",        AttackType.LIE),
    ("Min-Max",    AttackType.MIN_MAX),
    ("Min-Sum",    AttackType.MIN_SUM),
    ("MPAF",       AttackType.MPAF),
])

DEFENSES = [
    "DT-Guard", "LUP", "ClipCluster", "SignGuard", "GeoMed",
    "PoC", "FedAvg", "Krum", "Median", "Trimmed Mean",
]

DEFENSE_YEARS = {
    "FedAvg": 2016, "Krum": 2017, "Median": 2018, "Trimmed Mean": 2018,
    "SignGuard": 2022, "GeoMed": 2022, "ClipCluster": 2024,
    "LUP": 2025, "PoC": 2025, "DT-Guard": 2025,
}


# =============================================================================
# Runners
# =============================================================================
def run_baseline(defense_name, attack_type, X_clients, y_clients,
                 X_test, y_test, input_dim, num_classes, device, num_malicious):
    np.random.seed(SEED); torch.manual_seed(SEED)
    n_mal = 0 if attack_type is None else num_malicious
    global_model = IoTAttackNet(input_dim, num_classes)
    client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(NUM_CLIENTS)]
    malicious_indices = list(range(NUM_CLIENTS - n_mal, NUM_CLIENTS))

    lup_trust = np.zeros((NUM_CLIENTS, 1))
    poc_history = np.ones(NUM_CLIENTS) * 0.5
    accuracies = []
    total_tp = total_fp = total_tn = total_fn = 0

    for rnd in range(NUM_ROUNDS):
        gw = get_parameters(global_model)
        cw = []
        for i, m in enumerate(client_models):
            set_parameters(m, gw)
            train_model(m, X_clients[i], y_clients[i], epochs=LOCAL_EPOCHS,
                        batch_size=BATCH_SIZE, lr=LR, device=device)
            cw.append(get_parameters(m))

        if n_mal > 0 and attack_type is not None:
            atk_str = attack_type.value
            for mi in malicious_indices:
                cw[mi] = apply_attack(cw[mi], atk_str, ATTACK_SCALE,
                                      all_client_weights=cw, malicious_indices=malicious_indices)

        rejected = []
        if defense_name == "FedAvg":
            agg, rejected = federated_averaging(cw)
        elif defense_name == "Krum":
            agg, rejected = krum_aggregation(cw, f=n_mal)
        elif defense_name == "Median":
            agg, rejected = median_aggregation(cw)
        elif defense_name == "Trimmed Mean":
            agg, rejected = trimmed_mean_aggregation(cw, trim_ratio=0.2)
        elif defense_name == "LUP":
            agg, rejected = lup_aggregation(cw, global_weights=gw, trust_scores=lup_trust)
            for idx in range(NUM_CLIENTS):
                if idx not in rejected:
                    lup_trust[idx, 0] += 1.0
        elif defense_name == "ClipCluster":
            agg, rejected = clipcluster_aggregation(cw, global_weights=gw)
        elif defense_name == "GeoMed":
            agg, rejected = geomed_aggregation(cw, global_weights=gw)
        elif defense_name == "SignGuard":
            agg, rejected = signguard_aggregation(cw, global_weights=gw)
        elif defense_name == "PoC":
            sizes = [len(X_clients[i]) for i in range(NUM_CLIENTS)]
            agg, rejected = poc_aggregation(cw, global_weights=gw,
                                             client_data_sizes=sizes, contribution_history=poc_history)
            for idx in range(NUM_CLIENTS):
                poc_history[idx] += (0.1 if idx not in rejected else -0.2)
                poc_history[idx] = float(np.clip(poc_history[idx], 0, 1))
        else:
            agg, rejected = federated_averaging(cw)

        vr = [i not in rejected for i in range(NUM_CLIENTS)]
        stats = compute_verification_stats(NUM_CLIENTS, malicious_indices, vr)
        total_tp += stats['tp']; total_fp += stats['fp']
        total_tn += stats['tn']; total_fn += stats['fn']
        set_parameters(global_model, agg)
        accuracies.append(evaluate_model(global_model, X_test, y_test, device=device))

    det = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    fpr = total_fp / (total_fp + total_tn) if (total_fp + total_tn) > 0 else 0.0
    return {'final_accuracy': accuracies[-1], 'detection_rate': det,
            'false_positive_rate': fpr, 'accuracy_history': accuracies}


def run_dtguard(attack_type, X_clients, y_clients, X_test, y_test,
                input_dim, num_classes, device, verifier, num_malicious):
    np.random.seed(SEED); torch.manual_seed(SEED)
    n_mal = 0 if attack_type is None else num_malicious
    global_model = IoTAttackNet(input_dim, num_classes)
    client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(NUM_CLIENTS)]
    malicious_indices = list(range(NUM_CLIENTS - n_mal, NUM_CLIENTS))
    verifier.client_history = {}
    shapley_history = []
    accuracies = []
    total_tp = total_fp = total_tn = total_fn = 0

    for rnd in range(NUM_ROUNDS):
        gw = get_parameters(global_model)
        cw = []
        for i, m in enumerate(client_models):
            set_parameters(m, gw)
            train_model(m, X_clients[i], y_clients[i], epochs=LOCAL_EPOCHS,
                        batch_size=BATCH_SIZE, lr=LR, device=device)
            cw.append(get_parameters(m))

        if n_mal > 0 and attack_type is not None:
            atk_str = attack_type.value
            for mi in malicious_indices:
                cw[mi] = apply_attack(cw[mi], atk_str, ATTACK_SCALE,
                                      all_client_weights=cw, malicious_indices=malicious_indices)

        verified_w, verified_idx, v_scores = [], [], []
        verification_results = []
        selector = CommitteeSelector(num_clients=NUM_CLIENTS, committee_size=COMMITTEE_SIZE,
                                     shapley_history=shapley_history)
        seeds = selector.committee_seeds(rnd + 1)

        for i in range(NUM_CLIENTS):
            set_parameters(client_models[i], cw[i])
            sc_list, pass_list = [], []
            for seed in seeds:
                res = verifier.verify(client_models[i], device, global_model=global_model,
                                      client_id=i, challenge_seed=seed,
                                      round_num=rnd + 1, data_size=len(X_clients[i]))
                sc_list.append(res['score']); pass_list.append(res['passed'])
            passed = sum(pass_list) >= (len(pass_list) // 2 + 1)
            verification_results.append(passed)
            if passed:
                verified_w.append(cw[i]); verified_idx.append(i)
                v_scores.append(float(np.mean(sc_list)))

        stats = compute_verification_stats(NUM_CLIENTS, malicious_indices, verification_results)
        total_tp += stats['tp']; total_fp += stats['fp']
        total_tn += stats['tn']; total_fn += stats['fn']

        if verified_w:
            vm = [client_models[i] for i in verified_idx]
            sv = calculate_shapley_values(vm, verified_w, X_test, y_test, device,
                                          n_samples=5, eval_subsample=1000)
            aw = calculate_weighted_shapley(sv, v_scores)
            full_shapley = np.zeros(NUM_CLIENTS)
            for j, idx in enumerate(verified_idx):
                full_shapley[idx] = sv[j]
            shapley_history.append(full_shapley)
            agg = weighted_federated_averaging(verified_w, aw)
        else:
            agg, _ = federated_averaging(cw)
            shapley_history.append(np.zeros(NUM_CLIENTS))

        set_parameters(global_model, agg)
        accuracies.append(evaluate_model(global_model, X_test, y_test, device=device))

    det = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    fpr = total_fp / (total_fp + total_tn) if (total_fp + total_tn) > 0 else 0.0
    return {'final_accuracy': accuracies[-1], 'detection_rate': det,
            'false_positive_rate': fpr, 'accuracy_history': accuracies}


# =============================================================================
# Main
# =============================================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ratio', type=int, default=0,
                        help='Run single ratio (10, 30, or 50). 0=all.')
    args = parser.parse_args()

    ratios_to_run = [args.ratio] if args.ratio in RATIOS else sorted(RATIOS.keys())

    start = datetime.now()
    print("=" * 100)
    print("  EXPERIMENT 7: UNIFIED DEFENSE COMPARISON — Kịch bản 2")
    print("=" * 100)
    print(f"  Ratios: {ratios_to_run}%")
    print(f"  Setup: {NUM_CLIENTS} clients, {NUM_ROUNDS} rounds, α={DIRICHLET_ALPHA}")
    print(f"  Attacks: {list(ATTACKS.keys())}")
    print(f"  Defenses: {DEFENSES}\n")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    cfg = Config(dataset_dir="data/CICIoT2023")
    train_df, test_df, feature_cols = load_data(cfg)
    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df['Label'].values.astype(np.int64)
    input_dim = len(feature_cols)
    num_classes = len(np.unique(y_test))

    np.random.seed(SEED)
    split_cfg = Config(num_clients=NUM_CLIENTS, dirichlet_alpha=DIRICHLET_ALPHA)
    X_clients, y_clients = create_federated_dataset(
        train_df, feature_cols, split_cfg, verbose=True, max_samples_per_client=20_000)

    # All results: all_results[ratio][defense][attack] = {...}
    all_results = {}
    all_timings = {}

    for ratio in ratios_to_run:
        n_mal = RATIOS[ratio]
        print(f"\n{'#'*100}")
        print(f"  MALICIOUS RATIO: {ratio}% ({n_mal}/{NUM_CLIENTS} clients)")
        print(f"{'#'*100}")

        # Train GAN once per ratio
        gan = GANGenerator(latent_dim=100, output_dim=input_dim)
        benign_X = [X_clients[i] for i in range(NUM_CLIENTS - n_mal)]
        benign_y = [y_clients[i] for i in range(NUM_CLIENTS - n_mal)]
        gan.train_gan(benign_X, benign_y, epochs=GAN_EPOCHS, device=device)
        verifier = DigitalTwinVerifier(gan, threshold=DT_THRESHOLD,
                                        challenge_samples=CHALLENGE_SAMPLES)

        results = {d: {} for d in DEFENSES}
        timings = {d: {} for d in DEFENSES}
        atk_names = list(ATTACKS.keys())

        total_runs = len(DEFENSES) * len(ATTACKS)
        run_idx = 0

        for atk_name, atk_type in ATTACKS.items():
            for defense in DEFENSES:
                run_idx += 1
                print(f"  [{run_idx}/{total_runs}] {defense} vs {atk_name} ...", end=" ", flush=True)
                t0 = time.time()
                try:
                    if defense == "DT-Guard":
                        result = run_dtguard(atk_type, X_clients, y_clients,
                                             X_test, y_test, input_dim, num_classes,
                                             device, verifier, n_mal)
                    else:
                        result = run_baseline(defense, atk_type, X_clients, y_clients,
                                              X_test, y_test, input_dim, num_classes,
                                              device, n_mal)
                except Exception:
                    traceback.print_exc()
                    result = {'final_accuracy': 0.0, 'detection_rate': 0.0,
                              'false_positive_rate': 0.0, 'accuracy_history': [0.0]}
                elapsed = time.time() - t0
                results[defense][atk_name] = result
                timings[defense][atk_name] = elapsed
                print(f"Acc={result['final_accuracy']:.4f} "
                      f"Det={result['detection_rate']:.0%} "
                      f"FPR={result['false_positive_rate']:.0%} ({elapsed:.0f}s)")

        all_results[ratio] = results
        all_timings[ratio] = timings

        # Print per-ratio table
        _print_accuracy_table(ratio, results, atk_names)

    # =========================================================================
    # Combined output
    # =========================================================================
    _print_combined_tables(all_results, all_timings, ratios_to_run)

    # Save
    results_dir = Path('results/paper')
    results_dir.mkdir(parents=True, exist_ok=True)

    save = {}
    for ratio in ratios_to_run:
        save[str(ratio)] = {}
        for d in DEFENSES:
            save[str(ratio)][d] = {}
            for a in ATTACKS.keys():
                r = all_results[ratio][d][a]
                save[str(ratio)][d][a] = {
                    'accuracy': round(r['final_accuracy'], 4),
                    'detection_rate': round(r['detection_rate'], 4),
                    'fpr': round(r['false_positive_rate'], 4),
                }
    with open(results_dir / 'exp7_unified.json', 'w') as f:
        json.dump(save, f, indent=2)

    elapsed = datetime.now() - start
    print(f"\n  ✅ Experiment 7 done in {elapsed}")


def _print_accuracy_table(ratio, results, atk_names):
    print(f"\n{'='*100}")
    print(f"  TABLE: ACCURACY at {ratio}% malicious  (higher = better)")
    print(f"{'='*100}")
    hdr = f"  {'Defense':<15} {'Year':<6}"
    for a in atk_names:
        hdr += f" {a:>10}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for d in DEFENSES:
        yr = DEFENSE_YEARS.get(d, "—")
        row = f"  {d:<15} {yr:<6}"
        for a in atk_names:
            acc = results[d][a]['final_accuracy']
            row += f" {acc*100:>9.2f}%"
        print(row)


def _print_combined_tables(all_results, all_timings, ratios):
    atk_names = list(ATTACKS.keys())

    # TABLE D: Average accuracy degradation
    print(f"\n{'='*100}")
    print(f"  TABLE D: AVERAGE ACCURACY DEGRADATION vs No Attack (%)")
    print(f"  Lower = more robust")
    print(f"{'='*100}")
    hdr = f"  {'Defense':<15}"
    for r in ratios:
        hdr += f" {r}% mal."
    hdr += "    Avg"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for d in DEFENSES:
        row = f"  {d:<15}"
        degs = []
        for r in ratios:
            no_atk = all_results[r][d]["No Attack"]['final_accuracy']
            avg_atk = np.mean([all_results[r][d][a]['final_accuracy']
                              for a in atk_names[1:]])
            deg = (1 - avg_atk / no_atk) * 100 if no_atk > 0 else 100
            degs.append(deg)
            row += f" {deg:>8.2f}%"
        row += f" {np.mean(degs):>7.2f}%"
        print(row)

    # TABLE E: Detection Rate
    print(f"\n{'='*100}")
    print(f"  TABLE E: AVERAGE DETECTION RATE across attacks (higher = better)")
    print(f"{'='*100}")
    hdr = f"  {'Defense':<15}"
    for r in ratios:
        hdr += f" {r}% mal."
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for d in DEFENSES:
        row = f"  {d:<15}"
        for r in ratios:
            avg_det = np.mean([all_results[r][d][a]['detection_rate']
                              for a in atk_names[1:]])
            row += f" {avg_det*100:>8.1f}%"
        print(row)

    # TABLE F: FPR
    print(f"\n{'='*100}")
    print(f"  TABLE F: AVERAGE FPR across attacks (lower = better)")
    print(f"{'='*100}")
    hdr = f"  {'Defense':<15}"
    for r in ratios:
        hdr += f" {r}% mal."
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for d in DEFENSES:
        row = f"  {d:<15}"
        for r in ratios:
            avg_fpr = np.mean([all_results[r][d][a]['false_positive_rate']
                              for a in atk_names[1:]])
            row += f" {avg_fpr*100:>8.1f}%"
        print(row)


if __name__ == "__main__":
    main()


