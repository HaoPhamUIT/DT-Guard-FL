"""Configuration for DTGuardFL experiments."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Optional
import yaml


class AttackType(str, Enum):
    NONE = "NONE"
    MODEL_POISONING = "MODEL_POISONING"
    GRADIENT_ASCENT = "GRADIENT_ASCENT"
    BYZANTINE_ATTACK = "BYZANTINE_ATTACK"
    BACKDOOR = "BACKDOOR"
    LABEL_FLIPPING = "LABEL_FLIPPING"
    MIMIC_ATTACK = "MIMIC_ATTACK"
    NOISE_INJECTION = "NOISE_INJECTION"
    DATA_POISONING = "DATA_POISONING"
    SYBIL_ATTACK = "SYBIL_ATTACK"
    FREE_RIDER = "FREE_RIDER"
    INFERENCE_ATTACK = "INFERENCE_ATTACK"
    # Advanced attacks from DT-BFL paper (2025)
    SIGN_FLIP = "SIGN_FLIP"
    LIE = "LIE"                # A Little Is Enough [Baruch et al., NeurIPS 2019]
    MIN_MAX = "MIN_MAX"        # Min-Max [Shejwalkar & Houmansadr, NDSS 2021]
    MIN_SUM = "MIN_SUM"        # Min-Sum [Shejwalkar & Houmansadr, NDSS 2021]
    MPAF = "MPAF"              # Model Poisoning Attack on FL [Cao et al., 2022]
    BYZMEAN = "BYZMEAN"        # ByzMean [LUP repo]


class DefenseType(str, Enum):
    NONE = "NONE"
    DTGUARD = "DTGUARD"  # Digital Twin Guard
    KRUM = "KRUM"
    FLTRUST = "FLTRUST"
    FEDRE = "FEDRE"
    # New defense baselines from 3 papers (2025)
    LUP = "LUP"              # Local Updates Purify [Issa et al., Ad Hoc Networks 2025]
    CLIPCLUSTER = "CLIPCLUSTER"  # ClipCluster [Zeng et al., IEEE TIFS 2024]
    SIGNGUARD = "SIGNGUARD"      # SignGuard [Xu et al., IEEE TDSC 2022]
    POC = "POC"              # Proof of Contribution [Zhang et al., IEEE TSG 2025]


@dataclass
class Config:
    """Unified configuration for DTGuardFL."""

    # Data
    dataset_dir: str = "data/CICIoT2023"
    dataset_type: str = "CICIoT2023"  # "CICIoT2023" or "ToN-IoT"
    cache_file: str = "training_data.pkl"
    test_size: float = 0.2
    
    # FL Setup
    num_clients: int = 3
    num_malicious: int = 1
    dirichlet_alpha: float = 0.5
    
    # Training
    num_rounds: int = 5
    local_epochs: int = 3
    batch_size: int = 32
    learning_rate: float = 0.001
    
    # DT-Guard
    dt_threshold: float = 0.20  # Lowered to reduce false positives
    dt_alpha: float = 0.7  # DR weight
    dt_beta: float = 0.3   # FPR weight
    gan_epochs: int = 50  # Increased for better training
    challenge_samples: int = 500
    
    # Attack
    attack_type: AttackType = AttackType.MODEL_POISONING
    attack_scale: float = 15.0  # Increased for real data detection
    
    # Defense
    defense_type: DefenseType = DefenseType.DTGUARD

    # Committee-based verification (inspired by HSDPS concept)
    use_committee: bool = False  # Use multiple verifiers
    committee_size: int = 0  # Number of committee members (0 = single verifier)

    # Async FL
    use_async: bool = False
    async_alpha: float = 0.5
    async_buffer_size: int = 3

    # System
    device: str = "auto"
    random_seed: int = 42
    
    @classmethod
    def from_yaml(cls, path: str) -> 'Config':
        """Load config from YAML file."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    def to_yaml(self, path: str):
        """Save config to YAML file."""
        with open(path, 'w') as f:
            yaml.dump(self.__dict__, f, sort_keys=False)


# Default CIC-IoT-2023 class mapping
CLASS_MAPPING = {
    "BENIGN": 0,
    "DDOS-RSTFINFLOOD": 1, "DDOS-PSHACK_FLOOD": 2, "DDOS-SYN_FLOOD": 3,
    "DDOS-UDP_FLOOD": 4, "DDOS-TCP_FLOOD": 5, "DDOS-ICMP_FLOOD": 6,
    "DDOS-SYNONYMOUSIP_FLOOD": 7, "DDOS-ACK_FRAGMENTATION": 8,
    "DDOS-UDP_FRAGMENTATION": 9, "DDOS-ICMP_FRAGMENTATION": 10,
    "DDOS-SLOWLORIS": 11, "DDOS-HTTP_FLOOD": 12,
    "DOS-UDP_FLOOD": 13, "DOS-SYN_FLOOD": 14, "DOS-TCP_FLOOD": 15, "DOS-HTTP_FLOOD": 16,
    "MIRAI-GREETH_FLOOD": 17, "MIRAI-GREIP_FLOOD": 18, "MIRAI-UDPPLAIN": 19,
    "RECON-PINGSWEEP": 20, "RECON-OSSCAN": 21, "RECON-PORTSCAN": 22,
    "VULNERABILITYSCAN": 23, "RECON-HOSTDISCOVERY": 24,
    "DNS_SPOOFING": 25, "MITM-ARPSPOOFING": 26, "BROWSERHIJACKING": 27,
    "BACKDOOR_MALWARE": 28, "XSS": 29, "UPLOADING_ATTACK": 30,
    "SQLINJECTION": 31, "COMMANDINJECTION": 32, "DICTIONARYBRUTEFORCE": 33,
}
