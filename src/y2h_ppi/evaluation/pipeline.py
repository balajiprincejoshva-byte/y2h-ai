import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any
from sklearn.metrics import roc_auc_score, average_precision_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from y2h_ppi.logger import logger
from y2h_ppi.features.pair_representation import combine_pair_features
from y2h_ppi.features.cache import load_feature_cache
from y2h_ppi.splitting.protein_disjoint_split import create_c1_c2_c3_splits
from y2h_ppi.evaluation.hub_baseline import HubDegreeBaseline
from y2h_ppi.evaluation.metrics import evaluate_all_metrics
from y2h_ppi.evaluation.bootstrap import compute_bootstrap_ci
from y2h_ppi.evaluation.run_manifest import generate_run_manifest

PROCESSED_DIR = Path("data/processed")
INTERIM_DIR = Path("data/interim")
REPORTS_DIR = Path("reports")

class RandomBaseline:
    def predict_proba(self, df_pairs: pd.DataFrame) -> np.ndarray:
        np.random.seed(42)
        return np.random.uniform(0, 1, size=len(df_pairs))

def run_phase5() -> dict:
    """Run Phase 5: Rigorous Park & Marcotte (2012) C1/C2/C3 Protein-Disjoint Evaluation."""
    logger.info("=== Phase 5 Execution Started: Rigorous Evaluation ===")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    pos_path = INTERIM_DIR / "positives_mapped.parquet"
    seq_path = INTERIM_DIR / "protein_sequences.parquet"
    
    if not pos_path.exists() or not seq_path.exists():
        raise FileNotFoundError("Required dataset files missing. Please run Phase 1 - Phase 4 first.")
        
    df_pos = pd.read_parquet(pos_path)
    df_pos['label'] = 1
    
    df_seq = pd.read_parquet(seq_path)
    protein_list = sorted(df_seq['protein_id'].unique().tolist())
    
    classic_cache = load_feature_cache("classical")
    if not classic_cache:
        raise FileNotFoundError("Classical feature cache missing.")
        
    # Generate run manifest
    manifest = generate_run_manifest(split_seed=42, model_seed=42, negative_sampling_seed=42)
    
    def get_features_and_labels_fast(df: pd.DataFrame):
        X_list, y_list = [], []
        for _, row in df.iterrows():
            pa, pb, lbl = row['protein_a'], row['protein_b'], row['label']
            if pa in classic_cache and pb in classic_cache:
                pair_v = combine_pair_features(classic_cache[pa], classic_cache[pb])
                X_list.append(pair_v)
                y_list.append(lbl)
        if not X_list:
            return np.empty((0, 0)), np.empty((0,))
        return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.int32)
    
    eval_results = {"models": {}, "manifest": manifest}
    
    # We will evaluate across 3 imbalances
    imbalances = {
        "1to1_balanced": "negatives_v3_1to1.parquet",
        "1to10_imbalanced": "negatives_v3_1to10.parquet",
        "1to100_imbalanced": "negatives_v3_1to100.parquet"
    }
    
    # First, load the models trained by Phase 4
    model_dir = PROCESSED_DIR / "saved_models"
    rf_model = joblib.load(model_dir / "random_forest_v3.joblib")
    lr_model = joblib.load(model_dir / "logistic_regression_v3.joblib")
    
    models = {
        "RandomForest": rf_model,
        "LogisticRegression": lr_model,
        "DegreeHubBaseline": HubDegreeBaseline(),
        "RandomBaseline": RandomBaseline()
    }
    
    for model_name in models.keys():
        eval_results["models"][model_name] = {"c1": {}, "c2": {}, "c3": {}}
        
    for imbalance_name, neg_file in imbalances.items():
        neg_path = PROCESSED_DIR / neg_file
        if not neg_path.exists():
            logger.warning(f"Skipping {imbalance_name} evaluation, missing {neg_file}")
            continue
            
        df_neg = pd.read_parquet(neg_path)
        df_neg['label'] = 0
        
        # Must re-create splits using the exact same seed to maintain C1/C2/C3 consistency
        splits = create_c1_c2_c3_splits(df_pos, df_neg, protein_list, train_ratio=0.8, c1_test_fraction=0.1, seed=42)
        
        test_pools = {
            "c1": splits["c1_test"],
            "c2": splits["c2_test"],
            "c3": splits["c3_test"]
        }
        
        # Fit DegreeHubBaseline on the current train split
        models["DegreeHubBaseline"].fit(splits["train"][splits["train"]['label'] == 1])
        
        for model_name, model_obj in models.items():
            for pool_name, df_pool in test_pools.items():
                if df_pool.empty:
                    continue
                    
                X_pool, y_pool = get_features_and_labels_fast(df_pool)
                
                if model_name in ["DegreeHubBaseline", "RandomBaseline"]:
                    y_prob = model_obj.predict_proba(df_pool)
                else:
                    y_prob = model_obj.predict_proba(X_pool)[:, 1]
                    
                metrics = evaluate_all_metrics(y_pool, y_prob)
                # Compute rigorous bootstrap CIs
                ci = compute_bootstrap_ci(y_pool, y_prob, n_iterations=200)
                metrics["auroc_ci"] = ci["auroc_ci"]
                metrics["auprc_ci"] = ci["auprc_ci"]
                
                eval_results["models"][model_name][pool_name][imbalance_name] = metrics
                logger.info(f"{model_name} {pool_name} {imbalance_name}: AUROC={metrics['auroc']:.4f}")

    out_path = REPORTS_DIR / "v3_evaluation_results.json"
    import json
    with open(out_path, "w") as f:
        json.dump(eval_results, f, indent=2)
        
    logger.info(f"=== Phase 5 Checkpoint PASSED. Canonical results saved to {out_path} ===")
    return eval_results

if __name__ == "__main__":
    run_phase5()
