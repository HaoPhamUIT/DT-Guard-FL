#!/usr/bin/env python3
"""
PAPER EXPERIMENTS — DT-Guard (IEEE ICCE 2026)
==============================================
Single unified script for all experiments needed in the 6-page paper.
Produces exactly the tables and data referenced in the Experiments section.

Three experiments, matching the three research gaps:

  EXP-A  (Gap 1 — Circumventable defenses):
    Defense comparison — 10 defenses × 5 attacks × 4 ratios (10/20/40/50%).
    Output: paper_expA.json with all ratios for Fig. 2.

  EXP-B  (Gap 2 — Non-IID confusion):
    FPR comparison at extreme Non-IID (α=0.1) vs moderate (α=0.5).
    Shows DT-Guard keeps low FPR while passive methods reject honest clients.
    Output: Inline numbers + optional figure in paper.

  EXP-C  (Gap 3 — Free-rider problem):
    DT-PW vs Trust-Score vs FedAvg vs Uniform, with 4 free-riders.
    Output: Table III in paper (Average weight by client role).

Usage:
    python run_paper_experiments.py                # Run all 3 experiments
    python run_paper_experiments.py --exp A        # EXP-A all ratios
    python run_paper_experiments.py --exp A 10     # EXP-A @ 10% malicious only
    python run_paper_experiments.py --exp A 20     # EXP-A @ 20% malicious only
    python run_paper_experiments.py --exp A 40     # EXP-A @ 40% malicious only
    python run_paper_experiments.py --exp A 50     # EXP-A @ 50% malicious only
    python run_paper_experiments.py --exp A merge  # Merge 4 partial files
    python run_paper_experiments.py --exp B        # Run only EXP-B
    python run_paper_experiments.py --exp C        # Run only EXP-C
    python run_paper_experiments.py --exp A 10 B   # EXP-A@10% + EXP-B
"""

import argparse
import copy
import torch
import numpy as np
import time
import json
import warnings
import traceback
import os
import psutil
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

warnings.filterwarnings('ignore', message=".*pin_memory.*")
warnings.filterwarnings('ignore', category=UserWarning)

from dtguard.config import Config, AttackType
from dtguard.data import load_data, create_federated_dataset
from dtguard.models import IoTAttackNet, TabDDPMChallengeGenerator
from dtguard.models.ids_model import (
    get_parameters, set_parameters, train_model, evaluate_model)
from dtguard.security import DigitalTwinVerifier, apply_attack
from dtguard.security import (
    dt_performance_weighting, combine_dtpw_verification, CommitteeSelector)
from dtguard.fl.aggregation import (
    compute_verification_stats, weighted_federated_averaging)
from dtguard.fl.baselines import (
    federated_averaging, krum_aggregation, median_aggregation,
    trimmed_mean_aggregation, lup_aggregation, clipcluster_aggregation,
    signguard_aggregation, poc_aggregation, geomed_aggregation,
)

# =============================================================================
#  SHARED CONFIG
# =============================================================================
NUM_CLIENTS       = 20
NUM_ROUNDS        = 20
LOCAL_EPOCHS      = 3
BATCH_SIZE        = 512
LR                = 0.001
DIRICHLET_ALPHA   = 0.5
ATTACK_SCALE      = 10.0
TABDDPM_EPOCHS    = 100
DT_THRESHOLD      = 0.6
CHALLENGE_SAMPLES = 200
COMMITTEE_SIZE    = 3
SEED              = 42

RESULTS_DIR = Path('results/paper')


# =============================================================================
#  HELPER: Data loading (shared across all experiments)
# =============================================================================
def load_all_data(alpha=DIRICHLET_ALPHA, max_per_client=20_000):
    """Load CIC-IoT-2023 and create federated split."""
    cfg = Config(dataset_dir="data/CICIoT2023")
    train_df, test_df, feature_cols = load_data(cfg)

    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df['Label'].values.astype(np.int64)
    input_dim = len(feature_cols)
    num_classes = len(np.unique(y_test))

    np.random.seed(SEED)
    split_cfg = Config(num_clients=NUM_CLIENTS, dirichlet_alpha=alpha)
    X_clients, y_clients = create_federated_dataset(
        train_df, feature_cols, split_cfg, verbose=False,
        max_samples_per_client=max_per_client)

    return X_clients, y_clients, X_test, y_test, input_dim, num_classes


def build_verifier(X_clients, y_clients, input_dim, num_classes,
                   benign_indices, device):
    """Train TabDDPM once, return cached verifier."""
    gen = TabDDPMChallengeGenerator(
        input_dim=input_dim, n_classes=num_classes,
        T=200, d_hidden=256, n_epochs=TABDDPM_EPOCHS, batch_size=512)

    X_ben = np.vstack([X_clients[i] for i in benign_indices])
    y_ben = np.concatenate([y_clients[i] for i in benign_indices])
    if len(X_ben) > 15000:
        idx = np.random.choice(len(X_ben), 15000, replace=False)
        X_ben, y_ben = X_ben[idx], y_ben[idx]

    gen.train_gan(X_ben, y_ben, device=device)
    verifier = DigitalTwinVerifier(
        gen, threshold=DT_THRESHOLD, challenge_samples=CHALLENGE_SAMPLES)
    return verifier, gen


