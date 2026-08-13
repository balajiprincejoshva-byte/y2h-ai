import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ApiError {
  isApiError: true;
  status: number;
  code?: string;
  message: string;
}

const handleApiError = (error: unknown): never => {
  if (axios.isAxiosError(error) && error.response) {
    const status = error.response.status;
    const data = error.response.data;
    
    let message = error.message;
    let code = undefined;
    
    if (data?.detail) {
      if (typeof data.detail === 'object' && data.detail.message) {
        message = data.detail.message;
        code = data.detail.code;
      } else if (typeof data.detail === 'string') {
        message = data.detail;
      }
    }

    const apiError: ApiError = {
      isApiError: true,
      status,
      code,
      message,
    };
    throw apiError;
  }
  throw error;
};

export interface PredictRequest {
  protein_a: string;
  protein_b: string;
  sequence_a?: string;
  sequence_b?: string;
}

export interface PredictResponse {
  prediction_id: string;
  protein_a: string;
  protein_b: string;
  raw_probability: number | null;
  calibrated_probability: number;
  confidence_band: string;
  model: {
    name: string;
    version: string;
    feature_version: string;
  };
  calibration: {
    method: string;
  };
  documentation: {
    status: string;
    source: string;
  };
  nearest_known_interactors: Array<[string, number]>;
  provenance_trace: Record<string, unknown>;
  error?: string;
}

export interface NetworkEdge {
  source: string;
  target: string;
  is_predicted: boolean;
  probability?: number;
}

export interface NetworkNode {
  id: string;
  degree: number;
  is_query: boolean;
}

export interface NetworkResponse {
  query_gene: string;
  total_nodes: number;
  total_edges: number;
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  metadata: {
    source: string;
    node_count: number;
    edge_count: number;
    depth: number;
    truncated: boolean;
  };
}

export interface NetworkCandidateEdge {
  source: string;
  target: string;
  probability: number;
  calibrated_probability: number;
  prediction_id: string;
  model_version: string;
  documentation_status: string;
}

export interface NetworkCandidatesResponse {
  query_protein: string;
  candidates: NetworkCandidateEdge[];
}

export interface ProteinStructureResponse {
  protein_id: string;
  structure_available: boolean;
  source?: string;
  pdb_url?: string;
  message?: string;
}

export interface ProvenanceManifest {
  run_id: string;
  timestamp: string;
  git_commit: string;
  python_version: string;
  dependency_lock_hash: string;
  dataset_hash: string;
  feature_hash: string;
  split_seed: number;
  model_seed: number;
  negative_sampling_seed: number;
  model_version: string;
  feature_version: string;
  evaluation_version: string;
}

export const Y2hApi = {
  getHealth: () => apiClient.get('/health').then(res => res.data).catch(handleApiError),
  
  searchProteins: (query: string) => 
    apiClient.get(`/proteins/search?query=${encodeURIComponent(query)}`).then(res => res.data).catch(handleApiError),
  
  predictPair: (data: PredictRequest) => 
    apiClient.post<PredictResponse>('/predict', data).then(res => res.data).catch(handleApiError),
    
  getKnownInteractors: (proteinId: string) => 
    apiClient.get<NetworkResponse>(`/protein/${proteinId}/known_interactors`).then(res => res.data).catch(handleApiError),
    
  getNetworkCandidates: (proteinId: string, limit: number = 25) =>
    apiClient.get<NetworkCandidatesResponse>(`/network/${proteinId}/candidates?limit=${limit}`).then(res => res.data).catch(handleApiError),
    
  getProteinStructure: (proteinId: string) =>
    apiClient.get<ProteinStructureResponse>(`/protein/${proteinId}/structure`).then(res => res.data).catch(handleApiError),
    
  getModelMetrics: () => apiClient.get('/model/metrics').then(res => res.data).catch(handleApiError),
  
  getModelAblation: () => apiClient.get('/model/ablation').then(res => res.data).catch(handleApiError),
  
  getProvenance: () => apiClient.get<ProvenanceManifest>('/provenance').then(res => res.data).catch(handleApiError),
};
