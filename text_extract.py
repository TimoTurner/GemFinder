import streamlit as st
import time

# Import real OpenAI implementation
from dotenv import load_dotenv
import os
import base64
import json
from io import BytesIO
from PIL import Image
from openai import OpenAI

# Load environment variables
try:
    load_dotenv()
except ImportError:
    pass

# API-Key aus Umgebungsvariablen
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def extract_text_from_image(uploaded_file):
    """Real OCR implementation using OpenAI GPT-4 Vision"""
    if not OPENAI_API_KEY:
        print("❌ OCR nicht verfügbar: OpenAI API-Schlüssel fehlt")
        return "❌ Texterkennung nicht verfügbar\n\nUm Bilder automatisch zu analysieren, wird ein OpenAI API-Schlüssel benötigt.\nBitte geben Sie die Informationen manuell ein."
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Process image
        image_bytes = uploaded_file.getvalue()
        image_bytes = downscale_image(image_bytes, max_side=1000)

        try:
            import filetype
            kind = filetype.guess(image_bytes)
            img_type = kind.extension if kind else "png"
        except ImportError:
            img_type = "png"

        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:image/{img_type};base64,{b64}"

        print("🤖 Calling OpenAI GPT-4 Vision for OCR...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Extrahiere nur den Fließtext aus dem Bild."},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text", "text": "Bitte gib nur den reinen Text zurück."}
                ]}
            ],
            temperature=0
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ OpenAI OCR error: {e}")
        return "❌ Texterkennung fehlgeschlagen\n\nDie automatische Bilderkennung ist momentan nicht verfügbar.\nBitte geben Sie die Informationen manuell ein."

def analyze_text_with_gpt4(extracted_text, mode_context=None):
    """Real text analysis using OpenAI GPT-4"""
    if not OPENAI_API_KEY:
        print("❌ Textanalyse nicht verfügbar: OpenAI API-Schlüssel fehlt")
        return ("", "", ["❌ Automatische Analyse nicht verfügbar"], "", "")
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f'''
        Analysiere folgenden Text eines Schallplattencovers und extrahiere:
        - Künstler
        - Album
        - Trackliste (jede Zeile ein Track, inkl. Remixe)
        - Label
        - Katalognummer

        Falls ein Wert fehlt, schreibe "".
        Antworte **nur im JSON-Format ohne zusätzliche Zeichen**:
        {{
            "artist": "...",
            "album": "...",
            "tracks": ["..."],
            "label": "...",
            "catalog_number": "..."
        }}
        Text:
        {extracted_text}
        '''
        
        print("🤖 Calling OpenAI GPT-4 for text analysis...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=400
        )
        
        raw = response.choices[0].message.content
        raw = raw.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(raw)
        
        return (
            data.get("artist", "").strip(),
            data.get("album", "").strip(),
            [t for t in data.get("tracks", [""]) if t.strip()],
            data.get("label", "").strip(),
            data.get("catalog_number", "").strip()
        )
        
    except Exception as e:
        print(f"❌ OpenAI analysis error: {e}")
        return ("", "", ["❌ Textanalyse fehlgeschlagen"], "", "")

def downscale_image(image_bytes, max_side=1000):
    """Downscale image to reduce API costs"""
    img = Image.open(BytesIO(image_bytes))
    img_format = img.format or "PNG"
    w, h = img.size
    if max(w, h) > max_side:
        scaling = max_side / max(w, h)
        new_size = (int(w * scaling), int(h * scaling))
        img = img.resize(new_size, Image.LANCZOS)
    output = BytesIO()
    img.save(output, format=img_format)
    return output.getvalue()

def normalize_field(field):
    if isinstance(field, str) and not field.strip():
        return ""
    return field