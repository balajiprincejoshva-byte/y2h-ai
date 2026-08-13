import numpy as np
from typing import Dict, List, Tuple
from scipy.spatial.distance import cdist

def find_nearest_known_interactors(
    target_protein: str,
    target_vec: np.ndarray,
    known_interactors_dict: Dict[str, np.ndarray],
    top_k: int = 5
) -> List[Tuple[str, float]]:
    """Find top-K nearest known interactors in sequence feature space using Cosine similarity."""
    if not known_interactors_dict or target_vec is None:
        return []
        
    protein_ids = list(known_interactors_dict.keys())
    matrix = np.array([known_interactors_dict[p] for p in protein_ids], dtype=np.float32)
    
    # Reshape target_vec
    target_mat = target_vec.reshape(1, -1)
    
    # Compute Cosine distances
    try:
        distances = cdist(target_mat, matrix, metric='cosine')[0]
        similarities = 1.0 - distances
    except Exception:
        similarities = np.zeros(len(protein_ids))
        
    top_indices = np.argsort(similarities)[::-1]
    
    results = []
    for idx in top_indices:
        pid = protein_ids[idx]
        if pid != target_protein:
            results.append((pid, round(float(similarities[idx]), 4)))
        if len(results) >= top_k:
            break
            
    return results
