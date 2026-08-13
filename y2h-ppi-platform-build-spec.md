# Y2H-AI: AI-Driven Computational Platform for Yeast Protein–Protein Interaction Prediction
## Complete Build Specification for a Coding Agent

**How to use this document:** Paste this entire document into your coding IDE agent (Claude Code, Cursor, Windsurf, etc.) as the founding prompt, or save it as `AGENTS.md` / `CLAUDE.md` in the repo root so the agent reads it automatically. Work phase by phase, in order. Do not start Phase N+1 until Phase N's checkpoint passes with real, printed evidence. If a phase is genuinely blocked (no GPU, a database is unreachable), fall back to the "Tier 1" option specified for that phase — never substitute fabricated output.

As a side effect, the auto-generated files in `reports/` (evaluation report, model card, limitations) double as source material for a written report or thesis chapter on this topic, since every number in them is real and traceable to a logged data source.

---

## 0. Mission and Non-Negotiable Rules

Build a real, working, scientifically defensible platform that predicts whether two *Saccharomyces cerevisiae* proteins physically interact, trained and evaluated on real yeast two-hybrid (Y2H) interaction data. The deliverable is not a script — it's a platform: data pipeline → feature engineering → multiple trained models → rigorous benchmarking → a prediction API → a web UI a biologist could actually use to screen candidate pairs and understand how much to trust the result.

**These rules override convenience at every step:**

1. **Real data only.** Every interaction record, protein sequence, and negative example comes from an actual downloaded public database (BioGRID, UniProt/SGD, Negatome, etc.). Never synthesize interaction labels or protein sequences.
2. **No mocked outputs, anywhere.** No hardcoded "example" predictions, no placeholder metrics, no `return 0.87 # TODO` left in delivered code. Every number in a report, dashboard, or API response is the output of code that actually ran on real data.
3. **Honest metrics, even when they're bad.** If performance collapses on the harder evaluation splits (it will — see Phase 5), report that plainly. A lower true number is a correct deliverable; a higher fabricated one is not.
4. **Data provenance is mandatory.** Every dataset pulled into the project is logged (source URL, access date, version/release, row count) in `data/raw/manifest.json`. This is what makes the results auditable — treat it as a first-class deliverable.
5. **Document limitations as rigorously as capabilities.** `reports/limitations.md` is required, not optional polish.
6. **Phase-gated, incremental execution.** After each phase, print/log concrete evidence (row counts, shapes, real metric values) before moving on.

---

## 1. Scientific Background (read before writing code)

**Yeast two-hybrid (Y2H)** detects physical protein–protein interactions (PPIs) by fusing candidate proteins to the DNA-binding and activation domains of a transcription factor; interaction reconstitutes the transcription factor and activates a reporter gene. Two landmark proteome-scale yeast Y2H screens — Uetz et al. (2000, *Nature*) and Ito et al. (2001, *PNAS*, 4,549 interactions across 3,278 of the ~6,000 yeast proteins) — largely founded the field, and both are folded into BioGRID today alongside thousands of smaller, more recent Y2H studies.

Y2H is noisy in both directions, and the platform's documentation must say so honestly:
- **False positives**: reporter autoactivation independent of a real interaction; interactions detected only because both proteins are overexpressed and forced into the nucleus, which would never happen in a real cell.
- **False negatives**: fusion proteins that misfold, fail to localize to the nucleus, or need cofactors/post-translational modifications not present in yeast to interact.

This is *why* a computational prediction layer is useful: it can flag inconsistencies and propose likely interactions for follow-up, generalizing to proteins never tested together.

**The single most important methodological trap in this field**, which this project must explicitly avoid, is described in Park & Marcotte (2012, *Nature Methods* 9:1134–1136), "Flaws in evaluation schemes for pair-input computational predictions." Because a PPI predictor takes a *pair* as input, a naive random split of pairs into train/test leaks information — most test-set proteins also appear, in some other pairing, in the training set, so the model can partly succeed just by having "met" both proteins before, not by learning real sequence-interaction rules. They define three regimes for a test pair (A, B):

