import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator


from y2h_ppi.logger import logger

class BaselineMLPipeline:
    """Classic ML classifiers (Logistic Regression, Random Forest)."""
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.models = {}
        
    def train_logistic_regression(self, X_train: np.ndarray, y_train: np.ndarray) -> LogisticRegression:
        logger.info("Training Logistic Regression baseline...")
        model = LogisticRegression(max_iter=1000, C=1.0, random_state=self.random_state, class_weight='balanced')
        model.fit(X_train, y_train)
        self.models['logistic_regression'] = model
        return model
        
    def train_random_forest(self, X_train: np.ndarray, y_train: np.ndarray, n_estimators: int = 100, max_depth: int = 12) -> RandomForestClassifier:
        logger.info("Training Random Forest baseline...")
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=self.random_state,
            class_weight='balanced',
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        self.models['random_forest'] = model
        return model
        
    def calibrate_model(self, model_name: str, X_val: np.ndarray, y_val: np.ndarray, method: str = 'isotonic') -> CalibratedClassifierCV:
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found.")
        logger.info(f"Calibrating {model_name} using {method} scaling on validation set...")
        base_model = self.models[model_name]
        calibrated_model = CalibratedClassifierCV(estimator=FrozenEstimator(base_model), method=method)
        calibrated_model.fit(X_val, y_val)
        self.models[model_name] = calibrated_model
        return calibrated_model
        

    def save_model(self, model_name: str, save_dir: Path):
        save_dir.mkdir(parents=True, exist_ok=True)
        if model_name in self.models:
            filepath = save_dir / f"{model_name}.joblib"
            joblib.dump(self.models[model_name], filepath)
            logger.info(f"Saved model '{model_name}' to {filepath}")
            
    def load_model(self, model_name: str, save_dir: Path) -> Any:
        filepath = save_dir / f"{model_name}.joblib"
        if filepath.exists():
            model = joblib.load(filepath)
            self.models[model_name] = model
            logger.info(f"Loaded model '{model_name}' from {filepath}")
            return model
        return None
