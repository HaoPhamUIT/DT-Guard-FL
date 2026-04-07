#!/usr/bin/env python3
"""
EXPERIMENT 5: CONTRIBUTION ASSESSMENT COMPARISON - ToN-IoT Dataset
=========================================================
Gap 3: Free-riders receive equal or HIGHER weight than honest clients
under existing aggregation strategies.

This mirrors experiments/thesis/run_experiment5_dtpw.py but uses ToN-IoT dataset.

Compares 5 contribution assessment strategies:
  1. DT-PW (Ours)     — DT-Driven Performance Weighting
  2. Shapley           — Monte-Carlo Shapley
  3. Trust-Score       — 1/(1+||w_i - w_global||) - REWARDS free-riders!
  4. Uniform           — Equal weights
  5. FedAvg            — No defense

Setup: 16 Normal + 4 Free-Riders (20 clients total). No attacks.
"""

import torch
import numpy as np
import time
import warnings
from datetime import datetime
from pathlib import Path
import json

warnings.filterwarnings('ignore')

from dtguard.config import Config
from dtguard.data import load_ton_iot_data, create_federated_dataset
from dtguard.models import IoTAttackNet, TabDDPMChallengeGenerator
from dtguard.models.ids_model import get_parameters, set_parameters, train_model, evaluate_model
from dtguard.security import DigitalTwinVerifier, CommitteeSelector
from dtguard.security import (dt_performance_weighting, combine_dtpw_verification,
                              classic_shapley_values)
from dtguard.fl.aggregation import weighted_federated_averaging
from dtguard.fl.baselines import federated_averaging

# =============================================================================
# Configuration (matching CICIoT2023 experiments)
# =============================================================================
NUM_CLIENTS        = 20
NUM_ROUNDS         = 20
LOCAL_EPOCHS       = 3
BATCH_SIZE         = 512
LR                 = 0.001
DIRICHLET          = 0.5
TABDDPM_EPOCHS     = 100
SEED               = 42

# Client role allocation (20 clients total)
NUM_FREE_RIDERS    = 4
NUM_NORMAL         = 16
FREE_RIDER_IDX   = list(range(NUM_CLIENTS - NUM_FREE_RIDERS, NUM_CLIENTS))
NORMAL_IDX       = list(range(0, NUM_NORMAL))

CLIENT_ROLES = {}
for i in NORMAL_IDX:     CLIENT_ROLES[i] = "Normal"
for i in FREE_RIDER_IDX: CLIENT_ROLES[i] = "FreeRider"

ROLE_COLORS = {"Normal": "blue", "FreeRider": "gray"}


def _local_train_or_freerider(model, global_weights, client_idx, X, y, device):
    """Train client model — or simulate free-rider behavior."""
    if client_idx in FREE_RIDER_IDX:
        # Free-rider: copy global + tiny noise
        noisy_w = []
        for w in global_weights:
            noise = np.random.normal(0, 0.0001, w.shape).astype(w.dtype)
            noisy_w.append(w + noise)
        return noisy_w
    else:
        set_parameters(model, global_weights)
        train_model(model, X, y, epochs=LOCAL_EPOCHS,
                    batch_size=BATCH_SIZE, lr=LR, device=device)
        return get_parameters(model)


# =============================================================================
# Strategy runners
# =============================================================================

