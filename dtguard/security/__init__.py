"""Security components: attacks, defenses, and verification."""

from .attacks import apply_attack
from .digital_twin import DigitalTwinVerifier
from .dt_pw import (dt_performance_weighting, combine_dtpw_verification,
                      classic_shapley_values,
                      calculate_shapley_values, calculate_weighted_shapley)
from .reputation import ReputationSystem
from .committee import CommitteeSelector

__all__ = [
    'apply_attack',
    'DigitalTwinVerifier',
    'dt_performance_weighting',
    'combine_dtpw_verification',
    'classic_shapley_values',
    'calculate_shapley_values',      # backward compat alias → dt_performance_weighting
    'calculate_weighted_shapley',     # backward compat alias → combine_dtpw_verification
    'ReputationSystem',
    'CommitteeSelector'
]
