# ToN-IoT Experiments for DT-Guard

This directory contains experiments for the **ToN-IoT dataset** that mirror the CIC-IoT-2023 experiments for fair comparison.

## Dataset

- **Source**: ToN-IoT (Testbed of Networks for IoT)
- **Location**: `data/ToN-IoT_Data/`
- **Structure**:
  - `train_data.csv` - Training features (368,824 samples, 10 features)
  - `train_label.csv` - Training labels (10 classes)
  - `test_data.csv` - Test features (92,209 samples)
  - `test_label.csv` - Test labels

## Experiments (matching CIC-IoT-2023 structure)

### Experiment 3: Comprehensive Defense Comparison
**File**: `run_experiment3.py`

Compares DT-Guard against 9 baselines under 5 attack types:
- **Defenses**: DT-Guard, LUP, ClipCluster, SignGuard, GeoMed, PoC, FedAvg, Krum, Median, Trimmed Mean
- **Attacks**: No Attack, Backdoor, LIE, Min-Max, Min-Sum, MPAF
- **Setup**: 20 clients, 5 malicious (25%), 10 rounds

```bash
.venv/bin/python experiments/ton_iot/run_experiment3.py
```

### Experiment 4: Non-IID Robustness
**File**: `run_experiment4_noniid.py`

Tests DT-Guard's ability to distinguish legitimate Non-IID drift from malicious attacks:
- **Defenses**: DT-Guard, LUP, ClipCluster, SignGuard, GeoMed, PoC
- **Dirichlet α**: 0.1 (Extreme) → 10.0 (Near-IID)
- **Scenarios**: No Attack (FPR), BACKDOOR (Accuracy, Detection)

```bash
.venv/bin/python experiments/ton_iot/run_experiment4_noniid.py
```

### Experiment 5: DT-PW Fairness Evaluation
**File**: `run_experiment5_dtpw.py`

Compares contribution assessment strategies with free-riders:
- **Strategies**: DT-PW, Shapley, Trust-Score, Uniform, FedAvg
- **Setup**: 16 Normal + 4 Free-Riders, 20 rounds

```bash
.venv/bin/python experiments/ton_iot/run_experiment5_dtpw.py
```

## Quick Test

```bash
# Quick sanity test
.venv/bin/python experiments/ton_iot/run_quick_test.py
```

## Results

Results are saved to `results/ton_iot/`:
- `exp3_comprehensive_toniot.pkl` - Defense comparison results
- `exp3_summary_toniot.json` - Summary in JSON format
- `exp4_noniid_toniot.json` - Non-IID robustness results
- `exp5_dtpw_toniot.json` - DT-PW fairness results

## Comparison with CIC-IoT-2023

| Metric | CIC-IoT-2023 | ToN-IoT |
|--------|--------------|---------|
| Features | 46 | 10 |
| Classes | 34 | 10 |
| Train samples | ~450K | 369K |
| Test samples | ~110K | 92K |

Both experiments use **identical configuration** for fair comparison:
- Same defense methods
- Same attack types
- Same FL settings (clients, rounds, epochs)
- Same evaluation metrics

## References

- Research proposal: `DocumentRef/de_cuong-DT-Guard.md`
- CIC-IoT-2023 experiments: `experiments/thesis/run_experiment*.py`
