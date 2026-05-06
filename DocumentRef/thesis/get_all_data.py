#!/usr/bin/env python3
"""Extract all thesis data from JSON result files."""
import json, pathlib, numpy as np

BASE = pathlib.Path(__file__).resolve().parent.parent.parent / "results"

def load(p):
    with open(p) as f:
        return json.load(f)

# ============================================================
# 1. Generator Selection (exp6_summary.json)
# ============================================================
print("=" * 70)
print("  GENERATOR SELECTION (fig_generator_selection.png)")
print("=" * 70)
exp6 = load(BASE / "generic" / "exp6_summary.json")
for g in ["TabDDPM", "TabSyn", "ForestDiffusion", "CTGAN", "WGAN-GP"]:
    r = exp6[g]
    print(f"  {g:>18}:  TSTR={r['custom_tstr']:.3f}"
          f"  Wass={r['stats.wasserstein_dist.joint']:.4f}"
          f"  JSD={r['stats.jensenshannon_dist.marginal']:.4f}"
          f"  Recall={r['stats.prdc.recall']:.3f}"
          f"  Cov={r['stats.prdc.coverage']:.4f}"
          f"  OracleAcc={r['oracle_label_accuracy']:.3f}"
          f"  DT-Sep={r['dt_guard_separation']:.3f}"
          f"  Time={r['train_gen_time']:.1f}s"
          f"  RAM={r['peak_ram_mb']:.1f}MB")

# ============================================================
# 2. Free-rider Detection (exp5_dtpw.json)
# ============================================================
print("\n" + "=" * 70)
print("  FREE-RIDER DETECTION (fig_free_rider_weights.png)")
print("=" * 70)
exp5 = load(BASE / "generic" / "exp5_dtpw.json")
cfg = exp5["config"]
fr_idx = cfg["free_rider_idx"]  # [16,17,18,19]
sh = exp5.get("score_history", {})
wh = exp5.get("weight_history", {})

# DT-PW and Shapley are in score_history; Trust-Score/Uniform/FedAvg in weight_history
sources = [
    ("DT-PW (Ours)", sh),
    ("Shapley", sh),
    ("Trust-Score (LUP)", wh),
    ("Uniform", wh),
    ("FedAvg", wh),
]
for strat_key, hist_dict in sources:
    if strat_key in hist_dict and "No Attack" in hist_dict[strat_key]:
        arr = np.array(hist_dict[strat_key]["No Attack"])
        last5 = arr[-5:].mean(axis=0)
        norm_w = last5[:16].mean()
        fr_w = last5[16:].mean()
        acc_vals = list(exp5["accuracy"].get(strat_key, {}).values())
        acc_pct = acc_vals[0] * 100 if acc_vals else 0
        detected = "Yes" if fr_w < 0.001 else "No"
        print(f"  {strat_key:>22}:  norm_w={norm_w:.4f}  fr_w={fr_w:.4f}"
              f"  detected={detected}  acc={acc_pct:.2f}%")

# Also from paper_expC (alternative source)
print("\n  --- paper_expC.json (CIC-IoT-2023 specific) ---")
ec = load(BASE / "paper" / "paper_expC.json")
for m, v in ec["table"].items():
    print(f"  {m:>22}:  norm_w={v['normal_weight']:.4f}"
          f"  fr_w={v['freerider_weight']:.4f}"
          f"  detected={v['fr_detected']}"
          f"  acc={v['accuracy']*100:.2f}%")

# ============================================================
# 3. Multi-ratio Defense Comparison
# ============================================================
DEFENSES = ["DT-Guard", "LUP", "ClipCluster", "SignGuard", "GeoMed",
            "PoC", "FedAvg", "Krum", "Median", "Trimmed Mean"]
ATTACKS = ["Backdoor", "LIE", "Min-Max", "Min-Sum", "MPAF"]

for ds, folder in [("CIC-IoT-2023", "paper"), ("ToN-IoT", "ton_iot")]:
    print(f"\n{'=' * 70}")
    print(f"  DEFENSE COMPARISON — {ds}")
    print(f"{'=' * 70}")
    for ratio in [10, 20, 40, 50]:
        data = load(BASE / folder / f"paper_expA_{ratio}.json")["results"]
        print(f"\n  --- {ratio}% malicious ---")
        for d in DEFENSES:
            if d not in data:
                continue
            accs = [data[d][a]["accuracy"] * 100 for a in ATTACKS if a in data[d]]
            dets = [data[d][a]["detection_rate"] * 100 for a in ATTACKS if a in data[d]]
            fprs = [data[d][a]["fpr"] * 100 for a in ATTACKS if a in data[d]]
            collapses = sum(1 for a in accs if a < 10)
            print(f"    {d:>14}: Acc={np.mean(accs):.1f}% [{min(accs):.1f}-{max(accs):.1f}]"
                  f"  Det={np.mean(dets):.1f}%  FPR={np.mean(fprs):.1f}%"
                  f"  Collapse={collapses}/5")

# ============================================================
# 4. Overhead Benchmark
# ============================================================
print(f"\n{'=' * 70}")
print("  OVERHEAD BENCHMARK (CIC-IoT-2023)")
print(f"{'=' * 70}")
ob = load(BASE / "paper" / "overhead_benchmark.json")
for r in ob["results"]:
    dt_total = r["dt_verify_per_round_s"] + r["dt_pw_per_round_s"]
    print(f"  {r['defense']:>14}: {r['per_round_s']:.3f}s/rnd"
          f"  train={r['train_per_round_s']:.3f}s"
          f"  agg={r['agg_per_round_s']:.4f}s"
          f"  dt_overhead={dt_total:.4f}s"
          f"  mem={r['peak_mem_mb']:.0f}MB"
          f"  acc={r['accuracy']*100:.2f}%")

# ============================================================
# 5. Available figures
# ============================================================
print(f"\n{'=' * 70}")
print("  AVAILABLE FIGURES")
print(f"{'=' * 70}")
for folder in ["generic/figures", "paper/figures", "ton_iot/figures"]:
    p = BASE / folder
    if p.exists():
        for f in sorted(p.glob("*.png")):
            print(f"  {folder}/{f.name}")

