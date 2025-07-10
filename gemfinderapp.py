# import socket
# import time
# import re
# import streamlit as st 
# import requests
# import datetime
# import pandas as pd

# # --- Session-State initialisieren ---
# for key in [
#     "suche_gestartet", "selected_track", "tracks_input",
#     "artist_input", "album_input", "label_input", "catalog_number_input", "ocr_applied",
#     "release_selected_idx", "release_confirmed", "log_opt_in", "track_for_search", "last_mode"
# ]:
#     if key not in st.session_state:
#         if key in ["suche_gestartet", "ocr_applied", "release_confirmed", "log_opt_in"]:
#             st.session_state[key] = False
#         elif key == "release_selected_idx":
#             st.session_state[key] = 0
#         elif key == "track_for_search":
#             st.session_state[key] = ""
#         elif key == "last_mode":
#             st.session_state[key] = "Manual Input"
#         else:
#             st.session_state[key] = ""

# st.set_page_config(page_title="GEM DETECTOR", layout="wide")

# def force_ipv4():
#     # Monkeypatch für IPv4
#     orig_getaddrinfo = socket.getaddrinfo
#     def getaddrinfo_ipv4(*args, **kwargs):
#         return [ai for ai in orig_getaddrinfo(*args, **kwargs) if ai[0] == socket.AF_INET]
#     socket.getaddrinfo = getaddrinfo_ipv4

# force_ipv4()

# from api_search import (
#     get_itunes_release_info,
#     search_discogs_releases,
#     get_discogs_release_details,
#     get_discogs_offers,
# )

# from text_extract import extract_text_from_image, analyze_text_with_gpt4

# from scrape_search import search_digital_releases_parallel

# # ... Später im Code, sobald du einen Wert für search_track hast:
# # results = search_digital_releases_parallel(st.session_state.artist_input, search_track)

# EURO_COUNTRIES = {
#     'Austria', 'Belgium', 'Croatia', 'Cyprus', 'Estonia', 'Finland', 'France',
#     'Germany', 'Greece', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg',
#     'Malta', 'Netherlands', 'Portugal', 'Slovakia', 'Slovenia', 'Spain'
# }

# ACCEPTED_CONDITIONS = ["Mint (M)", "Near Mint (NM or M-)", "Very Good Plus (VG+)"]

# def get_user_country_by_ip():
#     """Ermittelt das Land des Users anhand der IP."""
#     import requests
#     try:
#         r = requests.get("https://ipinfo.io/json")
#         if r.status_code == 200:
#             country = r.json().get("country", "")
#             code_map = {
#                 "AT": "Austria", "BE": "Belgium", "HR": "Croatia", "CY": "Cyprus", "EE": "Estonia",
#                 "FI": "Finland", "FR": "France", "DE": "Germany", "GR": "Greece", "IE": "Ireland",
#                 "IT": "Italy", "LV": "Latvia", "LT": "Lithuania", "LU": "Luxembourg", "MT": "Malta",
#                 "NL": "Netherlands", "PT": "Portugal", "SK": "Slovakia", "SI": "Slovenia", "ES": "Spain"
#             }
#             return code_map.get(country, "")
#     except Exception as e:
#         print(f"IP Country Error: {e}")
#     return ""

# import re

# def normalize_trackname(name):
#     # Kleinbuchstaben, keine Sonderzeichen, keine Whitespaces
#     return re.sub(r'\W+', '', name.lower())

# def filter_and_sort_listings(listings):
#     """
#     - Nimmt nur Angebote mit Zustand >= VG+
#     - Sortiert nach (Preis + Versand) aufsteigend
#     - Innerhalb Preisgruppen sortiert nach Zustand (besser zuerst)
#     - Nur Angebote aus EU-Ländern
#     """
#     def price_float(val):
#         try:
#             return float(val)
#         except Exception:
#             return 9999.0

#     filtered = []
#     for l in listings:
#         if (
#             l.get("ships_from") in EURO_COUNTRIES
#             and l.get("condition") in ACCEPTED_CONDITIONS
#         ):
#             price = price_float(l.get("price"))
#             shipping = price_float(l.get("shipping_price"))
#             total = price + shipping
#             filtered.append({
#                 "price": price,
#                 "shipping": shipping,
#                 "total": total,
#                 "condition": l.get("condition"),
#                 "ships_from": l.get("ships_from"),
#                 "seller": l.get("seller", {}).get("username", ""),
#                 "link": l.get("uri", ""),
#                 "info": l,
#             })
#     # Sortieren nach total price, dann Zustand (besser zuerst)
#     condition_rank = {c: i for i, c in enumerate(ACCEPTED_CONDITIONS)}
#     filtered.sort(key=lambda x: (x["total"], condition_rank.get(x["condition"], 99)))
#     return filtered



# def log_search(track, user_country, extra_info=None):
#     with open("search_log.csv", "a") as f:
#         timestamp = datetime.datetime.now().isoformat()
#         fields = [timestamp, track, user_country, str(extra_info)]
#         f.write(";".join(fields) + "\n")

# st.image("record mole copy.png", width=220)
# st.title("GEM DETECTOR")


# # --- Layout: Mode-Auswahl + Reset-Button ---
# col_mode, col_reset = st.columns([5, 1])
# with col_mode:
#     mode = st.radio(
#         "Choose Input Mode:",
#         ("Manual Input", "Take a picture", "Upload photo"),
#         key="input_mode"
#     )
# with col_reset:
#     if st.button("Reset", key="reset_manual"):
#         # Komplettes Reset, KEINE Session-State-Behandlung für file_uploader!
#         for key in [
#             "tracks_input", "selected_track", "artist_input", "album_input",
#             "label_input", "catalog_number_input", "ocr_applied", "suche_gestartet",
#             "release_selected_idx", "release_confirmed", "log_opt_in", "track_for_search"
#         ]:
#             if key in st.session_state:
#                 if key in ["ocr_applied", "suche_gestartet", "release_confirmed", "log_opt_in"]:
#                     st.session_state[key] = False
#                 elif key == "release_selected_idx":
#                     st.session_state[key] = 0
#                 else:
#                     st.session_state[key] = ""
#         st.session_state.last_mode = mode
#         st.rerun()

# # --- Reset beim Mode-Wechsel ---
# if mode != st.session_state.last_mode:
#     for key in [
#         "tracks_input", "selected_track", "artist_input", "album_input",
#         "label_input", "catalog_number_input", "ocr_applied", "suche_gestartet",
#         "release_selected_idx", "release_confirmed", "log_opt_in", "track_for_search"
#     ]:
#         if key in st.session_state:
#             if key in ["ocr_applied", "suche_gestartet", "release_confirmed", "log_opt_in"]:
#                 st.session_state[key] = False
#             elif key == "release_selected_idx":
#                 st.session_state[key] = 0
#             else:
#                 st.session_state[key] = ""
#     st.session_state.last_mode = mode
#     st.rerun()

