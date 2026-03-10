#!/usr/bin/env python3
"""
EXPERIMENT: OVERHEAD ANALYSIS — Latency & Memory Trade-off
============================================================
Measures per-round wall-clock time and peak memory for each defense
strategy over a full FL training session.
Produces TABLE II in the paper: Per-Round Overhead Comparison
  - Strategy | Train/rnd (s) | Agg/rnd (s) | Peak RSS (MB) | Acc. (%)

After running, update the numbers in:
  DocumentRef/IEEE_paper/IEEE-conference-template-062824.tex
  (search for \\label{tab:overhead})

Usage:
    python run_experiment_overhead.py
    python run_experiment_overhead.py --rounds 10 --clients 10   # quick test
"""

import argparse
import time
import os
import traceback
import numpy as np
import torch
import json
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

from dtguard.config import Config, AttackType
from dtguard.data import load_data, create_federated_dataset
from dtguard.models import IoTAttackNet, GANGenerator
from dtguard.models.ids_model import get_parameters, set_parameters, train_model, evaluate_model
from dtguard.security import (
    DigitalTwinVerifier, apply_attack,
    calculate_shapley_values, calculate_weighted_shapley, CommitteeSelector,
)
from dtguard.fl.aggregation import compute_verification_stats, weighted_federated_averaging
from dtguard.fl.baselines import (
    federated_averaging, krum_aggregation, median_aggregation,
    trimmed_mean_aggregation, lup_aggregation, clipcluster_aggregation,
    signguard_aggregation, poc_aggregation, geomed_aggregation,
)

# Try psutil for memory measurement; fall back to resource module on macOS/Linux
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    import resource


# =============================================================================
# Configuration
# =============================================================================
SEED = 42
DEFAULT_CLIENTS = 20
DEFAULT_ROUNDS = 20
LOCAL_EPOCHS = 3
BATCH_SIZE = 512
LR = 0.001
DIRICHLET_ALPHA = 0.5
ATTACK_SCALE = 10.0
GAN_EPOCHS = 50
DT_THRESHOLD = 0.6
COMMITTEE_SIZE = 3
CHALLENGE_SAMPLES = 200
NUM_MALICIOUS_RATIO = 0.1   # 10% malicious for overhead test

ATTACK = AttackType.BACKDOOR  # single representative attack

DEFENSES_TO_BENCHMARK = [
    "FedAvg",
    "Krum",
    "Median",
    "Trimmed Mean",
    "GeoMed",
    "SignGuard",
    "ClipCluster",
    "LUP",
    "PoC",
    "DT-Guard",
]


# =============================================================================
# Memory helpers
# =============================================================================
def get_memory_mb():
    """Return current process RSS in MB."""
    if HAS_PSUTIL:
        proc = psutil.Process(os.getpid())
        return proc.memory_info().rss / (1024 * 1024)
    else:
        # macOS/Linux fallback (ru_maxrss is in bytes on macOS, KB on Linux)
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        import platform
        if platform.system() == "Darwin":
            return usage / (1024 * 1024)
        else:
            return usage / 1024


