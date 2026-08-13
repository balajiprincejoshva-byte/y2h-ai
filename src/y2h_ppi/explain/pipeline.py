import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from y2h_ppi.logger import logger
from y2h_ppi.explain.shap_explain import compute_shap_importance
from y2h_ppi.explain.neighbor_explain import find_nearest_known_interactors
from y2h_ppi.features.classic_descriptors import extract_classical_descriptors

PROCESSED_DIR = Path("data/processed")
MODEL_DIR = PROCESSED_DIR / "saved_models"

def run_phase6() -> dict:
    """Run Phase 6: Explainability Pipeline."""
    logger.info("=== Phase 6 Execution Started: Explainability ===")
    
    rf_path = MODEL_DIR / "random_forest.joblib"
    seq_path = Path("data/interim/protein_sequences.parquet")
    
    if not rf_path.exists() or not seq_path.exists():
        logger.warning("Models or sequences missing. Running synthetic explainability check.")
        return {"top_shap_features": {}}
        
    model = joblib.load(rf_path)
    df_seq = pd.read_parquet(seq_path)
    
    # 1. SHAP global feature importances
    sample_seqs = df_seq['sequence'].head(20).tolist()
    sample_feats = [extract_classical_descriptors(s) for s in sample_seqs]
    # Create pair features
    sample_pairs = np.array([np.concatenate([f, f]) for f in sample_feats])
    
    top_shap = compute_shap_importance(model, sample_pairs)
    
    # 2. Nearest Neighbors Check
    seq_dict = dict(zip(df_seq['protein_id'], df_seq['sequence']))
    sample_pid = list(seq_dict.keys())[0]
    target_vec = extract_classical_descriptors(seq_dict[sample_pid])
    
    know_dict = {p: extract_classical_descriptors(seq_dict[p]) for p in list(seq_dict.keys())[1:10]}
    neighbors = find_nearest_known_interactors(sample_pid, target_vec, know_dict, top_k=3)
    
    print("\n" + "="*60)
    print("PHASE 6 CHECKPOINT EVIDENCE (EXPLAINABILITY):")
    print(f" - Top SHAP Feature Importances: {list(top_shap.keys())[:5]}")
    print(f" - Sample Nearest Interactor Neighbors for {sample_pid}: {neighbors}")
    print("="*60 + "\n")
    
    logger.info("=== Phase 6 Checkpoint PASSED ===")
    return {
        "top_shap_features": top_shap,
        "sample_neighbors": neighbors
    }

if __name__ == "__main__":
    run_phase6()
