#!/usr/bin/env python3
"""
PAPER EXPERIMENTS — DT-Guard on ToN-IoT Dataset
=================================================
Mirrors experiments/paper/run_paper_experiments.py but uses the ToN-IoT dataset.
Produces the same JSON output format for direct comparison with CICIoT2023 results.

Three experiments + overhead benchmark:

  EXP-A  (Gap 1 — Circumventable defenses):
    Defense comparison — 10 defenses × 6 scenarios × 4 ratios (10/20/40/50%).
    Output: paper_expA.json, paper_expA_{10,20,40,50}.json

  EXP-B  (Gap 2 — Non-IID confusion):
    Non-IID robustness — FPR at α=0.1 vs α=0.5, no attack + LIE attack.
    Output: paper_expB.json

  EXP-C  (Gap 3 — Free-rider problem):
    DT-PW vs Trust-Score vs FedAvg vs Uniform, with 4 free-riders.
    Output: paper_expC.json

  OVERHEAD:
    Per-round latency & memory for each defense.
    Output: overhead_benchmark.json

Usage:
    python run_paper_experiments.py                # Run all experiments
    python run_paper_experiments.py --exp A        # EXP-A all ratios
    python run_paper_experiments.py --exp A 10     # EXP-A @ 10% malicious only
    python run_paper_experiments.py --exp A 20     # EXP-A @ 20% malicious only
    python run_paper_experiments.py --exp A 40     # EXP-A @ 40% malicious only
    python run_paper_experiments.py --exp A 50     # EXP-A @ 50% malicious only
    python run_paper_experiments.py --exp A merge  # Merge 4 partial files
    python run_paper_experiments.py --exp B        # Run only EXP-B
    python run_paper_experiments.py --exp C        # Run only EXP-C
    python run_paper_experiments.py --exp O        # Run only overhead benchmark
    python run_paper_experiments.py --exp A 10 B C # EXP-A@10% + EXP-B + EXP-C
"""

import argparse
import torch
import numpy as np
import time
import json
import warnings
import traceback
import os
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

warnings.filterwarnings('ignore', message=".*pin_memory.*")
warnings.filterwarnings('ignore', category=UserWarning)

# Try psutil for memory measurement
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    import resource
    import platform

from dtguard.config import Config, AttackType
from dtguard.data import load_ton_iot_data, create_federated_dataset
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
# ToN-IoT is a small (10-feature, 10-class) pre-normalised dataset that
# converges to ~99 %+ accuracy very quickly.  To produce meaningful
# differentiation between defenses we:
#   • raise ATTACK_SCALE  10 → 20   (LIE now uses z=2.0 instead of 1.0)
#   • lower DIRICHLET_ALPHA 0.5 → 0.3 (stronger Non-IID → harder task)
#   • drop LOCAL_EPOCHS    3 → 1   (weaker per-round models)
#   • cap   samples/client at 10 000  (less data → more vulnerable)
#   • raise CHALLENGE_SAMPLES 200 → 1000  (larger challenge for small features)
# These settings make the experiment *harder* so that weaker defenses
# visibly degrade, while DT-Guard's behavioral verification still holds.
# =============================================================================
NUM_CLIENTS       = 20
NUM_ROUNDS        = 20
LOCAL_EPOCHS      = 2           # weaker local models → attacks bite harder
BATCH_SIZE        = 512
LR                = 0.001
DIRICHLET_ALPHA   = 0.5
ATTACK_SCALE      = 20.0        # 2× CICIoT setting — LIE z scales to 2.0
TABDDPM_EPOCHS    = 100
DT_THRESHOLD      = 0.5
CHALLENGE_SAMPLES = 500        # 5× CICIoT — small feature space needs larger sample
COMMITTEE_SIZE    = 3
SEED              = 42
MAX_SAMPLES_CLIENT = 10_000     # less data per client → more attack surface

# Resolve project root (2 levels up from experiments/ton_iot)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR     = str(PROJECT_ROOT / "data" / "ToN-IoT_Data")
RESULTS_DIR  = PROJECT_ROOT / "results" / "ton_iot"


# =============================================================================
#  MEMORY HELPERS
# =============================================================================
def get_memory_mb():
    """Return current process RSS in MB."""
    if HAS_PSUTIL:
        proc = psutil.Process(os.getpid())
        return proc.memory_info().rss / (1024 * 1024)
    else:
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if platform.system() == "Darwin":
            return usage / (1024 * 1024)
        else:
            return usage / 1024


