import re
import gzip
import requests
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple
from Bio import SeqIO
from y2h_ppi.logger import logger
from y2h_ppi.data.manifest import update_manifest_entry

RAW_DIR = Path("data/raw")
INTERIM_DIR = Path("data/interim")

SGD_FASTA_URL = "https://downloads.yeastgenome.org/sequence/S288C_reference/orf_protein/orf_trans_all.fasta.gz"
UNIPROT_FASTA_URL = "https://rest.uniprot.org/uniprotkb/stream?format=fasta&query=%28proteome%3AUP000002311%29"

def download_yeast_sequences(raw_dir: Path = RAW_DIR) -> Tuple[Path, str]:
    """Download yeast reference proteome FASTA file from SGD or UniProt."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    target_path = raw_dir / "yeast_reference_proteome.fasta"
    
    if target_path.exists() and target_path.stat().st_size > 1000000:
        logger.info(f"Found cached yeast reference FASTA: {target_path}")
        return target_path, SGD_FASTA_URL
    
    # Try downloading official SGD ORF protein translations FASTA first (100% yeast ORF match)
    logger.info("Downloading SGD yeast ORF protein translations FASTA...")
    try:
        r = requests.get(SGD_FASTA_URL, timeout=60)
        r.raise_for_status()
        gz_data = gzip.decompress(r.content).decode("utf-8")
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(gz_data)
        logger.info(f"Downloaded SGD reference proteome FASTA to {target_path}")
        return target_path, SGD_FASTA_URL
    except Exception as e:
        logger.warning(f"SGD FASTA download failed: {e}. Trying UniProt fallback...")
        
    # UniProt Fallback
    try:
        r = requests.get(UNIPROT_FASTA_URL, timeout=60)
        r.raise_for_status()
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(r.text)
        logger.info(f"Downloaded UniProt proteome FASTA to {target_path}")
        return target_path, UNIPROT_FASTA_URL
    except Exception as ex:
        logger.error(f"Failed downloading proteome FASTA: {ex}")
        raise ex

def parse_yeast_fasta(fasta_path: Path) -> Tuple[pd.DataFrame, int]:
    """Parse FASTA headers and map all ID variants to build canonical protein registry."""
    import hashlib
    
    registry = []
    total_parsed = 0
    
    with open(fasta_path, "r", encoding="utf-8") as handle:
        for record in SeqIO.parse(handle, "fasta"):
            total_parsed += 1
            seq = str(record.seq).upper().replace("*", "")
            if not seq:
                continue
                
            header = record.description
            words = header.split(" ")
            
            canonical_id = record.id.split("|")[1] if "|" in record.id else record.id
            canonical_id = canonical_id.upper()
            
            systematic_name = words[0].upper() if len(words) > 0 else canonical_id
            standard_name = words[1].upper() if len(words) > 1 and words[1].upper() != systematic_name and not words[1].startswith("SGDID:") else None
            
            sgdid = None
            for w in words:
                if w.startswith("SGDID:"):
                    sgdid = w.split(":")[1].strip(",")
                    
            seq_hash = hashlib.sha256(seq.encode('utf-8')).hexdigest()
            
            registry.append({
                "protein_id": systematic_name,
                "systematic_name": systematic_name,
                "standard_name": standard_name,
                "sgdid": sgdid,
                "sequence": seq,
                "sequence_length": len(seq),
                "sequence_hash": seq_hash,
                "mapping_status": "canonical"
            })
            
    df_registry = pd.DataFrame(registry)
    
    # Check duplicates and mark ambiguous if multiple sequences map to same ID
    # In SGD this shouldn't happen for systematic names, but just in case:
    df_registry = df_registry.drop_duplicates(subset=["protein_id"])
    
    logger.info(f"Parsed {total_parsed} FASTA records. Built registry of {len(df_registry)} canonical proteins.")
    return df_registry, total_parsed

def map_sequences_to_positives(positives_df: pd.DataFrame, raw_dir: Path = RAW_DIR, interim_dir: Path = INTERIM_DIR) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """Map protein sequences to BioGRID positive pairs and log mapping statistics."""
    fasta_path, url = download_yeast_sequences(raw_dir)
    df_registry, raw_fasta_count = parse_yeast_fasta(fasta_path)
    
    # Save canonical registry and the minimal sequence parquet expected by downstream steps
    # We now write to data/processed for the registry
    processed_dir = Path("data/processed")
    processed_dir.mkdir(exist_ok=True, parents=True)
    
    df_registry.to_parquet(processed_dir / "yeast_protein_registry.parquet", index=False)
    
    # seq_df is required by current downstream (it expects 'protein_id' and 'sequence')
    seq_df = df_registry[['protein_id', 'sequence']].copy()
    seq_df.to_parquet(interim_dir / "protein_sequences.parquet", index=False)
    
    seq_dict = dict(zip(seq_df['protein_id'], seq_df['sequence']))
    
    # Interaction sequence coverage
    all_proteins = set(positives_df['protein_a']).union(set(positives_df['protein_b']))
    mapped_proteins = {p: seq_dict[p] for p in all_proteins if p in seq_dict}
    
    coverage = len(mapped_proteins) / len(all_proteins) if all_proteins else 0.0
    logger.info(f"BioGRID interaction sequence mapping coverage: {len(mapped_proteins)} / {len(all_proteins)} ({coverage:.2%})")
    
    positives_mapped = positives_df[
        positives_df['protein_a'].isin(mapped_proteins) & 
        positives_df['protein_b'].isin(mapped_proteins)
    ].copy().reset_index(drop=True)
    
    logger.info(f"BioGRID positive pairs after sequence mapping filter: {len(positives_mapped)} pairs.")
    
    positives_mapped.to_parquet(interim_dir / "positives_mapped.parquet", index=False)
    
    import json
    coverage_report = {
        "total_biogrid_interaction_pairs": len(positives_df),
        "pairs_with_both_sequences_available": len(positives_mapped),
        "coverage_percentage": len(positives_mapped) / len(positives_df) if len(positives_df) > 0 else 0
    }
    with open("reports/interaction_sequence_coverage.json", "w") as f:
        json.dump(coverage_report, f, indent=2)
    
    update_manifest_entry(
        source_name="SGD Yeast Proteome Sequences",
        url=url,
        version="SGD Reference Proteome",
        raw_count=raw_fasta_count,
        filtered_count=len(df_registry),
        description=f"Complete Yeast canonical proteome ingested ({len(df_registry)} proteins)."
    )
    
    return positives_mapped, seq_dict