# # --- Masken-Sperrlogik ---
# disable_mask = False

# # --- MANUAL INPUT ---
# if mode == "Manual Input":
#     disable_mask = False
#     st.session_state.ocr_applied = True  # Maske ist sofort editierbar

# # --- TAKE A PICTURE ---
# elif mode == "Take a picture":
#     disable_mask = not st.session_state.ocr_applied
#     st.write("### Foto aufnehmen")
#     photo = st.camera_input("Take a photo of your vinyl")
#     if photo is not None and not st.session_state.ocr_applied:
#         with st.spinner("Texterkennung läuft..."):
#             extracted_text = extract_text_from_image(photo)
#             artist, album, tracks, label, catalog_number = analyze_text_with_gpt4(extracted_text)
#         st.session_state.artist_input = artist or ""
#         st.session_state.album_input = album or ""
#         st.session_state.label_input = label or ""
#         st.session_state.catalog_number_input = catalog_number or ""
#         st.session_state.tracks_input = "\n".join(tracks) if isinstance(tracks, list) else (tracks or "")
#         st.session_state.ocr_applied = True
#         st.rerun()

# # --- UPLOAD PHOTO ---
# elif mode == "Upload photo":
#     disable_mask = not st.session_state.ocr_applied
#     st.write("### Foto hochladen")
#     photo = st.file_uploader("Upload a photo", type=["jpg", "png"], key="uploader")
#     if photo is not None and not st.session_state.ocr_applied:
#         with st.spinner("Texterkennung läuft..."):
#             extracted_text = extract_text_from_image(photo)
#             artist, album, tracks, label, catalog_number = analyze_text_with_gpt4(extracted_text)
#         st.session_state.artist_input = artist or ""
#         st.session_state.album_input = album or ""
#         st.session_state.label_input = label or ""
#         st.session_state.catalog_number_input = catalog_number or ""
#         st.session_state.tracks_input = "\n".join(tracks) if isinstance(tracks, list) else (tracks or "")
#         st.session_state.ocr_applied = True
#         st.rerun()

# # --- Editierbare Suchmaske (je nach ocr_applied) ---
# tracks_input = st.text_area("Track", value=st.session_state.tracks_input, key="tracks_input", height=68 if mode == "Manual Input" else 120, disabled=disable_mask)
# st.text_input(
#     "Künstler",
#     value=st.session_state.artist_input,
#     key="artist_input",
#     disabled=disable_mask,
#     placeholder="Für Revibed-Suche notwendig"
# )
# st.text_input("Katalognummer", value=st.session_state.catalog_number_input, key="catalog_number_input", disabled=disable_mask)
# st.text_input(
#     "Album",
#     value=st.session_state.album_input,
#     key="album_input",
#     disabled=disable_mask,
#     placeholder="Für Revibed-Suche notwendig"
# )
# st.text_input("Label", value=st.session_state.label_input, key="label_input", disabled=disable_mask)
# # --- Track-Auswahl und Vorbelegung ---

# track_list = [t for t in st.session_state.tracks_input.splitlines() if t.strip()]
# st.session_state.selected_track = ""  # Initialisierung, wenn keine Auswahl möglich

# # Die Track-Auswahl-Logik steht NUR EINMAL hier!
# if st.session_state.ocr_applied and track_list:
#     if len(track_list) == 1:
#         st.session_state.selected_track = track_list[0]
#         # Kein Radio-Button, keine Ausgabe!
#     elif len(track_list) > 1:
#         selected = st.radio(
#             "Wähle einen Track für die Suche aus:",
#             track_list,
#             key="track_radio"   # << EINDEUTIGER KEY!
#         )
#         st.session_state.selected_track = selected

# # Ergebnisanzeige — NUR wenn gesucht wurde
# if st.session_state.suche_gestartet and st.session_state.track_for_search:
#     search_track = st.session_state.track_for_search
#     # ... hier folgt deine Suchlogik/Ergebnisanzeige ...

# # --- EINZIGER Button für alle Modi ---
# if st.session_state.ocr_applied and st.button("Speichern und suchen", key="btn_suche") and st.session_state.selected_track:
#     st.session_state.track_for_search = st.session_state.selected_track
#     st.session_state.suche_gestartet = True
#     st.session_state.show_digital = True    # <<< WICHTIG: Immer zurück auf Digitalmodus!
   
# if "show_digital" not in st.session_state:
#     st.session_state.show_digital = True
    
# # --- Ergebnisse anzeigen ---
# if st.session_state.get("suche_gestartet") and st.session_state.track_for_search:
#     search_track = st.session_state.track_for_search
#     platform_timings = {}

#     # --- iTunes-API und Scraper-Shops abfragen ---
#     start = time.time()
#     try:
#         itunes = get_itunes_release_info(st.session_state.artist_input, search_track)
#     except Exception as e:
#         print("Fehler bei iTunes:", e)
#         itunes = {}
#     platform_timings["iTunes"] = time.time() - start

#     start = time.time()
#     results = search_digital_releases_parallel(st.session_state.artist_input, search_track)
#     platform_timings["Digital Shops"] = time.time() - start

#     # Ergebnisse kombinieren (einheitliche Feldnamen)
#     all_results = []
#     if itunes and itunes.get("release_url") and itunes.get("title"):
#         all_results.append({
#             "platform": "iTunes",
#             "title": itunes.get("title"),
#             "artist": itunes.get("artist", st.session_state.artist_input),
#             "album": itunes.get("album", ""),
#             "label": itunes.get("label", ""),
#             "price": itunes.get("price", ""),
#             "cover_url": itunes.get("cover", ""),
#             "url": itunes.get("release_url", ""),
#             "preview": itunes.get("preview", "")
#         })
#     all_results.extend(results)

#     # Funktion zum Prüfen, ob ein echter Treffer vorliegt
#     def is_real_hit(entry):
#         title = (entry.get("title") or "").strip().lower()
#         return title not in ["kein treffer", "fehler / kein treffer", ""]

#     real_hits = [entry for entry in all_results if is_real_hit(entry)]
#     any_hit = len(real_hits) > 0

