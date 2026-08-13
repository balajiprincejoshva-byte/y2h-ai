import streamlit as st
import requests
import pandas as pd
from frontend.components.network_3d import render_3d_network
from frontend.components.style import load_css

st.set_page_config(page_title="3D Network Explorer | Y2H-AI", page_icon="🌐", layout="wide")
load_css()

API_BASE = "http://localhost:8000"

st.title("🌐 3D Protein Interaction Network")
st.markdown("*Navigate known biological neighborhoods and expand them with computationally prioritized predictions.*")

st.markdown("---")

col_search, col_action = st.columns([2, 1])

with col_search:
    query_node = st.text_input("Enter Query Protein (e.g., YFL039C)", "YFL039C")
    
with col_action:
    st.write("")
    st.write("")
    expand = st.button("🔮 Predict Missing Interactions", type="primary")

try:
    # 1. Fetch Known Network
    net_res = requests.get(f"{API_BASE}/protein/{query_node}/known_interactors")
    if net_res.status_code == 200:
        net_data = net_res.json()
        
        # Mark all as documented
        for e in net_data.get('edges', []):
            e['type'] = 'documented_reference'
            
        # 2. Add Predicted Candidates if requested
        candidates = []
        if expand:
            with st.spinner("Generating computationally prioritized candidates..."):
                cand_res = requests.get(f"{API_BASE}/network/{query_node}/candidates?limit=10")
                if cand_res.status_code == 200:
                    candidates = cand_res.json().get("candidates", [])
                    
                    # Add candidate nodes and edges to network
                    for c in candidates:
                        if not any(n['id'] == c['target'] for n in net_data['nodes']):
                            net_data['nodes'].append({"id": c['target'], "label": c['target'], "degree": 1})
                        
                        net_data['edges'].append({
                            "source": c['source'],
                            "target": c['target'],
                            "type": "predicted_candidate",
                            "probability": c['probability']
                        })
                    st.success(f"Added top {len(candidates)} computationally prioritized candidate edges.")
        
        # 3. Render 3D Network
        st.plotly_chart(render_3d_network(net_data, query_node), use_container_width=True)
        
        # 4. Legend & Info
        st.markdown("""
        **Legend**: 
        🔵 Query Protein | ⚪ Documented Interactor 
        <span style='color:#10B981'>━━</span> Documented Edge | <span style='color:#F59E0B'>┄┄</span> Predicted Edge
        """, unsafe_allow_html=True)
        
        st.caption("*Disclaimer: Predicted edges are computationally prioritized and have not been experimentally validated. Absence of an edge does not establish non-interaction.*")
        
        # 5. Candidate Ranking Table
        if candidates:
            st.markdown("---")
            st.subheader("Candidate Ranking Panel")
            df = pd.DataFrame(candidates)
            df = df[['target', 'probability', 'model_version', 'documentation_status', 'prediction_id']]
            df.columns = ["Protein", "Probability", "Model", "Reference Status", "Prediction ID"]
            st.dataframe(df, use_container_width=True)
            
    else:
        st.warning("Could not fetch known interactors for this protein.")
except Exception as e:
    st.error(f"API Error: {e}")
