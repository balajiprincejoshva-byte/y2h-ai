import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    """Config manager loading settings from YAML files."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.data_config = self._load_yaml("data.yaml")
        self.features_config = self._load_yaml("features.yaml")
        self.model_config = self._load_yaml("model.yaml")
        self.eval_config = self._load_yaml("eval.yaml")
        
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        filepath = self.config_dir / filename
        if not filepath.exists():
            return {}
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

config = ConfigManager()
