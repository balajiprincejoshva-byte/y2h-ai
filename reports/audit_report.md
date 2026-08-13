# Y2H-AI V2 Full Project Audit Report

## 1.1 Implementation Inventory

| Component | Advertised | Actually Implemented | Actually Executed | Evidence |
|-----------|------------|----------------------|--------------------|----------|
| BioGRID | Yes | Yes | Yes | `src/y2h_ppi/data/biogrid.py` and `manifest.json` report 12,683 pairs. |
| SGD/UniProt | Yes | Yes | Yes | `src/y2h_ppi/data/uniprot.py` and `manifest.json` report 3,687 sequences. |
| Negatome | Yes | Yes | Yes | `src/y2h_ppi/data/negatome.py` pulls 0 pairs overlapping with yeast. |
| Negative sampling | Yes | Yes | Yes | `src/y2h_ppi/data/negatives.py` generated 1:1, 1:10, 1:100 sets. |
| AAC, DPC, CTD, Conjoint | Yes | Yes | Yes | `src/y2h_ppi/features/classic_descriptors.py` cached 3,687 protein features. |
| ESM-2 | Yes | Yes | Yes | `src/y2h_ppi/features/esm_embeddings.py` generated and cached embeddings. |
| Logistic Regression | Yes | Yes | Yes | Trained in `trainer.py` but **NOT evaluated** in `pipeline.py`. |
| Random Forest | Yes | Yes | Yes | Trained and evaluated in `pipeline.py`. |
| XGBoost/LightGBM | Yes | Partial | No | Code in `baseline_ml.py` but never called in `trainer.py`. |
| MLP | Yes | Partial | No | Stub in `mlp_model.py`, never trained or evaluated. |
| Siamese model | Yes | Partial | No | Stub in `mlp_model.py`, never trained or evaluated. |
| RCNN/PIPR-style model | No | No | No | Not present in codebase. |
| C1, C2, C3 | Yes | Yes | Yes | Executed in `src/y2h_ppi/evaluation/pipeline.py`. |
| SHAP | Yes | Yes | Yes | Executed in `src/y2h_ppi/explain/shap_explain.py`. |
| API | Yes | Yes | Yes | `src/y2h_ppi/api/main.py` verified working via pytest. |
| Streamlit | Yes | Yes | No | Code in `frontend/app.py`, but not systematically tested in phase scripts. |
| Docker | Yes | Yes | No | `Dockerfile` and `docker-compose.yml` present, untested in Phase scripts. |
| pytest | Yes | Yes | Yes | `pytest tests/` passes 6/6 tests. |

## 1.2 Dead / Stub Code Identification

- **`mlp_model.py`**: Contains `PyTorchMLP` and `SiameseNetwork` classes. Neither is called by `trainer.py` or any pipeline script. They are dead code.
- **`baseline_ml.py`**: Contains `train_gradient_boosting` (XGBoost/LightGBM) which is never invoked in `trainer.py`.
- **Threshold Selection**: Hardcoded probability threshold > 0.5 is used in prediction, without formal selection on a validation set.
- **Negative Sampling**: Random pairs are excluded only from `positive_pairs` (the specific Y2H dataset) instead of all known physical positives, creating potential biological false negatives.

## 1.3 Inconsistencies

See `consistency_audit.json` for metric inconsistencies across the repository documentation vs. pipeline outputs.
