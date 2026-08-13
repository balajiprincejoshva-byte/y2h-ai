import json
import uuid
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

MANIFEST_PATH = Path("reports/v3_run_manifest.json")

def _hash_file(filepath: Path) -> str:
    if not filepath.exists():
        return "MISSING"
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def generate_run_manifest(
    split_seed: int,
    model_seed: int,
    negative_sampling_seed: int,
    model_version: str = "v3.0-RF/LR",
    feature_version: str = "v3.0-Classical+ESM",
    evaluation_version: str = "v3.0-Park-Marcotte"
) -> Dict[str, Any]:
    
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    manifest = {
        "run_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": "N/A",
        "python_version": sys.version,
        "dependency_lock_hash": _hash_file(Path("requirements.txt")),
        "dataset_hash": _hash_file(Path("data/interim/biogrid_positives.parquet")),
        "feature_hash": _hash_file(Path("data/interim/features_cache/classical_features.parquet")),
        "split_seed": split_seed,
        "model_seed": model_seed,
        "negative_sampling_seed": negative_sampling_seed,
        "model_version": model_version,
        "feature_version": feature_version,
        "evaluation_version": evaluation_version
    }
    
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    return manifest
