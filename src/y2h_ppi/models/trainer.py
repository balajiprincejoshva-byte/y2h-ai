import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple
from y2h_ppi.logger import logger
from y2h_ppi.features.pair_representation import combine_pair_features
from y2h_ppi.features.cache import load_feature_cache
from y2h_ppi.models.baseline_ml import BaselineMLPipeline
from y2h_ppi.splitting.protein_disjoint_split import create_c1_c2_c3_splits

PROCESSED_DIR = Path("data/processed")
MODEL_DIR = PROCESSED_DIR / "saved_models"

def run_phase4() -> dict:
    """Run Phase 4: Fast Model Training using cached protein features."""
    logger.info("=== Phase 4 Execution Started: Model Training ===")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    pos_path = Path("data/interim/positives_mapped.parquet")
    neg_path = PROCESSED_DIR / "negatives_v3_1to1.parquet"
    
    if not pos_path.exists() or not neg_path.exists():
        raise FileNotFoundError("Prerequisite datasets missing. Run Phase 1 & Phase 2 first.")
        
    df_pos = pd.read_parquet(pos_path)
    df_neg = pd.read_parquet(neg_path)
    
    df_pos['label'] = 1
    df_neg['label'] = 0
    
    # Load sequences to get unique proteins
    seq_path = Path("data/interim/protein_sequences.parquet")
    df_seq = pd.read_parquet(seq_path)
    protein_list = sorted(df_seq['protein_id'].unique().tolist())
    
    # Create strict protein-disjoint splits to ensure no C2/C3 leakage into saved models
    splits = create_c1_c2_c3_splits(df_pos, df_neg, protein_list, train_ratio=0.8, c1_test_fraction=0.1, seed=42)
    df_train = splits["train"]
    df_val = splits["c1_test"]  # Use C1 test as validation for calibration
    
    # Load cached protein feature dictionary for instantaneous lookup
    classic_cache = load_feature_cache("classical")
    if not classic_cache:
        raise FileNotFoundError("Classical feature cache missing. Run Phase 3 first.")
        
    logger.info(f"Loaded {len(classic_cache)} protein feature vectors from cache.")
    
    def get_features_and_labels(df):
        X_list, y_list = [], []
        for _, row in df.iterrows():
            pa, pb, lbl = row['protein_a'], row['protein_b'], row['label']
            if pa in classic_cache and pb in classic_cache:
                pair_vec = combine_pair_features(classic_cache[pa], classic_cache[pb])
                X_list.append(pair_vec)
                y_list.append(lbl)
        if not X_list:
            return np.empty((0, 0)), np.empty((0,))
        return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.int32)
        
    X_train, y_train = get_features_and_labels(df_train)
    X_val, y_val = get_features_and_labels(df_val)
    
    logger.info(f"Built training dataset matrix X: {X_train.shape}, y: {y_train.shape}")
    
    # 1. Train and Calibrate Random Forest Baseline Model
    ml_pipe = BaselineMLPipeline(random_state=42)
    rf_model = ml_pipe.train_random_forest(X_train, y_train, n_estimators=50, max_depth=10)
    ml_pipe.models["random_forest_v3"] = ml_pipe.models.pop("random_forest")
    ml_pipe.calibrate_model("random_forest_v3", X_val, y_val, method="isotonic")
    ml_pipe.save_model("random_forest_v3", MODEL_DIR)
    
    # 2. Train and Calibrate Logistic Regression
    lr_model = ml_pipe.train_logistic_regression(X_train, y_train)
    ml_pipe.models["logistic_regression_v3"] = ml_pipe.models.pop("logistic_regression")
    ml_pipe.calibrate_model("logistic_regression_v3", X_val, y_val, method="isotonic")
    ml_pipe.save_model("logistic_regression_v3", MODEL_DIR)
    
    # 3. Reload saved model & run inference verification on sample pair
    reloaded_rf = joblib.load(MODEL_DIR / "random_forest_v3.joblib")
    sample_pair_x = X_val[0:1]
    sample_pred_prob = float(reloaded_rf.predict_proba(sample_pair_x)[0, 1])
    sample_true_label = int(y_val[0])
    
    print("\n" + "="*60)
    print("PHASE 4 CHECKPOINT EVIDENCE:")
    print(f" - Trained & Saved Models: Random Forest, Logistic Regression ({MODEL_DIR})")
    print(f" - Reloaded Model Verification Test:")
    print(f"   * Sample Pair True Label: {sample_true_label}")
    print(f"   * Reloaded Random Forest Predicted Probability: {sample_pred_prob:.4f}")
    print("="*60 + "\n")
    
    logger.info("=== Phase 4 Checkpoint PASSED ===")
    return {
        "models_saved": ["random_forest", "logistic_regression"],
        "sample_pred_prob": sample_pred_prob
    }

if __name__ == "__main__":
    run_phase4()
