from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

def get_settings_layout():
    return dbc.Container([

        # ⬅ Go To Dashboard Button at the top
        dbc.Row([
            dbc.Col(
                dbc.Button(
                    "⬅ Go To Dashboard",
                    id="go-dashboard-top",
                    color="primary",
                    size="lg",
                    className="mb-4"
                ),
                width=3
            )
        ]),

        html.H2("⚙ Advanced System Settings", className="mb-4"),

        # 1️⃣ Detection Algorithm Configuration
        dbc.Card([
            dbc.CardHeader("🧠 Detection Algorithm Configuration"),
            dbc.CardBody([
                html.Label("Select Detection Method"),
                dcc.Dropdown(
                    id="algorithm-selector",
                    options=[
                        {"label": "Z-Score (Statistical)", "value": "zscore"},
                        {"label": "IQR Method (Robust Statistical)", "value": "iqr"},
                        {"label": "Isolation Forest (Machine Learning)", "value": "isolation"}
                    ],
                    value="zscore",
                    clearable=False
                ),
                html.Br(),
                html.Label("Sensitivity Level"),
                dcc.Slider(
                    id="sensitivity-slider",
                    min=0.1,
                    max=1,
                    step=0.1,
                    value=0.7,
                    marks={0.1: "Low", 0.5: "Medium", 1: "High"}
                )
            ])
        ], className="mb-4"),

        # 2️⃣ Real-Time Monitoring
        dbc.Card([
            dbc.CardHeader("📡 Real-Time Monitoring Mode"),
            dbc.CardBody([
                dbc.Checklist(
                    options=[{"label": "Enable Live Monitoring Mode", "value": "live"}],
                    value=[],
                    id="live-mode-toggle",
                    switch=True
                ),
                html.Br(),
                html.Label("Auto Refresh Interval (seconds)"),
                dcc.Slider(
                    id="live-refresh",
                    min=5,
                    max=60,
                    step=5,
                    value=15,
                    marks={5: "5s", 30: "30s", 60: "60s"}
                )
            ])
        ], className="mb-4"),

        # 3️⃣ Risk Classification System
        dbc.Card([
            dbc.CardHeader("🚨 Risk Classification Settings"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("High Risk Threshold (Z-Score)"),
                        dbc.Input(id="high-risk-threshold", type="number", value=2)
                    ], md=6),
                    dbc.Col([
                        html.Label("Medium Risk Threshold (Z-Score)"),
                        dbc.Input(id="medium-risk-threshold", type="number", value=1)
                    ], md=6)
                ])
            ])
        ], className="mb-4"),

        # 4️⃣ Performance Tracking
        dbc.Card([
            dbc.CardHeader("📊 Model Performance Tracking"),
            dbc.CardBody([
                dbc.Checklist(
                    options=[
                        {"label": "Track Detection Accuracy", "value": "accuracy"},
                        {"label": "Store Detection History", "value": "history"},
                        {"label": "Enable Performance Logging", "value": "logging"}
                    ],
                    value=["accuracy"],
                    id="performance-options",
                    switch=True
                )
            ])
        ], className="mb-4"),

        # 5️⃣ Report Configuration
        dbc.Card([
            dbc.CardHeader("📤 Report & Export Configuration"),
            dbc.CardBody([
                dbc.Checklist(
                    options=[
                        {"label": "Include Graphs in Report", "value": "graphs"},
                        {"label": "Include Statistical Summary", "value": "summary"},
                        {"label": "Auto Generate Report After Upload", "value": "auto"}
                    ],
                    value=["graphs", "summary"],
                    id="report-options",
                    switch=True
                )
            ])
        ], className="mb-4"),

        # 6️⃣ Security Settings
        dbc.Card([
            dbc.CardHeader("🔐 Security & Access Control"),
            dbc.CardBody([
                dbc.Checklist(
                    options=[
                        {"label": "Enable Two-Factor Authentication (2FA)", "value": "2fa"},
                        {"label": "Session Timeout (30 Minutes)", "value": "timeout"},
                        {"label": "Enable Activity Logging", "value": "activity"}
                    ],
                    value=["timeout"],
                    id="security-options",
                    switch=True
                )
            ])
        ], className="mb-4"),

        # 7️⃣ Appearance Settings
        dbc.Card([
            dbc.CardHeader("🎨 Appearance & Theme Settings"),
            dbc.CardBody([
                html.Label("Select Dashboard Theme"),
                dcc.Dropdown(
                    id="theme-selector",
                    options=[
                        {"label": "Dark Mode", "value": "dark"},
                        {"label": "Light Mode", "value": "light"},
                        {"label": "Cyber Blue", "value": "cyber"}
                    ],
                    value="dark",
                    clearable=False
                )
            ])
        ], className="mb-4"),

        # 💾 Save Button
        dbc.Button(
            "💾 Save All Settings",
            id="save-settings",
            color="success",
            size="lg",
            className="mb-4",
            n_clicks=0
        ),

        # Toast for Save Confirmation
        dbc.Toast(
            "Settings saved successfully!",
            id="save-toast",
            header="Success",
            icon="success",
            duration=3000,
            is_open=False,
            dismissable=True,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        ),

        # Hidden div to handle redirect
        html.Div(id="dashboard-navigate", style={"display": "none"}),

        # Persistent Storage
        dcc.Store(id="settings-store", storage_type="local")

    ], fluid=True)

# --- App Layout ---
app.layout = get_settings_layout()

# --- Callbacks ---

# Save Settings Toast
@app.callback(
    Output("save-toast", "is_open"),
    Input("save-settings", "n_clicks"),
    prevent_initial_call=True
)
def show_save_toast(n_clicks):
    if n_clicks:
        return True
    return False

# Go to Dashboard Top Button
@app.callback(
    Output("dashboard-navigate", "children"),
    Input("go-dashboard-top", "n_clicks"),
    prevent_initial_call=True
)
def go_to_dashboard(n_clicks):
    if n_clicks:
        return dcc.Location(href="/dashboard", id="redirect-dashboard")
    return ""

# --- Run Server ---
if __name__ == "__main__":
    app.run_server(debug=True)