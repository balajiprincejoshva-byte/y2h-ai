# Y2H-AI Model Card

## Model Details
- **Developer**: Antigravity & User Team
- **Model Type**: Random Forest & Logistic Regression on Classical Sequence Descriptors & ESM-2 Embeddings
- **Organism**: *Saccharomyces cerevisiae* (Taxonomy ID: 559292)
- **Primary Inputs**: Amino Acid Sequences / Protein Systematic ORF Identifiers
- **Primary Outputs**: Calibrated interaction probability $P(\text{Interacting} \mid \text{Protein}_A, \text{Protein}_B)$ and documented BioGRID status.

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

## Evaluation Metrics & Ablation
- Canonical performance metrics across C1/C2/C3 splits and imbalances are available in: `reports/evaluation_results.json`.
- **Feature Ablation**: Empirical evaluation demonstrated that ESM-2 embeddings failed to provide an uplift over Classical Sequence Descriptors on the strictly unseen C3 split (Classical: AUROC 0.6796 vs ESM-2: AUROC 0.6474).
