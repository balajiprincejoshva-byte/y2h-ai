import numpy as np
from typing import Dict, Tuple
from sklearn.metrics import roc_auc_score, average_precision_score

def compute_bootstrap_ci(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_iterations: int = 1000,
    confidence_level: float = 0.95,
    seed: int = 42
) -> Dict[str, Tuple[float, float]]:
    """Compute 95% bootstrap confidence intervals for AUROC and AUPRC."""
    np.random.seed(seed)
    n_samples = len(y_true)
    if n_samples == 0:
        return {"auroc_ci": (0.0, 0.0), "auprc_ci": (0.0, 0.0)}
        
    auroc_scores = []
    auprc_scores = []
    
    alpha = (1.0 - confidence_level) / 2.0
    
    for _ in range(n_iterations):
        indices = np.random.choice(n_samples, size=n_samples, replace=True)
        sample_y = y_true[indices]
        sample_p = y_prob[indices]
        
        if len(set(sample_y)) > 1:
            try:
                auroc_scores.append(roc_auc_score(sample_y, sample_p))
            except Exception:
                pass
            try:
                auprc_scores.append(average_precision_score(sample_y, sample_p))
            except Exception:
                pass
                
    if auroc_scores:
        auroc_ci = (
            round(float(np.percentile(auroc_scores, alpha * 100)), 4),
            round(float(np.percentile(auroc_scores, (1.0 - alpha) * 100)), 4)
        )
    else:
        auroc_ci = (0.0, 0.0)
        
    if auprc_scores:
        auprc_ci = (
            round(float(np.percentile(auprc_scores, alpha * 100)), 4),
            round(float(np.percentile(auprc_scores, (1.0 - alpha) * 100)), 4)
        )
    else:
        auprc_ci = (0.0, 0.0)
        
    return {
        "auroc_ci": auroc_ci,
        "auprc_ci": auprc_ci
    }
