import random
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Set, Tuple, List, Dict
from y2h_ppi.logger import logger
from y2h_ppi.data.manifest import update_manifest_entry

INTERIM_DIR = Path("data/interim")
PROCESSED_DIR = Path("data/processed")

def generate_random_negatives(
    positive_pairs: Set[Tuple[str, str]],
    protein_list: List[str],
    target_count: int,
    seed: int = 42
) -> List[Tuple[str, str]]:
    """Sample random protein pairs excluding known positive physical interactions."""
    random.seed(seed)
    negatives = set()
    attempts = 0
    max_attempts = target_count * 100
    
    n_proteins = len(protein_list)
    if n_proteins < 2:
        raise ValueError("Need at least 2 proteins to generate negative pairs.")
        
    while len(negatives) < target_count and attempts < max_attempts:
        attempts += 1
        idx_a = random.randint(0, n_proteins - 1)
        idx_b = random.randint(0, n_proteins - 1)
        if idx_a == idx_b:
            continue
            
        p1, p2 = protein_list[idx_a], protein_list[idx_b]
        pa, pb = min(p1, p2), max(p1, p2)
        pair = (pa, pb)
        
        if pair not in positive_pairs and pair not in negatives:
            negatives.add(pair)
            
    if len(negatives) < target_count:
        logger.warning(f"Could only sample {len(negatives)} negative pairs out of target {target_count}.")
        
    return list(negatives)

