<div align="center">

# 🧬 Y2H-AI
**Autonomous Protein-Protein Interaction & Structural Biology Engine**

[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](#)
[![Python FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](#)
[![Machine Learning](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](#)
[![AlphaFold](https://img.shields.io/badge/AlphaFold_3D-035ED1?style=for-the-badge&logo=google&logoColor=white)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](#)

> **Standard databases catalog the known. Y2H-AI predicts the undiscovered.** <br>
> An enterprise-grade computational biology platform that leverages calibrated Machine Learning and AlphaFold structural data to predict, visualize, and map complex *Saccharomyces cerevisiae* protein-protein interaction networks.

</div>

---
<div align="center">

<!-- Replace src with your actual deployment demo video or screenshot -->
<img width="1280" height="720" alt="Y2H-AI Demo" src="https://github.com/user-attachments/assets/your-video-id-here" />

[![To Try Y2H-AI Demo](https://img.shields.io/badge/Live-Demo-00a393?style=for-the-badge)](https://y2h-ai.vercel.app)

---

## 🚀 The Paradigm Shift in Proteomics

Physical high-throughput screening methods (like Yeast Two-Hybrid) are currently bottlenecked by massive false-positive rates, high costs, and biological noise. Researchers spend months running wet-lab validations just to map a fraction of a cellular interactome.

**Y2H-AI** digitizes this. It ingests known physical interaction topologies and orchestrates a highly calibrated Random Forest engine to predict hidden relationships. It answers the hardest questions in proteomics: *"Which proteins will interact, how confident are we, and what does the resulting subnet topology look like?"*

---

## 🧠 Core Platform Architecture

### 1. Interaction Laboratory (Pairwise Prediction)
Moving beyond simple binary classification, Y2H-AI provides a forensic probabilistic breakdown of any two proteins. It calculates a rigorously calibrated interaction probability, complete with confidence bands, decision thresholds, and nearest-neighbor reference interactions to eliminate "black-box" ML hesitation.

### 2. Protein Observatory (AlphaFold Integration)
The platform seamlessly resolves proteins to their 3D physical structures. Using real-time integration with the AlphaFold EBI database, researchers can visually inspect the predicted folding structures, atomic surfaces, and binding pockets of the proteins in question.

### 3. The 3D Network Explorer (Force-Directed Graph)
A built-in topological engine that allows users to test network hypotheses. The engine calculates dynamic force-directed layouts, mapping a query protein's known interactors alongside AI-generated candidate interactions in a fully navigable, physics-based 3D space.

### 4. Aerogel UX & Telemetry Interface
Designed with a bespoke, laboratory-grade "Aerogel" aesthetic. The interface prioritizes data density and readability, featuring interactive scientific rails, real-time model stability metrics, and sub-millisecond API telemetry.

---

## 📸 Feature Showcase

*(Note: Add your actual demo GIFs or screenshots here)*

| The Interaction Laboratory | Protein 3D Observatory |
| :---: | :---: |
| <img width="400" height="214" alt="Lab Demo" src="https://github.com/user-attachments/assets/placeholder-1" /> | <img width="400" height="214" alt="AlphaFold Demo" src="https://github.com/user-attachments/assets/placeholder-2" /> |
| *Pairwise prediction with rigorous statistical calibration bands.* | *Real-time AlphaFold structure resolution and rendering.* |

| 3D Network Explorer | Model Telemetry |
| :---: | :---: |
| <img width="400" height="214" alt="Network Demo" src="https://github.com/user-attachments/assets/placeholder-3" /> | <img width="400" height="214" alt="Model Demo" src="https://github.com/user-attachments/assets/placeholder-4" /> |
| *Physics-based interaction topology mapping.* | *Transparent ML performance metrics and feature ablation.* |

---

## 🛠️ Tech Stack & Engineering

Y2H-AI relies on a decoupled, high-performance architecture to handle complex data inference and 3D visualization:

* **Frontend Engine:** Next.js 14 (Turbopack), React Three Fiber / 3Dmol.js (for structural resolution), TailwindCSS.
* **Backend Inference:** Python FastAPI, Scikit-Learn (Random Forest V3 pipeline), Pandas.
* **Data Layer:** Parquet-optimized feature stores and calibrated probability models mapping the BioGRID interactome.
* **Deployment:** Vercel (Edge Network) + Render (Python Web Service).

---

## 💻 Quick Start (Local Deployment)

**1. Clone the Repository**
```bash
git clone https://github.com/balajiprincejoshva-byte/y2h-ai.git
cd y2h-ai
```

**2. Boot the AI Backend**
```bash
pip install -r requirements.txt
uvicorn src.y2h_ppi.api.main:app --host 0.0.0.0 --port 8000
```

**3. Boot the Frontend Engine**
```bash
cd web
npm install
npm run dev
```

---

## 🔬 Scientific Methodology & Model Architecture

Y2H-AI operates on a highly optimized **V3 Random Forest Pipeline**, trained exclusively on curated, physical protein interactions to eliminate topological hallucination.

### Phase 1: Ingestion & Feature Engineering
Raw unstructured interaction data (BioGRID, Negatome) is notoriously noisy. Y2H-AI filters this into pristine, high-confidence subsets.
* **Curated Negatives:** To prevent class imbalance and topological leakage, negative samples are rigorously verified through structural disjoint splitting.
* **Feature Extraction:** Biological sequences are mapped using advanced embeddings and classic physiochemical descriptors, standardized into highly dense vector spaces.

### Phase 2: Calibrated Inference
Standard classification models output uncalibrated confidence (often overconfident on edge cases). 
The inference layer employs **Isotonic Calibration**, forcing the raw output of the Random Forest ensemble to mathematically reflect the true empirical probability of interaction.
* *Result:* An 80% prediction score mathematically guarantees an 80% likelihood of physical interaction in a wet-lab environment.

### Phase 3: Structural & Network Resolution
When evaluating a hypothesis, the engine traverses known topological graphs to pull supporting structural evidence.
* **Network Candidates:** The system scans the entire registry to rank the highest-probability theoretical interactors for any given protein.
* **3D Folding Integration:** Instantly maps the Uniprot ID to its corresponding `.cif` AlphaFold model for spatial conformation analysis.

---

## ⚙️ Systems Topology

Y2H-AI utilizes a decoupled, high-throughput microservice architecture:

* **Inference Layer (Python / FastAPI):** Handles heavy ML workloads, Pandas data manipulation, and extremely fast `.joblib` model deserialization.
* **Storage Layer:** Utilizes compressed `.parquet` formats for instantaneous feature retrieval without the overhead of an external SQL database.
* **Client Telemetry (Next.js / WebGL):** A browser-native interface that renders complex 3D structures and dynamic force-directed graphs via hardware-accelerated WebGL.

---
<div align="center">
<i>Engineered by Balaji Muthukumar</i>
</div>
