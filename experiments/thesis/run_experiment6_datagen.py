#!/usr/bin/env python3
"""
EXPERIMENT 6: DATA GENERATOR A/B TESTING (Kịch bản 1)
======================================================
So sánh 5 mô hình sinh dữ liệu thách thức cho Digital Twin.
Mỗi generator chạy native (mã nguồn gốc) → sinh ra file .pkl riêng
→ đánh giá bằng synthcity Metrics.evaluate() + DT-Guard separation.

Pipeline (decoupled):
  PHASE 1: Train + Generate → synthetic_{name}.pkl
  PHASE 2: Evaluate tất cả pkl files bằng synthcity metrics
  PHASE 3: DT-Guard integration test
  PHASE 4: Output tables + ranking

Generators (đề cương §3 Kịch bản 1):
  Nhóm Diffusion:
    1. TabDDPM           (Kotelnikov et al., ICML 2023)  — tab-ddpm native
    2. TabSyn            (Zhang et al., ICLR 2024)       — tabsyn native
    3. ForestDiffusion   (Jolicoeur-Martineau, ICLR 2024)— pip ForestDiffusion
  Nhóm GAN:
    4. CTGAN             (Xu et al., NeurIPS 2019)      — pip ctgan
    5. WGAN-GP           (DT-Guard baseline)            — native

Output files:
  data/synthetic/synthetic_{name}.pkl     — synthetic DataFrames
  results/paper_experiments/exp6_*.pkl    — full results
  results/paper_experiments/exp6_*.json   — summary

Metrics — synthcity Metrics.evaluate():
  Fidelity:    performance.xgb (TSTR), stats.wasserstein_dist, stats.jensenshannon_dist
  Coverage:    sanity.nearest_syn_neighbor_distance (DCR), stats.prdc, stats.alpha_precision
  Detection:   detection.detection_xgb
  Custom:      DT-Guard separation, oracle_label_accuracy, train_time, peak_ram

Requirements:
  pip install synthcity ctgan ForestDiffusion
  ./scripts/setup_generators.sh   (installs pip dependencies)
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import time
import pickle
import traceback
import warnings
import json
from datetime import datetime
from pathlib import Path

from dtguard.config import Config
from dtguard.data import load_data
from dtguard.models import IoTAttackNet
from dtguard.models.ids_model import train_model, evaluate_model

warnings.filterwarnings('ignore')

SEED = 42
N_SYNTHETIC = 10000
N_REAL_SUBSAMPLE = 30000
WGAN_EPOCHS = 300
SYNTHETIC_DIR = Path('data/synthetic')
RESULTS_DIR = Path('results/thesis')

# Generator registry: (name, family, reference, year)
GENERATORS = [
    ("TabDDPM",          "Diffusion", "Kotelnikov et al., ICML 2023",       2023),
    ("TabSyn",           "Diffusion", "Zhang et al., ICLR 2024",            2024),
    ("ForestDiffusion",  "Diffusion", "Jolicoeur-Martineau et al., ICLR 2024", 2024),
    ("CTGAN",            "GAN",       "Xu et al., NeurIPS 2019",            2019),
    ("WGAN-GP",          "GAN",       "Gulrajani et al., NeurIPS 2017",     2017),
]

# Synthcity metrics
EVAL_METRICS = {
    'sanity':      ['nearest_syn_neighbor_distance'],
    'stats':       ['wasserstein_dist', 'jensenshannon_dist', 'prdc', 'alpha_precision'],
    'performance': ['xgb'],
    'detection':   ['detection_xgb'],
}


# ============================================================================
# PHASE 1: Native Generator Implementations
# ============================================================================

def _generate_tabddpm(X_train, y_train, feature_cols, n_syn, device):
    """TabDDPM — Native MLP-based denoising diffusion for tabular data.
    Reference impl: yandex-research/tab-ddpm (ICML 2023).
    Simplified standalone version using same architecture."""
    n_features = X_train.shape[1]
    n_classes = len(np.unique(y_train))

    # Normalize
    X_mean = X_train.mean(axis=0)
    X_std = X_train.std(axis=0) + 1e-8
    X_norm = (X_train - X_mean) / X_std

    # One-hot encode labels
    y_onehot = np.zeros((len(y_train), n_classes), dtype=np.float32)
    for i, c in enumerate(np.unique(y_train)):
        y_onehot[y_train == c, i] = 1.0
    data = np.hstack([X_norm, y_onehot]).astype(np.float32)
    data_dim = data.shape[1]

    # Diffusion hyperparams (matching TabDDPM paper)
    T = 500
    betas = torch.linspace(1e-4, 0.02, T, device=device)
    alphas = 1.0 - betas
    alpha_bars = torch.cumprod(alphas, dim=0)

    # MLP denoiser with time embedding (TabDDPM architecture)
    class TabDDPMDenoiser(nn.Module):
        def __init__(self, d_in, d_hidden=512):
            super().__init__()
            self.time_emb = nn.Sequential(nn.Linear(1, d_hidden), nn.SiLU())
            self.net = nn.Sequential(
                nn.Linear(d_in, d_hidden), nn.SiLU(), nn.Dropout(0.1),
                nn.Linear(d_hidden, d_hidden), nn.SiLU(), nn.Dropout(0.1),
                nn.Linear(d_hidden, d_hidden), nn.SiLU(),
                nn.Linear(d_hidden, d_in),
            )
            self.cond = nn.Linear(d_hidden, d_hidden)

        def forward(self, x_t, t_norm):
            t_emb = self.time_emb(t_norm)
            h = self.net[0](x_t)  # first linear
            h = self.net[1](h)    # SiLU
            h = self.net[2](h)    # Dropout
            h = h + self.cond(t_emb)
            for layer in self.net[3:]:
                h = layer(h)
            return h

    model = TabDDPMDenoiser(data_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    data_t = torch.from_numpy(data).float().to(device)
    dataset = torch.utils.data.TensorDataset(data_t)
    loader = torch.utils.data.DataLoader(dataset, batch_size=256, shuffle=True)

    model.train()
    for epoch in range(200):
        for (batch,) in loader:
            bs = batch.size(0)
            t = torch.randint(0, T, (bs,), device=device)
            noise = torch.randn_like(batch)
            ab = alpha_bars[t].unsqueeze(1)
            x_t = torch.sqrt(ab) * batch + torch.sqrt(1 - ab) * noise
            t_norm = (t.float() / T).unsqueeze(1)
            pred = model(x_t, t_norm)
            loss = nn.functional.mse_loss(pred, noise)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    # Reverse diffusion sampling
    model.eval()
    with torch.no_grad():
        x = torch.randn(n_syn, data_dim, device=device)
        for t_idx in reversed(range(T)):
            t_norm = torch.full((n_syn, 1), t_idx / T, device=device)
            pred_noise = model(x, t_norm)
            alpha = alphas[t_idx]
            alpha_bar = alpha_bars[t_idx]
            x = (x - (1 - alpha) / torch.sqrt(1 - alpha_bar) * pred_noise) / torch.sqrt(alpha)
            if t_idx > 0:
                x += torch.sqrt(betas[t_idx]) * torch.randn_like(x)

    syn = x.cpu().numpy()
    X_syn = (syn[:, :n_features] * X_std + X_mean).astype(np.float32)
    y_logits = syn[:, n_features:]
    classes = np.unique(y_train)
    y_syn = classes[np.argmax(y_logits, axis=1)].astype(np.int64)
    return X_syn, y_syn


def _generate_tabsyn(X_train, y_train, feature_cols, n_syn, device):
    """TabSyn — VAE + Latent Diffusion for tabular data.
    Reference impl: amazon-science/tabsyn (ICLR 2024).
    Two-phase: 1) Train VAE encoder-decoder, 2) Diffusion in latent space."""
    n_features = X_train.shape[1]
    n_classes = len(np.unique(y_train))
    classes = np.unique(y_train)
    latent_dim = 64

    # Normalize
    X_mean = X_train.mean(axis=0)
    X_std = X_train.std(axis=0) + 1e-8
    X_norm = (X_train - X_mean) / X_std

    # One-hot labels
    y_onehot = np.zeros((len(y_train), n_classes), dtype=np.float32)
    for i, c in enumerate(classes):
        y_onehot[y_train == c, i] = 1.0
    data = np.hstack([X_norm, y_onehot]).astype(np.float32)
    data_dim = data.shape[1]
    data_t = torch.from_numpy(data).float().to(device)

    # Phase 1: VAE
    class TabSynVAE(nn.Module):
        def __init__(self):
            super().__init__()
            self.encoder = nn.Sequential(
                nn.Linear(data_dim, 256), nn.ReLU(), nn.Linear(256, 128), nn.ReLU())
            self.fc_mu = nn.Linear(128, latent_dim)
            self.fc_logvar = nn.Linear(128, latent_dim)
            self.decoder = nn.Sequential(
                nn.Linear(latent_dim, 128), nn.ReLU(),
                nn.Linear(128, 256), nn.ReLU(), nn.Linear(256, data_dim))

        def encode(self, x):
            h = self.encoder(x)
            return self.fc_mu(h), self.fc_logvar(h)

        def decode(self, z):
            return self.decoder(z)

        def forward(self, x):
            mu, logvar = self.encode(x)
            std = torch.exp(0.5 * logvar)
            z = mu + std * torch.randn_like(std)
            return self.decode(z), mu, logvar

    vae = TabSynVAE().to(device)
    opt_vae = torch.optim.Adam(vae.parameters(), lr=1e-3)
    ds = torch.utils.data.TensorDataset(data_t)
    dl = torch.utils.data.DataLoader(ds, batch_size=256, shuffle=True)

    vae.train()
    for epoch in range(150):
        for (batch,) in dl:
            recon, mu, logvar = vae(batch)
            recon_loss = nn.functional.mse_loss(recon, batch, reduction='sum')
            kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
            loss = recon_loss + 0.5 * kl_loss
            opt_vae.zero_grad(); loss.backward(); opt_vae.step()

    # Encode all data to latent
    vae.eval()
    with torch.no_grad():
        mu_all, _ = vae.encode(data_t)
        z_all = mu_all  # use mean for stability

    # Phase 2: Diffusion in latent space
    T = 300
    betas = torch.linspace(1e-4, 0.02, T, device=device)
    alphas = 1.0 - betas
    alpha_bars = torch.cumprod(alphas, dim=0)

    denoiser = nn.Sequential(
        nn.Linear(latent_dim + 1, 256), nn.SiLU(),
        nn.Linear(256, 256), nn.SiLU(),
        nn.Linear(256, latent_dim),
    ).to(device)
    opt_diff = torch.optim.Adam(denoiser.parameters(), lr=1e-3)

    z_ds = torch.utils.data.TensorDataset(z_all)
    z_dl = torch.utils.data.DataLoader(z_ds, batch_size=256, shuffle=True)

    denoiser.train()
    for epoch in range(200):
        for (batch,) in z_dl:
            bs = batch.size(0)
            t = torch.randint(0, T, (bs,), device=device)
            noise = torch.randn_like(batch)
            ab = alpha_bars[t].unsqueeze(1)
            z_t = torch.sqrt(ab) * batch + torch.sqrt(1 - ab) * noise
            t_emb = (t.float() / T).unsqueeze(1)
            pred = denoiser(torch.cat([z_t, t_emb], dim=1))
            loss = nn.functional.mse_loss(pred, noise)
            opt_diff.zero_grad(); loss.backward(); opt_diff.step()

    # Sample latent → decode
    denoiser.eval()
    with torch.no_grad():
        z = torch.randn(n_syn, latent_dim, device=device)
        for t_idx in reversed(range(T)):
            t_emb = torch.full((n_syn, 1), t_idx / T, device=device)
            pred_noise = denoiser(torch.cat([z, t_emb], dim=1))
            alpha = alphas[t_idx]; alpha_bar = alpha_bars[t_idx]
            z = (z - (1 - alpha) / torch.sqrt(1 - alpha_bar) * pred_noise) / torch.sqrt(alpha)
            if t_idx > 0:
                z += torch.sqrt(betas[t_idx]) * torch.randn_like(z)
        syn = vae.decode(z).cpu().numpy()

    X_syn = (syn[:, :n_features] * X_std + X_mean).astype(np.float32)
    y_logits = syn[:, n_features:]
    y_syn = classes[np.argmax(y_logits, axis=1)].astype(np.int64)
    return X_syn, y_syn


def _generate_forest_diffusion(X_train, y_train, feature_cols, n_syn, device):
    """ForestDiffusion — Tree-based diffusion (CPU only).
    Reference impl: SamsungSAILMontreal/ForestDiffusion (ICLR 2024).
    Uses pip package directly.

    Complexity: n_t × n_classes XGBoost models (p_in_one=True).
    With 34 classes: n_t=30 → 1020 models.
    label_y provides class-conditional generation."""
    from ForestDiffusion import ForestDiffusionModel

    n_classes = len(np.unique(y_train))
    print(f"\n      [ForestDiffusion] {len(X_train)} samples, {X_train.shape[1]} features, "
          f"{n_classes} classes → ~{30*n_classes} XGBoost models")

    model = ForestDiffusionModel(
        X=X_train.astype(np.float64),
        label_y=y_train.astype(np.int64),
        n_t=30,              # noise levels (default=50)
        n_estimators=50,     # trees per XGBoost (default=100)
        max_depth=6,         # tree depth (default=7)
        duplicate_K=1,       # no data duplication
        seed=SEED,
        n_jobs=-1,           # use all CPUs
    )
    result = model.generate(batch_size=n_syn)
    # generate() returns np.array of shape (n_syn, n_features + 1)
    # Last column is the label assigned by ForestDiffusion (from label_y classes)
    n_f = X_train.shape[1]
    X_syn = result[:, :n_f].astype(np.float32)
    y_raw = result[:, n_f]  # float labels from ForestDiffusion
    # Map to nearest valid class
    classes = np.unique(y_train)
    y_syn = np.array([classes[np.argmin(np.abs(classes - v))] for v in y_raw], dtype=np.int64)
    return X_syn, y_syn


def _generate_ctgan(X_train, y_train, feature_cols, n_syn, device):
    """CTGAN — Conditional GAN for tabular data.
    Reference impl: sdv-dev/CTGAN (NeurIPS 2019). pip install ctgan.
    Label must be treated as discrete column for conditional generation."""
    from ctgan import CTGAN

    df = pd.DataFrame(X_train, columns=feature_cols)
    # Convert label to string to ensure CTGAN treats it as categorical (not continuous)
    df['Label'] = y_train.astype(str)

    model = CTGAN(
        epochs=300, batch_size=500,
        generator_dim=(256, 256, 256), discriminator_dim=(256, 256, 256),
        pac=1,                 # No packing — better for many discrete classes
        verbose=False,
        cuda=(str(device) != 'cpu'),
    )
    model.fit(df, discrete_columns=['Label'])
    syn_df = model.sample(n_syn)
    X_syn = syn_df[feature_cols].values.astype(np.float32)
    # Convert string labels back to int
    y_syn = syn_df['Label'].astype(int).values.astype(np.int64)
    return X_syn, y_syn


def _generate_wgangp(X_train, y_train, feature_cols, n_syn, device):
    """WGAN-GP — Conditional WGAN-GP baseline for tabular data.
    All samples generated purely from latent space (no real data copying).
    Uses class embedding for conditional generation of all 34 classes."""
    n_features = X_train.shape[1]
    classes = np.unique(y_train)
    n_classes = len(classes)
    latent_dim = 100

    # Normalize features
    X_mean = X_train.mean(axis=0)
    X_std = X_train.std(axis=0) + 1e-8
    X_norm = ((X_train - X_mean) / X_std).astype(np.float32)

    # Class-to-index mapping
    class_to_idx = {c: i for i, c in enumerate(classes)}
    y_idx = np.array([class_to_idx[c] for c in y_train], dtype=np.int64)

    # Conditional Generator: z + class_embedding → features
    class CondGenerator(nn.Module):
        def __init__(self):
            super().__init__()
            self.class_emb = nn.Embedding(n_classes, 32)
            self.net = nn.Sequential(
                nn.Linear(latent_dim + 32, 256), nn.LeakyReLU(0.2), nn.BatchNorm1d(256),
                nn.Linear(256, 256), nn.LeakyReLU(0.2), nn.BatchNorm1d(256),
                nn.Linear(256, n_features), nn.Tanh(),
            )
        def forward(self, z, labels):
            emb = self.class_emb(labels)
            return self.net(torch.cat([z, emb], dim=1))

    # Conditional Critic: features + class_embedding → score
    class CondCritic(nn.Module):
        def __init__(self):
            super().__init__()
            self.class_emb = nn.Embedding(n_classes, 32)
            self.net = nn.Sequential(
                nn.Linear(n_features + 32, 256), nn.LeakyReLU(0.2),
                nn.Linear(256, 128), nn.LeakyReLU(0.2),
                nn.Linear(128, 1),
            )
        def forward(self, x, labels):
            emb = self.class_emb(labels)
            return self.net(torch.cat([x, emb], dim=1))

    gen = CondGenerator().to(device)
    crit = CondCritic().to(device)
    opt_g = torch.optim.Adam(gen.parameters(), lr=1e-4, betas=(0.5, 0.9))
    opt_c = torch.optim.Adam(crit.parameters(), lr=1e-4, betas=(0.5, 0.9))

    X_t = torch.FloatTensor(X_norm).to(device)
    y_t = torch.LongTensor(y_idx).to(device)
    n_critic = 5
    gp_lambda = 10.0
    batch_size = min(256, len(X_train))

    # Training loop
    gen.train(); crit.train()
    for epoch in range(WGAN_EPOCHS):
        for _ in range(n_critic):
            idx = torch.randint(0, len(X_t), (batch_size,))
            real_x, real_y = X_t[idx], y_t[idx]
            z = torch.randn(batch_size, latent_dim, device=device)
            fake_x = gen(z, real_y).detach()

            # Gradient penalty
            eps = torch.rand(batch_size, 1, device=device)
            interp = (eps * real_x + (1 - eps) * fake_x).requires_grad_(True)
            d_interp = crit(interp, real_y)
            grads = torch.autograd.grad(d_interp, interp,
                grad_outputs=torch.ones_like(d_interp),
                create_graph=True, retain_graph=True)[0]
            gp = ((grads.norm(2, dim=1) - 1) ** 2).mean()

            c_loss = -(crit(real_x, real_y).mean() - crit(fake_x, real_y).mean()) + gp_lambda * gp
            opt_c.zero_grad(); c_loss.backward(); opt_c.step()

        # Generator step
        z = torch.randn(batch_size, latent_dim, device=device)
        fake_labels = y_t[torch.randint(0, len(y_t), (batch_size,))]
        g_loss = -crit(gen(z, fake_labels), fake_labels).mean()
        opt_g.zero_grad(); g_loss.backward(); opt_g.step()

    # Generate: sample labels from real distribution, generate features
    gen.eval()
    with torch.no_grad():
        # Sample labels proportional to real distribution
        label_probs = np.bincount(y_idx, minlength=n_classes).astype(np.float64)
        label_probs /= label_probs.sum()
        syn_labels_idx = np.random.choice(n_classes, size=n_syn, p=label_probs)
        syn_labels_t = torch.LongTensor(syn_labels_idx).to(device)

        z = torch.randn(n_syn, latent_dim, device=device)
        X_syn_norm = gen(z, syn_labels_t).cpu().numpy()

    # Denormalize
    X_syn = (X_syn_norm * X_std + X_mean).astype(np.float32)
    y_syn = classes[syn_labels_idx].astype(np.int64)
    return X_syn, y_syn


# Registry: name → generator function
GENERATOR_FUNCS = {
    "TabDDPM":         _generate_tabddpm,
    "TabSyn":          _generate_tabsyn,
    "ForestDiffusion": _generate_forest_diffusion,
    "CTGAN":           _generate_ctgan,
    "WGAN-GP":         _generate_wgangp,
}


# ============================================================================
# PHASE 2: Evaluation (synthcity metrics + custom TSTR)
# ============================================================================

def compute_tstr(X_syn, y_syn, X_real_test, y_real_test):
    """Custom TSTR: Train on Synthetic, Test on Real.
    synthcity's performance.xgb often returns 0 for many-class problems.
    We compute it directly with XGBoost."""
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.metrics import accuracy_score

    # Filter: only use classes that exist in both synthetic and real
    syn_classes = set(np.unique(y_syn))
    real_classes = set(np.unique(y_real_test))
    common = syn_classes & real_classes

    if len(common) < 2:
        return 0.0

    # Filter to common classes
    syn_mask = np.isin(y_syn, list(common))
    real_mask = np.isin(y_real_test, list(common))

    X_s, y_s = X_syn[syn_mask], y_syn[syn_mask]
    X_r, y_r = X_real_test[real_mask], y_real_test[real_mask]

    # Subsample for speed
    if len(X_s) > 5000:
        idx = np.random.choice(len(X_s), 5000, replace=False)
        X_s, y_s = X_s[idx], y_s[idx]
    if len(X_r) > 5000:
        idx = np.random.choice(len(X_r), 5000, replace=False)
        X_r, y_r = X_r[idx], y_r[idx]

    clf = GradientBoostingClassifier(
        n_estimators=50, max_depth=4, random_state=SEED,
        subsample=0.8, learning_rate=0.1,
    )
    try:
        clf.fit(X_s, y_s)
        preds = clf.predict(X_r)
        return float(accuracy_score(y_r, preds))
    except Exception:
        return 0.0


def run_synthcity_eval(real_df, syn_df, target_col):
    """Evaluate synthetic data using synthcity Metrics.evaluate()."""
    from synthcity.plugins.core.dataloader import GenericDataLoader
    from synthcity.metrics.eval import Metrics

    X_gt = GenericDataLoader(real_df, target_column=target_col)
    X_syn = GenericDataLoader(syn_df, target_column=target_col)

    score_df = Metrics.evaluate(
        X_gt=X_gt, X_syn=X_syn,
        metrics=EVAL_METRICS,
        task_type='classification',
    )
    results = {}
    for metric_name in score_df.index:
        row = score_df.loc[metric_name]
        mean_val = float(row.get('mean', row.iloc[0])) if 'mean' in row.index else float(row.iloc[0])
        direction = str(row.get('direction', '')) if 'direction' in row.index else ''
        results[metric_name] = {'mean': mean_val, 'direction': direction}
    return results


# ============================================================================
# PHASE 3: DT-Guard Integration + Custom Metrics
# ============================================================================

def compute_oracle_label_accuracy(X_syn, y_syn, oracle_model, device):
    """Oracle Label Accuracy — Conditional Control metric (đề cương §3).

    Measures whether the generator produces samples with correct labels.
    A pre-trained IDS Oracle predicts the label of each synthetic sample;
    if it matches the generator's intended label → conditional control is good.

    Args:
        X_syn: Synthetic features
        y_syn: Generator's intended labels
        oracle_model: Pre-trained IDS model on real data
        device: torch device

    Returns:
        float: Fraction of synthetic samples where Oracle agrees with generator label
    """
    oracle_model.eval()
    oracle_model.to(device)
    X_t = torch.FloatTensor(X_syn).to(device)

    with torch.no_grad():
        preds = oracle_model(X_t).argmax(dim=1).cpu().numpy()

    accuracy = float(np.mean(preds == y_syn))
    return accuracy


def compute_dt_guard_separation(X_syn, y_syn, X_real, y_real,
                                 input_dim, num_classes, device):
    """DT-Guard separation = acc(benign_model) − acc(random_model) on challenge data."""
    X_ch = X_syn[:500]
    y_ch = y_syn[:500]

    # Benign model (trained on real data)
    benign = IoTAttackNet(input_dim, num_classes)
    n = min(5000, len(X_real))
    idx = np.random.choice(len(X_real), n, replace=False)
    train_model(benign, X_real[idx], y_real[idx], epochs=3, batch_size=256, device=device)
    acc_b = evaluate_model(benign, X_ch, y_ch, device=device)

    # Random model (untrained)
    acc_p = evaluate_model(IoTAttackNet(input_dim, num_classes), X_ch, y_ch, device=device)

    return float(acc_b - acc_p)


# ============================================================================
# Main
# ============================================================================

def main():
    start = datetime.now()
    print("=" * 100)
    print("  EXPERIMENT 6: DATA GENERATOR A/B TESTING (Kịch bản 1)")
    print("  Native implementations — decoupled pipeline")
    print("=" * 100)
    print(f"  Start: {start.strftime('%Y-%m-%d %H:%M:%S')}")

    np.random.seed(SEED)
    torch.manual_seed(SEED)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"  Device: {device}")

    SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ---- Load data ----
    cfg = Config(dataset_dir="data/CICIoT2023")
    train_df, test_df, feature_cols = load_data(cfg)
    target_col = 'Label'
    input_dim = len(feature_cols)
    num_classes = len(np.unique(test_df[target_col]))

    # Subsample for speed
    if len(train_df) > N_REAL_SUBSAMPLE:
        real_df = train_df.sample(n=N_REAL_SUBSAMPLE, random_state=SEED).reset_index(drop=True)
    else:
        real_df = train_df.copy()
    real_df = real_df[feature_cols + [target_col]].copy()

    X_real = real_df[feature_cols].values.astype(np.float32)
    y_real = real_df[target_col].values.astype(np.int64)

    print(f"  Data: {input_dim} features, {num_classes} classes")
    print(f"  Real subsample: {len(real_df)}, Test: {len(test_df)}")
    print(f"  Generators: {[g[0] for g in GENERATORS]}")
    print(f"  Output dir: {SYNTHETIC_DIR}/\n")

    # ---- Pre-train IDS Oracle for Label Accuracy metric ----
    print("  Pre-training IDS Oracle for Conditional Control metric...", end=" ", flush=True)
    t0 = time.time()
    oracle_model = IoTAttackNet(input_dim, num_classes)
    train_model(oracle_model, X_real, y_real, epochs=10, batch_size=256, device=device)
    oracle_acc = evaluate_model(oracle_model,
                                test_df[feature_cols].values.astype(np.float32),
                                test_df['Label'].values.astype(np.int64),
                                device=device)
    print(f"done ({time.time()-t0:.1f}s, Oracle test acc={oracle_acc:.4f})")

    # ---- Compute TRTR baseline (Train on Real, Test on Real) ----
    print("  Computing TRTR baseline...", end=" ", flush=True)
    X_test_sub = test_df[feature_cols].values.astype(np.float32)[:5000]
    y_test_sub = test_df['Label'].values.astype(np.int64)[:5000]
    trtr = compute_tstr(X_real, y_real, X_test_sub, y_test_sub)
    print(f"TRTR = {trtr:.4f}")

    # RAM tracking helper (tracemalloc — accurate peak memory for Python objects)
    import tracemalloc

    def start_ram_tracking():
        tracemalloc.start()

    def stop_ram_tracking_mb():
        """Return peak RAM usage in MB since start_ram_tracking()."""
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return peak / (1024 * 1024)

    # ==================================================================
    # PHASE 1: Train + Generate → .pkl files
    # ==================================================================
    print("=" * 100)
    print("  PHASE 1: TRAIN & GENERATE SYNTHETIC DATA")
    print("=" * 100)

    gen_meta = {}  # name → {train_time, gen_time, pkl_path, n_samples}

    for idx, (name, family, ref, year) in enumerate(GENERATORS, 1):
        pkl_path = SYNTHETIC_DIR / f'synthetic_{name.lower().replace("-","_")}.pkl'
        print(f"\n  [{idx}/{len(GENERATORS)}] {name}  ({family} — {ref})")

        gen_func = GENERATOR_FUNCS.get(name)
        if gen_func is None:
            print(f"    ❌ No implementation found")
            continue

        try:
            print(f"    Training + generating {N_SYNTHETIC} samples...", end=" ", flush=True)
            start_ram_tracking()
            t0 = time.time()
            X_syn, y_syn = gen_func(X_real, y_real, feature_cols, N_SYNTHETIC, device)
            total_time = time.time() - t0
            peak_ram = stop_ram_tracking_mb()

            # Build DataFrame and save as pkl
            syn_df = pd.DataFrame(X_syn, columns=feature_cols)
            syn_df[target_col] = y_syn

            syn_df.to_pickle(pkl_path)
            print(f"done ({total_time:.1f}s, RAM peak={peak_ram:.1f}MB) → {pkl_path.name}")
            print(f"    Shape: {syn_df.shape}, Labels: {np.unique(y_syn)[:5]}...")

            gen_meta[name] = {
                'family': family, 'ref': ref, 'year': year,
                'train_gen_time': total_time,
                'peak_ram_mb': peak_ram,
                'pkl_path': str(pkl_path),
                'n_samples': len(syn_df),
            }

        except Exception:
            print(f"    ❌ FAILED")
            traceback.print_exc()
            gen_meta[name] = None

    # ==================================================================
    # PHASE 2: Evaluate all .pkl files with synthcity metrics
    # ==================================================================
    print("\n" + "=" * 100)
    print("  PHASE 2: EVALUATE WITH SYNTHCITY METRICS")
    print("=" * 100)

    all_results = {}

    for name, family, ref, year in GENERATORS:
        if gen_meta.get(name) is None:
            all_results[name] = None
            continue

        pkl_path = Path(gen_meta[name]['pkl_path'])
        print(f"\n  Evaluating {name} from {pkl_path.name}...", end=" ", flush=True)

        try:
            syn_df = pd.read_pickle(pkl_path)

            t0 = time.time()
            sc_scores = run_synthcity_eval(real_df, syn_df, target_col)
            eval_time = time.time() - t0
            print(f"done ({eval_time:.1f}s)")

            for k, v in sc_scores.items():
                print(f"    {k}: {v['mean']:.4f}  ({v['direction']})")

            # DT-Guard separation
            print(f"    DT-Guard separation...", end=" ", flush=True)
            X_syn = syn_df[feature_cols].values.astype(np.float32)
            y_syn = syn_df[target_col].values.astype(np.int64)
            dt_sep = compute_dt_guard_separation(
                X_syn, y_syn, X_real, y_real, input_dim, num_classes, device)
            print(f"{dt_sep:.4f}")

            # Oracle Label Accuracy (Conditional Control)
            print(f"    Oracle label accuracy...", end=" ", flush=True)
            oracle_acc_syn = compute_oracle_label_accuracy(
                X_syn, y_syn, oracle_model, device)
            print(f"{oracle_acc_syn:.4f}")

            # Custom TSTR (synthcity's xgb often fails with many classes)
            print(f"    Custom TSTR...", end=" ", flush=True)
            tstr_score = compute_tstr(X_syn, y_syn, X_test_sub, y_test_sub)
            print(f"{tstr_score:.4f}  (TRTR={trtr:.4f})")

            all_results[name] = {
                **gen_meta[name],
                'synthcity': sc_scores,
                'dt_guard_separation': dt_sep,
                'oracle_label_accuracy': oracle_acc_syn,
                'custom_tstr': tstr_score,
                'eval_time': eval_time,
            }

        except Exception:
            print(f"FAILED")
            traceback.print_exc()
            all_results[name] = None

    # ==================================================================
    # PHASE 4: Output Tables
    # ==================================================================
    valid = [g[0] for g in GENERATORS if all_results.get(g[0]) is not None]
    if not valid:
        print("\n  ❌ No generators succeeded.")
        return

    # Map display keys → synthcity compound keys (pick the most representative sub-metric)
    _METRIC_MAP = {
        'wasserstein':    'stats.wasserstein_dist.joint',
        'jensenshannon':  'stats.jensenshannon_dist.marginal',
        'dcr':            'sanity.nearest_syn_neighbor_distance.mean',
        'precision':      'stats.prdc.precision',
        'recall':         'stats.prdc.recall',
        'density':        'stats.prdc.density',
        'coverage':       'stats.prdc.coverage',
        'alpha_prec':     'stats.alpha_precision.delta_precision_alpha_OC',
        'authenticity':   'stats.alpha_precision.authenticity_OC',
        'tstr_gt':        'performance.xgb.gt',
        'tstr_syn_id':    'performance.xgb.syn_id',
        'tstr_syn_ood':   'performance.xgb.syn_ood',
        'detection':      'detection.detection_xgb.mean',
    }

    def _get(name, key):
        r = all_results[name]
        if key in ('dt_guard_separation', 'train_gen_time', 'eval_time',
                    'oracle_label_accuracy', 'peak_ram_mb', 'custom_tstr'):
            return r.get(key)
        sc = r.get('synthcity', {})
        # Direct match
        if key in sc:
            return sc[key]['mean']
        # Try mapped key
        mapped = _METRIC_MAP.get(key)
        if mapped and mapped in sc:
            return sc[mapped]['mean']
        # Substring search (fallback)
        for k, v in sc.items():
            if key in k:
                return v['mean']
        return None

    # ---- TABLE 1: FIDELITY ----
    print("\n" + "=" * 105)
    print("  TABLE 1: FIDELITY (Độ trung thực)")
    print("=" * 105)
    t1 = [('custom_tstr', 'TSTR↑'), ('wasserstein', 'Wasserstein↓'),
          ('jensenshannon', 'JSD↓')]
    hdr = f"  {'Generator':<18} {'Family':<10} {'Year':<6}"
    for _, label in t1:
        hdr += f" {label:>18}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for n in valid:
        r = all_results[n]
        row = f"  {n:<18} {r['family']:<10} {r['year']:<6}"
        for key, _ in t1:
            v = _get(n, key)
            row += f" {v:>17.4f}" if v is not None else f" {'N/A':>17}"
        print(row)

    # ---- TABLE 2: COVERAGE & DIVERSITY ----
    print("\n" + "=" * 105)
    print("  TABLE 2: COVERAGE & DIVERSITY (Độ bao phủ)")
    print("=" * 105)
    t2 = [('dcr', 'DCR↓'), ('precision', 'Precision↑'),
          ('recall', 'Recall↑'), ('coverage', 'Coverage↑'), ('authenticity', 'Authentic↑')]
    hdr = f"  {'Generator':<18} {'Family':<10}"
    for _, label in t2:
        hdr += f" {label:>18}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for n in valid:
        r = all_results[n]
        row = f"  {n:<18} {r['family']:<10}"
        for key, _ in t2:
            v = _get(n, key)
            row += f" {v:>17.4f}" if v is not None else f" {'N/A':>17}"
        print(row)

    # ---- TABLE 3: COST & DT-GUARD ----
    print("\n" + "=" * 115)
    print("  TABLE 3: CHI PHÍ, CONDITIONAL CONTROL & TÍCH HỢP DT-GUARD")
    print("=" * 115)
    print(f"  {'Generator':<18} {'Family':<10} {'Time(s)↓':>10} {'RAM(MB)↓':>10} "
          f"{'OracleAcc↑':>12} {'DT-Sep↑':>10}")
    print("  " + "-" * 72)
    for n in valid:
        r = all_results[n]
        ram = r.get('peak_ram_mb', 0.0)
        oracle = r.get('oracle_label_accuracy', 0.0)
        print(f"  {n:<18} {r['family']:<10} {r['train_gen_time']:>9.1f}s {ram:>9.1f} "
              f"{oracle:>11.4f} {r['dt_guard_separation']:>9.4f}")

    # ---- COMPOSITE RANKING ----
    print("\n" + "=" * 105)
    print("  COMPOSITE RANKING")
    print("=" * 105)

    if len(valid) >= 2:
        # Higher is better
        high_keys = ['custom_tstr', 'precision', 'recall', 'coverage', 'authenticity',
                     'dt_guard_separation', 'oracle_label_accuracy']
        # Lower is better (detection removed — returns 1.0 for all, no discrimination)
        low_keys = ['wasserstein', 'jensenshannon', 'dcr',
                    'train_gen_time', 'peak_ram_mb']

        scores = {n: 0.0 for n in valid}
        for key in high_keys:
            vals = [(n, _get(n, key)) for n in valid if _get(n, key) is not None]
            if len(vals) < 2: continue
            vmin, vmax = min(v for _, v in vals), max(v for _, v in vals)
            rng = max(vmax - vmin, 1e-10)
            for n, v in vals:
                scores[n] += (v - vmin) / rng

        for key in low_keys:
            vals = [(n, _get(n, key)) for n in valid if _get(n, key) is not None]
            if len(vals) < 2: continue
            vmin, vmax = min(v for _, v in vals), max(v for _, v in vals)
            rng = max(vmax - vmin, 1e-10)
            for n, v in vals:
                scores[n] += 1.0 - (v - vmin) / rng

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        print(f"  {'Rank':<6} {'Generator':<18} {'Family':<10} {'Year':<6} {'Score':>10}")
        print("  " + "-" * 52)
        for rank, (n, score) in enumerate(ranked, 1):
            r = all_results[n]
            marker = " ★ RECOMMENDED" if rank == 1 else ""
            print(f"  {rank:<6} {n:<18} {r['family']:<10} {r['year']:<6} {score:>9.3f}{marker}")

    # ---- Save results ----
    # Full results as pkl (consistent with other experiments)
    with open(RESULTS_DIR / 'exp6_datagen.pkl', 'wb') as f:
        pickle.dump({
            'results': all_results,
            'config': {
                'n_synthetic': N_SYNTHETIC,
                'n_real_subsample': N_REAL_SUBSAMPLE,
                'generators': GENERATORS,
                'eval_metrics': EVAL_METRICS,
                'seed': SEED,
            },
        }, f)

    # Summary as json
    summary = {}
    for n in valid:
        r = all_results[n]
        flat = {
            'family': r['family'], 'year': r['year'], 'ref': r['ref'],
            'train_gen_time': r['train_gen_time'],
            'peak_ram_mb': r.get('peak_ram_mb', 0.0),
            'dt_guard_separation': r['dt_guard_separation'],
            'oracle_label_accuracy': r.get('oracle_label_accuracy', 0.0),
            'custom_tstr': r.get('custom_tstr', 0.0),
            'trtr_baseline': trtr,
        }
        for k, v in r['synthcity'].items():
            flat[k] = v['mean']
            flat[f"{k}_direction"] = v['direction']
        summary[n] = flat
    with open(RESULTS_DIR / 'exp6_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    elapsed = datetime.now() - start
    print(f"\n  ✅ Experiment 6 done in {elapsed}")
    print(f"     Synthetic data: {SYNTHETIC_DIR}/synthetic_*.pkl")
    print(f"     Full results:   {RESULTS_DIR / 'exp6_datagen.pkl'}")
    print(f"     Summary:        {RESULTS_DIR / 'exp6_summary.json'}")


if __name__ == "__main__":
    main()























































