import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict
from y2h_ppi.logger import logger

CACHE_DIR = Path("data/interim/features_cache")

def save_feature_cache(protein_ids: list, features: np.ndarray, feature_type: str):
    """Save calculated protein feature matrix to parquet cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(features)
    df.insert(0, 'protein_id', protein_ids)
    out_file = CACHE_DIR / f"{feature_type}_features.parquet"
    df.to_parquet(out_file, index=False)
    logger.info(f"Saved feature cache to {out_file} (shape: {features.shape})")

def load_feature_cache(feature_type: str) -> Dict[str, np.ndarray]:
    """Load cached protein features dictionary keyed by protein_id."""
    out_file = CACHE_DIR / f"{feature_type}_features.parquet"
    if not out_file.exists():
        return {}
    df = pd.read_parquet(out_file)
    p_ids = df['protein_id'].tolist()
    feat_matrix = df.drop(columns=['protein_id']).values.astype(np.float32)
    return {pid: feat_matrix[i] for i, pid in enumerate(p_ids)}
