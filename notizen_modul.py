import streamlit as st
from datetime import datetime, date
import json
import os
import sys

# KI Helfer laden
def lade_ki():
    import importlib.util
    spec = importlib.util.spec_from_file_location("ki_helfer", "ki_helfer.py")
    ki = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ki)
    return ki

# ─── Daten laden/speichern ─────────────────────────────────────
NOTIZEN_FILE = "data/notizen.json"
ORDNER_FILE = "data/ordner.json"

STANDARD_ORDNER = [
    "00 Eingang", "10 Projekte", "20 Schleifprozess",
    "30 Lieferanten", "40 Privat"
]

STANDARD_TAGS = [
    "00 Eingang", "10 Projekte", "20 Schleifprozess",
    "30 Lieferanten", "40 Privat"
]

KURZNOTIZ_FARBEN = {
    "🔴 Rot": "#fee2e2",
    "🟠 Orange": "#ffedd5",
    "🟡 Gelb": "#fef9c3",
    "🟢 Grün": "#dcfce7",
}

def lade_notizen():
    if os.path.exists(NOTIZEN_FILE):
        with open(NOTIZEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def speichere_notizen(notizen):
    os.makedirs("data", exist_ok=True)
    with open(NOTIZEN_FILE, "w", encoding="utf-8") as f:
        json.dump(notizen, f, ensure_ascii=False, indent=2)

def lade_ordner():
    if os.path.exists(ORDNER_FILE):
        with open(ORDNER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return STANDARD_ORDNER.copy()

def speichere_ordner(ordner):
    os.makedirs("data", exist_ok=True)
    with open(ORDNER_FILE, "w", encoding="utf-8") as f:
        json.dump(ordner, f, ensure_ascii=False, indent=2)

def naechste_id(notizen):
    if not notizen:
        return 1
    return max(n["id"] for n in notizen) + 1

# ─── Session State ─────────────────────────────────────────────
if "notizen" not in st.session_state:
    st.session_state.notizen = lade_notizen()
if "ordner_liste" not in st.session_state:
    st.session_state.ordner_liste = lade_ordner()
if "sel_notiz_id" not in st.session_state:
    st.session_state.sel_notiz_id = None
if "zeige_neu_notiz" not in st.session_state:
    st.session_state.zeige_neu_notiz = False
if "notiz_vorlage" not in st.session_state:
    st.session_state.notiz_vorlage = None
if "ordner_filter" not in st.session_state:
    st.session_state.ordner_filter = "Alle"
if "suche" not in st.session_state:
    st.session_state.suche = ""
if "zeige_ordner_mgmt" not in st.session_state:
    st.session_state.zeige_ordner_mgmt = False

# ─── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    .notiz-item {
        background: #fffdf8; border: 1px solid #e6dfd3; border-radius: 11px;
        padding: 12px 14px; margin-bottom: 8px; cursor: pointer; transition: .15s;
    }
    .notiz-item:hover { border-color: #d8cdbd; }
    .notiz-item.sel { border-color: #c2410c; background: #fef0e6; }
    .notiz-titel { font-weight: 600; font-size: 0.92rem; margin-bottom: 3px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .notiz-meta { font-size: 0.74rem; color: #6b6258; }
    .notiz-tag { display: inline-block; font-size: 0.68rem; background: #fef0e6;
        color: #c2410c; padding: 2px 7px; border-radius: 10px; margin-top: 4px; font-weight: 600; }
    .notiz-tag.gelb { background: #fef9c3; color: #854d0e; }
    .notiz-tag.gruen { background: #dcfce7; color: #166534; }
    .notiz-tag.rot { background: #fee2e2; color: #991b1b; }
    .vorlage-btn {
        background: #fffdf8; border: 1px solid #e6dfd3; border-radius: 12px;
        padding: 16px; text-align: center; cursor: pointer; transition: .15s;
        margin-bottom: 8px;
    }
    .vorlage-btn:hover { border-color: #c2410c; background: #fef0e6; }
    .vorlage-icon { font-size: 1.8rem; margin-bottom: 6px; }
    .vorlage-name { font-weight: 600; font-size: 0.9rem; color: #26201a; }
    .vorlage-desc { font-size: 0.75rem; color: #6b6258; margin-top: 3px; }
    .notiz-header-besprechung {
        background: #fffdf8; border: 1px solid #e6dfd3; border-radius: 10px;
        padding: 14px 16px; margin-bottom: 14px; border-left: 4px solid #c2410c;
    }
    .kurznotiz-rot { background: #fee2e2 !important; border-color: #fca5a5 !important; }
    .kurznotiz-orange { background: #ffedd5 !important; border-color: #fdba74 !important; }
    .kurznotiz-gelb { background: #fef9c3 !important; border-color: #fde047 !important; }
    .kurznotiz-gruen { background: #dcfce7 !important; border-color: #86efac !important; }
</style>
""", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────
heute = datetime.now()
heute_str = heute.strftime("%A, %d. %B %Y")
kw = heute.isocalendar()[1]

st.markdown(f"""
<div style='background: linear-gradient(135deg, #2b2018, #3d2c1d); border-radius: 14px;
     padding: 22px 26px; margin-bottom: 20px;'>
    <h1 style='margin:0; font-size:1.8rem; color:#fbf6ee;'>📝 Notizen</h1>
    <p style='margin:6px 0 0; font-size:0.82rem; color:#bfae9a; text-transform:uppercase; letter-spacing:0.04em;'>
        {heute_str} · KW {kw}</p>
</div>""", unsafe_allow_html=True)

# ─── Layout: Links Liste, Rechts Editor ────────────────────────
col_links, col_rechts = st.columns([1, 2])

with col_links:
    # Suche
    suche = st.text_input("🔍 Notizen suchen", placeholder="Suchbegriff eingeben...")
    
    # Neue Notiz Button
    if st.button("✏️ Neue Notiz", use_container_width=True, type="primary"):
        st.session_state.zeige_neu_notiz = True
        st.session_state.notiz_vorlage = None
        st.session_state.sel_notiz_id = None
        st.rerun()

    # Ordner Filter
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**📁 Ordner**")
    
    alle_ordner = ["Alle"] + st.session_state.ordner_liste
    for ordner in alle_ordner:
        anzahl = len([n for n in st.session_state.notizen 
                     if ordner == "Alle" or n.get("ordner") == ordner])
        aktiv = st.session_state.ordner_filter == ordner
        if st.button(
            f"{'📂' if aktiv else '📁'} {ordner} ({anzahl})",
            key=f"ordner_{ordner}",
            use_container_width=True,
            type="primary" if aktiv else "secondary"
        ):
            st.session_state.ordner_filter = ordner
            st.rerun()

    # Ordner verwalten
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚙️ Ordner verwalten", use_container_width=True):
        st.session_state.zeige_ordner_mgmt = not st.session_state.zeige_ordner_mgmt
        st.rerun()

    if st.session_state.zeige_ordner_mgmt:
        st.markdown("**Neuen Ordner anlegen:**")
        neuer_ordner = st.text_input("Ordnername", key="neuer_ordner_input", 
                                      placeholder="z.B. 50 Archiv")
        if st.button("➕ Anlegen", key="btn_neuer_ordner"):
            if neuer_ordner and neuer_ordner not in st.session_state.ordner_liste:
                st.session_state.ordner_liste.append(neuer_ordner)
                speichere_ordner(st.session_state.ordner_liste)
                st.success(f"Ordner '{neuer_ordner}' angelegt!")
                st.rerun()

        st.markdown("**Ordner umbenennen:**")
        ordner_zum_umbenennen = st.selectbox("Ordner wählen", 
                                              st.session_state.ordner_liste,
                                              key="ordner_umbenennen_sel")
        neuer_name = st.text_input("Neuer Name", key="neuer_ordner_name")
        if st.button("✏️ Umbenennen", key="btn_umbenennen"):
            if neuer_name and ordner_zum_umbenennen in st.session_state.ordner_liste:
                idx = st.session_state.ordner_liste.index(ordner_zum_umbenennen)
                st.session_state.ordner_liste[idx] = neuer_name
                # Notizen aktualisieren
                for n in st.session_state.notizen:
                    if n.get("ordner") == ordner_zum_umbenennen:
                        n["ordner"] = neuer_name
                speichere_ordner(st.session_state.ordner_liste)
                speichere_notizen(st.session_state.notizen)
                st.success("Umbenannt!")
                st.rerun()

    st.markdown("<hr style='border-color:#e6dfd3;'>", unsafe_allow_html=True)
    
    # Notizen Liste
    notizen_gefiltert = st.session_state.notizen
    if st.session_state.ordner_filter != "Alle":
        notizen_gefiltert = [n for n in notizen_gefiltert 
                            if n.get("ordner") == st.session_state.ordner_filter]
    if suche:
        notizen_gefiltert = [n for n in notizen_gefiltert 
                            if suche.lower() in n.get("titel", "").lower() 
                            or suche.lower() in n.get("inhalt", "").lower()]
    
    notizen_gefiltert = sorted(notizen_gefiltert, key=lambda x: x.get("geaendert", ""), reverse=True)
    
    if not notizen_gefiltert:
        st.markdown("<p style='color:#6b6258; font-style:italic; font-size:0.88rem;'>Keine Notizen gefunden.</p>", unsafe_allow_html=True)
    
    for notiz in notizen_gefiltert:
        aktiv = notiz["id"] == st.session_state.sel_notiz_id
        farbe_bg = KURZNOTIZ_FARBEN.get(notiz.get("farbe", ""), "#fffdf8")
        border = "#c2410c" if aktiv else "#e6dfd3"
        
        if notiz.get("vorlage") == "kurznotiz":
            bg = farbe_bg
        else:
            bg = "#fef0e6" if aktiv else "#fffdf8"
            
        st.markdown(f"""
        <div style='background:{bg}; border:1px solid {border}; border-radius:11px;
             padding:12px 14px; margin-bottom:8px;'>
            <div style='font-weight:600; font-size:0.92rem;'>{notiz.get("titel", "Ohne Titel")}</div>
            <div style='font-size:0.74rem; color:#6b6258;'>
                {notiz.get("ordner", "00 Eingang")} · 
                {datetime.fromisoformat(notiz.get("geaendert", datetime.now().isoformat())).strftime("%d.%m. %H:%M")}
            </div>
        </div>""", unsafe_allow_html=True)
        
        if st.button("Öffnen", key=f"open_notiz_{notiz['id']}", use_container_width=True):
            st.session_state.sel_notiz_id = notiz["id"]
            st.session_state.zeige_neu_notiz = False
            st.rerun()

with col_rechts:

    # ─── Neue Notiz: Vorlage wählen ────────────────────────────
    if st.session_state.zeige_neu_notiz and st.session_state.notiz_vorlage is None:
        st.markdown("### 📋 Vorlage wählen")
        st.markdown("<p style='color:#6b6258;'>Wähle eine Vorlage für deine neue Notiz:</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class='vorlage-btn'>
                <div class='vorlage-icon'>👥</div>
                <div class='vorlage-name'>Besprechung</div>
                <div class='vorlage-desc'>Thema, Teilnehmer, Datum im Kopf</div>
            </div>""", unsafe_allow_html=True)
            if st.button("Besprechung wählen", key="vorlage_besprechung", use_container_width=True):
                st.session_state.notiz_vorlage = "besprechung"
                st.rerun()
        
        with col2:
            st.markdown("""
            <div class='vorlage-btn'>
                <div class='vorlage-icon'>⚡</div>
                <div class='vorlage-name'>Kurznotiz</div>
                <div class='vorlage-desc'>Schnelle Idee mit Farbe & Erinnerung</div>
            </div>""", unsafe_allow_html=True)
            if st.button("Kurznotiz wählen", key="vorlage_kurznotiz", use_container_width=True):
                st.session_state.notiz_vorlage = "kurznotiz"
                st.rerun()
        
        with col3:
            st.markdown("""
            <div class='vorlage-btn'>
                <div class='vorlage-icon'>📄</div>
                <div class='vorlage-name'>Allgemeine Notiz</div>
                <div class='vorlage-desc'>Freie Notiz mit Thema & Datum</div>
            </div>""", unsafe_allow_html=True)
            if st.button("Allgemein wählen", key="vorlage_allgemein", use_container_width=True):
                st.session_state.notiz_vorlage = "allgemein"
                st.rerun()
        
        if st.button("Abbrechen", key="cancel_neu"):
            st.session_state.zeige_neu_notiz = False
            st.rerun()

    # ─── Neue Notiz: Besprechung ───────────────────────────────
    elif st.session_state.zeige_neu_notiz and st.session_state.notiz_vorlage == "besprechung":
        st.markdown("### 👥 Neue Besprechungsnotiz")
        
        st.markdown("<div style='background:#fffdf8; border:1px solid #e6dfd3; border-left:4px solid #c2410c; border-radius:10px; padding:14px 16px; margin-bottom:14px;'>", unsafe_allow_html=True)
        st.markdown("**📋 BESPRECHUNG**")
        col1, col2 = st.columns(2)
        with col1:
            b_thema = st.text_input("Thema *", placeholder="z.B. Lieferantengespräch")
            b_teilnehmer = st.text_input("Teilnehmer", placeholder="z.B. Müller, Schmidt")
        with col2:
            b_datum = st.date_input("Datum", value=date.today(), key="b_datum")
            b_ordner = st.selectbox("Ordner", st.session_state.ordner_liste, key="b_ordner")
        st.markdown("</div>", unsafe_allow_html=True)
        
        b_inhalt = st.text_area("Inhalt / Protokoll", height=250,
                                placeholder="Besprochene Punkte, Beschlüsse, Maßnahmen...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Speichern", type="primary", use_container_width=True, key="save_besprechung"):
                if b_thema:
                    neue_notiz = {
                        "id": naechste_id(st.session_state.notizen),
                        "vorlage": "besprechung",
                        "titel": f"Besprechung: {b_thema}",
                        "thema": b_thema,
                        "teilnehmer": b_teilnehmer,
                        "datum": str(b_datum),
                        "inhalt": b_inhalt,
                        "ordner": b_ordner,
                        "tags": [],
                        "erstellt": datetime.now().isoformat(),
                        "geaendert": datetime.now().isoformat()
                    }
                    st.session_state.notizen.insert(0, neue_notiz)
                    speichere_notizen(st.session_state.notizen)
                    st.session_state.sel_notiz_id = neue_notiz["id"]
                    st.session_state.zeige_neu_notiz = False
                    st.success("Besprechungsnotiz gespeichert!")
                    st.rerun()
        with col2:
            if st.button("Abbrechen", use_container_width=True, key="cancel_besprechung"):
                st.session_state.zeige_neu_notiz = False
                st.session_state.notiz_vorlage = None
                st.rerun()

    # ─── Neue Notiz: Kurznotiz ─────────────────────────────────
    elif st.session_state.zeige_neu_notiz and st.session_state.notiz_vorlage == "kurznotiz":
        st.markdown("### ⚡ Neue Kurznotiz")
        
        k_farbe = st.selectbox("🎨 Farbe", list(KURZNOTIZ_FARBEN.keys()), key="k_farbe")
        farbe_bg = KURZNOTIZ_FARBEN[k_farbe]
        
        st.markdown(f"""
        <div style='background:{farbe_bg}; border:1px solid #e6dfd3; border-radius:12px; 
             padding:14px 16px; margin-bottom:10px;'>
            <div style='font-size:0.75rem; color:#6b6258; font-weight:600;'>
                NOTIZ · {date.today().strftime("%d.%m.%Y")}
            </div>
        </div>""", unsafe_allow_html=True)
        
        k_inhalt = st.text_area("Gedanke / Idee *", height=120,
                                placeholder="Schnell notieren was nicht vergessen werden soll...")
        
        col1, col2 = st.columns(2)
        with col1:
            k_erinnerung = st.checkbox("⏰ Erinnerung setzen")
        with col2:
            k_ordner = st.selectbox("Ordner", st.session_state.ordner_liste, key="k_ordner")
        
        if k_erinnerung:
            k_erinnerung_datum = st.date_input("Erinnerung am", value=date.today(), key="k_erinnerung_datum")
            k_erinnerung_uhrzeit = st.time_input("Uhrzeit", key="k_uhrzeit")
        else:
            k_erinnerung_datum = None
            k_erinnerung_uhrzeit = None

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Speichern", type="primary", use_container_width=True, key="save_kurznotiz"):
                if k_inhalt:
                    neue_notiz = {
                        "id": naechste_id(st.session_state.notizen),
                        "vorlage": "kurznotiz",
                        "titel": k_inhalt[:40] + ("..." if len(k_inhalt) > 40 else ""),
                        "inhalt": k_inhalt,
                        "farbe": k_farbe,
                        "ordner": k_ordner,
                        "erinnerung": str(k_erinnerung_datum) if k_erinnerung_datum else None,
                        "erinnerung_uhrzeit": str(k_erinnerung_uhrzeit) if k_erinnerung_uhrzeit else None,
                        "tags": [],
                        "erstellt": datetime.now().isoformat(),
                        "geaendert": datetime.now().isoformat()
                    }
                    st.session_state.notizen.insert(0, neue_notiz)
                    speichere_notizen(st.session_state.notizen)
                    st.session_state.sel_notiz_id = neue_notiz["id"]
                    st.session_state.zeige_neu_notiz = False
                    st.success("Kurznotiz gespeichert!")
                    st.rerun()
        with col2:
            if st.button("Abbrechen", use_container_width=True, key="cancel_kurznotiz"):
                st.session_state.zeige_neu_notiz = False
                st.session_state.notiz_vorlage = None
                st.rerun()

    # ─── Neue Notiz: Allgemein ─────────────────────────────────
    elif st.session_state.zeige_neu_notiz and st.session_state.notiz_vorlage == "allgemein":
        st.markdown("### 📄 Neue Notiz")
        
        st.markdown("<div style='background:#fffdf8; border:1px solid #e6dfd3; border-left:4px solid #6b6258; border-radius:10px; padding:14px 16px; margin-bottom:14px;'>", unsafe_allow_html=True)
        st.markdown("**📄 NOTIZ**")
        col1, col2 = st.columns(2)
        with col1:
            a_thema = st.text_input("Thema *", placeholder="z.B. Projektidee")
            a_ordner = st.selectbox("Ordner", st.session_state.ordner_liste, key="a_ordner")
        with col2:
            a_datum = st.date_input("Datum", value=date.today(), key="a_datum")
            a_tags = st.multiselect("Tags", STANDARD_TAGS + st.session_state.ordner_liste, key="a_tags")
        st.markdown("</div>", unsafe_allow_html=True)
        
        a_inhalt = st.text_area("Inhalt *", height=250, placeholder="Notiz eingeben...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Speichern", type="primary", use_container_width=True, key="save_allgemein"):
                if a_thema and a_inhalt:
                    neue_notiz = {
                        "id": naechste_id(st.session_state.notizen),
                        "vorlage": "allgemein",
                        "titel": a_thema,
                        "thema": a_thema,
                        "datum": str(a_datum),
                        "inhalt": a_inhalt,
                        "ordner": a_ordner,
                        "tags": a_tags,
                        "erstellt": datetime.now().isoformat(),
                        "geaendert": datetime.now().isoformat()
                    }
                    st.session_state.notizen.insert(0, neue_notiz)
                    speichere_notizen(st.session_state.notizen)
                    st.session_state.sel_notiz_id = neue_notiz["id"]
                    st.session_state.zeige_neu_notiz = False
                    st.success("Notiz gespeichert!")
                    st.rerun()
        with col2:
            if st.button("Abbrechen", use_container_width=True, key="cancel_allgemein"):
                st.session_state.zeige_neu_notiz = False
                st.session_state.notiz_vorlage = None
                st.rerun()

    # ─── Notiz anzeigen / bearbeiten ───────────────────────────
    elif st.session_state.sel_notiz_id is not None:
        notiz = next((n for n in st.session_state.notizen 
                     if n["id"] == st.session_state.sel_notiz_id), None)
        
        if notiz:
            vorlage = notiz.get("vorlage", "allgemein")
            farbe_bg = KURZNOTIZ_FARBEN.get(notiz.get("farbe", ""), "#fffdf8")
            
            # Header je nach Vorlage
            if vorlage == "besprechung":
                st.markdown(f"""
                <div style='background:#fffdf8; border:1px solid #e6dfd3; border-left:4px solid #c2410c; 
                     border-radius:10px; padding:14px 16px; margin-bottom:14px;'>
                    <div style='font-weight:700; font-size:1rem; color:#c2410c;'>📋 BESPRECHUNG</div>
                    <div style='font-size:0.88rem; margin-top:4px;'>
                        <b>Thema:</b> {notiz.get("thema", "")} &nbsp;|&nbsp; 
                        <b>Teilnehmer:</b> {notiz.get("teilnehmer", "")} &nbsp;|&nbsp;
                        <b>Datum:</b> {notiz.get("datum", "")}
                    </div>
                </div>""", unsafe_allow_html=True)
            
            elif vorlage == "kurznotiz":
                st.markdown(f"""
                <div style='background:{farbe_bg}; border:1px solid #e6dfd3; border-radius:12px; 
                     padding:10px 14px; margin-bottom:10px;'>
                    <div style='font-size:0.75rem; color:#6b6258; font-weight:600;'>
                        ⚡ KURZNOTIZ · {notiz.get("datum", date.today().strftime("%Y-%m-%d"))}
                        {f"&nbsp;|&nbsp; ⏰ Erinnerung: {notiz.get('erinnerung', '')}" if notiz.get("erinnerung") else ""}
                    </div>
                </div>""", unsafe_allow_html=True)
            
            else:
                st.markdown(f"""
                <div style='background:#fffdf8; border:1px solid #e6dfd3; border-left:4px solid #6b6258; 
                     border-radius:10px; padding:10px 14px; margin-bottom:10px;'>
                    <div style='font-size:0.75rem; color:#6b6258; font-weight:600;'>
                        📄 NOTIZ · {notiz.get("datum", "")} · {notiz.get("thema", "")}
                    </div>
                </div>""", unsafe_allow_html=True)

            # Titel bearbeiten
            edit_titel = st.text_input("Titel", value=notiz.get("titel", ""), key="edit_notiz_titel")
            
            # Ordner & Tags
            col1, col2 = st.columns(2)
            with col1:
                edit_ordner = st.selectbox("Ordner", st.session_state.ordner_liste,
                    index=st.session_state.ordner_liste.index(notiz.get("ordner", "00 Eingang")) 
                    if notiz.get("ordner") in st.session_state.ordner_liste else 0,
                    key="edit_notiz_ordner")
            with col2:
                edit_tags = st.multiselect("Tags", STANDARD_TAGS + st.session_state.ordner_liste,
                    default=notiz.get("tags", []), key="edit_notiz_tags")
            
            # Inhalt bearbeiten
            edit_inhalt = st.text_area("Inhalt", value=notiz.get("inhalt", ""), 
                                       height=300, key="edit_notiz_inhalt")
            
            # Aktionsbuttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("💾 Speichern", type="primary", use_container_width=True, key="save_edit_notiz"):
                    notiz["titel"] = edit_titel
                    notiz["inhalt"] = edit_inhalt
                    notiz["ordner"] = edit_ordner
                    notiz["tags"] = edit_tags
                    notiz["geaendert"] = datetime.now().isoformat()
                    speichere_notizen(st.session_state.notizen)
                    st.success("Gespeichert!")
                    st.rerun()
            with col2:
                # Drucken als PDF Export
                    druck_text = f"""TITEL: {notiz.get('titel', '')}
DATUM: {notiz.get('datum', '')}
ORDNER: {notiz.get('ordner', '')}

{notiz.get('inhalt', '')}"""
                    st.download_button("🖨️ Als PDF/Drucken", 
                        data=druck_text.encode('utf-8'),
                        file_name=f"{notiz.get('titel', 'notiz')}.txt",
                        mime="text/plain",
                        use_container_width=True, 
                        key="print_notiz")
            with col3:
                # Als TXT herunterladen
                export_text = f"Titel: {notiz.get('titel', '')}\n"
                export_text += f"Datum: {notiz.get('datum', '')}\n"
                export_text += f"Ordner: {notiz.get('ordner', '')}\n\n"
                export_text += notiz.get("inhalt", "")
                st.download_button("📤 Teilen", data=export_text,
                    file_name=f"{notiz.get('titel', 'notiz')}.txt",
                    mime="text/plain", use_container_width=True, key="share_notiz")
            with col4:
                if st.button("🗑️ Löschen", use_container_width=True, key="del_notiz"):
                    st.session_state.notizen = [n for n in st.session_state.notizen 
                                               if n["id"] != st.session_state.sel_notiz_id]
                    speichere_notizen(st.session_state.notizen)
                    st.session_state.sel_notiz_id = None
                    st.rerun()
            
            # KI Funktionen
            st.markdown("<div style='background:#faf7f0; border:1px solid #e6dfd3; border-radius:12px; padding:14px; margin-top:14px;'>", unsafe_allow_html=True)
            st.markdown("**🤖 KI-Funktionen**")
            ki = lade_ki()
            if not ki.hat_api_key():
                st.warning("⚠️ Kein API-Key hinterlegt. Bitte unter ⚙️ Einstellungen eintragen.")
            else:
                col_ki1, col_ki2, col_ki3, col_ki4 = st.columns(4)
                with col_ki1:
                    if st.button("✨ Formatieren", use_container_width=True, key="ki_format"):
                        with st.spinner("KI formatiert..."):
                            inhalt = document.getElementById if False else edit_inhalt
                            ergebnis, fehler = ki.ki_formatieren(edit_inhalt)
                            if ergebnis:
                                st.session_state["ki_ergebnis"] = ergebnis
                                st.session_state["ki_modus"] = "format"
                            else:
                                st.error(fehler)
                with col_ki2:
                    if st.button("📋 Zusammenfassen", use_container_width=True, key="ki_summary"):
                        with st.spinner("KI zusammenfasst..."):
                            ergebnis, fehler = ki.ki_zusammenfassen(edit_inhalt)
                            if ergebnis:
                                st.session_state["ki_ergebnis"] = ergebnis
                                st.session_state["ki_modus"] = "summary"
                            else:
                                st.error(fehler)
                with col_ki3:
                    if st.button("✅ To-dos finden", use_container_width=True, key="ki_tasks"):
                        with st.spinner("KI sucht Aufgaben..."):
                            ergebnis, fehler = ki.ki_aufgaben_extrahieren(edit_inhalt)
                            if ergebnis:
                                st.session_state["ki_ergebnis"] = ergebnis
                                st.session_state["ki_modus"] = "tasks"
                            else:
                                st.error(fehler)
                with col_ki4:
                    if st.button("🔤 Korrigieren", use_container_width=True, key="ki_grammar"):
                        with st.spinner("KI korrigiert..."):
                            ergebnis, fehler = ki.ki_korrigieren(edit_inhalt)
                            if ergebnis:
                                st.session_state["ki_ergebnis"] = ergebnis
                                st.session_state["ki_modus"] = "grammar"
                            else:
                                st.error(fehler)
                
                # KI Ergebnis anzeigen
                if "ki_ergebnis" in st.session_state and st.session_state.get("ki_modus"):
                    modus = st.session_state["ki_modus"]
                    ergebnis = st.session_state["ki_ergebnis"]
                    
                    if modus == "tasks":
                        try:
                            aufgaben = json.loads(ergebnis.replace("\","").strip())
                            st.markdown("**Gefundene To-dos:**")
                            for i, a in enumerate(aufgaben):
                                col_a, col_d = st.columns([3,1])
                                with col_a:
                                    st.text(a.get("text",""))
                                with col_d:
                                    st.text(a.get("datum","") or "kein Datum")
                            if st.button("📅 Alle in Planer übernehmen", type="primary", key="ki_tasks_add"):
                                aufgaben_file = "data/aufgaben.json"
                                bestehende = []
                                if os.path.exists(aufgaben_file):
                                    with open(aufgaben_file, "r", encoding="utf-8") as f:
                                        bestehende = json.load(f)
                                naechste = max([a["id"] for a in bestehende], default=0) + 1
                                for a in aufgaben:
                                    bestehende.append({
                                        "id": naechste,
                                        "text": a.get("text",""),
                                        "datum": a.get("datum") or str(date.today()),
                                        "erledigt": False,
                                        "typ": "normal",
                                        "erstellt": str(date.today())
                                    })
                                    naechste += 1
                                with open(aufgaben_file, "w", encoding="utf-8") as f:
                                    json.dump(bestehende, f, ensure_ascii=False, indent=2)
                                st.success(f"{len(aufgaben)} Aufgaben in den Planer übernommen!")
                                del st.session_state["ki_ergebnis"]
                                del st.session_state["ki_modus"]
                        except:
                            st.markdown(ergebnis)
                    elif modus in ["format", "grammar"]:
                        st.markdown("**KI-Ergebnis:**")
                        st.text_area("Ergebnis", value=ergebnis, height=150, key="ki_result_text")
                        if st.button("✅ In Notiz übernehmen", type="primary", key="ki_apply"):
                            notiz["inhalt"] = ergebnis
                            notiz["geaendert"] = datetime.now().isoformat()
                            speichere_notizen(st.session_state.notizen)
                            del st.session_state["ki_ergebnis"]
                            del st.session_state["ki_modus"]
                            st.success("Übernommen!")
                            st.rerun()
                    else:
                        st.markdown("**Zusammenfassung:**")
                        st.info(ergebnis)
                        if st.button("✖️ Schließen", key="ki_close"):
                            del st.session_state["ki_ergebnis"]
                            del st.session_state["ki_modus"]
                            st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Leer-Zustand
        st.markdown("""
        <div style='background:#fffdf8; border:1px solid #e6dfd3; border-radius:14px; 
             padding:40px; text-align:center; color:#6b6258;'>
            <div style='font-size:2.5rem; margin-bottom:12px;'>📝</div>
            <div style='font-weight:600; font-size:1rem; margin-bottom:6px;'>Keine Notiz ausgewählt</div>
            <div style='font-size:0.88rem;'>Wähle links eine Notiz oder erstelle eine neue.</div>
        </div>""", unsafe_allow_html=True)