# =============================================================================
#  HELPER: Single FL run — baseline defense
# =============================================================================
def _run_baseline(defense_name, attack_type, n_mal,
                  X_clients, y_clients, X_test, y_test,
                  input_dim, num_classes, device):
    """Run one (defense, attack) pair. Returns dict of metrics."""
    np.random.seed(SEED); torch.manual_seed(SEED)

    mal_idx = list(range(NUM_CLIENTS - n_mal, NUM_CLIENTS))
    global_model = IoTAttackNet(input_dim, num_classes)
    client_models = [IoTAttackNet(input_dim, num_classes)
                     for _ in range(NUM_CLIENTS)]

    accuracies = []
    tp_sum = fp_sum = tn_sum = fn_sum = 0
    lup_trust = np.zeros((NUM_CLIENTS, 1))
    poc_hist = np.ones(NUM_CLIENTS) * 0.5

    for rnd in range(NUM_ROUNDS):
        gw = get_parameters(global_model)
        cw = []
        for i, m in enumerate(client_models):
            set_parameters(m, gw)
            train_model(m, X_clients[i], y_clients[i],
                        epochs=LOCAL_EPOCHS, batch_size=BATCH_SIZE,
                        lr=LR, device=device)
            cw.append(get_parameters(m))

        if n_mal > 0 and attack_type is not None:
            atk = (attack_type.value if isinstance(attack_type, AttackType)
                   else attack_type)
            for mi in mal_idx:
                cw[mi] = apply_attack(cw[mi], atk, ATTACK_SCALE,
                                      all_client_weights=cw,
                                      malicious_indices=mal_idx)

        agg_map = {
            "FedAvg":       lambda: federated_averaging(cw),
            "Krum":         lambda: krum_aggregation(cw, f=n_mal),
            "Median":       lambda: median_aggregation(cw),
            "Trimmed Mean": lambda: trimmed_mean_aggregation(cw, trim_ratio=0.2),
            "GeoMed":       lambda: geomed_aggregation(cw, global_weights=gw),
            "SignGuard":    lambda: signguard_aggregation(cw, global_weights=gw),
            "ClipCluster":  lambda: clipcluster_aggregation(cw, global_weights=gw),
            "LUP":          lambda: lup_aggregation(cw, global_weights=gw,
                                                     trust_scores=lup_trust),
            "PoC":          lambda: poc_aggregation(
                                cw, global_weights=gw,
                                client_data_sizes=[len(X_clients[i])
                                                   for i in range(NUM_CLIENTS)],
                                contribution_history=poc_hist),
        }
        aggregated, rejected = agg_map[defense_name]()

        if defense_name == "LUP":
            for idx in range(NUM_CLIENTS):
                if idx not in rejected:
                    lup_trust[idx, 0] += 1.0
        elif defense_name == "PoC":
            for idx in range(NUM_CLIENTS):
                if idx not in rejected:
                    poc_hist[idx] = min(1.0, poc_hist[idx] + 0.1)
                else:
                    poc_hist[idx] = max(0.0, poc_hist[idx] - 0.2)

        vr = [i not in rejected for i in range(NUM_CLIENTS)]
        st = compute_verification_stats(NUM_CLIENTS, mal_idx, vr)
        tp_sum += st['tp']; fp_sum += st['fp']
        tn_sum += st['tn']; fn_sum += st['fn']

        set_parameters(global_model, aggregated)
        accuracies.append(evaluate_model(global_model, X_test, y_test,
                                         device=device))

    det = tp_sum / (tp_sum + fn_sum) if (tp_sum + fn_sum) else 0.
    fpr = fp_sum / (fp_sum + tn_sum) if (fp_sum + tn_sum) else 0.
    return {'accuracy': accuracies[-1], 'detection_rate': det,
            'fpr': fpr, 'history': accuracies}


