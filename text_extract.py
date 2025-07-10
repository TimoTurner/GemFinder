import streamlit as st

# Dummy-Implementierung
def extract_text_from_image(uploaded_file):
    # Simulierter OCR-Output
    return "Künstler: Example Artist\nAlbum: Demo Album\nDemo Track A\nDemo Track B\nLabel: Demo Label\nKatalognummer: DEMO-001"

def analyze_text_with_gpt4(extracted_text):
    # Simulierte Feldanalyse
    return "Swag", "", ["Pina", ""], "", ""



# from dotenv import load_dotenv
# import os
# import io
# import base64
# import json
# import numpy as np
# import cv2
# import filetype
# from PIL import Image
# import streamlit as st
# from openai import OpenAI

# # API-Key aus Umgebungsvariablen
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     raise RuntimeError("OPENAI_API_KEY nicht gefunden! Bitte in .env setzen.")

# client = OpenAI(api_key=OPENAI_API_KEY)


# def preprocess_image(image_path):
#     """Optimierte Bildvorverarbeitung für OCR."""
#     image = Image.open(image_path)
#     image = image.convert("L")
#     img_cv = np.array(image)
#     img_cv = cv2.convertScaleAbs(img_cv, alpha=1.5, beta=10)
#     img_cv = cv2.GaussianBlur(img_cv, (5, 5), 0)
#     kernel = np.array([[0, -1, 0],
#                        [-1,  5, -1],
#                        [0, -1, 0]])
#     img_cv = cv2.filter2D(img_cv, -1, kernel)
#     img_cv = cv2.adaptiveThreshold(img_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
#     image = Image.fromarray(img_cv)
#     img_byte_arr = io.BytesIO()
#     image.save(img_byte_arr, format="PNG")
#     return img_byte_arr.getvalue()

# def extract_text_from_image(uploaded_file):
#     image_bytes = uploaded_file.getvalue()
#     kind = filetype.guess(image_bytes)
#     img_type = kind.extension if kind else "png"
#     b64 = base64.b64encode(image_bytes).decode("utf-8")
#     data_url = f"data:image/{img_type};base64,{b64}"

#     if not client:
#         # Dummy output (zum Entwickeln)
#         return "Künstler: Example Artist\nAlbum: Demo Album\nTrack: Demo Track A\nTrack: Demo Track B\nLabel: Demo Label\nKatalognummer: DEMO-001"

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": "Extrahiere nur den Fließtext aus diesem Bild."},
#                 {"role": "user", "content": [
#                     {"type": "image_url", "image_url": {"url": data_url}}
#                 ]}
#             ],
#             temperature=0
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         st.error(f"❌ OpenAI Vision Error: {e}")
#         return ""

# import os
# import base64
# import json
# from PIL import Image
# from openai import OpenAI

# # Optional, aber sehr empfohlen:
# from dotenv import load_dotenv
# load_dotenv()  # Lädt Variablen aus .env

# # API-Key aus Umgebungsvariablen
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     raise RuntimeError("OPENAI_API_KEY nicht gefunden! Bitte in .env setzen.")

# client = OpenAI(api_key=OPENAI_API_KEY)

# # --- Funktionen ---

# def extract_text_from_image(uploaded_file):
#     """Extrahiert reinen Fließtext aus einem Bild (via OpenAI Vision)."""
#     image_bytes = uploaded_file.getvalue()
#     # Dateityp ermitteln (jpg, png, etc.)
#     try:
#         from filetype import guess
#         kind = guess(image_bytes)
#         img_type = kind.extension if kind else "png"
#     except ImportError:
#         img_type = "png"  # Fallback

#     b64 = base64.b64encode(image_bytes).decode("utf-8")
#     data_url = f"data:image/{img_type};base64,{b64}"

#     response = client.chat.completions.create(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": "Extrahiere nur den Fließtext aus dem Bild."},
#             {"role": "user", "content": [
#                 {"type": "image_url", "image_url": {"url": data_url}},
#                 {"type": "text", "text": "Bitte gib nur den reinen Text zurück."}
#             ]}
#         ],
#         temperature=0
#     )
#     return response.choices[0].message.content

# def analyze_text_with_gpt4(text):
#     """Analysiert OCR-Text & gibt Felder als Tupel zurück."""
#     prompt = f"""
#     Analysiere folgenden Text eines Schallplattencovers und extrahiere:
#     - Künstler
#     - Album
#     - Trackliste (jede Zeile ein Track, inkl. Remixe)
#     - Label
#     - Katalognummer