#     if any_hit:
#         # --- FALL: Mindestens ein Treffer gefunden ---
#         st.markdown("#### Digitale Verfügbarkeit")
#         for entry in all_results:
#             st.markdown(f"""
#                 <div style="margin-bottom:1.7em; border:1px solid #e2e6ed; border-radius:14px; padding:0.7em 1.1em; box-shadow:0 2px 16px #d8f7fd40;">
#                     <div style="font-size:1.1em; font-weight:bold; color:#1ad6cc; margin-bottom:0.5em;">
#                         {entry.get("platform", "-")}
#                     </div>
#                     {"<a href='%s' target='_blank'><img src='%s' style='width:100px; margin-bottom:0.6em; border-radius:9px; box-shadow:0 2px 10px #e4f8ff;'></a><br>" % (entry.get('url',''), entry.get('cover_url','')) if entry.get("cover_url") else ""}
#                     <span style="font-weight:600;">{entry.get('title', '')}</span><br>
#                     <span style="color:#666;">{entry.get('artist','')}</span><br>
#                     <span style="color:#333;">{entry.get('album','')}</span><br>
#                     <span style="color:#aaa;">{entry.get('label','')}</span><br>
#                     <span style="color:#1ad64a; font-weight:600; font-size:1.07em;">
#                         {entry.get('price','')}
#                     </span><br>
#                 </div>
#             """, unsafe_allow_html=True)
#             # Audio nur bei echten iTunes-Treffern
#             if entry.get("platform") == "iTunes" and entry.get("preview") and is_real_hit(entry):
#                 st.audio(entry["preview"], format="audio/mp4")
#         # Button zum Wechsel in den Discogs-Modus
#         discogs_search = st.button("Auf Discogs suchen", key="discogs_search")
#         if discogs_search:
#             st.session_state.show_digital = False
#             st.rerun()

#     else:
#         # --- FALL: Kein Treffer auf irgendeiner Plattform ---
#         st.markdown(
#             """
#             <div style="text-align:center; margin-top:2em; margin-bottom:2em;">
#                 <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExaHN1YWc1ZjgwdDg0bnd6eXRqbmM4bG9ndmh4ZDYybWJqOTFoZjQ2YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/trHKezeRU0OPRyVYvI/giphy.gif"
#                     style="width: 180px; border-radius:30px;" alt="Diamond Gem" />
#                 <div style="font-size:2em; color:#17e6ff; font-weight:bold; margin-top:0.5em; letter-spacing:0.05em; text-shadow: 0 0 20px #89ffff;">
#                     You found a true gem
#                 </div>
#             </div>
#             """, unsafe_allow_html=True
#         )






import socket
import time
import re
import streamlit as st 
import requests
import datetime
import pandas as pd
import threading
# --- Session-State initialisieren ---
for key in [
    "results_digital", "results_discogs", "results_revibed", "suche_gestartet", "selected_track", "tracks_input",
    "artist_input", "album_input", "label_input", "catalog_number_input", "ocr_applied",
    "release_selected_idx", "release_confirmed", "log_opt_in", "track_for_search", "last_mode",
    "discogs_revibed_mode", "show_digital"
]:
    if key not in st.session_state:
        st.session_state[key] = []
        if key in ["suche_gestartet", "ocr_applied", "release_confirmed", "log_opt_in", "discogs_revibed_mode", "show_digital"]:
            st.session_state[key] = False
        elif key == "release_selected_idx":
            st.session_state[key] = 0
        elif key == "track_for_search":
            st.session_state[key] = ""
        elif key == "last_mode":
            st.session_state[key] = "Manual Input"
        else:
            st.session_state[key] = ""


st.set_page_config(page_title="GEM DETECTOR", layout="wide")

def force_ipv4():
    orig_getaddrinfo = socket.getaddrinfo
    def getaddrinfo_ipv4(*args, **kwargs):
        return [ai for ai in orig_getaddrinfo(*args, **kwargs) if ai[0] == socket.AF_INET]
    socket.getaddrinfo = getaddrinfo_ipv4
force_ipv4()

from api_search import (
    get_itunes_release_info,
    search_discogs_releases,
    get_discogs_release_details,
    get_discogs_offers,
)
from text_extract import extract_text_from_image, analyze_text_with_gpt4
from scrape_search import search_digital_releases_parallel, search_revibed
from rapidfuzz import fuzz
from concurrent.futures import ThreadPoolExecutor, as_completed
from scrape_search import search_bandcamp, search_beatport, search_traxsource

def is_fuzzy_match(user_track, shop_title, threshold=80):
    if not user_track or not shop_title:
        return False
    return fuzz.partial_ratio(user_track.lower(), shop_title.lower()) >= threshold


def fetch_result(platform, artist, track, album):
    # Dummy-Funktionen oder echte API-Scraper hier einbinden
    if platform == "iTunes":
        return get_itunes_release_info(artist, track)
    elif platform == "Beatport":
        return scrape_beatport_release_info(artist, track)
    elif platform == "Bandcamp":
        return scrape_bandcamp_release_info(artist, track)
    elif platform == "Traxsource":
        return scrape_traxsource_release_info(artist, track)
    return None

def run_parallel_queries(artist, track, album):
    if "live_results" not in st.session_state:
        st.session_state["live_results"] = []
    futures_dict = {}


# def show_live_results():
#     results = st.session_state.get("live_results", [])
#     st.markdown("### Live-Suchergebnisse")
#     if not results:
#         st.info("Noch keine Suchergebnisse...")
#     for entry in results:
#         st.markdown(f"**{entry.get('platform','?')}**")
#         st.markdown(f"**{entry.get('title','')}**")
#         # Hier kannst du weitere Felder und das Cover anzeigen wie gewohnt
#         st.markdown("---")

# def show_live_results():
#     PLACEHOLDER_COVER = "cover_placeholder.png"
#     NO_HIT_COVER     = "not_found.png"

#     results = st.session_state.get("live_results", [])
#     st.markdown("### Live-Suchergebnisse")
#     if not results:
#         st.info("Noch keine Suchergebnisse…")
#         return

#     # nur das neueste Ergebnis anzeigen
#     entry = results[-1]

#     platform    = entry.get("platform", "?")
#     title       = entry.get("title", "")
#     artist      = entry.get("artist", "")
#     album       = entry.get("album", "")
#     label       = entry.get("label", "")
#     price       = entry.get("price", "")
#     cover_url   = entry.get("cover_url", "") or PLACEHOLDER_COVER
#     release_url = entry.get("url", "")
#     preview     = entry.get("preview", "")

#     cols = st.columns([1, 5])
#     with cols[0]:
#         st.image(cover_url, width=92)
#     with cols[1]:
#         # Plattformname als Link (fett)
#         if release_url:
#             st.markdown(f"[**{platform}**]({release_url})")
#         else:
#             st.markdown(f"**{platform}**")
#         # Titel
#         st.markdown(f"**{title}**")
#         # Metadaten
#         if artist:
#             st.markdown(artist)
#         if album:
#             st.markdown(f"*{album}*")
#         if label:
#             st.markdown(f"`{label}`")
#         if price:
#             st.markdown(f":green[{price}]")
#         # Audio-Preview
#         if preview:
#             st.audio(preview, format="audio/mp4")
#     st.markdown("---")


