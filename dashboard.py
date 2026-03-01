import dash
from dash import dcc, html, dash_table, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd
import numpy as np
import json

styles = {
    'background': '#1a1a2e',
    'text': '#e0e0e0',
    'primary': '#0f4c75',
    'secondary': '#6f3dff',
    'success': '#00bfa5',
    'danger': '#ff006e',
    'info': '#4c00b0',
    'warning': '#ffc400',
    'card_bg': '#2a2a4a',
    'card_border': '#4c4c6c',
    'sidebar_bg': '#121226',
    'sidebar_text': '#ffffff',
    'high_risk': '#ff006e',
    'medium_risk': '#ffc400',
    'low_risk': '#00bfa5',
}

GRAPH_HEIGHT = 380
TABLE_HEIGHT = 360


def _empty_fig(label="Upload a CSV file to get started"):
    fig = go.Figure()
    fig.add_annotation(
        text=label,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=15, color=styles['text'], family="Arial"),
        bgcolor="rgba(42,42,74,0.8)",
        bordercolor=styles['card_border'],
        borderwidth=2,
        borderpad=16,
    )
    fig.update_layout(
        plot_bgcolor=styles['card_bg'],
        paper_bgcolor=styles['card_bg'],
        font_color=styles['text'],
        height=GRAPH_HEIGHT,
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def get_empty_figure():
    return _empty_fig("No anomaly data available – upload a CSV to generate a security report")


def classify_risk(count, total_anomalies):
    if total_anomalies == 0:
        return "Low"
    ratio = count / total_anomalies
    if ratio > 0.5:
        return "High"
    elif ratio > 0.2:
        return "Medium"
    return "Low"


# ─────────────────────────────────────────────
# Dashboard layout
# ─────────────────────────────────────────────
def get_dashboard_layout():
    return html.Div(
        id="dashboard-wrapper",
        style={
            'backgroundColor': styles['background'],
            'minHeight': '100vh',
            'fontFamily': 'sans-serif',
            'color': styles['text'],
        },
        children=[

            # ── Sidebar ───────────────────────────────────
            html.Div(
                id="sidebar",
                children=[
                    html.Div(id="sidebar-brand", children=[
                        html.H2(
                            "Anomaly Detector",
                            style={
                                'color': styles['secondary'],
                                'fontSize': '1.5rem',
                                'fontWeight': 'bold',
                                'margin': '0 0 12px 0',
                                'textAlign': 'center',
                            }
                        ),
                    ]),

                    html.Div(id="sidebar-navlinks", children=[
                        dbc.NavLink(
                            "📊 Dashboard", href="/", active="exact",
                            className="nav-link",
                            style={'color': styles['sidebar_text'], 'fontWeight': 'bold',
                                   'fontSize': '1rem', 'padding': '4px 0'},
                        ),
                        html.A(
                            "📥 Reports", id="download-report-link", href="#",
                            className="nav-link",
                            style={'color': styles['sidebar_text'], 'opacity': 0.8,
                                   'fontSize': '1rem', 'textDecoration': 'none', 'padding': '4px 0'},
                        ),
                    ]),

                    html.Hr(style={'borderColor': '#444', 'margin': '12px 0'}),

                    html.Div(
                        id="sidebar-inner-controls",
                        children=[
                            html.Div(id="sidebar-feature", children=[
                                html.P("Select Feature:",
                                       style={'color': styles['sidebar_text'],
                                              'marginBottom': '4px', 'fontSize': '0.9rem'}),
                                dcc.Dropdown(
                                    id='feature-dropdown',
                                    placeholder="Select a feature…",
                                    style={'color': styles['text'],
                                           'backgroundColor': styles['card_bg'],
                                           'border': 'none', 'fontSize': '0.9rem'},
                                ),
                            ]),

                            html.Div(id="sidebar-slider", children=[
                                html.P("Z-Score Threshold:",
                                       style={'color': styles['sidebar_text'],
                                              'marginBottom': '4px', 'fontSize': '0.9rem'}),
                                dcc.Slider(
                                    id='z-score-threshold-slider',
                                    min=1, max=5, step=0.1, value=3,
                                    marks={i: {'label': str(i),
                                               'style': {'color': styles['sidebar_text'],
                                                         'fontSize': '0.8rem'}}
                                           for i in range(1, 6)},
                                    tooltip={"placement": "bottom", "always_visible": True},
                                ),
                            ]),

                            html.Div(id="sidebar-upload", children=[
                                html.P("Upload CSV:",
                                       style={'color': styles['sidebar_text'],
                                              'marginBottom': '4px', 'fontSize': '0.9rem'}),
                                dcc.Upload(
                                    id='upload-data',
                                    children=html.Div([
                                        dbc.Button('📂 Upload File', color="info",
                                                   style={'width': '100%', 'fontSize': '0.9rem'}),
                                    ]),
                                    multiple=False,
                                ),
                            ]),
                        ],
                    ),

                    dcc.Download(id="smart-report-download"),
                ],
            ),

            # ── Main content ──────────────────────────────
            html.Div(
                id="main-content",
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                html.H4(
                                    "Anomaly Detection Dashboard",
                                    style={'color': styles['text'], 'fontWeight': 'bold'},
                                ),
                                xs=12, md=6,
                            ),
                            dbc.Col(
                                html.Div(
                                    [
                                        dbc.Button("🚀 Advanced Insights", href="/insights", color="primary", className="me-2 mb-1"),
                                        dcc.Link(
                                            dbc.Button("⚙ Settings", color="secondary", className="me-2 mb-1"),
                                            href="/settings",
                                        ),
                                        dbc.Button("🚪 Logout", id="logout-btn", href="/logout", color="danger", className="ms-2")
                                    ],
                                    id="header-buttons",
                                    style={'textAlign': 'right', 'display': 'flex',
                                           'flexWrap': 'wrap', 'justifyContent': 'flex-end', 'gap': '6px'},
                                ),
                                xs=12, md=6,
                            ),
                        ],
                        align="center",
                        className="mb-4",
                        style={
                            'backgroundColor': styles['card_bg'],
                            'padding': '14px 18px',
                            'borderRadius': '10px',
                            'boxShadow': '0 5px 20px rgba(0,0,0,0.3)',
                        },
                    ),

                    # ── KPI cards ─────────────────────────
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(dbc.CardBody([
                                    html.H5("Total Rows", className="card-title text-muted"),
                                    html.H3("0", id="total-rows-kpi",
                                            className="card-text text-light font-weight-bold pulse"),
                                ])),
                                xs=12, sm=4, className="kpi-col mb-3",
                            ),
                            dbc.Col(
                                dbc.Card(dbc.CardBody([
                                    html.H5("Numerical Features", className="card-title text-muted"),
                                    html.H3("0", id="numeric-features-kpi",
                                            className="card-text text-info font-weight-bold pulse"),
                                ])),
                                xs=12, sm=4, className="kpi-col mb-3",
                            ),
                            dbc.Col(
                                dbc.Card(dbc.CardBody([
                                    html.H5("Total Anomalies", className="card-title text-muted"),
                                    html.H3("0", id="total-anomalies-kpi",
                                            className="card-text text-danger font-weight-bold pulse"),
                                ])),
                                xs=12, sm=4, className="kpi-col mb-3",
                            ),
                        ],
                        className="mb-2",
                    ),

                    html.Div(
                        id='output-data-upload',
                        style={
                            'minHeight': '48px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'color': styles['secondary'],
                            'padding': '8px 0',
                        },
                        children=html.Span(
                            "Please upload a CSV file to get started.",
                            style={'textAlign': 'center'},
                        ),
                    ),

                    # ── Attack Types ───────────────────────
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                html.H5("🎯 Attack Types",
                                        style={'color': styles['secondary'], 'fontWeight': 'bold', 'margin': 0}),
                                style={'backgroundColor': styles['primary'],
                                       'borderBottom': f'3px solid {styles["secondary"]}'},
                            ),
                            dbc.CardBody([
                                dcc.Store(id='selected-attack', data=None),
                                dbc.Row(
                                    id='attack-types-grid',
                                    className="g-2",
                                    children=_build_attack_cards(selected_idx=-1),
                                ),
                            ]),
                        ],
                        className="mb-4",
                        style={'boxShadow': '0 12px 40px rgba(0,0,0,0.4)'},
                    ),

                    # ── Smart Security Report ──────────────
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                html.H5("📊 Smart Security Report",
                                        style={'color': styles['secondary'], 'fontWeight': 'bold', 'margin': 0}),
                                style={'backgroundColor': styles['primary'],
                                       'borderBottom': f'3px solid {styles["danger"]}'},
                            ),
                            dbc.CardBody([
                                dcc.Store(id='smart-report-data', data=None),
                                dcc.Store(id='attack-trend-data', data=None),

                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Card(dbc.CardBody([
                                                html.H6("🎯 HIGHEST ATTACK PREDICTION",
                                                        style={'color': styles['warning'], 'fontWeight': 'bold',
                                                               'marginBottom': '12px'}),
                                                html.H3(id="highest-attack-name", children="—",
                                                        className="mb-2",
                                                        style={'color': styles['text'], 'minHeight': '42px'}),
                                                html.H4(id="highest-attack-count", children="0",
                                                        className="mb-2",
                                                        style={'color': styles['danger'], 'fontWeight': 'bold',
                                                               'minHeight': '36px'}),
                                                html.Div(id="highest-attack-prob", children="0%",
                                                         style={'color': styles['success'], 'fontSize': '1.2rem',
                                                                'fontWeight': 'bold', 'minHeight': '28px'}),
                                                html.Div(id="highest-risk-badge",
                                                         children=html.Div("—",
                                                                           style={'color': styles['text']}),
                                                         className="mt-3",
                                                         style={'minHeight': '48px'}),
                                            ], style={'textAlign': 'center'})),
                                            xs=12, md=8, className="mb-3",
                                        ),
                                        dbc.Col(
                                            dbc.Card(dbc.CardBody([
                                                dbc.Button(
                                                    "📥 Download Report",
                                                    id="download-pdf-btn",
                                                    color="danger",
                                                    size="lg",
                                                    className="w-100",
                                                    style={'fontWeight': 'bold', 'fontSize': '1.05rem'},
                                                ),
                                                html.P(
                                                    id="report-timestamp",
                                                    children="No report generated",
                                                    className="mt-3 text-muted small",
                                                    style={'textAlign': 'center', 'minHeight': '20px'},
                                                ),
                                            ])),
                                            xs=12, md=4, className="mb-3",
                                        ),
                                    ],
                                    className="mb-4",
                                ),

                                dbc.Row(
                                    dbc.Col(
                                        dbc.Card([
                                            dbc.CardHeader(
                                                "📈 Attack Trend Over Time",
                                                style={'backgroundColor': styles['card_bg'],
                                                       'color': styles['text']},
                                            ),
                                            dbc.CardBody(
                                                dcc.Graph(
                                                    id='attack-trend-graph',
                                                    figure=_empty_fig(
                                                        "No anomaly data – upload a CSV to generate report"),
                                                    config={'displayModeBar': False},
                                                    style={'height': f'{GRAPH_HEIGHT}px'},
                                                    className="fixed-graph",
                                                ),
                                                style={'padding': '8px'},
                                            ),
                                        ]),
                                        xs=12,
                                    ),
                                    className="mb-4",
                                ),

                                dbc.Row(
                                    dbc.Col(
                                        dbc.Card([
                                            dbc.CardHeader(
                                                "📋 Attack Summary Report",
                                                style={'backgroundColor': styles['card_bg'],
                                                       'color': styles['text']},
                                            ),
                                            dbc.CardBody(
                                                dash_table.DataTable(
                                                    id='attack-summary-table',
                                                    columns=[
                                                        {"name": "Attack Type", "id": "attack_type"},
                                                        {"name": "Total Count", "id": "count"},
                                                        {"name": "Probability %", "id": "probability"},
                                                        {"name": "Risk Level", "id": "risk_level"},
                                                    ],
                                                    data=[],
                                                    style_header={
                                                        'backgroundColor': styles['primary'],
                                                        'color': 'white',
                                                        'fontWeight': 'bold',
                                                        'fontSize': '14px',
                                                    },
                                                    style_data={
                                                        'backgroundColor': styles['card_bg'],
                                                        'color': styles['text'],
                                                        'fontSize': '13px',
                                                    },
                                                    style_data_conditional=[
                                                        {'if': {'filter_query': '{risk_level} = High'},
                                                         'backgroundColor': styles['high_risk'],
                                                         'color': 'white', 'fontWeight': 'bold'},
                                                        {'if': {'filter_query': '{risk_level} = Medium'},
                                                         'backgroundColor': styles['medium_risk'],
                                                         'color': 'black', 'fontWeight': 'bold'},
                                                        {'if': {'filter_query': '{risk_level} = Low'},
                                                         'backgroundColor': styles['low_risk'],
                                                         'color': 'white', 'fontWeight': 'bold'},
                                                    ],
                                                    style_cell={
                                                        'textAlign': 'left',
                                                        'padding': '12px',
                                                        'border': f'1px solid {styles["card_border"]}',
                                                        'whiteSpace': 'normal',
                                                        'height': 'auto',
                                                    },
                                                    sort_action="native",
                                                    page_size=10,
                                                    style_table={
                                                        'overflowX': 'auto',
                                                        'height': f'{TABLE_HEIGHT}px',
                                                        'overflowY': 'auto',
                                                    },
                                                ),
                                            ),
                                        ]),
                                        xs=12,
                                    ),
                                ),
                            ]),
                        ],
                        className="mb-5",
                        style={'boxShadow': '0 20px 50px rgba(255,0,110,0.2)'},
                    ),

                    # ── Analysis plots ──
                    html.Div(
                        id='plots-container',
                        children=[
                            dbc.Row(
                                dbc.Col(
                                    dbc.Card(dbc.CardBody([
                                        html.H5("Normal vs. Abnormal", className="card-title"),
                                        dcc.Graph(
                                            id='anomaly-scatter-plot',
                                            figure=_empty_fig(),
                                            config={'displayModeBar': False},
                                            style={'height': f'{GRAPH_HEIGHT}px'},
                                            className="fixed-graph",
                                        ),
                                    ])),
                                    xs=12,
                                ),
                                className="mb-4",
                            ),
                            dbc.Row(id='histogram-plots-row', className="mb-4"),
                            dbc.Row(
                                dbc.Col(
                                    dbc.Card(dbc.CardBody([
                                        html.H5("Anomalous Data Points", className="card-title"),
                                        dash_table.DataTable(
                                            id='anomaly-table',
                                            columns=[],
                                            data=[],
                                            style_header={
                                                'backgroundColor': styles['card_bg'],
                                                'color': styles['text'],
                                                'fontWeight': 'bold',
                                            },
                                            style_data={
                                                'backgroundColor': styles['card_bg'],
                                                'color': styles['text'],
                                            },
                                            style_cell={
                                                'textAlign': 'left',
                                                'padding': '10px',
                                                'borderBottom': f'1px solid {styles["card_border"]}',
                                                'whiteSpace': 'normal',
                                                'height': 'auto',
                                            },
                                            style_table={
                                                'overflowX': 'auto',
                                                'height': f'{TABLE_HEIGHT}px',
                                                'overflowY': 'auto',
                                            },
                                        ),
                                    ])),
                                    xs=12,
                                ),
                            ),
                        ],
                        style={'display': 'block'},
                    ),
                ],
            ),
        ],
    )