- **C1** — both A and B also appear in the training pairs (easiest; misleadingly close to what naive random-split CV reports)
- **C2** — exactly one of A, B appears in training (harder; representative of predicting for a partially-studied protein)
- **C3** — neither A nor B appears in training (hardest; the realistic case of screening a novel/understudied protein)

Reported AUROC/AUPRC routinely drops sharply from C1 to C3 in the literature. **Phase 5 requires implementing and reporting all three regimes — this is the difference between a toy project and a scientifically credible one.**

---

## 2. Architecture Overview

```
Data Layer   →   Feature Layer         →   Modeling Layer         →   Evaluation Layer          →   Serving Layer  →  UI Layer
(BioGRID,        (sequence descriptors     (classic ML + deep         (protein-disjoint             (FastAPI)        (predict page,
 UniProt/SGD,     + ESM-2 embeddings)       learning, tiered by        C1/C2/C3 splits,                                network explorer,
 Negatome)                                  available compute)         honest metrics)                                 performance dashboard)
```

Repository layout:

```
y2h-ppi-platform/
├── README.md
├── LICENSE
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── config/
│   ├── data.yaml
│   ├── features.yaml
│   ├── model.yaml
│   └── eval.yaml
├── data/
│   ├── raw/                 # untouched downloads + manifest.json
│   ├── interim/
│   └── processed/
├── src/y2h_ppi/
│   ├── data/                 # download_biogrid.py, download_sequences.py, download_negatome.py,
│   │                          # curate_positives.py, generate_negatives.py, manifest.py
│   ├── features/              # classic_descriptors.py, plm_embeddings.py, pair_representation.py, cache.py
│   ├── splitting/               # protein_disjoint_split.py  (C1/C2/C3 logic)
│   ├── models/                  # baseline_ml.py, mlp_embedding.py, siamese_network.py, rcnn_sequence.py, train.py
│   ├── evaluation/               # metrics.py, calibration.py, baselines.py, bootstrap_ci.py, report_generator.py
│   ├── explain/                   # shap_explain.py
│   ├── inference/                  # predictor.py
│   ├── network/                     # graph_builder.py
│   └── api/                          # main.py, schemas.py, routers/{predict,network,metrics}.py
├── frontend/                          # Streamlit MVP, or React/Vite as a stretch upgrade
├── tests/
├── reports/                            # evaluation_report.md/json, model_card.md, limitations.md — all auto-generated
└── scripts/                             # cli.py (Typer), run_pipeline.sh
```

---

## 3. Tech Stack

- **Language**: Python 3.11
- **Core**: pandas, numpy, scikit-learn, xgboost (or lightgbm), scipy
- **Deep learning**: PyTorch
- **Protein language model**: `transformers` (HuggingFace) or `fair-esm`, using Meta's ESM-2 checkpoints — Lin et al. 2023, *Science* 379:1123–1130
- **Bioinformatics utilities**: Biopython; `propy3` or `iFeatureOmega` for validated classical sequence descriptors
- **Explainability**: SHAP
- **Network/graph**: networkx, pyvis (or cytoscape.js if the frontend is React)
- **API**: FastAPI + uvicorn + pydantic
- **Frontend**: Streamlit for the MVP (ship this first); React + Vite + Tailwind as an optional stretch upgrade once the API is stable
- **CLI/config**: Typer, pydantic-settings, YAML configs
- **Testing**: pytest
- **Packaging/repro**: Docker, pinned `requirements.txt`, fixed random seeds everywhere

---

## Phase 0 — Environment & Repository Setup

1. `git init`; create the folder tree above.
2. Set up a virtual environment; pin dependency versions in `requirements.txt` as you add them.
3. Build a small `config/` system: YAML files loaded via pydantic-settings, so every downstream choice (organism filter, ESM-2 model size, split ratios, random seed) is config-driven, not hardcoded in scripts.
4. Set up logging (Python `logging`, not stray print statements) writing to `logs/`.
5. **Checkpoint**: `python -m y2h_ppi.cli --help` runs and lists a subcommand per phase below.

