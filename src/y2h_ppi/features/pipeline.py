import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
from y2h_ppi.logger import logger
from y2h_ppi.features.classic_descriptors import extract_classical_descriptors
from y2h_ppi.features.esm_embeddings import ESMEmbeddingExtractor
from y2h_ppi.features.pair_representation import combine_pair_features, assert_pair_symmetry
from y2h_ppi.features.cache import save_feature_cache, load_feature_cache

INTERIM_DIR = Path("data/interim")
PROCESSED_DIR = Path("data/processed")

def compute_protein_features(seq_df: pd.DataFrame) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    """Compute Tier 1 (classical) and Tier 2 (ESM-2) protein features."""
    logger.info("Computing protein feature matrices...")
    
    classic_cache = load_feature_cache("classical")
    esm_cache = load_feature_cache("esm")
    
    protein_ids = seq_df['protein_id'].tolist()
    sequences = seq_df['sequence'].tolist()
    
    if len(classic_cache) < len(protein_ids):
        logger.info("Computing Tier 1 Classical Sequence Descriptors (AAC, DPC, CTD, Conjoint Triad)...")
        classic_features = [extract_classical_descriptors(seq) for seq in sequences]
        classic_matrix = np.array(classic_features, dtype=np.float32)
        save_feature_cache(protein_ids, classic_matrix, "classical")
        classic_cache = {pid: classic_matrix[i] for i, pid in enumerate(protein_ids)}
    else:
        logger.info(f"Loaded cached Tier 1 Classical Descriptors for {len(classic_cache)} proteins.")
        
    if len(esm_cache) < len(protein_ids):
        logger.info("Computing Tier 2 ESM-2 Embeddings in parallel batches...")
        extractor = ESMEmbeddingExtractor()
        esm_features = extractor.embed_sequences_batch(sequences, batch_size=32)
        esm_matrix = np.array(esm_features, dtype=np.float32)
        save_feature_cache(protein_ids, esm_matrix, "esm")
        esm_cache = {pid: esm_matrix[i] for i, pid in enumerate(protein_ids)}
    else:
        logger.info(f"Loaded cached Tier 2 ESM Embeddings for {len(esm_cache)} proteins.")
        
    return classic_cache, esm_cache

def build_pair_dataset(df_pairs: pd.DataFrame, feat_dict: Dict[str, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
    """Convert pair DataFrame (protein_a, protein_b, label) to pair feature matrix X and label vector y."""
    X_list = []
    y_list = []
    
    for _, row in df_pairs.iterrows():
        pa, pb = row['protein_a'], row['protein_b']
        label = row.get('label', 0)
        
        if pa in feat_dict and pb in feat_dict:
            vec_a, vec_b = feat_dict[pa], feat_dict[pb]
            pair_vec = combine_pair_features(vec_a, vec_b)
            X_list.append(pair_vec)
            y_list.append(label)
            
    if not X_list:
        return np.empty((0, 0), dtype=np.float32), np.empty((0,), dtype=np.int32)
        
    return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.int32)

def run_phase3() -> dict:
    """Run Phase 3: Compute classical descriptors, ESM-2 embeddings, and pair representations."""
    logger.info("=== Phase 3 Execution Started: Feature Engineering ===")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    seq_path = INTERIM_DIR / "protein_sequences.parquet"
    if not seq_path.exists():
        raise FileNotFoundError("Protein sequences file missing. Please run Phase 1 & Phase 2 first.")
        
    seq_df = pd.read_parquet(seq_path)
    
    classic_dict, esm_dict = compute_protein_features(seq_df)
    
    sample_pid = list(classic_dict.keys())[0]
    sample_classic_dim = classic_dict[sample_pid].shape[0]
    sample_esm_dim = esm_dict[sample_pid].shape[0]
    
    pair_classic_dim = sample_classic_dim * 2
    pair_esm_dim = sample_esm_dim * 2
    
    p1_id, p2_id = list(classic_dict.keys())[:2]
    assert_pair_symmetry(classic_dict[p1_id], classic_dict[p2_id])
    assert_pair_symmetry(esm_dict[p1_id], esm_dict[p2_id])
    logger.info("Symmetry Assertion PASSED: F(A, B) == F(B, A) verified for pair features.")
    
    print("\n" + "="*60)
    print("PHASE 3 CHECKPOINT EVIDENCE:")
    print(f" - Tier 1 Classical Sequence Feature Vector Dim: {sample_classic_dim} (Pair Dim: {pair_classic_dim})")
    print(f" - Tier 2 ESM Embedding Vector Dim: {sample_esm_dim} (Pair Dim: {pair_esm_dim})")
    print(" - Pair Order Symmetry Assertion (F(A,B) == F(B,A)): PASSED")
    print("="*60 + "\n")
    
    logger.info("=== Phase 3 Checkpoint PASSED ===")
    return {
        "classic_dim": pair_classic_dim,
        "esm_dim": pair_esm_dim,
        "symmetry_passed": True
    }

if __name__ == "__main__":
    run_phase3()
