import plotly.graph_objects as go
import numpy as np

def render_3d_network(net_data: dict, query_protein: str):
    """Render a 3D protein interaction network using Plotly."""
    nodes = net_data.get('nodes', [])
    edges = net_data.get('edges', [])
    
    # 1. Distribute nodes in 3D space (simple spring layout approximation or random sphere)
    # Since we don't have networkx running in this component, we'll do a simple sphere layout
    # Center query node
    pos = {query_protein: (0, 0, 0)}
    
    # Distribute others on a sphere
    other_nodes = [n for n in nodes if n['id'] != query_protein]
    phi = np.random.uniform(0, np.pi, len(other_nodes))
    costheta = np.random.uniform(-1, 1, len(other_nodes))
    u = np.random.uniform(0, 1, len(other_nodes))
    theta = np.arccos(costheta)
    r = 10 * np.cbrt(u)
    
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    
    for i, n in enumerate(other_nodes):
        pos[n['id']] = (x[i], y[i], z[i])
        
    # 2. Build Edge Traces
    edge_x = []
    edge_y = []
    edge_z = []
    
    pred_edge_x = []
    pred_edge_y = []
    pred_edge_z = []
    
    for edge in edges:
        x0, y0, z0 = pos.get(edge['source'], (0,0,0))
        x1, y1, z1 = pos.get(edge['target'], (0,0,0))
        
        if edge.get('type') == 'predicted_candidate':
            pred_edge_x.extend([x0, x1, None])
            pred_edge_y.extend([y0, y1, None])
            pred_edge_z.extend([z0, z1, None])
        else:
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_z.extend([z0, z1, None])
            
    trace_edges = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(color='rgba(16, 185, 129, 0.5)', width=2),
        name='Documented Edge',
        hoverinfo='none'
    )
    
    trace_pred_edges = go.Scatter3d(
        x=pred_edge_x, y=pred_edge_y, z=pred_edge_z,
        mode='lines',
        line=dict(color='rgba(245, 158, 11, 0.8)', width=3, dash='dash'),
        name='Predicted Candidate',
        hoverinfo='none'
    )
    
    # 3. Build Node Traces
    node_x = []
    node_y = []
    node_z = []
    node_color = []
    node_text = []
    node_size = []
    
    for n in nodes:
        nx, ny, nz = pos.get(n['id'], (0,0,0))
        node_x.append(nx)
        node_y.append(ny)
        node_z.append(nz)
        node_text.append(f"{n['label']}<br>Degree: {n.get('degree', 1)}")
        
        if n['id'] == query_protein:
            node_color.append('#3B82F6') # Blue for query
            node_size.append(15)
        else:
            node_color.append('#94A3B8') # Gray for others
            node_size.append(8)
            
    trace_nodes = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        text=[n['id'] for n in nodes],
        textposition="top center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line_width=2,
            line_color='white'
        ),
        name='Proteins'
    )
    
    # 4. Layout
    layout = go.Layout(
        scene=dict(
            xaxis=dict(showbackground=False, showticklabels=False, title=''),
            yaxis=dict(showbackground=False, showticklabels=False, title=''),
            zaxis=dict(showbackground=False, showticklabels=False, title=''),
            bgcolor='#0F172A'
        ),
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            font=dict(color="white")
        ),
        paper_bgcolor='#0F172A',
        plot_bgcolor='#0F172A'
    )
    
    fig = go.Figure(data=[trace_edges, trace_pred_edges, trace_nodes], layout=layout)
    return fig
