import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from y2h_ppi.logger import logger
from y2h_ppi.features.pair_representation import combine_pair_features
from y2h_ppi.features.cache import load_feature_cache
from y2h_ppi.splitting.protein_disjoint_split import create_c1_c2_c3_splits
from y2h_ppi.evaluation.metrics import evaluate_all_metrics

PROCESSED_DIR = Path("data/processed")
INTERIM_DIR = Path("data/interim")
REPORTS_DIR = Path("reports")

def run_ablation_study():
    """Run Feature Ablation Study: Classical vs ESM-2 vs Combined."""
    logger.info("=== Phase 6 Execution Started: Feature Ablation Study ===")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    pos_path = INTERIM_DIR / "positives_mapped.parquet"
    neg_1to1_path = PROCESSED_DIR / "negatives_1to1.parquet"
    seq_path = INTERIM_DIR / "protein_sequences.parquet"
    
    df_pos = pd.read_parquet(pos_path)
    df_pos['label'] = 1
    df_neg_1to1 = pd.read_parquet(neg_1to1_path)
    df_neg_1to1['label'] = 0
    df_seq = pd.read_parquet(seq_path)
    protein_list = sorted(df_seq['protein_id'].unique().tolist())
    
    classic_cache = load_feature_cache("classical")
    esm_cache = load_feature_cache("esm")
    
    if not classic_cache:
        logger.warning("Classical feature cache missing.")
        return
        
    if not esm_cache:
        logger.warning("ESM feature cache missing. Skipping ablation study.")
        return
        
    splits = create_c1_c2_c3_splits(df_pos, df_neg_1to1, protein_list, train_ratio=0.8, c1_test_fraction=0.1, seed=42)
    df_train = splits["train"]
    df_test_pools = {"c1": splits["c1_test"], "c2": splits["c2_test"], "c3": splits["c3_test"]}
    
    def get_features(df, cache_a, cache_b=None):
        X_list, y_list = [], []
        for _, row in df.iterrows():
            pa, pb, lbl = row['protein_a'], row['protein_b'], row['label']
            if pa in cache_a and pb in cache_a:
                if cache_b and pa in cache_b and pb in cache_b:
                    v_a = np.concatenate([cache_a[pa], cache_b[pa]])
                    v_b = np.concatenate([cache_a[pb], cache_b[pb]])
                else:
                    v_a = cache_a[pa]
                    v_b = cache_a[pb]
                pair_v = combine_pair_features(v_a, v_b)
                X_list.append(pair_v)
                y_list.append(lbl)
        if not X_list:
            return np.empty((0, 0)), np.empty((0,))
        return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.int32)
        
    feature_sets = {
        "Classical-Only": (classic_cache, None),
        "ESM-2-Only": (esm_cache, None),
        "Classical+ESM-2": (classic_cache, esm_cache)
    }
    
    ablation_results = {}
    
    for feat_name, caches in feature_sets.items():
        logger.info(f"Evaluating {feat_name} feature set...")
        cache_a, cache_b = caches
        X_train, y_train = get_features(df_train, cache_a, cache_b)
        
        rf = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        
        ablation_results[feat_name] = {}
        for pool_name, df_pool in df_test_pools.items():
            if df_pool.empty:
                continue
            X_pool, y_pool = get_features(df_pool, cache_a, cache_b)
            if len(X_pool) > 0:
                y_prob = rf.predict_proba(X_pool)[:, 1]
                metrics = evaluate_all_metrics(y_pool, y_prob)
                ablation_results[feat_name][pool_name] = metrics
                logger.info(f"  {pool_name} AUROC: {metrics['auroc']:.4f}")
                
    out_path = REPORTS_DIR / "ablation_results.json"
    with open(out_path, "w") as f:
        json.dump(ablation_results, f, indent=2)
        
    logger.info(f"Saved ablation results to {out_path}")

if __name__ == "__main__":
    run_ablation_study()