import threading
import concurrent.futures

# ——————————————————————————————————————————————
# 1) Live-Renderer: nur das frisch hinzugekommene Result anzeigen
# ——————————————————————————————————————————————

def show_live_results():
    PLACEHOLDER_COVER = "cover_placeholder.png"
    NO_HIT_COVER     = "not_found.png"

    results = st.session_state.get("live_results", [])

    # Header nur beim allerersten Live-Eintrag
    if not results:
        st.markdown("### Live-Suchergebnisse")
        st.info("Noch keine Suchergebnisse…")
        return
    if len(results) == 1:
        st.markdown("### Live-Suchergebnisse")

    entry     = results[-1]
    cover_url = entry.get("cover_url","") or PLACEHOLDER_COVER
    cols      = st.columns([1,5])
    with cols[0]:
        st.image(cover_url, width=92)
    with cols[1]:
        platform = entry.get("platform","?")
        url      = entry.get("url","")
        if url:
            st.markdown(f"[**{platform}**]({url})")
        else:
            st.markdown(f"**{platform}**")

        st.markdown(f"**{entry.get('title','')}**")
        if entry.get("artist"):
            st.markdown(entry["artist"])
        if entry.get("album"):
            st.markdown(f"*{entry['album']}*")
        if entry.get("label"):
            st.markdown(f"`{entry['label']}`")
        if entry.get("price"):
            st.markdown(f":green[{entry['price']}]")
        if entry.get("preview"):
            st.audio(entry["preview"], format="audio/mp4")

    st.markdown("---")


EURO_COUNTRIES = {
    'Austria', 'Belgium', 'Croatia', 'Cyprus', 'Estonia', 'Finland', 'France',
    'Germany', 'Greece', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg',
    'Malta', 'Netherlands', 'Portugal', 'Slovakia', 'Slovenia', 'Spain'
}
ACCEPTED_CONDITIONS = ["Mint (M)", "Near Mint (NM or M-)", "Very Good Plus (VG+)"]

# Hilfsfunktionen
def normalize_trackname(name):
    return re.sub(r'\W+', '', name.lower())

def get_user_country_by_ip():
    try:
        r = requests.get("https://ipinfo.io/json")
        if r.status_code == 200:
            country = r.json().get("country", "")
            code_map = {...} # wie gehabt
            return code_map.get(country, "")
    except Exception as e:
        print(f"IP Country Error: {e}")
    return ""

def filter_and_sort_listings(listings):
    def price_float(val):
        try:
            return float(val)
        except Exception:
            return 9999.0
    filtered = []
    for l in listings:
        if (
            l.get("ships_from") in EURO_COUNTRIES
            and l.get("condition") in ACCEPTED_CONDITIONS
        ):
            price = price_float(l.get("price"))
            shipping = price_float(l.get("shipping_price"))
            total = price + shipping
            filtered.append({
                "price": price,
                "shipping": shipping,
                "total": total,
                "condition": l.get("condition"),
                "ships_from": l.get("ships_from"),
                "seller": l.get("seller", {}).get("username", ""),
                "link": l.get("uri", ""),
                "info": l,
            })
    condition_rank = {c: i for i, c in enumerate(ACCEPTED_CONDITIONS)}
    filtered.sort(key=lambda x: (x["total"], condition_rank.get(x["condition"], 99)))
    return filtered

# --- Header ---
st.image("record mole copy.png", width=220)
st.title("GEM DETECTOR")


# --- Layout: Mode-Auswahl + Reset-Button ---
col_mode, col_reset = st.columns([5, 1])
with col_mode:
    mode = st.radio(
        "Choose Input Mode:",
        ("Manual Input", "Take a picture", "Upload photo"),
        key="input_mode"
    )
with col_reset:
    if st.button("Reset", key="reset_manual"):
        # Komplettes Reset, KEINE Session-State-Behandlung für file_uploader!
        for key in [
            "tracks_input", "selected_track", "artist_input", "album_input",
            "label_input", "catalog_number_input", "ocr_applied", "suche_gestartet",
            "release_selected_idx", "release_confirmed", "log_opt_in", "track_for_search"
        ]:
            if key in st.session_state:
                if key in ["ocr_applied", "suche_gestartet", "release_confirmed", "log_opt_in", "discogs_revibed_mode"]:
                    st.session_state[key] = False
                elif key == "release_selected_idx":
                    st.session_state[key] = 0
                else:
                    st.session_state[key] = ""
        st.session_state.last_mode = mode
        st.rerun()

# --- Reset beim Mode-Wechsel ---
if mode != st.session_state.last_mode:
    for key in [
        "tracks_input", "selected_track", "artist_input", "album_input",
        "label_input", "catalog_number_input", "ocr_applied", "suche_gestartet",
        "release_selected_idx", "release_confirmed", "log_opt_in", "track_for_search"
    ]:
        if key in st.session_state:
            if key in ["ocr_applied", "suche_gestartet", "release_confirmed", "log_opt_in"]:
                st.session_state[key] = False
            elif key == "release_selected_idx":
                st.session_state[key] = 0
            else:
                st.session_state[key] = ""
    st.session_state.last_mode = mode
    st.rerun()

# --- Masken-Sperrlogik ---
disable_mask = False

# --- Editierbare Suchmaske (keine doppelten Keys!) ---
tracks_input = st.text_area(
    "Track",
    value=st.session_state.tracks_input,
    key="tracks_input"
)
st.text_input(
    "Künstler",
    value=st.session_state.artist_input,
    key="artist_input"
)
st.text_input(
    "Katalognummer",
    value=st.session_state.catalog_number_input,
    key="catalog_number_input"
)
st.text_input(
    "Album",
    value=st.session_state.album_input,
    key="album_input"
)
# st.text_input(
#     "Label",
#     value=st.session_state.label_input,
#     key="label_input",
# )

track_list = [t for t in st.session_state.tracks_input.splitlines() if t.strip()]
artist_ok = bool(st.session_state.artist_input.strip())
album_ok = bool(st.session_state.album_input.strip())
catno_ok = bool(st.session_state.catalog_number_input.strip())


# Mapping für Plattform-Logos & Links
PLACEHOLDER_COVER = "https://via.placeholder.com/92x92.png?text=No+Image"

