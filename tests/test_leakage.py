import pytest
import pandas as pd
from y2h_ppi.splitting.protein_disjoint_split import create_c1_c2_c3_splits

def test_c3_protein_disjoint_leakage():
    """Unit test asserting zero protein overlap between C3 test set and training set."""
    proteins = [f"YPROT{i:03d}" for i in range(100)]
    
    pos_pairs = [(proteins[i], proteins[i+1]) for i in range(0, 40, 2)]
    neg_pairs = [(proteins[i], proteins[i+1]) for i in range(40, 80, 2)]
    
    df_pos = pd.DataFrame(pos_pairs, columns=['protein_a', 'protein_b'])
    df_pos['label'] = 1
    df_neg = pd.DataFrame(neg_pairs, columns=['protein_a', 'protein_b'])
    df_neg['label'] = 0
    
    splits = create_c1_c2_c3_splits(df_pos, df_neg, proteins, train_ratio=0.8, c1_test_fraction=0.1, seed=42)
    
    df_train = splits["train"]
    df_c3 = splits["c3_test"]
    
    train_prots = set(df_train['protein_a']).union(set(df_train['protein_b']))
    c3_prots = set(df_c3['protein_a']).union(set(df_c3['protein_b']))
    
    leakage = train_prots.intersection(c3_prots)
    assert len(leakage) == 0, f"C3 leakage test failed: Found {len(leakage)} overlapping proteins!"