# =============================================================================
# Benchmark runner
# =============================================================================
def benchmark_defense(defense_name, X_clients, y_clients, X_test, y_test,
                      input_dim, num_classes, device, num_malicious,
                      num_rounds, num_clients, verifier=None):
    """Run one defense strategy and return timing + memory data."""

    np.random.seed(SEED)
    torch.manual_seed(SEED)

    global_model = IoTAttackNet(input_dim, num_classes).to(device)
    client_models = [IoTAttackNet(input_dim, num_classes).to(device)
                     for _ in range(num_clients)]
    malicious_indices = list(range(num_clients - num_malicious, num_clients))

    lup_trust = np.zeros((num_clients, 1))
    poc_history = np.ones(num_clients) * 0.5
    shapley_history = []

    if verifier is not None:
        verifier.client_history = {}

    round_times = []          # wall-clock per round (training + aggregation)
    train_times = []          # training-only per round
    agg_times = []            # aggregation-only per round (defense overhead)
    dt_verify_times = []      # DT verification per round (DT-Guard only)
    dt_pw_times = []          # DT-PW scoring per round (DT-Guard only)

    mem_before = get_memory_mb()
    peak_mem = mem_before

    for rnd in range(num_rounds):
        round_start = time.perf_counter()

        # ---- Phase 1: Local training (same for all strategies) ----
        train_start = time.perf_counter()
        gw = get_parameters(global_model)
        cw = []
        for i, m in enumerate(client_models):
            set_parameters(m, gw)
            train_model(m, X_clients[i], y_clients[i],
                        epochs=LOCAL_EPOCHS, batch_size=BATCH_SIZE,
                        lr=LR, device=device)
            cw.append(get_parameters(m))

        # Apply attacks
        if num_malicious > 0:
            atk_str = ATTACK.value
            for mi in malicious_indices:
                cw[mi] = apply_attack(cw[mi], atk_str, ATTACK_SCALE,
                                      all_client_weights=cw,
                                      malicious_indices=malicious_indices)
        train_end = time.perf_counter()
        train_times.append(train_end - train_start)

        # ---- Phase 2: Server-side aggregation (varies per defense) ----
        agg_start = time.perf_counter()
        dt_verify_t = 0.0
        dt_pw_t = 0.0

        if defense_name == "DT-Guard":
            # DT Verification
            dt_v_start = time.perf_counter()
            verified_w, verified_idx, v_scores = [], [], []
            verification_results = []
            selector = CommitteeSelector(num_clients=num_clients,
                                         committee_size=COMMITTEE_SIZE,
                                         shapley_history=shapley_history)
            seeds = selector.committee_seeds(rnd + 1)

            for i in range(num_clients):
                set_parameters(client_models[i], cw[i])
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
                    verified_w.append(cw[i])
                    verified_idx.append(i)
                    v_scores.append(float(np.mean(sc_list)))
            dt_verify_t = time.perf_counter() - dt_v_start

            # DT-PW Scoring + Aggregation
            dt_pw_start = time.perf_counter()
            if verified_w:
                vm = [client_models[i] for i in verified_idx]
                sv = calculate_shapley_values(vm, verified_w, X_test, y_test,
                                              device, n_samples=5,
                                              eval_subsample=1000,
                                              global_weights=gw)
                aw = calculate_weighted_shapley(sv, v_scores)
                full_shapley = np.zeros(num_clients)
                for j, idx in enumerate(verified_idx):
                    full_shapley[idx] = sv[j]
                shapley_history.append(full_shapley)
                agg = weighted_federated_averaging(verified_w, aw)
            else:
                agg, _ = federated_averaging(cw)
                shapley_history.append(np.zeros(num_clients))
            dt_pw_t = time.perf_counter() - dt_pw_start

        else:
            # Baseline defenses
            n_mal = num_malicious
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
                agg, rejected = lup_aggregation(cw, global_weights=gw,
                                                trust_scores=lup_trust)
                for idx in range(num_clients):
                    if idx not in rejected:
                        lup_trust[idx, 0] += 1.0
            elif defense_name == "ClipCluster":
                agg, rejected = clipcluster_aggregation(cw, global_weights=gw)
            elif defense_name == "GeoMed":
                agg, rejected = geomed_aggregation(cw, global_weights=gw)
            elif defense_name == "SignGuard":
                agg, rejected = signguard_aggregation(cw, global_weights=gw)
            elif defense_name == "PoC":
                sizes = [len(X_clients[i]) for i in range(num_clients)]
                agg, rejected = poc_aggregation(cw, global_weights=gw,
                                                client_data_sizes=sizes,
                                                contribution_history=poc_history)
                for idx in range(num_clients):
                    poc_history[idx] += (0.1 if idx not in rejected else -0.2)
                    poc_history[idx] = float(np.clip(poc_history[idx], 0, 1))

        agg_end = time.perf_counter()
        agg_times.append(agg_end - agg_start)
        dt_verify_times.append(dt_verify_t)
        dt_pw_times.append(dt_pw_t)

        set_parameters(global_model, agg)

        round_end = time.perf_counter()
        round_times.append(round_end - round_start)

        cur_mem = get_memory_mb()
        if cur_mem > peak_mem:
            peak_mem = cur_mem

    # Final accuracy
    accuracy = evaluate_model(global_model, X_test, y_test, device=device)
    mem_overhead = peak_mem - mem_before

    return {
        "defense": defense_name,
        "total_time_s": sum(round_times),
        "per_round_s": np.mean(round_times),
        "train_per_round_s": np.mean(train_times),
        "agg_per_round_s": np.mean(agg_times),
        "dt_verify_per_round_s": np.mean(dt_verify_times),
        "dt_pw_per_round_s": np.mean(dt_pw_times),
        "peak_mem_mb": peak_mem,
        "mem_overhead_mb": mem_overhead,
        "accuracy": accuracy,
        "round_times": round_times,
        "agg_times": agg_times,
    }


