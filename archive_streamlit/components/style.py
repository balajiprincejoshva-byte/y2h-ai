import streamlit as st

def load_css():
    st.markdown("""
    <style>
    /* Premium Scientific Dark Theme */
    
    /* Global Backgrounds */
    .stApp {
        background-color: #0B0F19;
        color: #E2E8F0;
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Hide Streamlit Header */
    header {visibility: hidden;}
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC;
        font-weight: 500;
        letter-spacing: -0.02em;
    }
    
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        color: #38BDF8;
        font-family: 'SF Mono', 'Roboto Mono', monospace;
        font-weight: 600;
    }
    
    /* Buttons */
    div.stButton > button {
        background-color: #1E293B;
        color: #F8FAFC;
        border: 1px solid #334155;
        border-radius: 6px;
        transition: all 0.2s ease;
        font-weight: 500;
        letter-spacing: 0.01em;
    }
    div.stButton > button:hover {
        background-color: #334155;
        border-color: #475569;
        color: #38BDF8;
    }
    div.stButton > button[kind="primary"] {
        background-color: #0284C7;
        border-color: #0284C7;
        color: white;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #0369A1;
        border-color: #0369A1;
    }
    
    /* Custom Cards */
    .premium-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .premium-card:hover {
        border-color: #374151;
        transform: translateY(-2px);
    }
    .premium-card h4 {
        margin-top: 0;
        color: #38BDF8;
        font-size: 1.1rem;
        font-weight: 600;
        border-bottom: 1px solid #1F2937;
        padding-bottom: 12px;
        margin-bottom: 16px;
    }
    .premium-card p {
        color: #94A3B8;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 0;
    }
    
    /* Status Indicators */
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        font-family: 'SF Mono', monospace;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .status-success {
        background-color: rgba(16, 185, 129, 0.1);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    .status-warning {
        background-color: rgba(245, 158, 11, 0.1);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.2);
    }
    .status-info {
        background-color: rgba(56, 189, 248, 0.1);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.2);
    }
    
    /* Expander override */
    .streamlit-expanderHeader {
        background-color: #111827 !important;
        color: #E2E8F0 !important;
        border-radius: 6px !important;
        border: 1px solid #1F2937 !important;
    }
    
    /* Replace native info/success/warning boxes */
    div[data-testid="stAlert"] {
        background-color: #111827;
        border: 1px solid #1F2937;
        color: #E2E8F0;
    }
    </style>
    """, unsafe_allow_html=True)
