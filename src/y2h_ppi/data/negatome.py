import requests
import urllib3
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Set
from y2h_ppi.logger import logger
from y2h_ppi.data.manifest import update_manifest_entry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RAW_DIR = Path("data/raw")
INTERIM_DIR = Path("data/interim")
HEADERS = {'User-Agent': 'Mozilla/5.0'}

NEGATOME_STRUCT_URL = "https://mips.helmholtz-muenchen.de/proj/ppi/negatome/combined_stringent.txt"

def download_negatome(raw_dir: Path = RAW_DIR) -> Tuple[Path, str]:
    """Download Negatome dataset file."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    target_path = raw_dir / "negatome_combined_stringent.txt"
    
    if target_path.exists() and target_path.stat().st_size < 1000:
        target_path.unlink()
        
    if not target_path.exists():
        logger.info("Downloading Negatome 2.0 dataset...")
        url = NEGATOME_STRUCT_URL
        try:
            r = requests.get(url, headers=HEADERS, verify=False, timeout=30)
            r.raise_for_status()
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(r.text)
            logger.info(f"Downloaded Negatome dataset from {url} ({target_path.stat().st_size} bytes)")
        except Exception as e:
            logger.warning(f"Negatome download failed ({e}). Creating basic negatome reference.")
            with open(target_path, "w", encoding="utf-8") as f:
                f.write("ProteinA\tProteinB\n")
    else:
        url = NEGATOME_STRUCT_URL
        logger.info(f"Found cached Negatome file: {target_path}")
        
    return target_path, url

def process_negatome_yeast(mapped_sequences: Dict[str, str], raw_dir: Path = RAW_DIR, interim_dir: Path = INTERIM_DIR) -> pd.DataFrame:
    """Filter Negatome dataset to yeast-mappable non-interacting pairs."""
    interim_dir.mkdir(parents=True, exist_ok=True)
    target_path, url = download_negatome(raw_dir)
    
    try:
        df_raw = pd.read_csv(target_path, sep=r'\s+', header=None, names=['raw_a', 'raw_b'], comment='#', on_bad_lines='skip')
    except Exception:
        df_raw = pd.DataFrame(columns=['raw_a', 'raw_b'])
        
    raw_count = len(df_raw)
    logger.info(f"Loaded raw Negatome dataset rows: {raw_count}")
    
    valid_proteins: Set[str] = set(mapped_sequences.keys())
    
    pairs = []
    for _, row in df_raw.iterrows():
        p1, p2 = str(row['raw_a']).upper().strip(), str(row['raw_b']).upper().strip()
        if p1 in valid_proteins and p2 in valid_proteins and p1 != p2:
            pa, pb = min(p1, p2), max(p1, p2)
            pairs.append((pa, pb))
            
    df_negatome = pd.DataFrame(pairs, columns=['protein_a', 'protein_b']).drop_duplicates().reset_index(drop=True)
    df_negatome['label'] = 0
    
    final_count = len(df_negatome)
    logger.info(f"Found {final_count} yeast-mappable Negatome non-interacting pairs.")
    
    out_path = interim_dir / "negatome_yeast_negatives.parquet"
    df_negatome.to_parquet(out_path, index=False)
    
    update_manifest_entry(
        source_name="Negatome 2.0 Yeast Non-Interactions",
        url=url,
        version="Negatome 2.0 Stringent",
        raw_count=raw_count,
        filtered_count=final_count,
        description="Negatome non-interacting pairs mapped to S. cerevisiae proteome."
    )
    
    return df_negatome
