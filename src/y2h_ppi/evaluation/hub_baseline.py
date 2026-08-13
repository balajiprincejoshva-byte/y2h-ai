import numpy as np
import pandas as pd
from typing import Dict
from y2h_ppi.logger import logger

class HubDegreeBaseline:
    """Degree/Hub baseline model scoring pairs by the product of protein degrees in training network."""
    
    def __init__(self):
        self.degree_map: Dict[str, int] = {}
        self.max_score: float = 1.0
        
    def fit(self, df_train_positives: pd.DataFrame):
        """Build node degree map from training physical interaction network."""
        degrees = {}
        for _, row in df_train_positives.iterrows():
            pa, pb = row['protein_a'], row['protein_b']
            degrees[pa] = degrees.get(pa, 0) + 1
            degrees[pb] = degrees.get(pb, 0) + 1
            
        self.degree_map = degrees
        max_deg = max(degrees.values()) if degrees else 1
        self.max_score = float(max_deg * max_deg)
        logger.info(f"Fitted Hub/Degree baseline on training network with {len(degrees)} unique nodes (max degree: {max_deg}).")
        
    def predict_proba(self, df_pairs: pd.DataFrame) -> np.ndarray:
        """Predict continuous probability scores proportional to deg(A) * deg(B)."""
        scores = []
        for _, row in df_pairs.iterrows():
            pa, pb = row['protein_a'], row['protein_b']
            deg_a = self.degree_map.get(pa, 0)
            deg_b = self.degree_map.get(pb, 0)
            score = float(deg_a * deg_b) / max(1.0, self.max_score)
            scores.append(score)
            
        return np.clip(np.array(scores, dtype=np.float32), 0.0, 1.0)
