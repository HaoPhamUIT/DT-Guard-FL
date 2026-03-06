"""Personalized Federated Learning Model for IoT IDS."""

import torch
import torch.nn as nn
import torch.nn.functional as F


class PersonalizedIoTModel(nn.Module):
    """
    Personalized FL model with:
    - Base layers: Shared across clients (uploaded to server)
    - Personal layers: Client-specific (kept local)
    """
    
    def __init__(self, input_size: int, num_classes: int):
        super().__init__()
        
        # Base layers (SHARED - upload to server)
        self.base = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
        # Personal layers (LOCAL - keep on client)
        self.personal = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes)
        )
    
    def forward(self, x):
        """Forward pass through base + personal layers."""
        features = self.base(x)
        return self.personal(features)
    
    def get_base_weights(self):
        """Extract only base layer weights for upload."""
        return {k: v.cpu().detach().numpy() 
                for k, v in self.base.state_dict().items()}
    
    def set_base_weights(self, weights):
        """Update only base layers from global model."""
        state_dict = {k: torch.tensor(v) for k, v in weights.items()}
        self.base.load_state_dict(state_dict, strict=True)
    
    def get_personal_weights(self):
        """Extract personal layer weights (for local storage)."""
        return {k: v.cpu().detach().numpy() 
                for k, v in self.personal.state_dict().items()}
    
    def set_personal_weights(self, weights):
        """Restore personal layers."""
        state_dict = {k: torch.tensor(v) for k, v in weights.items()}
        self.personal.load_state_dict(state_dict, strict=True)
