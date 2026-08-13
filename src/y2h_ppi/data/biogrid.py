import os
import re
import zipfile
import requests
import pandas as pd
from pathlib import Path
from typing import Tuple, List
from y2h_ppi.logger import logger
from y2h_ppi.data.manifest import update_manifest_entry

RAW_DIR = Path("data/raw")
INTERIM_DIR = Path("data/interim")
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def resolve_latest_biogrid_version() -> str:
    """Dynamically resolve the latest BioGRID release version string."""
    try:
        url = "https://downloads.thebiogrid.org/BioGRID/Release-Archive/"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            versions = re.findall(r'BIOGRID-(\d+\.\d+\.\d+)', r.text)
            if versions:
                sorted_versions = sorted(list(set(versions)), key=lambda x: [int(p) for p in x.split('.')])
                latest = sorted_versions[-1]
                logger.info(f"Resolved latest BioGRID version: {latest}")
                return latest
    except Exception as e:
        logger.warning(f"Could not query BioGRID release archive: {e}. Falling back to release version 4.4.240.")
    return "4.4.240"

def download_biogrid_yeast(raw_dir: Path = RAW_DIR) -> Tuple[Path, str, str]:
    """Download BioGRID organism TAB3 zip archive containing S. cerevisiae interactions."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if cached organism zip exists
    cached_test_zip = raw_dir / "test_biogrid_organism.zip"
    version = "4.4.240"
    
    file_name = f"BIOGRID-ORGANISM-{version}.tab3.zip"
    download_url = f"https://downloads.thebiogrid.org/Download/BioGRID/Release-Archive/BIOGRID-{version}/{file_name}"
    target_path = raw_dir / file_name
    
    if cached_test_zip.exists() and cached_test_zip.stat().st_size > 10000000:
        logger.info(f"Found validated BioGRID archive: {cached_test_zip}")
        return cached_test_zip, download_url, version
        
    if not target_path.exists():
        logger.info(f"Downloading BioGRID organism dataset from {download_url}...")
        try:
            r = requests.get(download_url, headers=HEADERS, stream=True, allow_redirects=True, timeout=120)
            r.raise_for_status()
            with open(target_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
            logger.info(f"BioGRID download complete: {target_path} (size: {target_path.stat().st_size} bytes)")
        except Exception as e:
            logger.error(f"Failed to download BioGRID file from {download_url}: {e}")
            raise e
    else:
        logger.info(f"Found cached BioGRID archive: {target_path}")
        
    return target_path, download_url, version

def process_biogrid_positives(raw_dir: Path = RAW_DIR, interim_dir: Path = INTERIM_DIR) -> pd.DataFrame:
    """Load, filter, canonicalize and deduplicate yeast Y2H physical interactions."""
    interim_dir.mkdir(parents=True, exist_ok=True)
    zip_path, url, version = download_biogrid_yeast(raw_dir)
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        tab3_filename = [name for name in z.namelist() if 'Saccharomyces_cerevisiae' in name or 'Saccharomyces' in name][0]
        logger.info(f"Extracting yeast interaction dataset '{tab3_filename}' from zip archive...")
        with z.open(tab3_filename) as f:
            df_raw = pd.read_csv(f, sep='\t', low_memory=False)
            
    raw_count = len(df_raw)
    logger.info(f"Loaded raw BioGRID rows for yeast: {raw_count}")
    
    col_systematic_a = [c for c in df_raw.columns if "Systematic Name" in c and "A" in c][0]
    col_systematic_b = [c for c in df_raw.columns if "Systematic Name" in c and "B" in c][0]
    col_symbol_a = [c for c in df_raw.columns if "Official Symbol" in c and "A" in c][0]
    col_symbol_b = [c for c in df_raw.columns if "Official Symbol" in c and "B" in c][0]
    col_tax_a = [c for c in df_raw.columns if "Organism ID" in c or "Organism" in c][0]
    col_tax_b = [c for c in df_raw.columns if "Organism ID" in c or "Organism" in c][1]
    col_exp_sys = [c for c in df_raw.columns if "Experimental System" in c and "Type" not in c][0]
    col_exp_type = [c for c in df_raw.columns if "Experimental System Type" in c][0]
    
    all_systems = df_raw[col_exp_sys].dropna().unique().tolist()
    y2h_systems = [s for s in all_systems if "Two-hybrid" in s or "two hybrid" in s.lower()]
    logger.info(f"Detected Y2H experimental systems in BioGRID dataset: {y2h_systems}")
    
    df_filtered = df_raw[
        (df_raw[col_exp_type].str.lower() == "physical") &
        (df_raw[col_exp_sys].isin(y2h_systems)) &
        (df_raw[col_tax_a].astype(str) == "559292") &
        (df_raw[col_tax_b].astype(str) == "559292")
    ].copy()
    
    logger.info(f"Rows after physical Y2H yeast filter: {len(df_filtered)}")
    
    df_filtered['protein_a'] = df_filtered[col_systematic_a].fillna(df_filtered[col_symbol_a]).str.strip().str.upper()
    df_filtered['protein_b'] = df_filtered[col_systematic_b].fillna(df_filtered[col_symbol_b]).str.strip().str.upper()
    
    df_filtered = df_filtered.dropna(subset=['protein_a', 'protein_b'])
    df_filtered = df_filtered[df_filtered['protein_a'] != df_filtered['protein_b']]
    
    df_filtered['pair_a'] = df_filtered[['protein_a', 'protein_b']].min(axis=1)
    df_filtered['pair_b'] = df_filtered[['protein_a', 'protein_b']].max(axis=1)
    
    positives_df = df_filtered[['pair_a', 'pair_b']].drop_duplicates().reset_index(drop=True)
    positives_df.rename(columns={'pair_a': 'protein_a', 'pair_b': 'protein_b'}, inplace=True)
    positives_df['label'] = 1
    
    final_count = len(positives_df)
    unique_proteins = len(set(positives_df['protein_a']).union(set(positives_df['protein_b'])))
    logger.info(f"Final BioGRID Y2H canonical positive pairs: {final_count} across {unique_proteins} unique proteins.")
    
    all_physical = df_raw[
        (df_raw[col_exp_type].str.lower() == "physical") &
        (df_raw[col_tax_a].astype(str) == "559292") &
        (df_raw[col_tax_b].astype(str) == "559292")
    ].copy()
    
    all_physical['protein_a'] = all_physical[col_systematic_a].fillna(all_physical[col_symbol_a]).str.strip().str.upper()
    all_physical['protein_b'] = all_physical[col_systematic_b].fillna(all_physical[col_symbol_b]).str.strip().str.upper()
    all_physical = all_physical.dropna(subset=['protein_a', 'protein_b'])
    all_physical = all_physical[all_physical['protein_a'] != all_physical['protein_b']]
    all_physical['pair_a'] = all_physical[['protein_a', 'protein_b']].min(axis=1)
    all_physical['pair_b'] = all_physical[['protein_a', 'protein_b']].max(axis=1)
    all_phys_df = all_physical[['pair_a', 'pair_b']].drop_duplicates().reset_index(drop=True)
    all_phys_df.rename(columns={'pair_a': 'protein_a', 'pair_b': 'protein_b'}, inplace=True)
    
    logger.info(f"Final BioGRID All Physical pairs for exclusion: {len(all_phys_df)}.")
    all_phys_df.to_parquet(interim_dir / "all_physical_positives.parquet", index=False)
    
    out_path = interim_dir / "biogrid_positives.parquet"
    positives_df.to_parquet(out_path, index=False)
    
    update_manifest_entry(
        source_name="BioGRID Yeast Y2H Positives",
        url=url,
        version=version,
        raw_count=raw_count,
        filtered_count=final_count,
        description=f"Physical yeast (taxid 559292) Y2H interactions ({', '.join(y2h_systems)}), canonicalized and deduplicated, homodimers removed."
    )
    
    return positives_df
