import streamlit as st
import pandas as pd
import joblib
import hashlib
import secrets
import plotly.graph_objects as go
from fpdf import FPDF
from db import get_connection

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Heart Disease Prediction",
    page_icon="❤️",
    layout="wide"
)

# ── DARK THEME CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* === BASE — kill ALL gaps === */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stMain"],
.main,
section[data-testid="stMain"],
section[data-testid="stMain"] > div,
[data-testid="stBlock"],
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlock"] > div,
.st-emotion-cache-1wivap2,
.st-emotion-cache-10oheav,
.st-emotion-cache-1r4qj8v,
.st-emotion-cache-12fm25u {
    background-color: #0a0a0a !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0 !important;
    margin: 0 !important;
    gap: 0 !important;
}
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"],
#MainMenu, footer, header { display: none !important; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
section[data-testid="stMain"] > div:first-child { padding: 0 !important; margin: 0 !important; }
.stApp > header { display: none !important; }

/* kill every possible streamlit wrapper */
.stMarkdown, [data-testid="stMarkdownContainer"],
.element-container, .row-widget,
.stVerticalBlockBorderWrapper,
[data-testid="column"],
[data-testid="stVerticalBlock"] > [data-testid="element-container"] {
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
}
[data-testid="stAppViewContainer"] > section { background: #0a0a0a !important; }

/* ===== AGGRESSIVE GAP ELIMINATION ===== */
[data-testid="stMain"] [data-testid="stVerticalBlock"] > [data-testid="element-container"] {
    margin: 0 !important; padding: 0 !important; border: none !important;
}
[data-testid="stMain"] > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
section[data-testid="stMain"] > div:first-child {
    margin-top: 0 !important; padding-top: 0 !important;
}
/* Kill gap between navbar (first child) and content (second child) */
[data-testid="stVerticalBlock"] > [data-testid="element-container"]:nth-child(2) {
    margin-top: 0 !important; padding-top: 0 !important;
}
[data-testid="stVerticalBlock"] > [data-testid="element-container"]:first-child {
    margin-top: 0 !important; padding-top: 0 !important;
}
.element-container { margin: 0 !important; padding: 0 !important; }

/* === NAVBAR === */
.navbar {
    background: #0f0f0f;
    border-bottom: 1px solid #1e1e1e;
    padding: 0 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 66px;
    width: 100%;
    position: sticky;
    top: 0;
    z-index: 1000;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-icon {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #7f0d1e 0%, #c9184a 100%);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(201,24,74,.35);
}
.brand-name { font-size: 15px; font-weight: 700; color: #f8fafc; line-height: 1.2; letter-spacing: -.02em; }
.brand-sub  { font-size: 11px; color: #475569; }
.nav-links  { display: flex; gap: 4px; align-items: center; }
.nav-link {
    display: inline-block; padding: 7px 16px;
    border-radius: 8px; font-size: 13px; font-weight: 500;
    color: #64748b; text-decoration: none !important;
    transition: background .15s, color .15s; border: 1px solid transparent;
}
.nav-link:hover { background: #181818; color: #e2e8f0; text-decoration: none !important; }
.nav-link.active { background: #c9184a; color: #fff; border-color: #c9184a; }
.nav-link.logout { color: #fb7185; }
.nav-link.logout:hover { background: #2a060e; border-color: #3f0a18; color: #f43f5e; }
.nav-username { font-size: 12px; color: #475569; padding: 0 8px; }

/* === PAGE WRAPPER === */
.pw { max-width: 1080px; margin: 0 auto; padding: 0 32px 80px; }

/* === HERO === */
.hero { margin-bottom: 24px; }
.hero h2 { font-size: 26px; font-weight: 700; color: #f8fafc; margin: 0 0 8px; letter-spacing: -.025em; }
.hero p   { font-size: 14px; color: #64748b; margin: 0; line-height: 1.6; }

/* === CARDS === */
.card {
    background: #111111;
    border: 1px solid #1e1e1e;
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 20px;
}
.ch {
    display: flex; align-items: center; gap: 8px;
    font-size: 11px; font-weight: 700; color: #475569;
    margin-bottom: 22px; padding-bottom: 16px;
    border-bottom: 1px solid #1a1a1a;
    text-transform: uppercase; letter-spacing: .08em;
}
.ch .reddot { width: 7px; height: 7px; border-radius: 50%; background: #c9184a; flex-shrink: 0; }

/* === AUTH CARD === */
.auth-card {
    max-width: 420px; margin: 40px auto 0;
    background: #111111; border: 1px solid #1e1e1e;
    border-radius: 16px; padding: 40px 36px;
}
.auth-card h2 {
    font-size: 22px; font-weight: 700; color: #f8fafc;
    margin: 0 0 6px; text-align: center;
}
.auth-card p {
    font-size: 13px; color: #64748b; text-align: center;
    margin: 0 0 28px; line-height: 1.6;
}
.auth-divider {
    text-align: center; font-size: 13px; color: #334155; margin: 20px 0;
}
.auth-divider a { color: #c9184a; text-decoration: none !important; font-weight: 600; }
.auth-divider a:hover { color: #fb7185; }

/* === USER BAR === */
.user-bar {
    display: flex; align-items: center; gap: 12px;
    background: #0f0f0f; border: 1px solid #1e1e1e;
    border-radius: 12px; padding: 12px 20px; margin-bottom: 20px;
}
.user-bar-label { font-size: 13px; font-weight: 600; color: #94a3b8; white-space: nowrap; }

/* === STAT ROW === */
.stat-row { display: flex; gap: 14px; margin-bottom: 24px; flex-wrap: wrap; }
.stat-card {
    flex: 1; min-width: 140px;
    background: #111111; border: 1px solid #1e1e1e;
    border-radius: 14px; padding: 22px 16px; text-align: center;
}
.sn { font-size: 36px; font-weight: 700; line-height: 1; margin-bottom: 6px; }
.sl { font-size: 12px; color: #475569; font-weight: 500; letter-spacing: .01em; }

/* === FEATURE GRID === */
.fg { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.ft { background: #161616; border: 1px solid #1e1e1e; border-radius: 12px; padding: 20px; }
.ft-icon { font-size: 28px; margin-bottom: 12px; display: block; }
.ft h4 { font-size: 14px; font-weight: 600; color: #e2e8f0; margin: 0 0 8px; }
.ft p  { font-size: 13px; color: #64748b; line-height: 1.65; margin: 0; }

/* === RISK TILES === */
.rtile {
    padding: 18px; background: #161616;
    border-radius: 12px; border: 1px solid #1e1e1e;
}
.rtile-title { font-size: 13px; font-weight: 600; color: #e2e8f0; margin-bottom: 6px; }
.rtile-desc  { font-size: 12px; color: #64748b; line-height: 1.65; }

/* === RESULT BOXES === */
.result-high {
    background: #150408; border: 1px solid #3f0a18;
    border-radius: 16px; padding: 26px; margin-top: 20px;
}
.result-low {
    background: #050f08; border: 1px solid #0a3018;
    border-radius: 16px; padding: 26px; margin-top: 20px;
}
.result-title { font-size: 20px; font-weight: 700; margin-bottom: 12px; }
.result-high .result-title { color: #fb7185; }
.result-low  .result-title { color: #4ade80; }
.result-sub  { font-size: 13px; line-height: 1.7; }
.result-high .result-sub { color: #e07b8a; }
.result-low  .result-sub { color: #6fcf97; }

/* === GAUGE === */
.gauge-wrap { display: flex; align-items: center; gap: 16px; margin: 16px 0 14px; }
.gauge-track { flex:1; height:10px; background:#1e1e1e; border-radius:99px; overflow:hidden; }
.gauge-fill  { height:100%; border-radius:99px; transition: width .8s cubic-bezier(.4,0,.2,1); }
.gauge-num   { font-size: 32px; font-weight: 700; min-width: 84px; text-align: right; }
.result-high .gauge-num { color: #fb7185; }
.result-low  .gauge-num { color: #4ade80; }

/* === SUGGESTIONS BOX === */
.sugg-box { margin-top:20px; border-radius:14px; padding:22px; border:1px solid; }
.sugg-box.high { background:#120306; border-color:#3f0a18; }
.sugg-box.low  { background:#040d07; border-color:#0a3018; }
.sugg-title {
    font-size:12px; font-weight:700; text-transform:uppercase;
    letter-spacing:.07em; margin-bottom:14px; display:flex; align-items:center; gap:8px;
}
.sugg-box.high .sugg-title { color:#f43f5e; }
.sugg-box.low  .sugg-title { color:#22c55e; }
.sugg-item {
    display:flex; align-items:flex-start; gap:10px;
    padding:10px 0; border-bottom:1px solid #1a1a1a;
    font-size:13px; line-height:1.6;
}
.sugg-item:last-child { border-bottom:none; padding-bottom:0; }
.sugg-box.high .sugg-item, .sugg-box.low .sugg-item { color:#cbd5e1; }
.sugg-icon { flex-shrink:0; font-size:15px; margin-top:1px; }

/* === RISK FACTOR BARS === */
.rf-section-label {
    font-size:11px; font-weight:700; color:#475569;
    text-transform:uppercase; letter-spacing:.07em; margin:24px 0 14px;
}
.rf-row { display:flex; align-items:center; gap:12px; margin-bottom:12px; }
.rf-label { font-size:12px; color:#94a3b8; width:140px; flex-shrink:0; font-weight:500; }
.rf-track { flex:1; height:6px; background:#1e1e1e; border-radius:99px; overflow:hidden; }
.rf-fill  { height:100%; border-radius:99px; }
.rf-val   { font-size:12px; color:#64748b; min-width:36px; text-align:right; font-weight:600; }

/* === HISTORY TABLE === */
.htw { overflow-x:auto; }
table.ht { width:100%; border-collapse:collapse; font-size:13px; }
.ht th {
    text-align:left; padding:12px 14px;
    border-bottom:1px solid #1e1e1e;
    font-size:11px; font-weight:700; color:#475569;
    text-transform:uppercase; letter-spacing:.06em; white-space:nowrap; background:#0f0f0f;
}
.ht td {
    padding:12px 14px; border-bottom:1px solid #161616;
    color:#cbd5e1; white-space:nowrap; font-size:13px;
}
.ht tr:hover td { background:#141414; }
.bh { display:inline-block; background:#2a060e; color:#fb7185; padding:4px 12px; border-radius:99px; font-size:11px; font-weight:700; border:1px solid #3f0a18; }
.bl { display:inline-block; background:#04150a; color:#4ade80; padding:4px 12px; border-radius:99px; font-size:11px; font-weight:700; border:1px solid #0a3018; }

/* === EMPTY STATE === */
.es { text-align:center; padding:60px 24px; }
.es-i { font-size:48px; margin-bottom:16px; opacity:.4; }
.es p { font-size:14px; color:#475569; line-height:1.7; }

/* === FOOTER === */
.footer {
    text-align:center; font-size:12px; color:#334155;
    padding:28px; margin-top:12px;
    border-top: 1px solid #161616; letter-spacing:.01em;
}

/* === STREAMLIT WIDGET DARK OVERRIDES === */
[data-testid="stSlider"] label,
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label {
    font-size:13px !important; font-weight:500 !important; color:#94a3b8 !important;
}
[data-baseweb="slider"] [role="slider"] {
    background:#c9184a !important; border-color:#c9184a !important;
    box-shadow:0 0 0 4px rgba(201,24,74,.2) !important;
}
[data-baseweb="select"] > div,
[data-baseweb="input"],
[data-baseweb="base-input"] {
    background:#161616 !important; border-color:#262626 !important; color:#e2e8f0 !important;
}
[data-baseweb="select"] > div:hover,
[data-baseweb="input"]:hover { border-color:#333 !important; }
[data-baseweb="select"] svg { fill:#64748b !important; }
[data-baseweb="menu"] {
    background:#161616 !important; border:1px solid #262626 !important; border-radius:10px !important;
}
[data-baseweb="menu"] li { color:#e2e8f0 !important; }
[data-baseweb="menu"] li:hover { background:#1e1e1e !important; }
[data-testid="stButton"] > button {
    background:linear-gradient(135deg,#a4133c 0%,#c9184a 100%) !important;
    color:#fff !important; border:none !important;
    border-radius:10px !important; font-weight:600 !important;
    font-size:15px !important; padding:14px 32px !important;
    width:100% !important; letter-spacing:-.01em;
    box-shadow:0 2px 12px rgba(201,24,74,.3) !important;
    transition:opacity .15s !important;
}
[data-testid="stButton"] > button:hover { opacity:.88 !important; }
[data-testid="stDownloadButton"] > button {
    background:#111111 !important; color:#c9184a !important;
    border:1.5px solid #c9184a !important; border-radius:10px !important;
    font-weight:600 !important; font-size:14px !important;
    width:100% !important; margin-top:18px !important;
}
[data-testid="stSpinner"] p { color:#94a3b8 !important; }
.js-plotly-plot, .plotly { background:transparent !important; }
[data-testid="stHorizontalBlock"] { gap:18px !important; }
[data-testid="stAlert"] {
    background:#161616 !important; border-color:#262626 !important; color:#94a3b8 !important;
}
[data-testid="stNumberInput"] button {
    background:#1e1e1e !important; border-color:#262626 !important; color:#94a3b8 !important;
}
[data-testid="stNumberInput"] { padding-bottom:0 !important; }
[data-testid="stNumberInput"] > div { height:38px !important; }
[data-testid="stNumberInput"] input { height:38px !important; font-size:14px !important; }
[data-testid="stSelectbox"] > div { min-height:38px !important; }
[data-testid="stSelectbox"] > div > div { min-height:38px !important; }
[data-testid="stSlider"] > div { padding-bottom:4px !important; }
[data-testid="stTickBar"] { display:none !important; }
[data-testid="stTextInput"] label { font-size:13px !important; color:#94a3b8 !important; }
[data-testid="stTextInput"] input {
    background:#161616 !important; border-color:#262626 !important; color:#e2e8f0 !important;
    border-radius:8px !important; padding:10px 14px !important; font-size:14px !important;
}
[data-testid="stTextInput"] input:focus { border-color:#c9184a !important; }
[data-testid="stPasswordInput"] label { font-size:13px !important; color:#94a3b8 !important; }
[data-testid="stPasswordInput"] input {
    background:#161616 !important; border-color:#262626 !important; color:#e2e8f0 !important;
    border-radius:8px !important; padding:10px 14px !important; font-size:14px !important;
}
[data-testid="stPasswordInput"] input:focus { border-color:#c9184a !important; }

/* Success / error messages in auth */
.st-emotion-cache-1wmy9hl, .stAlert {
    font-size:13px !important;
}
</style>

""", unsafe_allow_html=True)


# ── LOAD MODEL ───────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    m  = joblib.load("logistic_heart.pkl")
    sc = joblib.load("scaler.pkl")
    ec = joblib.load("columns.pkl")
    return m, sc, ec

model, scaler, expected_columns = load_model()


# ── AUTH HELPERS ─────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${h}"

def check_password(password: str, stored: str) -> bool:
    salt, h = stored.split("$", 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == h

def init_users_table():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass

def signup_user(username: str, email: str, password: str) -> tuple[bool, str]:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cur.fetchone():
            cur.close(); conn.close()
            return False, "Username or email already exists."
        pw_hash = hash_password(password)
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, pw_hash)
        )
        conn.commit()
        cur.close(); conn.close()
        return True, "Account created! You can now log in."
    except Exception as e:
        return False, f"Error: {e}"

def ensure_predictions_schema():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                patient_name VARCHAR(100),
                age INTEGER, sex VARCHAR(10), chest_pain VARCHAR(10),
                resting_bp INTEGER, cholesterol INTEGER, fasting_bs INTEGER,
                resting_ecg VARCHAR(10), max_hr INTEGER,
                exercise_angina VARCHAR(10), oldpeak FLOAT, st_slope VARCHAR(10),
                prediction VARCHAR(20), probability FLOAT,
                prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        for col, dtype in {
            "patient_name": "VARCHAR(100)", "age": "INTEGER", "sex": "VARCHAR(10)",
            "chest_pain": "VARCHAR(10)", "resting_bp": "INTEGER",
            "cholesterol": "INTEGER", "fasting_bs": "INTEGER",
            "resting_ecg": "VARCHAR(10)", "max_hr": "INTEGER",
            "exercise_angina": "VARCHAR(10)", "oldpeak": "FLOAT",
            "st_slope": "VARCHAR(10)", "prediction": "VARCHAR(20)", "probability": "FLOAT",
        }.items():
            try:
                cur.execute(f"ALTER TABLE predictions ADD COLUMN {col} {dtype}")
                conn.commit()
            except Exception:
                conn.rollback()
        cur.close(); conn.close()
    except Exception:
        pass

def login_user(username: str, password: str) -> tuple[bool, str]:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT password_hash FROM users WHERE username = %s",
            (username,)
        )
        row = cur.fetchone()
        cur.close(); conn.close()
        if not row:
            return False, "Invalid username or password."
        if not check_password(password, row[0]):
            return False, "Invalid username or password."
        return True, "Login successful."
    except Exception as e:
        return False, f"Error: {e}"


# ── SESSION STATE ────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# Restore session from query params (survives full page reloads from <a href>)
if not st.session_state.logged_in and st.query_params.get("u"):
    st.session_state.logged_in = True
    st.session_state.user = st.query_params["u"]

init_users_table()
ensure_predictions_schema()


# ── PAGE ROUTING ─────────────────────────────────────────────────────────────
ALL_PAGES = ["About", "Login", "Signup", "Prediction", "Dashboard", "History", "Logout"]
PUBLIC_PAGES = ["About", "Login", "Signup"]
AUTH_PAGES = ["Prediction", "Dashboard", "History"]

qp   = st.query_params.get("page", "About")
page = qp if qp in ALL_PAGES else "About"

# Redirect to Login if trying to access auth pages while logged out
if page in AUTH_PAGES and not st.session_state.logged_in:
    st.query_params.page = "Login"
    page = "Login"


# ── NAVBAR ───────────────────────────────────────────────────────────────────
if st.session_state.logged_in:
    shown_pages = ["About", "Prediction", "Dashboard", "History"]
else:
    shown_pages = ["About", "Login", "Signup"]

ICONS = {
    "About": "ℹ️", "Login": "🔑", "Signup": "📝",
    "Prediction": "🩺", "Dashboard": "📊", "History": "📜",
}

links = []
for p in shown_pages:
    cls = "nav-link active" if p == page else "nav-link"
    u = st.session_state.user or ""
    auth_suffix = f"&u={u}" if u else ""
    links.append(f'<a class="{cls}" href="?page={p}{auth_suffix}" target="_self">{ICONS[p]} {p}</a>')

if st.session_state.logged_in:
    links.append(f'<span class="nav-username">{st.session_state.user}</span>')
    links.append(f'<a class="nav-link logout" href="?page=Logout" target="_self">🚪 Logout</a>')

tabs_html = "".join(links)

st.markdown(f"""
<div class="navbar">
  <div class="brand">
    <div class="brand-icon">❤️</div>
    <div>
      <div class="brand-name">CardioScan AI</div>
      <div class="brand-sub">Heart Disease Prediction System</div>
    </div>
  </div>
  <div class="nav-links">{tabs_html}</div>
</div>
""", unsafe_allow_html=True)


# ── LOGOUT HANDLER ───────────────────────────────────────────────────────────
if page == "Logout":
    st.session_state.logged_in = False
    st.session_state.user = None
    st.query_params.page = "About"
    st.rerun()


# ════════════════════════════════════════════════════════════
#  ABOUT
# ════════════════════════════════════════════════════════════
if page == "About":
    st.markdown('<div class="pw">', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero">
      <h2>About this tool</h2>
      <p>An AI-powered clinical decision-support tool for estimating cardiovascular risk using 11 standard clinical measurements.</p>
    </div>

    <div class="card">
      <div class="ch"><span class="reddot"></span>Overview</div>
      <p style="font-size:14px;color:#94a3b8;line-height:1.85;margin:0">
        This application uses a <strong style="color:#e2e8f0">logistic regression model</strong>
        trained on the UCI Heart Disease dataset to estimate a patient's probability of heart disease.
        After each prediction, the tool provides <strong style="color:#e2e8f0">personalised, probability-based suggestions</strong>
        to help clinicians and patients understand the results and take appropriate action.
        It is intended for <strong style="color:#e2e8f0">educational and research purposes only</strong>
        and should never replace a qualified clinician's judgement.
      </p>
    </div>

    <div class="card">
      <div class="ch"><span class="reddot"></span>Key features</div>
      <div class="fg">
        <div class="ft"><span class="ft-icon">🧠</span><h4>Machine learning model</h4>
          <p>Logistic regression with StandardScaler normalisation, trained on 918 clinical records from the UCI Heart Disease dataset with strong predictive accuracy.</p></div>
        <div class="ft"><span class="ft-icon">📋</span><h4>11 clinical features</h4>
          <p>Age, sex, chest pain type, resting BP, cholesterol, fasting blood sugar, ECG results, max HR, exercise angina, oldpeak, and ST slope.</p></div>
        <div class="ft"><span class="ft-icon">💡</span><h4>Smart suggestions</h4>
          <p>Context-aware, probability-based health recommendations tailored to each patient's specific clinical values — not just a generic result.</p></div>
        <div class="ft"><span class="ft-icon">📄</span><h4>PDF report export</h4>
          <p>Download a detailed patient report after each prediction, including the probability score, risk factors, and all clinical inputs.</p></div>
      </div>
    </div>

    <div class="card">
      <div class="ch"><span class="reddot"></span>Top risk factors assessed</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
        <div class="rtile"><div class="rtile-title">Chest pain type (ASY)</div>
          <div class="rtile-desc">Asymptomatic presentation is the strongest single predictor — silent symptoms are the most dangerous.</div></div>
        <div class="rtile"><div class="rtile-title">ST slope (Flat / Down)</div>
          <div class="rtile-desc">A flat or downward-sloping ST segment during exercise is a strong marker of myocardial ischaemia.</div></div>
        <div class="rtile"><div class="rtile-title">Oldpeak (ST depression)</div>
          <div class="rtile-desc">Values above 2 mm indicate reduced coronary blood flow and significantly elevate risk.</div></div>
        <div class="rtile"><div class="rtile-title">Exercise-induced angina</div>
          <div class="rtile-desc">Chest pain triggered by physical activity is a classic symptom of obstructive coronary artery disease.</div></div>
        <div class="rtile"><div class="rtile-title">Age & sex</div>
          <div class="rtile-desc">Risk increases significantly after 55. Males have a statistically higher baseline cardiovascular risk.</div></div>
        <div class="rtile"><div class="rtile-title">Blood pressure & cholesterol</div>
          <div class="rtile-desc">Elevated resting BP (≥140 mmHg) and cholesterol (≥240 mg/dL) are major modifiable risk factors.</div></div>
      </div>
    </div>

    <div class="card">
      <div class="ch"><span class="reddot"></span>How to use</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div style="display:flex;align-items:flex-start;gap:14px;padding:14px;background:#161616;border-radius:12px;border:1px solid #1e1e1e">
          <div style="width:28px;height:28px;background:#1a0608;border:1px solid #3f0a18;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:#fb7185;flex-shrink:0">1</div>
          <div><div style="font-size:13px;font-weight:600;color:#e2e8f0;margin-bottom:4px">Create an account</div><div style="font-size:13px;color:#64748b;line-height:1.6">Sign up with a username, email, and password on the Signup page.</div></div>
        </div>
        <div style="display:flex;align-items:flex-start;gap:14px;padding:14px;background:#161616;border-radius:12px;border:1px solid #1e1e1e">
          <div style="width:28px;height:28px;background:#1a0608;border:1px solid #3f0a18;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:#fb7185;flex-shrink:0">2</div>
          <div><div style="font-size:13px;font-weight:600;color:#e2e8f0;margin-bottom:4px">Log in</div><div style="font-size:13px;color:#64748b;line-height:1.6">Log in with your credentials — your predictions will be saved to your account automatically.</div></div>
        </div>
        <div style="display:flex;align-items:flex-start;gap:14px;padding:14px;background:#161616;border-radius:12px;border:1px solid #1e1e1e">
          <div style="width:28px;height:28px;background:#1a0608;border:1px solid #3f0a18;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:#fb7185;flex-shrink:0">3</div>
          <div><div style="font-size:13px;font-weight:600;color:#e2e8f0;margin-bottom:4px">Predict & track</div><div style="font-size:13px;color:#64748b;line-height:1.6">Run heart disease predictions and view your personal history on the History page.</div></div>
        </div>
      </div>
    </div>

    <div class="footer">⚕️ This tool is for educational purposes only and should not be considered a medical diagnosis.</div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  LOGIN
# ════════════════════════════════════════════════════════════
elif page == "Login":
    st.markdown('<div class="pw">', unsafe_allow_html=True)
    st.markdown("""
    <div class="auth-card">
      <h2>🔑 Welcome back</h2>
      <p>Log in to access predictions, your dashboard, and prediction history.</p>
      <div style="margin-bottom:24px">
    """, unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="Enter your username", key="login_user")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        login_btn = st.button("Log in", use_container_width=True)

    if login_btn:
        if not username or not password:
            st.error("Please fill in all fields.")
        else:
            ok, msg = login_user(username, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.query_params.page = "Prediction"
                st.query_params.u = username
                st.rerun()
            else:
                st.error(msg)

    st.markdown(f"""
      </div>
      <div class="auth-divider">Don't have an account? <a href="?page=Signup">Create one</a></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  SIGNUP
# ════════════════════════════════════════════════════════════
elif page == "Signup":
    st.markdown('<div class="pw">', unsafe_allow_html=True)
    st.markdown("""
    <div class="auth-card">
      <h2>📝 Create account</h2>
      <p>Sign up to track your heart disease predictions, view analytics, and download reports.</p>
      <div style="margin-bottom:24px">
    """, unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="Choose a username (min 3 chars)", key="signup_user")
    email = st.text_input("Email", placeholder="your@email.com", key="signup_email")
    password = st.text_input("Password", type="password", placeholder="Create a password (min 4 chars)", key="signup_pass")
    confirm = st.text_input("Confirm password", type="password", placeholder="Re-enter password", key="signup_confirm")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        signup_btn = st.button("Create account", use_container_width=True)

    if signup_btn:
        if not username or not email or not password or not confirm:
            st.error("Please fill in all fields.")
        elif password != confirm:
            st.error("Passwords do not match.")
        elif len(password) < 4:
            st.error("Password must be at least 4 characters.")
        elif len(username) < 3:
            st.error("Username must be at least 3 characters.")
        else:
            ok, msg = signup_user(username, email, password)
            if ok:
                st.success(msg)
                st.markdown("""
                <div style="text-align:center;margin-top:16px">
                  <a href="?page=Login" style="display:inline-block;background:linear-gradient(135deg,#a4133c 0%,#c9184a 100%);color:#fff;text-decoration:none;padding:12px 32px;border-radius:10px;font-weight:600;font-size:15px">Go to login →</a>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(msg)

    st.markdown(f"""
      </div>
      <div class="auth-divider">Already have an account? <a href="?page=Login">Log in</a></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  PREDICTION
# ════════════════════════════════════════════════════════════
elif page == "Prediction":
    st.markdown('<div class="pw">', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero">
      <h2>🩺 Patient information</h2>
      <p>Enter the patient's clinical measurements below, then click <strong style="color:#e2e8f0">Predict Risk</strong> to get an AI-powered assessment.</p>
    </div>
    """, unsafe_allow_html=True)

    user = st.session_state.user
    st.markdown(f"""
    <div class="user-bar">
      <span class="user-bar-label">👤 Logged in as:</span>
      <span style="flex:1;color:#e2e8f0;font-weight:600;font-size:14px">{user}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Inputs ──
    st.markdown('<div class="card"><div class="ch"><span class="reddot"></span>Clinical inputs</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.slider("Age", 18, 100, 40)
    with col2:
        sex = st.selectbox("Sex", ["M", "F"], format_func=lambda x: "Male" if x == "M" else "Female")
    with col3:
        chest_pain = st.selectbox("Chest pain type", ["ATA", "NAP", "TA", "ASY"],
            help="ATA = Atypical Angina | NAP = Non-Anginal Pain | TA = Typical Angina | ASY = Asymptomatic")

    col1, col2, col3 = st.columns(3)
    with col1:
        resting_bp = st.number_input("Resting blood pressure (mm Hg)", 80, 200, 120)
    with col2:
        cholesterol = st.number_input("Cholesterol (mg/dL)", 100, 600, 200)
    with col3:
        fasting_bs = st.selectbox("Fasting blood sugar > 120 mg/dL", [0, 1],
            format_func=lambda x: "Yes (1)" if x == 1 else "No (0)")

    col1, col2, col3 = st.columns(3)
    with col1:
        resting_ecg = st.selectbox("Resting ECG", ["Normal", "ST", "LVH"])
    with col2:
        max_hr = st.number_input("Max heart rate achieved (bpm)", 60, 220, 150)
    with col3:
        exercise_angina = st.selectbox("Exercise-induced angina", ["Y", "N"],
            format_func=lambda x: "Yes" if x == "Y" else "No")

    col1, col2 = st.columns(2)
    with col1:
        oldpeak = st.slider("Oldpeak — ST depression", 0.0, 6.0, 1.0, step=0.1)
    with col2:
        st_slope = st.selectbox("ST slope", ["Up", "Flat", "Down"])

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Predict ──
    st.markdown('<div class="card"><div class="ch"><span class="reddot"></span>Risk assessment</div>', unsafe_allow_html=True)

    if st.button("🔍 Predict Risk", use_container_width=True):
        with st.spinner("Analysing clinical data…"):

            raw = {
                "Age": age, "RestingBP": resting_bp, "Cholesterol": cholesterol,
                "FastingBS": fasting_bs, "MaxHR": max_hr, "Oldpeak": oldpeak,
                "Sex_" + sex: 1,
                "ChestPainType_" + chest_pain: 1,
                "RestingECG_" + resting_ecg: 1,
                "ExerciseAngina_" + exercise_angina: 1,
                "ST_Slope_" + st_slope: 1,
            }
            inp = pd.DataFrame([raw])
            for c in expected_columns:
                if c not in inp.columns:
                    inp[c] = 0
            inp    = inp[expected_columns]
            scaled = scaler.transform(inp)
            pred   = model.predict(scaled)[0]
            prob   = model.predict_proba(scaled)[0][1] * 100
            label  = "High Risk" if pred == 1 else "Low Risk"

            # Save to DB (tagged with logged-in username)
            try:
                conn = get_connection()
                cur  = conn.cursor()
                cur.execute(
                    """INSERT INTO predictions
                       (patient_name, age, sex, chest_pain, resting_bp, cholesterol, fasting_bs,
                        resting_ecg, max_hr, exercise_angina, oldpeak, st_slope, prediction, probability)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (user, age, sex, chest_pain, resting_bp, cholesterol, fasting_bs,
                     resting_ecg, max_hr, exercise_angina, oldpeak, st_slope, label, prob)
                )
                conn.commit(); cur.close(); conn.close()
            except Exception as e:
                st.warning(f"Could not save to database: {e}")

            # ── Risk factor breakdown ──
            factors = [
                ("Age",             int((age - 18) / 82 * 100),
                 "#f43f5e" if age > 55 else "#22c55e"),
                ("Chest pain type", 90 if chest_pain=="ASY" else 65 if chest_pain=="TA" else 35 if chest_pain=="NAP" else 15,
                 "#f43f5e" if chest_pain == "ASY" else "#22c55e"),
                ("Oldpeak",         int(oldpeak / 6 * 100),
                 "#f43f5e" if oldpeak > 2 else "#22c55e"),
                ("Max heart rate",  int((220 - max_hr) / 160 * 100),
                 "#f43f5e" if max_hr < 100 else "#22c55e"),
                ("Exercise angina", 80 if exercise_angina == "Y" else 20,
                 "#f43f5e" if exercise_angina == "Y" else "#22c55e"),
                ("ST slope",        90 if st_slope == "Down" else 60 if st_slope == "Flat" else 15,
                 "#f43f5e" if st_slope != "Up" else "#22c55e"),
            ]

            bar_col = "#f43f5e" if pred == 1 else "#22c55e"
            res_cls = "result-high" if pred == 1 else "result-low"
            ico     = "⚠️" if pred == 1 else "✅"
            rtitle  = "High risk of heart disease" if pred == 1 else "Low risk of heart disease"
            sub     = ("This patient's clinical profile indicates an elevated probability of coronary artery disease. "
                       "Immediate cardiology referral and further diagnostic evaluation are strongly advised."
                       if pred == 1 else
                       "This patient's clinical profile suggests a lower likelihood of significant heart disease at this time. "
                       "Continue preventive care and routine annual monitoring.")

            factors_html = "".join(
                f'<div class="rf-row">'
                f'<span class="rf-label">{n}</span>'
                f'<div class="rf-track"><div class="rf-fill" style="width:{v}%;background:{c}"></div></div>'
                f'<span class="rf-val">{v}%</span>'
                f'</div>'
                for n, v, c in factors
            )

            st.markdown(f"""
            <div class="{res_cls}">
              <div class="result-title">{ico} {rtitle}</div>
              <div style="font-size:13px;color:#64748b;margin-bottom:8px">User: <strong style="color:#e2e8f0">{user}</strong></div>
              <div class="gauge-wrap">
                <div class="gauge-track">
                  <div class="gauge-fill" style="width:{prob:.1f}%;background:{bar_col}"></div>
                </div>
                <span class="gauge-num">{prob:.1f}%</span>
              </div>
              <div class="result-sub">{sub}</div>
            </div>
            <div class="rf-section-label">Contributing risk factors</div>
            {factors_html}
            """, unsafe_allow_html=True)

            # Suggestions
            def get_suggestions(prob, pred, age, sex, chest_pain, resting_bp,
                                 cholesterol, fasting_bs, max_hr, exercise_angina, oldpeak, st_slope):
                if pred == 1:
                    s = []
                    s.append(("🏥", "Schedule an appointment with a cardiologist as soon as possible for a comprehensive cardiovascular evaluation."))
                    if chest_pain == "ASY":
                        s.append(("⚠️", "Asymptomatic chest pain detected — this is a significant warning sign. Do not ignore silent symptoms; request a stress test or coronary angiography."))
                    if resting_bp >= 140:
                        s.append(("💊", f"Resting BP is {resting_bp} mm Hg (hypertensive range). Discuss antihypertensive medication with your doctor and reduce sodium intake to under 2,300 mg/day."))
                    elif resting_bp >= 120:
                        s.append(("🩺", f"Blood pressure is elevated at {resting_bp} mm Hg. Monitor daily and reduce stress, caffeine, and salt."))
                    if cholesterol >= 240:
                        s.append(("🥗", f"Total cholesterol is high at {cholesterol} mg/dL. A plant-based diet, regular exercise, and possible statin therapy are recommended."))
                    elif cholesterol >= 200:
                        s.append(("🥗", f"Cholesterol at {cholesterol} mg/dL is borderline high. Reduce saturated fat and increase soluble fiber intake."))
                    if fasting_bs == 1:
                        s.append(("🩸", "Fasting blood sugar is elevated (> 120 mg/dL), indicating possible diabetes or prediabetes. Consult an endocrinologist and consider an HbA1c test."))
                    if exercise_angina == "Y":
                        s.append(("🚫", "Exercise-induced chest pain is present. Avoid strenuous activity until cleared by a physician. A stress echocardiogram is advised."))
                    if oldpeak > 2:
                        s.append(("📉", f"ST depression of {oldpeak:.1f} mm during exercise suggests significant ischemia. An urgent cardiology review is recommended."))
                    if st_slope in ("Flat", "Down"):
                        s.append(("📊", f"ST slope is '{st_slope}', which is associated with reduced coronary blood flow. This warrants further diagnostic imaging."))
                    if max_hr < 100:
                        s.append(("❤️", f"Max heart rate of {max_hr} bpm is low. This may indicate chronotropic incompetence. Discuss with your cardiologist."))
                    if age > 60:
                        s.append(("🧓", f"Age {age} is a significant independent risk factor. Annual cardiac screenings are strongly recommended."))
                    s.append(("🚭", "If you smoke, stopping immediately is the single most impactful change you can make for heart health."))
                    s.append(("🏃", "Under physician guidance, begin a supervised cardiac rehabilitation program with low-intensity aerobic activity."))
                    return s, "high"
                else:
                    s = []
                    s.append(("✅", f"Your current risk probability is {prob:.1f}%, which is reassuring. Continue with annual health checkups to maintain this status."))
                    if resting_bp >= 120:
                        s.append(("🩺", f"Blood pressure of {resting_bp} mm Hg is slightly elevated. Adopt a DASH diet, reduce sodium, and exercise regularly to keep it in check."))
                    else:
                        s.append(("💚", f"Blood pressure at {resting_bp} mm Hg is in a healthy range. Keep up the good work with a balanced diet and active lifestyle."))
                    if cholesterol >= 200:
                        s.append(("🥗", f"Cholesterol at {cholesterol} mg/dL is borderline. Increase omega-3 intake (fatty fish, flaxseed) and reduce trans fats."))
                    else:
                        s.append(("💚", f"Cholesterol at {cholesterol} mg/dL looks healthy. Maintain a heart-friendly diet with fruits, vegetables, and whole grains."))
                    if fasting_bs == 1:
                        s.append(("🩸", "Fasting blood sugar is elevated. Even with low cardiac risk, diabetes management is critical — consult your doctor."))
                    if max_hr >= 150:
                        s.append(("🏃", f"Max heart rate of {max_hr} bpm indicates good cardiovascular fitness. Aim for 150 minutes of moderate aerobic exercise per week."))
                    s.append(("😴", "Ensure 7–9 hours of quality sleep per night. Poor sleep is a hidden but significant cardiovascular risk factor."))
                    s.append(("🧘", "Manage stress through mindfulness, yoga, or deep-breathing exercises. Chronic stress raises cortisol and blood pressure."))
                    s.append(("🚭", "Avoid smoking and limit alcohol to reduce your long-term cardiovascular risk."))
                    s.append(("📅", "Schedule a comprehensive health checkup annually, including ECG and lipid panel, to catch any early changes."))
                    return s, "low"

            sugg_list, sugg_cls = get_suggestions(
                prob, pred, age, sex, chest_pain, resting_bp,
                cholesterol, fasting_bs, max_hr, exercise_angina, oldpeak, st_slope
            )
            sugg_icon_label = "⚠️ Urgent recommendations" if pred == 1 else "💡 Health recommendations"
            items_html = "".join(
                f'<div class="sugg-item"><span class="sugg-icon">{ic}</span><span>{txt}</span></div>'
                for ic, txt in sugg_list
            )
            st.markdown(f"""
            <div class="sugg-box {sugg_cls}">
              <div class="sugg-title">{sugg_icon_label}</div>
              {items_html}
            </div>
            """, unsafe_allow_html=True)

            # PDF Report
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 18)
            pdf.set_text_color(180, 20, 60)
            pdf.cell(0, 14, "Heart Disease Risk Report", ln=True, align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", size=12)
            pdf.ln(4)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"User: {user}", ln=True)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Result: {label}", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Risk Probability: {prob:.2f}%", ln=True)
            pdf.ln(4)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Patient Details:", ln=True)
            pdf.set_font("Arial", size=11)
            for k, v in [
                ("Age", age), ("Sex", "Male" if sex == "M" else "Female"),
                ("Chest Pain Type", chest_pain), ("Resting BP", f"{resting_bp} mm Hg"),
                ("Cholesterol", f"{cholesterol} mg/dL"),
                ("Fasting Blood Sugar >120", "Yes" if fasting_bs == 1 else "No"),
                ("Resting ECG", resting_ecg), ("Max Heart Rate", max_hr),
                ("Exercise Angina", "Yes" if exercise_angina == "Y" else "No"),
                ("Oldpeak", f"{oldpeak:.1f}"), ("ST Slope", st_slope),
            ]:
                pdf.cell(0, 9, f"  {k}: {v}", ln=True)
            pdf.ln(6)
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 10, "Recommendations:", ln=True)
            pdf.set_font("Arial", size=10)
            for _, txt in sugg_list[:5]:
                txt = txt.replace("–", "-")
                txt = txt.replace("—", "-")
                txt = txt.replace("•", "*")
                txt = txt.replace("'", "'")
                txt = txt.replace(""", '"')
                txt = txt.replace(""", '"')
                pdf.multi_cell(0, 8, f"  - {txt}")
                pdf.ln(1)
            pdf.ln(4)
            pdf.set_font("Arial", "I", 10)
            pdf.set_text_color(120, 120, 120)
            pdf.multi_cell(0, 8,
                "Disclaimer: This report is generated by an AI-assisted educational tool and "
                "should not be considered a medical diagnosis. Always consult a qualified "
                "healthcare professional.")
            pdf.output("Heart_Report.pdf")

            with open("Heart_Report.pdf", "rb") as f:
                st.download_button(
                    label="📄 Download PDF Report", data=f,
                    file_name="Heart_Report.pdf", mime="application/pdf"
                )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">⚕️ For educational purposes only — not a medical diagnosis.</div></div>',
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  DASHBOARD
# ════════════════════════════════════════════════════════════
elif page == "Dashboard":
    st.markdown('<div class="pw">', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero">
      <h2>📊 Dashboard</h2>
      <p>Analytics and summary statistics across your predictions.</p>
    </div>
    """, unsafe_allow_html=True)

    user = st.session_state.user
    try:
        conn = get_connection()
        df   = pd.read_sql(
            "SELECT * FROM predictions WHERE patient_name = %s ORDER BY prediction_date DESC",
            conn, params=(user,)
        )
        conn.close()
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        df = pd.DataFrame()

    total    = len(df)
    high     = int((df["prediction"] == "High Risk").sum()) if total > 0 else 0
    low      = total - high
    avg_prob = f"{df['probability'].mean():.1f}%" if total > 0 else "—"
    high_pct = f"{high/total*100:.0f}%" if total > 0 else "—"

    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-card">
        <div class="sn" style="color:#f8fafc">{total}</div>
        <div class="sl">Your predictions</div>
      </div>
      <div class="stat-card">
        <div class="sn" style="color:#fb7185">{high}</div>
        <div class="sl">High risk</div>
      </div>
      <div class="stat-card">
        <div class="sn" style="color:#4ade80">{low}</div>
        <div class="sl">Low risk</div>
      </div>
      <div class="stat-card">
        <div class="sn" style="color:#f8fafc">{avg_prob}</div>
        <div class="sl">Avg probability</div>
      </div>
      <div class="stat-card">
        <div class="sn" style="color:#fb7185">{high_pct}</div>
        <div class="sl">High risk rate</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if total == 0:
        st.markdown("""
        <div class="card">
          <div class="es">
            <div class="es-i">📊</div>
            <p>No predictions yet.<br>Go to the <strong style="color:#e2e8f0">Prediction</strong> tab to get started.</p>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card"><div class="ch"><span class="reddot"></span>Risk distribution</div>', unsafe_allow_html=True)
            fig_pie = go.Figure(go.Pie(
                labels=["High Risk", "Low Risk"], values=[high, low],
                hole=0.60,
                marker=dict(colors=["#c9184a", "#15803d"], line=dict(color="#111111", width=3)),
                textinfo="percent+label", textfont=dict(size=12, color="#e2e8f0"),
                showlegend=False,
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
            ))
            fig_pie.update_layout(
                margin=dict(t=10, b=10, l=10, r=10), height=270,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", family="Inter"),
                annotations=[dict(text=f"<b>{total}</b><br>total", x=0.5, y=0.5,
                                  font=dict(size=16, color="#e2e8f0"), showarrow=False)]
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="card"><div class="ch"><span class="reddot"></span>Probability trend (last 20)</div>', unsafe_allow_html=True)
            trend = df.sort_values("prediction_date").tail(20).reset_index(drop=True)
            colors = ["#f43f5e" if p >= 50 else "#22c55e" for p in trend["probability"]]
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=list(range(1, len(trend) + 1)), y=trend["probability"].round(1),
                mode="lines+markers", line=dict(color="#c9184a", width=2),
                marker=dict(color=colors, size=7, line=dict(width=0)),
                fill="tozeroy", fillcolor="rgba(201,24,74,0.08)",
                hovertemplate="Prediction #%{x}<br>Probability: %{y:.1f}%<extra></extra>",
            ))
            fig_line.add_hline(y=50, line_dash="dot", line_color="#475569",
                               annotation_text="50% threshold", annotation_font_color="#64748b",
                               annotation_font_size=11)
            fig_line.update_layout(
                margin=dict(t=10, b=30, l=10, r=10), height=270,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#64748b", family="Inter"),
                xaxis=dict(showgrid=False, title=dict(text="Prediction #", font=dict(size=11, color="#475569")),
                           tickfont=dict(color="#475569"), zeroline=False),
                yaxis=dict(showgrid=True, gridcolor="#161616", range=[0, 105],
                           title=dict(text="Probability %", font=dict(size=11, color="#475569")),
                           tickfont=dict(color="#475569"), zeroline=False),
            )
            st.plotly_chart(fig_line, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if "age" in df.columns:
            st.markdown('<div class="card"><div class="ch"><span class="reddot"></span>Age vs risk probability</div>', unsafe_allow_html=True)
            fig_sc = go.Figure(go.Scatter(
                x=df["age"], y=df["probability"].round(1), mode="markers",
                marker=dict(
                    color=df["probability"],
                    colorscale=[[0, "#15803d"], [0.5, "#f59e0b"], [1, "#c9184a"]],
                    size=10, opacity=0.8, showscale=True,
                    colorbar=dict(title=dict(text="Prob %", font=dict(color="#64748b", size=11)),
                                  thickness=12, len=0.85, tickfont=dict(color="#64748b"),
                                  bgcolor="rgba(0,0,0,0)", bordercolor="#1e1e1e"),
                    line=dict(width=0),
                ),
                text=df.get("prediction"),
                hovertemplate="Age: %{x}<br>Probability: %{y:.1f}%<br>%{text}<extra></extra>",
            ))
            fig_sc.add_hline(y=50, line_dash="dot", line_color="#475569")
            fig_sc.update_layout(
                margin=dict(t=10, b=30, l=10, r=10), height=260,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#64748b", family="Inter"),
                xaxis=dict(showgrid=False, title=dict(text="Age", font=dict(size=11, color="#475569")),
                           tickfont=dict(color="#475569"), zeroline=False),
                yaxis=dict(showgrid=True, gridcolor="#161616", range=[0, 105],
                           title=dict(text="Probability %", font=dict(size=11, color="#475569")),
                           tickfont=dict(color="#475569"), zeroline=False),
            )
            st.plotly_chart(fig_sc, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="footer">⚕️ For educational purposes only — not a medical diagnosis.</div></div>',
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  HISTORY
# ════════════════════════════════════════════════════════════
elif page == "History":
    st.markdown('<div class="pw">', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero">
      <h2>📜 Prediction history</h2>
      <p>All predictions saved under your account, ordered by most recent first.</p>
    </div>
    """, unsafe_allow_html=True)

    user = st.session_state.user
    try:
        conn    = get_connection()
        history = pd.read_sql(
            "SELECT * FROM predictions WHERE patient_name = %s ORDER BY prediction_date DESC",
            conn, params=(user,)
        )
        conn.close()
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        history = pd.DataFrame()

    n = len(history)
    st.markdown(f"""
    <div class="user-bar" style="margin-bottom:16px">
      <span class="user-bar-label">👤 Logged in as:</span>
      <span style="flex:1;color:#e2e8f0;font-weight:600;font-size:14px">{user}</span>
      <span style="font-size:11px;color:#475569">(only your predictions shown)</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="card"><div class="ch"><span class="reddot"></span>'
        f'{n} record{"s" if n != 1 else ""}</div>',
        unsafe_allow_html=True
    )

    if n == 0:
        st.markdown(f"""
        <div class="es">
          <div class="es-i">📜</div>
          <p>No predictions found for <strong style="color:#e2e8f0">{user}</strong>.<br>Go to the Prediction tab to run one.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        show_cols = [c for c in [
            "prediction_date", "age", "sex", "chest_pain", "resting_bp",
            "cholesterol", "max_hr", "oldpeak", "st_slope", "prediction", "probability"
        ] if c in history.columns]

        disp = history[show_cols].copy()
        if "probability" in disp.columns:
            disp["probability"] = disp["probability"].round(1).astype(str) + "%"

        col_labels = {
            "prediction_date": "Date", "age": "Age", "sex": "Sex",
            "chest_pain": "Chest Pain", "resting_bp": "BP (mmHg)",
            "cholesterol": "Chol.", "max_hr": "Max HR",
            "oldpeak": "Oldpeak", "st_slope": "ST Slope",
            "prediction": "Result", "probability": "Probability"
        }

        heads = "".join(
            f"<th>{col_labels.get(c, c.replace('_',' ').title())}</th>"
            for c in disp.columns
        )
        rows = ""
        for _, row in disp.iterrows():
            cells = ""
            for col in disp.columns:
                v = row[col]
                if col == "prediction":
                    cls = "bh" if v == "High Risk" else "bl"
                    cells += f'<td><span class="{cls}">{v}</span></td>'
                elif col == "sex":
                    cells += f"<td>{'Male' if v == 'M' else 'Female'}</td>"
                else:
                    cells += f"<td>{v}</td>"
            rows += f"<tr>{cells}</tr>"

        st.markdown(f"""
        <div class="htw">
          <table class="ht">
            <thead><tr>{heads}</tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">⚕️ For educational purposes only — not a medical diagnosis.</div></div>',
                unsafe_allow_html=True)