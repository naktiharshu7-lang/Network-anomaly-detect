# insight.py
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import random

# ---------------- Styles ---------------- #
styles = {
    'bg': '#0b0f1a',
    'card': '#151a2d',
    'accent': '#6f3dff',
    'danger': '#ff4d6d',
    'warning': '#ffb74d',
    'success': '#00e5a8',
    'text': '#e6e6f0',
    'muted': '#9aa4bf'
}

# ---------------- Layout ---------------- #
def get_insights_layout():
    return dbc.Container([
        # Interval for live updates
        dcc.Interval(id="update-interval", interval=2000, n_intervals=0),

        # Header
        dbc.Row([
            dbc.Col(html.H2("🚀 Advanced Insight Dashboard", style={'color': styles['text'], 'fontWeight': '700'}), md=10),
            dbc.Col(dbc.Button("⬅ Back to Dashboard", href="/", color="secondary"), md=2)
        ], className="mb-4"),

        # Summary Cards
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("🔥 Max Z-Score", className="card-title", style={'color': styles['accent']}),
                html.H2(id="max-z", style={'color': styles['danger'], 'fontWeight': 'bold'}),
            ]), style={'background': 'linear-gradient(135deg,#1f1a2d,#261d3a)','boxShadow':'0 4px 20px rgba(0,0,0,0.6)'}), md=3),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("⚡ Critical Index", className="card-title", style={'color': styles['accent']}),
                html.H2(id="critical-idx", style={'color': styles['warning'], 'fontWeight': 'bold'}),
            ]), style={'background': 'linear-gradient(135deg,#1f1a2d,#261d3a)','boxShadow':'0 4px 20px rgba(0,0,0,0.6)'}), md=3),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("📊 Total Anomalies", className="card-title", style={'color': styles['accent']}),
                html.H2(id="total-anomalies", style={'color': styles['success'], 'fontWeight': 'bold'}),
            ]), style={'background': 'linear-gradient(135deg,#1f1a2d,#261d3a)','boxShadow':'0 4px 20px rgba(0,0,0,0.6)'}), md=3),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("⚙ Threshold", className="card-title", style={'color': styles['accent']}),
                dcc.Slider(id="threshold-slider", min=0, max=6, step=0.1, value=3,
                           marks={i:str(i) for i in range(0,7)}, tooltip={"placement":"top","always_visible":True})
            ]), style={'background': 'linear-gradient(135deg,#1f1a2d,#261d3a)','boxShadow':'0 4px 20px rgba(0,0,0,0.6)'}), md=3)
        ], className="mb-4"),

        # Trend Graph
        dbc.Row([dbc.Col(dbc.Card([
            dbc.CardHeader("📈 Anomaly Trend", style={'color': styles['accent'], 'fontWeight': '600'}),
            dbc.CardBody(dcc.Graph(id="trend-graph", config={'displayModeBar': False}))
        ], style={'backgroundColor': styles['card'],'boxShadow':'0 0 35px rgba(0,0,0,0.6)'}), md=12)], className="mb-4"),

        # Top Anomalies Table + AI Explanation
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("🔥 Top 10 Critical Anomalies", style={'color': styles['accent'], 'fontWeight': '600'}),
                dbc.CardBody(dbc.Table(id="top-anomalies-table", bordered=True, striped=True, hover=True,
                                       style={'color': styles['text'], 'backgroundColor': styles['card']}))
            ]), md=6),

            dbc.Col(dbc.Card([
                dbc.CardHeader("🤖 AI Explanation", style={'color': styles['accent'], 'fontWeight': '600'}),
                dbc.CardBody(html.Div(id="ai-explain-panel", style={'color': styles['text'], 'lineHeight':'1.8'}))
            ]), md=6)
        ])
    ], fluid=True, style={'backgroundColor': styles['bg'],'minHeight':'100vh','paddingTop':'30px'})


# ---------------- Callback ---------------- #
@callback(
    Output("trend-graph","figure"),
    Output("top-anomalies-table","children"),
    Output("ai-explain-panel","children"),
    Output("max-z","children"),
    Output("critical-idx","children"),
    Output("total-anomalies","children"),
    Input("update-interval","n_intervals"),
    Input("threshold-slider","value")
)
def update_dashboard(n, threshold):

    # Simulated dynamic Z-score data
    zscores = np.array([round(random.uniform(2,5.5),2) for _ in range(20)])
    idx = np.arange(1,len(zscores)+1)

    # ---------------- Trend Graph ---------------- #
    colors = [styles['danger'] if z>threshold+1 else styles['warning'] if z>threshold else styles['accent'] for z in zscores]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=idx, y=zscores, mode='lines+markers',
        line=dict(color=styles['accent'], width=3),
        marker=dict(size=12, color=colors),
        hovertemplate="Index: %{x}<br>Z-Score: %{y}<extra></extra>"
    ))
    fig.add_hline(y=threshold, line_dash="dash", line_color=styles['danger'], annotation_text=f"Threshold={threshold}")
    fig.update_layout(template="plotly_dark", paper_bgcolor=styles['card'], plot_bgcolor=styles['card'],
                      font_color=styles['text'], height=450, margin=dict(l=30,r=30,t=40,b=30))

    # ---------------- Top Anomalies Table ---------------- #
    top_idx = np.argsort(zscores)[-10:][::-1]
    table_header = [html.Thead(html.Tr([html.Th("Rank"), html.Th("Index"), html.Th("Z-Score"), html.Th("Severity")]))]
    table_rows = []
    for rank,i in enumerate(top_idx,1):
        z = zscores[i]
        if z>threshold+1:
            severity = dbc.Badge("High", color="danger", className="ml-1")
        elif z>threshold:
            severity = dbc.Badge("Medium", color="warning", className="ml-1")
        else:
            severity = dbc.Badge("Low", color="secondary", className="ml-1")
        table_rows.append(html.Tr([html.Td(rank), html.Td(i+1), html.Td(f"{z:.2f}"), html.Td(severity)]))
    table_body = [html.Tbody(table_rows)]

    # ---------------- AI Explanation Panel ---------------- #
    explain_items = []
    for i in top_idx:
        explain_items.append(
            dbc.Collapse(
                dbc.Card([
                    dbc.CardHeader(f"Index {i+1} Explanation", style={'color': styles['accent']}),
                    dbc.CardBody(f"Z-Score = {zscores[i]:.2f}. Detected anomaly above threshold. "
                                 f"Recommendation: Investigate this metric and compare with historical patterns.")
                ]),
                id=f"collapse-{i+1}",
                is_open=True
            )
        )

    # ---------------- Summary Metrics ---------------- #
    max_z = f"{zscores.max():.2f}"
    critical_idx = f"{zscores.argmax()+1}"
    total_anomalies = np.sum(zscores>threshold)

    return fig, table_header+table_body, explain_items, max_z, critical_idx, total_anomalies


# ---------------- Run App ---------------- #
if __name__=="__main__":
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = get_insights_layout()
    app.run_server(debug=True)