import streamlit as st
import requests
from frontend.components.model_plots import render_c1_c2_c3_chart, render_ablation_chart
import pandas as pd
from frontend.components.style import load_css

st.set_page_config(page_title="Model Reliability Observatory | Y2H-AI", page_icon="📊", layout="wide")
load_css()

API_BASE = "http://localhost:8000"

st.title("📊 Model Reliability Observatory")
st.markdown("*Transparent visualization of scientific model performance, ablation studies, and evaluation regimes.*")

st.markdown("---")

try:
    metrics_data = requests.get(f"{API_BASE}/model/metrics").json()
    ablation_data = requests.get(f"{API_BASE}/model/ablation").json()
    
    st.header("1. Model Generalization Landscape")
    st.markdown("""
    This section evaluates how well the models generalize across different levels of protein novelty using the Park & Marcotte (2012) evaluation scheme.
    - **C1 (Seen proteins)**: Both proteins in the test pair were seen during training.
    - **C2 (Partially novel)**: One protein is novel.
    - **C3 (Unseen proteins)**: Both proteins are novel to the model.
    """)
    
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.plotly_chart(render_c1_c2_c3_chart(metrics_data, metric="auroc"), use_container_width=True)
    with m_col2:
        st.plotly_chart(render_c1_c2_c3_chart(metrics_data, metric="auprc"), use_container_width=True)
        
    st.info("💡 **Scientific Observation:** The topology baseline (DegreeHub) collapses entirely in C3, demonstrating that network topology alone cannot predict interactions between unseen proteins. Sequence-based models retain significant signal.")
    
    st.markdown("---")
    st.header("2. Feature Contribution & Ablation (C3)")
    st.markdown("This chart isolates the contribution of Classical sequence descriptors vs ESM-2 representations in the hardest generalization task (C3).")
    
    a_col1, a_col2 = st.columns([2, 1])
    with a_col1:
        st.plotly_chart(render_ablation_chart(ablation_data, split="c3"), use_container_width=True)
        
    with a_col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.warning("⚠️ **Empirical Finding:** In the current C3 experiment, ESM-2 embeddings did not improve over classical sequence descriptors alone. The classical descriptors provided the most robust C3 signal.")
        
        c3_data = ablation_data.get('c3', {})
        if c3_data:
            df = pd.DataFrame([
                {"Feature Set": k, "AUROC": v.get("auroc")} for k,v in c3_data.items()
            ])
            st.dataframe(df, hide_index=True, use_container_width=True)
            
except Exception as e:
    st.error(f"Could not load canonical metrics. Is the API running? ({e})")
