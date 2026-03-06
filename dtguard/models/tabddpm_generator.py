"""TabDDPM-based challenge set generator for Digital Twin verification.

Replaces GANGenerator as the data generator for DT-Guard.
TabDDPM (Kotelnikov et al., ICML 2023) is a denoising diffusion model
specifically designed for tabular data.

Interface compatible with GANGenerator.generate_challenge_set().
"""

import torch
import torch.nn as nn
import numpy as np


class TabDDPMChallengeGenerator:
    """TabDDPM-based challenge set generator.

    Trains a denoising diffusion model on client data (features + labels),
    then generates challenge sets with binary labels (0=benign, 1=attack)
    for Digital Twin verification.
    """

    def __init__(self, input_dim, n_classes, latent_dim=None,
                 T=500, d_hidden=512, n_epochs=200, batch_size=256, lr=1e-3):
        """
        Args:
            input_dim: Number of features (e.g. 39)
            n_classes: Number of classes in dataset (e.g. 34)
            T: Number of diffusion timesteps
            d_hidden: Hidden dimension of denoiser MLP
            n_epochs: Training epochs
            batch_size: Training batch size
            lr: Learning rate
        """
        self.input_dim = input_dim
        self.n_classes = n_classes
        self.T = T
        self.d_hidden = d_hidden
        self.n_epochs = n_epochs
        self.batch_size = batch_size
        self.lr = lr

        # Store real data for challenge set mixing
        self.real_attacks = None    # np.array of attack features
        self.real_benign = None     # np.array of benign features

        # Normalization parameters
        self.X_mean = None
        self.X_std = None
        self.classes = None

        # Model (initialized during training)
        self.model = None
        self.betas = None
        self.alphas = None
        self.alpha_bars = None
        self._trained = False

    def _build_denoiser(self, data_dim, device):
        """Build TabDDPM denoiser network."""

        class TabDDPMDenoiser(nn.Module):
            def __init__(self, d_in, d_hidden):
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
                h = self.net[0](x_t)
                h = self.net[1](h)
                h = self.net[2](h)
                h = h + self.cond(t_emb)
                for layer in self.net[3:]:
                    h = layer(h)
                return h

        return TabDDPMDenoiser(data_dim, self.d_hidden).to(device)

    def train_gan(self, X_train_list, y_train_list, epochs=None, device='cpu'):
        """Train TabDDPM on client data.

        Interface compatible with GANGenerator.train_gan().

        Args:
            X_train_list: List of training data arrays from clients, or single array
            y_train_list: List of label arrays from clients, or single array
            epochs: Override n_epochs if provided
            device: torch device
        """
        if epochs is not None:
            self.n_epochs = epochs

        device = torch.device(device) if isinstance(device, str) else device

        # Aggregate data from all clients
        if isinstance(X_train_list, list):
            X_train = np.vstack(X_train_list)
            y_train = np.concatenate(y_train_list)
        else:
            X_train = X_train_list
            y_train = y_train_list

        # Store real data for challenge set generation
        attack_mask = y_train > 0
        benign_mask = y_train == 0
        self.real_attacks = X_train[attack_mask].astype(np.float32)
        self.real_benign = X_train[benign_mask].astype(np.float32)

        if len(self.real_attacks) == 0:
            self._trained = False
            return

        # Normalize features
        self.X_mean = X_train.mean(axis=0).astype(np.float32)
        self.X_std = X_train.std(axis=0).astype(np.float32) + 1e-8
        X_norm = ((X_train - self.X_mean) / self.X_std).astype(np.float32)

        # One-hot encode labels
        self.classes = np.unique(y_train)
        n_cls = len(self.classes)
        y_onehot = np.zeros((len(y_train), n_cls), dtype=np.float32)
        for i, c in enumerate(self.classes):
            y_onehot[y_train == c, i] = 1.0

        data = np.hstack([X_norm, y_onehot]).astype(np.float32)
        data_dim = data.shape[1]

        # Diffusion schedule
        self.betas = torch.linspace(1e-4, 0.02, self.T, device=device)
        self.alphas = 1.0 - self.betas
        self.alpha_bars = torch.cumprod(self.alphas, dim=0)

        # Build and train denoiser
        self.model = self._build_denoiser(data_dim, device)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        data_t = torch.from_numpy(data).float().to(device)
        dataset = torch.utils.data.TensorDataset(data_t)
        loader = torch.utils.data.DataLoader(
            dataset, batch_size=self.batch_size, shuffle=True,
            drop_last=False, pin_memory=False)

        self.model.train()
        for epoch in range(self.n_epochs):
            for (batch,) in loader:
                bs = batch.size(0)
                t = torch.randint(0, self.T, (bs,), device=device)
                noise = torch.randn_like(batch)
                ab = self.alpha_bars[t].unsqueeze(1)
                x_t = torch.sqrt(ab) * batch + torch.sqrt(1 - ab) * noise
                t_norm = (t.float() / self.T).unsqueeze(1)
                pred = self.model(x_t, t_norm)
                loss = nn.functional.mse_loss(pred, noise)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        self._device = device
        self._data_dim = data_dim
        self._trained = True

        # Pre-generate challenge pool to avoid slow diffusion at inference time
        self._pregenerate_pool(device, pool_size=2000)

    def _pregenerate_pool(self, device, pool_size=2000):
        """Pre-generate a pool of synthetic samples for fast challenge set creation."""
        syn = self._sample_diffusion(pool_size, device)
        X_syn = (syn[:, :self.input_dim] * self.X_std + self.X_mean).astype(np.float32)
        y_logits = syn[:, self.input_dim:]
        y_syn = self.classes[np.argmax(y_logits, axis=1)]

        # Split into benign and attack pools
        benign_mask = y_syn == 0
        attack_mask = y_syn > 0
        self._syn_benign_pool = X_syn[benign_mask]
        self._syn_attack_pool = X_syn[attack_mask]

    def _sample_diffusion(self, n_samples, device):
        """Run reverse diffusion to generate synthetic samples."""
        self.model.eval()
        with torch.no_grad():
            x = torch.randn(n_samples, self._data_dim, device=device)
            for t_idx in reversed(range(self.T)):
                t_norm = torch.full((n_samples, 1), t_idx / self.T, device=device)
                pred_noise = self.model(x, t_norm)
                alpha = self.alphas[t_idx]
                alpha_bar = self.alpha_bars[t_idx]
                x = (x - (1 - alpha) / torch.sqrt(1 - alpha_bar) * pred_noise) / torch.sqrt(alpha)
                if t_idx > 0:
                    x += torch.sqrt(self.betas[t_idx]) * torch.randn_like(x)
        return x.cpu().numpy()

    def generate_challenge_set(self, n_samples=500, device='cpu', rng=None, attack_ratio=0.5):
        """Generate challenge set for Digital Twin verification.

        Returns binary-labeled data: 0=benign, 1=attack.
        Uses TabDDPM to generate synthetic samples mixed with real data.

        Args:
            n_samples: Total number of samples
            device: torch device
            rng: numpy random generator for reproducibility
            attack_ratio: Fraction of attack samples (default 0.5)

        Returns:
            (X_challenge, y_challenge): features and binary labels
        """
        rng = rng or np.random.default_rng()
        device = torch.device(device) if isinstance(device, str) else device

        n_attack = int(n_samples * attack_ratio)
        n_benign = n_samples - n_attack

        if self._trained:
            # Use pre-generated synthetic pool (fast — no diffusion at inference)
            syn_benign = self._syn_benign_pool
            syn_attack = self._syn_attack_pool

            # --- Assemble attack portion ---
            # Mix: 50% TabDDPM synthetic attacks + 50% real attacks
            n_syn_attack = min(n_attack // 2, len(syn_attack)) if len(syn_attack) > 0 else 0
            n_real_attack = n_attack - n_syn_attack

            attack_parts = []
            if n_syn_attack > 0 and len(syn_attack) > 0:
                idx = rng.choice(len(syn_attack), n_syn_attack, replace=True)
                attack_parts.append(syn_attack[idx])

            if self.real_attacks is not None and len(self.real_attacks) > 0:
                idx = rng.choice(len(self.real_attacks), n_real_attack, replace=True)
                attack_parts.append(self.real_attacks[idx])
            elif n_real_attack > 0:
                attack_parts.append(rng.standard_normal(
                    (n_real_attack, self.input_dim)).astype(np.float32))

            attack_samples = np.vstack(attack_parts) if attack_parts else \
                rng.standard_normal((n_attack, self.input_dim)).astype(np.float32)

            # --- Assemble benign portion ---
            # Mix: 50% TabDDPM synthetic benign + 50% real benign
            n_syn_benign = min(n_benign // 2, len(syn_benign))
            n_real_benign = n_benign - n_syn_benign

            benign_parts = []
            if n_syn_benign > 0 and len(syn_benign) > 0:
                idx = rng.choice(len(syn_benign), n_syn_benign, replace=True)
                benign_parts.append(syn_benign[idx])

            if self.real_benign is not None and len(self.real_benign) > 0:
                idx = rng.choice(len(self.real_benign), n_real_benign, replace=True)
                benign_parts.append(self.real_benign[idx])
            elif n_real_benign > 0:
                benign_parts.append(rng.standard_normal(
                    (n_real_benign, self.input_dim)).astype(np.float32))

            benign_samples = np.vstack(benign_parts) if benign_parts else \
                rng.standard_normal((n_benign, self.input_dim)).astype(np.float32)

        else:
            # Fallback: use real data only (same as GANGenerator fallback)
            if self.real_attacks is not None and len(self.real_attacks) > 0:
                idx = rng.choice(len(self.real_attacks), n_attack, replace=True)
                attack_samples = self.real_attacks[idx]
            else:
                attack_samples = rng.standard_normal(
                    (n_attack, self.input_dim)).astype(np.float32)

            if self.real_benign is not None and len(self.real_benign) > 0:
                idx = rng.choice(len(self.real_benign), n_benign, replace=True)
                benign_samples = self.real_benign[idx]
            else:
                benign_samples = rng.standard_normal(
                    (n_benign, self.input_dim)).astype(np.float32)

        # Combine
        X_challenge = np.vstack([attack_samples, benign_samples]).astype(np.float32)
        y_challenge = np.concatenate([
            np.ones(n_attack, dtype=np.int64),    # Attacks = 1
            np.zeros(n_benign, dtype=np.int64)    # Benign = 0
        ])

        return X_challenge, y_challenge

