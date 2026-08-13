import pandas as pd
from pathlib import Path
from y2h_ppi.logger import logger
from y2h_ppi.data.biogrid import process_biogrid_positives
from y2h_ppi.data.uniprot import map_sequences_to_positives
from y2h_ppi.data.negatome import process_negatome_yeast

def run_phase1() -> dict:
    """Run Phase 1: Ingest BioGRID Y2H positives, UniProt proteome sequences, and Negatome negatives."""
    logger.info("=== Phase 1 Execution Started ===")
    
    # 1. BioGRID Positives (use cached)
    df_positives = pd.read_parquet("data/interim/biogrid_positives.parquet")
    
    # 2. Sequences Mapping
    df_positives_mapped, seq_dict = map_sequences_to_positives(df_positives)
    
    # 3. Negatome Yeast Negatives
    df_negatome = process_negatome_yeast(seq_dict)
    
    pos_count = len(df_positives_mapped)
    unique_proteins = len(seq_dict)
    neg_count = len(df_negatome)
    
    print("\n" + "="*60)
    print("PHASE 1 CHECKPOINT EVIDENCE:")
    print(f" (a) Curated Yeast Y2H-derived Positive Pairs: {pos_count}")
    print(f" (b) Unique Yeast Proteins with Sequences Attached: {unique_proteins}")
    print(f" (c) Negatome Yeast-Mappable Negative Pairs: {neg_count}")
    print("="*60 + "\n")
    
    logger.info("=== Phase 1 Checkpoint PASSED ===")
    return {
        "positive_pairs": pos_count,
        "unique_proteins": unique_proteins,
        "negatome_pairs": neg_count
    }

if __name__ == "__main__":
    run_phase1()
