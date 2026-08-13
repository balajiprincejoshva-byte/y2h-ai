import pytest
import pandas as pd
from y2h_ppi.splitting.protein_disjoint_split import create_c1_c2_c3_splits

def test_c1_c2_c3_split_determinism():
    """Ensure that with the same seed, the splits are identical."""
    proteins = [f"YPROT{i:03d}" for i in range(100)]
    pos_pairs = [(proteins[i], proteins[i+1]) for i in range(0, 40, 2)]
    neg_pairs = [(proteins[i], proteins[i+1]) for i in range(40, 80, 2)]
    
    df_pos = pd.DataFrame(pos_pairs, columns=['protein_a', 'protein_b'])
    df_pos['label'] = 1
    df_neg = pd.DataFrame(neg_pairs, columns=['protein_a', 'protein_b'])
    df_neg['label'] = 0
    
    splits_1 = create_c1_c2_c3_splits(df_pos, df_neg, proteins, train_ratio=0.8, c1_test_fraction=0.1, seed=42)
    splits_2 = create_c1_c2_c3_splits(df_pos, df_neg, proteins, train_ratio=0.8, c1_test_fraction=0.1, seed=42)
    
    assert list(splits_1["train"]['protein_a']) == list(splits_2["train"]['protein_a'])
    assert list(splits_1["c3_test"]['protein_a']) == list(splits_2["c3_test"]['protein_a'])