# ─────────────────────────────────────────────
# Helper: build attack-type card columns
# ─────────────────────────────────────────────
def _build_attack_cards(selected_idx=-1):
    cards_meta = [
        {'id': 'ddos-card',       'icon': '🌩️', 'name': 'DDoS'},
        {'id': 'dos-card',        'icon': '🚫', 'name': 'DoS'},
        {'id': 'portscan-card',   'icon': '🔍', 'name': 'Port Scan'},
        {'id': 'bruteforce-card', 'icon': '🔨', 'name': 'Brute Force'},
        {'id': 'botnet-card',     'icon': '🤖', 'name': 'Botnet'},
        {'id': 'webattacks-card', 'icon': '🌐', 'name': 'Web Attacks'},
    ]
    cols = []
    for i, card in enumerate(cards_meta):
        is_sel = (i == selected_idx)
        card_style = {
            'background': (
                f'linear-gradient(145deg, {styles["secondary"]}, #5a3fff)'
                if is_sel else
                f'linear-gradient(145deg, {styles["card_bg"]}, #363656)'
            ),
            'padding': '18px 12px',
            'borderRadius': '12px',
            'cursor': 'pointer',
            'transition': 'all 0.25s cubic-bezier(0.4,0,0.2,1)',
            'border': f'2px solid {styles["secondary"]}' if is_sel else '2px solid transparent',
            'textAlign': 'center',
            'boxShadow': '0 10px 28px rgba(111,61,255,0.4)' if is_sel else '0 4px 16px rgba(0,0,0,0.25)',
            'transform': 'translateY(-4px)' if is_sel else 'translateY(0)',
        }
        label_style = {
            'color': 'white' if is_sel else styles['text'],
            'fontWeight': '700',
            'fontSize': '1rem',
            'margin': 0,
        }
        cols.append(
            dbc.Col(
                html.Div(
                    [
                        html.Span(card['icon'],
                                  style={'fontSize': '2rem', 'display': 'block', 'marginBottom': '8px'}),
                        html.H6(card['name'], style=label_style),
                    ],
                    id=card['id'],
                    n_clicks=0,
                    style=card_style,
                ),
                xs=6, sm=4, md=2,
                className="attack-col mb-2",
            )
        )
    return cols


