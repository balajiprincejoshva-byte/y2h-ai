import streamlit as st
import requests
import json
from frontend.components.style import load_css

st.set_page_config(page_title="Methods & Provenance | Y2H-AI", page_icon="📚", layout="wide")
load_css()

API_BASE = "http://localhost:8000"

st.title("📚 Scientific Methods & Data Provenance")
st.markdown("*Transparency into the data sources, modeling techniques, and biological assumptions underlying the platform.*")

st.markdown("---")

tab1, tab2 = st.tabs(["Data Provenance", "Methods Briefing"])

with tab1:
    st.header("Canonical Data Manifest")
    try:
        prov = requests.get(f"{API_BASE}/provenance").json()
        st.json(prov)
    except:
        st.error("Provenance manifest unavailable.")
        
with tab2:
    st.header("Methods & Limitations")
    try:
        card_res = requests.get(f"{API_BASE}/model/card")
        if card_res.status_code == 200:
            st.markdown(card_res.text)
        else:
            st.warning("Model card could not be loaded.")
    except:
        st.error("API Error.")

st.markdown("---")
st.markdown("""
### ⚠️ Scientific Interpretation Limitations

1. **Computational prioritization is not experimental confirmation.** Y2H-AI outputs probabilities meant to guide laboratory hypothesis generation.
2. **Absence from reference databases is not evidence of non-interaction.** Our strict non-overlap negatives assume unobserved pairs are negatives for training, but this is a noisy assumption.
3. **Generalization drops with novelty.** The model performs best on proteins similar to those in the training set (C1) and degrades when evaluating completely unstudied proteins (C3).
4. **Species Limitation.** This instance is explicitly trained on *Saccharomyces cerevisiae* and does not claim cross-species applicability.
""")