PLATFORM_LINKS = {
    "Beatport": (
        "https://www.beatport.com/",
        "https://seeklogo.com/images/B/beatport-logo-1A5DCCBFAE-seeklogo.com.png"
    ),
    "Bandcamp": (
        "https://bandcamp.com/",
        "https://cdn-icons-png.flaticon.com/512/2111/2111624.png"
    ),
    "Traxsource": (
        "https://www.traxsource.com/",
        "https://cdn.traxsource.com/static/images/logos/apple-touch-icon-114x114.png"
    ),
    "iTunes": (
        "https://music.apple.com/",
        "https://upload.wikimedia.org/wikipedia/commons/d/de/ITunes_logo.png"
    ),
    "Revibed": (
        "https://revibed.com/",
        "https://revibed.com/favicon-32x32.png"
    ),
    "Discogs": (
        "https://www.discogs.com/",
        "https://upload.wikimedia.org/wikipedia/commons/0/09/Discogs_Logo.png"
    ),
}

def get_platform_info(platform):
    url, logo = PLATFORM_LINKS.get(platform, ("#", PLACEHOLDER_COVER))
    return url, logo


def can_search_digital_shops(track, artist, album):
    # Mindestens: Track UND (Artist ODER Album), notfalls Track allein
    if track:
        return True
    if artist and (album or track):
        return True
    return False

def can_search_revibed(artist, album, track):
    # Artist + (Album ODER Track)
    return bool(artist and (album or track))

def can_search_discogs(catno, artist, track, album):
    if catno:
        return True
    if artist and (track or album):
        return True
    return False

import threading

def run_digital_shops_live_worker(track, artist, album, catno):
    can_search = can_search_digital_shops(track, artist, album)
    if can_search:
        itunes = get_itunes_release_info(artist, track)
        if itunes and itunes.get("release_url") and itunes.get("title"):
            entry = {
                "platform": "iTunes",
                "title": itunes.get("title"),
                "artist": itunes.get("artist", artist),
                "album": itunes.get("album", ""),
                "label": itunes.get("label", ""),
                "price": itunes.get("price", ""),
                "cover_url": itunes.get("cover", ""),
                "url": itunes.get("release_url", ""),
                "preview": itunes.get("preview", "")
            }
        else:
            entry = {
                "platform": "iTunes",
                "title": "Kein Treffer",
                "artist": artist,
                "album": album,
                "label": "",
                "price": "",
                "cover_url": "",
                "url": "",
                "preview": ""
            }
        live_results = st.session_state.get("live_results", [])
        live_results.append(entry)
        st.session_state["live_results"] = live_results

    platforms = ["Beatport", "Bandcamp", "Traxsource"]
    if can_search:
        if track and artist:
            results = search_digital_releases_parallel(artist, track, '', '')
        elif track and album:
            results = search_digital_releases_parallel('', track, album, '')
        elif track:
            results = search_digital_releases_parallel('', track, '', '')
        else:
            results = []
        for entry in results:
            live_results = st.session_state.get("live_results", [])
            live_results.append(entry)
            st.session_state["live_results"] = live_results
    else:
        for p in platforms:
            entry = {
                "platform": p,
                "title": "Nicht gesucht (Angaben fehlen)",
                "artist": "",
                "album": "",
                "label": "",
                "price": "",
                "cover_url": "",
                "url": ""
            }
            live_results = st.session_state.get("live_results", [])
            live_results.append(entry)
            st.session_state["live_results"] = live_results

def is_fuzzy_match(user_track, shop_title, threshold=80):
    if not user_track or not shop_title:
        return False
    return fuzz.partial_ratio(user_track.lower(), shop_title.lower()) >= threshold

def show_digital_block():
    PLACEHOLDER_COVER = "cover_placeholder.png"   # neutrales Bild
    NO_HIT_COVER = "not_found.png"                # durchgestrichenes Bild

    all_results = st.session_state.results_digital
    user_track = st.session_state.track_for_search.strip()

    st.markdown("#### Digitale Verfügbarkeit")

    def is_real_hit(entry):
        title = (entry.get("title") or "").strip().lower()
        return title not in ["kein treffer", "fehler / kein treffer", "", "nicht gesucht (angaben fehlen)"]

    real_hits = [entry for entry in all_results if is_real_hit(entry) and entry.get("platform", "").lower() != "itunes"]
    any_hit = len(real_hits) > 0

    for entry in all_results:
        platform_str = entry.get("platform", "")
        title_str = str(entry.get("title", ""))
        artist_str = str(entry.get("artist", ""))
        album_str = str(entry.get("album", ""))
        label_raw = entry.get("label", "")
        label_str = label_raw[0] if isinstance(label_raw, list) and label_raw else str(label_raw)
        price_str = str(entry.get("price", ""))
        cover_url = entry.get("cover_url", "")
        release_url = entry.get("url", "").strip()
        platform_url, _ = get_platform_info(platform_str)

        # Bildauswahl
        if not cover_url or not cover_url.strip():
            if not is_real_hit(entry):
                cover_url = NO_HIT_COVER
            else:
                cover_url = PLACEHOLDER_COVER

        # Fuzzy Matching für Beatport
        highlight = False
        if platform_str == "Beatport" and is_fuzzy_match(user_track, title_str):
            highlight = True

        cols = st.columns([1, 5])
        with cols[0]:
            st.image(cover_url, width=92)
        with cols[1]:
            # Plattformname als Link (fett, immer)
            if release_url:
                st.markdown(f"[**{platform_str}**]({release_url})", unsafe_allow_html=True)
            else:
                st.markdown(f"[**{platform_str}**]({platform_url})", unsafe_allow_html=True)

            # Titel ggf. farbig hervorheben, sonst normal
            if highlight:
                st.markdown(f":red[**{title_str}**]")
            else:
                st.markdown(f"**{title_str}**")

            if artist_str:
                st.markdown(f"{artist_str}")
            if album_str:
                st.markdown(f"*{album_str}*")
            if label_str:
                st.markdown(f"`{label_str}`")
            if price_str and release_url:
                st.markdown(f"[{price_str}]({release_url})", unsafe_allow_html=True)
            elif price_str:
                st.markdown(f":green[{price_str}]")
            if platform_str == "iTunes" and entry.get("preview") and is_real_hit(entry):
                st.audio(entry["preview"], format="audio/mp4")
        st.markdown("---")

    if not any_hit:
        st.image(NO_HIT_COVER, width=92)
        st.markdown("**You found a true gem**")
        st.markdown(":gray[Kein digitaler Treffer auf den Plattformen gefunden.]")
        # Umschalten und rerun (wie gehabt)
        st.session_state.discogs_revibed_mode = True
        st.session_state.show_digital = False
        artist = st.session_state.artist_input.strip()
        album = st.session_state.album_input.strip()
        track = st.session_state.track_for_search.strip()
        st.session_state.results_discogs = search_discogs_releases(artist, track)
        if album:
            st.session_state.results_revibed = search_revibed('', album)
        elif artist:
            st.session_state.results_revibed = search_revibed(artist, '')
        else:
            st.session_state.results_revibed = [{
                'platform': 'Revibed',
                'title': '',
                'artist': '',
                'album': '',
                'label': '',
                'price': '',
                'cover_url': '',
                'url': '',
                'search_time': 0.0,
                'message': "Für Revibed-Suche mindestens Album ODER Artist ausfüllen."
            }]
        st.rerun()

    # --- BUTTON: Discogs & Revibed explizit suchen ---
    if st.button("Auf Discogs und Revibed suchen", key="discogs_search_digital"):
        st.session_state.discogs_revibed_mode = True
        st.session_state.show_digital = False
        artist = st.session_state.artist_input.strip()
        album = st.session_state.album_input.strip()
        track = st.session_state.track_for_search.strip()
        st.session_state.results_discogs = search_discogs_releases(artist, track)
        if album:
            st.session_state.results_revibed = search_revibed('', album)
        elif artist:
            st.session_state.results_revibed = search_revibed(artist, '')
        else:
            st.session_state.results_revibed = [{
                'platform': 'Revibed',
                'title': '',
                'artist': '',
                'album': '',
                'label': '',
                'price': '',
                'cover_url': '',
                'url': '',
                'search_time': 0.0,
                'message': "Für Revibed-Suche mindestens Album ODER Artist ausfüllen."
            }]
        st.rerun()