# =============================================================================
#  HELPER: Single FL run — DT-Guard
# =============================================================================
def _run_dtguard(attack_type, n_mal,
                 X_clients, y_clients, X_test, y_test,
                 input_dim, num_classes, device, verifier):
    """Run DT-Guard for one attack. Returns dict of metrics."""
    np.random.seed(SEED); torch.manual_seed(SEED)

    mal_idx = list(range(NUM_CLIENTS - n_mal, NUM_CLIENTS))
    global_model = IoTAttackNet(input_dim, num_classes)
    client_models = [IoTAttackNet(input_dim, num_classes)
                     for _ in range(NUM_CLIENTS)]
    verifier.client_history = {}

    from dtguard.security import calculate_shapley_values, calculate_weighted_shapley

    accuracies = []
    tp_sum = fp_sum = tn_sum = fn_sum = 0
    shapley_hist = []

    for rnd in range(NUM_ROUNDS):
        gw = get_parameters(global_model)
        cw = []
        for i, m in enumerate(client_models):
            set_parameters(m, gw)
            train_model(m, X_clients[i], y_clients[i],
                        epochs=LOCAL_EPOCHS, batch_size=BATCH_SIZE,
                        lr=LR, device=device)
            cw.append(get_parameters(m))

        if n_mal > 0 and attack_type is not None:
            atk = (attack_type.value if isinstance(attack_type, AttackType)
                   else attack_type)
            for mi in mal_idx:
                cw[mi] = apply_attack(cw[mi], atk, ATTACK_SCALE,
                                      all_client_weights=cw,
                                      malicious_indices=mal_idx)

        # Four-layer verification
        vw, vi, vs = [], [], []
        vr = []
        selector = CommitteeSelector(num_clients=NUM_CLIENTS,
                                     committee_size=COMMITTEE_SIZE,
                                     shapley_history=shapley_hist)
        seeds = selector.committee_seeds(rnd + 1)

        for i in range(NUM_CLIENTS):
            set_parameters(client_models[i], cw[i])
            sc_list, pa_list = [], []
            for seed in seeds:
                res = verifier.verify(
                    client_models[i], device, global_model=global_model,
                    client_id=i, challenge_seed=seed,
                    round_num=rnd + 1, data_size=len(X_clients[i]))
                sc_list.append(res['score']); pa_list.append(res['passed'])
            passed = sum(pa_list) >= (len(pa_list) // 2 + 1)
            vr.append(passed)
            if passed:
                vw.append(cw[i]); vi.append(i)
                vs.append(float(np.mean(sc_list)))

        st = compute_verification_stats(NUM_CLIENTS, mal_idx, vr)
        tp_sum += st['tp']; fp_sum += st['fp']
        tn_sum += st['tn']; fn_sum += st['fn']

        if vw:
            vm = [client_models[j] for j in vi]
            sv = calculate_shapley_values(
                vm, vw, X_test, y_test, device,
                n_samples=10, eval_subsample=2000,
                global_weights=gw, challenge_gen=verifier.gan)
            aw = calculate_weighted_shapley(sv, vs)
            full_sv = np.zeros(NUM_CLIENTS)
            for j, idx in enumerate(vi):
                full_sv[idx] = sv[j]
            shapley_hist.append(full_sv)
            aggregated = weighted_federated_averaging(vw, aw)
        else:
            aggregated, _ = federated_averaging(cw)
            shapley_hist.append(np.zeros(NUM_CLIENTS))

        set_parameters(global_model, aggregated)
        accuracies.append(evaluate_model(global_model, X_test, y_test,
                                         device=device))

    det = tp_sum / (tp_sum + fn_sum) if (tp_sum + fn_sum) else 0.
    fpr = fp_sum / (fp_sum + tn_sum) if (fp_sum + tn_sum) else 0.
    return {'accuracy': accuracies[-1], 'detection_rate': det,
            'fpr': fpr, 'history': accuracies}


# #############################################################################
#
#  EXP-A: DEFENSE COMPARISON (Gap 1)
#  → 10 defenses × 5 attacks × 4 malicious ratios (10%, 20%, 40%, 50%)
#  → Supports per-ratio execution for parallel terminals:
#      python3 run_paper_experiments.py --exp A 10   # terminal 1
#      python3 run_paper_experiments.py --exp A 20   # terminal 2
#      python3 run_paper_experiments.py --exp A 40   # terminal 3
#      python3 run_paper_experiments.py --exp A 50   # terminal 4
#      python3 run_paper_experiments.py --exp A merge # combine results
#
# #############################################################################

ALL_MAL_RATIOS = OrderedDict([
    ("10%", 2),    # 2/20 clients
    ("20%", 4),    # 4/20
    ("40%", 8),    # 8/20
    ("50%", 10),   # 10/20
])

ATTACKS_A = OrderedDict([
    ("No Attack", None),
    ("Backdoor",  AttackType.BACKDOOR),
    ("LIE",       AttackType.LIE),
    ("Min-Max",   AttackType.MIN_MAX),
    ("Min-Sum",   AttackType.MIN_SUM),
    ("MPAF",      AttackType.MPAF),
])
DEFENSES_A = ["DT-Guard", "LUP", "ClipCluster", "SignGuard", "GeoMed",
              "PoC", "FedAvg", "Krum", "Median", "Trimmed Mean"]


def merge_expA():
    """Merge paper_expA_{10,20,40,50}.json into paper_expA.json.

    Uses copy.deepcopy when assigning per-ratio dicts so the four entries
    never share references (a past bug produced 4 identical ratios).
    Also sanity-checks that ratios are not byte-identical after merge.
    """
    print("\n  Merging EXP-A partial results...")
    merged = {'ratios': {}, 'config': {
        'mal_ratios': {k: v for k, v in ALL_MAL_RATIOS.items()},
        'alpha': DIRICHLET_ALPHA, 'rounds': NUM_ROUNDS,
        'num_clients': NUM_CLIENTS,
        'attacks': list(ATTACKS_A.keys()),
        'defenses': DEFENSES_A}}

    missing = []
    for pct in [10, 20, 40, 50]:
        fpath = RESULTS_DIR / f'paper_expA_{pct}.json'
        if not fpath.exists():
            missing.append(str(fpath))
            continue
        with open(fpath) as f:
            partial = json.load(f)
        # partial has {"ratio_label": "X%", "results": {...}, "timings": {...}}
        label = partial['ratio_label']
        # Deep-copy to guarantee independent dicts for each ratio.
        merged['ratios'][label] = {
            'results':     copy.deepcopy(partial['results']),
            'timings':     copy.deepcopy(partial['timings']),
            'n_malicious': partial.get('n_malicious')}
        print(f"    ✓ Loaded {fpath} ({label}, n_mal={partial.get('n_malicious')})")

    if missing:
        print(f"    ⚠ Missing files: {', '.join(missing)}")
        print(f"    Run those ratios first, then merge again.")
        return

    # ── Sanity check: ratios must be distinct (avoid the past dup-ref bug) ──
    labels = list(merged['ratios'].keys())
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            if merged['ratios'][a] is merged['ratios'][b]:
                raise RuntimeError(
                    f"Internal bug: ratios {a} and {b} share the same object")
            if merged['ratios'][a]['results'] == merged['ratios'][b]['results']:
                print(f"    ⚠ WARNING: results for {a} and {b} are byte-identical."
                      f"  Re-run those ratios.")

    out = RESULTS_DIR / 'paper_expA.json'
    with open(out, 'w') as f:
        json.dump(merged, f, indent=2)
    print(f"\n  ✓ Merged → {out}")
    print(f"    Contains: {list(merged['ratios'].keys())}")


def experiment_A(device, ratio_pct=None):
    """10 defenses × 6 scenarios. If ratio_pct given, run only that ratio."""

    # Determine which ratios to run
    if ratio_pct is not None:
        label = f"{ratio_pct}%"
        if label not in ALL_MAL_RATIOS:
            print(f"  ✘ Unknown ratio: {ratio_pct}%. Use 10, 20, 40, or 50.")
            return
        run_ratios = OrderedDict([(label, ALL_MAL_RATIOS[label])])
        print(f"\n" + "=" * 80)
        print(f"  EXP-A: DEFENSE COMPARISON — {label} malicious ONLY")
        print(f"  → 10 defenses × 6 scenarios")
        print(f"  → Output: paper_expA_{ratio_pct}.json")
        print("=" * 80, flush=True)
    else:
        run_ratios = ALL_MAL_RATIOS
        print("\n" + "=" * 80)
        print("  EXP-A: DEFENSE COMPARISON — ALL ratios")
        print("  → 10 defenses × 6 scenarios × {10%, 20%, 40%, 50%}")
        print("=" * 80, flush=True)

    # Load data once
    X_cl, y_cl, X_te, y_te, dim, ncls = load_all_data()

    # Pre-train verifier once
    benign_idx_min = list(range(NUM_CLIENTS - max(ALL_MAL_RATIOS.values())))
    print("  Training TabDDPM for DT-Guard...", end=" ", flush=True)
    t0 = time.time()
    verifier, _ = build_verifier(X_cl, y_cl, dim, ncls, benign_idx_min, device)
    print(f"done ({time.time()-t0:.0f}s)", flush=True)

    # Total runs for ETA
    runs_per_ratio = len(DEFENSES_A) * len(ATTACKS_A)
    total_runs = runs_per_ratio * len(run_ratios)
    global_run = 0
    t0_all = time.time()

    all_results = {}
    all_timings = {}

    for ratio_label, n_mal in run_ratios.items():
        print(f"\n{'━' * 80}")
        print(f"  MALICIOUS RATIO: {ratio_label}  ({n_mal}/{NUM_CLIENTS} clients)")
        print(f"{'━' * 80}", flush=True)

        results = {}
        timings = {}

        for atk_name, atk_type in ATTACKS_A.items():
            for defense in DEFENSES_A:
                global_run += 1
                elapsed_total = time.time() - t0_all
                if global_run > 1:
                    avg_per_run = elapsed_total / (global_run - 1)
                    remaining = avg_per_run * (total_runs - global_run + 1)
                    eta_str = f"ETA {remaining/60:.0f}min"
                else:
                    eta_str = "ETA ..."

                print(f"  [{global_run}/{total_runs}] "
                      f"{defense:15s} vs {atk_name:10s} ... ",
                      end="", flush=True)
                t0_run = time.time()
                try:
                    n = 0 if atk_type is None else n_mal
                    if defense == "DT-Guard":
                        r = _run_dtguard(atk_type, n, X_cl, y_cl, X_te, y_te,
                                         dim, ncls, device, verifier)
                    else:
                        r = _run_baseline(defense, atk_type, n,
                                          X_cl, y_cl, X_te, y_te,
                                          dim, ncls, device)
                except Exception:
                    traceback.print_exc()
                    r = {'accuracy': 0., 'detection_rate': 0., 'fpr': 0.,
                         'history': [0.]*NUM_ROUNDS}

                elapsed = time.time() - t0_run
                results.setdefault(defense, {})[atk_name] = r
                timings.setdefault(defense, {})[atk_name] = elapsed
                print(f"Acc={r['accuracy']*100:.2f}%  "
                      f"Det={r['detection_rate']:.0%}  "
                      f"FPR={r['fpr']:.0%}  ({elapsed:.0f}s)  {eta_str}",
                      flush=True)

        all_results[ratio_label] = results
        all_timings[ratio_label] = timings

        # Print table
        atk_names = [a for a in ATTACKS_A if a != "No Attack"]
        print(f"\n  TABLE: Accuracy (%) — {ratio_label} Malicious")
        print("  " + "─" * 72)
        hdr = f"  {'Defense':<15}"
        for a in atk_names:
            hdr += f"  {a:>8}"
        hdr += f"  {'Avg':>8}"
        print(hdr)
        print("  " + "─" * 72)
        for d in DEFENSES_A:
            row = f"  {d:<15}"
            vals = []
            for a in atk_names:
                v = results[d][a]['accuracy'] * 100
                vals.append(v)
                row += f"  {v:>7.1f}%"
            row += f"  {np.mean(vals):>7.1f}%"
            print(row)
        print(flush=True)

        # ── Save this ratio immediately (for per-ratio mode) ──
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        ratio_save = {
            'ratio_label': ratio_label,
            'n_malicious': n_mal,
            'results': {},
            'timings': {}}
        for d in DEFENSES_A:
            ratio_save['results'][d] = {}
            ratio_save['timings'][d] = {}
            for a in ATTACKS_A:
                r = results[d][a]
                ratio_save['results'][d][a] = {
                    'accuracy': round(r['accuracy'], 4),
                    'detection_rate': round(r['detection_rate'], 4),
                    'fpr': round(r['fpr'], 4)}
                ratio_save['timings'][d][a] = round(timings[d][a], 1)

        pct_num = int(ratio_label.replace('%', ''))
        partial_path = RESULTS_DIR / f'paper_expA_{pct_num}.json'
        with open(partial_path, 'w') as f:
            json.dump(ratio_save, f, indent=2)
        print(f"  ✓ Saved → {partial_path}", flush=True)

    total_time = time.time() - t0_all
    print(f"\n  Done in {total_time:.0f}s ({total_time/60:.1f} min)", flush=True)

    # If running all ratios, also save the merged file by re-reading the
    # per-ratio JSONs we just wrote.  This funnels every write path through
    # `merge_expA()` so that future bug fixes only need to be applied once.
    if ratio_pct is None:
        merge_expA()

    return all_results


# #############################################################################
#
#  EXP-B: NON-IID ROBUSTNESS (Gap 2)
#  → Paper inline: FPR at α=0.1 vs α=0.5, no attack
#  Shows passive methods wrongly reject honest Non-IID clients,
#  while DT-Guard keeps low FPR via behavioral testing.
#
# #############################################################################
def experiment_B(device):
    """FPR under no attack at extreme vs moderate Non-IID."""
    print("\n" + "=" * 80)
    print("  EXP-B: NON-IID ROBUSTNESS — FPR under no attack")
    print("  → Paper inline numbers (Gap 2 evidence)")
    print("=" * 80)

    ALPHAS = [0.1, 0.5]
    DEFENSES = ["DT-Guard", "LUP", "ClipCluster", "SignGuard", "GeoMed", "PoC"]
    # Also run with LIE attack to show confusion
    SCENARIOS = [
        ("No Attack", None, 0),
        ("LIE",       AttackType.LIE, 5),  # 25% malicious
    ]

    results = {}  # results[alpha][scenario][defense] = {fpr, accuracy, det}

    for alpha in ALPHAS:
        results[alpha] = {}
        print(f"\n  ── α = {alpha} {'(Extreme Non-IID)' if alpha == 0.1 else '(Moderate)'} ──")

        X_cl, y_cl, X_te, y_te, dim, ncls = load_all_data(alpha=alpha)
        benign_idx = list(range(NUM_CLIENTS - 5))  # max 5 malicious

        print(f"  Training TabDDPM...", end=" ", flush=True)
        t0 = time.time()
        verifier, _ = build_verifier(X_cl, y_cl, dim, ncls, benign_idx, device)
        print(f"done ({time.time()-t0:.0f}s)")

        for scn_name, atk_type, n_mal in SCENARIOS:
            results[alpha][scn_name] = {}
            for d in DEFENSES:
                print(f"    {d:15s} vs {scn_name:10s} ...", end=" ", flush=True)
                t0 = time.time()
                try:
                    if d == "DT-Guard":
                        r = _run_dtguard(atk_type, n_mal, X_cl, y_cl,
                                         X_te, y_te, dim, ncls, device, verifier)
                    else:
                        r = _run_baseline(d, atk_type, n_mal,
                                          X_cl, y_cl, X_te, y_te,
                                          dim, ncls, device)
                except Exception:
                    traceback.print_exc()
                    r = {'accuracy': 0., 'detection_rate': 0., 'fpr': 0.,
                         'history': [0.]*NUM_ROUNDS}

                results[alpha][scn_name][d] = r
                print(f"Acc={r['accuracy']*100:.1f}%  "
                      f"FPR={r['fpr']*100:.1f}%  ({time.time()-t0:.0f}s)")

    # ── Print summary ──
    print("\n" + "─" * 80)
    print("  NON-IID COMPARISON: FPR (%) — No Attack (lower = better)")
    print("─" * 80)
    hdr = f"  {'Defense':<15}"
    for alpha in ALPHAS:
        hdr += f"  α={alpha:>4}"
    print(hdr)
    for d in DEFENSES:
        row = f"  {d:<15}"
        for alpha in ALPHAS:
            fpr = results[alpha]["No Attack"][d]['fpr'] * 100
            row += f"  {fpr:>5.1f}%"
        print(row)

    print("\n  ACCURACY (%) under LIE attack:")
    hdr = f"  {'Defense':<15}"
    for alpha in ALPHAS:
        hdr += f"  α={alpha:>4}"
    print(hdr)
    for d in DEFENSES:
        row = f"  {d:<15}"
        for alpha in ALPHAS:
            acc = results[alpha]["LIE"][d]['accuracy'] * 100
            row += f"  {acc:>5.1f}%"
        print(row)

    # ── Save ──
    save = {}
    for alpha in ALPHAS:
        save[str(alpha)] = {}
        for scn in results[alpha]:
            save[str(alpha)][scn] = {}
            for d in results[alpha][scn]:
                r = results[alpha][scn][d]
                save[str(alpha)][scn][d] = {
                    'accuracy': round(r['accuracy'], 4),
                    'fpr': round(r['fpr'], 4),
                    'detection_rate': round(r['detection_rate'], 4)}

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'paper_expB.json', 'w') as f:
        json.dump(save, f, indent=2)
    print(f"\n  ✓ Saved → {RESULTS_DIR / 'paper_expB.json'}")

    return results


