from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import re  # ← added for validation

# ======================
# TEMP USER DATABASE
# ======================
USERS_DB = {
    'admin': {"password": "admin123", "email": "admin@gmail.com"},
    'user': {"password": "user123", "email": "user@gmail.com"}
}

styles = {
    "bg": "#0b0f1a",
    "card": "rgba(18,25,44,0.75)",
    "primary": "#00e5ff",
    "secondary": "#6c63ff",
    "danger": "#ff4d6d",
    "success": "#00ffcc",
    "text": "#e6e6e6"
}

# ======================
# SHARED BACKGROUND
# ======================
CYBER_BG = {
    "minHeight": "100vh",
    "background": """
        radial-gradient(circle at 20% 20%, rgba(0,229,255,.15), transparent 40%),
        radial-gradient(circle at 80% 30%, rgba(108,99,255,.15), transparent 40%),
        linear-gradient(135deg, #05070f 0%, #0b0f1a 40%, #000 100%)
    """,
    "display": "flex",
    "justifyContent": "center",
    "alignItems": "center"
}

def glass_card(children):
    return dbc.Card(
        children,
        style={
            "width": "420px",
            "padding": "2.5rem",
            "background": styles["card"],
            "borderRadius": "18px",
            "backdropFilter": "blur(14px)",
            "boxShadow": "0 0 35px rgba(0,229,255,0.35)",
            "border": "1px solid rgba(0,229,255,0.25)",
        }
    )

# ======================
# LOGIN PAGE
# ======================
def get_login_layout():
    return html.Div(
        style=CYBER_BG,
        children=[
            glass_card([
                html.H3("Secure Login", style={"color": styles["primary"], "textAlign": "center"}),
                html.P("Network Anomaly Detection System",
                       style={"textAlign": "center", "color": styles["text"], "opacity": .8}),

                dbc.Input(id="login-username", placeholder="Username", className="mb-3",
                          style={"backgroundColor": styles["bg"], "color": "white"}),

                dbc.Input(id="login-password", placeholder="Password", type="password", className="mb-3",
                          style={"backgroundColor": styles["bg"], "color": "white"}),

                dbc.Button("LOGIN", id="login-btn", className="w-100 mb-2",
                           style={"background": "linear-gradient(90deg,#00e5ff,#6c63ff)", "border": "none"}),

                html.Div(id="login-message", style={"textAlign": "center", "color": styles["danger"], "minHeight": "22px"}),

                dcc.Link("New User? Register", href="/register",
                         style={"display": "block", "textAlign": "center", "marginTop": "12px", "color": styles["secondary"]})
            ])
        ]
    )

# ======================
# REGISTER PAGE
# ======================
def get_register_layout():
    return html.Div(
        style=CYBER_BG,
        children=[
            glass_card([
                html.H3("Create Account", style={"color": styles["primary"], "textAlign": "center"}),

                dbc.Input(id="reg-username", placeholder="Username", className="mb-2",
                          style={"backgroundColor": styles["bg"], "color": "white"}),

                dbc.Input(id="reg-email", placeholder="Email", type="email", className="mb-2",
                          style={"backgroundColor": styles["bg"], "color": "white"}),

                dbc.Input(id="reg-password", placeholder="Password", type="password", className="mb-3",
                          style={"backgroundColor": styles["bg"], "color": "white"}),

                dbc.Button("REGISTER", id="register-btn", className="w-100",
                           style={"background": "linear-gradient(90deg,#00e5ff,#6c63ff)", "border": "none"}),

                html.Div(id="register-message",
                         style={"textAlign": "center", "marginTop": "10px", "color": styles["success"], "minHeight": "22px"}),

                dcc.Link("⬅ Back to Login", href="/login",
                         style={"display": "block", "textAlign": "center", "marginTop": "12px", "color": styles["secondary"]})
            ])
        ]
    )

# ======================
# VALIDATION HELPERS        ← only new code lives here
# ======================
def validate_username(username):
    """3–20 chars, only letters, numbers, underscore."""
    if not username:
        return "❌ Username is required."
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return "❌ Username must be 3–20 chars (letters, numbers, _ only)."
    return None  # valid

def validate_email(email):
    """Basic RFC-style email check."""
    if not email:
        return "❌ Email is required."
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email):
        return "❌ Enter a valid email address."
    return None  # valid

def validate_password(password):
    """Minimum 6 characters."""
    if not password:
        return "❌ Password is required."
    if len(password) < 6:
        return "❌ Password must be at least 6 characters."
    return None  # valid

# ======================
# CALLBACKS
# ======================
def register_login_callbacks(app):

    @app.callback(
        Output("register-message", "children"),
        Input("register-btn", "n_clicks"),
        State("reg-username", "value"),
        State("reg-email", "value"),
        State("reg-password", "value"),
        prevent_initial_call=True
    )
    def register_user(n, username, email, password):

        # ── Validation (new) ──────────────────────────────────────────────────
        err = validate_username(username)
        if err:
            return err

        err = validate_email(email)
        if err:
            return err

        err = validate_password(password)
        if err:
            return err

        # ── USERS_DB logic unchanged ──────────────────────────────────────────
        if username in USERS_DB:
            return "❌ Username already exists."

        USERS_DB[username] = {"password": password, "email": email}
        return "✅ Registered! Go back and login."

    @app.callback(
        Output("login-state", "data"),
        Output("login-message", "children"),
        Input("login-btn", "n_clicks"),
        State("login-username", "value"),
        State("login-password", "value"),
        prevent_initial_call=True
    )
    def login_user(n, username, password):

        # ── Validation (new) ──────────────────────────────────────────────────
        if not username or not username.strip():
            return {"logged_in": False}, "❌ Username is required."

        if not password:
            return {"logged_in": False}, "❌ Password is required."

        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            return {"logged_in": False}, "❌ Invalid username format."

        if len(password) < 6:
            return {"logged_in": False}, "❌ Password must be at least 6 characters."

        # ── USERS_DB logic unchanged ──────────────────────────────────────────
        if username in USERS_DB and USERS_DB[username]["password"] == password:
            return {"logged_in": True}, "✅ Login successful!"

        return {"logged_in": False}, "❌ Invalid credentials."