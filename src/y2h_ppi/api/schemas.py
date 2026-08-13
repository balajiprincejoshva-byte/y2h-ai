from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Dict, Any

class PredictRequest(BaseModel):
    protein_a: str = Field(..., example="YFL039C")
    protein_b: str = Field(..., example="YAL001C")
    sequence_a: Optional[str] = None
    sequence_b: Optional[str] = None

class BatchPredictRequest(BaseModel):
    pairs: List[Tuple[str, str]] = Field(..., example=[("YFL039C", "YAL001C"), ("YFL039C", "YOR001W")])

class ModelMetadata(BaseModel):
    name: str
    version: str
    feature_version: str

class CalibrationMetadata(BaseModel):
    method: str

class DocumentationStatus(BaseModel):
    status: str
    source: str

class PredictResponse(BaseModel):
    prediction_id: str
    protein_a: str
    protein_b: str
    raw_probability: Optional[float] = None
    calibrated_probability: float
    confidence_band: str
    model: ModelMetadata
    calibration: CalibrationMetadata
    documentation: DocumentationStatus
    nearest_known_interactors: List[Tuple[str, float]]
    provenance_trace: Dict[str, Any]
    error: Optional[str] = None

class NetworkMetadata(BaseModel):
    source: str
    node_count: int
    edge_count: int
    depth: int
    truncated: bool

class NetworkResponse(BaseModel):
    query_gene: str
    total_nodes: int
    total_edges: int
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    metadata: NetworkMetadata
