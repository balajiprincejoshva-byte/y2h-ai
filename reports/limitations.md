# Y2H-AI Platform: Scientific Limitations

## 1. Y2H Experimental Noise
- **False Positives**: Overexpression auto-activation in artificial yeast nucleus environment.
- **False Negatives**: Misfolding of fusion proteins, missing post-translational modifications, or cofactors absent in yeast.

## 2. Lack of Confirmed Negative Ground Truth
- No universal experimental confirmation of non-interaction at proteome scale.
- Handled by benchmarking across Curated Negatives (Negatome) and Random Sampling across 1:1, 1:10, and 1:100 imbalance ratios.

## 3. Generalization & Information Leakage (Park & Marcotte 2012)
- High reported performance on naive C1 evaluation overstates real-world precision for novel proteins (C3 split).
- Report explicitly exposes C1/C2/C3 performance breakdown.