def show_discogs_and_revibed_block(releases, track_for_search, revibed_results):
    PLACEHOLDER_COVER = "cover_placeholder.png"
    NO_HIT_COVER = "not_found.png"

    st.markdown("#### Discogs Releases")
    if releases:
        selected_idx = st.radio(
            "Wähle das passende Release für deinen Track:",
            options=list(range(len(releases))),
            index=st.session_state.get("release_selected_idx", 0),
            format_func=lambda i: (
                f"{releases[i].get('title', '-')}"
                f" – {releases[i].get('label', ['-'])[0] if releases[i].get('label') else '-'}"
                f" ({releases[i].get('year', '-')})"
            ),
            key="release_select"
        )
        st.session_state.release_selected_idx = selected_idx 
        r = releases[selected_idx]
        cover_url = r.get("cover") or r.get("cover_image") or r.get("thumb")
        if not cover_url or not cover_url.strip():
            cover_url = PLACEHOLDER_COVER
        label_raw = r.get("label", ["-"])
        label_str = label_raw[0] if isinstance(label_raw, list) and label_raw else str(label_raw)
        format_list = r.get("format", [])
        format_str = ", ".join(format_list) if isinstance(format_list, list) else str(format_list)
        year_str = r.get("year", "-")
        catno_str = r.get("catno", "-")
        title_str = r.get("title", "-")
        url = r.get("uri") or r.get("url") or ""

        cols = st.columns([1, 5])
        with cols[0]:
            st.image(cover_url, width=92)
        with cols[1]:
            st.markdown(f"**{title_str}**")
            st.markdown(f"`{label_str}` | {year_str} | {format_str} | Katalog: `{catno_str}`")
            if url:
                st.markdown(f"[Discogs Release →](https://www.discogs.com{url})", unsafe_allow_html=False)
        # Tracklist
        tracklist = r.get("tracklist", [])
        if tracklist:
            st.markdown("**Tracklist:**")
            for t in tracklist:
                if isinstance(t, dict):
                    track_title = t.get("title", "")
                else:
                    track_title = str(t)
                if track_title and track_title.lower() == st.session_state.track_for_search.strip().lower():
                    st.markdown(f":red[**{track_title}**]")
                else:
                    st.markdown(f"{track_title}")
        st.markdown("---")
    else:
        st.image(NO_HIT_COVER, width=92)
        st.info("Keine Discogs-Releases gefunden.")

    # ----------- Revibed-Block -----------
    st.markdown("#### Revibed: Treffer zu artist und release")
    real_revibed_hits = [r for r in revibed_results if r.get("title") and r.get("title").strip()]
    if real_revibed_hits:
        for entry in real_revibed_hits:
            cover_url = entry.get("cover_url", "")
            if not cover_url or not cover_url.strip():
                cover_url = PLACEHOLDER_COVER
            title_str = str(entry.get("title", ""))
            artist_str = str(entry.get("artist", ""))
            album_str = str(entry.get("album", ""))
            label_raw = entry.get("label", "")
            label_str = label_raw[0] if isinstance(label_raw, list) and label_raw else str(label_raw)
            price_str = str(entry.get("price", ""))
            url = entry.get("url", "")
            cols = st.columns([1, 5])
            with cols[0]:
                st.image(cover_url, width=92)
            with cols[1]:
                st.markdown(f"**{title_str}**")
                if artist_str:
                    st.markdown(f"{artist_str}")
                if album_str:
                    st.markdown(f"*{album_str}*")
                if label_str:
                    st.markdown(f"`{label_str}`")
                if price_str and url:
                    st.markdown(f"[{price_str}]({url})", unsafe_allow_html=False)
                elif price_str:
                    st.markdown(f":green[{price_str}]")
            st.markdown("---")
    else:
        st.image(NO_HIT_COVER, width=92)
        st.info("Kein Treffer")

    if st.button("Zurück zu digitalen Shops", key="digital_back_revibed"):
        st.session_state.discogs_revibed_mode = False
        st.session_state.show_digital = True
        st.rerun()

# --- Track-Auswahl vor der Suche ---
if not st.session_state.suche_gestartet:
    if track_list and len(track_list) > 1:
        selected = st.radio(
            "Wähle einen Track für die Suche aus:",
            track_list,
            key="track_radio"
        )
        st.session_state.selected_track = selected
    elif track_list and len(track_list) == 1:
        st.session_state.selected_track = track_list[0]
    else:
        st.session_state.selected_track = ""

# --- EINZIGER Button (aktiv nach den Regeln) ---
track = st.session_state.selected_track.strip() if "selected_track" in st.session_state else ""
artist = st.session_state.artist_input.strip()
album = st.session_state.album_input.strip()
catno = st.session_state.catalog_number_input.strip()

button_enabled = (
    can_search_digital_shops(track, artist, album) or
    can_search_revibed(artist, album, track) or
    can_search_discogs(catno, artist, track, album)
)

