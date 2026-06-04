import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(
    page_title="Planer App",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #f4f1ea; }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2b2018 0%, #3d2c1d 100%) !important;
    }
    
    /* Sidebar Button Text sichtbar machen */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        color: #bfae9a !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        text-align: left !important;
        padding: 12px 16px !important;
        width: 100% !important;
        font-size: 0.95rem !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.1) !important;
        color: #fff !important;
        border-color: rgba(255,255,255,0.3) !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #c2410c !important;
        color: #fff !important;
        border-color: #c2410c !important;
    }
    
    /* Metriken */
    .metric-card {
        background: #fffdf8;
        border: 1px solid #e6dfd3;
        border-radius: 14px;
        padding: 18px 20px;
        text-align: center;
        box-shadow: 0 1px 2px rgba(38,32,26,.06);
        margin-bottom: 8px;
    }
    .metric-card .value { font-size: 2rem; font-weight: 700; color: #c2410c; }
    .metric-card .label { font-size: 0.82rem; color: #6b6258; margin-top: 4px; }
    
    /* Karten */
    .card {
        background: #fffdf8;
        border: 1px solid #e6dfd3;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(38,32,26,.06), 0 8px 24px rgba(38,32,26,.06);
    }
    
    h1, h2, h3 { color: #26201a; }
    
    /* Hauptbereich Buttons */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    
    hr { border-color: #e6dfd3; }
</style>
""", unsafe_allow_html=True)

if "seite" not in st.session_state:
    st.session_state.seite = "Dashboard"

def lade_aufgaben():
    if os.path.exists("data/aufgaben.json"):
        with open("data/aufgaben.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def lade_notizen():
    if os.path.exists("data/notizen.json"):
        with open("data/notizen.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def lade_rechnungen():
    if os.path.exists("data/rechnungen.json"):
        with open("data/rechnungen.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ─── Sidebar Navigation ────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 16px 0 24px;'>
        <div style='font-size:1.6rem; font-weight:700; color:#fbf6ee;'>📋 Planer</div>
        <div style='font-size:0.75rem; color:#bfae9a; margin-top:4px; 
             text-transform:uppercase; letter-spacing:0.05em;'>Gries Schleiftechnik</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    nav_items = [
        ("🏠", "Dashboard"),
        ("📅", "Planer"),
        ("📝", "Notizen"),
        ("📄", "Rechnungen"),
        ("✉️", "Outlook"),
        ("⚙️", "Einstellungen"),
    ]
    
    for icon, name in nav_items:
        aktiv = st.session_state.seite == name
        if st.button(
            f"{icon}  {name}",
            key=f"nav_{name}",
            use_container_width=True,
            type="primary" if aktiv else "secondary"
        ):
            st.session_state.seite = name
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem; color:#6b6258; padding: 8px 0;'>
        Version 0.2 · Phase 3<br>Daten: lokal
    </div>
    """, unsafe_allow_html=True)

# ─── Header Funktion ───────────────────────────────────────────
seite = st.session_state.seite
heute = datetime.now()
heute_str = heute.strftime("%A, %d. %B %Y")
kw = heute.isocalendar()[1]

def app_header(titel, icon):
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #2b2018, #3d2c1d); border-radius: 14px;
         padding: 22px 26px; margin-bottom: 20px;'>
        <h1 style='margin:0; font-size:1.8rem; color:#fbf6ee;'>{icon} {titel}</h1>
        <p style='margin:6px 0 0; font-size:0.82rem; color:#bfae9a; 
             text-transform:uppercase; letter-spacing:0.04em;'>{heute_str} · KW {kw}</p>
    </div>""", unsafe_allow_html=True)

# ─── Seiten ────────────────────────────────────────────────────
if seite == "Dashboard":
    app_header("Dashboard", "🏠")
    
    aufgaben = lade_aufgaben()
    notizen = lade_notizen()
    rechnungen = lade_rechnungen()
    offen = len([a for a in aufgaben if not a.get("erledigt")])
    offene_re = len([r for r in rechnungen if r.get("status") == "offen"])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='value'>{offen}</div><div class='label'>Offene Aufgaben</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='value'>{len(notizen)}</div><div class='label'>Notizen</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='value'>{offene_re}</div><div class='label'>Offene Rechnungen</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='metric-card'><div class='value'>0</div><div class='label'>Neue Mails</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='card'><h3>📅 Heute</h3>", unsafe_allow_html=True)
        heute_iso = str(heute.date())
        heute_aufgaben = [a for a in aufgaben if a.get("datum") == heute_iso and not a.get("erledigt")]
        if heute_aufgaben:
            for a in heute_aufgaben:
                farbe = "#dc2626" if a.get("typ") == "rechnung" else "#c2410c"
                st.markdown(f"<div style='padding:6px 0; border-bottom:1px solid #e6dfd3; color:{farbe};'>⭕ {a['text']}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#6b6258; font-style:italic;'>Keine Aufgaben für heute.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'><h3>📝 Letzte Notizen</h3>", unsafe_allow_html=True)
        if notizen:
            for n in notizen[:3]:
                st.markdown(f"<div style='padding:6px 0; border-bottom:1px solid #e6dfd3;'>📝 {n.get('titel', 'Ohne Titel')}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#6b6258; font-style:italic;'>Noch keine Notizen vorhanden.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif seite == "Planer":
    exec(open('planer_modul.py', encoding='utf-8').read())

elif seite == "Notizen":
    exec(open("notizen_modul.py", encoding="utf-8").read())

elif seite == "Rechnungen":
    exec(open("rechnungen_modul.py", encoding="utf-8").read())

elif seite == "Outlook":
    app_header("Outlook", "✉️")
    st.markdown("<div class='card'><h3>🚧 Wird aufgebaut...</h3><p style='color:#6b6258;'>Die Outlook-Integration kommt in Phase 6.</p></div>", unsafe_allow_html=True)

elif seite == "Einstellungen":
    app_header("Einstellungen", "⚙️")
    
    # KI Helfer laden
    import importlib.util, sys
    spec = importlib.util.spec_from_file_location("ki_helfer", "ki_helfer.py")
    ki = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ki)
    
    st.markdown("<div style='background:#fffdf8; border:1px solid #e6dfd3; border-radius:14px; padding:20px; margin-bottom:16px;'>", unsafe_allow_html=True)
    st.subheader("🔑 Anthropic API-Schlüssel")
    
    aktueller_key = ki.lade_api_key()
    if aktueller_key:
        st.markdown("<div style='background:#dcfce7; border:1px solid #86efac; border-radius:8px; padding:10px 14px; margin-bottom:12px;'><span style='color:#166534;'>✅ API-Schlüssel ist hinterlegt und aktiv</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background:#fee2e2; border:1px solid #fca5a5; border-radius:8px; padding:10px 14px; margin-bottom:12px;'><span style='color:#991b1b;'>⚠️ Kein API-Schlüssel hinterlegt - KI-Funktionen nicht verfügbar</span></div>", unsafe_allow_html=True)
    
    neuer_key = st.text_input("Anthropic API-Key", type="password", placeholder="sk-ant-...", value=aktueller_key)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Schlüssel speichern", type="primary", use_container_width=True):
            if neuer_key:
                ki.speichere_api_key(neuer_key)
                st.success("✅ Schlüssel gespeichert! KI-Funktionen sind jetzt aktiv.")
                st.rerun()
    with col2:
        if st.button("🔍 Verbindung testen", use_container_width=True):
            with st.spinner("Teste Verbindung..."):
                antwort, fehler = ki.claude_anfrage("Antworte nur mit: OK", max_tokens=10)
                if antwort:
                    st.success("✅ Verbindung erfolgreich!")
                else:
                    st.error(f"❌ Fehler: {fehler}")
    
    st.markdown("<div style='font-size:0.8rem; color:#6b6258; margin-top:10px;'>Der Schlüssel wird lokal auf deinem PC gespeichert und nicht weitergegeben.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Daten Export
    st.markdown("<div style='background:#fffdf8; border:1px solid #e6dfd3; border-radius:14px; padding:20px;'>", unsafe_allow_html=True)
    st.subheader("💾 Datensicherung")
    if st.button("⬇️ Alle Daten exportieren", use_container_width=True):
        import zipfile, io
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for datei in ["data/aufgaben.json", "data/notizen.json", "data/rechnungen.json", "data/lieferanten.json"]:
                if os.path.exists(datei):
                    zf.write(datei)
        st.download_button("📦 ZIP herunterladen", data=zip_buffer.getvalue(),
            file_name=f"planer_backup_{date.today()}.zip", mime="application/zip")
    st.markdown("</div>", unsafe_allow_html=True)
