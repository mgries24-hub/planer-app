import streamlit as st
from datetime import datetime, date, timedelta
import json
import os
import base64

# ─── Daten laden/speichern ─────────────────────────────────────
import os
def get_data_base():
    onedrive = os.path.join(os.path.expanduser("~"), "OneDrive - Gries Schleiftechnik GmbH & Co. KG", "Dokumente - Gries DMS", "01_PlanerApp")
    return onedrive if os.path.exists(onedrive) else "data"
DATA_BASE = get_data_base()
Rechnungen_DIR = os.path.join(DATA_BASE, "Rechnungen")
os.makedirs(Rechnungen_DIR, exist_ok=True)
RECHNUNGEN_FILE = os.path.join(Rechnungen_DIR, "rechnungen.json")
LIEFERANTEN_FILE = os.path.join(Rechnungen_DIR, "lieferanten.json")
PDF_ORDNER = os.path.join(Rechnungen_DIR, "PDFs")

def lade_rechnungen():
    if os.path.exists(RECHNUNGEN_FILE):
        with open(RECHNUNGEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def speichere_rechnungen(rechnungen):
    os.makedirs("data", exist_ok=True)
    with open(RECHNUNGEN_FILE, "w", encoding="utf-8") as f:
        json.dump(rechnungen, f, ensure_ascii=False, indent=2)

def lade_lieferanten():
    if os.path.exists(LIEFERANTEN_FILE):
        with open(LIEFERANTEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def speichere_lieferanten(lieferanten):
    os.makedirs("data", exist_ok=True)
    with open(LIEFERANTEN_FILE, "w", encoding="utf-8") as f:
        json.dump(lieferanten, f, ensure_ascii=False, indent=2)

def speichere_aufgabe_rechnung(rechnung):
    """Erstellt automatisch eine rote Aufgabe im Planer"""
    aufgaben_file = "data/aufgaben.json"
    aufgaben = []
    if os.path.exists(aufgaben_file):
        with open(aufgaben_file, "r", encoding="utf-8") as f:
            aufgaben = json.load(f)
    
    # Prüfen ob schon eine Aufgabe für diese Rechnung existiert
    bestehend = [a for a in aufgaben if a.get("rechnung_id") == rechnung["id"]]
    if bestehend:
        # Aktualisieren
        for a in bestehend:
            a["datum"] = rechnung["zahldatum"]
            a["text"] = f"💳 Rechnung bezahlen: {rechnung['lieferant']} ({rechnung['re_nummer']})"
    else:
        # Neu erstellen
        neue_id = max([a["id"] for a in aufgaben], default=0) + 1
        aufgaben.append({
            "id": neue_id,
            "text": f"💳 Rechnung bezahlen: {rechnung['lieferant']} ({rechnung['re_nummer']})",
            "datum": rechnung["zahldatum"],
            "erledigt": rechnung.get("status") == "bezahlt",
            "typ": "rechnung",
            "rechnung_id": rechnung["id"],
            "notiz": f"Betrag: {rechnung.get('betrag', '')} €",
            "erstellt": str(date.today())
        })
    
    with open(aufgaben_file, "w", encoding="utf-8") as f:
        json.dump(aufgaben, f, ensure_ascii=False, indent=2)

def naechste_id(liste):
    if not liste:
        return 1
    return max(x["id"] for x in liste) + 1

# ─── Session State ─────────────────────────────────────────────
if "rechnungen" not in st.session_state:
    st.session_state.rechnungen = lade_rechnungen()
if "lieferanten" not in st.session_state:
    st.session_state.lieferanten = lade_lieferanten()
if "sel_rechnung_id" not in st.session_state:
    st.session_state.sel_rechnung_id = None
if "zeige_neu_rechnung" not in st.session_state:
    st.session_state.zeige_neu_rechnung = False
if "zeige_lieferanten" not in st.session_state:
    st.session_state.zeige_lieferanten = False
if "re_filter" not in st.session_state:
    st.session_state.re_filter = "Alle"

# ─── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    .re-card {
        background: #fffdf8; border: 1px solid #e6dfd3; border-radius: 11px;
        padding: 12px 14px; margin-bottom: 8px;
    }
    .re-card.offen { border-left: 4px solid #dc2626; }
    .re-card.bezahlt { border-left: 4px solid #5a7a52; opacity: 0.8; }
    .re-card.sel { border-color: #c2410c; background: #fef0e6; }
    .badge-offen {
        background: #fee2e2; color: #dc2626; padding: 3px 10px;
        border-radius: 20px; font-size: 0.75rem; font-weight: 600;
    }
    .badge-bezahlt {
        background: #dcfce7; color: #166534; padding: 3px 10px;
        border-radius: 20px; font-size: 0.75rem; font-weight: 600;
    }
    .re-header {
        background: #fffdf8; border: 1px solid #e6dfd3; border-left: 4px solid #dc2626;
        border-radius: 10px; padding: 14px 16px; margin-bottom: 16px;
    }
    .pdf-viewer {
        border: 1px solid #e6dfd3; border-radius: 10px; overflow: hidden;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────
heute = datetime.now()
heute_str = heute.strftime("%A, %d. %B %Y")
kw = heute.isocalendar()[1]

st.markdown(f"""
<div style='background: linear-gradient(135deg, #2b2018, #3d2c1d); border-radius: 14px;
     padding: 22px 26px; margin-bottom: 20px;'>
    <h1 style='margin:0; font-size:1.8rem; color:#fbf6ee;'>📄 Rechnungen</h1>
    <p style='margin:6px 0 0; font-size:0.82rem; color:#bfae9a; text-transform:uppercase; letter-spacing:0.04em;'>
        {heute_str} · KW {kw}</p>
</div>""", unsafe_allow_html=True)

# ─── Übersicht Metriken ────────────────────────────────────────
rechnungen = st.session_state.rechnungen
offen = [r for r in rechnungen if r.get("status") == "offen"]
bezahlt = [r for r in rechnungen if r.get("status") == "bezahlt"]
summe_offen = sum(float(r.get("betrag", 0)) for r in offen)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div style='background:#fee2e2; border:1px solid #fca5a5; border-radius:12px; 
        padding:16px; text-align:center;'>
        <div style='font-size:1.8rem; font-weight:700; color:#dc2626;'>{len(offen)}</div>
        <div style='font-size:0.82rem; color:#991b1b;'>Offene Rechnungen</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div style='background:#dcfce7; border:1px solid #86efac; border-radius:12px; 
        padding:16px; text-align:center;'>
        <div style='font-size:1.8rem; font-weight:700; color:#166534;'>{len(bezahlt)}</div>
        <div style='font-size:0.82rem; color:#166534;'>Bezahlte Rechnungen</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div style='background:#fff7ed; border:1px solid #fdba74; border-radius:12px; 
        padding:16px; text-align:center;'>
        <div style='font-size:1.8rem; font-weight:700; color:#c2410c;'>{summe_offen:,.2f} €</div>
        <div style='font-size:0.82rem; color:#9a3412;'>Offener Betrag</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Aktionsbuttons ────────────────────────────────────────────
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    if st.button("➕ Neue Rechnung erfassen", type="primary", use_container_width=True):
        st.session_state.zeige_neu_rechnung = True
        st.session_state.sel_rechnung_id = None
        st.rerun()
with col2:
    if st.button("👥 Lieferanten verwalten", use_container_width=True):
        st.session_state.zeige_lieferanten = not st.session_state.zeige_lieferanten
        st.rerun()
with col3:
    filter_opt = st.selectbox("Filter", ["Alle", "Offen", "Bezahlt"], 
                               key="re_filter_select",
                               index=["Alle", "Offen", "Bezahlt"].index(st.session_state.re_filter))
    if filter_opt != st.session_state.re_filter:
        st.session_state.re_filter = filter_opt
        st.rerun()

# ─── Lieferanten verwalten ─────────────────────────────────────
if st.session_state.zeige_lieferanten:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 👥 Lieferantendatenbank")
    
    col_l, col_r = st.columns([1, 2])
    with col_l:
        st.markdown("**Neuen Lieferanten anlegen:**")
        l_name = st.text_input("Firmenname *", key="l_name")
        l_iban = st.text_input("IBAN", key="l_iban", placeholder="DE00 0000 0000 0000 0000 00")
        l_email = st.text_input("E-Mail", key="l_email")
        l_telefon = st.text_input("Telefon", key="l_telefon")
        
        if st.button("💾 Lieferant speichern", type="primary", key="save_lieferant"):
            if l_name:
                neuer = {
                    "id": naechste_id(st.session_state.lieferanten),
                    "name": l_name,
                    "iban": l_iban,
                    "email": l_email,
                    "telefon": l_telefon,
                    "erstellt": str(date.today())
                }
                st.session_state.lieferanten.append(neuer)
                speichere_lieferanten(st.session_state.lieferanten)
                st.success(f"Lieferant '{l_name}' gespeichert!")
                st.rerun()
    
    with col_r:
        if st.session_state.lieferanten:
            for lief in st.session_state.lieferanten:
                lief_rechnungen = [r for r in rechnungen if r.get("lieferant") == lief["name"]]
                lief_offen = len([r for r in lief_rechnungen if r.get("status") == "offen"])
                st.markdown(f"""
                <div style='background:#fffdf8; border:1px solid #e6dfd3; border-radius:10px; 
                     padding:12px 16px; margin-bottom:8px;'>
                    <div style='font-weight:600;'>{lief["name"]}</div>
                    <div style='font-size:0.8rem; color:#6b6258;'>
                        IBAN: {lief.get("iban", "—")} &nbsp;|&nbsp; 
                        {lief_offen} offene Rechnung(en)
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Noch keine Lieferanten angelegt.")
    
    st.markdown("---")

# ─── Neue Rechnung erfassen ────────────────────────────────────
if st.session_state.zeige_neu_rechnung:
    st.markdown("### ➕ Neue Rechnung erfassen")
    
    with st.container():
        st.markdown("<div style='background:#fffdf8; border:1px solid #e6dfd3; border-left:4px solid #dc2626; border-radius:12px; padding:20px; margin-bottom:16px;'>", unsafe_allow_html=True)
        
        # PDF Upload
        uploaded_pdf = st.file_uploader("📎 PDF hochladen", type=["pdf"], key="pdf_upload")
        
        if uploaded_pdf:
            st.success(f"✅ {uploaded_pdf.name} hochgeladen")
            st.info("💡 KI-Texterkennung wird in Phase 6 mit Claude API eingebunden. Bitte Felder manuell ausfüllen.")
        
        col1, col2 = st.columns(2)
        with col1:
            # Lieferant aus Datenbank oder neu
            lieferanten_namen = [l["name"] for l in st.session_state.lieferanten]
            lieferanten_optionen = ["— Neu eingeben —"] + lieferanten_namen
            lief_auswahl = st.selectbox("Lieferant", lieferanten_optionen, key="re_lief_sel")
            
            if lief_auswahl == "— Neu eingeben —":
                re_lieferant = st.text_input("Lieferant Name *", key="re_lief_neu")
            else:
                re_lieferant = lief_auswahl
            
            re_nummer = st.text_input("Rechnungs-Nr. *", placeholder="z.B. RE-2026-001", key="re_nummer")
            re_betrag = st.number_input("Betrag (€) *", min_value=0.0, step=0.01, key="re_betrag")

        with col2:
            re_datum = st.date_input("RE-Datum *", value=date.today(), key="re_datum")
            
            # Zahldatum automatisch berechnen
            zahldatum_auto = re_datum + timedelta(days=30)
            re_zahldatum = st.date_input(
                "Zu zahlen am (30 Tage netto)", 
                value=zahldatum_auto, 
                key="re_zahldatum",
                help="Automatisch berechnet: RE-Datum + 30 Tage. Kann manuell angepasst werden (z.B. für Skonto)."
            )
            
            re_status = st.selectbox("Status", ["offen", "bezahlt"], key="re_status")
        
        re_notiz = st.text_area("Notiz zur Rechnung", 
                                placeholder="z.B. von Privat bezahlt, Skonto genutzt, ...",
                                height=80, key="re_notiz")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Rechnung speichern", type="primary", use_container_width=True, key="save_rechnung"):
                lief_final = re_lieferant if lief_auswahl == "— Neu eingeben —" else lief_auswahl
                if lief_final and re_nummer:
                    # PDF speichern
                    pdf_pfad = None
                    if uploaded_pdf:
                        os.makedirs(PDF_ORDNER, exist_ok=True)
                        pdf_pfad = f"{PDF_ORDNER}/{re_nummer.replace('/', '-')}_{uploaded_pdf.name}"
                        with open(pdf_pfad, "wb") as f:
                            f.write(uploaded_pdf.getbuffer())
                    
                    neue_re = {
                        "id": naechste_id(st.session_state.rechnungen),
                        "lieferant": lief_final,
                        "re_nummer": re_nummer,
                        "betrag": re_betrag,
                        "re_datum": str(re_datum),
                        "zahldatum": str(re_zahldatum),
                        "status": re_status,
                        "notiz": re_notiz,
                        "pdf_pfad": pdf_pfad,
                        "erstellt": str(date.today())
                    }
                    
                    st.session_state.rechnungen.append(neue_re)
                    speichere_rechnungen(st.session_state.rechnungen)
                    
                    # Lieferant automatisch speichern falls neu
                    if lief_auswahl == "— Neu eingeben —" and lief_final:
                        if not any(l["name"] == lief_final for l in st.session_state.lieferanten):
                            st.session_state.lieferanten.append({
                                "id": naechste_id(st.session_state.lieferanten),
                                "name": lief_final,
                                "iban": "",
                                "email": "",
                                "telefon": "",
                                "erstellt": str(date.today())
                            })
                            speichere_lieferanten(st.session_state.lieferanten)
                    
                    # Aufgabe im Planer erstellen
                    if re_status == "offen":
                        speichere_aufgabe_rechnung(neue_re)
                    
                    st.session_state.sel_rechnung_id = neue_re["id"]
                    st.session_state.zeige_neu_rechnung = False
                    st.success(f"✅ Rechnung gespeichert! Aufgabe im Planer erstellt.")
                    st.rerun()
        with col2:
            if st.button("Abbrechen", use_container_width=True, key="cancel_rechnung"):
                st.session_state.zeige_neu_rechnung = False
                st.rerun()

# ─── Rechnungsliste + Detail ───────────────────────────────────
else:
    col_links, col_rechts = st.columns([1, 2])
    
    with col_links:
        st.markdown("### 📋 Rechnungen")
        
        re_liste = st.session_state.rechnungen
        if st.session_state.re_filter == "Offen":
            re_liste = [r for r in re_liste if r.get("status") == "offen"]
        elif st.session_state.re_filter == "Bezahlt":
            re_liste = [r for r in re_liste if r.get("status") == "bezahlt"]
        
        re_liste = sorted(re_liste, key=lambda x: x.get("zahldatum", ""), reverse=False)
        
        if not re_liste:
            st.markdown("<p style='color:#6b6258; font-style:italic;'>Keine Rechnungen vorhanden.</p>", unsafe_allow_html=True)
        
        for re in re_liste:
            ist_offen = re.get("status") == "offen"
            aktiv = re["id"] == st.session_state.sel_rechnung_id
            
            border_farbe = "#c2410c" if aktiv else ("#dc2626" if ist_offen else "#5a7a52")
            bg = "#fef0e6" if aktiv else ("#fff5f5" if ist_offen else "#f0fdf4")
            
            zahldatum = date.fromisoformat(re.get("zahldatum", str(date.today())))
            tage_bis = (zahldatum - date.today()).days
            
            if ist_offen and tage_bis < 0:
                warnung = f"⚠️ {abs(tage_bis)} Tage überfällig!"
                warnung_farbe = "#dc2626"
            elif ist_offen and tage_bis <= 5:
                warnung = f"⏰ In {tage_bis} Tagen fällig"
                warnung_farbe = "#d97706"
            else:
                warnung = ""
                warnung_farbe = ""
            
            st.markdown(f"""
            <div style='background:{bg}; border:1px solid {border_farbe}; border-left:4px solid {border_farbe};
                 border-radius:11px; padding:12px 14px; margin-bottom:8px;'>
                <div style='font-weight:600; font-size:0.92rem;'>{re["lieferant"]}</div>
                <div style='font-size:0.78rem; color:#6b6258;'>
                    {re["re_nummer"]} · {re.get("betrag", 0):,.2f} €
                </div>
                <div style='font-size:0.74rem; color:#6b6258;'>
                    Zahlung: {zahldatum.strftime("%d.%m.%Y")}
                    {"&nbsp; <span style='color:" + warnung_farbe + ";'>" + warnung + "</span>" if warnung else ""}
                </div>
                <div style='margin-top:4px;'>
                    <span class='{"badge-offen" if ist_offen else "badge-bezahlt"}'>
                        {"Offen" if ist_offen else "Bezahlt"}
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)
            
            if st.button("Öffnen", key=f"open_re_{re['id']}", use_container_width=True):
                st.session_state.sel_rechnung_id = re["id"]
                st.rerun()
    
    with col_rechts:
        if st.session_state.sel_rechnung_id:
            re = next((r for r in st.session_state.rechnungen 
                      if r["id"] == st.session_state.sel_rechnung_id), None)
            
            if re:
                ist_offen = re.get("status") == "offen"
                
                st.markdown(f"""
                <div style='background:#fffdf8; border:1px solid #e6dfd3; 
                     border-left:4px solid {"#dc2626" if ist_offen else "#5a7a52"};
                     border-radius:10px; padding:14px 16px; margin-bottom:16px;'>
                    <div style='font-weight:700; font-size:1.1rem;'>📄 {re["lieferant"]}</div>
                    <div style='font-size:0.88rem; margin-top:6px; color:#6b6258;'>
                        RE-Nr: <b style='color:#26201a;'>{re["re_nummer"]}</b> &nbsp;|&nbsp;
                        Betrag: <b style='color:#c2410c;'>{re.get("betrag", 0):,.2f} €</b> &nbsp;|&nbsp;
                        Status: <span class='{"badge-offen" if ist_offen else "badge-bezahlt"}'>
                            {"Offen" if ist_offen else "Bezahlt"}</span>
                    </div>
                    <div style='font-size:0.85rem; margin-top:4px; color:#6b6258;'>
                        RE-Datum: {re.get("re_datum", "")} &nbsp;|&nbsp;
                        Zahlung bis: <b style='color:{"#dc2626" if ist_offen else "#5a7a52"};'>{re.get("zahldatum", "")}</b>
                    </div>
                </div>""", unsafe_allow_html=True)
                
                # Felder bearbeiten
                col1, col2 = st.columns(2)
                with col1:
                    edit_zahldatum = st.date_input("Zahldatum anpassen", 
                        value=date.fromisoformat(re.get("zahldatum", str(date.today()))),
                        key="edit_zahldatum")
                    edit_status = st.selectbox("Status", ["offen", "bezahlt"],
                        index=0 if re.get("status") == "offen" else 1,
                        key="edit_re_status")
                with col2:
                    edit_betrag = st.number_input("Betrag (€)", 
                        value=float(re.get("betrag", 0)),
                        step=0.01, key="edit_re_betrag")
                    edit_notiz = st.text_input("Notiz", 
                        value=re.get("notiz", ""), key="edit_re_notiz")
                
                # Aktionsbuttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("💾 Speichern", type="primary", use_container_width=True, key="save_re_edit"):
                        re["zahldatum"] = str(edit_zahldatum)
                        re["status"] = edit_status
                        re["betrag"] = edit_betrag
                        re["notiz"] = edit_notiz
                        speichere_rechnungen(st.session_state.rechnungen)
                        # Planer-Aufgabe aktualisieren
                        speichere_aufgabe_rechnung(re)
                        st.success("Gespeichert!")
                        st.rerun()
                with col2:
                    # Export
                    export = f"Rechnung: {re['re_nummer']}\nLieferant: {re['lieferant']}\nBetrag: {re.get('betrag', 0)} EUR\nRE-Datum: {re.get('re_datum', '')}\nZahlung bis: {re.get('zahldatum', '')}\nStatus: {re.get('status', '')}\nNotiz: {re.get('notiz', '')}"
                    st.download_button("📤 Exportieren", data=export,
                        file_name=f"RE_{re['re_nummer']}.txt",
                        mime="text/plain", use_container_width=True, key="export_re")
                with col3:
                    if st.button("🗑️ Löschen", use_container_width=True, key="del_re"):
                        st.session_state.rechnungen = [r for r in st.session_state.rechnungen 
                                                       if r["id"] != st.session_state.sel_rechnung_id]
                        speichere_rechnungen(st.session_state.rechnungen)
                        st.session_state.sel_rechnung_id = None
                        st.rerun()
                
                # PDF anzeigen
                if re.get("pdf_pfad") and os.path.exists(re["pdf_pfad"]):
                    st.markdown("### 📎 Rechnung PDF")
                    with open(re["pdf_pfad"], "rb") as f:
                        pdf_bytes = f.read()
                    b64 = base64.b64encode(pdf_bytes).decode()
                    st.markdown(f"""
                    <div class='pdf-viewer'>
                        <iframe src="data:application/pdf;base64,{b64}" 
                                width="100%" height="600px" type="application/pdf">
                        </iframe>
                    </div>""", unsafe_allow_html=True)
                elif re.get("pdf_pfad"):
                    st.info("PDF nicht gefunden. Möglicherweise wurde die Datei verschoben.")
                
                # Notiz anzeigen
                if re.get("notiz"):
                    st.markdown(f"""
                    <div style='background:#fef9c3; border:1px solid #fde047; border-radius:10px; 
                         padding:12px 16px; margin-top:12px;'>
                        <div style='font-size:0.8rem; font-weight:600; color:#854d0e;'>📝 NOTIZ</div>
                        <div style='margin-top:4px;'>{re["notiz"]}</div>
                    </div>""", unsafe_allow_html=True)
        
        else:
            st.markdown("""
            <div style='background:#fffdf8; border:1px solid #e6dfd3; border-radius:14px; 
                 padding:40px; text-align:center; color:#6b6258;'>
                <div style='font-size:2.5rem; margin-bottom:12px;'>📄</div>
                <div style='font-weight:600; font-size:1rem; margin-bottom:6px;'>Keine Rechnung ausgewählt</div>
                <div style='font-size:0.88rem;'>Wähle links eine Rechnung oder erfasse eine neue.</div>
            </div>""", unsafe_allow_html=True)