---

## Phase 1 — Data Acquisition (Real Data Only)

### 1.1 Interaction data: BioGRID

- BioGRID publishes monthly releases at `https://downloads.thebiogrid.org/BioGRID/`. **Do not hardcode a version number** — resolve the current release programmatically, either by parsing the directory listing at `https://downloads.thebiogrid.org/BioGRID/Latest-Release/`, or via the `bioversions` PyPI package (`pip install bioversions; bioversions.get_version("biogrid")`).
- Download the **organism-specific TAB3 file** for *Saccharomyces cerevisiae* (taxonomy ID **559292**) — filename pattern `BIOGRID-ORGANISM-Saccharomyces_cerevisiae_S288c-<version>.tab3.zip`. This is far smaller than the all-organism file and the right scope for this project.
- Load into pandas. Relevant columns include (verify exact header names against the file you actually download — schema documented at `https://wiki.thebiogrid.org/doku.php/downloads`): Systematic Name / Official Symbol for Interactor A and B, Organism ID for A and B, **Experimental System**, **Experimental System Type** (physical vs. genetic), Throughput, Publication Source.
- Print the unique values of `Experimental System` present in the file, then programmatically select every value corresponding to yeast two-hybrid methodology (variants containing "Two-hybrid"). **Log the exact list you selected** into the manifest — verify against what's actually in the file this month rather than assuming a fixed list.
- Filter to `Experimental System Type == Physical`, both interactors' Organism ID == 559292.
- Deduplicate: interactions are undirected (A–B ≡ B–A); canonicalize pairs (e.g., sort by ID) before deduping. Drop self-interactions unless you deliberately want to model homodimerization separately — note the decision either way.
- This filtered, deduplicated table is your **positive interaction set**. Print the final row count and unique protein count — this is real evidence for the checkpoint.

### 1.2 Protein sequences: SGD / UniProt

- Download the *S. cerevisiae* reference proteome from UniProt (reference proteome ID **UP000002311**) via the UniProt REST API, or the ORF protein translations FASTA from SGD (`https://www.yeastgenome.org/`, downloads section). Verify the exact current REST query syntax at build time — UniProt's API evolves, don't assume an old URL pattern is still exact.
- Build an ID-mapping table from BioGRID's Systematic Name (stable yeast ORF identifiers, e.g. `YFL039C`) to UniProt accession. Systematic names are more reliable join keys for yeast than gene symbols, which have aliases.
- Report what fraction of BioGRID interactor IDs successfully map to a sequence. Anything that doesn't map gets logged and excluded, not silently dropped.

### 1.3 Curated negative interactions: Negatome

- Download Negatome (Smialowski et al. 2010, *NAR* 38:D540–D544; Negatome 2.0: Blohm et al. 2014, *NAR* 42:D396–D400) from `https://mips.helmholtz-muenchen.de/proj/ppi/negatome/`.
- Filter to pairs where both proteins map to the yeast proteome. **Expect this to be small** — Negatome is dominated by human/structural-complex data. Document the actual count; this motivates Phase 2's additional negative-sampling strategies.

### 1.4 Manifest (required deliverable)

Write `data/raw/manifest.json` recording, per source: URL, access timestamp, version/release identifier, raw row count, post-filter row count, and a one-line description of the filter logic applied.

**Phase 1 Checkpoint**: print (a) number of curated yeast Y2H-derived positive pairs, (b) number of unique proteins with sequences successfully attached, (c) number of Negatome yeast-mappable negative pairs.

---

## Phase 2 — Negative Sampling Strategy

There is no experimentally confirmed "this pair definitely does not interact" ground truth at scale — this is a known, fundamental limitation of the field, and the platform must be explicit about it (this reasoning belongs directly in `reports/limitations.md`).

Implement **three negative sets**, not one, and carry all three through evaluation:

