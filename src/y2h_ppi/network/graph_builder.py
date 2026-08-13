import networkx as nx
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from y2h_ppi.logger import logger

INTERIM_DIR = Path("data/interim")

def build_protein_network(gene_id: str, depth: int = 1, max_nodes: int = 100) -> Dict[str, Any]:
    """Construct NetworkX interaction neighborhood graph for a given gene ID."""
    pos_path = INTERIM_DIR / "positives_mapped.parquet"
    gene_clean = gene_id.strip().upper()
    if not pos_path.exists():
        return {"query_gene": gene_clean, "nodes": [], "edges": [], "metadata": {}}
        
    df_pos = pd.read_parquet(pos_path)
    
    # 1-hop
    sub_df_1 = df_pos[(df_pos['protein_a'] == gene_clean) | (df_pos['protein_b'] == gene_clean)]
    
    edges_set = set()
    nodes = set([gene_clean])
    
    is_truncated = len(sub_df_1) > max_nodes
    if is_truncated:
        sub_df_1 = sub_df_1.head(max_nodes)
        
    for _, row in sub_df_1.iterrows():
        pa, pb = row['protein_a'], row['protein_b']
        nodes.add(pa)
        nodes.add(pb)
        edges_set.add((pa, pb))
        
    if depth == 2 and not is_truncated:
        neighbors = list(nodes - {gene_clean})
        sub_df_2 = df_pos[(df_pos['protein_a'].isin(neighbors)) | (df_pos['protein_b'].isin(neighbors))]
        
        for _, row in sub_df_2.iterrows():
            if len(nodes) >= max_nodes:
                is_truncated = True
                break
            pa, pb = row['protein_a'], row['protein_b']
            nodes.add(pa)
            nodes.add(pb)
            edges_set.add((pa, pb))
            
    edges = [{"source": u, "target": v, "type": "documented_biogrid", "confidence": 1.0} for u, v in edges_set]
    
    node_degrees = {n: 0 for n in nodes}
    for e in edges:
        node_degrees[e["source"]] += 1
        node_degrees[e["target"]] += 1
        
    node_list = [{"id": n, "label": n, "is_query": (n == gene_clean), "degree": node_degrees.get(n, 1)} for n in nodes]
    
    metadata = {
        "source": "BioGRID/Y2H V2 Canonical Dataset",
        "node_count": len(node_list),
        "edge_count": len(edges),
        "depth": depth,
        "truncated": is_truncated
    }
    
    return {
        "query_gene": gene_clean,
        "total_nodes": len(node_list),
        "total_edges": len(edges),
        "nodes": node_list,
        "edges": edges,
        "metadata": metadata
    }
