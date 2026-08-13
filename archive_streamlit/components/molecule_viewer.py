import py3Dmol
import requests
import streamlit as st
import streamlit.components.v1 as components

def fetch_pdb_content(url: str) -> str:
    """Fetch PDB text content from a URL."""
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text
        return None
    except:
        return None

def render_molecule(pdb_data: str, style: str = "cartoon", color: str = "spectrum", width: int = 800, height: int = 500):
    """
    Render a 3D molecule using py3Dmol.
    style: 'cartoon', 'stick', 'sphere', 'surface'
    color: 'spectrum', 'chain', or a specific color name
    """
    view = py3Dmol.view(width=width, height=height)
    view.addModel(pdb_data, "pdb")
    
    if style == "cartoon":
        view.setStyle({'cartoon': {'color': color}})
    elif style == "stick":
        view.setStyle({'stick': {}})
    elif style == "surface":
        view.addSurface(py3Dmol.VDW, {'opacity': 0.8, 'color': 'white'})
    elif style == "sphere":
        view.setStyle({'sphere': {}})
        
    view.zoomTo()
    
    # Generate HTML and embed in Streamlit
    html = view._make_html()
    
    # Replace the py3dmol default full page CSS to fit in container properly
    html = html.replace('width: 100%; height: 100%;', f'width: {width}px; height: {height}px;')
    
    components.html(html, height=height + 20)

def render_conceptual_interaction(prob: float, width: int = 800, height: int = 400):
    """
    Render a purely conceptual visualization of an interaction hypothesis, 
    making sure NOT to pretend it's a real physical docking.
    """
    st.markdown("<div style='text-align: center; color: #94A3B8; font-style: italic; margin-bottom: 10px;'>Conceptual interaction visualization — not an atomic docking prediction.</div>", unsafe_allow_html=True)
    
    # We will just draw two spheres connected by a dashed line using raw HTML/SVG
    opacity = max(0.2, prob)
    stroke_dash = "5,5" if prob < 0.7 else "0"
    
    svg = f"""
    <svg width="100%" height="{height}" style="background-color: #0F172A; border-radius: 10px;">
        <circle cx="30%" cy="50%" r="50" fill="#3B82F6" />
        <text x="30%" y="50%" fill="white" font-family="sans-serif" font-size="14" text-anchor="middle" dy=".3em">Protein A</text>
        
        <circle cx="70%" cy="50%" r="50" fill="#10B981" />
        <text x="70%" y="50%" fill="white" font-family="sans-serif" font-size="14" text-anchor="middle" dy=".3em">Protein B</text>
        
        <line x1="30%" y1="50%" x2="70%" y2="50%" stroke="#F8FAFC" stroke-width="{prob * 10}" stroke-dasharray="{stroke_dash}" stroke-opacity="{opacity}" />
        <text x="50%" y="45%" fill="white" font-family="sans-serif" font-size="16" text-anchor="middle">P(interaction) = {prob:.2f}</text>
    </svg>
    """
    st.markdown(svg, unsafe_allow_html=True)