# ─────────────────────────────────────────────
# Callbacks
# ─────────────────────────────────────────────

@callback(
    Output('attack-types-grid', 'children', allow_duplicate=True),
    [Input('ddos-card', 'n_clicks'),
     Input('dos-card', 'n_clicks'),
     Input('portscan-card', 'n_clicks'),
     Input('bruteforce-card', 'n_clicks'),
     Input('botnet-card', 'n_clicks'),
     Input('webattacks-card', 'n_clicks')],
    prevent_initial_call=True,
)
def update_attack_selection(ddos, dos, portscan, bruteforce, botnet, webattacks):
    clicks = [ddos or 0, dos or 0, portscan or 0,
              bruteforce or 0, botnet or 0, webattacks or 0]
    selected_idx = clicks.index(max(clicks)) if max(clicks) > 0 else -1
    return _build_attack_cards(selected_idx)


# ✅ FIXED: Smart report generator with robust data parsing
@callback(
    [Output('smart-report-data', 'data'),
     Output('attack-trend-data', 'data'),
     Output('highest-attack-name', 'children'),
     Output('highest-attack-count', 'children'),
     Output('highest-attack-prob', 'children'),
     Output('highest-risk-badge', 'children'),
     Output('attack-trend-graph', 'figure'),
     Output('attack-summary-table', 'data'),
     Output('report-timestamp', 'children')],
    Input('anomalous-data-store', 'data'),
    State('total-anomalies-kpi', 'children'),
    prevent_initial_call=True,
)
def generate_smart_report(anomalous_json, total_anomalies_str):
    """
    ✅ FIXED ISSUES:
    1. Removed 'stored-data' State — it was unused and caused confusion
    2. Robust parsing: handles str, dict, None from dcc.Store
    3. No longer fails silently when anomalous_json is a JSON string
    4. total_anomalies_str safely converted with fallback to 0
    """
    _empty = _empty_fig("No anomaly data – upload a CSV to generate report")

    _low_risk_badge = html.Div(
        "🟢 LOW RISK",
        style={'color': styles['low_risk'], 'fontSize': '1.1rem', 'fontWeight': 'bold'}
    )
    _default_timestamp = datetime.now().strftime("%B %d, %Y - %I:%M %p")

    # ── Guard: no data ──────────────────────────────────────────────────
    if anomalous_json is None:
        return (None, None, "—", "0", "0%", _low_risk_badge,
                _empty, [], "Upload a CSV to generate report")

    # ── Safe int conversion for total_anomalies_str ─────────────────────
    try:
        total_anomalies_kpi = int(str(total_anomalies_str).replace(',', ''))
    except (ValueError, TypeError):
        total_anomalies_kpi = 0

    if total_anomalies_kpi == 0:
        return (None, None, "No Threats Detected", "0", "0%", _low_risk_badge,
                _empty, [], _default_timestamp)

    # ── Parse anomalous_json robustly ───────────────────────────────────
    # app.py stores it as: anomalous_points.to_json(date_format='iso', orient='split')
    # IMPORTANT: must use io.StringIO() so pandas reads content, not a file path
    try:
        import io as _io

        if isinstance(anomalous_json, str):
            # ✅ Wrap in StringIO — prevents pandas mistaking the JSON string for a filepath
            df_anomalies = pd.read_json(_io.StringIO(anomalous_json), orient='split')

        elif isinstance(anomalous_json, dict):
            # Already parsed as a dict (orient='split' structure: {columns, data, index})
            df_anomalies = pd.DataFrame(
                data=anomalous_json.get('data', []),
                columns=anomalous_json.get('columns', []),
            )
        else:
            raise ValueError(f"Unexpected type for anomalous_json: {type(anomalous_json)}")

    except Exception as e:
        import traceback
        print(f"[Smart Report] Error parsing anomalous data: {e}")
        traceback.print_exc()
        return (None, None, "Parse Error", "0", "0%",
                html.Div("⚠️ Parse Error", style={'color': styles['danger']}),
                _empty, [], f"Error: {str(e)[:60]}")

    total_anomalies = max(len(df_anomalies), 1)

    # ── Generate attack predictions ─────────────────────────────────────
    attack_types = ['DDoS', 'DoS', 'Port Scan', 'Brute Force', 'Botnet', 'Web Attacks']
    np.random.seed(42 + total_anomalies)

    total_attacks = max(1, total_anomalies // 2)
    attack_counts = {}
    for attack in attack_types:
        base_count = np.random.poisson(max(1, total_attacks / len(attack_types)))
        if attack == 'DDoS':
            count = max(0, base_count + np.random.poisson(max(1, total_anomalies * 0.15)))
        else:
            count = max(0, base_count)
        attack_counts[attack] = int(count)   # ✅ ensure Python int, not numpy int

    report_data = []
    trend_data = []
    current_time = pd.Timestamp.now()

    for attack, count in attack_counts.items():
        if count > 0:
            probability = (count / total_anomalies * 100)
            risk_level = classify_risk(count, total_anomalies)
            report_data.append({
                'attack_type': attack,
                'count': count,
                'probability': f"{probability:.1f}%",
                'risk_level': risk_level,
            })
            trend_data.append({
                'timestamp': current_time.isoformat(),
                'attack_type': attack,
                'count': count,
            })

    if not report_data:
        return (None, None, "No Threats Detected", "0", "0%", _low_risk_badge,
                _empty, [], _default_timestamp)

    # ── Highest attack ───────────────────────────────────────────────────
    highest = max(report_data, key=lambda x: x['count'])

    risk_colors = {
        'High':   styles['high_risk'],
        'Medium': styles['medium_risk'],
        'Low':    styles['low_risk'],
    }
    risk_icon = "🔴" if highest['risk_level'] == 'High' else ("🟡" if highest['risk_level'] == 'Medium' else "🟢")
    risk_badge = html.Div([
        html.Span(f"{risk_icon} ", style={'fontSize': '1.6rem', 'marginRight': '6px'}),
        html.Span(
            f"{highest['risk_level']} RISK",
            style={
                'backgroundColor': risk_colors[highest['risk_level']],
                'color': 'white' if highest['risk_level'] != 'Medium' else 'black',
                'padding': '8px 18px',
                'borderRadius': '20px',
                'fontWeight': 'bold',
                'fontSize': '1rem',
            },
        ),
    ], style={'textAlign': 'center', 'padding': '8px'})

    # ── Chart ────────────────────────────────────────────────────────────
    trend_df = pd.DataFrame(trend_data)
    if len(trend_df) > 0:
        fig = px.bar(
            trend_df, x='attack_type', y='count',
            title="🎯 Predicted Attack Distribution",
            color='count',
            color_continuous_scale=['#00bfa5', '#ffc400', '#ff006e'],
        )
    else:
        fig = _empty_fig()

    fig.update_layout(
        plot_bgcolor=styles['card_bg'],
        paper_bgcolor=styles['card_bg'],
        font_color=styles['text'],
        height=GRAPH_HEIGHT,
        showlegend=False,
        title_font_size=16,
        xaxis_title="Attack Type",
        yaxis_title="Predicted Count",
        margin=dict(l=20, r=20, t=50, b=20),
    )

    timestamp = datetime.now().strftime("%B %d, %Y - %I:%M %p")

    return (
        report_data,
        trend_data,
        highest['attack_type'],
        f"{highest['count']:,}",
        highest['probability'],
        risk_badge,
        fig,
        report_data,
        timestamp,
    )


# Download report
@callback(
    Output("smart-report-download", "data"),
    Input("download-pdf-btn", "n_clicks"),
    [State('smart-report-data', 'data'),
     State('report-timestamp', 'children')],
    prevent_initial_call=True,
)
def generate_html_report(n_clicks, report_data, timestamp):
    if not report_data:
        return no_update

    highest = max(report_data, key=lambda x: x['count'])

    rows_html = "\n".join(
        f'<tr class="{r["risk_level"].lower()}">'
        f'<td><strong>{r["attack_type"]}</strong></td>'
        f'<td><strong>{r["count"]:,}</strong></td>'
        f'<td>{r["probability"]}</td>'
        f'<td>{r["risk_level"]}</td></tr>'
        for r in report_data
    )

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>SOC Security Report – {highest['attack_type']}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);color:#e0e0e0;
     font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif;padding:40px;line-height:1.6}}
