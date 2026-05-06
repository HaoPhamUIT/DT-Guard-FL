"""Extract thesis tables from JSON result files — no rounding errors, no guessing."""
import json, pathlib

BASE = pathlib.Path("/Users/hao.pham/PycharmProjects/DTGuardFL/DT-Guard-FL/results")

DEFENSES = ["DT-Guard","LUP","ClipCluster","SignGuard","GeoMed","PoC","FedAvg","Krum","Median","Trimmed Mean"]
ATTACKS = ["No Attack","Backdoor","LIE","Min-Max","Min-Sum","MPAF"]

def load(path):
    with open(path) as f:
        return json.load(f)

def pct(v): return f"{v*100:.2f}"

def print_table(dataset, ratio, metric):
    folder = "paper" if dataset == "CIC-IoT-2023" else "ton_iot"
    data = load(BASE / folder / f"paper_expA_{ratio}.json")
    results = data["results"]
    print(f"\n=== {dataset} — {ratio}% malicious — {metric.upper()} ===")
    header = ["Defense"] + ATTACKS
    print(" | ".join(f"{h:>14}" for h in header))
    print("-" * (15 * len(header)))
    for d in DEFENSES:
        if d not in results:
            continue
        row = [f"{d:>14}"]
        for a in ATTACKS:
            if a in results[d]:
                row.append(f"{pct(results[d][a][metric]):>14}")
            else:
                row.append(f"{'N/A':>14}")
        print(" | ".join(row))

# Print all main tables
for ds in ["CIC-IoT-2023", "ToN-IoT"]:
    for ratio in [50, 40, 20, 10]:
        for metric in ["accuracy", "detection_rate", "fpr"]:
            print_table(ds, ratio, metric)

# Overhead benchmark
print("\n=== OVERHEAD BENCHMARK (CIC-IoT-2023) ===")
ob = load(BASE / "paper" / "overhead_benchmark.json")
print(f"{'Defense':>14} | {'Total/rnd(s)':>12} | {'Train(s)':>10} | {'Agg(s)':>10} | {'DT_V(s)':>10} | {'DT_PW(s)':>10} | {'Mem(MB)':>10} | {'Acc':>8}")
for r in ob["results"]:
    print(f"{r['defense']:>14} | {r['per_round_s']:>12.4f} | {r['train_per_round_s']:>10.4f} | {r['agg_per_round_s']:>10.6f} | {r['dt_verify_per_round_s']:>10.6f} | {r['dt_pw_per_round_s']:>10.6f} | {r['peak_mem_mb']:>10.2f} | {r['accuracy']*100:>7.2f}%")

# Free-rider (ExpC)
print("\n=== FREE-RIDER (CIC-IoT-2023) ===")
ec = load(BASE / "paper" / "paper_expC.json")
for method, vals in ec["table"].items():
    print(f"{method:>14}: normal_w={vals['normal_weight']:.4f}  fr_w={vals['freerider_weight']:.4f}  detected={vals['fr_detected']}  acc={vals['accuracy']*100:.2f}%")

