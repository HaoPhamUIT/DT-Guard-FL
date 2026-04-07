"""Data loading and preprocessing for CIC-IoT-2023."""

from pathlib import Path
from typing import Tuple, List
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from dtguard.config import Config, CLASS_MAPPING


def load_data(config: Config) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Load and preprocess CIC-IoT-2023 dataset.
    
    Returns:
        train_df: Training dataframe
        test_df: Testing dataframe
        feature_cols: List of feature column names
    """
    cache_path = Path(config.cache_file)
    
    # Load from cache if exists
    if cache_path.exists():
        print(f"Loading from cache: {cache_path}")
        full_df = pd.read_pickle(cache_path)
    else:
        print(f"Loading from CSV files in {config.dataset_dir}")
        csv_files = sorted(Path(config.dataset_dir).glob("*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {config.dataset_dir}")
        
        # Load and combine all CSV files
        dfs = []
        for csv_file in csv_files:
            print(f"  Reading {csv_file.name}...")
            df = pd.read_csv(csv_file)
            dfs.append(df)
        
        full_df = pd.concat(dfs, ignore_index=True)
        
        # Map labels to integers
        if 'Label' in full_df.columns:
            full_df['Label'] = full_df['Label'].map(CLASS_MAPPING)
        
        # Drop NaN and convert label to int
        full_df = full_df.dropna(subset=['Label'])
        full_df['Label'] = full_df['Label'].astype(int)
        
        # Cache for future use
        full_df.to_pickle(cache_path)
        print(f"Cached to {cache_path}")
    
    # Get feature columns
    feature_cols = [c for c in full_df.columns if c != 'Label']
    
    # Train/test split
    train_df, test_df = train_test_split(
        full_df,
        test_size=config.test_size,
        random_state=config.random_seed,
        stratify=full_df['Label']
    )
    
    # Scale features
    train_df = _scale_features(train_df, feature_cols)
    test_df = _scale_features(test_df, feature_cols)
    
    print(f"✓ Train: {len(train_df)} samples, Test: {len(test_df)} samples")
    print(f"✓ Features: {len(feature_cols)}, Classes: {full_df['Label'].nunique()}")
    
    return train_df, test_df, feature_cols


def create_federated_dataset(
    train_df: pd.DataFrame,
    feature_cols: List[str],
    config: Config,
    verbose: bool = False,
    max_samples_per_client: int = 0
) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """
    Split training data across clients using Dirichlet distribution.
    
    Args:
        max_samples_per_client: Cap each client's data (0 = no cap).
            Use 10_000 for quick tests, 20_000 for full experiments.
            Stratified sub-sampling preserves class ratios.

    Returns:
        X_clients: List of feature arrays for each client
        y_clients: List of label arrays for each client
    """
    y_data = train_df['Label'].values
    class_indices = {cls: np.where(y_data == cls)[0] for cls in np.unique(y_data)}
    
    client_indices = [[] for _ in range(config.num_clients)]
    
    # Dirichlet distribution for Non-IID split
    for cls, indices in class_indices.items():
        n_samples = len(indices)
        proportions = np.random.dirichlet([config.dirichlet_alpha] * config.num_clients)
        splits = (proportions * n_samples).astype(int)
        
        # Adjust for rounding errors
        while splits.sum() < n_samples:
            splits[np.argmax(proportions)] += 1
        while splits.sum() > n_samples:
            splits[np.argmax(splits)] -= 1
        
        # Distribute samples
        np.random.shuffle(indices)
        start = 0
        for client_id, split_size in enumerate(splits):
            end = start + split_size
            client_indices[client_id].extend(indices[start:end])
            start = end
    
    # Convert to numpy arrays
    X_clients = []
    y_clients = []
    for client_id in range(config.num_clients):
        idxs = client_indices[client_id]
        X_c = train_df.iloc[idxs][feature_cols].values.astype(np.float32)
        y_c = train_df.iloc[idxs]['Label'].values.astype(np.int64)

        # Subsample if too large (stratified to keep class ratios)
        if max_samples_per_client > 0 and len(X_c) > max_samples_per_client:
            classes, counts = np.unique(y_c, return_counts=True)
            total = len(y_c)
            keep = []
            for cls, cnt in zip(classes, counts):
                cls_idx = np.where(y_c == cls)[0]
                n_keep = max(1, int(round(max_samples_per_client * cnt / total)))
                n_keep = min(n_keep, len(cls_idx))
                keep.extend(np.random.choice(cls_idx, n_keep, replace=False))
            keep = np.array(keep)
            np.random.shuffle(keep)
            X_c = X_c[keep]
            y_c = y_c[keep]

        X_clients.append(X_c)
        y_clients.append(y_c)
        if verbose:
            print(f"  Client {client_id}: {len(X_c)} samples")

    return X_clients, y_clients


def _scale_features(df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
    """Scale features using StandardScaler."""
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    scaler = StandardScaler()
    df[feature_cols] = df[feature_cols].astype(np.float32)
    df.loc[:, feature_cols] = scaler.fit_transform(df[feature_cols])
    return df


def load_ton_iot_data(data_dir: str = "data/ToN-IoT_Data",
                      test_size: float = 0.2,
                      random_seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Load and preprocess ToN-IoT dataset.

    ToN-IoT dataset structure:
        train_data.csv: Training features (no header)
        train_label.csv: Training labels (no header)
        test_data.csv: Test features (no header)
        test_label.csv: Test labels (no header)

    Args:
        data_dir: Directory containing ToN-IoT CSV files
        test_size: Fraction of training data to use for validation (not used if test_data exists)
        random_seed: Random seed for reproducibility

    Returns:
        train_df: Training dataframe with features and Label column
        test_df: Testing dataframe with features and Label column
        feature_cols: List of feature column names (feature_0, feature_1, ...)
    """
    data_path = Path(data_dir)

    # Load training data
    train_data_file = data_path / "train_data.csv"
    train_label_file = data_path / "train_label.csv"

    if not train_data_file.exists() or not train_label_file.exists():
        raise FileNotFoundError(f"ToN-IoT training files not found in {data_dir}")

    print(f"Loading ToN-IoT training data from {data_dir}...")

    # Load features and labels separately
    train_features = pd.read_csv(train_data_file, header=None)
    train_labels = pd.read_csv(train_label_file, header=None)

    # Combine into single dataframe
    train_df = train_features.copy()
    train_df['Label'] = train_labels.iloc[:, 0].astype(int)

    # Load test data if exists
    test_data_file = data_path / "test_data.csv"
    test_label_file = data_path / "test_label.csv"

    if test_data_file.exists() and test_label_file.exists():
        print(f"Loading ToN-IoT test data...")
        test_features = pd.read_csv(test_data_file, header=None)
        test_labels = pd.read_csv(test_label_file, header=None)

        test_df = test_features.copy()
        test_df['Label'] = test_labels.iloc[:, 0].astype(int)
    else:
        # Split from training data
        from sklearn.model_selection import train_test_split
        train_df, test_df = train_test_split(
            train_df, test_size=test_size, random_state=random_seed,
            stratify=train_df['Label']
        )

    # Create feature column names and rename columns
    n_features = train_df.shape[1] - 1  # Exclude Label
    feature_cols = [f"feature_{i}" for i in range(n_features)]

    # Rename columns (0, 1, 2, ... -> feature_0, feature_1, ...)
    train_df.columns = feature_cols + ['Label']
    test_df.columns = feature_cols + ['Label']

    # Drop NaN and infinite values
    train_df = train_df.replace([np.inf, -np.inf], np.nan).dropna()
    test_df = test_df.replace([np.inf, -np.inf], np.nan).dropna()

    # Scale features
    train_df = _scale_features(train_df, feature_cols)
    test_df = _scale_features(test_df, feature_cols)

    print(f"✓ Train: {len(train_df)} samples, Test: {len(test_df)} samples")
    print(f"✓ Features: {len(feature_cols)}, Classes: {train_df['Label'].nunique()}")
    print(f"✓ Class distribution: {train_df['Label'].value_counts().to_dict()}")

    return train_df, test_df, feature_cols
