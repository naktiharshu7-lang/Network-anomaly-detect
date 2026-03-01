import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import zscore
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import base64
import io
import dash_bootstrap_components as dbc
import numpy as np
from dashboard import get_dashboard_layout, _empty_fig, GRAPH_HEIGHT
from login import get_login_layout, get_register_layout, register_login_callbacks
from settings import get_settings_layout
from insights import get_insights_layout

# ──────────────────────────────────────────────
# Initialize Dash App
# ──────────────────────────────────────────────
app = dash.Dash(
    __name__,
    title="Anomaly Detector",
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True,
)
server = app.server

styles = {
    'background':   '#1a1a2e',
    'text':         '#e0e0e0',
    'primary':      '#0f4c75',
    'secondary':    '#6f3dff',
    'success':      '#00bfa5',
    'danger':       '#ff006e',
    'info':         '#4c00b0',
    'warning':      '#ffc400',
    'card_bg':      '#2a2a4a',
    'card_border':  '#4c4c6c',
    'sidebar_bg':   '#121226',
    'sidebar_text': '#ffffff',
}

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {%favicon%}
        {%css%}
        <style>
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            @keyframes pulse  { 0%,100% { transform: scale(1); } 50% { transform: scale(1.05); } }
            .fade-in { animation: fadeIn 0.8s ease-in-out; }
            .pulse   { animation: pulse 2s infinite; }

            *, *::before, *::after { box-sizing: border-box; }
            body, html {
                margin: 0;
                padding: 0;
                overflow-x: hidden;
                background-color: #1a1a2e !important;
                color: #e0e0e0 !important;
            }

            #dashboard-wrapper {
                display: flex;
                flex-direction: row;
                min-height: 100vh;
                background-color: #1a1a2e;
            }

            #sidebar {
                width: 260px;
                min-width: 260px;
                min-height: 100vh;
                position: fixed;
                top: 0;
                left: 0;
                bottom: 0;
                z-index: 200;
                overflow-y: auto;
                background-color: #121226;
                padding: 20px;
                display: flex;
                flex-direction: column;
            }

            #main-content {
                margin-left: 260px;
                flex: 1;
                min-width: 0;
                padding: 24px;
                background-color: #1a1a2e;
            }

            #sidebar-toggle { display: none; }

            .card {
                background-color: #2a2a4a !important;
                border: 1px solid #4c4c6c !important;
                color: #e0e0e0 !important;
                border-radius: 10px;
                transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
            }
            .card:hover { transform: translateY(-4px); box-shadow: 0 10px 24px rgba(0,0,0,0.3); }
            .card-body   { background-color: #2a2a4a !important; color: #e0e0e0 !important; }
            .card-header {
                background-color: #0f4c75 !important;
                color: #e0e0e0 !important;
                border-bottom: 1px solid #4c4c6c !important;
            }
            .card-title { color: #a0a0b0 !important; }
            .card-text  { color: #e0e0e0 !important; }

            .Select-control, .Select-menu-outer, .Select-input {
                background-color: #2a2a4a !important;
                color: #e0e0e0 !important;
                border: 1px solid #4c4c6c !important;
            }
            .Select-placeholder { color: #e0e0e0 !important; opacity: 0.6; }
            .Select-value-label { color: #e0e0e0 !important; }

            .nav-link        { color: #ffffff !important; }
            .nav-link:hover  { color: #6f3dff !important; background: transparent !important; }
            .nav-link.active { color: #6f3dff !important; background: transparent !important; }

            hr { border-color: #4c4c6c !important; opacity: 0.5; }
            .row { margin-left: 0 !important; margin-right: 0 !important; }
            .dash-table-container { overflow-x: auto; }
            .fixed-graph { height: 380px; }

            @media (min-width: 768px) and (max-width: 991px) {
                #sidebar      { width: 200px; min-width: 200px; }
                #main-content { margin-left: 200px; }
                .attack-col   { flex: 0 0 33.33%; max-width: 33.33%; }
            }

            @media (max-width: 767px) {
                #dashboard-wrapper { flex-direction: row; }
                #sidebar {
                    position: fixed !important;
                    left: 0 !important;
                    right: auto !important;
                    top: 0;
                    bottom: 0;
                    width: 200px;
                    min-width: 200px;
                    height: 100vh;
                    padding: 18px 14px;
                    overflow-y: auto;
                    overflow-x: hidden;
                    background-color: #121226;
                    border-right: 3px solid #6f3dff;
                    display: flex;
                    flex-direction: column;
                    align-items: stretch;
                    gap: 16px;
                    box-shadow: 2px 0 12px rgba(0,0,0,0.4);
                }
                #sidebar-brand h2 { font-size: 1.3rem !important; margin: 0 0 8px 0 !important; }
                #sidebar-navlinks {
                    width: 100%;
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                    padding-bottom: 12px;
                    border-bottom: 1px solid #4c4c6c;
                    margin-bottom: 12px;
                }
                .nav-link { padding: 10px 8px !important; font-size: 0.95rem !important; border-radius: 6px; }
                #sidebar-inner-controls { display: flex; flex-direction: column; gap: 16px; align-items: stretch; width: 100%; }
                #sidebar-feature, #sidebar-slider, #sidebar-upload { display: block; width: 100%; }
                #main-content { margin-left: 200px !important; padding: 16px !important; width: calc(100% - 200px); overflow-x: hidden; }
                .kpi-col    { flex: 0 0 100%; max-width: 100%; margin-bottom: 12px; }
                .attack-col { flex: 0 0 50%; max-width: 50%; margin-bottom: 10px; }
                .fixed-graph { height: 320px; }
            }

            @media (max-width: 480px) {
                .attack-col  { flex: 0 0 50%; max-width: 50%; }
                .kpi-col     { flex: 0 0 100%; max-width: 100%; }
                .card-body   { padding: 10px !important; }
                #main-content { padding: 8px !important; }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

# ──────────────────────────────────────────────
# Root layout — ALL dcc.Store components live here
# ──────────────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),

    dcc.Store(id='login-state',            data={'logged_in': False}),
    dcc.Store(id='stored-data'),
    dcc.Store(id='numeric-cols'),
    # ✅ FIX: Store anomalous data as a plain dict/list (not JSON string)
    # so dashboard.py callback can reliably parse it
    dcc.Store(id='anomalous-data-store'),
    dcc.Store(id='download-report-trigger'),
    dcc.Store(id='settings-store'),
])


# ──────────────────────────────────────────────
# Settings
# ──────────────────────────────────────────────
@app.callback(
    Output("settings-store", "data"),
    Input("save-settings", "n_clicks"),
    State("theme-selector", "value"),
    State("refresh-interval", "value"),
    State("threshold-slider", "value"),
    State("alert-options", "value"),
    State("report-options", "value"),
    prevent_initial_call=True,
)
def save_settings(n, theme, refresh, threshold, alerts, reports):
    if n:
        return {
            "theme":            theme,
            "refresh_interval": refresh,
            "threshold":        threshold,
            "alerts":           alerts,
            "reports":          reports,
        }
    return dash.no_update


# ──────────────────────────────────────────────
# Page routing
# ──────────────────────────────────────────────
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('login-state', 'data'),
)
def display_page(pathname, login_state):
    if pathname == "/logout":
        return get_login_layout()
    if pathname == "/register":
        return get_register_layout()
    if not login_state or not login_state.get('logged_in'):
        return get_login_layout()
    if pathname == "/insights":
        return get_insights_layout()
    if pathname == "/settings":
        return get_settings_layout()
    return get_dashboard_layout()


# ──────────────────────────────────────────────
# File upload
# ──────────────────────────────────────────────
@app.callback(
    [
        Output('output-data-upload',   'children'),
        Output('feature-dropdown',     'options'),
        Output('feature-dropdown',     'value'),
        Output('stored-data',          'data'),
        Output('numeric-cols',         'data'),
        Output('total-rows-kpi',       'children'),
        Output('numeric-features-kpi', 'children'),
    ],
    Input('upload-data',  'contents'),
    State('upload-data',  'filename'),
)
def handle_file_upload(contents, filename):
    placeholder_msg = html.Span(
        "Please upload a CSV file to get started.",
        style={'textAlign': 'center', 'color': styles['secondary']},
    )

    if contents is None:
        return placeholder_msg, [], None, None, None, "0", "0"

    _, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        if 'csv' in filename.lower():
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        else:
            return (
                html.Span("Please upload a CSV file.", style={'color': styles['danger']}),
                [], None, None, None, "0", "0",
            )
    except Exception as e:
        return (
            html.Span(f"Error processing file: {e}", style={'color': styles['danger']}),
            [], None, None, None, "0", "0",
        )

    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
    default_feature = numeric_columns[0] if numeric_columns else None

    return (
        html.Span(
            f"✅ '{filename}' loaded — {len(df):,} rows, {len(numeric_columns)} numeric features.",
            style={'color': styles['success']},
        ),
        [{'label': col.replace('_', ' ').title(), 'value': col} for col in numeric_columns],
        default_feature,
        df.to_dict('records'),
        numeric_columns,
        f"{len(df):,}",
        str(len(numeric_columns)),
    )


# ──────────────────────────────────────────────
# Anomaly detection
# ✅ FIX: Store anomalous data as orient='records' dict
# instead of a raw JSON string — dashboard.py parses it correctly
# ──────────────────────────────────────────────
@app.callback(
    [
        Output('anomaly-scatter-plot',   'figure'),
        Output('histogram-plots-row',    'children'),
        Output('anomaly-table',          'data'),
        Output('anomaly-table',          'columns'),
        Output('total-anomalies-kpi',    'children'),
        Output('anomalous-data-store',   'data'),
    ],
    [
        Input('stored-data',              'data'),
        Input('numeric-cols',             'data'),
        Input('feature-dropdown',         'value'),
        Input('z-score-threshold-slider', 'value'),
    ],
)
def update_analysis(data, numeric_cols, selected_feature, z_score_threshold):
    placeholder = _empty_fig()

    if data is None or selected_feature is None or numeric_cols is None:
        return placeholder, [], [], [], "0", None

    df = pd.DataFrame(data)

    if selected_feature not in df.columns or df[selected_feature].dtype not in ['int64', 'float64']:
        return placeholder, [], [], [], "0", None

    df['z_score'] = zscore(df[selected_feature].dropna())
    df['anomaly_label'] = df['z_score'].apply(
        lambda x: 'Abnormal' if abs(x) > z_score_threshold else 'Normal'
    )

    scatter_x = selected_feature
    other_features = [col for col in numeric_cols if col != selected_feature]
    scatter_y = other_features[0] if other_features else selected_feature
    if scatter_x == scatter_y:
        df['index'] = df.index
        scatter_y = 'index'

    scatter_fig = px.scatter(
        df,
        x=scatter_x,
        y=scatter_y,
        color='anomaly_label',
        title=(
            f'Anomaly Detection: {scatter_x.replace("_", " ").title()}'
            f' vs {scatter_y.replace("_", " ").title()}'
        ),
        color_discrete_map={'Normal': '#90ee90', 'Abnormal': styles['danger']},
        hover_data=[scatter_x, scatter_y, 'z_score'],
    )
    scatter_fig.update_layout(
        plot_bgcolor=styles['card_bg'],
        paper_bgcolor=styles['card_bg'],
        font={'color': styles['text']},
        height=GRAPH_HEIGHT,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    histogram_plots = []
    for col in numeric_cols:
        hist_fig = px.histogram(
            df,
            x=col,
            color='anomaly_label',
            title=f'Distribution of {col.replace("_", " ").title()}',
            color_discrete_map={'Normal': '#90ee90', 'Abnormal': styles['danger']},
        )
        hist_fig.update_layout(
            plot_bgcolor=styles['card_bg'],
            paper_bgcolor=styles['card_bg'],
            font={'color': styles['text']},
            height=GRAPH_HEIGHT,
            margin=dict(l=20, r=20, t=50, b=20),
        )
        histogram_plots.append(
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H5(
                        f'{col.replace("_", " ").title()} Distribution',
                        className="card-title",
                    ),
                    dcc.Graph(
                        figure=hist_fig,
                        config={'displayModeBar': False},
                        style={'height': f'{GRAPH_HEIGHT}px'},
                    ),
                ])),
                xs=12, md=6,
                className="mb-3",
            )
        )

    anomalous_points = df[df['anomaly_label'] == 'Abnormal'].copy()
    anomalous_points['index'] = anomalous_points.index
    anomalous_points['z_score'] = anomalous_points['z_score'].round(2)

    table_cols = [
        {'name': i.replace('_', ' ').title(), 'id': i}
        for i in ['index'] + numeric_cols + ['z_score']
    ]

    # ✅ KEY FIX: Store as JSON string using orient='split'
    # This matches what generate_smart_report in dashboard.py expects
    anomalous_data_json = anomalous_points.to_json(date_format='iso', orient='split')

    return (
        scatter_fig,
        histogram_plots,
        anomalous_points.to_dict('records'),
        table_cols,
        str(len(anomalous_points)),
        anomalous_data_json,   # ✅ stored as JSON string, orient='split'
    )


# ──────────────────────────────────────────────
# Legacy CSV download (sidebar "Reports" link)
# ──────────────────────────────────────────────
@app.callback(
    Output("download-report-trigger", "data"),
    Input("download-report-link", "n_clicks"),
    State('anomalous-data-store', 'data'),
    prevent_initial_call=True,
)
def generate_report(n_clicks, anomalous_data_json):
    if n_clicks and anomalous_data_json:
        df = pd.read_json(anomalous_data_json, orient='split')
        return dcc.send_data_frame(df.to_csv, "anomaly_report.csv")
    return None


# ──────────────────────────────────────────────
# Login / registration callbacks
# ──────────────────────────────────────────────
register_login_callbacks(app)

# ──────────────────────────────────────────────
# Run
# ──────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=False)