1. **Curated negatives** — the yeast-mappable Negatome pairs from 1.3.
2. **Random-sampled negatives** — random pairs from the yeast proteome, excluded from sampling if they appear in the union of your BioGRID positive set (all physical evidence, not just Y2H, to be conservative) plus IntAct/DIP if you have time to pull them as cross-checks. Sample enough for a 1:1 balanced primary training/evaluation set.
3. **Realistic-imbalance negative sets** — additional random-sampled sets at 1:10 and 1:100 positive:negative ratios (sampled once and frozen for reproducibility), used only at evaluation time to show how precision degrades under realistic imbalance. The true genome-wide pair space for ~6,000 yeast proteins is on the order of 18 million possible pairs against tens of thousands of known positives — evaluating only at 1:1 balance would badly overstate real-world precision, and the report must not do that silently.

**Phase 2 Checkpoint**: print the size of each negative set, and confirm via an assertion (not eyeballing) zero overlap between any negative set and the positive set.

---

## Phase 3 — Feature Engineering

### 3.1 Classical sequence descriptors (Tier 1 — required, CPU-only)

Implement, or use a validated package (`propy3` / `iFeatureOmega`) for:
- **AAC** (Amino Acid Composition): 20-dim, frequency of each residue.
- **DPC** (Dipeptide Composition): 400-dim.
- **CTD** (Composition–Transition–Distribution): physicochemical-property-grouped descriptors (hydrophobicity, charge, polarity, etc.).
- **Conjoint Triad (CT)**: Shen et al. 2007, *PNAS* 104:4337–4341 (doi:10.1073/pnas.0607879104). Groups the 20 amino acids into 7 classes by dipole moment/side-chain volume, then counts frequencies of all 3-residue windows over the grouped sequence → 7³ = 343-dim vector. **Verify the exact letter→group assignment against the primary source (DOI above) or the `propy3`/iFeatureOmega implementation before finalizing** — don't guess at the table from memory.

Cache computed features (parquet) keyed by protein ID so they're never recomputed unnecessarily.

### 3.2 Protein language model embeddings (Tier 2 — compute-tiered)

Use ESM-2 (Lin et al. 2023, *Science* 379:1123–1130):

| Compute available | Model |
|---|---|
| CPU only | `facebook/esm2_t6_8M_UR50D` or `facebook/esm2_t12_35M_UR50D` |
| Single consumer GPU | `facebook/esm2_t30_150M_UR50D` or `facebook/esm2_t33_650M_UR50D` |
| Cloud/large GPU | `facebook/esm2_t33_650M_UR50D` or larger |

Mean-pool per-residue embeddings (excluding special tokens) into a fixed-length per-protein vector. **This tier is an enhancement, not a blocker** — if it's genuinely too slow or unavailable, Tier-1 descriptors alone are a complete, legitimate deliverable; say so explicitly rather than silently skipping evaluation of what you did build.

### 3.3 Pair representation

A pair's label is symmetric: interacting(A,B) = interacting(B,A). Naive concatenation `[vec_A, vec_B]` bakes in an arbitrary ordering the model can exploit as a shortcut. Use a symmetric combination instead, e.g. `[vec_A + vec_B, |vec_A − vec_B|]`, or a genuinely symmetric (Siamese) architecture. Note whichever choice you make — this is a real, documented source of evaluation bias if skipped.

**Phase 3 Checkpoint**: print feature matrix shapes for both tiers; assert that swapping protein order in a pair produces an identical feature vector.

---

## Phase 4 — Modeling

Train, in order of increasing complexity — each a real, complete, saved model, not a stub:

1. **Baselines on classical descriptors**: Logistic Regression (interpretability reference), Random Forest, XGBoost/LightGBM.
2. **MLP on ESM-2 embeddings** (symmetric pair representation), class-weighted loss for imbalance.
3. **Siamese network**: shared-weight encoder branches over per-protein embeddings, combined via a learned similarity head.
4. **Stretch (optional, compute-permitting)**: a sequence-level RCNN (residual conv + recurrent, in the spirit of PIPR), or a simplified contact-map-style architecture in the spirit of D-SCRIPT (Sledzieski, Singh, Cowen & Berger, 2021, *Cell Systems* 12:969–982) — cite properly if you build toward it, and don't claim parity with the published model's full-scale performance since you won't train at their scale.

