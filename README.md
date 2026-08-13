<div align="center">

# 🧬 Y2H-AI

### Autonomous Protein-Protein Interaction & Structural Biology Engine

[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge\&logo=nextdotjs\&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)](#)
[![Machine Learning](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge\&logo=scikit-learn\&logoColor=white)](#)
[![AlphaFold](https://img.shields.io/badge/AlphaFold-035ED1?style=for-the-badge\&logo=google\&logoColor=white)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](#)

> **Standard databases catalog the known. Y2H-AI predicts the undiscovered.**

An enterprise-grade computational biology platform that leverages calibrated machine learning and AlphaFold structural data to predict, visualize, and map complex *Saccharomyces cerevisiae* protein-protein interaction networks.

<br>

</div>

---

## 🎥 Demo

<div align="center">

<img width="100%" alt="Y2H-AI Demo" src="https://github.com/user-attachments/assets/40c73ad6-b14e-4206-a4b7-a2f236f73697" />

<br><br>

### ▶️ [Try the Live Demo](https://y2h-ai-ten.vercel.app)

### 🎬 [Watch the Full Demo Video](https://github.com/user-attachments/assets/ed8bf392-48b0-4c2d-a9f2-3214307455e3)

</div>

---

## 🚀 The Paradigm Shift in Proteomics

Physical high-throughput screening methods such as Yeast Two-Hybrid (Y2H) assays can be affected by false positives, experimental cost, biological noise, and limited throughput. Researchers may spend substantial time validating candidate interactions before obtaining a useful picture of the interactome.

**Y2H-AI** approaches this problem computationally.

The platform ingests known physical interaction topologies and orchestrates a calibrated Random Forest inference engine to prioritize potential protein-protein interactions.

It answers three core questions:

> **Which proteins are likely to interact?**
> **How confident is the model in that prediction?**
> **What does the resulting interaction network look like?**

---

# 🧠 Core Platform Architecture

## 1. Interaction Laboratory

### Pairwise Protein-Protein Interaction Prediction

Moving beyond simple binary classification, Y2H-AI provides a probabilistic breakdown of any two proteins.

The inference pipeline provides:

* Calibrated interaction probability
* Prediction confidence information
* Decision thresholds
* Supporting reference interactions
* Model-derived feature information
* Pairwise interaction classification

This provides researchers with more context than a simple `YES / NO` prediction.

---

## 2. Protein Observatory

### AlphaFold Structural Integration

The platform resolves proteins to their predicted 3D structures using AlphaFold structural data.

Researchers can inspect:

* Protein folding structures
* Molecular surfaces
* Structural geometry
* Candidate binding regions
* Protein-level structural context

This connects **interaction prediction** with **structural interpretation** inside the same interface.

---

## 3. 3D Network Explorer

### Force-Directed Interaction Graph

Y2H-AI includes an interactive 3D network engine for exploring protein interaction hypotheses.

The network explorer dynamically maps:

* Known protein interactors
* AI-generated candidate interactions
* Interaction confidence
* Network topology
* Protein neighborhoods
* Candidate interaction clusters

The result is a navigable, physics-based representation of the interactome.

---

## 4. Aerogel UX & Telemetry Interface

Y2H-AI uses a bespoke **Aerogel-inspired scientific interface** designed around high information density and rapid interpretation.

The interface combines:

* Scientific data panels
* Interactive analysis rails
* Model telemetry
* Prediction statistics
* Network visualization
* 3D molecular visualization
* Real-time API status information

---

# 📸 Feature Showcase

<div align="center">

|                                                         Interaction Laboratory                                                         |                                                         Protein 3D Observatory                                                         |
| :------------------------------------------------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------------------------------------------: |
| <img width="500" alt="Interaction Laboratory" src="https://github.com/user-attachments/assets/40c73ad6-b14e-4206-a4b7-a2f236f73697" /> | <img width="500" alt="Protein 3D Observatory" src="https://github.com/user-attachments/assets/520e1292-b185-4c20-a594-a7deb298ef99" /> |
|                                      *Pairwise prediction with calibrated statistical confidence.*                                     |                                           *AlphaFold structure resolution and 3D rendering.*                                           |

<br>

|                                                         3D Network Explorer                                                         |                                                         Model Telemetry                                                         |
| :---------------------------------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------------------------: |
| <img width="500" alt="3D Network Explorer" src="https://github.com/user-attachments/assets/544c335b-8b53-4eff-9f53-c3cbdb62bd50" /> | <img width="500" alt="Model Telemetry" src="https://github.com/user-attachments/assets/81b3b50c-4932-418f-8e22-b5177ee9a2b8" /> |
|                                            *Physics-based interaction topology mapping.*                                            |                                    *Transparent ML performance metrics and feature analysis.*                                   |

</div>

---

# 🛠️ Tech Stack & Engineering

Y2H-AI uses a decoupled architecture separating the computational inference layer from the interactive visualization layer.

### Frontend

* **Next.js 14**
* **React**
* **TypeScript**
* **TailwindCSS**
* **React Three Fiber**
* **3Dmol.js**
* **WebGL**

### Backend

* **Python**
* **FastAPI**
* **Scikit-Learn**
* **Pandas**
* **Joblib**

### Data & ML

* **BioGRID interactome data**
* **Negatome-derived negative evidence**
* **Parquet feature stores**
* **Calibrated Random Forest models**
* **Protein sequence-derived features**
* **Physicochemical descriptors**

### Deployment

* **Vercel** — Frontend
* **Render** — Python inference API

---

# 💻 Quick Start

## 1. Clone the Repository

```bash
git clone https://github.com/balajiprincejoshva-byte/y2h-ai.git
cd y2h-ai
```

## 2. Start the AI Backend

```bash
pip install -r requirements.txt

uvicorn src.y2h_ppi.api.main:app \
  --host 0.0.0.0 \
  --port 8000
```

## 3. Start the Frontend

```bash
cd web

npm install
npm run dev
```

The frontend will be available at:

```text
http://localhost:3000
```

---

# 🔬 Scientific Methodology & Model Architecture

Y2H-AI operates on a **V3 Random Forest inference pipeline** trained using curated physical protein-protein interaction data.

The architecture consists of three primary phases.

---

## Phase 1 — Data Ingestion & Feature Engineering

Raw interaction datasets can contain experimental noise, incomplete observations, and heterogeneous evidence.

Y2H-AI processes the available interaction evidence into structured training and inference features.

### Curated Negative Evidence

Negative examples are constructed to reduce class imbalance and minimize potential topological leakage between training and evaluation data.

### Feature Extraction

Protein information is transformed into machine-learning features using:

* Sequence-derived representations
* Physicochemical descriptors
* Interaction-derived features
* Protein-level metadata
* Structural context where available

These features are transformed into dense numerical representations suitable for ensemble learning.

---

# Phase 2 — Calibrated Inference

Traditional classifiers can produce probabilities that do not accurately represent empirical likelihood.

Y2H-AI therefore applies **Isotonic Calibration** to the Random Forest output.

The goal is to make predicted probabilities better aligned with observed interaction frequencies.

For example:

> A calibrated prediction of `0.80` should be interpreted as an estimated 80% interaction probability under the model's calibration and evaluation assumptions — **not as a guarantee of experimental interaction**.

This distinction is important when using machine-learning predictions to prioritize wet-lab validation.

---

# Phase 3 — Structural & Network Resolution

Once a protein interaction hypothesis is evaluated, Y2H-AI connects the prediction with structural and network-level evidence.

### Network Candidate Discovery

The system searches the interaction registry to identify and rank candidate interactors based on model predictions.

### Structural Resolution

Protein identifiers can be mapped to corresponding AlphaFold structural models for downstream 3D visualization.

This allows the platform to move from:

**Prediction → Network → Structure**

within a single workflow.

---

# ⚙️ Systems Topology

Y2H-AI follows a decoupled computational architecture.

```text
                    ┌─────────────────────────┐
                    │       Next.js UI         │
                    │   Scientific Dashboard   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      FastAPI Layer       │
                    │   REST API / Inference   │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
      ┌──────────────┐   ┌───────────────┐  ┌──────────────┐
      │ Random Forest│   │ Feature Store │  │ AlphaFold    │
      │ V3 Pipeline  │   │   Parquet     │  │ Structures   │
      └──────────────┘   └───────────────┘  └──────────────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  3D Network + Protein   │
                    │       Visualization     │
                    └─────────────────────────┘
```

### Inference Layer

**Python / FastAPI**

Handles:

* Machine-learning inference
* Feature processing
* Pandas transformations
* Model deserialization
* Prediction calibration
* API requests

### Storage Layer

**Parquet**

Compressed feature stores provide efficient access to structured interaction and feature data without requiring a heavyweight relational database for the core inference workflow.

### Client Visualization Layer

**Next.js / WebGL**

The browser handles:

* Interactive protein visualization
* 3D molecular rendering
* Force-directed network visualization
* Scientific dashboard rendering
* Model telemetry

Hardware-accelerated WebGL enables the interface to render complex 3D biological data directly in the browser.

---

# 🧪 Research Workflow

```text
Protein A + Protein B
          │
          ▼
   Feature Extraction
          │
          ▼
   Random Forest V3
          │
          ▼
 Isotonic Calibration
          │
          ▼
 Interaction Probability
          │
          ├───────────────┐
          ▼               ▼
   Network Context    AlphaFold
          │             Structure
          └───────┬───────┘
                  ▼
          Integrated Analysis
```

---

# 🎯 Project Goals

Y2H-AI is designed to demonstrate how modern computational biology systems can combine:

* Machine learning
* Protein interaction data
* Structural biology
* Network science
* 3D visualization
* Scientific computing
* Modern web engineering

The long-term objective is to provide a unified computational environment for **protein interaction hypothesis generation and structural exploration**.

---

<div align="center">

## 🧬 Y2H-AI

**Predict. Visualize. Explore.**

<br>

<i>Engineered by Balaji Muthukumar</i>

</div>
