# Experiments Directory

This directory contains all experiment scripts organized by purpose.

## 📁 Directory Structure

### `/paper/` - IEEE ICCE 2026 Paper Experiments
**Current (Latest) experiments for the 6-page IEEE paper.**

- **`run_paper_experiments.py`** - Main unified script for EXP-A, B, C
  - EXP-A: Defense comparison (10 defenses × 5 attacks × 4 ratios)
  - EXP-B: Non-IID robustness (FPR at α=0.1 vs α=0.5)
  - EXP-C: Contribution fairness (DT-PW vs Trust-Score vs FedAvg vs Uniform)

- **`run_experiment7_unified.py`** - Unified defense comparison across malicious ratios (10%, 30%, 50%)
  - Produces comparison tables matching Kịch bản 2 requirements
  - Tests all 10 defenses against 6 attack scenarios

- **`run_experiment_overhead.py`** - Computational overhead analysis
  - Measures per-round latency & memory trade-off
  - Produces Table II for the paper

**Usage:**
```bash
# Run all paper experiments
python experiments/paper/run_paper_experiments.py

# Run specific experiment
python experiments/paper/run_paper_experiments.py --exp A 50  # EXP-A @ 50% malicious
python experiments/paper/run_paper_experiments.py --exp B       # EXP-B only
python experiments/paper/run_paper_experiments.py --exp C       # EXP-C only

# Run overhead analysis
python experiments/paper/run_experiment_overhead.py
```

### `/thesis/` - Thesis Experiments
**Legacy experiments from the thesis work.**

Contains earlier experimental scripts:
- `run_experiment[1-6,10,25,50].py` - Individual experiment scripts
- `run_experiments.py` - General experiment runner
- `run_experiment4_noniid.py` - Non-IID data experiments
- `run_experiment5_dtpw.py` - DT-PW weighting experiments
- `run_experiment6_datagen.py` - Data generation experiments
- `run_experiment5_shapley_quick_test.py` - Shapley value tests
- `run_quick_experiment3.py` - Quick test runs

**Note:** These are kept for reference and reproducibility of thesis results.

## 📊 Output Structure

All experiment results are saved to:
```
results/
└── paper_experiments/
    ├── paper_expA.json          # Defense comparison results
    ├── paper_expB.json          # Non-IID robustness results
    ├── paper_expC.json          # Fairness results
    ├── overhead_benchmark.json  # Overhead analysis
    └── figures/                 # Generated plots
        ├── fig2_degradation.pdf
        ├── fig3_fpr.pdf
        └── fig4_weights.pdf
```

## 🔧 Common Configuration

Most experiments share these parameters:
- **Dataset:** CIC-IoT-2023
- **Clients:** 20
- **Rounds:** 20
- **Local Epochs:** 3
- **Batch Size:** 512
- **Learning Rate:** 0.001
- **Dirichlet α:** 0.5 (unless testing Non-IID)

## 📝 Notes

- Paper experiments use TabDDPM for challenge generation
- Thesis experiments may use older GAN-based approach
- Results are deterministic with fixed seed (42)
