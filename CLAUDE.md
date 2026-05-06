# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DT-Guard is a Federated Learning defense system for IoT intrusion detection that uses **Digital Twin (DT) verification** to detect and filter malicious clients. It combines:

- **TabDDPM Challenge Generator**: Denoising diffusion model for synthetic attack generation
- **Digital Twin Verifier**: Active behavioral testing of client models
- **DT-PW Weighting**: Dynamic contribution scoring via prediction disagreement
- **Committee Selection**: Reputation-based verifier selection using Shapley values
- **Multiple Baseline Defenses**: LUP, ClipCluster, SignGuard, PoC, GeoMed, Krum, Median, Trimmed Mean

### Research Context (IEEE ICCE 2026 Paper)

The system addresses three research gaps:
1. **Gap 1 (Circumventable Defenses)**: Passive defenses (Krum, etc.) are vulnerable to advanced attacks
2. **Gap 2 (Non-IID Confusion)**: Passive methods falsely reject honest clients under heterogeneous data
3. **Gap 3 (Free-rider Problem)**: Trust-based methods reward non-contributing clients

---

## Common Development Tasks

### Running Experiments

```bash
# Install dependencies
pip install -r requirements.txt

# CIC-IoT-2023 dataset - Place CSV files in data/CICIoT2023/

# Run all paper experiments (EXP-A, B, C)
python experiments/paper/run_paper_experiments.py

# Run specific experiment with malicious ratio (for parallel execution)
python experiments/paper/run_paper_experiments.py --exp A 10  # 10% malicious
python experiments/paper/run_paper_experiments.py --exp A 20  # 20% malicious
python experiments/paper/run_paper_experiments.py --exp A 40  # 40% malicious
python experiments/paper/run_paper_experiments.py --exp A 50  # 50% malicious
python experiments/paper/run_paper_experiments.py --exp A merge  # Merge partial results

# ToN-IoT dataset experiments (mirrors paper structure)
python experiments/ton_iot/run_paper_experiments.py --exp A 10

# Generate publication figures
python plots/paper/generate_paper_plots.py
python plots/paper/generate_overhead_plot.py
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_security.py -v

# Quick integration test
python legacy/run_quick_test.py
```

---

## Architecture

### Core Package Structure (`dtguard/`)

```
dtguard/
├── config.py           # Config dataclass, AttackType/DefenseType enums
├── data/
│   └── loader.py       # CIC-IoT-2023/ToN-IoT loading, Dirichlet federated split
├── models/
│   ├── ids_model.py            # IoTAttackNet (256→128→64→num_classes)
│   └── tabddpm_generator.py    # TabDDPM diffusion for challenge sets
├── security/
│   ├── digital_twin.py         # DigitalTwinVerifier: active verification
│   ├── attacks.py              # LIE, Min-Max, Min-Sum, MPAF, etc.
│   ├── dt_pw.py               # DT-PW: prediction disagreement scoring
│   ├── committee.py            # CommitteeSelector: reputation-based verifiers
│   └── reputation.py          # ReputationSystem: score tracking
└── fl/
    ├── aggregation.py           # run_federated_learning(), FedAvg
    └── baselines.py           # LUP, ClipCluster, SignGuard, PoC, GeoMed...
```

### Key Abstractions

**Config (`dtguard.config.Config`)**
- Centralized configuration dataclass
- `dataset_type`: "CICIoT2023" or "ToN-IoT"
- `num_clients`, `num_malicious`: FL setup
- `dirichlet_alpha`: Non-IID heterogeneity (lower = more heterogeneous)
- `dt_threshold`, `challenge_samples`: DT verifier settings
- `attack_type`: From AttackType enum (BACKDOOR, LIE, MIN_MAX, etc.)
- `defense_type`: From DefenseType enum (DTGUARD, LUP, CLIPCLUSTER, etc.)

**Data Flow**
1. `load_data()` → Load CSVs, cache to pickle, train/test split
2. `create_federated_dataset()` → Dirichlet-based Non-IID split across clients
3. `TabDDPMChallengeGenerator.train_gan()` → Train diffusion on benign data
4. `DigitalTwinVerifier.verify()` → Generate challenge set, test model
5. `run_federated_learning()` → Main FL loop with verification

### DT Verification Pipeline

Each round:
1. Local training on each client
2. Attack applied to malicious clients (via `apply_attack()`)
3. **DT Verification** (if `verifier` is not None):
   - CommitteeSelector picks verifier committee (reputation + Shapley)
   - For each client: multiple verifications with different seeds
   - Pass/fail based on hybrid score: 70% performance (F1) + 30% integrity (weight divergence)
4. Shapley/DT-PW weighting of passed clients
5. Weighted aggregation

**Key verification scoring formula**:
- `hybrid_score = 0.7 * f1_score + 0.3 * integrity_score`
- `integrity_score = 1.0 - normalized_weight_divergence`
- For severe poisoning (divergence > 10.0): `score = min(performance, integrity)`

