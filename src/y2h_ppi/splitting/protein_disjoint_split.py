import random
import pandas as pd
import numpy as np
from typing import Set, Dict, List, Tuple
from y2h_ppi.logger import logger

def partition_proteins(protein_list: List[str], train_ratio: float = 0.8, seed: int = 42) -> Tuple[Set[str], Set[str]]:
    """Partition unique protein IDs into P_train (80%) and P_heldout (20%) at protein level."""
    random.seed(seed)
    shuffled = sorted(list(set(protein_list)))
    random.shuffle(shuffled)
    
    n_train = int(len(shuffled) * train_ratio)
    p_train = set(shuffled[:n_train])
    p_heldout = set(shuffled[n_train:])
    
    logger.info(f"Partitioned {len(shuffled)} proteins into P_train ({len(p_train)}) and P_heldout ({len(p_heldout)}).")
    return p_train, p_heldout

def create_c1_c2_c3_splits(
    df_positives: pd.DataFrame,
    df_negatives: pd.DataFrame,
    protein_list: List[str],
    train_ratio: float = 0.8,
    c1_test_fraction: float = 0.1,
    seed: int = 42
) -> Dict[str, pd.DataFrame]:
    """
    Construct Park & Marcotte (2012) protein-disjoint dataset splits:
    - Train Pairs: both proteins in P_train (minus held-back C1 slice)
    - C1 Test Pairs: both proteins in P_train, held out from training pairs
    - C2 Test Pairs: exactly one protein in P_train, one in P_heldout
    - C3 Test Pairs: both proteins in P_heldout (completely unseen proteins)
    """
    p_train, p_heldout = partition_proteins(protein_list, train_ratio=train_ratio, seed=seed)
    
    df_all = pd.concat([df_positives, df_negatives], ignore_index=True)
    
    c1_candidates = []
    c2_pairs = []
    c3_pairs = []
    
    for _, row in df_all.iterrows():
        pa, pb = row['protein_a'], row['protein_b']
        lbl = row.get('label', 0)
        
        in_train_a = pa in p_train
        in_train_b = pb in p_train
        
        if in_train_a and in_train_b:
            c1_candidates.append((pa, pb, lbl))
        elif (in_train_a and not in_train_b) or (not in_train_a and in_train_b):
            c2_pairs.append((pa, pb, lbl))
        else:
            c3_pairs.append((pa, pb, lbl))
            
    df_c1_cand = pd.DataFrame(c1_candidates, columns=['protein_a', 'protein_b', 'label'])
    df_c2 = pd.DataFrame(c2_pairs, columns=['protein_a', 'protein_b', 'label'])
    df_c3 = pd.DataFrame(c3_pairs, columns=['protein_a', 'protein_b', 'label'])
    
    # Hold back a slice of C1 candidate pairs for C1 testing, rest for training
    df_c1_cand = df_c1_cand.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    n_c1_test = int(len(df_c1_cand) * c1_test_fraction)
    
    df_c1_test = df_c1_cand.iloc[:n_c1_test].reset_index(drop=True)
    df_train = df_c1_cand.iloc[n_c1_test:].reset_index(drop=True)
    
    logger.info(f"Dataset split counts: Train Pairs={len(df_train)}, C1 Test={len(df_c1_test)}, C2 Test={len(df_c2)}, C3 Test={len(df_c3)}.")
    
    # Assert C3 Leakage Check
    train_proteins_in_pairs = set(df_train['protein_a']).union(set(df_train['protein_b']))
    c3_proteins_in_pairs = set(df_c3['protein_a']).union(set(df_c3['protein_b']))
    leakage = train_proteins_in_pairs.intersection(c3_proteins_in_pairs)
    assert len(leakage) == 0, f"C3 LEAKAGE ERROR: {len(leakage)} proteins overlap between C3 test set and train set!"
    logger.info("Assertion PASSED: C3 protein-disjoint leakage test strictly verified (0 overlapping proteins).")
    
    return {
        "train": df_train,
        "c1_test": df_c1_test,
        "c2_test": df_c2,
        "c3_test": df_c3,
        "p_train": p_train,
        "p_heldout": p_heldout
    }
