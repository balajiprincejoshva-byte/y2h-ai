import pytest
import pandas as pd
from y2h_ppi.data.negatives import generate_random_negatives

def test_negative_set_zero_overlap():
    """Unit test asserting generated negative sets have zero overlap with positives."""
    pos_pairs = {("P1", "P2"), ("P3", "P4"), ("P5", "P6")}
    protein_list = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10"]
    
    negatives = generate_random_negatives(pos_pairs, protein_list, target_count=5, seed=42)
    neg_set = set(negatives)
    
    overlap = pos_pairs.intersection(neg_set)
    assert len(overlap) == 0, f"Negative sampling validation failed: {len(overlap)} overlapping pairs!"