All training runs: fixed seeds, checkpoint the best model by **validation AUPRC** (not accuracy — the data is imbalanced), log hyperparameters and training curves to `reports/`.

**Phase 4 Checkpoint**: at least one Tier-1 model exists with saved weights, reloadable, and produces a printed prediction on a held-out example.

---

## Phase 5 — Rigorous Evaluation (the scientific core of the project)

### 5.1 Protein-disjoint splitting — implement this exactly

This is what most toy projects in this space get wrong, per Park & Marcotte (2012):

```
1. Partition the full protein set P into P_train and P_heldout (e.g. 80/20, or k-fold
   at the PROTEIN level — group-based logic keyed by protein ID, not pair ID).
2. Build the training pair set: all positive/negative pairs where BOTH proteins are
   in P_train, minus a held-back slice used for C1 testing.
3. Classify every evaluation pair (A, B) not in the training pair set:
     C1: A in P_train AND B in P_train   (both proteins seen during training, via other pairings)
     C2: exactly one of {A, B} in P_train, the other in P_heldout
     C3: A in P_heldout AND B in P_heldout   (neither protein seen during training at all)
4. Evaluate the trained model separately on the C1, C2, and C3 pools. Report all three —
   do not average them into one headline number without also showing the breakdown.
```

Write a `pytest` unit test asserting that, for the C3 pool specifically, neither protein in any C3 test pair appears anywhere in the training pair set. This is a real, automated leakage check, not a manual eyeball check.

### 5.2 Metrics

For each of C1/C2/C3, and each of the 1:1 / 1:10 / 1:100 negative-ratio sets from Phase 2: AUROC, **AUPRC** (primary metric given imbalance — report at least as prominently as AUROC), Precision, Recall, F1, Matthews Correlation Coefficient, Precision@K (K = top 50/100/500 ranked predictions), and a calibration curve (predicted probability vs. observed frequency).

### 5.3 Baselines you must beat — and report, even if you don't

- **Random predictor** (sanity floor).
- **Degree/hub baseline**: score a pair by the product (or sum) of each protein's known-interaction count in the training network. Real interactomes are scale-free, so this trivial "popularity" heuristic is a surprisingly strong baseline in this literature — a model that doesn't clear it meaningfully hasn't learned sequence-interaction biology, it's learned who's popular. Report this comparison honestly.

### 5.4 Confidence intervals

Bootstrap the test set (resample with replacement, ≥1000 iterations), report 95% CIs on headline metrics, per split class.

### 5.5 Auto-generated report

All of the above is written by code into `reports/evaluation_report.md` and `reports/evaluation_report.json`, regenerated fresh every evaluation run — never hand-edited with invented numbers.

**Phase 5 Checkpoint**: the report exists, contains real C1/C2/C3 numbers for at least one Tier-1 model, and (expected, not a bug) shows performance degrading from C1 → C2 → C3.

---

## Phase 6 — Explainability

- SHAP (`TreeExplainer`) on tree-based models over classical descriptors: global feature importance plot + example-level force plots for a handful of specific predicted pairs.
- For embedding-based models, surface nearest-neighbor known interactors in embedding space as a lighter-weight explanation aid, since raw embedding dimensions aren't individually interpretable.

---

## Phase 7 — Inference Service (library level, pre-API)

Build `src/y2h_ppi/inference/predictor.py`: given two protein identifiers (systematic name / UniProt accession) or two raw FASTA sequences, return a probability, a discretized confidence band, the model version used, and a check against the curated positive/negative sets so the response can say "this pair is already a documented BioGRID interaction" rather than presenting a prediction as the only source of truth. Support batch scoring of a gene list, with a runtime/size warning since scoring is O(n²) in the number of proteins.

