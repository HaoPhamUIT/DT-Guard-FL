"""Committee-based verifier selection (inspired by HSDPS concept)."""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np


@dataclass
class CommitteeSelector:
    """
    Select a verifier committee using reputation and Shapley value scores.

    Inspired by HSDPS (High Security Distributed Proof-of-Stake) concept from
    blockchain-based FL, but adapted for active behavioral verification instead
    of blockchain consensus.
    """

    num_clients: int
    committee_size: int
    reputation_scores: Optional[np.ndarray] = None
    shapley_history: Optional[List[np.ndarray]] = None

    def select_committee(self) -> List[int]:
        """Return a sorted list of verifier indices (deterministic)."""
        if self.committee_size <= 0 or self.committee_size >= self.num_clients:
            return list(range(self.num_clients))

        rep = self._normalize(self.reputation_scores, self.num_clients, default=1.0)
        shapley = self._normalize(self._mean_shapley(), self.num_clients, default=0.0)

        # Reputation-dominant weighting with Shapley as tie-breaker signal.
        scores = 0.7 * rep + 0.3 * shapley
        ranked = np.argsort(scores)[::-1]
        return sorted(ranked[: self.committee_size].tolist())

    def committee_seeds(self, round_num: int) -> List[int]:
        """Stable per-round seeds for committee verifiers."""
        committee = self.select_committee()
        return [round_num * 10_000 + idx * 97 for idx in committee]

    def _mean_shapley(self) -> Optional[np.ndarray]:
        if not self.shapley_history:
            return None
        return np.mean(np.stack(self.shapley_history, axis=0), axis=0)

    @staticmethod
    def _normalize(values: Optional[np.ndarray], size: int, default: float) -> np.ndarray:
        if values is None or len(values) != size:
            return np.ones(size) * default
        v = np.array(values, dtype=float)
        if v.max() == v.min():
            return np.ones(size) * default
        return (v - v.min()) / (v.max() - v.min())

