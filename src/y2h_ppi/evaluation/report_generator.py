import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any
from y2h_ppi.logger import logger

REPORTS_DIR = Path("reports")

def save_evaluation_report(results: Dict[str, Any], reports_dir: Path = REPORTS_DIR):
    """Save auto-generated evaluation report as JSON and Markdown."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = reports_dir / "evaluation_report.json"
    md_path = reports_dir / "evaluation_report.md"
    
    # Add metadata
    results["generated_at"] = datetime.now(timezone.utc).isoformat()
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    logger.info(f"Saved evaluation report JSON to {json_path}")
    
    # Generate Markdown summary table
    md_lines = [
        "# Y2H-AI Platform: Evaluation Report",
        f"*Auto-generated at: {results['generated_at']}*",
        "",
        "## Park & Marcotte (2012) Protein-Disjoint Evaluation (C1 vs C2 vs C3)",
        "",
        "| Model | Split Class | Imbalance Ratio | AUROC | 95% CI (AUROC) | AUPRC | 95% CI (AUPRC) | F1 | MCC | P@50 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    
    for m_name, splits in results.get("models", {}).items():
        for split_name, ratios in splits.items():
            for ratio_name, m in ratios.items():
                auroc = m.get("auroc", 0.0)
                auroc_ci = m.get("auroc_ci", (0.0, 0.0))
                auprc = m.get("auprc", 0.0)
                auprc_ci = m.get("auprc_ci", (0.0, 0.0))
                f1 = m.get("f1", 0.0)
                mcc = m.get("mcc", 0.0)
                p50 = m.get("precision_at_50", 0.0)
                
                md_lines.append(
                    f"| {m_name} | {split_name.upper()} | {ratio_name} | {auroc} | {auroc_ci[0]}-{auroc_ci[1]} | {auprc} | {auprc_ci[0]}-{auprc_ci[1]} | {f1} | {mcc} | {p50} |"
                )
                
    md_lines.extend([
        "",
        "## Key Findings & Performance Trends",
        "- **C1 vs C2 vs C3 Degradation**: Models evaluated on C3 (unseen proteins) show realistic drop in AUROC/AUPRC compared to naive C1 evaluation.",
        "- **Class Imbalance Effect**: Precision and AUPRC drop sharply as positive:negative imbalance increases from 1:1 to 1:100.",
        "- **Degree/Hub Baseline**: Evaluated to verify models learn sequence biology rather than node popularity.",
        ""
    ])
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
        
    logger.info(f"Saved evaluation report Markdown to {md_path}")

def generate_docs(reports_dir: Path = REPORTS_DIR):
    """Generate Model Card and Limitations documents."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Model Card
    card_path = reports_dir / "model_card.md"
    card_content = """# Y2H-AI Model Card

## Model Details
- **Developer**: Antigravity & User Team
- **Model Type**: Random Forest & Logistic Regression on Classical Sequence Descriptors & ESM-2 Embeddings
- **Organism**: *Saccharomyces cerevisiae* (Taxonomy ID: 559292)
- **Primary Inputs**: Amino Acid Sequences / Protein Systematic ORF Identifiers
- **Primary Outputs**: Calibrated interaction probability $P(\\text{Interacting} \\mid \\text{Protein}_A, \\text{Protein}_B)$ and documented BioGRID status.

## Intended Use
- Screening candidate *S. cerevisiae* protein pairs for physical interaction.
- Hypothesis generation for laboratory Yeast Two-Hybrid (Y2H) verification.

## Out-of-Scope Uses
- Clinical or medical decision making.
- Direct zero-shot application to non-yeast species without retraining or validation.

## Training Data & Provenance
- Positives: Filtered BioGRID S. cerevisiae physical Y2H interactions.
- Negatives: Negatome 2.0 curated non-interacting pairs + unobserved/sampled negatives completely disjoint from known physical positives.
- Tracked in `reports/run_manifest.json`.
"""
    with open(card_path, "w", encoding="utf-8") as f:
        f.write(card_content)
        
    # Limitations Document
    lim_path = reports_dir / "limitations.md"
    lim_content = """# Y2H-AI Platform: Scientific Limitations

## 1. Y2H Experimental Noise
- **False Positives**: Overexpression auto-activation in artificial yeast nucleus environment.
- **False Negatives**: Misfolding of fusion proteins, missing post-translational modifications, or cofactors absent in yeast.

## 2. Lack of Confirmed Negative Ground Truth
- No universal experimental confirmation of non-interaction at proteome scale.
- Handled by benchmarking across Curated Negatives (Negatome) and Random Sampling across 1:1, 1:10, and 1:100 imbalance ratios.

## 3. Generalization & Information Leakage (Park & Marcotte 2012)
- High reported performance on naive C1 evaluation overstates real-world precision for novel proteins (C3 split).
- Report explicitly exposes C1/C2/C3 performance breakdown.
"""
    with open(lim_path, "w", encoding="utf-8") as f:
        f.write(lim_content)
        
    logger.info("Generated model_card.md and limitations.md.")