# =============================================================================
# Main
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Overhead benchmark")
    parser.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS)
    parser.add_argument("--clients", type=int, default=DEFAULT_CLIENTS)
    args = parser.parse_args()

    num_rounds = args.rounds
    num_clients = args.clients
    num_malicious = max(1, int(num_clients * NUM_MALICIOUS_RATIO))

    print("=" * 90)
    print("  OVERHEAD ANALYSIS: Latency & Memory Trade-off")
    print("=" * 90)
    print(f"  Clients: {num_clients}  |  Malicious: {num_malicious}")
    print(f"  Rounds: {num_rounds}   |  Attack: {ATTACK.value}")
    print(f"  Local Epochs: {LOCAL_EPOCHS}  |  Batch Size: {BATCH_SIZE}")
    print(f"  Defenses: {DEFENSES_TO_BENCHMARK}")
    print(f"  Memory backend: {'psutil' if HAS_PSUTIL else 'resource (fallback)'}")
    print()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  Device: {device}\n")

    # ---- Load data ----
    cfg = Config(dataset_dir="data/CICIoT2023")
    train_df, test_df, feature_cols = load_data(cfg)
    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df["Label"].values.astype(np.int64)
    input_dim = len(feature_cols)
    num_classes = len(np.unique(y_test))

    np.random.seed(SEED)
    split_cfg = Config(num_clients=num_clients, dirichlet_alpha=DIRICHLET_ALPHA)
    X_clients, y_clients = create_federated_dataset(
        train_df, feature_cols, split_cfg, verbose=True,
        max_samples_per_client=20_000,
    )

    # ---- Train GAN for DT-Guard ----
    print("\n  Training GAN for DT challenge data...")
    gan = GANGenerator(latent_dim=100, output_dim=input_dim)
    benign_X = [X_clients[i] for i in range(num_clients - num_malicious)]
    benign_y = [y_clients[i] for i in range(num_clients - num_malicious)]
    gan.train_gan(benign_X, benign_y, epochs=GAN_EPOCHS, device=device)
    verifier = DigitalTwinVerifier(gan, threshold=DT_THRESHOLD,
                                   challenge_samples=CHALLENGE_SAMPLES)

    # ---- Benchmark each defense ----
    all_results = []

    for defense in DEFENSES_TO_BENCHMARK:
        print(f"\n{'─' * 90}")
        print(f"  Benchmarking: {defense}")
        print(f"{'─' * 90}")

        try:
            result = benchmark_defense(
                defense_name=defense,
                X_clients=X_clients,
                y_clients=y_clients,
                X_test=X_test,
                y_test=y_test,
                input_dim=input_dim,
                num_classes=num_classes,
                device=device,
                num_malicious=num_malicious,
                num_rounds=num_rounds,
                num_clients=num_clients,
                verifier=verifier if defense == "DT-Guard" else None,
            )
            all_results.append(result)

            print(f"    Total: {result['total_time_s']:.1f}s  "
                  f"| Per-round: {result['per_round_s']:.2f}s  "
                  f"| Agg: {result['agg_per_round_s']:.3f}s  "
                  f"| Accuracy: {result['accuracy']:.4f}")
            if defense == "DT-Guard":
                print(f"    DT-Verify: {result['dt_verify_per_round_s']:.3f}s/round  "
                      f"| DT-PW: {result['dt_pw_per_round_s']:.3f}s/round")
        except Exception as e:
            print(f"    ERROR: {e}")
            traceback.print_exc()

    # ---- Print summary table ----
    if not all_results:
        print("\nNo results collected.")
        return

    # Find FedAvg baseline for computing overhead
    fedavg_result = next((r for r in all_results if r["defense"] == "FedAvg"), None)
    fedavg_agg = fedavg_result["agg_per_round_s"] if fedavg_result else 0.0
    fedavg_total = fedavg_result["total_time_s"] if fedavg_result else 1.0

    print(f"\n\n{'=' * 90}")
    print("  TABLE: Per-Round Overhead Comparison")
    print(f"  ({num_clients} clients, {num_rounds} rounds, "
          f"{num_malicious} malicious, attack={ATTACK.value})")
    print(f"{'=' * 90}")

    header = (f"  {'Strategy':<15} {'Total (s)':>10} {'Train (s)':>10} "
              f"{'Agg (s)':>10} {'Overhead':>10} {'Peak RSS':>10} "
              f"{'Mem Δ':>8} {'Acc':>8}")
    print(header)
    print(f"  {'─' * 83}")

    for r in all_results:
        overhead_pct = ((r["agg_per_round_s"] - fedavg_agg) / max(fedavg_agg, 0.001)) * 100
        overhead_str = f"+{overhead_pct:.1f}%" if overhead_pct > 0 else f"{overhead_pct:.1f}%"
        mem_delta = f"+{r['mem_overhead_mb']:.1f}" if r['mem_overhead_mb'] > 0 else f"{r['mem_overhead_mb']:.1f}"

        print(f"  {r['defense']:<15} "
              f"{r['total_time_s']:>10.1f} "
              f"{r['train_per_round_s']:>10.2f} "
              f"{r['agg_per_round_s']:>10.3f} "
              f"{overhead_str:>10} "
              f"{r['peak_mem_mb']:>10.1f} "
              f"{mem_delta:>8} "
              f"{r['accuracy']:>8.4f}")

    # DT-Guard breakdown
    dtg = next((r for r in all_results if r["defense"] == "DT-Guard"), None)
    if dtg:
        print(f"\n  DT-Guard Breakdown (per round):")
        print(f"    Training:       {dtg['train_per_round_s']:.2f}s")
        print(f"    DT Verification:{dtg['dt_verify_per_round_s']:.3f}s")
        print(f"    DT-PW Scoring:  {dtg['dt_pw_per_round_s']:.3f}s")
        print(f"    Total Server:   {dtg['dt_verify_per_round_s'] + dtg['dt_pw_per_round_s']:.3f}s")
        server_overhead = dtg['dt_verify_per_round_s'] + dtg['dt_pw_per_round_s']
        total_per_round = dtg['per_round_s']
        print(f"    Server/Total:   {server_overhead / total_per_round * 100:.1f}%")

    # ---- Save results ----
    out_dir = Path("results/paper_experiments")
    out_dir.mkdir(parents=True, exist_ok=True)

    save_data = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "num_clients": num_clients,
            "num_rounds": num_rounds,
            "num_malicious": num_malicious,
            "attack": ATTACK.value,
            "local_epochs": LOCAL_EPOCHS,
            "batch_size": BATCH_SIZE,
        },
        "results": [],
    }
    for r in all_results:
        entry = {k: v for k, v in r.items() if k not in ("round_times", "agg_times")}
        entry["round_times"] = r["round_times"]
        entry["agg_times"] = r["agg_times"]
        save_data["results"].append(entry)

    out_path = out_dir / "overhead_benchmark.json"
    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")

    # ---- Generate LaTeX table matching paper Table II ----
    print(f"\n\n  LaTeX table for paper (copy to IEEE-conference-template-062824.tex):")
    print(r"  \begin{tabular}{|l|r|r|r|r|}")
    print(r"  \hline")
    print(r"  \textbf{Strategy} & \textbf{Train/rnd (s)} & \textbf{Agg/rnd (s)} "
          r"& \textbf{Peak RSS (MB)} & \textbf{Acc.\ (\%)} \\")
    print(r"  \hline")
    for r in all_results:
        if r['defense'] == 'DT-Guard':
            print(f"  \\hline")
            print(f"  \\textbf{{{r['defense']}}} & \\textbf{{{r['train_per_round_s']:.2f}}} & "
                  f"\\textbf{{{r['agg_per_round_s']:.3f}}} & "
                  f"\\textbf{{{r['peak_mem_mb']:.0f}}} & "
                  f"\\textbf{{{r['accuracy']*100:.1f}}} \\\\")
        else:
            print(f"  {r['defense']:<15} & {r['train_per_round_s']:.2f} & "
                  f"{r['agg_per_round_s']:.3f} & "
                  f"{r['peak_mem_mb']:.0f} & "
                  f"{r['accuracy']*100:.1f} \\\\")
    print(r"  \hline")
    print(r"  \end{tabular}")

    # ---- DT-Guard breakdown for paper text ----
    if dtg:
        print(f"\n  Paper text values (for Computational Overhead paragraph):")
        print(f"    Train/rnd:        {dtg['train_per_round_s']:.2f} s")
        print(f"    DT-Verify/rnd:    {dtg['dt_verify_per_round_s']:.3f} s")
        print(f"    DT-PW/rnd:        {dtg['dt_pw_per_round_s']:.3f} s")
        print(f"    Total Agg/rnd:    {dtg['agg_per_round_s']:.3f} s")
        server_oh = dtg['dt_verify_per_round_s'] + dtg['dt_pw_per_round_s']
        pct = server_oh / dtg['per_round_s'] * 100
        print(f"    Server % of round: {pct:.1f}%")
        print(f"    Total session:    {dtg['total_time_s']:.1f} s")
        fedavg_total_s = fedavg_result['total_time_s'] if fedavg_result else 0
        print(f"    FedAvg session:   {fedavg_total_s:.1f} s")
        print(f"    Mem overhead:     {dtg['mem_overhead_mb']:.1f} MB")

    print(f"\n{'=' * 90}")
    print(f"  Done. Total benchmark time: {sum(r['total_time_s'] for r in all_results):.0f}s")
    print(f"{'=' * 90}")


if __name__ == "__main__":
    main()