### DT-PW (Free-rider Detection)

Principle: Free-riders copy global model → predictions ≈ global → low disagreement
- Compute prediction disagreement rate between client and global model
- If `disagree < 2%`: score = 0 (free-rider)
- Otherwise: score = disagree (trained client)
- Weights normalized to sum = 1

---

## Attack Types (Faithful to LUP Repository)

Advanced attacks (from DT-BFL/LUP papers):
- **LIE** (A Little Is Enough): `μ - z*σ` where z scales with attack strength
- **MIN_MAX**: Binary search for optimal gamma under max-distance constraint
- **MIN_SUM**: Binary search for optimal gamma under max-sum-distance constraint
- **MPAF**: `(w - w_base) * 10.0` where w_base is random
- **BYZMEAN**: `μ - 0.5*σ`
- **SIGN_FLIP**: Simple gradient sign flip

Classic attacks:
- **MODEL_POISONING**: Scale weights by attack_scale
- **BACKDOOR**: Perturbation targeting last 2 layers
- **NOISE_INJECTION**: Add Gaussian noise to alternate layers

---

## Baseline Defenses (`dtguard.fl.baselines`)

All baselines return `(aggregated_weights, rejected_indices)` tuple:

| Defense | Approach | Key Features |
|----------|-----------|---------------|
| **LUP** | 2-stage: MAD bounding + clustering | Trust score, kurtosis, distance features |
| **ClipCluster** | Norm-clip + cosine clustering | Agglomerative clustering on cosine distance |
| **SignGuard** | L2 filtering + sign-gradient clustering | MeanShift on sign features (pos/neg/zero fractions) |
| **PoC** | Contribution = quality × trust × capability | MMD² deviation, historical trust, data size |
| **GeoMed** | Weiszfeld's algorithm | Iteratively reweighted geometric median |
| **Krum** | Select most representative | Distance-based scoring, n-2f nearest neighbors |
| **Median** | Coordinate-wise median | L2-based outlier rejection |
| **Trimmed Mean** | Remove extreme values by norm | Trim top/bottom by trim_ratio |

---

## Experiment Results

**Output directory**: `results/paper/` or `results/ton_iot/`

Result files:
- `paper_expA.json` - Defense comparison (10 defenses × 5 attacks × 4 ratios)
- `paper_expB.json` - Non-IID FPR analysis (α=0.1 vs α=0.5)
- `paper_expC.json` - Free-rider weight comparison (DT-PW vs Trust-Score vs Uniform)
- `overhead_benchmark.json` - Computational cost analysis

**Per-ratio partial files**: `paper_expA_10.json`, `paper_expA_20.json`, etc.
Use `--exp A merge` to combine partial results.

---

## Configuration Notes

- **DT threshold**: `dt_threshold` (default 0.20) - Lower = more detections
- **TabDDPM epochs**: `gan_epochs` (default 50-100) - Higher = better challenge sets
- **Challenge samples**: `challenge_samples` (default 500) - More samples = more reliable verification
- **Committee size**: `committee_size` (default 3) - Number of verifiers per round
- **Attack scale**: `attack_scale` (default 10.0-15.0) - Attack strength multiplier

**Non-IID tuning**:
- `dirichlet_alpha=0.1`: Extreme heterogeneity (harder for passive methods)
- `dirichlet_alpha=0.5`: Moderate heterogeneity (baseline)

---

## Datasets

### CIC-IoT-2023
- 10M+ network flows, 86 features, 34 classes
- Download: [UNB CIC Dataset](https://www.unb.ca/cic/datasets/iot-2023.html)
- Placement: `data/CICIoT2023/*.csv`

### ToN-IoT
- Structure: `train_data.csv`, `train_label.csv`, `test_data.csv`, `test_label.csv`
- Placement: `data/ToN-IoT_Data/`
- Use `load_ton_iot_data()` in `data/loader.py`

---

## Important Patterns

1. **Device handling**: Always pass `device` to models - use `torch.device('cuda' if torch.cuda.is_available() else 'cpu')`

2. **Weight conversion**: Models use PyTorch tensors, but aggregation uses NumPy arrays. Use `get_parameters()` and `set_parameters()` from `dtguard.models.ids_model`.

3. **Deterministic seeds**: Set `np.random.seed(SEED)` and `torch.manual_seed(SEED)` before experiments

4. **Reproducible challenges**: Pass `challenge_seed` to `verifier.verify()` for deterministic challenge sets (used in committee-based verification)

5. **BatchNorm safety**: Training with BatchNorm requires at least 2 samples per batch. The `train_model()` function handles this automatically by adjusting batch size.

6. **Memory**: Large experiments (20 clients, 20 rounds, 200 challenge samples) can use significant memory. The TabDDPM pre-generates a pool of samples to avoid slow diffusion at inference time.