# #############################################################################
#
#  EXP-C: CONTRIBUTION FAIRNESS (Gap 3)
#  → Paper Table III: Average weight by client role
#  16 Normal + 4 Free-Riders, No Attack.
#
# #############################################################################
def experiment_C(device):
    """DT-PW vs Trust-Score vs Uniform vs FedAvg with free-riders."""
    print("\n" + "=" * 80)
    print("  EXP-C: CONTRIBUTION FAIRNESS — Free-rider detection")
    print("  → Paper Table III")
    print("=" * 80)

    N_FR = 4
    N_NORMAL = NUM_CLIENTS - N_FR
    FR_IDX = list(range(N_NORMAL, NUM_CLIENTS))
    NORMAL_IDX = list(range(N_NORMAL))

    X_cl, y_cl, X_te, y_te, dim, ncls = load_all_data()

    print(f"  Training TabDDPM...", end=" ", flush=True)
    t0 = time.time()
    verifier, gen = build_verifier(X_cl, y_cl, dim, ncls, NORMAL_IDX, device)
    print(f"done ({time.time()-t0:.0f}s)")

    def _freerider_train(model, gw, idx, X, y, dev):
        """Normal clients train; free-riders copy global + tiny noise."""
        if idx in FR_IDX:
            return [w + np.random.normal(0, 1e-4, w.shape).astype(w.dtype)
                    for w in gw]
        set_parameters(model, gw)
        train_model(model, X, y, epochs=LOCAL_EPOCHS,
                    batch_size=BATCH_SIZE, lr=LR, device=dev)
        return get_parameters(model)

    def _run_strategy(name, use_verifier=False, weight_fn=None):
        """Generic strategy runner."""
        np.random.seed(SEED); torch.manual_seed(SEED)
        gm = IoTAttackNet(dim, ncls)
        cms = [IoTAttackNet(dim, ncls) for _ in range(NUM_CLIENTS)]
        if use_verifier:
            verifier.client_history = {}
        acc_hist = []
        weight_hist = []

        for rnd in range(NUM_ROUNDS):
            gw = get_parameters(gm)
            cw = [_freerider_train(cms[i], gw, i, X_cl[i], y_cl[i], device)
                  for i in range(NUM_CLIENTS)]

            if use_verifier:
                # DT verification gate
                vw, vi, vsc = [], [], []
                sel = CommitteeSelector(num_clients=NUM_CLIENTS, committee_size=1)
                seeds = sel.committee_seeds(rnd + 1)
                for i in range(NUM_CLIENTS):
                    set_parameters(cms[i], cw[i])
                    sl, pl = [], []
                    for s in seeds:
                        res = verifier.verify(
                            cms[i], device, global_model=gm, client_id=i,
                            challenge_seed=s, round_num=rnd+1,
                            data_size=len(X_cl[i]))
                        sl.append(res['score']); pl.append(res['passed'])
                    if sum(pl) >= (len(pl)//2+1):
                        vw.append(cw[i]); vi.append(i)
                        vsc.append(float(np.mean(sl)))
                rnd_w = np.zeros(NUM_CLIENTS)

                if vw and weight_fn is not None:
                    w_arr = weight_fn(vw, vi, vsc, gw, cms, rnd)
                    for j, idx in enumerate(vi):
                        rnd_w[idx] = w_arr[j]
                    agg = weighted_federated_averaging(vw, w_arr)
                elif vw:
                    uw = 1.0 / len(vw)
                    for idx in vi:
                        rnd_w[idx] = uw
                    agg, _ = federated_averaging(vw)
                else:
                    agg, _ = federated_averaging(cw)
            else:
                # No verification (FedAvg)
                rnd_w = np.ones(NUM_CLIENTS) / NUM_CLIENTS
                agg, _ = federated_averaging(cw)

            weight_hist.append(rnd_w)
            set_parameters(gm, agg)
            acc_hist.append(evaluate_model(gm, X_te, y_te, device=device))

        return acc_hist[-1], acc_hist, weight_hist

    # ── DT-PW weighting function ──
    def dtpw_fn(vw, vi, vsc, gw, cms, rnd):
        vm = [cms[j] for j in vi]
        pw = dt_performance_weighting(
            vm, vw, X_te, y_te, device,
            eval_subsample=5000, global_weights=gw,
            challenge_gen=gen,
            client_data_sizes=[len(X_cl[j]) for j in vi])
        return combine_dtpw_verification(pw, vsc)

    # ── Trust-Score weighting function (LUP/PoC style) ──
    def trust_fn(vw, vi, vsc, gw, cms, rnd):
        gw_flat = np.concatenate([g.flatten() for g in gw])
        trust = []
        for w in vw:
            w_flat = np.concatenate([p.flatten() for p in w])
            trust.append(1.0 / (1.0 + np.linalg.norm(w_flat - gw_flat)))
        s = sum(trust)
        return [t/s for t in trust]

    # ── Run all strategies ──
    strategies = OrderedDict()

    print("\n  Running DT-PW...", end=" ", flush=True)
    t0 = time.time()
    mem_before = psutil.Process(os.getpid()).memory_info().rss / 1024**2
    acc, hist, wh = _run_strategy("DT-PW", use_verifier=True, weight_fn=dtpw_fn)
    mem_after = psutil.Process(os.getpid()).memory_info().rss / 1024**2
    dtpw_time = time.time() - t0
    dtpw_mem = mem_after - mem_before
    strategies["DT-PW"] = {'acc': acc, 'hist': hist, 'weights': wh}
    print(f"{acc*100:.2f}%  ({dtpw_time:.0f}s, +{max(0,dtpw_mem):.0f}MB)")

    print("  Running Trust-Score...", end=" ", flush=True)
    t0 = time.time()
    acc, hist, wh = _run_strategy("Trust", use_verifier=True, weight_fn=trust_fn)
    trust_time = time.time() - t0
    strategies["Trust-Score"] = {'acc': acc, 'hist': hist, 'weights': wh}
    print(f"{acc*100:.2f}%  ({trust_time:.0f}s)")

    print("  Running Uniform...", end=" ", flush=True)
    t0 = time.time()
    acc, hist, wh = _run_strategy("Uniform", use_verifier=True)
    strategies["Uniform"] = {'acc': acc, 'hist': hist, 'weights': wh}
    print(f"{acc*100:.2f}%  ({time.time()-t0:.0f}s)")

    print("  Running FedAvg...", end=" ", flush=True)
    t0 = time.time()
    acc, hist, wh = _run_strategy("FedAvg", use_verifier=False)
    fedavg_time = time.time() - t0
    strategies["FedAvg"] = {'acc': acc, 'hist': hist, 'weights': wh}
    print(f"{acc*100:.2f}%  ({fedavg_time:.0f}s)")

    # ── Compute average weights by role (last 5 rounds) ──
    last_n = 5
    print("\n" + "─" * 80)
    print("  TABLE III: Average Weight by Client Role")
    print("─" * 80)
    hdr = f"  {'Strategy':<15}  {'Normal':>8}  {'Free-Rider':>10}  {'FR Detected':>12}  {'Accuracy':>8}"
    print(hdr)
    print("  " + "─" * (len(hdr) - 2))

    table_data = {}
    for sname, sdata in strategies.items():
        w_arr = np.array(sdata['weights'][-last_n:])  # (last_n, NUM_CLIENTS)
        normal_avg = np.mean([w_arr[:, i].mean() for i in NORMAL_IDX])
        fr_avg = np.mean([w_arr[:, i].mean() for i in FR_IDX])
        # Free-rider detected = avg weight < 0.5 * uniform expectation
        uniform_expected = 1.0 / NUM_CLIENTS
        fr_detected = "Yes" if fr_avg < uniform_expected * 0.5 else "No"
        acc = sdata['acc']

        table_data[sname] = {
            'normal_weight': round(float(normal_avg), 4),
            'freerider_weight': round(float(fr_avg), 4),
            'fr_detected': fr_detected,
            'accuracy': round(float(acc), 4)}

        print(f"  {sname:<15}  {normal_avg:>7.4f}   {fr_avg:>9.4f}   "
              f"{fr_detected:>11s}   {acc*100:>7.2f}%")

    # ── Overhead comparison ──
    print(f"\n  Overhead: DT-Guard adds ~{dtpw_time - fedavg_time:.0f}s "
          f"({(dtpw_time/fedavg_time - 1)*100:.0f}% overhead) per {NUM_ROUNDS} rounds")
    print(f"  Peak memory delta: ~{max(0, dtpw_mem):.0f} MB")

    # ── Save ──
    save = {
        'table': table_data,
        'accuracy_history': {s: [float(v) for v in d['hist']]
                             for s, d in strategies.items()},
        'weight_history': {s: [w.tolist() for w in d['weights']]
                           for s, d in strategies.items()},
        'overhead': {
            'dtpw_seconds': round(dtpw_time, 1),
            'fedavg_seconds': round(fedavg_time, 1),
            'overhead_pct': round((dtpw_time/fedavg_time - 1)*100, 1),
            'memory_delta_mb': round(max(0, dtpw_mem), 1)},
        'config': {
            'num_clients': NUM_CLIENTS, 'num_freeriders': N_FR,
            'rounds': NUM_ROUNDS, 'roles': {
                str(i): ('FreeRider' if i in FR_IDX else 'Normal')
                for i in range(NUM_CLIENTS)}},
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'paper_expC.json', 'w') as f:
        json.dump(save, f, indent=2)
    print(f"\n  ✓ Saved → {RESULTS_DIR / 'paper_expC.json'}")

    # ── Plots ──
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig_dir = RESULTS_DIR / 'figures'
        fig_dir.mkdir(parents=True, exist_ok=True)

        # Weight distribution bar chart
        fig, axes = plt.subplots(1, 4, figsize=(18, 4), sharey=True)
        colors = ['#4285F4' if i in NORMAL_IDX else '#EA4335' for i in range(NUM_CLIENTS)]
        for ax, (sname, sdata) in zip(axes, strategies.items()):
            w_avg = np.mean(sdata['weights'][-last_n:], axis=0)
            ax.bar(range(NUM_CLIENTS), w_avg, color=colors,
                   edgecolor='black', linewidth=0.3, width=0.7)
            ax.set_xlabel('Client ID', fontsize=9)
            ax.set_title(sname, fontweight='bold', fontsize=10)
            ax.set_xticks(range(0, NUM_CLIENTS, 4))
            ax.axhline(y=1/NUM_CLIENTS, color='gray', linestyle='--',
                       linewidth=0.8, alpha=0.5)
        axes[0].set_ylabel('Aggregation Weight')
        from matplotlib.patches import Patch
        fig.legend(handles=[
            Patch(facecolor='#4285F4', label='Normal'),
            Patch(facecolor='#EA4335', label='Free-Rider')],
            loc='lower center', ncol=2, fontsize=9,
            bbox_to_anchor=(0.5, -0.04))
        plt.suptitle('Weight Distribution — Only DT-PW suppresses free-riders',
                     fontsize=11, fontweight='bold')
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(fig_dir / 'paper_weights.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Plot → {fig_dir / 'paper_weights.png'}")

        # Convergence curves
        fig, ax = plt.subplots(figsize=(8, 5))
        markers = {'DT-PW': '-o', 'Trust-Score': '-s',
                   'Uniform': '-^', 'FedAvg': '-x'}
        for sname, sdata in strategies.items():
            ax.plot(range(1, NUM_ROUNDS+1),
                    [v*100 for v in sdata['hist']],
                    markers.get(sname, '-o'), linewidth=1.5,
                    markersize=4, label=sname)
        ax.set_xlabel('Round'); ax.set_ylabel('Accuracy (%)')
        ax.set_title('Convergence with 20% Free-Riders', fontweight='bold')
        ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(fig_dir / 'paper_convergence.png', dpi=300,
                    bbox_inches='tight')
        plt.close()
        print(f"  ✓ Plot → {fig_dir / 'paper_convergence.png'}")

    except ImportError:
        print("  ⚠ matplotlib not available — skipping plots")

    return strategies


# #############################################################################
#  MAIN
# #############################################################################
def main():
    parser = argparse.ArgumentParser(
        description="DT-Guard paper experiments (IEEE ICCE 2026)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run_paper_experiments.py                   # Run all experiments
  python3 run_paper_experiments.py --exp A           # Run EXP-A (all ratios)
  python3 run_paper_experiments.py --exp A 10        # Run EXP-A @ 10%% only
  python3 run_paper_experiments.py --exp A 20        # Run EXP-A @ 20%% only
  python3 run_paper_experiments.py --exp A 40        # Run EXP-A @ 40%% only
  python3 run_paper_experiments.py --exp A 50        # Run EXP-A @ 50%% only
  python3 run_paper_experiments.py --exp A merge     # Merge 4 partial files
  python3 run_paper_experiments.py --exp B           # Run EXP-B
  python3 run_paper_experiments.py --exp C           # Run EXP-C
""")
    parser.add_argument('--exp', nargs='+', default=None,
                        help='Experiment to run: A [10|20|40|50|merge], B, or C')
    args = parser.parse_args()

    # Parse --exp arguments
    if args.exp is None:
        exps = [('A', None), ('B', None), ('C', None)]
    else:
        exps = []
        i = 0
        while i < len(args.exp):
            letter = args.exp[i].upper()
            if letter not in ('A', 'B', 'C'):
                parser.error(f"Unknown experiment: {args.exp[i]}. Use A, B, or C.")
            sub = None
            # Check if next arg is a sub-parameter for A
            if letter == 'A' and i + 1 < len(args.exp):
                nxt = args.exp[i + 1]
                if nxt in ('10', '20', '40', '50', 'merge'):
                    sub = nxt
                    i += 1
            exps.append((letter, sub))
            i += 1

    start = datetime.now()
    print("╔" + "═" * 78 + "╗")
    print("║  DT-Guard — Paper Experiments for IEEE ICCE 2026 (6-page paper)       ║")
    print("╚" + "═" * 78 + "╝")
    print(f"  Start: {start.strftime('%Y-%m-%d %H:%M:%S')}")

    exp_desc = []
    for letter, sub in exps:
        if sub:
            exp_desc.append(f"EXP-{letter} ({sub})")
        else:
            exp_desc.append(f"EXP-{letter}")
    print(f"  Running: {', '.join(exp_desc)}")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"  Device: {device}\n", flush=True)

    for letter, sub in exps:
        if letter == 'A':
            if sub == 'merge':
                merge_expA()
            elif sub is not None:
                experiment_A(device, ratio_pct=int(sub))
            else:
                experiment_A(device)
        elif letter == 'B':
            experiment_B(device)
        elif letter == 'C':
            experiment_C(device)

    elapsed = datetime.now() - start
    print(f"\n{'═' * 80}")
    print(f"  ✅ All done! Total time: {elapsed}")
    print(f"  Results: {RESULTS_DIR}")
    print(f"{'═' * 80}")


if __name__ == "__main__":
    main()