def run_phase2(seed: int = 42) -> Dict[str, int]:
    """Run Phase 2: Construct negative sets (Curated, Random 1:1, Realistic Imbalance 1:10, 1:100)."""
    logger.info("=== Phase 2 Execution Started: Negative Sampling Strategy ===")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load mapped positives, all physical positives (for exclusion), and sequences
    pos_path = INTERIM_DIR / "positives_mapped.parquet"
    all_phys_path = INTERIM_DIR / "all_physical_positives.parquet"
    seq_path = INTERIM_DIR / "protein_sequences.parquet"
    negatome_path = INTERIM_DIR / "negatome_yeast_negatives.parquet"
    
    if not pos_path.exists() or not seq_path.exists() or not all_phys_path.exists():
        raise FileNotFoundError("Phase 1 outputs missing. Please run Phase 1 first.")
        
    df_pos = pd.read_parquet(pos_path)
    df_all_phys = pd.read_parquet(all_phys_path)
    df_seq = pd.read_parquet(seq_path)
    
    pos_pairs_set: Set[Tuple[str, str]] = set(zip(df_pos['protein_a'], df_pos['protein_b']))
    exclusion_pairs_set: Set[Tuple[str, str]] = set(zip(df_all_phys['protein_a'], df_all_phys['protein_b']))
    protein_list: List[str] = sorted(df_seq['protein_id'].unique().tolist())
    
    n_positives = len(df_pos)
    logger.info(f"Targeting positive baseline set size: {n_positives} pairs.")
    
    # 1. Curated Negatives (Negatome)
    if negatome_path.exists():
        df_curated = pd.read_parquet(negatome_path)
    else:
        df_curated = pd.DataFrame(columns=['protein_a', 'protein_b', 'label'])
        
    # Ensure zero overlap between Curated Negatives & ALL Physical Positives
    curated_pairs = set(zip(df_curated['protein_a'], df_curated['protein_b'])) if not df_curated.empty else set()
    overlap_curated = curated_pairs.intersection(exclusion_pairs_set)
    if overlap_curated:
        logger.warning(f"Removing {len(overlap_curated)} overlapping pairs from Curated Negatives.")
        curated_pairs = curated_pairs - exclusion_pairs_set
        df_curated = pd.DataFrame(list(curated_pairs), columns=['protein_a', 'protein_b'])
        df_curated['label'] = 0
        
    # 2. Random-Sampled Negatives (1:1 Ratio)
    neg_1to1_list = generate_random_negatives(exclusion_pairs_set, protein_list, target_count=n_positives, seed=seed)
    df_neg_1to1 = pd.DataFrame(neg_1to1_list, columns=['protein_a', 'protein_b'])
    df_neg_1to1['label'] = 0
    
    # 3. Realistic-Imbalance Negatives (1:10 & 1:100 Ratios)
    neg_1to10_list = generate_random_negatives(exclusion_pairs_set, protein_list, target_count=n_positives * 10, seed=seed + 1)
    df_neg_1to10 = pd.DataFrame(neg_1to10_list, columns=['protein_a', 'protein_b'])
    df_neg_1to10['label'] = 0
    
    neg_1to100_list = generate_random_negatives(exclusion_pairs_set, protein_list, target_count=n_positives * 100, seed=seed + 2)
    df_neg_1to100 = pd.DataFrame(neg_1to100_list, columns=['protein_a', 'protein_b'])
    df_neg_1to100['label'] = 0
    
    # Strict Assertions: Zero overlap with positive set
    set_1to1 = set(zip(df_neg_1to1['protein_a'], df_neg_1to1['protein_b']))
    set_1to10 = set(zip(df_neg_1to10['protein_a'], df_neg_1to10['protein_b']))
    set_1to100 = set(zip(df_neg_1to100['protein_a'], df_neg_1to100['protein_b']))
    
    assert len(set_1to1.intersection(pos_pairs_set)) == 0, "ERROR: Overlap found between 1:1 negatives and positives!"
    assert len(set_1to10.intersection(pos_pairs_set)) == 0, "ERROR: Overlap found between 1:10 negatives and positives!"
    assert len(set_1to100.intersection(pos_pairs_set)) == 0, "ERROR: Overlap found between 1:100 negatives and positives!"
    
    logger.info("Assertion PASSED: Programmatic check confirmed ZERO overlap between all negative sets and BioGRID positive set.")
    
    # Save datasets (V3 Expansion)
    df_curated.to_parquet(PROCESSED_DIR / "negatives_v3_curated.parquet", index=False)
    df_neg_1to1.to_parquet(PROCESSED_DIR / "negatives_v3_1to1.parquet", index=False)
    df_neg_1to10.to_parquet(PROCESSED_DIR / "negatives_v3_1to10.parquet", index=False)
    df_neg_1to100.to_parquet(PROCESSED_DIR / "negatives_v3_1to100.parquet", index=False)
    
    update_manifest_entry(
        source_name="Negative Sampling Sets",
        url="Generated programmatically",
        version="v1.0 (seed 42)",
        raw_count=n_positives * 100,
        filtered_count=len(df_neg_1to1) + len(df_neg_1to10) + len(df_neg_1to100),
        description=f"Constructed 1:1 ({len(df_neg_1to1)}), 1:10 ({len(df_neg_1to10)}), 1:100 ({len(df_neg_1to100)}) random negative sets + Negatome curated ({len(df_curated)}), verified zero overlap."
    )
    
    print("\n" + "="*60)
    print("PHASE 2 CHECKPOINT EVIDENCE:")
    print(f" - Curated Negatives (Negatome): {len(df_curated)} pairs")
    print(f" - Random Negatives (1:1 Balanced): {len(df_neg_1to1)} pairs")
    print(f" - Imbalance Negatives (1:10 Ratio): {len(df_neg_1to10)} pairs")
    print(f" - Imbalance Negatives (1:100 Ratio): {len(df_neg_1to100)} pairs")
    print(" - Zero-Overlap Verification Assertion: PASSED (0 overlapping pairs)")
    print("="*60 + "\n")
    
    logger.info("=== Phase 2 Checkpoint PASSED ===")
    return {
        "curated": len(df_curated),
        "random_1to1": len(df_neg_1to1),
        "imbalance_1to10": len(df_neg_1to10),
        "imbalance_1to100": len(df_neg_1to100)
    }

if __name__ == "__main__":
    run_phase2()
