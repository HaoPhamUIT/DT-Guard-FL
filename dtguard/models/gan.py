"""WGAN-GP based challenge set generator."""

import torch
import torch.nn as nn
import torch.autograd as autograd
import numpy as np


class Generator(nn.Module):
    """Generator network for WGAN-GP."""
    
    def __init__(self, latent_dim=100, output_dim=86):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(256),
            nn.Linear(256, 128),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(128),
            nn.Linear(128, output_dim),
            nn.Tanh()
        )
    
    def forward(self, z):
        return self.model(z)


class Critic(nn.Module):
    """Critic network for WGAN-GP (replaces discriminator)."""
    
    def __init__(self, input_dim=86):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.LeakyReLU(0.2),
            nn.Linear(128, 64),
            nn.LeakyReLU(0.2),
            nn.Linear(64, 1)
        )
    
    def forward(self, x):
        return self.model(x)


class GANGenerator(nn.Module):
    """Lightweight GAN to generate attack challenge samples."""

    def __init__(self, latent_dim=100, output_dim=86):
        super().__init__()
        self.latent_dim = latent_dim
        self.output_dim = output_dim
        
        self.generator = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(256),
            nn.Linear(256, 128),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(128),
            nn.Linear(128, output_dim),
            nn.Tanh()
        )

        self.discriminator = nn.Sequential(
            nn.Linear(output_dim, 128),
            nn.LeakyReLU(0.2),
            nn.Linear(128, 64),
            nn.LeakyReLU(0.2),
            nn.Linear(64, 1)
        )

        self.real_attacks = None
        self.real_benign = None

    def forward(self, z):
        return self.generator(z)

    def _critic(self, x):
        return self.discriminator(x)

    def _gradient_penalty(self, real, fake, device):
        batch_size = real.size(0)
        eps = torch.rand(batch_size, 1, device=device)
        eps = eps.expand_as(real)
        interpolates = eps * real + (1 - eps) * fake
        interpolates.requires_grad_(True)
        d_interpolates = self._critic(interpolates)
        grads = torch.autograd.grad(
            outputs=d_interpolates,
            inputs=interpolates,
            grad_outputs=torch.ones_like(d_interpolates),
            create_graph=True,
            retain_graph=True,
            only_inputs=True
        )[0]
        grads = grads.view(batch_size, -1)
        return ((grads.norm(2, dim=1) - 1) ** 2).mean()

    def train_gan(self, X_train_list, y_train_list, epochs=30, device='cpu'):
        """Train GAN on aggregated data from multiple clients.

        Args:
            X_train_list: List of training data from each client OR single array
            y_train_list: List of labels from each client OR single array
        """
        self.to(device)
        
        # Handle both single client and multiple clients
        if isinstance(X_train_list, list):
            # Aggregate data from all clients
            X_train = np.vstack(X_train_list)
            y_train = np.concatenate(y_train_list)
        else:
            X_train = X_train_list
            y_train = y_train_list
        
        # Store real attack AND benign samples
        attack_mask = y_train > 0
        benign_mask = y_train == 0
        
        self.real_attacks = X_train[attack_mask]
        self.real_benign = X_train[benign_mask]
        
        if len(self.real_attacks) == 0:
            return
        
        real_attacks = torch.FloatTensor(self.real_attacks).to(device)
        optimizer_g = torch.optim.Adam(self.generator.parameters(), lr=0.0001, betas=(0.5, 0.9))
        optimizer_d = torch.optim.Adam(self.discriminator.parameters(), lr=0.0001, betas=(0.5, 0.9))

        n_critic = 5
        gp_lambda = 10.0

        for epoch in range(epochs):
            batch_size = min(64, len(real_attacks))
            for _ in range(n_critic):
                indices = torch.randint(0, len(real_attacks), (batch_size,))
                real_batch = real_attacks[indices]

                z = torch.randn(batch_size, self.latent_dim, device=device)
                fake_batch = self.forward(z).detach()

                d_real = self._critic(real_batch)
                d_fake = self._critic(fake_batch)
                gp = self._gradient_penalty(real_batch, fake_batch, device)

                d_loss = -(torch.mean(d_real) - torch.mean(d_fake)) + gp_lambda * gp

                optimizer_d.zero_grad()
                d_loss.backward()
                optimizer_d.step()

            z = torch.randn(batch_size, self.latent_dim, device=device)
            fake_batch = self.forward(z)
            g_loss = -torch.mean(self._critic(fake_batch))

            optimizer_g.zero_grad()
            g_loss.backward()
            optimizer_g.step()

    def generate_challenge_set(self, n_samples=500, device='cpu', rng=None, attack_ratio=0.5):
        """Generate challenge set with configurable attack ratio.
        
        Args:
            n_samples: Total samples
            device: Device
            rng: Random generator
            attack_ratio: Ratio of attacks (0.5 = balanced for testing both DR and FPR)
        """
        self.eval()

        rng = rng or np.random.default_rng()

        with torch.no_grad():
            n_attack = int(n_samples * attack_ratio)
            n_benign = n_samples - n_attack

            # Generate fake attacks (25% of attacks)
            n_fake_attack = n_attack // 4
            z = torch.randn(n_fake_attack, self.latent_dim, device=device)
            fake_attacks = self.forward(z).cpu().numpy()

            # Sample real attacks (75% of attacks)
            n_real_attack = n_attack - n_fake_attack
            if self.real_attacks is not None and len(self.real_attacks) > 0:
                indices = rng.choice(len(self.real_attacks), n_real_attack, replace=True)
                real_attacks = self.real_attacks[indices]
            else:
                real_attacks = rng.standard_normal((n_real_attack, self.output_dim))

            # Sample real benign
            if self.real_benign is not None and len(self.real_benign) > 0:
                indices = rng.choice(len(self.real_benign), n_benign, replace=True)
                benign_samples = self.real_benign[indices]
            else:
                benign_samples = rng.standard_normal((n_benign, self.output_dim))

            # Combine: [attacks, benign]
            X_challenge = np.vstack([fake_attacks, real_attacks, benign_samples]).astype(np.float32)
            y_challenge = np.concatenate([
                np.ones(n_attack, dtype=np.int64),   # Attacks = 1
                np.zeros(n_benign, dtype=np.int64)   # Benign = 0
            ])

        return X_challenge, y_challenge
