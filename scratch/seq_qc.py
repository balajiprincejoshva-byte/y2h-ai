import os
import json
import pandas as pd
from pathlib import Path

def run_sequence_qc(registry_path="data/processed/yeast_protein_registry.parquet", report_path="reports/sequence_quality_report.json"):
    if not os.path.exists(registry_path):
        print(f"File not found: {registry_path}")
        return
        
    df = pd.read_parquet(registry_path)
    
    total_records = len(df)
    
    # 1. Check duplicate IDs
    duplicate_ids = df[df.duplicated(subset=['protein_id'], keep=False)]['protein_id'].unique().tolist()
    
    # 2. Check duplicate sequences
    duplicate_seqs = df[df.duplicated(subset=['sequence'], keep=False)]['protein_id'].unique().tolist()
    
    # 3. Check invalid characters (standard 20 amino acids + B, Z, J, X, U, O)
    # Typically only ACDEFGHIKLMNPQRSTVWY are expected, but B,Z,X,U,O can appear.
    # Let's check for anything that is not an uppercase English letter.
    invalid_records = []
    valid_alphabet = set("ACDEFGHIKLMNPQRSTVWYBZJXUO")
    
    missing_seqs = []
    
    for _, row in df.iterrows():
        seq = str(row['sequence']).upper()
        if not seq or seq == "NAN" or seq == "NONE":
            missing_seqs.append(row['protein_id'])
            continue
            
        invalid_chars = set(seq) - valid_alphabet
        if invalid_chars:
            invalid_records.append({
                "protein_id": row['protein_id'],
                "invalid_chars": list(invalid_chars)
            })
            
    # Ambiguous mappings
    ambiguous_mappings = df[df['mapping_status'] == 'ambiguous']['protein_id'].tolist() if 'mapping_status' in df.columns else []
    
    valid_records = total_records - len(invalid_records) - len(missing_seqs) - len(ambiguous_mappings)
    
    report = {
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records_count": len(invalid_records),
        "duplicate_ids": duplicate_ids,
        "duplicate_sequences_count": len(duplicate_seqs),
        "ambiguous_mappings": ambiguous_mappings,
        "missing_sequences": missing_seqs,
        "invalid_characters_examples": invalid_records[:5]
    }
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"Sequence QC complete. Report saved to {report_path}")

if __name__ == "__main__":
    run_sequence_qc()
