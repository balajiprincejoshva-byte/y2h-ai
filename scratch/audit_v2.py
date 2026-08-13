import os
import hashlib
import json
import pandas as pd
from Bio import SeqIO

def get_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def phase_0_audit():
    files_to_hash = [
        "reports/evaluation_results.json",
        "reports/ablation_results.json",
        "reports/run_manifest.json",
        "data/processed/saved_models/random_forest.joblib",
        "data/interim/positives_mapped.parquet",
        "data/processed/negatives_1to1.parquet",
        "data/processed/negatives_1to10.parquet",
        "data/processed/negatives_1to100.parquet",
        "data/interim/protein_sequences.parquet"
    ]
    
    audit = {}
    for f in files_to_hash:
        audit[f] = get_sha256(f)
        
    os.makedirs("reports", exist_ok=True)
    with open("reports/v2_state_hashes.json", "w") as f:
        json.dump(audit, f, indent=2)
    print("Phase 0 audit saved to reports/v2_state_hashes.json")

def phase_1_audit():
    # Total reference proteins
    fasta_path = "data/raw/yeast_reference_proteome.fasta"
    total_ref = 0
    if os.path.exists(fasta_path):
        for _ in SeqIO.parse(fasta_path, "fasta"):
            total_ref += 1

    # Proteins with sequences (current)
    seq_path = "data/interim/protein_sequences.parquet"
    if os.path.exists(seq_path):
        df_seq = pd.read_parquet(seq_path)
        proteins_with_sequences = df_seq['protein_id'].nunique()
        seq_proteins = set(df_seq['protein_id'])
    else:
        proteins_with_sequences = 0
        seq_proteins = set()

    # BioGRID proteins
    pos_path = "data/interim/biogrid_positives.parquet"
    if os.path.exists(pos_path):
        df_pos = pd.read_parquet(pos_path)
        biogrid_proteins = set(df_pos['protein_a']).union(set(df_pos['protein_b']))
        biogrid_count = len(biogrid_proteins)
    else:
        biogrid_proteins = set()
        biogrid_count = 0

    # Proteins mapped to BioGRID (mapped currently)
    # The proteins in biogrid that we HAVE a sequence for
    mapped_proteins = biogrid_proteins.intersection(seq_proteins)
    mapped_count = len(mapped_proteins)

    # Feature complete / model supported
    feature_complete_proteins = proteins_with_sequences
    model_supported_proteins = feature_complete_proteins

    coverage_fraction = model_supported_proteins / total_ref if total_ref > 0 else 0
    unresolved_proteins = list(biogrid_proteins - seq_proteins)

    report = {
        "organism": "Saccharomyces cerevisiae",
        "total_reference_proteins": total_ref,
        "proteins_with_sequences": proteins_with_sequences,
        "biogrid_proteins": biogrid_count,
        "mapped_proteins": mapped_count,
        "feature_complete_proteins": feature_complete_proteins,
        "model_supported_proteins": model_supported_proteins,
        "coverage_fraction": coverage_fraction,
        "unresolved_proteins_count": len(unresolved_proteins),
        "unresolved_sample": unresolved_proteins[:10]
    }

    with open("reports/sequence_coverage_audit.json", "w") as f:
        json.dump(report, f, indent=2)
    print("Phase 1 audit saved to reports/sequence_coverage_audit.json")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    phase_0_audit()
    phase_1_audit()