#     Falls ein Wert fehlt, schreibe "".
#     Antworte **nur im JSON-Format ohne zusätzliche Zeichen**:
#     {{
#         "artist": "...",
#         "album": "...",
#         "tracks": ["..."],
#         "label": "...",
#         "catalog_number": "..."
#     }}
#     Text:
#     {text}
#     """
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0,
#             max_tokens=400
#         )
#         raw = response.choices[0].message.content
#         # Defensive: Entfernt Code-Tags, falls GPT sie anhängt
#         raw = raw.strip().removeprefix("```json").removesuffix("```").strip()
#         data = json.loads(raw)
#         return (
#             data.get("artist", ""),
#             data.get("album", ""),
#             data.get("tracks", [""]),
#             data.get("label", ""),
#             data.get("catalog_number", "")
#         )
#     except Exception as e:
#         # Optional: logging.error(str(e))
#         return "", "", [""], "", ""

# def normalize_field(field):
#     if isinstance(field, str) and field.strip().lower() == "":
#         return ""
#     return field




# hier drunter angeblich "schnellere" Bilderkennung



# import os
# import base64
# import json
# from io import BytesIO
# from PIL import Image
# from openai import OpenAI

# # Optional, aber empfohlen für .env-Unterstützung
# try:
#     from dotenv import load_dotenv
#     load_dotenv()
# except ImportError:
#     pass  # Funktioniert auch ohne dotenv, wenn Umgebungsvariable gesetzt

# # API-Key aus Umgebungsvariablen
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     raise RuntimeError("OPENAI_API_KEY nicht gefunden! Bitte in .env setzen.")

# client = OpenAI(api_key=OPENAI_API_KEY)

# def downscale_image(image_bytes, max_side=1000):
#     """Skaliert das Bild auf max_side (z.B. 1000px), ohne Seitenverhältnis zu verlieren."""
#     img = Image.open(BytesIO(image_bytes))
#     img_format = img.format or "PNG"
#     w, h = img.size
#     if max(w, h) > max_side:
#         scaling = max_side / max(w, h)
#         new_size = (int(w * scaling), int(h * scaling))
#         img = img.resize(new_size, Image.LANCZOS)
#     output = BytesIO()
#     img.save(output, format=img_format)
#     return output.getvalue()

# def extract_text_from_image(uploaded_file):
#     """Extrahiert reinen Fließtext aus einem Bild (via OpenAI Vision)."""
#     image_bytes = uploaded_file.getvalue()
#     # Downscale für bessere Performance, wenn nötig
#     image_bytes = downscale_image(image_bytes, max_side=1000)

#     # Dateityp ermitteln (jpg, png, etc.)
#     try:
#         from filetype import guess
#         kind = guess(image_bytes)
#         img_type = kind.extension if kind else "png"
#     except ImportError:
#         img_type = "png"  # Fallback

#     b64 = base64.b64encode(image_bytes).decode("utf-8")
#     data_url = f"data:image/{img_type};base64,{b64}"

#     response = client.chat.completions.create(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": "Extrahiere nur den Fließtext aus dem Bild."},
#             {"role": "user", "content": [
#                 {"type": "image_url", "image_url": {"url": data_url}},
#                 {"type": "text", "text": "Bitte gib nur den reinen Text zurück."}
#             ]}
#         ],
#         temperature=0
#     )
#     return response.choices[0].message.content

# def analyze_text_with_gpt4(text):
#     """Analysiert OCR-Text & gibt Felder als Tupel zurück."""
#     prompt = f"""
#     Analysiere folgenden Text eines Schallplattencovers und extrahiere:
#     - Künstler
#     - Album
#     - Trackliste (jede Zeile ein Track, inkl. Remixe)
#     - Label
#     - Katalognummer

#     Falls ein Wert fehlt, schreibe "".
#     Antworte **nur im JSON-Format ohne zusätzliche Zeichen**:
#     {{
#         "artist": "...",
#         "album": "...",
#         "tracks": ["..."],
#         "label": "...",
#         "catalog_number": "..."
#     }}
#     Text:
#     {text}
#     """
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0,
#             max_tokens=400
#         )
#         raw = response.choices[0].message.content
#         # Defensive: Entfernt Code-Tags, falls GPT sie anhängt
#         raw = raw.strip().removeprefix("```json").removesuffix("```").strip()
#         data = json.loads(raw)
#         # Leere Felder zurückgeben, nie "Nicht gefunden"
#         return (
#             data.get("artist", "").strip(),
#             data.get("album", "").strip(),
#             [t for t in data.get("tracks", [""]) if t.strip()],
#             data.get("label", "").strip(),
#             data.get("catalog_number", "").strip()
#         )
#     except Exception as e:
#         # Optional: Logging, z.B. print(e)
#         return "", "", [""], "", ""

# def normalize_field(field):
#     if isinstance(field, str) and not field.strip():
#         return ""
#     return field