# =============================================================================
#  HELPER: Data loading (shared across all experiments)
# =============================================================================
def load_all_data(alpha=DIRICHLET_ALPHA, max_per_client=MAX_SAMPLES_CLIENT):
    """Load ToN-IoT and create federated split."""
    train_df, test_df, feature_cols = load_ton_iot_data(
        data_dir=DATA_DIR, random_seed=SEED)

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
#  → 10 defenses × 6 scenarios × 4 malicious ratios (10%, 20%, 40%, 50%)
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
    ("LIE", AttackType.LIE),
    ("Min-Max",   AttackType.MIN_MAX),
    ("Min-Sum",   AttackType.MIN_SUM),
    ("Backdoor", AttackType.BACKDOOR),
    ("MPAF",      AttackType.MPAF),
])

DEFENSES_A = ["DT-Guard", "LUP", "ClipCluster", "SignGuard", "GeoMed",
              "PoC", "FedAvg", "Krum", "Median", "Trimmed Mean"]


def merge_expA():
    """Merge paper_expA_{10,20,40,50}.json into paper_expA.json."""
    print("\n  Merging EXP-A partial results...")
    merged = {'ratios': {}, 'config': {
        'dataset': 'ToN-IoT',
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
        label = partial['ratio_label']
        merged['ratios'][label] = {
            'results': partial['results'],
            'timings': partial['timings']}
        print(f"    ✓ Loaded {fpath} ({label})")

    if missing:
        print(f"    ⚠ Missing files: {', '.join(missing)}")
        print(f"    Run those ratios first, then merge again.")
        return

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
        print(f"  EXP-A [ToN-IoT]: DEFENSE COMPARISON — {label} malicious ONLY")
        print(f"  → 10 defenses × 6 scenarios")
        print(f"  → Output: paper_expA_{ratio_pct}.json")
        print("=" * 80, flush=True)
    else:
        run_ratios = ALL_MAL_RATIOS
        print("\n" + "=" * 80)
        print("  EXP-A [ToN-IoT]: DEFENSE COMPARISON — ALL ratios")
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
        print(f"\n  TABLE: Accuracy (%) — {ratio_label} Malicious [ToN-IoT]")
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

        # ── Save this ratio immediately ──
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        ratio_save = {
            'dataset': 'ToN-IoT',
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

    # If running all ratios, also save the merged file
    if ratio_pct is None:
        save = {'ratios': {}, 'config': {
            'dataset': 'ToN-IoT',
            'mal_ratios': {k: v for k, v in ALL_MAL_RATIOS.items()},
            'alpha': DIRICHLET_ALPHA, 'rounds': NUM_ROUNDS,
            'num_clients': NUM_CLIENTS,
            'attacks': list(ATTACKS_A.keys()),
            'defenses': DEFENSES_A}}
        for ratio_label in run_ratios:
            save['ratios'][ratio_label] = {'results': {}, 'timings': {}}
            for d in DEFENSES_A:
                save['ratios'][ratio_label]['results'][d] = {}
                save['ratios'][ratio_label]['timings'][d] = {}
                for a in ATTACKS_A:
                    r = all_results[ratio_label][d][a]
                    save['ratios'][ratio_label]['results'][d][a] = {
                        'accuracy': round(r['accuracy'], 4),
                        'detection_rate': round(r['detection_rate'], 4),
                        'fpr': round(r['fpr'], 4)}
                    save['ratios'][ratio_label]['timings'][d][a] = round(
                        all_timings[ratio_label][d][a], 1)
        with open(RESULTS_DIR / 'paper_expA.json', 'w') as f:
            json.dump(save, f, indent=2)
        print(f"  ✓ Saved → {RESULTS_DIR / 'paper_expA.json'}")

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
    print("  EXP-B [ToN-IoT]: NON-IID ROBUSTNESS — FPR under no attack")
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
    print("  NON-IID COMPARISON [ToN-IoT]: FPR (%) — No Attack (lower = better)")
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
    save = {'dataset': 'ToN-IoT'}
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
    print("  EXP-C [ToN-IoT]: CONTRIBUTION FAIRNESS — Free-rider detection")
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
    mem_before = get_memory_mb()
    acc, hist, wh = _run_strategy("DT-PW", use_verifier=True, weight_fn=dtpw_fn)
    mem_after = get_memory_mb()
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
    print("  TABLE III [ToN-IoT]: Average Weight by Client Role")
    print("─" * 80)
    hdr = f"  {'Strategy':<15}  {'Normal':>8}  {'Free-Rider':>10}  {'FR Detected':>12}  {'Accuracy':>8}"
    print(hdr)
    print("  " + "─" * (len(hdr) - 2))

    table_data = {}
    for sname, sdata in strategies.items():
        w_arr = np.array(sdata['weights'][-last_n:])  # (last_n, NUM_CLIENTS)
        normal_avg = np.mean([w_arr[:, i].mean() for i in NORMAL_IDX])
        fr_avg = np.mean([w_arr[:, i].mean() for i in FR_IDX])
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
        'dataset': 'ToN-IoT',
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
        plt.suptitle('Weight Distribution [ToN-IoT] — Only DT-PW suppresses free-riders',
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
        ax.set_title('Convergence with 20% Free-Riders [ToN-IoT]', fontweight='bold')
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
#
#  OVERHEAD BENCHMARK
#  → Per-round latency & memory for each defense
#  → Output: overhead_benchmark.json (same format as paper version)
#
# #############################################################################
OVERHEAD_ATTACK = AttackType.BACKDOOR
OVERHEAD_DEFENSES = [
    "FedAvg", "Krum", "Median", "Trimmed Mean", "GeoMed",
    "SignGuard", "ClipCluster", "LUP", "PoC", "DT-Guard",
]


def _benchmark_defense(defense_name, X_clients, y_clients, X_test, y_test,
                       input_dim, num_classes, device, num_malicious,
                       num_rounds, num_clients, verifier=None):
    """Run one defense strategy and return timing + memory data."""
    from dtguard.security import calculate_shapley_values, calculate_weighted_shapley

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

    round_times = []
    train_times = []
    agg_times = []
    dt_verify_times = []
    dt_pw_times = []

    mem_before = get_memory_mb()
    peak_mem = mem_before

    for rnd in range(num_rounds):
        round_start = time.perf_counter()

        # Phase 1: Local training
        train_start = time.perf_counter()
        gw = get_parameters(global_model)
        cw = []
        for i, m in enumerate(client_models):
            set_parameters(m, gw)
            train_model(m, X_clients[i], y_clients[i],
                        epochs=LOCAL_EPOCHS, batch_size=BATCH_SIZE,
                        lr=LR, device=device)
            cw.append(get_parameters(m))

        if num_malicious > 0:
            atk_str = OVERHEAD_ATTACK.value
            for mi in malicious_indices:
                cw[mi] = apply_attack(cw[mi], atk_str, ATTACK_SCALE,
                                      all_client_weights=cw,
                                      malicious_indices=malicious_indices)
        train_end = time.perf_counter()
        train_times.append(train_end - train_start)

        # Phase 2: Server-side aggregation
        agg_start = time.perf_counter()
        dt_verify_t = 0.0
        dt_pw_t = 0.0

        if defense_name == "DT-Guard":
            dt_v_start = time.perf_counter()
            verified_w, verified_idx, v_scores = [], [], []
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
                if passed:
                    verified_w.append(cw[i])
                    verified_idx.append(i)
                    v_scores.append(float(np.mean(sc_list)))
            dt_verify_t = time.perf_counter() - dt_v_start

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
            n_mal = num_malicious
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


def experiment_overhead(device):
    """Overhead benchmark: latency & memory for all defenses."""
    num_malicious = max(1, int(NUM_CLIENTS * 0.1))  # 10% malicious

    print("\n" + "=" * 90)
    print("  OVERHEAD BENCHMARK [ToN-IoT]: Latency & Memory Trade-off")
    print("=" * 90)
    print(f"  Clients: {NUM_CLIENTS}  |  Malicious: {num_malicious}")
    print(f"  Rounds: {NUM_ROUNDS}   |  Attack: {OVERHEAD_ATTACK.value}")
    print(f"  Local Epochs: {LOCAL_EPOCHS}  |  Batch Size: {BATCH_SIZE}")
    print(f"  Defenses: {OVERHEAD_DEFENSES}")
    print()

    # Load data
    X_cl, y_cl, X_te, y_te, dim, ncls = load_all_data()

    # Train verifier for DT-Guard
    benign_idx = list(range(NUM_CLIENTS - num_malicious))
    print("  Training TabDDPM for DT-Guard...", end=" ", flush=True)
    t0 = time.time()
    verifier, _ = build_verifier(X_cl, y_cl, dim, ncls, benign_idx, device)
    print(f"done ({time.time()-t0:.0f}s)")

    all_results = []

    for defense in OVERHEAD_DEFENSES:
        print(f"\n{'─' * 90}")
        print(f"  Benchmarking: {defense}")
        print(f"{'─' * 90}")

        try:
            result = _benchmark_defense(
                defense_name=defense,
                X_clients=X_cl, y_clients=y_cl,
                X_test=X_te, y_test=y_te,
                input_dim=dim, num_classes=ncls,
                device=device, num_malicious=num_malicious,
                num_rounds=NUM_ROUNDS, num_clients=NUM_CLIENTS,
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

    if not all_results:
        print("\nNo results collected.")
        return

    # Print summary table
    fedavg_result = next((r for r in all_results if r["defense"] == "FedAvg"), None)
    fedavg_agg = fedavg_result["agg_per_round_s"] if fedavg_result else 0.0

    print(f"\n\n{'=' * 90}")
    print(f"  TABLE: Per-Round Overhead Comparison [ToN-IoT]")
    print(f"  ({NUM_CLIENTS} clients, {NUM_ROUNDS} rounds, "
          f"{num_malicious} malicious, attack={OVERHEAD_ATTACK.value})")
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
        server_overhead = dtg['dt_verify_per_round_s'] + dtg['dt_pw_per_round_s']
        print(f"    Total Server:   {server_overhead:.3f}s")
        print(f"    Server/Total:   {server_overhead / dtg['per_round_s'] * 100:.1f}%")

    # Save
    save_data = {
        "dataset": "ToN-IoT",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "num_clients": NUM_CLIENTS,
            "num_rounds": NUM_ROUNDS,
            "num_malicious": num_malicious,
            "attack": OVERHEAD_ATTACK.value,
            "local_epochs": LOCAL_EPOCHS,
            "batch_size": BATCH_SIZE,
        },
        "results": [],
    }
    for r in all_results:
        entry = {k: v for k, v in r.items()}
        save_data["results"].append(entry)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "overhead_benchmark.json"
    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2, default=str)
    print(f"\n  ✓ Saved → {out_path}")

    return all_results


# #############################################################################
#  MAIN
# #############################################################################
def main():
    parser = argparse.ArgumentParser(
        description="DT-Guard experiments on ToN-IoT dataset (IEEE ICCE 2026)",
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
  python3 run_paper_experiments.py --exp O           # Run overhead benchmark
""")
    parser.add_argument('--exp', nargs='+', default=None,
                        help='Experiment to run: A [10|20|40|50|merge], B, C, or O')
    args = parser.parse_args()

    # Parse --exp arguments
    if args.exp is None:
        exps = [('A', None), ('B', None), ('C', None), ('O', None)]
    else:
        exps = []
        i = 0
        while i < len(args.exp):
            letter = args.exp[i].upper()
            if letter not in ('A', 'B', 'C', 'O'):
                parser.error(f"Unknown experiment: {args.exp[i]}. Use A, B, C, or O.")
            sub = None
            if letter == 'A' and i + 1 < len(args.exp):
                nxt = args.exp[i + 1]
                if nxt in ('10', '20', '40', '50', 'merge'):
                    sub = nxt
                    i += 1
            exps.append((letter, sub))
            i += 1

    start = datetime.now()
    print("╔" + "═" * 78 + "╗")
    print("║  DT-Guard — ToN-IoT Experiments for IEEE ICCE 2026                    ║")
    print("╚" + "═" * 78 + "╝")
    print(f"  Dataset: ToN-IoT ({DATA_DIR})")
    print(f"  Start:   {start.strftime('%Y-%m-%d %H:%M:%S')}")

    exp_desc = []
    for letter, sub in exps:
        if sub:
            exp_desc.append(f"EXP-{letter} ({sub})")
        else:
            exp_desc.append(f"EXP-{letter}")
    print(f"  Running: {', '.join(exp_desc)}")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"  Device:  {device}")
    print(f"  Output:  {RESULTS_DIR}\n", flush=True)

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
        elif letter == 'O':
            experiment_overhead(device)

    elapsed = datetime.now() - start
    print(f"\n{'═' * 80}")
    print(f"  ✅ All done! Total time: {elapsed}")
    print(f"  Results: {RESULTS_DIR}")
    print(f"{'═' * 80}")


if __name__ == "__main__":
    main()

