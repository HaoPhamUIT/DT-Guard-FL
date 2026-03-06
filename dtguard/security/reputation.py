"""Reputation system for tracking client trustworthiness."""

import numpy as np
from typing import Dict, List


class ReputationSystem:
    """Track and update client reputation scores over rounds."""
    
    def __init__(self, num_clients: int, initial_score: float = 1.0, decay: float = 0.9):
        """
        Args:
            num_clients: Number of clients
            initial_score: Initial reputation score
            decay: Decay factor for old scores
        """
        self.num_clients = num_clients
        self.scores = np.ones(num_clients) * initial_score
        self.decay = decay
        self.history = []
    
    def update(self, client_id: int, passed: bool, verification_score: float = None):
        """
        Update reputation based on verification result.
        
        Args:
            client_id: Client index
            passed: Whether client passed verification
            verification_score: Optional verification score
        """
        if passed:
            # Increase reputation
            if verification_score is not None:
                self.scores[client_id] = min(1.0, self.scores[client_id] * 1.1 + verification_score * 0.1)
            else:
                self.scores[client_id] = min(1.0, self.scores[client_id] * 1.1)
        else:
            # Decrease reputation
            self.scores[client_id] = max(0.0, self.scores[client_id] * 0.5)
        
        # Apply decay to all scores
        self.scores = self.scores * self.decay + (1 - self.decay)
    
    def get_score(self, client_id: int) -> float:
        """Get current reputation score."""
        return self.scores[client_id]
    
    def get_all_scores(self) -> np.ndarray:
        """Get all reputation scores."""
        return self.scores.copy()
    
    def should_filter(self, client_id: int, threshold: float = 0.3) -> bool:
        """Check if client should be filtered based on reputation."""
        return self.scores[client_id] < threshold
    
    def reset(self):
        """Reset all scores to initial value."""
        self.scores = np.ones(self.num_clients)