def run_dtpw(X_clients, y_clients, X_test, y_test,
             input_dim, num_classes, device, verifier,
             challenge_gen=None):
    """DT-Guard + DT-Driven Performance Weighting (DT-PW)."""
    np.random.seed(SEED); torch.manual_seed(SEED)
    global_model = IoTAttackNet(input_dim, num_classes)
    client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(NUM_CLIENTS)]
    verifier.client_history = {}
    acc_history, score_history, weight_history = [], [], []

    for rnd in range(NUM_ROUNDS):
        gw = get_parameters(global_model)
        cw = [_local_train_or_freerider(client_models[i], gw, i,
              X_clients[i], y_clients[i], device) for i in range(NUM_CLIENTS)]

        verified_w, verified_idx, v_scores = [], [], []
        selector = CommitteeSelector(num_clients=NUM_CLIENTS, committee_size=1)
        seeds = selector.committee_seeds(rnd + 1)
        for i in range(NUM_CLIENTS):
            set_parameters(client_models[i], cw[i])
            sc_list, pass_list = [], []
            for seed in seeds:
                res = verifier.verify(client_models[i], device,
                                      global_model=global_model, client_id=i,
                                      challenge_seed=seed, round_num=rnd + 1,
                                      data_size=len(X_clients[i]))
                sc_list.append(res['score']); pass_list.append(res['passed'])
            if sum(pass_list) >= (len(pass_list) // 2 + 1):
                verified_w.append(cw[i]); verified_idx.append(i)
                v_scores.append(float(np.mean(sc_list)))

        round_weights, round_scores = np.zeros(NUM_CLIENTS), np.zeros(NUM_CLIENTS)
        if verified_w:
            vm = [client_models[i] for i in verified_idx]
            debug_mode = (rnd + 1) in [5, 10]
            pw = dt_performance_weighting(vm, verified_w, X_test, y_test, device,
                                          eval_subsample=5000,
                                          global_weights=gw,
                                          challenge_gen=challenge_gen,
                                          client_data_sizes=[len(X_clients[i]) for i in verified_idx],
                                          debug=debug_mode)
            aw = combine_dtpw_verification(pw, v_scores)
            for j, idx in enumerate(verified_idx):
                round_weights[idx] = aw[j]; round_scores[idx] = pw[j]
            aggregated = weighted_federated_averaging(verified_w, aw)
        else:
            aggregated, _ = federated_averaging(cw)

        score_history.append(round_scores); weight_history.append(round_weights)
        set_parameters(global_model, aggregated)
        acc_history.append(evaluate_model(global_model, X_test, y_test, device=device))

    return acc_history[-1], acc_history, score_history, weight_history


def run_trust_score(X_clients, y_clients, X_test, y_test,
                    input_dim, num_classes, device, verifier):
    """DT-Guard + Trust-Score weighting (LUP/PoC-style)."""
    np.random.seed(SEED); torch.manual_seed(SEED)
    global_model = IoTAttackNet(input_dim, num_classes)
    client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(NUM_CLIENTS)]
    verifier.client_history = {}
    acc_history, weight_history = [], []

    for rnd in range(NUM_ROUNDS):
        gw = get_parameters(global_model)
        cw = [_local_train_or_freerider(client_models[i], gw, i,
              X_clients[i], y_clients[i], device) for i in range(NUM_CLIENTS)]

        verified_w, verified_idx = [], []
        selector = CommitteeSelector(num_clients=NUM_CLIENTS, committee_size=1)
        seeds = selector.committee_seeds(rnd + 1)
        for i in range(NUM_CLIENTS):
            set_parameters(client_models[i], cw[i])
            pass_list = []
            for seed in seeds:
                res = verifier.verify(client_models[i], device,
                                      global_model=global_model, client_id=i,
                                      challenge_seed=seed, round_num=rnd + 1,
                                      data_size=len(X_clients[i]))
                pass_list.append(res['passed'])
            if sum(pass_list) >= (len(pass_list) // 2 + 1):
                verified_w.append(cw[i]); verified_idx.append(i)

        round_weights = np.zeros(NUM_CLIENTS)
        if verified_w:
            gw_flat = np.concatenate([g.flatten() for g in gw])
            trust = []
            for j, w in enumerate(verified_w):
                w_flat = np.concatenate([p.flatten() for p in w])
                dev = np.linalg.norm(w_flat - gw_flat)
                trust.append(1.0 / (1.0 + dev))
            tw_sum = sum(trust)
            trust = [t / tw_sum for t in trust]
            for j, idx in enumerate(verified_idx):
                round_weights[idx] = trust[j]
            aggregated = weighted_federated_averaging(verified_w, trust)
        else:
            aggregated, _ = federated_averaging(cw)

        weight_history.append(round_weights)
        set_parameters(global_model, aggregated)
        acc_history.append(evaluate_model(global_model, X_test, y_test, device=device))

    return acc_history[-1], acc_history, weight_history


def run_classic_shapley(X_clients, y_clients, X_test, y_test,
                        input_dim, num_classes, device, verifier):
    """DT-Guard + Classic Monte-Carlo Shapley weighting."""
    np.random.seed(SEED); torch.manual_seed(SEED)
    global_model = IoTAttackNet(input_dim, num_classes)
    client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(NUM_CLIENTS)]
    verifier.client_history = {}
    acc_history, score_history, weight_history = [], [], []

    for rnd in range(NUM_ROUNDS):
        gw = get_parameters(global_model)
        cw = [_local_train_or_freerider(client_models[i], gw, i,
              X_clients[i], y_clients[i], device) for i in range(NUM_CLIENTS)]

        verified_w, verified_idx, v_scores = [], [], []
        selector = CommitteeSelector(num_clients=NUM_CLIENTS, committee_size=1)
        seeds = selector.committee_seeds(rnd + 1)
        for i in range(NUM_CLIENTS):
            set_parameters(client_models[i], cw[i])
            sc_list, pass_list = [], []
            for seed in seeds:
                res = verifier.verify(client_models[i], device,
                                      global_model=global_model, client_id=i,
                                      challenge_seed=seed, round_num=rnd + 1,
                                      data_size=len(X_clients[i]))
                sc_list.append(res['score']); pass_list.append(res['passed'])
            if sum(pass_list) >= (len(pass_list) // 2 + 1):
                verified_w.append(cw[i]); verified_idx.append(i)
                v_scores.append(float(np.mean(sc_list)))

        round_weights, round_scores = np.zeros(NUM_CLIENTS), np.zeros(NUM_CLIENTS)
        if verified_w:
            vm = [client_models[i] for i in verified_idx]
            sv = classic_shapley_values(vm, verified_w, X_test, y_test, device,
                                        n_samples=20, eval_subsample=2000)
            aw = combine_dtpw_verification(sv, v_scores)
            for j, idx in enumerate(verified_idx):
                round_weights[idx] = aw[j]; round_scores[idx] = sv[j]
            aggregated = weighted_federated_averaging(verified_w, aw)
        else:
            aggregated, _ = federated_averaging(cw)

        score_history.append(round_scores); weight_history.append(round_weights)
        set_parameters(global_model, aggregated)
        acc_history.append(evaluate_model(global_model, X_test, y_test, device=device))

    return acc_history[-1], acc_history, score_history, weight_history


def run_uniform(X_clients, y_clients, X_test, y_test,
                input_dim, num_classes, device, verifier):
    """DT-Guard + Uniform weighting."""
    np.random.seed(SEED); torch.manual_seed(SEED)
    global_model = IoTAttackNet(input_dim, num_classes)
    client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(NUM_CLIENTS)]
    verifier.client_history = {}
    acc_history, weight_history = [], []

    for rnd in range(NUM_ROUNDS):
        gw = get_parameters(global_model)
        cw = [_local_train_or_freerider(client_models[i], gw, i,
              X_clients[i], y_clients[i], device) for i in range(NUM_CLIENTS)]

        verified_w, verified_idx_list = [], []
        selector = CommitteeSelector(num_clients=NUM_CLIENTS, committee_size=1)
        seeds = selector.committee_seeds(rnd + 1)
        for i in range(NUM_CLIENTS):
            set_parameters(client_models[i], cw[i])
            pass_list = []
            for seed in seeds:
                res = verifier.verify(client_models[i], device,
                                      global_model=global_model, client_id=i,
                                      challenge_seed=seed, round_num=rnd + 1,
                                      data_size=len(X_clients[i]))
                pass_list.append(res['passed'])
            if sum(pass_list) >= (len(pass_list) // 2 + 1):
                verified_w.append(cw[i]); verified_idx_list.append(i)

        round_weights = np.zeros(NUM_CLIENTS)
        if verified_w:
            uw = 1.0 / len(verified_w)
            for idx in verified_idx_list:
                round_weights[idx] = uw
            aggregated, _ = federated_averaging(verified_w)
        else:
            aggregated, _ = federated_averaging(cw)

        weight_history.append(round_weights)
        set_parameters(global_model, aggregated)
        acc_history.append(evaluate_model(global_model, X_test, y_test, device=device))

    return acc_history[-1], acc_history, weight_history


def run_fedavg(X_clients, y_clients, X_test, y_test,
               input_dim, num_classes, device):
    """Plain FedAvg — no defense, no weighting."""
    np.random.seed(SEED); torch.manual_seed(SEED)
    global_model = IoTAttackNet(input_dim, num_classes)
    client_models = [IoTAttackNet(input_dim, num_classes) for _ in range(NUM_CLIENTS)]
    acc_history, weight_history = [], []

    for rnd in range(NUM_ROUNDS):
        gw = get_parameters(global_model)
        cw = [_local_train_or_freerider(client_models[i], gw, i,
              X_clients[i], y_clients[i], device) for i in range(NUM_CLIENTS)]

        round_weights = np.ones(NUM_CLIENTS) / NUM_CLIENTS
        weight_history.append(round_weights)
        aggregated, _ = federated_averaging(cw)
        set_parameters(global_model, aggregated)
        acc_history.append(evaluate_model(global_model, X_test, y_test, device=device))

    return acc_history[-1], acc_history, weight_history


# =============================================================================
# Main
# =============================================================================
def main():
    start = datetime.now()
    print("=" * 100)
    print("  EXPERIMENT 5: CONTRIBUTION ASSESSMENT COMPARISON - ToN-IoT Dataset")
    print("  DT-PW vs Shapley vs Trust-Score vs Uniform vs FedAvg")
    print("=" * 100)
    print(f"  Setup: {NUM_CLIENTS} clients, {NUM_ROUNDS} rounds")
    print(f"  Roles: {NUM_NORMAL} normal, {NUM_FREE_RIDERS} free-riders\n")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Load ToN-IoT data
    cfg = Config()
    train_df, test_df, feature_cols = load_ton_iot_data(
        data_dir="data/ToN-IoT_Data",
        random_seed=SEED
    )
    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df['Label'].values.astype(np.int64)
    input_dim = len(feature_cols)
    num_classes = len(np.unique(y_test))

    np.random.seed(SEED)
    split_cfg = Config(num_clients=NUM_CLIENTS, dirichlet_alpha=DIRICHLET)
    X_clients, y_clients = create_federated_dataset(
        train_df, feature_cols, split_cfg, verbose=False,
        max_samples_per_client=10_000)

    # Show client characteristics
    print("  Client data characteristics:")
    print(f"    {'ID':<6} {'Role':<12} {'Samples':<9} {'Classes':<9} {'Description'}")
    print(f"    {'-'*65}")
    role_desc = {
        "Normal": "Standard Non-IID data",
        "FreeRider": "Echo global + noise (0 work) ✗",
    }
    for i in range(NUM_CLIENTS):
        role = CLIENT_ROLES[i]
        n_cls = len(np.unique(y_clients[i]))
        desc = role_desc[role]
        print(f"    {i:<6} {role:<12} {len(X_clients[i]):<9} {n_cls:<9} {desc}")

    # Train TabDDPM for DT-Guard
    print("\n  Training TabDDPM for DT-Guard...", end=" ", flush=True)
    t0 = time.time()
    tabddpm_gen = TabDDPMChallengeGenerator(
        input_dim=input_dim, n_classes=num_classes,
        T=200, d_hidden=256, n_epochs=TABDDPM_EPOCHS, batch_size=512)
    train_idx = NORMAL_IDX
    X_benign = np.vstack([X_clients[i] for i in train_idx])
    y_benign = np.concatenate([y_clients[i] for i in train_idx])
    if len(X_benign) > 15000:
        idx = np.random.choice(len(X_benign), 15000, replace=False)
        X_benign, y_benign = X_benign[idx], y_benign[idx]
    tabddpm_gen.train_gan(X_benign, y_benign, device=device)
    verifier = DigitalTwinVerifier(tabddpm_gen, threshold=0.65, challenge_samples=100)
    print(f"done ({time.time()-t0:.1f}s)\n")

    scenarios = [("No Attack", None)]

    # =========================================================================
    # TABLE A: Accuracy — Aggregation Strategy Comparison
    # =========================================================================
    print("=" * 100)
    print("  TABLE A: ACCURACY — AGGREGATION STRATEGY COMPARISON - ToN-IoT")
    print("=" * 100)

    strategies = ["DT-PW (Ours)", "Shapley", "Trust-Score (LUP)",
                  "Uniform", "FedAvg"]
    all_results = {}

    for scn_name, _ in scenarios:
        print(f"\n  Running scenario: {scn_name}")

        t0 = time.time()
        acc_pw, hist_pw, score_pw, w_pw = run_dtpw(
            X_clients, y_clients, X_test, y_test,
            input_dim, num_classes, device, verifier,
            challenge_gen=tabddpm_gen)
        print(f"    DT-PW:       {acc_pw*100:.2f}%  ({time.time()-t0:.0f}s)")
        all_results.setdefault("DT-PW (Ours)", {})[scn_name] = {
            'acc': acc_pw, 'hist': hist_pw, 'scores': score_pw, 'weights': w_pw}

        t0 = time.time()
        acc_sv, hist_sv, score_sv, w_sv = run_classic_shapley(
            X_clients, y_clients, X_test, y_test,
            input_dim, num_classes, device, verifier)
        print(f"    Shapley:     {acc_sv*100:.2f}%  ({time.time()-t0:.0f}s)")
        all_results.setdefault("Shapley", {})[scn_name] = {
            'acc': acc_sv, 'hist': hist_sv, 'scores': score_sv, 'weights': w_sv}

        t0 = time.time()
        acc_ts, hist_ts, w_ts = run_trust_score(
            X_clients, y_clients, X_test, y_test,
            input_dim, num_classes, device, verifier)
        print(f"    Trust-Score: {acc_ts*100:.2f}%  ({time.time()-t0:.0f}s)")
        all_results.setdefault("Trust-Score (LUP)", {})[scn_name] = {
            'acc': acc_ts, 'hist': hist_ts, 'weights': w_ts}

        t0 = time.time()
        acc_uni, hist_uni, w_uni = run_uniform(
            X_clients, y_clients, X_test, y_test,
            input_dim, num_classes, device, verifier)
        print(f"    Uniform:     {acc_uni*100:.2f}%  ({time.time()-t0:.0f}s)")
        all_results.setdefault("Uniform", {})[scn_name] = {
            'acc': acc_uni, 'hist': hist_uni, 'weights': w_uni}

        t0 = time.time()
        acc_fa, hist_fa, w_fa = run_fedavg(
            X_clients, y_clients, X_test, y_test,
            input_dim, num_classes, device)
        print(f"    FedAvg:      {acc_fa*100:.2f}%  ({time.time()-t0:.0f}s)")
        all_results.setdefault("FedAvg", {})[scn_name] = {
            'acc': acc_fa, 'hist': hist_fa, 'weights': w_fa}

    # Print accuracy table
    print(f"\n  {'Strategy':<30}", end="")
    for scn_name, _ in scenarios:
        print(f"  {scn_name:>14}", end="")
    print()
    print("  " + "-" * 60)
    for strat in strategies:
        row = f"  {strat:<30}"
        for scn_name, _ in scenarios:
            acc = all_results[strat][scn_name]['acc']
            row += f"  {acc*100:>13.2f}%"
        print(row)

    # =========================================================================
    # TABLE B: Per-Client Weight Assignment (THE KEY TABLE FOR GAP 3)
    # =========================================================================
    print("\n" + "=" * 120)
    print("  TABLE B: PER-CLIENT WEIGHT ASSIGNMENT — No Attack scenario - ToN-IoT")
    print("  ★ KEY: DT-PW suppresses free-riders via effort gating")
    print("=" * 120)

    scn = "No Attack"
    last_n = 5

    pw_weights = np.mean(all_results["DT-PW (Ours)"][scn]['weights'][-last_n:], axis=0)
    sv_weights = np.mean(all_results["Shapley"][scn]['weights'][-last_n:], axis=0)
    ts_weights = np.mean(all_results["Trust-Score (LUP)"][scn]['weights'][-last_n:], axis=0)
    uni_weights = np.mean(all_results["Uniform"][scn]['weights'][-last_n:], axis=0)

    print(f"\n  {'ID':<5} {'Role':<12} {'Samples':<8} "
          f"{'DT-PW':>8} {'Shapley':>9} {'TrustScr':>9} {'Uniform':>8}  {'Analysis'}")
    print(f"  {'-'*100}")

    for i in range(NUM_CLIENTS):
        role = CLIENT_ROLES[i]
        pw, sv, tw, uw = pw_weights[i], sv_weights[i], ts_weights[i], uni_weights[i]

        if role == "FreeRider":
            if pw < uw * 0.5:
                analysis = "✓ DT-PW suppresses"
            else:
                analysis = "— not suppressed"
            if tw > pw:
                analysis += " | ⚠ Trust rewards!"
            if sv > pw:
                analysis += " | Shapley > DT-PW"
        else:
            analysis = ""

        print(f"  {i:<5} {role:<12} {len(X_clients[i]):<8} "
              f"{pw:>7.4f}  {sv:>8.4f}  {tw:>8.4f}  {uw:>7.4f}  {analysis}")

    # Summary by role
    print(f"\n  Average weight by role:")
    print(f"  {'Role':<14} {'DT-PW':>8} {'Shapley':>9} {'TrustScr':>9} {'Uniform':>8}")
    print(f"  {'-'*52}")
    for role_name in ["Normal", "FreeRider"]:
        idx_list = [i for i, r in CLIENT_ROLES.items() if r == role_name]
        if not idx_list: continue
        pw_avg = np.mean([pw_weights[i] for i in idx_list])
        sv_avg = np.mean([sv_weights[i] for i in idx_list])
        tw_avg = np.mean([ts_weights[i] for i in idx_list])
        uw_avg = np.mean([uni_weights[i] for i in idx_list])
        print(f"  {role_name:<14} {pw_avg:>7.4f}  {sv_avg:>8.4f}  {tw_avg:>8.4f}  {uw_avg:>7.4f}")

    # =========================================================================
    # Save results
    # =========================================================================
    results_dir = Path('results/ton_iot')
    results_dir.mkdir(parents=True, exist_ok=True)

    save_data = {
        'accuracy': {},
        'accuracy_history': {},
        'score_history': {},
        'weight_history': {},
        'config': {
            'dataset': 'ToN-IoT',
            'num_clients': NUM_CLIENTS,
            'num_rounds': NUM_ROUNDS,
            'roles': {str(k): v for k, v in CLIENT_ROLES.items()},
            'normal_idx': NORMAL_IDX,
            'free_rider_idx': FREE_RIDER_IDX,
            'client_sizes': [len(X_clients[i]) for i in range(NUM_CLIENTS)],
        },
    }
    for strat, scns in all_results.items():
        save_data['accuracy'][strat] = {}
        save_data['accuracy_history'][strat] = {}
        save_data['weight_history'][strat] = {}
        for scn_name, data in scns.items():
            save_data['accuracy'][strat][scn_name] = float(data['acc'])
            save_data['accuracy_history'][strat][scn_name] = [
                float(h) for h in data['hist']]
            save_data['weight_history'][strat][scn_name] = [
                w.tolist() for w in data['weights']]
            if 'scores' in data:
                save_data['score_history'].setdefault(strat, {})[scn_name] = [
                    h.tolist() for h in data['scores']]

    with open(results_dir / 'exp5_dtpw_toniot.json', 'w') as f:
        json.dump(save_data, f, indent=2)
    print(f"\n  Results saved to {results_dir / 'exp5_dtpw_toniot.json'}")

    elapsed = datetime.now() - start
    print(f"\n  ✅ Experiment 5 (ToN-IoT) done in {elapsed}")


if __name__ == "__main__":
    main()
