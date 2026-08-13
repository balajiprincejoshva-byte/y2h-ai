# Y2H-AI: AI-Driven Computational Platform for Yeast Protein–Protein Interaction Prediction

Y2H-AI is a scientific platform designed to predict physical protein–protein interactions (PPIs) in *Saccharomyces cerevisiae* using real experimental Yeast Two-Hybrid (Y2H) data, classical sequence descriptors, protein language model embeddings (ESM-2), and Park & Marcotte (2012) protein-disjoint evaluation standards.

---

## Key Features

1. **Real Data Provenance**: Ingests filtered BioGRID physical Y2H interactions (taxid 559292), SGD reference proteome sequences, and Negatome 2.0 curated non-interacting pairs. Tracked in `data/raw/manifest.json`.
2. **Strict Non-Overlapping Negative Sampling**: Curated Negatome negatives + random-sampled negatives across 1:1, 1:10, and 1:100 imbalance ratios with zero positive overlap verification assertions.
3. **Multi-Tier Feature Engineering**:
   - **Tier 1 (Classical)**: Amino Acid Composition (AAC - 20 dim), Dipeptide Composition (DPC - 400 dim), CTD (21 dim), Conjoint Triad (343 dim - Shen et al. 2007).
   - **Tier 2 (Protein LM)**: ESM-2 (`facebook/esm2_t6_8M_UR50D`) mean-pooled residue embeddings.
   - **Symmetric Pair Combination**: $[v_A + v_B, |v_A - v_B|]$ guaranteeing $F(A, B) \equiv F(B, A)$.
4. **Park & Marcotte (2012) Protein-Disjoint Evaluation**: Benchmarked across C1 (both proteins seen), C2 (one protein seen), and C3 (unseen proteins) splits with 0-leakage automated unit testing.
5. **Explainability**: SHAP global feature importances & sequence-space nearest interactors lookup.
6. **API & Web UI**: Production FastAPI REST backend and Streamlit Web Application.

---

## Park & Marcotte (2012) Evaluation Benchmark Results

The V2 revision of this platform outputs all canonical, reproducible metric evaluations into a single JSON artifact. 
Please refer to the single source of truth for full details: 👉 [reports/evaluation_results.json](file:///c:/Users/Balaji/Desktop/Genetic%20engineering%20capstone%20project/reports/evaluation_results.json)

**Baseline Balanced (1:1) Performance:**
- **C1 (Seen in train)**: Random Forest AUROC = **0.7719**
- **C2 (One protein seen)**: Random Forest AUROC = **0.7240**
- **C3 (Both unseen)**: Random Forest AUROC = **0.6662**
- **Degree Hub Baseline (C3)**: AUROC = **0.5000** (Random)

*Performance drops honestly from C1 → C2 → C3, reflecting true real-world generalization to novel proteins, rigorously benchmarked against the graph topology DegreeHub baseline.*

---

## Quickstart Guide

### 1. Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### 2. Phase-Gated Pipeline Execution
```bash
python -m y2h_ppi.cli reproduce # Runs entire pipeline sequentially with single command (Phase 0 - 9)
```

### 3. Launch Production API & Streamlit Web UI
```bash
# Start FastAPI backend
uvicorn src.y2h_ppi.api.main:app --host 0.0.0.0 --port 8000

# Start Streamlit Frontend
streamlit run frontend/app.py --server.port 8501
```

### 4. Docker Deployment
```bash
docker-compose up --build
```

---

## Documentation & Reports

- [Model Card](file:///c:/Users/Balaji/Desktop/Genetic%20engineering%20capstone%20project/reports/model_card.md)
- [Scientific Limitations](file:///c:/Users/Balaji/Desktop/Genetic%20engineering%20capstone%20project/reports/limitations.md)
- [Data Provenance Manifest](file:///c:/Users/Balaji/Desktop/Genetic%20engineering%20capstone%20project/data/raw/manifest.json)
- [Evaluation Results JSON](file:///c:/Users/Balaji/Desktop/Genetic%20engineering%20capstone%20project/reports/evaluation_results.json)