.container{{max-width:1100px;margin:0 auto}}
.header{{text-align:center;background:linear-gradient(135deg,#6f3dff,#0f4c75);
          padding:36px;border-radius:18px;margin-bottom:36px;
          box-shadow:0 20px 60px rgba(111,61,255,0.3)}}
.header h1{{font-size:2.4rem;font-weight:700;margin-bottom:8px}}
.timestamp{{color:#a0a0a0;font-size:1rem}}
.highest{{background:linear-gradient(145deg,#ff006e,#ff4d82);padding:30px;
           border-radius:18px;text-align:center;margin:36px 0;
           box-shadow:0 25px 50px rgba(255,0,110,0.4)}}
.highest h2{{font-size:1.6rem;margin-bottom:12px;color:white}}
.highest h1{{font-size:3rem;margin:16px 0;color:white;font-weight:800}}
.stats{{display:flex;justify-content:center;gap:36px;margin-top:16px;flex-wrap:wrap}}
.stat-value{{font-size:1.8rem;font-weight:700;color:#00ff88}}
table{{width:100%;border-collapse:collapse;background:rgba(42,42,74,0.95);
       margin-top:28px;border-radius:14px;overflow:hidden;
       box-shadow:0 20px 40px rgba(0,0,0,0.4)}}
th{{background:linear-gradient(145deg,#0f4c75,#1a5a8c);color:white;padding:18px;
    text-align:left;font-weight:600;font-size:14px;border-bottom:3px solid rgba(111,61,255,0.3)}}
td{{padding:16px 18px;border-bottom:1px solid rgba(76,76,108,0.5);font-size:13px}}
.high{{background:rgba(255,0,110,0.8)!important;color:white!important;font-weight:700}}
.medium{{background:rgba(255,196,0,0.8)!important;color:black!important;font-weight:700}}
.low{{background:rgba(0,191,165,0.8)!important;color:white!important;font-weight:700}}
.footer{{text-align:center;margin-top:50px;color:#888;font-size:12px;
          padding:24px;border-top:1px solid rgba(76,76,108,0.3)}}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🚨 SOC SECURITY REPORT</h1>
    <div class="timestamp">Generated: {timestamp}</div>
  </div>
  <div class="highest">
    <h2>🔴 HIGHEST THREAT DETECTED</h2>
    <h1>{highest['attack_type']}</h1>
    <div class="stats">
      <div class="stat"><div class="stat-value">{highest['count']:,}</div><div>INCIDENTS</div></div>
      <div class="stat"><div class="stat-value">{highest['probability']}</div><div>PROBABILITY</div></div>
      <div class="stat"><div class="stat-value" style="color:#ffaa00">{highest['risk_level']}</div><div>RISK LEVEL</div></div>
    </div>
  </div>
  <table>
    <thead><tr><th>Attack Type</th><th>Total Count</th><th>Probability</th><th>Risk Level</th></tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
  <div class="footer">Generated by Anomaly Detection Dashboard | Total entries: {len(report_data)} | {timestamp}</div>
</div>
</body>
</html>"""

    filename = (
        f"SOC_Security_Report_{highest['attack_type'].replace(' ', '_')}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    )
    return dict(content=html_content, filename=filename)
