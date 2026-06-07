import streamlit as st
from datetime import datetime, date, timedelta
import json
import os

# ─── Daten laden/speichern ─────────────────────────────────────
import os
def get_data_base():
    onedrive = os.path.join(os.path.expanduser("~"), "OneDrive - Gries Schleiftechnik GmbH & Co. KG", "Dokumente - Gries DMS", "01_PlanerApp")
    return onedrive if os.path.exists(onedrive) else "data"
DATA_BASE = get_data_base()
DATA_FILE = os.path.join(DATA_BASE, "Aufgaben", "aufgaben.json")

def lade_aufgaben():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def speichere_aufgaben(aufgaben):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(aufgaben, f, ensure_ascii=False, indent=2)

def naechste_id(aufgaben):
    if not aufgaben:
        return 1
    return max(a["id"] for a in aufgaben) + 1

# ─── Session State ─────────────────────────────────────────────
if "aufgaben" not in st.session_state:
    st.session_state.aufgaben = lade_aufgaben()
if "zeige_neu" not in st.session_state:
    st.session_state.zeige_neu = False
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None
if "kalender_tag" not in st.session_state:
    st.session_state.kalender_tag = None
if "ansicht" not in st.session_state:
    st.session_state.ansicht = "Woche"

# ─── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f4f1ea; }

    .aufgabe-card {
        background: #fffdf8;
        border: 1px solid #e6dfd3;
        border-radius: 11px;
        padding: 12px 16px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .aufgabe-card.erledigt {
        opacity: 0.6;
        text-decoration: line-through;
    }
    .aufgabe-card.rechnung {
        border-left: 4px solid #dc2626;
        background: #fff5f5;
    }

    .tag-card {
        background: #fffdf8;
        border: 1px solid #e6dfd3;
        border-radius: 9px;
        padding: 8px;
        min-height: 90px;
        margin-bottom: 4px;
    }
    .tag-card.heute {
        border-color: #c2410c;
        background: #fef0e6;
    }
    .tag-header {
        font-size: 0.78rem;
        font-weight: 600;
        color: #6b6258;
        border-bottom: 1px solid #e6dfd3;
        padding-bottom: 4px;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
    }
    .tag-header.heute-header { color: #c2410c; }

    .aufgabe-tag {
        font-size: 0.72rem;
        background: #fffdf8;
        border-left: 3px solid #b08968;
        padding: 3px 6px;
        border-radius: 4px;
        margin: 2px 0;
        line-height: 1.3;
    }
    .aufgabe-tag.erledigt {
        border-left-color: #5a7a52;
        color: #6b6258;
        text-decoration: line-through;
        opacity: 0.7;
    }
    .aufgabe-tag.rechnung {
        border-left-color: #dc2626;
        background: #fff5f5;
    }

    .woche-header {
        background: #faf7f0;
        border: 1px solid #e6dfd3;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        font-weight: 600;
        color: #26201a;
    }

    .badge-offen {
        background: #fef0e6;
        color: #c2410c;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .badge-erledigt {
        background: #eef3ea;
        color: #5a7a52;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .badge-rechnung {
        background: #fff5f5;
        color: #dc2626;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────
heute = datetime.now()
heute_str = heute.strftime("%A, %d. %B %Y")
kw = heute.isocalendar()[1]

st.markdown(f"""
<div style='background: linear-gradient(135deg, #2b2018, #3d2c1d); border-radius: 14px;
     padding: 22px 26px; margin-bottom: 20px; color: #fbf6ee;'>
    <h1 style='margin:0; font-size:1.8rem; color:#fbf6ee;'>📅 Planer</h1>
    <p style='margin:6px 0 0; font-size:0.82rem; color:#bfae9a; text-transform:uppercase; letter-spacing:0.04em;'>
        {heute_str} · KW {kw}
    </p>
</div>
""", unsafe_allow_html=True)

# ─── Ansicht wählen ────────────────────────────────────────────
col_a, col_b, col_c, col_neu = st.columns([1, 1, 1, 2])
with col_a:
    if st.button("📆 Tag", use_container_width=True,
                 type="primary" if st.session_state.ansicht == "Tag" else "secondary"):
        st.session_state.ansicht = "Tag"
        st.rerun()
with col_b:
    if st.button("📅 Woche", use_container_width=True,
                 type="primary" if st.session_state.ansicht == "Woche" else "secondary"):
        st.session_state.ansicht = "Woche"
        st.rerun()
with col_c:
    if st.button("🗓️ Monat", use_container_width=True,
                 type="primary" if st.session_state.ansicht == "Monat" else "secondary"):
        st.session_state.ansicht = "Monat"
        st.rerun()
with col_neu:
    if st.button("➕ Neue Aufgabe", use_container_width=True, type="primary"):
        st.session_state.zeige_neu = not st.session_state.zeige_neu
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ─── Neue Aufgabe Formular ─────────────────────────────────────
if st.session_state.zeige_neu:
    with st.container():
        st.markdown("<div style='background:#fffdf8; border:1px solid #e6dfd3; border-radius:14px; padding:20px; margin-bottom:16px;'>", unsafe_allow_html=True)
        st.subheader("➕ Neue Aufgabe")
        col1, col2 = st.columns(2)
        with col1:
            neu_text = st.text_input("Aufgabe *", placeholder="z. B. Angebot prüfen")
            neu_wiederholend = st.checkbox("🔄 Wiederkehrende Aufgabe")
        with col2:
            neu_datum = st.date_input("Fällig am *", value=date.today())
            if neu_wiederholend:
                neu_wiederholung = st.selectbox("Wiederholung", ["Täglich", "Wöchentlich", "Monatlich"])
            else:
                neu_wiederholung = None

        neu_notiz = st.text_area("Notiz (optional)", height=80)

        col_save, col_cancel = st.columns(2)
        with col_save:
            if st.button("💾 Speichern", type="primary", use_container_width=True):
                if neu_text:
                    neue_aufgabe = {
                        "id": naechste_id(st.session_state.aufgaben),
                        "text": neu_text,
                        "datum": str(neu_datum),
                        "erledigt": False,
                        "typ": "normal",
                        "wiederholend": neu_wiederholend,
                        "wiederholung": neu_wiederholung,
                        "notiz": neu_notiz,
                        "erstellt": str(date.today())
                    }
                    st.session_state.aufgaben.append(neue_aufgabe)
                    speichere_aufgaben(st.session_state.aufgaben)
                    st.session_state.zeige_neu = False
                    st.success("Aufgabe gespeichert!")
                    st.rerun()
        with col_cancel:
            if st.button("Abbrechen", use_container_width=True):
                st.session_state.zeige_neu = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ─── Aufgabe bearbeiten ────────────────────────────────────────
if st.session_state.edit_id is not None:
    aufgabe = next((a for a in st.session_state.aufgaben if a["id"] == st.session_state.edit_id), None)
    if aufgabe:
        with st.container():
            st.markdown("<div style='background:#fffdf8; border:2px solid #c2410c; border-radius:14px; padding:20px; margin-bottom:16px;'>", unsafe_allow_html=True)
            st.subheader("✏️ Aufgabe bearbeiten")
            col1, col2 = st.columns(2)
            with col1:
                edit_text = st.text_input("Aufgabe", value=aufgabe["text"], key="edit_text")
            with col2:
                edit_datum = st.date_input("Datum", value=date.fromisoformat(aufgabe["datum"]), key="edit_datum")
            edit_notiz = st.text_area("Notiz", value=aufgabe.get("notiz", ""), key="edit_notiz", height=80)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Speichern", type="primary", use_container_width=True):
                    aufgabe["text"] = edit_text
                    aufgabe["datum"] = str(edit_datum)
                    aufgabe["notiz"] = edit_notiz
                    speichere_aufgaben(st.session_state.aufgaben)
                    st.session_state.edit_id = None
                    st.rerun()
            with col2:
                if st.button("🗑️ Löschen", use_container_width=True):
                    st.session_state.aufgaben = [a for a in st.session_state.aufgaben if a["id"] != st.session_state.edit_id]
                    speichere_aufgaben(st.session_state.aufgaben)
                    st.session_state.edit_id = None
                    st.rerun()
            with col3:
                if st.button("Schließen", use_container_width=True):
                    st.session_state.edit_id = None
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ─── Hauptbereich: Aufgaben + Kalender ─────────────────────────
col_links, col_rechts = st.columns([1, 2])

with col_links:
    # Offene Aufgaben
    st.markdown("### 📋 Offene Aufgaben")
    aufgaben = st.session_state.aufgaben

    # Filtern nach Ansicht
    if st.session_state.ansicht == "Tag":
        heute_iso = str(date.today())
        sichtbar = [a for a in aufgaben if a["datum"] == heute_iso]
    elif st.session_state.ansicht == "Woche":
        montag = date.today() - timedelta(days=date.today().weekday())
        sonntag = montag + timedelta(days=6)
        sichtbar = [a for a in aufgaben if montag <= date.fromisoformat(a["datum"]) <= sonntag]
    else:
        sichtbar = [a for a in aufgaben if date.fromisoformat(a["datum"]).month == date.today().month]

    offen = [a for a in sichtbar if not a["erledigt"]]
    erledigt = [a for a in sichtbar if a["erledigt"]]

    if not offen:
        st.markdown("<p style='color:#6b6258; font-style:italic; font-size:0.88rem;'>Keine offenen Aufgaben.</p>", unsafe_allow_html=True)

    for aufgabe in sorted(offen, key=lambda x: x["datum"]):
        col_check, col_text, col_edit = st.columns([0.5, 4, 0.8])
        with col_check:
            if st.checkbox("✓", key=f"check_{aufgabe['id']}", value=False, label_visibility="hidden"):
                aufgabe["erledigt"] = True
                speichere_aufgaben(st.session_state.aufgaben)
                st.rerun()
        with col_text:
            farbe = "#dc2626" if aufgabe.get("typ") == "rechnung" else "#26201a"
            datum_fmt = date.fromisoformat(aufgabe["datum"]).strftime("%d.%m.")
            st.markdown(f"<div style='color:{farbe}; font-size:0.92rem;'>{aufgabe['text']}<br><span style='font-size:0.74rem; color:#6b6258;'>{datum_fmt}</span></div>", unsafe_allow_html=True)
        with col_edit:
            if st.button("✏️", key=f"edit_{aufgabe['id']}"):
                st.session_state.edit_id = aufgabe["id"]
                st.rerun()

    # Erledigte Aufgaben
    if erledigt:
        st.markdown("<hr style='border-color:#e6dfd3; margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown("### ✅ Erledigt")
        for aufgabe in erledigt:
            col_check, col_text = st.columns([0.5, 5])
            with col_check:
                if st.checkbox("✓", key=f"check_{aufgabe['id']}", value=True, label_visibility="hidden"):
                    pass
                else:
                    aufgabe["erledigt"] = False
                    speichere_aufgaben(st.session_state.aufgaben)
                    st.rerun()
            with col_text:
                datum_fmt = date.fromisoformat(aufgabe["datum"]).strftime("%d.%m.")
                st.markdown(f"<div style='color:#6b6258; font-size:0.88rem; text-decoration:line-through;'>{aufgabe['text']}<br><span style='font-size:0.74rem;'>{datum_fmt}</span></div>", unsafe_allow_html=True)

with col_rechts:
    # Kalenderansicht
    st.markdown("### 📅 Wochenübersicht")

    montag = date.today() - timedelta(days=date.today().weekday())
    tage_namen = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

    cols = st.columns(7)
    for i, col in enumerate(cols):
        tag = montag + timedelta(days=i)
        tag_iso = str(tag)
        ist_heute = tag == date.today()
        tag_aufgaben = [a for a in st.session_state.aufgaben if a["datum"] == tag_iso]

        with col:
            header_style = "color:#c2410c; font-weight:700;" if ist_heute else "color:#6b6258; font-weight:600;"
            bg = "background:#fef0e6; border:1px solid #c2410c;" if ist_heute else "background:#fffdf8; border:1px solid #e6dfd3;"
            st.markdown(f"""
            <div style='{bg} border-radius:9px; padding:8px; min-height:100px; margin-bottom:4px;'>
                <div style='font-size:0.75rem; {header_style} border-bottom:1px solid #e6dfd3; padding-bottom:3px; margin-bottom:5px; display:flex; justify-content:space-between;'>
                    <span>{tage_namen[i]}</span><span>{tag.day}</span>
                </div>
            """, unsafe_allow_html=True)

            for aufgabe in tag_aufgaben:
                farbe = "#dc2626" if aufgabe.get("typ") == "rechnung" else "#b08968"
                text_style = "text-decoration:line-through; opacity:0.7;" if aufgabe["erledigt"] else ""
                st.markdown(f"""
                <div style='font-size:0.7rem; background:#fffdf8; border-left:3px solid {farbe};
                     padding:3px 5px; border-radius:4px; margin:2px 0; {text_style}'>
                    {aufgabe["text"][:20]}{"..." if len(aufgabe["text"]) > 20 else ""}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # Tag antippen für Detail
            if st.button(f"🔍", key=f"tag_{tag_iso}", help=f"Details für {tag.strftime('%d.%m.')}"):
                st.session_state.kalender_tag = tag_iso
                st.rerun()

    # Tages-Detail Popup
    if st.session_state.kalender_tag:
        tag = date.fromisoformat(st.session_state.kalender_tag)
        tag_aufgaben = [a for a in st.session_state.aufgaben if a["datum"] == st.session_state.kalender_tag]

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:#fffdf8; border:2px solid #c2410c; border-radius:14px; padding:20px;'>
            <h3 style='margin:0 0 12px; color:#c2410c;'>📆 {tag.strftime("%A, %d. %B %Y")}</h3>
        """, unsafe_allow_html=True)

        if not tag_aufgaben:
            st.markdown("<p style='color:#6b6258; font-style:italic;'>Keine Aufgaben an diesem Tag.</p>", unsafe_allow_html=True)
        else:
            for aufgabe in tag_aufgaben:
                status = "✅" if aufgabe["erledigt"] else "⭕"
                typ_badge = "<span style='background:#fff5f5; color:#dc2626; padding:2px 6px; border-radius:10px; font-size:0.7rem;'>Rechnung</span>" if aufgabe.get("typ") == "rechnung" else ""
                st.markdown(f"""
                <div style='padding:8px 0; border-bottom:1px solid #e6dfd3;'>
                    {status} <b>{aufgabe["text"]}</b> {typ_badge}
                    {f"<br><span style='font-size:0.82rem; color:#6b6258;'>{aufgabe.get('notiz', '')}</span>" if aufgabe.get("notiz") else ""}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("✖️ Schließen", key="close_detail"):
            st.session_state.kalender_tag = None
            st.rerun()
