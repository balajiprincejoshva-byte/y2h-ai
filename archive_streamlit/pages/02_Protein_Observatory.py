import streamlit as st
import requests
from frontend.components.molecule_viewer import render_molecule, fetch_pdb_content
from frontend.components.style import load_css

st.set_page_config(page_title="Protein Observatory | Y2H-AI", page_icon="🧬", layout="wide")
load_css()

API_BASE = "http://localhost:8000"

st.title("🧬 Protein Observatory")
st.markdown("*Detailed biological and computational profile for individual proteins.*")

st.markdown("---")

prot_query = st.text_input("Enter Protein Identifier (e.g., YFL039C)", "YFL039C")

if st.button("View Profile", type="primary"):
    c1, c2, c3 = st.columns([1.5, 1, 1])
    
    with c1:
        st.subheader("3D Structure")
        meta = requests.get(f"{API_BASE}/protein/{prot_query}/structure").json()
        if meta.get("structure_available"):
            st.caption(f"Source: {meta.get('source')}")
            pdb_text = fetch_pdb_content(meta.get("pdb_url"))
            if pdb_text:
                render_molecule(pdb_text, width=500, height=450, color="spectrum")
            else:
                st.warning("Could not fetch PDB data.")
        else:
            st.info("No validated structural model is available for this protein.")
            st.markdown("#### Sequence-Level Representation")
            st.progress(0.7, text="Length: ~350 aa (Conceptual)")
            st.caption("Sequence-derived profiles are extracted natively by ESM-2 embeddings.")
            
    with c2:
        st.subheader("Profile")
        st.markdown(f"**Identifier:** `{prot_query}`")
        st.markdown("**Organism:** *Saccharomyces cerevisiae*")
        st.markdown("**Feature Vectors:**")
        st.markdown("- Classical: `Available (784 dim)`")
        st.markdown("- ESM-2: `Available (320 dim)`")
        
        st.markdown("### Structural Status")
        if meta.get("structure_available"):
            st.success("Validated structure mapped.")
        else:
            st.warning("Unmapped / Unavailable.")
            
    with c3:
        st.subheader("Network Context")
        try:
            net_res = requests.get(f"{API_BASE}/protein/{prot_query}/known_interactors")
            if net_res.status_code == 200:
                net_data = net_res.json()
                nodes = net_data.get("nodes", [])
                st.metric("Documented Y2H Partners", max(0, len(nodes) - 1))
                st.metric("Topology Degree", max(0, len(nodes) - 1))
                
                with st.expander("Known Interactors"):
                    for n in nodes:
                        if n['id'] != prot_query:
                            st.write(f"- {n['id']}")
            else:
                st.error("Network data unavailable.")
        except:
            st.error("Could not reach API.")
