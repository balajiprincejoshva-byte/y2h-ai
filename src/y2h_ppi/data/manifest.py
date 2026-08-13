import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
from y2h_ppi.logger import logger

MANIFEST_PATH = Path("data/raw/manifest.json")

def init_manifest() -> Dict[str, Any]:
    """Initialize or load existing data manifest."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    if MANIFEST_PATH.exists():
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not read existing manifest: {e}. Creating fresh manifest.")
    
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "sources": {}
    }
    save_manifest(manifest)
    return manifest

def update_manifest_entry(source_name: str, url: str, version: str, raw_count: int, filtered_count: int, description: str):
    """Add or update a dataset provenance entry in manifest.json."""
    manifest = init_manifest()
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    manifest["sources"][source_name] = {
        "url": url,
        "access_timestamp": datetime.now(timezone.utc).isoformat(),
        "version": version,
        "raw_row_count": raw_count,
        "post_filter_row_count": filtered_count,
        "filter_description": description
    }
    save_manifest(manifest)
    logger.info(f"Updated manifest entry for '{source_name}': {filtered_count} records recorded.")

def save_manifest(manifest: Dict[str, Any]):
    """Save manifest dictionary to data/raw/manifest.json."""
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
