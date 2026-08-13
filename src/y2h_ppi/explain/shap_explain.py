import numpy as np
from typing import Dict, Any, List
from y2h_ppi.logger import logger

def compute_shap_importance(model: Any, X_sample: np.ndarray, feature_names: List[str] = None) -> Dict[str, float]:
    """Compute global feature importance using SHAP TreeExplainer or model feature importances."""
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
    except Exception as e:
        logger.warning(f"SHAP TreeExplainer failed or unavailable ({e}). Using tree feature importances.")
        if hasattr(model, 'feature_importances_'):
            mean_abs_shap = model.feature_importances_
        else:
            mean_abs_shap = np.ones(X_sample.shape[1]) / X_sample.shape[1]
            
    # Ensure mean_abs_shap is 1D array
    mean_abs_shap = np.asarray(mean_abs_shap).ravel()
    
    if feature_names is None or len(feature_names) != len(mean_abs_shap):
        feature_names = [f"feat_{idx}" for idx in range(len(mean_abs_shap))]
        
    top_indices = np.argsort(mean_abs_shap)[::-1][:15]
    result_dict = {}
    for idx in top_indices:
        i = int(np.asarray(idx).item())
        result_dict[feature_names[i]] = round(float(mean_abs_shap[i]), 4)
    return result_dict
