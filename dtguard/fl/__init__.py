"""Federated Learning components."""

from .aggregation import federated_averaging, weighted_federated_averaging, run_federated_learning
from .baselines import (
    krum_aggregation, median_aggregation, trimmed_mean_aggregation, multi_krum_aggregation,
    federated_averaging as baseline_fedavg,
    lup_aggregation, clipcluster_aggregation, signguard_aggregation, poc_aggregation,
    geomed_aggregation,
)
from .async_aggregation import run_async_federated_learning

__all__ = [
    'federated_averaging',
    'weighted_federated_averaging',
    'run_federated_learning',
    'krum_aggregation',
    'median_aggregation',
    'trimmed_mean_aggregation',
    'multi_krum_aggregation',
    'run_async_federated_learning',
    'lup_aggregation',
    'clipcluster_aggregation',
    'signguard_aggregation',
    'poc_aggregation',
    'geomed_aggregation',
]
