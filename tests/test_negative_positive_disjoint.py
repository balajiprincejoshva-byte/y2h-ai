import pytest
from y2h_ppi.data.negatives import generate_random_negatives

def test_negative_positive_disjoint():
    """Ensure that generated random negatives never overlap with the provided positive/exclusion set."""
    proteins = [f"P{i}" for i in range(10)]
    
    # Let's say all sequential pairs are positives
    pos_pairs = set([(proteins[i], proteins[i+1]) for i in range(9)])
    
    # Generate random negatives
    neg_pairs = generate_random_negatives(pos_pairs, proteins, target_count=5, seed=42)
    
    overlap = set(neg_pairs).intersection(pos_pairs)
    assert len(overlap) == 0, f"Found overlap between negatives and exclusion set: {overlap}"
