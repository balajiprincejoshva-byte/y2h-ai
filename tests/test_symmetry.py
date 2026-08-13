import numpy as np
from y2h_ppi.features.pair_representation import combine_pair_features, assert_pair_symmetry

def test_pair_representation_symmetry():
    """Ensure that F(A, B) == F(B, A)"""
    vec_a = np.random.rand(128)
    vec_b = np.random.rand(128)
    assert assert_pair_symmetry(vec_a, vec_b) == True
