import numpy as np

def combine_pair_features(vec_a: np.ndarray, vec_b: np.ndarray) -> np.ndarray:
    """
    Construct a symmetric pair representation vector: [vec_A + vec_B, |vec_A - vec_B|].
    Guarantees order independence: F(A, B) == F(B, A).
    """
    sum_vec = vec_a + vec_b
    diff_vec = np.abs(vec_a - vec_b)
    return np.concatenate([sum_vec, diff_vec])

def assert_pair_symmetry(vec_a: np.ndarray, vec_b: np.ndarray):
    """Assert that swapping protein order produces an identical pair feature vector."""
    pair1 = combine_pair_features(vec_a, vec_b)
    pair2 = combine_pair_features(vec_b, vec_a)
    np.testing.assert_allclose(pair1, pair2, rtol=1e-6, atol=1e-6)
    return True