# ——————————————————————————————————————————————
# Live-Button‐Handler mit sofortigen Live-Updates
# ——————————————————————————————————————————————
if st.button("Speichern und suchen", key="btn_suche"):
    # 1) Session-State setzen
    st.session_state.suche_gestartet     = True
    st.session_state.track_for_search     = st.session_state.selected_track
    st.session_state.show_digital         = True
    st.session_state.discogs_revibed_mode = False

    # 2) Live-Ergebnislisten initialisieren
    st.session_state["live_results"] = []
    st.session_state.results_digital  = []

    # 3) Eingaben
    track  = st.session_state.selected_track.strip()
    artist = st.session_state.artist_input.strip()
    album  = st.session_state.album_input.strip()

    # 4) Status- und Ergebnis-Container
    status            = st.empty()
    results_container = st.container()

    # 5) iTunes sofort abfragen und anzeigen
    status.text("Suche auf iTunes…")
    if can_search_digital_shops(track, artist, album):
        it = get_itunes_release_info(artist, track)
        if it and it.get("release_url") and it.get("title"):
            entry = {
                "platform": "iTunes",
                "title":    it["title"],
                "artist":   it.get("artist", artist),
                "album":    it.get("album", ""),
                "label":    it.get("label", ""),
                "price":    it.get("price", ""),
                "cover_url":it.get("cover", ""),
                "url":      it.get("release_url", ""),
                "preview":  it.get("preview", "")
            }
        else:
            entry = {
                "platform":"iTunes",
                "title":"Kein Treffer",
                "artist":"",
                "album":"",
                "label":"",
                "price":"",
                "cover_url":"",
                "url":"",
                "preview":""
            }
    else:
        entry = {
            "platform":"iTunes",
            "title":"Nicht gesucht (Angaben fehlen)",
            "artist":"",
            "album":"",
            "label":"",
            "price":"",
            "cover_url":"",
            "url":"",
            "preview":""
        }

    # a) Push & Render
    st.session_state["live_results"].append(entry)
    with results_container:
        show_live_results()

    # 6) Parallel: Beatport, Bandcamp, Traxsource
    from concurrent.futures import ThreadPoolExecutor, as_completed

    funcs = [
        ("Beatport",   lambda: search_beatport(artist, track)),
        ("Bandcamp",   lambda: search_bandcamp(artist, track)),
        ("Traxsource", lambda: search_traxsource(artist, track)),
    ]
    with ThreadPoolExecutor(max_workers=3) as exe:
        futures = {exe.submit(f): name for name, f in funcs}
        for fut in as_completed(futures):
            name = futures[fut]

            # <<< Hier den Status aktualisieren >>>
            status.text(f"Suche auf {name}…")

            try:
                hits = fut.result(timeout=8)
                shop_entry = hits[0] if hits else {
                    "platform": name,
                    "title":    "Kein Treffer",
                    "artist":   "", "album": "", "label": "", "price": "",
                    "cover_url":"", "url": ""
                }
            except Exception:
                shop_entry = {
                    "platform": name,
                    "title":    "Fehler",
                    "artist":   "", "album":    "", "label":    "",
                    "price":    "", "cover_url":"",
                    "url":      ""
                }

            st.session_state["live_results"].append(shop_entry)
            st.session_state.results_digital.append(shop_entry)
            with results_container:
                show_live_results()

    # 7) Statuszeile leeren
    status.empty()

    real_hits = [
        r for r in st.session_state.results_digital
        if r["platform"].lower() != "itunes"
        and r["title"].strip().lower() not in [
            "", 
            "kein treffer", 
            "fehler / kein treffer",      # ← hier ergänzt
            "nicht gesucht (angaben fehlen)"
        ]
    ]
    
    any_hit = len(real_hits) > 0
    any_hit = 0
    #  def is_real_hit(entry):
    #     title = (entry.get("title") or "").strip().lower()
    #     return title not in ["kein treffer", "fehler / kein treffer", "", "nicht gesucht (angaben fehlen)"]

    # real_hits = [entry for entry in all_results if is_real_hit(entry) and entry.get("platform", "").lower() != "itunes"]

    if not any_hit:
        print("no hits")
        # schalte um
        st.session_state.discogs_revibed_mode = True
        st.session_state.show_digital       = False

        # hole Discogs + Revibed-Ergebnisse
        artist = st.session_state.artist_input.strip()
        track  = st.session_state.track_for_search.strip()
        album  = st.session_state.album_input.strip()

        st.session_state.results_discogs = search_discogs_releases(artist, track)
        if album:
            st.session_state.results_revibed = search_revibed('', album)
        else:
            st.session_state.results_revibed = search_revibed(artist, '')

        # direkt anzeigen
        show_discogs_and_revibed_block(
            st.session_state.results_discogs,
            st.session_state.track_for_search,
            st.session_state.results_revibed
        )

    if st.button("Auf Discogs und Revibed suchen", key="discogs_search_digital"):
        print("Auf Discogs und Revibed suchen")
        st.session_state.discogs_revibed_mode = True
        st.session_state.show_digital = False
        artist = st.session_state.artist_input.strip()
        album = st.session_state.album_input.strip()
        track = st.session_state.track_for_search.strip()
        st.session_state.results_discogs = search_discogs_releases(artist, track)
        if album:
            st.session_state.results_revibed = search_revibed('', album)
        elif artist:
            st.session_state.results_revibed = search_revibed(artist, '')
        else:
            st.session_state.results_revibed = [{
                'platform': 'Revibed',
                'title': '',
                'artist': '',
                'album': '',
                'label': '',
                'price': '',
                'cover_url': '',
                'url': '',
                'search_time': 0.0,
                'message': "Für Revibed-Suche mindestens Album ODER Artist ausfüllen."
            }]
        # st.rerun()


# # --- BUTTON: Speichern und suchen (Digitale Shops) ---
# if st.button("Speichern und suchen", key="btn_suche"):
#     st.session_state.suche_gestartet = True
#     st.session_state.track_for_search = st.session_state.selected_track
#     st.session_state.show_digital = True
#     st.session_state.discogs_revibed_mode = False

#     track = st.session_state.selected_track.strip()
#     artist = st.session_state.artist_input.strip()
#     album = st.session_state.album_input.strip()
#     catno = st.session_state.catalog_number_input.strip()

#     results = []

#     if can_search_digital_shops(track, artist, album):
#         try:
#             itunes = get_itunes_release_info(artist, track)
#             # ... dein bisheriger iTunes-Logik ...
#             if itunes and itunes.get("release_url") and itunes.get("title"):
#                 results.append({
#                     "platform": "iTunes",
#                     "title": itunes.get("title"),
#                     "artist": itunes.get("artist", artist),
#                     "album": itunes.get("album", ""),
#                     "label": itunes.get("label", ""),
#                     "price": itunes.get("price", ""),
#                     "cover_url": itunes.get("cover", ""),
#                     "url": itunes.get("release_url", ""),
#                     "preview": itunes.get("preview", "")
#                 })
#         except Exception as e:
#             print("Fehler bei iTunes:", e)
#         # Digitale Shops
#         if track and artist:
#             results_digital = search_digital_releases_parallel(artist, track, '', '')
#         elif track and album:
#             results_digital = search_digital_releases_parallel('', track, album, '')
#         elif track:
#             results_digital = search_digital_releases_parallel('', track, '', '')
#         else:
#             results_digital = []
#         results.extend(results_digital)
#     else:
#         results.extend([
#             {"platform": p, "title": "Nicht gesucht (Angaben fehlen)", "artist": "", "album": "", "label": "", "price": "", "cover_url": "", "url": ""}
#             for p in ["Beatport", "Bandcamp", "Traxsource"]
#         ])
#     st.session_state.results_digital = results
#     st.session_state.results_discogs = []
#     st.session_state.results_revibed = []


