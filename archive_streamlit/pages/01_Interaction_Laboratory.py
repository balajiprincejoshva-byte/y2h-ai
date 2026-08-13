import streamlit as st
import requests
import time
from frontend.components.molecule_viewer import render_molecule, render_conceptual_interaction, fetch_pdb_content
from frontend.components.style import load_css

st.set_page_config(page_title="Interaction Laboratory | Y2H-AI", page_icon="🔬", layout="wide")
load_css()

API_BASE = "http://localhost:8000"

st.title("🔬 Molecular Interaction Laboratory")
st.markdown("*Explore sequence-derived protein interaction hypotheses using the Y2H-AI computational pipeline.*")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Protein A")
    prot_a = st.text_input("Protein A Identifier (e.g., YFL039C)", "YFL039C", key="pa")

with col2:
    st.subheader("Protein B")
    prot_b = st.text_input("Protein B Identifier (e.g., YLL050C)", "YLL050C", key="pb")

if st.button("⚡ Run Interaction Analysis", type="primary", use_container_width=True):
    if not prot_a or not prot_b:
        st.error("Please enter identifiers for both Protein A and Protein B.")
    else:
        # Visual Staged Analysis
        status_placeholder = st.empty()
        with status_placeholder.container():
            st.info("✓ Resolving sequences...")
            time.sleep(0.5)
            st.info("✓ Generating sequence feature vectors...")
            time.sleep(0.5)
            st.info("✓ Model inference executing...")
            
        try:
            res = requests.post(f"{API_BASE}/predict", json={"protein_a": prot_a, "protein_b": prot_b})
            if res.status_code == 200:
                data = res.json()
                
                status_placeholder.empty()
                
                # Result Card
                prob = data.get("calibrated_probability", 0.0)
                doc_status = data.get("documentation_status", "?")
                
                st.markdown("### Interaction Assessment")
                rc1, rc2, rc3 = st.columns(3)
                
                rc1.metric("Calibrated Probability", f"{prob*100:.1f}%")
                
                if doc_status == "Documented in reference database":
                    rc2.success("✓ Documented interaction")
                else:
                    rc2.warning("? No documented interaction found")
                    
                rc3.info(f"Model: {data.get('model_version', 'v2.0-RF')}")
                
                # 3D Visualization
                st.markdown("---")
                st.markdown("### 🧬 Molecular Interaction View")
                
                vc1, vc2 = st.columns(2)
                
                # Fetch Structure Meta
                meta_a = requests.get(f"{API_BASE}/protein/{prot_a}/structure").json()
                meta_b = requests.get(f"{API_BASE}/protein/{prot_b}/structure").json()
                
                with vc1:
                    st.markdown(f"**{prot_a} Structure**")
                    if meta_a.get("structure_available"):
                        st.caption(f"Source: {meta_a.get('source')}")
                        pdb_text = fetch_pdb_content(meta_a.get("pdb_url"))
                        if pdb_text:
                            render_molecule(pdb_text, width=400, height=350, color="chain")
                        else:
                            st.warning("Could not fetch PDB data.")
                    else:
                        st.warning("No validated structure available.")
                
                with vc2:
                    st.markdown(f"**{prot_b} Structure**")
                    if meta_b.get("structure_available"):
                        st.caption(f"Source: {meta_b.get('source')}")
                        pdb_text = fetch_pdb_content(meta_b.get("pdb_url"))
                        if pdb_text:
                            # Use a different color scheme to distinguish
                            render_molecule(pdb_text, width=400, height=350, style="cartoon", color="spectrum")
                        else:
                            st.warning("Could not fetch PDB data.")
                    else:
                        st.warning("No validated structure available.")
                        
                st.markdown("---")
                
                if st.checkbox("🔗 Show Interaction Hypothesis"):
                    render_conceptual_interaction(prob)
                    
                # Evidence Trail
                with st.expander("🔎 Evidence Trail & Technical Provenance", expanded=False):
                    st.markdown(f"""
                    **Prediction ID:** `{data.get('prediction_id', 'N/A')}`  
                    **Timestamp:** `{data.get('timestamp', 'N/A')}`  
                    **Feature Source:** `SGD FASTA -> ESM-2 + Classical`  
                    **Documentation Lookup:** `BioGRID v4.4.240 Physical Y2H`  
                    
                    *Scientific Note: Computational prioritization is not experimental confirmation. Absence from the reference datasets is not evidence of non-interaction.*
                    """)
                    
            else:
                status_placeholder.error(f"Inference API Error: {res.text}")
        except Exception as e:
            status_placeholder.error(f"Connection to Inference API failed. Is the backend running? ({e})")
