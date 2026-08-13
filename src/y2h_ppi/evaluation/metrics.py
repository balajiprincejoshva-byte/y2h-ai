import numpy as np
from typing import Dict, Any, List
from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_score,
    recall_score, f1_score, matthews_corrcoef
)
from sklearn.calibration import calibration_curve

def compute_precision_at_k(y_true: np.ndarray, y_prob: np.ndarray, k: int) -> float:
    """Compute Precision@K for top-K ranked predicted probabilities."""
    if len(y_true) == 0 or k <= 0:
        return 0.0
    top_indices = np.argsort(y_prob)[::-1][:k]
    return float(np.mean(y_true[top_indices]))

def evaluate_all_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> Dict[str, Any]:
    """Compute comprehensive evaluation metrics (AUROC, AUPRC, Precision, Recall, F1, MCC, P@K)."""
    if len(y_true) == 0:
        return {}
        
    y_pred = (y_prob >= threshold).astype(int)
    
    try:
        auroc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        auroc = 0.5
        
    try:
        auprc = float(average_precision_score(y_true, y_prob))
    except Exception:
        auprc = 0.0
        
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    mcc = float(matthews_corrcoef(y_true, y_pred)) if len(set(y_true)) > 1 else 0.0
    
    p_at_50 = compute_precision_at_k(y_true, y_prob, 50)
    p_at_100 = compute_precision_at_k(y_true, y_prob, 100)
    p_at_500 = compute_precision_at_k(y_true, y_prob, 500)
    
    # Calibration Curve (prob_true, prob_pred)
    try:
        prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=10, strategy='uniform')
        calib_data = {"prob_true": prob_true.tolist(), "prob_pred": prob_pred.tolist()}
    except Exception:
        calib_data = {"prob_true": [], "prob_pred": []}
        
    return {
        "auroc": round(auroc, 4),
        "auprc": round(auprc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "mcc": round(mcc, 4),
        "precision_at_50": round(p_at_50, 4),
        "precision_at_100": round(p_at_100, 4),
        "precision_at_500": round(p_at_500, 4),
        "calibration": calib_data
    }
