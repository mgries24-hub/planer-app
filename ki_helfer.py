import streamlit as st
from datetime import datetime, date
import json
import os
import base64

# ─── API Key laden ─────────────────────────────────────────────
def lade_api_key():
    # Erst aus .streamlit/secrets.toml versuchen
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except:
        pass
    # Dann aus lokaler Datei
    key_file = "data/.api_key"
    if os.path.exists(key_file):
        with open(key_file, "r") as f:
            return f.read().strip()
    return ""

def speichere_api_key(key):
    os.makedirs("data", exist_ok=True)
    with open("data/.api_key", "w") as f:
        f.write(key)

def hat_api_key():
    return bool(lade_api_key())

# ─── Claude API aufrufen ───────────────────────────────────────
def claude_anfrage(prompt, max_tokens=2000):
    import urllib.request
    import urllib.error
    
    key = lade_api_key()
    if not key:
        return None, "Kein API-Key hinterlegt"
    
    daten = json.dumps({
        "model": "claude-sonnet-4-5",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")
    
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=daten,
        headers={
            "Content-Type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01"
        }
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            antwort = json.loads(resp.read().decode("utf-8"))
            text = "".join(b["text"] for b in antwort["content"] if b["type"] == "text")
            return text, None
    except urllib.error.HTTPError as e:
        fehler = e.read().decode("utf-8")
        return None, f"API Fehler: {fehler}"
    except Exception as e:
        return None, str(e)

def claude_bild_anfrage(bild_bytes, media_type, prompt):
    """Für PDF-Seiten als Bild an Claude schicken"""
    import urllib.request
    import urllib.error
    
    key = lade_api_key()
    if not key:
        return None, "Kein API-Key hinterlegt"
    
    b64 = base64.b64encode(bild_bytes).decode("utf-8")
    
    daten = json.dumps({
        "model": "claude-sonnet-4-5",
        "max_tokens": 1000,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": b64
                    }
                },
                {"type": "text", "text": prompt}
            ]
        }]
    }).encode("utf-8")
    
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=daten,
        headers={
            "Content-Type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01"
        }
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            antwort = json.loads(resp.read().decode("utf-8"))
            text = "".join(b["text"] for b in antwort["content"] if b["type"] == "text")
            return text, None
    except urllib.error.HTTPError as e:
        fehler = e.read().decode("utf-8")
        return None, f"API Fehler: {fehler}"
    except Exception as e:
        return None, str(e)

# ─── KI Prompts ────────────────────────────────────────────────
def ki_formatieren(text):
    prompt = f"""Formatiere die folgende Notiz sauber und übersichtlich mit Markdown-Überschriften, 
Absätzen und Aufzählungen, ohne den Inhalt zu verändern. Gib nur die formatierte Notiz zurück.

NOTIZ:
{text}"""
    return claude_anfrage(prompt)

def ki_zusammenfassen(text):
    prompt = f"""Schreibe eine prägnante Zusammenfassung der folgenden Notiz auf Deutsch. 
Beginne mit 2-3 Sätzen Überblick, dann die wichtigsten Punkte als Stichpunkte.

NOTIZ:
{text}"""
    return claude_anfrage(prompt)

def ki_aufgaben_extrahieren(text):
    prompt = f"""Extrahiere alle konkreten Aufgaben/To-dos aus der folgenden Notiz. 
Antworte AUSSCHLIESSLICH mit einem JSON-Array ohne Markdown, im Format:
[{{"text":"Aufgabe","datum":"YYYY-MM-DD oder null"}}]

NOTIZ:
{text}"""
    return claude_anfrage(prompt)

def ki_korrigieren(text):
    prompt = f"""Korrigiere Rechtschreibung und Grammatik der folgenden Notiz auf Deutsch. 
Behalte Inhalt und Struktur exakt bei. Gib nur den korrigierten Text zurück.

NOTIZ:
{text}"""
    return claude_anfrage(prompt)

def ki_rechnung_auslesen(pdf_bytes):
    """Liest Rechnungsdaten aus PDF aus"""
    # PDF erste Seite als Bild rendern mit PyMuPDF falls verfügbar
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        seite = doc[0]
        mat = fitz.Matrix(2, 2)  # 2x Zoom für bessere Qualität
        pix = seite.get_pixmap(matrix=mat)
        bild_bytes = pix.tobytes("jpeg")
        
        prompt = """Lies diese Rechnung und extrahiere folgende Daten.
Antworte NUR mit JSON ohne Markdown:
{
  "lieferant": "Firmenname des Rechnungsstellers",
  "re_nummer": "Rechnungsnummer",
  "re_datum": "Datum im Format YYYY-MM-DD",
  "betrag": "Gesamtbetrag als Zahl ohne Währungszeichen",
  "waehrung": "EUR oder CHF etc."
}
Falls ein Wert nicht gefunden wird, setze null."""
        
        return claude_bild_anfrage(bild_bytes, "image/jpeg", prompt)
    except ImportError:
        # Fallback: Text aus PDF extrahieren
        try:
            import pypdf
            import io
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            for seite in reader.pages[:2]:
                text += seite.extract_text() + "\n"
            
            prompt = f"""Lies diesen Rechnungstext und extrahiere folgende Daten.
Antworte NUR mit JSON ohne Markdown:
{{
  "lieferant": "Firmenname des Rechnungsstellers",
  "re_nummer": "Rechnungsnummer",
  "re_datum": "Datum im Format YYYY-MM-DD",
  "betrag": "Gesamtbetrag als Zahl ohne Währungszeichen",
  "waehrung": "EUR oder CHF etc."
}}
Falls ein Wert nicht gefunden wird, setze null.

RECHNUNGSTEXT:
{text[:3000]}"""
            return claude_anfrage(prompt)
        except Exception as e:
            return None, str(e)
    except Exception as e:
        return None, str(e)
