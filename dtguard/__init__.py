"""
DTGuardFL - Digital Twin Guard for Federated Learning
Active verification for robust IoT intrusion detection
"""

__version__ = '1.0.0'
__author__ = 'DTGuard Team'

# Core imports
from dtguard.config import Config
from dtguard.data import load_data, create_federated_dataset
from dtguard.models import IoTAttackNet, GANGenerator
from dtguard.security import DigitalTwinVerifier, apply_attack, calculate_shapley_values
from dtguard.fl import run_federated_learning, weighted_federated_averaging
from dtguard.utils import plot_poc_results, print_summary_table

__all__ = [
    'Config',
    'load_data',
    'create_federated_dataset',
    'IoTAttackNet',
    'GANGenerator',
    'DigitalTwinVerifier',
    'apply_attack',
    'calculate_shapley_values',
    'run_federated_learning',
    'weighted_federated_averaging',
    'plot_poc_results',
    'print_summary_table',
]
