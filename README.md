# DTGuardFL - Digital Twin Guard for Federated Learning

Active verification for robust IoT intrusion detection using Digital Twin technology.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run main demo
python experiments/run_dtguard.py

# Run paper experiments (2 main experiments)
python run_experiments.py
```

## 📁 Project Structure

```
DTGuardFL/
├── dtguard/                 # Main package
│   ├── config.py           # Configuration
│   ├── data/               # Data loading & preprocessing
│   ├── models/             # Neural networks (IoT model + GAN)
│   ├── security/           # Attacks + DT verifier
│   └── fl/                 # Federated learning
│
├── experiments/            # Experiment scripts
│   └── run_dtguard.py     # Demo experiment
│
├── run_experiments.py      # Paper experiments (unified)
│
├── configs/                # Configuration files
│   └── default.yaml       # Default settings
│
├── data/                   # Dataset (place CIC-IoT-2023 here)
│   └── CICIoT2023/
│
└── tests/                  # Unit tests
```

## 🎯 Features

- **Digital Twin Verification**: Active model verification using GAN-generated challenge sets
- **Non-IID Data**: Dirichlet distribution for realistic heterogeneous data
- **Attack Detection**: Model poisoning, gradient ascent, Byzantine attacks
- **CIC-IoT-2023**: 10M+ samples, 86 features, 34 attack classes

## 📊 Usage

### Basic Usage

```python
from dtguard import Config
from dtguard.data import load_data, create_federated_dataset
from dtguard.models import IoTAttackNet, GANGenerator
from dtguard.security import DigitalTwinVerifier
from dtguard.fl import run_federated_learning

# Configure
config = Config(num_clients=3, num_rounds=5)

# Load data
train_df, test_df, features = load_data(config)
X_clients, y_clients = create_federated_dataset(train_df, features, config)

# Train GAN
gan = GANGenerator(output_dim=len(features))
gan.train_gan(X_clients[0], y_clients[0])

# Create verifier
verifier = DigitalTwinVerifier(gan)

# Run FL with DT-Guard
metrics = run_federated_learning(...)
```

### Configuration

Edit `configs/default.yaml`:

```yaml
num_clients: 3
num_rounds: 5
dirichlet_alpha: 0.5  # Non-IID level
dt_threshold: 0.5     # Verification threshold
attack_type: "MODEL_POISONING"
attack_scale: 3.0
```

## 📈 Expected Output

### Demo (run_dtguard.py)
```
DT-GUARD - Active Digital Twin Verification for FL
============================================================
--- Round 1/5 ---
  Client 0: Trained (benign)
  Client 1: Trained (benign)
  Client 2: Trained (MALICIOUS)

  Digital Twin Verification:
    Client 0: Score=0.723 ✓ PASS
    Client 1: Score=0.698 ✓ PASS
    Client 2: Score=0.234 ✗ FAIL

  Filtered: 1 malicious client(s)
  Global Accuracy: 0.8234
============================================================
Final Accuracy: 0.8456
Detection Rate: 100.0%
```

### Paper Experiments (run_experiments.py)
```
EXPERIMENT 1: DEFENSE COMPARISON
  MODEL_POISONING: Acc=0.8567, Det=95%
  GRADIENT_ASCENT: Acc=0.8423, Det=100%
  LABEL_FLIPPING: Acc=0.8789, Det=90%

EXPERIMENT 2: ABLATION STUDY
  Full: Acc=0.8567 (Baseline)
  w/o_DT: Acc=0.8345 (-2.2%)
  w/o_Shapley: Acc=0.8123 (-4.4%)
  Baseline: Acc=0.4567 (-40.0%)
```

## 📊 Paper Figures

```bash
# Run paper experiments (defense comparison)
python run_experiments.py

# Plot paper-ready figures
python experiments/plot_paper_results.py
```

## 🔬 Key Components

### 1. Digital Twin Verifier
- Generates challenge sets using GAN
- Tests models in sandbox environment
- Scores: Si = α·DR - β·FPR
- Filters malicious models before aggregation

### 2. GAN Challenge Generator
- Lightweight WGAN architecture
- Generates synthetic attack samples
- Mixes with real attacks (50-50)

### 3. Federated Learning
- Non-IID data distribution
- FedAvg aggregation
- Support for multiple attack types

## 📊 Dataset

**CIC-IoT-2023**
- 10,170,198 samples
- 86 features
- 34 classes (1 Benign + 33 Attacks)
- DDoS, DoS, Mirai, Reconnaissance, Web attacks, etc.

Place dataset in `data/CICIoT2023/` directory.

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_security.py
```

## 📝 License

MIT License

---

**Version**: 1.0.0  
**Status**: ✅ Production Ready
# DT-Guard-FL
