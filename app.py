import streamlit as st

st.set_page_config(
    page_title="Planer App",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS Design ───────────────────────────────────────────────
st.markdown("""
<style>
    /* Hintergrund */
    .stApp { background-color: #f4f1ea; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2b2018 0%, #3d2c1d 100%);
    }
    [data-testid="stSidebar"] * { color: #fbf6ee !important; }

    /* Navigation Buttons */
    .nav-btn {
        display: block;
        width: 100%;
        padding: 14px 18px;
        margin: 4px 0;
        border-radius: 10px;
        border: none;
        background: transparent;
        color: #bfae9a !important;
        font-size: 1rem;
        font-weight: 600;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s;
    }
    .nav-btn:hover { background: rgba(255,255,255,0.1); color: #fff !important; }
    .nav-btn.active { background: #c2410c !important; color: #fff !important; }

    /* Header */
    .app-header {
        background: linear-gradient(135deg, #2b2018, #3d2c1d);
        border-radius: 14px;
        padding: 22px 26px;
        margin-bottom: 20px;
        color: #fbf6ee;
    }
    .app-header h1 { margin: 0; font-size: 1.8rem; color: #fbf6ee; }
    .app-header p { margin: 6px 0 0; font-size: 0.82rem; color: #bfae9a; text-transform: uppercase; letter-spacing: 0.04em; }

    /* Karten */
    .card {
        background: #fffdf8;
        border: 1px solid #e6dfd3;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(38,32,26,.06), 0 8px 24px rgba(38,32,26,.06);
    }

    /* Metriken */
    .metric-card {
        background: #fffdf8;
        border: 1px solid #e6dfd3;
        border-radius: 14px;
        padding: 18px 20px;
        text-align: center;
        box-shadow: 0 1px 2px rgba(38,32,26,.06);
    }
    .metric-card .value { font-size: 2rem; font-weight: 700; color: #c2410c; }
    .metric-card .label { font-size: 0.82rem; color: #6b6258; margin-top: 4px; }

    /* Streamlit Elemente anpassen */
    h1, h2, h3 { color: #26201a; }
    .stButton > button {
        background: #c2410c;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stButton > button:hover { background: #a83209; color: white; }

    /* Divider */
    hr { border-color: #e6dfd3; }
</style>
""", unsafe_allow_html=True)

# ─── Session State ─────────────────────────────────────────────
if "seite" not in st.session_state:
    st.session_state.seite = "Dashboard"

# ─── Sidebar Navigation ────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 16px 0 24px;'>
        <div style='font-size:1.6rem; font-weight:700; color:#fbf6ee;'>📋 Planer</div>
        <div style='font-size:0.75rem; color:#bfae9a; margin-top:4px; text-transform:uppercase; letter-spacing:0.05em;'>Gries Schleiftechnik</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation
    nav_items = [
        ("🏠", "Dashboard"),
        ("📅", "Planer"),
        ("📝", "Notizen"),
        ("📄", "Rechnungen"),
        ("✉️", "Outlook"),
        ("⚙️", "Einstellungen"),
    ]

    for icon, name in nav_items:
        if st.button(f"{icon}  {name}", key=f"nav_{name}",
                     use_container_width=True,
                     type="primary" if st.session_state.seite == name else "secondary"):
            st.session_state.seite = name
            st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem; color:#6b6258; padding: 8px 0;'>
        Version 0.1 · Phase 2<br>
        Daten: lokal
    </div>
    """, unsafe_allow_html=True)

# ─── Seiten ────────────────────────────────────────────────────
seite = st.session_state.seite

# Datum für Header
from datetime import datetime
heute = datetime.now().strftime("%A, %d. %B %Y")
kw = datetime.now().isocalendar()[1]

if seite == "Dashboard":
    st.markdown(f"""
    <div class='app-header'>
        <h1>🏠 Dashboard</h1>
        <p>{heute} · KW {kw}</p>
    </div>
    """, unsafe_allow_html=True)

    # Metriken
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <div class='value'>0</div>
            <div class='label'>Offene Aufgaben</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <div class='value'>0</div>
            <div class='label'>Notizen</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <div class='value'>0</div>
            <div class='label'>Offene Rechnungen</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class='metric-card'>
            <div class='value'>0</div>
            <div class='label'>Neue Mails</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='card'>
            <h3>📅 Heute</h3>
            <p style='color:#6b6258; font-style:italic;'>Noch keine Aufgaben für heute.</p>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='card'>
            <h3>📝 Letzte Notizen</h3>
            <p style='color:#6b6258; font-style:italic;'>Noch keine Notizen vorhanden.</p>
        </div>""", unsafe_allow_html=True)

elif seite == "Planer":
    st.markdown(f"""
    <div class='app-header'>
        <h1>📅 Planer</h1>
        <p>{heute} · KW {kw}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class='card'>
        <h3>🚧 Wird aufgebaut...</h3>
        <p style='color:#6b6258;'>Das Planer-Modul wird in Phase 3 fertiggestellt.</p>
    </div>""", unsafe_allow_html=True)

elif seite == "Notizen":
    st.markdown(f"""
    <div class='app-header'>
        <h1>📝 Notizen</h1>
        <p>{heute} · KW {kw}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class='card'>
        <h3>🚧 Wird aufgebaut...</h3>
        <p style='color:#6b6258;'>Das Notizen-Modul wird in Phase 3 fertiggestellt.</p>
    </div>""", unsafe_allow_html=True)

elif seite == "Rechnungen":
    st.markdown(f"""
    <div class='app-header'>
        <h1>📄 Rechnungen</h1>
        <p>{heute} · KW {kw}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class='card'>
        <h3>🚧 Wird aufgebaut...</h3>
        <p style='color:#6b6258;'>Das Rechnungs-Modul wird in Phase 4 fertiggestellt.</p>
    </div>""", unsafe_allow_html=True)

elif seite == "Outlook":
    st.markdown(f"""
    <div class='app-header'>
        <h1>✉️ Outlook</h1>
        <p>{heute} · KW {kw}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class='card'>
        <h3>🚧 Wird aufgebaut...</h3>
        <p style='color:#6b6258;'>Die Outlook-Integration wird in Phase 5 fertiggestellt.</p>
    </div>""", unsafe_allow_html=True)

elif seite == "Einstellungen":
    st.markdown(f"""
    <div class='app-header'>
        <h1>⚙️ Einstellungen</h1>
        <p>{heute} · KW {kw}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🔑 API-Schlüssel")
    api_key = st.text_input("Anthropic API-Key", type="password", placeholder="sk-ant-...")
    if st.button("Speichern"):
        st.success("Schlüssel gespeichert!")
    st.markdown("</div>", unsafe_allow_html=True)
