import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from y2h_ppi.api.schemas import PredictRequest, BatchPredictRequest, PredictResponse, NetworkResponse
from y2h_ppi.inference.predictor import PPIPredictor
from y2h_ppi.network.graph_builder import build_protein_network
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI(
    title="Y2H-AI API Platform",
    description="AI-Driven Computational Platform for Yeast Protein-Protein Interaction Prediction",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = PPIPredictor()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Y2H-AI Prediction Platform", "version": "0.1.0"}

@app.post("/predict", response_model=PredictResponse)
def predict_pair(req: PredictRequest):
    try:
        res = predictor.predict_pair(
            protein_a=req.protein_a,
            protein_b=req.protein_b,
            seq_a=req.sequence_a,
            seq_b=req.sequence_b
        )
        return res
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail={"code": "MODEL_UNAVAILABLE", "message": "The validated prediction model is currently unavailable."}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict/batch")
def predict_batch(req: BatchPredictRequest):
    if len(req.pairs) > 500:
        raise HTTPException(status_code=400, detail="Batch size exceeds maximum limit of 500 pairs.")
    try:
        res = predictor.predict_batch(req.pairs)
        return {"results": res, "total_scored": len(res)}
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail={"code": "MODEL_UNAVAILABLE", "message": "The validated prediction model is currently unavailable."}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/protein/{protein_id}/known_interactors", response_model=NetworkResponse)
def get_known_interactors(protein_id: str):
    net_data = build_protein_network(protein_id)
    return net_data

@app.get("/proteins/search")
def search_proteins(query: str = ""):
    registry_path = Path("data/processed/yeast_protein_registry.parquet")
    if not registry_path.exists():
        return {"results": []}
    
    df = pd.read_parquet(registry_path)
    q = query.upper().strip()
    
    if not q:
        results = df.head(100).fillna("").to_dict(orient="records")
    else:
        # Search by systematic name, standard name, or Uniprot/SGDID
        mask = (
            df["protein_id"].str.contains(q, na=False) |
            df["standard_name"].str.contains(q, na=False) |
            df["sgdid"].str.contains(q, na=False)
        )
        results = df[mask].head(100).fillna("").to_dict(orient="records")
        
    for r in results:
        # Don't send the entire sequence over the wire for search
        r.pop("sequence", None)
        
    return {"results": results}

@app.get("/model/metrics")
def get_model_metrics():
    report_path = Path("reports/v3_evaluation_results.json")
    if not report_path.exists():
        raise HTTPException(status_code=444, detail="Evaluation results not found. Run Phase 5 pipeline first.")
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

@app.get("/model/card")
def get_model_card():
    card_path = Path("reports/model_card.md")
    if not card_path.exists():
        raise HTTPException(status_code=404, detail="Model card not found.")
    return FileResponse(card_path, media_type="text/markdown")

@app.get("/model/ablation")
def get_model_ablation():
    ablation_path = Path("reports/ablation_results.json")
    if not ablation_path.exists():
        raise HTTPException(status_code=404, detail="Ablation results not found.")
    with open(ablation_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/provenance")
def get_provenance():
    manifest_path = Path("reports/v3_run_manifest.json")
    if not manifest_path.exists():
        raise HTTPException(status_code=404, detail="Manifest not found.")
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)

import requests

@app.get("/protein/{protein_id}/structure")
def get_protein_structure(protein_id: str):
    """
    Looks up structural models for yeast proteins using UniProt and AlphaFold DB.
    """
    pid = protein_id.upper().strip()
    
    KNOWN_MAPPINGS = {
        "YAL001C": "P34111",
        "YFL039C": "P60010",
        "YAL034C": "P00549",
        "YAL068C": "P18962"
    }
    
    try:
        if pid in KNOWN_MAPPINGS:
            uniprot_id = KNOWN_MAPPINGS[pid]
        else:
            # Configure resilient session
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            session = requests.Session()
            retries = Retry(total=3, backoff_factor=1, status_forcelist=[ 500, 502, 503, 504 ])
            session.mount('https://', HTTPAdapter(max_retries=retries))
            
            # 1. Look up UniProt Accession for the S. cerevisiae protein
            uniprot_url = f"https://rest.uniprot.org/uniprotkb/search?query={pid}+AND+organism_id:559292&format=json"
            res = session.get(uniprot_url, timeout=15)
            res.raise_for_status()
            data = res.json()
            
            if not data.get("results"):
                return {
                    "protein_id": pid,
                    "structure_available": False,
                    "message": "No validated structure available for this protein."
                }
                
            uniprot_id = data["results"][0]["primaryAccession"]
        
        # 2. Return the AlphaFold PDB URL
        af_url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v6.pdb"
        
        return {
            "protein_id": pid,
            "structure_available": True,
            "source": "AlphaFold DB",
            "pdb_url": af_url
        }
        
    except Exception as e:
        return {
            "protein_id": pid,
            "structure_available": False,
            "message": f"Structure lookup failed: {str(e)}"
        }

@app.get("/network/{protein_id}/candidates")
def get_network_candidates(protein_id: str, limit: int = 25):
    """Generate missing candidate interactions for the neighborhood."""
    net_data = build_protein_network(protein_id, depth=2)
    
    known_partners = set()
    all_nodes = set()
    for edge in net_data['edges']:
        if edge['source'] == protein_id.upper():
            known_partners.add(edge['target'])
        elif edge['target'] == protein_id.upper():
            known_partners.add(edge['source'])
            
    for node in net_data['nodes']:
        all_nodes.add(node['id'])
        
    candidates = all_nodes - known_partners - {protein_id.upper()}
    
    if not candidates:
        return {"query_protein": protein_id, "candidates": []}
        
    candidate_list = list(candidates)[:limit]
    pairs = [(protein_id, c) for c in candidate_list]
    
    # Batch predict
    try:
        res = predictor.predict_batch(pairs)
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail={"code": "MODEL_UNAVAILABLE", "message": "The validated prediction model is currently unavailable."}
        )
    
    # Format and sort
    out = []
    for r in res:
        out.append({
            "source": protein_id.upper(),
            "target": r["protein_b"],
            "probability": r["calibrated_probability"],
            "calibrated_probability": r["calibrated_probability"],
            "prediction_id": r["prediction_id"],
            "model_version": r["model"]["version"],
            "documentation_status": r["documentation"]["status"]
        })
        
    out = sorted(out, key=lambda x: x["probability"], reverse=True)
    return {"query_protein": protein_id, "candidates": out[:limit]}
