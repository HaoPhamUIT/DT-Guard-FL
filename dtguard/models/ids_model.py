"""IoT Attack Detection Neural Network."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import numpy as np


class FocalLoss(nn.Module):
    """Focal Loss for handling class imbalance."""
    def __init__(self, alpha=0.25, gamma=2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
    
    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        return focal_loss.mean()


class IoTAttackNet(nn.Module):
    """Multi-class IoT attack detection model.

    Architecture: 256→128→64→num_classes with BatchNorm and Dropout.
    Centralized accuracy ceiling: ~77% on CIC-IoT-2023 (34 classes).
    Previous small model (128→64→32) saturated at ~71%.
    """

    def __init__(self, input_size: int, num_classes: int):
        super().__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.bn1 = nn.BatchNorm1d(256)
        self.fc2 = nn.Linear(256, 128)
        self.bn2 = nn.BatchNorm1d(128)
        self.fc3 = nn.Linear(128, 64)
        self.bn3 = nn.BatchNorm1d(64)
        self.fc4 = nn.Linear(64, num_classes)
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = F.relu(self.bn1(self.fc1(x)))
        x = self.dropout(x)
        x = F.relu(self.bn2(self.fc2(x)))
        x = self.dropout(x)
        x = F.relu(self.bn3(self.fc3(x)))
        return self.fc4(x)


def train_model(model, X_train, y_train, epochs=3, batch_size=256, lr=0.001, device='cpu'):
    """Train model on local data with class balancing."""
    model.train()
    model.to(device)

    # Pre-convert to tensors once (avoid repeated conversion)
    if isinstance(X_train, np.ndarray):
        X_t = torch.from_numpy(X_train).float()
        y_t = torch.from_numpy(y_train).long()
    else:
        X_t = torch.FloatTensor(X_train)
        y_t = torch.LongTensor(y_train)

    dataset = TensorDataset(X_t, y_t)

    # Adjust batch size for small datasets (need at least 2 for BatchNorm)
    n_samples = len(dataset)
    if n_samples < 2:
        # Not enough data for training with BatchNorm
        return 0.0

    effective_batch_size = min(batch_size, max(2, n_samples // 2))
    drop_last = n_samples >= effective_batch_size * 2

    loader = DataLoader(dataset, batch_size=effective_batch_size, shuffle=True,
                        num_workers=0, pin_memory=(str(device).startswith('cuda')),
                        drop_last=drop_last)

    # Calculate class weights
    num_classes = model.fc4.out_features
    unique_classes, class_counts = np.unique(y_train, return_counts=True)
    class_weights = torch.ones(num_classes, device=device)
    total_samples = len(y_train)
    for cls, count in zip(unique_classes, class_counts):
        class_weights[cls] = total_samples / (len(unique_classes) * count)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    total_loss = 0.0
    num_batches = 0

    for epoch in range(epochs):
        for data, target in loader:
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            num_batches += 1

    return total_loss / num_batches if num_batches > 0 else 0.0


def evaluate_model(model, X_test, y_test, batch_size=1024, device='cpu'):
    """Evaluate model accuracy."""
    model.eval()
    model.to(device)

    if isinstance(X_test, np.ndarray):
        X_t = torch.from_numpy(X_test).float()
        y_t = torch.from_numpy(y_test).long()
    else:
        X_t = torch.FloatTensor(X_test)
        y_t = torch.LongTensor(y_test)

    dataset = TensorDataset(X_t, y_t)
    loader = DataLoader(dataset, batch_size=batch_size, num_workers=0)

    correct = 0
    total = 0

    with torch.no_grad():
        for data, target in loader:
            data, target = data.to(device), target.to(device)
            outputs = model(data)
            preds = outputs.argmax(dim=1)
            correct += (preds == target).sum().item()
            total += target.size(0)

    return correct / total if total > 0 else 0.0


def get_parameters(model):
    """Extract model parameters as numpy arrays."""
    return [val.cpu().detach().numpy() for val in model.state_dict().values()]


def set_parameters(model, parameters):
    """Load parameters into model."""
    params_dict = zip(model.state_dict().keys(), parameters)
    state_dict = {k: torch.tensor(v) for k, v in params_dict}
    model.load_state_dict(state_dict, strict=True)