---

## Phase 8 — Platform: API + Web UI

### 8.1 FastAPI backend

- `POST /predict` — `{protein_a, protein_b}` (ID or sequence) → `{probability, predicted_label, confidence_interval, is_documented_interaction, model_version, nearest_known_interactors}`
- `POST /predict/batch` — list of pairs, capped batch size, background-job pattern for larger requests
- `GET /protein/{id}/known_interactors` — curated (not predicted) BioGRID-derived neighbors, for network context
- `GET /model/metrics` — serves the real `evaluation_report.json` (C1/C2/C3 breakdown) — **the platform should expose its own honest reliability, not hide it in documentation nobody reads**
- `GET /model/card` — serves `model_card.md`/json
- `GET /health`

### 8.2 Frontend (ship Streamlit first; React/Vite is a stretch upgrade once the API is stable)

- **Predict page**: two protein inputs (ID autocomplete against the yeast gene list, or paste sequence) → probability gauge, CI, nearest known interactors, and a clear flag if the pair is already a documented interaction.
- **Network Explorer page**: pick a gene, visualize its known-interaction neighborhood (networkx + pyvis, or cytoscape.js in React), with an option to overlay high-confidence novel predicted edges in a visually distinct style.
- **Model Performance Dashboard**: the platform's differentiating feature — real C1/C2/C3 AUROC/AUPRC bars, the calibration curve, and the degree-baseline comparison, so a user can see exactly how much to trust a prediction depending on whether the queried proteins are well- or poorly-studied. Pull this live from `/model/metrics`, don't bury it in a PDF.
- **About/Methods page**: data provenance, citations, limitations, pulled from the manifest and `limitations.md`, not re-typed.

**Phase 8 Checkpoint**: `docker-compose up` brings up the API and frontend; a real request against `/predict` with two real yeast protein IDs returns a real, non-hardcoded probability.

---

## Phase 9 — Testing, Reproducibility, Documentation

- `pytest` covering: data schema validation, feature-vector shape/range checks, the C1/C2/C3 leakage assertion (5.1), pair-order symmetry (3.3), and API contract tests via FastAPI's `TestClient`.
- `Dockerfile` + `docker-compose.yml` for API + frontend.
- `requirements.txt`/`pyproject.toml` with pinned versions.
- `README.md`: setup, quickstart, a one-paragraph methods summary, an honest results table (C1/C2/C3, not just the best number), citations, link to `limitations.md`.
- `reports/model_card.md`: training data description + date, intended use, explicitly out-of-scope uses (this is yeast-specific research tooling, not a clinical or cross-species decision tool without further validation), metrics broken out by C1/C2/C3.
- `reports/limitations.md` (required): Y2H false-positive/false-negative sources (Section 1); the lack of confirmed true negatives and how that was worked around (Section 2); the yeast-only, non-cross-species scope of the trained model; the gap between curated 1:1 benchmark performance and true genome-wide screening precision at realistic (very high) class imbalance.

---

## Definition of Done

- [ ] `data/raw/manifest.json` documents every real data source with URL, date, version, counts
- [ ] Positive interaction set is real, filtered BioGRID Y2H data for yeast (taxid 559292), deduplicated
- [ ] Three negative sets exist (curated, random 1:1, realistic-imbalance 1:10 & 1:100), verified non-overlapping with positives
- [ ] Tier-1 classical descriptors implemented/validated and cached; symmetry unit test passes
- [ ] At least one trained, saved, reloadable model (Tier 1 minimum; embeddings/DL as compute allows)
- [ ] Protein-disjoint C1/C2/C3 splitting implemented with a passing leakage unit test
- [ ] `reports/evaluation_report.{md,json}` auto-generated with real AUROC/AUPRC/F1/MCC/Precision@K/calibration, per split class, per negative-ratio set, with bootstrap CIs
- [ ] Degree-baseline and random-baseline comparisons reported
- [ ] SHAP explainability implemented for at least the tree-based model
- [ ] FastAPI backend running with all endpoints returning real (non-hardcoded) results
- [ ] Frontend running with Predict, Network Explorer, and Model Performance Dashboard pages
- [ ] `reports/limitations.md` and `reports/model_card.md` complete
- [ ] pytest suite passing, including the leakage and symmetry checks
- [ ] Docker setup runs the whole platform with one command
- [ ] README complete with an honest, real results table

