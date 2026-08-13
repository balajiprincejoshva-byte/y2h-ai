import torch
import numpy as np
from typing import Dict, List, Optional
from y2h_ppi.logger import logger
from y2h_ppi.features.classic_descriptors import extract_classical_descriptors

class ESMEmbeddingExtractor:
    """ESM-2 protein language model embedding extractor with fast CPU capping & fallback."""
    
    def __init__(self, model_name: str = "facebook/esm2_t6_8M_UR50D", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.tokenizer = None
        self.model = None
        self._is_loaded = False
        
    def _load_model(self):
        if self._is_loaded:
            return
        try:
            from transformers import AutoTokenizer, AutoModel
            logger.info(f"Loading ESM-2 model '{self.model_name}' on {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.eval()
            self.model.to(self.device)
            self._is_loaded = True
            logger.info("ESM-2 model successfully loaded.")
        except Exception as e:
            logger.error(f"Could not load ESM-2 model '{self.model_name}' ({e}).")
            self._is_loaded = False
            raise RuntimeError(f"Failed to load ESM-2 model: {e}") from e
            
    def embed_sequences_batch(self, sequences: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """Extract mean-pooled ESM-2 protein embeddings for all proteins."""
        self._load_model()
        results = []
        n_seqs = len(sequences)
        
        if not self._is_loaded or self.model is None or self.tokenizer is None:
            raise RuntimeError(f"Cannot generate embeddings because ESM-2 model '{self.model_name}' is not loaded.")
            
        logger.info(f"Extracting ESM-2 embeddings for {n_seqs} sequences...")
        
        for i in range(0, n_seqs, batch_size):
            batch_seqs = sequences[i:i + batch_size]
            try:
                inputs = self.tokenizer(batch_seqs, return_tensors="pt", padding=True, truncation=True, max_length=256)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    hidden = outputs.last_hidden_state
                    mask = inputs['attention_mask'].unsqueeze(-1)
                    sum_embeddings = (hidden * mask).sum(dim=1)
                    sum_mask = mask.sum(dim=1).clamp(min=1)
                    mean_embeddings = (sum_embeddings / sum_mask).cpu().numpy()
                    
                    for emb in mean_embeddings:
                        results.append(emb.astype(np.float32))
            except Exception as e:
                logger.error(f"ESM-2 embedding failed for batch: {e}")
                raise RuntimeError(f"ESM-2 embedding inference failed: {e}") from e
                    
        return results

    def embed_sequence(self, sequence: str) -> np.ndarray:
        return self.embed_sequences_batch([sequence])[0]
