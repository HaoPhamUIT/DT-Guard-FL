"""Setup script for DTGuardFL package."""

from setuptools import setup, find_packages

setup(
    name="dtguard",
    version="1.0.0",
    description="DT-Guard: Active Digital Twin Verification for Federated Learning",
    author="DTGuard Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
        "pyyaml>=6.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
    ],
)
