import plotly.graph_objects as go
import plotly.express as px

def render_c1_c2_c3_chart(eval_data: dict, metric: str = 'auroc'):
    """Render a C1/C2/C3 line chart for models."""
    splits = ['C1', 'C2', 'C3']
    
    # We will parse out Random Forest, Logistic Regression, DegreeHub, Random from the eval_data
    # The structure of eval_data is:
    # { "c1": { "1to1_balanced": { "models": { "Random Forest v2": {"auroc": 0.77}, "DegreeHub": ... } } } }
    
    # In V2, evaluation_results.json has a flat structure or nested. Let's assume nested from V2 logic.
    # We'll construct a mock structure parser based on standard V2 output.
    
    models = ["Random Forest", "Logistic Regression", "DegreeHub (Topology Baseline)"]
    colors = {"Random Forest": "#3B82F6", "Logistic Regression": "#10B981", "DegreeHub (Topology Baseline)": "#F59E0B"}
    
    fig = go.Figure()
    
    for model in models:
        y_vals = []
        for split in ['c1', 'c2', 'c3']:
            try:
                # Attempt to extract metric for 1:1 balanced
                val = eval_data[split]["1to1_balanced"]["models"][model][metric]
                y_vals.append(val)
            except:
                y_vals.append(None)
                
        if any(y_vals):
            fig.add_trace(go.Scatter(
                x=splits, 
                y=y_vals,
                mode='lines+markers',
                name=model,
                line=dict(color=colors.get(model, "#fff"), width=3),
                marker=dict(size=10)
            ))
            
    # Add random baseline
    fig.add_trace(go.Scatter(
        x=splits,
        y=[0.5, 0.5, 0.5] if metric == 'auroc' else [None, None, None],
        mode='lines',
        name='Random Baseline',
        line=dict(color='#ef4444', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title=f"Generalization Gap ({metric.upper()})",
        xaxis_title="Protein Novelty Split",
        yaxis_title=metric.upper(),
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        font=dict(color="white"),
        hovermode="x unified"
    )
    
    return fig

def render_ablation_chart(ablation_data: dict, split: str = 'c3'):
    """Render a bar chart for feature ablation."""
    
    # Data is like:
    # { "c3": { "Classical-Only": {"auroc": 0.67}, "ESM-2-Only": {"auroc": 0.64}, "Classical + ESM-2": ... } }
    try:
        data = ablation_data[split]
        features = list(data.keys())
        aurocs = [data[f].get('auroc', 0) for f in features]
        
        fig = go.Figure([go.Bar(
            x=features,
            y=aurocs,
            marker_color=['#3B82F6' if 'Combined' in f or '+' in f else '#94A3B8' for f in features]
        )])
        
        fig.update_layout(
            title=f"Feature Ablation ({split.upper()})",
            xaxis_title="Feature Set",
            yaxis_title="AUROC",
            paper_bgcolor="#0F172A",
            plot_bgcolor="#0F172A",
            font=dict(color="white")
        )
        # Add baseline line
        fig.add_hline(y=0.5, line_dash="dash", line_color="#ef4444", annotation_text="Random (0.5)")
        
        return fig
    except:
        return go.Figure()
