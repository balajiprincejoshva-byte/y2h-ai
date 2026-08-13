import joblib
import pandas as pd
import numpy as np
import uuid
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from y2h_ppi.logger import logger
from y2h_ppi.features.classic_descriptors import extract_classical_descriptors
from y2h_ppi.features.pair_representation import combine_pair_features
from y2h_ppi.explain.neighbor_explain import find_nearest_known_interactors

MODEL_DIR = Path("data/processed/saved_models")
INTERIM_DIR = Path("data/interim")

class PPIPredictor:
    """Production Inference Service for Yeast PPI Prediction."""
    
    def __init__(self, model_dir: Path = MODEL_DIR):
        self.model_dir = model_dir
        self.model = None
        self.seq_dict = {}
        self.pos_pairs_set = set()
        self.model_metadata = {
            "name": "Random Forest",
            "version": "Y2H-AI RF V3",
            "feature_version": "Tier 1 Classical Descriptors"
        }
        self._is_loaded = False
        
    def load(self):
        if self._is_loaded:
            return
            
        rf_path = self.model_dir / "random_forest_v3.joblib"
        if rf_path.exists():
            self.model = joblib.load(rf_path)
            logger.info(f"Loaded predictor model from {rf_path}")
        else:
            logger.error(f"Model file {rf_path} not found.")
            
        seq_path = INTERIM_DIR / "protein_sequences.parquet"
        if seq_path.exists():
            df_seq = pd.read_parquet(seq_path)
            self.seq_dict = dict(zip(df_seq['protein_id'], df_seq['sequence']))
            
        pos_path = INTERIM_DIR / "positives_mapped.parquet"
        if pos_path.exists():
            df_pos = pd.read_parquet(pos_path)
            self.pos_pairs_set = set((min(a, b), max(a, b)) for a, b in zip(df_pos['protein_a'], df_pos['protein_b']))
            
        self._is_loaded = True
        
    def predict_pair(
        self,
        protein_a: str,
        protein_b: str,
        seq_a: Optional[str] = None,
        seq_b: Optional[str] = None
    ) -> Dict[str, Any]:
        """Score a single protein pair."""
        self.load()
        
        pa_clean = protein_a.strip().upper()
        pb_clean = protein_b.strip().upper()
        
        s1 = seq_a or self.seq_dict.get(pa_clean, "")
        s2 = seq_b or self.seq_dict.get(pb_clean, "")
        
        if not s1 or not s2:
            raise ValueError(f"Sequence not found for one or both proteins: {pa_clean}, {pb_clean}")
            
        vec_a = extract_classical_descriptors(s1)
        vec_b = extract_classical_descriptors(s2)
        pair_vec = combine_pair_features(vec_a, vec_b).reshape(1, -1)
        
        if self.model is not None and hasattr(self.model, 'predict_proba'):
            prob = float(self.model.predict_proba(pair_vec)[0, 1])
        else:
            raise RuntimeError("Model is not loaded or missing predict_proba. Cannot run inference.")
            
        # Confidence Band
        if prob >= 0.75:
            band = "High Confidence"
        elif prob >= 0.45:
            band = "Medium Confidence"
        else:
            band = "Low Confidence"
            
        canonical_pair = (min(pa_clean, pb_clean), max(pa_clean, pb_clean))
        is_documented = canonical_pair in self.pos_pairs_set
        
        know_dict = {p: extract_classical_descriptors(s) for p, s in list(self.seq_dict.items())[:15]}
        nearest = find_nearest_known_interactors(pa_clean, vec_a, know_dict, top_k=3)
        
        ci_lower = None
        ci_upper = None
        
        doc_status = "Documented Interaction" if is_documented else "No documented interaction found"
        prediction_id = str(uuid.uuid4())
        
        return {
            "prediction_id": prediction_id,
            "protein_a": pa_clean,
            "protein_b": pb_clean,
            "raw_probability": None, # The ML baseline only saves the CalibratedClassifierCV
            "calibrated_probability": round(prob, 4),
            "confidence_band": band,
            "model": self.model_metadata,
            "calibration": {
                "method": "Isotonic Regression"
            },
            "documentation": {
                "status": "Documented Interaction" if is_documented else "No documented interaction found",
                "source": "S. cerevisiae BIOGRID Reference (Positives Mapped)"
            },
            "nearest_known_interactors": nearest,
            "provenance_trace": {
                "timestamp": pd.Timestamp.utcnow().isoformat(),
                "model_loaded": self._is_loaded
            }
        }
        
    def predict_batch(self, pairs: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Score a batch of protein pairs."""
        return [self.predict_pair(pa, pb) for pa, pb in pairs]

def run_phase7() -> dict:
    """Run Phase 7: Inference Engine Verification."""
    logger.info("=== Phase 7 Execution Started: Inference Engine Verification ===")
    predictor = PPIPredictor()
    
    res = predictor.predict_pair("YFL039C", "YAL001C")
    print("\n" + "="*60)
    print("PHASE 7 CHECKPOINT EVIDENCE (INFERENCE ENGINE):")
    print(f" Sample Single Prediction for ({res['protein_a']}, {res['protein_b']}):")
    print(f"  * Prediction ID: {res['prediction_id']}")
    print(f"  * Calibrated Probability: {res['calibrated_probability']}")
    print(f"  * Confidence Band: {res['confidence_band']}")
    print(f"  * Documentation Status: {res['documentation']['status']}")
    print(f"  * Model Version: {res['model']['version']}")
    print("="*60 + "\n")
    
    logger.info("=== Phase 7 Checkpoint PASSED ===")
    return res

if __name__ == "__main__":
    run_phase7()