---

## Execution Protocol for the Agent

Work the phases in order. After each phase, print or log concrete, real evidence (counts, shapes, metric values) before proceeding — treat this as the phase's exit test, not a formality. If a phase's full-scale option isn't feasible in the current environment (no GPU, a specific database unreachable), implement the Tier-1/fallback option called out in that phase, note it in `reports/limitations.md`, and continue — never substitute a mocked result to avoid an honest "this part is smaller-scale than ideal" note. Where a design decision isn't fully specified above (exact hyperparameters, exact UniProt query syntax), make a reasonable choice, log the reasoning in code comments or the relevant config file, and move on rather than stalling.

---

## Stretch Goals (only after Definition of Done is met)

- **Cross-species generalization test**: evaluate the trained yeast model on a human or fly Y2H benchmark (zero/few-shot) to characterize how far sequence-based patterns transfer — a natural extension of the C1/C2/C3 discussion.
- **Structural augmentation**: AlphaFold DB (Jumper et al. 2021, *Nature*; Varadi et al. 2022, *Nucleic Acids Res*) provides precomputed structural models for the yeast proteome; structure-derived features or lightweight docking-style scoring of the platform's top novel predictions could serve as an orthogonal validation signal.
- **Natural-language prediction explanations**: an LLM summarizing real SHAP output plus any available GO annotations into a plain-language rationale for a specific prediction — must call a real API on real SHAP values, never a canned template dressed up as personalized.
- **CI/CD**: GitHub Actions running the pytest suite (including the leakage test) on every push.
- **Genome-wide candidate report**: batch-score sparsely-annotated yeast proteins against well-characterized hub proteins, ranked, as a candidate list for wet-lab follow-up — clearly labeled as hypothesis-generating, not validated.

---

## Key References

- Park Y, Marcotte EM. Flaws in evaluation schemes for pair-input computational predictions. *Nat Methods*. 2012;9(12):1134–1136. doi:10.1038/nmeth.2259
- Shen J, Zhang J, Luo X, et al. Predicting protein–protein interactions based only on sequences information. *PNAS*. 2007;104(11):4337–4341. doi:10.1073/pnas.0607879104
- Uetz P, Giot L, Cagney G, et al. A comprehensive analysis of protein–protein interactions in *Saccharomyces cerevisiae*. *Nature*. 2000;403(6770):623–627.
- Ito T, Chiba T, Ozawa R, et al. A comprehensive two-hybrid analysis to explore the yeast protein interactome. *PNAS*. 2001;98(8):4569–4574.
- Smialowski P, Pagel P, Wong P, et al. The Negatome database: a reference set of non-interacting protein pairs. *Nucleic Acids Res*. 2010;38(Database issue):D540–D544.
- Blohm P, Frishman G, Smialowski P, et al. Negatome 2.0: a database of non-interacting proteins derived by literature mining, manual annotation and protein structure analysis. *Nucleic Acids Res*. 2014;42(Database issue):D396–D400.
- Lin Z, Akin H, Rao R, et al. Evolutionary-scale prediction of atomic-level protein structure with a language model. *Science*. 2023;379(6637):1123–1130.
- Sledzieski S, Singh R, Cowen L, Berger B. D-SCRIPT translates genome to phenome with sequence-based, structure-aware, genome-scale predictions of protein–protein interactions. *Cell Systems*. 2021;12(10):969–982.
- BioGRID: consult `https://wiki.thebiogrid.org` for the current schema and citation details at build time (the database updates monthly).