# def is_fuzzy_match(user_track, shop_title, threshold=80):
#     if not user_track or not shop_title:
#         return False
#     return fuzz.partial_ratio(user_track.lower(), shop_title.lower()) >= threshold

# def show_digital_block():
#     PLACEHOLDER_COVER = "cover_placeholder.png"   # neutrales Bild
#     NO_HIT_COVER = "not_found.png"                # durchgestrichenes Bild

#     all_results = st.session_state.results_digital
#     user_track = st.session_state.track_for_search.strip()

#     st.markdown("#### Digitale Verfügbarkeit")

#     def is_real_hit(entry):
#         title = (entry.get("title") or "").strip().lower()
#         return title not in ["kein treffer", "fehler / kein treffer", "", "nicht gesucht (angaben fehlen)"]

#     real_hits = [entry for entry in all_results if is_real_hit(entry) and entry.get("platform", "").lower() != "itunes"]
#     any_hit = len(real_hits) > 0

#     for entry in all_results:
#         platform_str = entry.get("platform", "")
#         title_str = str(entry.get("title", ""))
#         artist_str = str(entry.get("artist", ""))
#         album_str = str(entry.get("album", ""))
#         label_raw = entry.get("label", "")
#         label_str = label_raw[0] if isinstance(label_raw, list) and label_raw else str(label_raw)
#         price_str = str(entry.get("price", ""))
#         cover_url = entry.get("cover_url", "")
#         release_url = entry.get("url", "").strip()
#         platform_url, _ = get_platform_info(platform_str)

#         # Bildauswahl
#         if not cover_url or not cover_url.strip():
#             if not is_real_hit(entry):
#                 cover_url = NO_HIT_COVER
#             else:
#                 cover_url = PLACEHOLDER_COVER

#         # Fuzzy Matching für Beatport
#         highlight = False
#         if platform_str == "Beatport" and is_fuzzy_match(user_track, title_str):
#             highlight = True

#         cols = st.columns([1, 5])
#         with cols[0]:
#             st.image(cover_url, width=92)
#         with cols[1]:
#             # Plattformname als Link (fett, immer)
#             if release_url:
#                 st.markdown(f"[**{platform_str}**]({release_url})", unsafe_allow_html=True)
#             else:
#                 st.markdown(f"[**{platform_str}**]({platform_url})", unsafe_allow_html=True)

#             # Titel ggf. farbig hervorheben, sonst normal
#             if highlight:
#                 st.markdown(f":red[**{title_str}**]")
#             else:
#                 st.markdown(f"**{title_str}**")

#             if artist_str:
#                 st.markdown(f"{artist_str}")
#             if album_str:
#                 st.markdown(f"*{album_str}*")
#             if label_str:
#                 st.markdown(f"`{label_str}`")
#             if price_str and release_url:
#                 st.markdown(f"[{price_str}]({release_url})", unsafe_allow_html=True)
#             elif price_str:
#                 st.markdown(f":green[{price_str}]")
#             if platform_str == "iTunes" and entry.get("preview") and is_real_hit(entry):
#                 st.audio(entry["preview"], format="audio/mp4")
#         st.markdown("---")

#     if not any_hit:
#         st.image(NO_HIT_COVER, width=92)
#         st.markdown("**You found a true gem**")
#         st.markdown(":gray[Kein digitaler Treffer auf den Plattformen gefunden.]")
#         # Umschalten und rerun (wie gehabt)
#         st.session_state.discogs_revibed_mode = True
#         st.session_state.show_digital = False
#         artist = st.session_state.artist_input.strip()
#         album = st.session_state.album_input.strip()
#         track = st.session_state.track_for_search.strip()
#         st.session_state.results_discogs = search_discogs_releases(artist, track)
#         if album:
#             st.session_state.results_revibed = search_revibed('', album)
#         elif artist:
#             st.session_state.results_revibed = search_revibed(artist, '')
#         else:
#             st.session_state.results_revibed = [{
#                 'platform': 'Revibed',
#                 'title': '',
#                 'artist': '',
#                 'album': '',
#                 'label': '',
#                 'price': '',
#                 'cover_url': '',
#                 'url': '',
#                 'search_time': 0.0,
#                 'message': "Für Revibed-Suche mindestens Album ODER Artist ausfüllen."
#             }]
#         st.rerun()

#     # --- BUTTON: Discogs & Revibed explizit suchen ---
#     if st.button("Auf Discogs und Revibed suchen", key="discogs_search_digital"):
#         st.session_state.discogs_revibed_mode = True
#         st.session_state.show_digital = False
#         artist = st.session_state.artist_input.strip()
#         album = st.session_state.album_input.strip()
#         track = st.session_state.track_for_search.strip()
#         st.session_state.results_discogs = search_discogs_releases(artist, track)
#         if album:
#             st.session_state.results_revibed = search_revibed('', album)
#         elif artist:
#             st.session_state.results_revibed = search_revibed(artist, '')
#         else:
#             st.session_state.results_revibed = [{
#                 'platform': 'Revibed',
#                 'title': '',
#                 'artist': '',
#                 'album': '',
#                 'label': '',
#                 'price': '',
#                 'cover_url': '',
#                 'url': '',
#                 'search_time': 0.0,
#                 'message': "Für Revibed-Suche mindestens Album ODER Artist ausfüllen."
#             }]
#         st.rerun()

# if st.session_state.get("suche_gestartet"):

    # # --------- 1. DISCOSGS/REVIBED MODUS (nur Discogs und Revibed) ---------
    # if st.session_state.discogs_revibed_mode:
    #     print("hello21")
    #     show_discogs_and_revibed_block(
    #         st.session_state.results_discogs,
    #         st.session_state.track_for_search.strip(),
    #         st.session_state.results_revibed
    #     )
    #     # Nutze st.session_state.results_discogs innerhalb von show_discogs_and_revibed_block!
    # else:
    #     print("hello3")
    #     # Hier alle Ergebnisse aus st.session_state.results_digital anzeigen
    #     # show_digital_block()
    #     show_live_results()


