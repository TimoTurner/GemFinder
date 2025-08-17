# main.py

import socket
import re
import streamlit as st
import requests
import datetime
import pandas as pd
from st_keyup import st_keyup
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Deine Modul-Imports ---
from providers_deployment import (
    SearchManager,
    DiscogsProvider, RevibedProvider,
    ItunesProvider, BeatportProvider, BandcampProvider, TraxsourceProvider
)
from state_manager import AppState
from ui_helpers_deployment import (
    show_live_results,
    show_revibed_fragment, show_discogs_block
)
from utils import get_platform_info, is_fuzzy_match

# Import deployment versions for Streamlit Cloud compatibility
import selenium_scraper_deployment as selenium_scraper
import scrape_search_deployment as scrape_search

from state_manager import AppState

# --- Helper function to fix common copy-paste errors ---
def fix_common_paste_errors(text):
    """
    Fix common human errors in copy-pasted music data
    """
    import re
    
    if not text:
        return text
    
    # 1. Fix multiple spaces (common in copy-paste)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 2. Fix missing spaces around common separators
    # "Artist-Title" → "Artist - Title"
    text = re.sub(r'([a-zA-Z])([–—-])([a-zA-Z])', r'\1 \2 \3', text)
    
    # 3. Fix double separators (common typo)
    # "Artist -- Title" → "Artist - Title"
    text = re.sub(r'[-–—]{2,}', '-', text)
    
    # 4. Fix spaces before punctuation (common in OCR/copy-paste)
    # "Artist - Title (" → "Artist - Title ("
    text = re.sub(r'\s+([.,;:!?\)\]])', r'\1', text)
    text = re.sub(r'([\(\[])\s+', r'\1', text)
    
    # 5. Fix common word separations (OCR errors)
    # "D aft Punk" → "Daft Punk"
    text = re.sub(r'\b([A-Z])\s+([a-z]{2,})', r'\1\2', text)
    
    # 6. Fix catalog number spacing issues
    # "ENV010" → "ENV 010", "E NV 010" → "ENV 010"
    text = re.sub(r'\b([A-Z]{2,6})(\d{2,6})\b', r'\1 \2', text)
    text = re.sub(r'\b([A-Z])\s+([A-Z]{1,5})\s+(\d{2,6})\b', r'\1\2 \3', text)
    
    # 7. Fix common feat/featuring spacing issues
    # "Artistfeat." → "Artist feat.", "feat.Artist" → "feat. Artist"
    text = re.sub(r'([a-zA-Z])(feat\.?|ft\.?)', r'\1 \2', text, flags=re.IGNORECASE)
    text = re.sub(r'(feat\.?|ft\.?)([A-Z])', r'\1 \2', text, flags=re.IGNORECASE)
    
    # 8. Fix parentheses spacing
    # "Title( Mix)" → "Title (Mix)", "Title (Mix )" → "Title (Mix)"
    text = re.sub(r'([a-zA-Z])\s*\(\s*', r'\1 (', text)
    text = re.sub(r'\s*\)\s*', r') ', text)
    text = re.sub(r'\)\s*$', r')', text)  # Remove trailing space after last parenthesis
    
    # 9. Fix bracket spacing
    text = re.sub(r'([a-zA-Z])\s*\[\s*', r'\1 [', text)
    text = re.sub(r'\s*\]\s*', r'] ', text)
    text = re.sub(r'\]\s*$', r']', text)
    
    # 10. Fix common remix/mix formatting
    # "Original mix" → "Original Mix" (proper capitalization)
    text = re.sub(r'\b(original|radio|extended|club|dub|instrumental)\s+(mix|edit|version)\b', 
                 lambda m: f"{m.group(1).title()} {m.group(2).title()}", text, flags=re.IGNORECASE)
    
    # 11. Fix ampersand spacing
    # "Artist&Artist" → "Artist & Artist", "Artist &Artist" → "Artist & Artist"
    text = re.sub(r'([a-zA-Z])&([a-zA-Z])', r'\1 & \2', text)
    text = re.sub(r'\s+&\s*([a-zA-Z])', r' & \1', text)
    text = re.sub(r'([a-zA-Z])\s*&\s+', r'\1 & ', text)
    
    # 12. Fix "vs" spacing issues
    text = re.sub(r'([a-zA-Z])vs\.?([a-zA-Z])', r'\1 vs. \2', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+vs\.?\s*([a-zA-Z])', r' vs. \1', text, flags=re.IGNORECASE)
    
    # 13. Final cleanup
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# --- Helper function for intelligent copy-paste parsing ---
def parse_music_data(text):
    """
    Intelligently parse copy-pasted music data and extract fields.
    Supports various formats like:
    - "Artist - Title"
    - "Artist - Album - Title"
    - "Title by Artist"
    - "Artist: Title"
    - Discogs URLs
    - Beatport URLs
    - Multi-line formats
    """
    import re
    
    if not text or not text.strip():
        return {}
    
    text = text.strip()
    result = {}
    
    # Pre-processing: Fix common copy-paste errors
    text = fix_common_paste_errors(text)
    
    # Check for URLs first
    if "discogs.com" in text.lower():
        # Extract from Discogs URL
        if "/release/" in text:
            # Try to extract release info from URL structure
            match = re.search(r'/release/(\d+)', text)
            if match:
                result["catalog_number"] = match.group(1)
        return result
    
    if "beatport.com" in text.lower() or "traxsource.com" in text.lower():
        # Extract from streaming platform URLs
        # These usually contain artist-title in the path
        parts = text.split('/')
        for part in parts:
            if '-' in part and len(part) > 10:
                # Likely artist-title part
                cleaned = part.replace('-', ' ').replace('_', ' ')
                return parse_music_data(cleaned)  # Recursive call
        return result
    
    # Multi-line parsing (each line is treated separately)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if len(lines) > 1:
        # Multi-track scenario
        tracks = []
        for line in lines:
            parsed = parse_music_data(line)
            if parsed.get("title"):
                tracks.append(parsed["title"])
        if tracks:
            result["tracks"] = "; ".join(tracks)
            # Use first line for other metadata
            first_parsed = parse_music_data(lines[0])
            result.update({k: v for k, v in first_parsed.items() if k != "title"})
        return result
    
    # Single line parsing patterns
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    
    # Pattern 1: "Artist - Title" or "Artist - Album - Title" (support various dash types)
    # Support multiple dash types: - – — (hyphen, en-dash, em-dash)
    dash_pattern = r'\s*[-–—]\s*'
    if re.search(dash_pattern, text):
        parts = [p.strip() for p in re.split(dash_pattern, text)]
        if len(parts) == 2:
            result["artist"] = parts[0]
            result["title"] = parts[1]
        elif len(parts) == 3:
            result["artist"] = parts[0]
            result["album"] = parts[1] 
            result["title"] = parts[2]
        elif len(parts) > 3:
            # Assume first is artist, last is title, middle parts are album
            result["artist"] = parts[0]
            result["title"] = parts[-1]
            result["album"] = " - ".join(parts[1:-1])
    
    # Pattern 2: "Title by Artist"
    elif ' by ' in text.lower():
        parts = re.split(r'\s+by\s+', text, flags=re.IGNORECASE)
        if len(parts) == 2:
            result["title"] = parts[0].strip()
            result["artist"] = parts[1].strip()
    
    # Pattern 3: "Artist: Title" or "Artist : Title"
    elif ':' in text:
        parts = [p.strip() for p in text.split(':', 1)]
        if len(parts) == 2:
            result["artist"] = parts[0]
            result["title"] = parts[1]
    
    # Pattern 4: Featuring/Collaboration formats
    # Handle "feat", "ft", "featuring", "&", "vs", "x" collaborations
    elif any(collab in text.lower() for collab in [' feat ', ' ft ', ' featuring ', ' & ', ' vs ', ' x ']):
        # Extract main artist and collaboration info
        collab_patterns = [
            (r'\s+(feat\.?|ft\.?|featuring)\s+(.+)', 'feat'),
            (r'\s+&\s+(.+)', 'collab'),
            (r'\s+(vs\.?|versus)\s+(.+)', 'vs'),
            (r'\s+x\s+(.+)', 'collab')
        ]
        
        for pattern, collab_type in collab_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                main_part = text[:match.start()].strip()
                collab_part = match.group(-1).strip()  # Last group
                
                # Try to parse main part as "Artist - Title"
                if re.search(dash_pattern, main_part):
                    main_parsed = [p.strip() for p in re.split(dash_pattern, main_part)]
                    if len(main_parsed) == 2:
                        result["artist"] = f"{main_parsed[0]} feat. {collab_part}" if collab_type == 'feat' else f"{main_parsed[0]} & {collab_part}"
                        result["title"] = main_parsed[1]
                        break
                else:
                    # Assume whole main part is artist
                    result["artist"] = f"{main_part} feat. {collab_part}" if collab_type == 'feat' else f"{main_part} & {collab_part}"
                    break
    
    # Pattern 4: Catalog number detection (letters/numbers pattern with brackets)
    catno_match = re.search(r'[\[\(]?([A-Z]{2,6}[\-\s]?\d{2,6})[\]\)]?', text)
    if catno_match:
        result["catalog_number"] = catno_match.group(1)  # Group 1 = without brackets
        # Remove entire catalog number including brackets from text and reparse
        remaining_text = text.replace(catno_match.group(0), '').strip()
        if remaining_text:
            remaining_parsed = parse_music_data(remaining_text)
            result.update(remaining_parsed)
    
    # Pattern 5: Year detection (4 digits)
    year_match = re.search(r'\b(19|20)\d{2}\b', text)
    if year_match:
        result["year"] = year_match.group(0)
    
    # Pattern 6: Mix version detection and cleanup
    # Clean up common mix suffixes from title if already parsed
    if result.get("title"):
        title = result["title"]
        # Remove common mix indicators that platforms auto-add
        mix_patterns = [
            r'\s*\(Original Mix\)$',
            r'\s*\(Radio Edit\)$', 
            r'\s*\(Extended Mix\)$',
            r'\s*\(Instrumental\)$',
            r'\s*\(Dub Mix\)$',
            r'\s*\(Club Mix\)$',
            r'\s*\(Original\)$'
        ]
        
        for pattern in mix_patterns:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        result["title"] = title.strip()
    
    # Pattern 7: Handle parentheses and brackets content
    # Extract remix info, year, or other metadata in parentheses
    if result.get("title"):
        title = result["title"]
        
        # Look for remix info in parentheses
        remix_match = re.search(r'\(([^)]*(?:remix|mix|edit|version|rework)[^)]*)\)', title, re.IGNORECASE)
        if remix_match:
            remix_info = remix_match.group(1)
            # Keep meaningful remix info, remove generic ones
            if not any(generic in remix_info.lower() for generic in ['original mix', 'radio edit', 'original']):
                # Keep the remix info as part of title for now
                pass
            else:
                # Remove generic remix info
                title = title.replace(remix_match.group(0), '').strip()
                result["title"] = title
    
    # Pattern 8: Handle quotation marks around titles
    if result.get("title"):
        title = result["title"]
        # Remove surrounding quotes if present
        if (title.startswith('"') and title.endswith('"')) or (title.startswith("'") and title.endswith("'")):
            result["title"] = title[1:-1].strip()
    
    # Fallback strategies for cases where no separators are found
    if not result and text:
        # Try to guess Artist - Title structure from word patterns
        fallback_result = guess_artist_title_fallback(text)
        if fallback_result:
            result.update(fallback_result)
        else:
            # Last resort: assume it's a title
            result["title"] = text
    
    return result

def guess_artist_title_fallback(text):
    """
    Fallback function to guess artist/title when no clear separators are found
    Uses heuristics based on common patterns
    """
    import re
    
    words = text.split()
    if len(words) < 2:
        return {"title": text}
    
    # Strategy 1: Look for title case patterns
    # Often artists are in title case, titles may have mixed case
    title_case_words = []
    other_words = []
    
    for i, word in enumerate(words):
        if word[0].isupper() and len(word) > 1 and word[1:].islower():
            title_case_words.append((i, word))
        else:
            other_words.append((i, word))
    
    # Strategy 2: Look for common artist name patterns
    # Two consecutive title case words often indicate artist name
    if len(title_case_words) >= 2:
        # Check if first few words are title case (likely artist)
        consecutive_title_case = 0
        for i, (pos, word) in enumerate(title_case_words):
            if pos == i:
                consecutive_title_case += 1
            else:
                break
        
        if consecutive_title_case >= 2 and consecutive_title_case < len(words):
            # Split at the end of consecutive title case words
            artist_words = words[:consecutive_title_case]
            title_words = words[consecutive_title_case:]
            
            return {
                "artist": " ".join(artist_words),
                "title": " ".join(title_words)
            }
    
    # Strategy 3: Look for common title indicators
    title_indicators = [
        r'\b(remix|mix|edit|version|rework|bootleg)\b',
        r'\b(love|night|day|time|life|world|heart|soul)\b',
        r'\b(the|a|an)\s+\w+',  # Articles often appear in titles
    ]
    
    for i, word in enumerate(words):
        for pattern in title_indicators:
            if re.search(pattern, word, re.IGNORECASE):
                # Split before this word (likely start of title)
                if i > 0:
                    return {
                        "artist": " ".join(words[:i]),
                        "title": " ".join(words[i:])
                    }
    
    # Strategy 4: Split at halfway point if text is long enough
    if len(words) >= 4:
        mid_point = len(words) // 2
        return {
            "artist": " ".join(words[:mid_point]),
            "title": " ".join(words[mid_point:])
        }
    
    # Strategy 5: Assume first word is artist if it's a proper noun
    if len(words) >= 2 and words[0][0].isupper():
        return {
            "artist": words[0],
            "title": " ".join(words[1:])
        }
    
    # Give up and return as title
    return {"title": text}

discogs_provider = DiscogsProvider()
revibed_provider = RevibedProvider()

app_state = AppState()   # initialisiert session_state mit allen Default-Keys

st.set_page_config(page_title="GEM DETECTOR", layout="wide")
app_state = AppState()

# Add CSS and JavaScript to prevent jumping to "remembered" scroll positions
st.markdown("""
<style>
.main .block-container {
    scroll-behavior: auto;
}
.stRadio > div {
    min-height: auto;
}
</style>
<script>
// Prevent jumping to "remembered" scroll positions
(function() {
    let currentScrollY = 0;
    
    // Capture scroll position before any radio button click
    function captureScrollPosition() {
        currentScrollY = window.scrollY;
        sessionStorage.setItem('preserveScrollY', currentScrollY.toString());
    }
    
    // Restore scroll position after page rerun
    function restoreScrollPosition() {
        const savedY = sessionStorage.getItem('preserveScrollY');
        if (savedY) {
            const scrollY = parseInt(savedY, 10);
            window.scrollTo(0, scrollY);
            sessionStorage.removeItem('preserveScrollY');
        }
    }
    
    // Set up listeners when DOM is ready
    function setupScrollPreservation() {
        // Capture position before radio button interactions
        const radioButtons = document.querySelectorAll('input[type="radio"]');
        radioButtons.forEach(radio => {
            radio.addEventListener('click', captureScrollPosition);
            radio.addEventListener('change', captureScrollPosition);
        });
    }
    
    // Initial setup
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupScrollPreservation);
    } else {
        setupScrollPreservation();
    }
    
    // Restore position after rerun
    restoreScrollPosition();
    
    // Re-setup listeners after Streamlit reruns
    setTimeout(setupScrollPreservation, 100);
})();
</script>
""", unsafe_allow_html=True)

# Clear render flags from previous script run
if "discogs_rendered_this_run" in st.session_state:
    del st.session_state.discogs_rendered_this_run
# DON'T clear discogs_just_rendered here - it should persist during the same run
# It will be cleared at the end of the script or when explicitly needed

# Store scroll position in session state
if "scroll_position" not in st.session_state:
    st.session_state.scroll_position = 0

# --- Header ---
# st.image("record_mole_copy.png", width=220)
st.image(os.path.join(os.path.dirname(__file__), "record_mole_copy.png"), width=220)     
st.title("GEM DETECTOR")
# Create containers with unique keys to force recreation on mode switches
container_key = f"containers_{st.session_state.get('container_generation', 0)}"
# Creating UI containers

live_placeholder      = st.empty()
secondary_placeholder = st.empty()

# --- Mode-Auswahl ---
mode = st.radio("Choose Input Mode:", 
                ("Manual Input","Take a picture","Upload photo"),
                key="input_mode")

# --- Paste and Reset Buttons (very compact) ---
col_buttons, col_spacer = st.columns([1, 3])

with col_buttons:
    # Check if paste was already used in this session
    paste_already_used = st.session_state.get("paste_used", False)
    
    # Put both buttons in the same narrow column with minimal spacing
    subcol1, subcol2 = st.columns([1, 1])
    
    with subcol1:
        if not paste_already_used:
            if st.button("Paste", key="paste_button"):
                # Simple approach - trigger a paste dialog
                st.session_state.show_paste_dialog = True
                st.rerun()
        else:
            st.button("Paste", key="paste_button_disabled", disabled=True, help="Paste already used. Use Reset to enable again.")
    
    with subcol2:
        reset_clicked = st.button("Reset", key="reset_button")

# Handle reset outside of columns to avoid layout issues
if reset_clicked:
    # Complete page reload - clear everything and start fresh
    import streamlit.components.v1 as components
    components.html("""
    <script>
    window.parent.location.reload();
    </script>
    """, height=0)

# Show simple paste dialog when triggered
if st.session_state.get("show_paste_dialog", False):
    # Use st_keyup for immediate processing
    paste_content = st_keyup(
        "Paste here (Ctrl+V):",
        key="paste_input_field",
        placeholder="Paste your music data here...",
        debounce=300
    )
    
    # Auto-process when content is entered
    if paste_content and paste_content.strip():
        parsed = parse_music_data(paste_content)
        
        # Apply parsed data directly to session state
        if parsed.get("tracks"):
            st.session_state.tracks_input = parsed["tracks"]
        elif parsed.get("title"):
            st.session_state.tracks_input = parsed["title"]
        
        if parsed.get("artist"):
            st.session_state.artist_input = parsed["artist"]
        if parsed.get("album"):
            st.session_state.album_input = parsed["album"]
        if parsed.get("catalog_number"):
            st.session_state.catalog_number_input = parsed["catalog_number"]
        
        # Mark paste as used and close dialog
        st.session_state.paste_used = True
        st.session_state.show_paste_dialog = False
        
        # Force input field refresh by incrementing reset counter
        if "reset_counter" not in st.session_state:
            st.session_state.reset_counter = 0
        st.session_state.reset_counter += 1
        
        st.success(f"✅ Pasted and parsed: {len([k for k in parsed.keys() if parsed[k]])} fields filled!")
        st.rerun()
    
    # Cancel option
    if st.button("Cancel", key="cancel_paste_dialog"):
        st.session_state.show_paste_dialog = False
        st.rerun()

if mode != st.session_state.last_mode:
    app_state.reset_search()
    # Clear photo processing states when mode changes
    if "last_processed_file" in st.session_state:
        del st.session_state["last_processed_file"]
    if "last_processed_camera" in st.session_state:
        del st.session_state["last_processed_camera"]
    
    # Clear all input fields when switching modes
    st.session_state.tracks_input = ""
    st.session_state.artist_input = ""
    st.session_state.album_input = ""
    st.session_state.catalog_number_input = ""
    
    # Clear the keyup component keys to force them to reset
    keyup_keys = ["tracks_keyup", "artist_keyup", "catalog_keyup", "album_keyup"]
    for key in keyup_keys:
        # Clear both with and without reset suffix
        if key in st.session_state:
            del st.session_state[key]
        # Clear with all possible reset suffixes
        for i in range(10):  # Clear up to 10 possible reset suffixes
            suffixed_key = f"{key}_{i}"
            if suffixed_key in st.session_state:
                del st.session_state[suffixed_key]
    
    # Increment reset counter to force component recreation with new keys
    if "reset_counter" not in st.session_state:
        st.session_state.reset_counter = 0
    st.session_state.reset_counter += 1
    
    st.session_state.last_mode = mode
    st.rerun()

# --- Helper function to create input fields ---
def create_input_fields(reset_suffix=""):
    """Create the standard input fields used across all modes"""
    # Use SAME logic as button: disable inputs when search started OR cache valid
    search_started = st.session_state.get("suche_gestartet", False)
    cache_valid = AppState().is_cache_valid() if search_started else False
    inputs_disabled = search_started and cache_valid
    
    print(f"🔍 DEBUG: search_started={search_started}, cache_valid={cache_valid}, inputs_disabled={inputs_disabled}")
    
    if inputs_disabled:
        # Show disabled text inputs when search is active
        st.text_input(
            "Track(s) - separate multiple tracks with semicolon", 
            value=st.session_state.get("tracks_input", ""),
            disabled=True,
            key=f"tracks_disabled{reset_suffix}"
        )
        st.caption("🔒 Inputs locked - use Reset button to modify search criteria")
        
        st.text_input(
            "Artist", 
            value=st.session_state.get("artist_input", ""),
            disabled=True,
            key=f"artist_disabled{reset_suffix}"
        )
        
        st.text_input(
            "Catalog Number", 
            value=st.session_state.get("catalog_number_input", ""),
            disabled=True,
            key=f"catalog_disabled{reset_suffix}"
        )
        
        st.text_input(
            "Album", 
            value=st.session_state.get("album_input", ""),
            disabled=True,
            key=f"album_disabled{reset_suffix}"
        )
    else:
        # Show normal interactive inputs when no search is active
        tracks_input = st_keyup(
            "Track(s) - separate multiple tracks with semicolon", 
            value=st.session_state.get("tracks_input", ""),
            debounce=100,  # Quick response for button updates
            key=f"tracks_keyup{reset_suffix}"
        )
        st.caption("Enter one or more track titles separated by semicolon (;)")
        if tracks_input != st.session_state.get("tracks_input", ""):
            st.session_state.tracks_input = tracks_input

        artist_input = st_keyup(
            "Artist", 
            value=st.session_state.get("artist_input", ""),
            debounce=100,  # Quick response for button updates
            key=f"artist_keyup{reset_suffix}"
        )
        if artist_input != st.session_state.get("artist_input", ""):
            st.session_state.artist_input = artist_input

        catalog_input = st_keyup(
            "Catalog Number", 
            value=st.session_state.get("catalog_number_input", ""),
            debounce=100,  # Quick response for button updates
            key=f"catalog_keyup{reset_suffix}"
        )
        if catalog_input != st.session_state.get("catalog_number_input", ""):
            st.session_state.catalog_number_input = catalog_input

        album_input = st_keyup(
            "Album", 
            value=st.session_state.get("album_input", ""),
            debounce=100,  # Quick response for button updates
            key=f"album_keyup{reset_suffix}"
        )
        if album_input != st.session_state.get("album_input", ""):
            st.session_state.album_input = album_input

# --- Helper function to check if button should be enabled ---
def check_button_state():
    """Check if search criteria are met and update button state"""
    app_state = AppState()
    criteria = app_state.get_criteria()
    
    # Provider lists
    digital_providers   = [ItunesProvider(), BeatportProvider(), BandcampProvider(), TraxsourceProvider()]
    secondary_providers = [DiscogsProvider(), RevibedProvider()]
    
    # Check which platforms can search with current criteria
    can_search_digital   = any(p.can_search(criteria) for p in digital_providers)
    can_search_secondary = any(p.can_search(criteria) for p in secondary_providers)
    
    # Update session state for button enabling
    st.session_state.can_search = can_search_digital or can_search_secondary
    return can_search_digital or can_search_secondary

def search_platform_thread_safe(provider, criteria):                                                                        
    """Thread-safe search ohne UI-Updates"""                    
    try: 
        result = provider.search(criteria)       
        return {"status": "success", "result": result, "provider": provider.name}                                                                                                                      
    except Exception as e:                    
        return {"status": "error", "error": str(e), "provider": provider.name}                                                                                                                                                                                                      

# --- Input Interface Based on Selected Mode ---
reset_suffix = f"_{st.session_state.get('reset_counter', 0)}"

if mode == "Manual Input":
    # --- Manual Input Fields ---
    create_input_fields(reset_suffix)

elif mode == "Upload photo":
    # --- Photo Upload Interface ---
    st.markdown("### 📸 Upload Photo")
    
    # Only show info text if no file has been processed
    if not st.session_state.get("last_processed_file"):
        st.info("Upload a photo of an album cover, label, or track listing to extract information automatically.")
    
    uploaded_file = st.file_uploader(
        "Choose an image file", 
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
        key="photo_upload"
    )
    
    if uploaded_file is not None:
        # Check if we've already processed this file
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.get("last_processed_file") != file_id:
            with st.spinner("🤖 Analyzing image and extracting text..."):
                from text_extract import extract_text_from_image, analyze_text_with_gpt4
                
                # Extract text from image
                extracted_text = extract_text_from_image(uploaded_file)
                
                # Analyze text to get structured fields (upload mode = discogs-only scenario)
                artist, album, tracks, label, catalog = analyze_text_with_gpt4(extracted_text, mode_context='upload')
                
                # Debug: Show what was extracted
                st.write("🔍 DEBUG - Upload mode extracted:")
                st.write(f"Artist: '{artist}'")
                st.write(f"Album: '{album}'") 
                st.write(f"Tracks: {tracks}")
                st.write(f"Label: '{label}'")
                st.write(f"Catalog: '{catalog}'")
                
                # Force update session state with ALL extracted information
                st.session_state.artist_input = str(artist) if artist else ""
                st.session_state.album_input = str(album) if album else ""
                st.session_state.catalog_number_input = str(catalog) if catalog else ""
                
                # Handle tracks (join if list, or use as string)
                if tracks:
                    if isinstance(tracks, list):
                        track_list = [str(t).strip() for t in tracks if str(t).strip()]
                        st.session_state.tracks_input = "; ".join(track_list) if track_list else ""
                    else:
                        st.session_state.tracks_input = str(tracks) if tracks else ""
                else:
                    st.session_state.tracks_input = ""
                
                # Remember that we processed this file
                st.session_state.last_processed_file = file_id
                
                st.success("✅ Text extracted and fields populated!")
                st.rerun()
            
    
    # Show the regular manual input fields (same as manual mode)
    create_input_fields(reset_suffix)

elif mode == "Take a picture":
    # --- Camera Interface ---
    st.markdown("### 📷 Take a Picture")
    
    # Only show info text if no photo has been processed
    if not st.session_state.get("last_processed_camera"):
        st.info("Use your device's camera to capture an album cover, label, or track listing.")
    
    # Camera and retake logic
    if not st.session_state.get("last_processed_camera"):
        # Show camera input for first photo (may not work in Streamlit Cloud)
        try:
            camera_photo = st.camera_input("📸 Take a photo")
        except Exception as e:
            st.error("📱 Camera not available in cloud environment. Please use 'Upload photo' mode instead.")
            camera_photo = None
    else:
        # Photo already taken - show retake button
        camera_photo = None
        if st.button("🔄 Retake Picture", key="retake_photo_btn"):
            # Clear the processed camera state to allow retaking
            if "last_processed_camera" in st.session_state:
                del st.session_state["last_processed_camera"]
            st.rerun()
    
    if camera_photo is not None:
        # Check if we've already processed this photo
        photo_id = f"camera_{camera_photo.size}_{hash(camera_photo.getvalue())}"
        if st.session_state.get("last_processed_camera") != photo_id:
            with st.spinner("🤖 Analyzing photo and extracting text..."):
                from text_extract import extract_text_from_image, analyze_text_with_gpt4
                
                # Extract text from image
                extracted_text = extract_text_from_image(camera_photo)
                
                # Analyze text to get structured fields (camera mode = revibed scenario)
                artist, album, tracks, label, catalog = analyze_text_with_gpt4(extracted_text, mode_context='camera')
                
                # Debug: Show what was extracted
                st.write("🔍 DEBUG - Camera mode extracted:")
                st.write(f"Artist: '{artist}'")
                st.write(f"Album: '{album}'") 
                st.write(f"Tracks: {tracks}")
                st.write(f"Label: '{label}'")
                st.write(f"Catalog: '{catalog}'")
                
                # Force update session state with ALL extracted information
                st.session_state.artist_input = str(artist) if artist else ""
                st.session_state.album_input = str(album) if album else ""
                st.session_state.catalog_number_input = str(catalog) if catalog else ""
                
                # Handle tracks (join if list, or use as string)
                if tracks:
                    if isinstance(tracks, list):
                        track_list = [str(t).strip() for t in tracks if str(t).strip()]
                        st.session_state.tracks_input = "; ".join(track_list) if track_list else ""
                    else:
                        st.session_state.tracks_input = str(tracks) if tracks else ""
                else:
                    st.session_state.tracks_input = ""
                
                # Remember that we processed this photo
                st.session_state.last_processed_camera = photo_id
                
                st.success("✅ Text extracted and fields populated!")
                st.rerun()
            
    
    # Show the regular manual input fields (same as manual mode)
    create_input_fields(reset_suffix)

# Check if input criteria have changed and update button state immediately
check_button_state()

# --- Track-Auswahl MOVED TO TOP (to minimize jumping impact) ---
track_list = [t.strip() for t in st.session_state.tracks_input.split(';') if t.strip()]
track_search_clicked = False

if track_list:
    if len(track_list) > 1:
        # Initialize with first track if not already set
        if "selected_track" not in st.session_state or st.session_state.selected_track not in track_list:
            st.session_state.selected_track = track_list[0]
        
        # Create sticky container for track selection
        st.markdown("### 🎵 Track Selection")
        
        # Create columns to make layout more stable
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_track = st.selectbox(
                "Choose a track for search:", 
                options=track_list,
                index=track_list.index(st.session_state.selected_track) if st.session_state.selected_track in track_list else 0,
                key="track_select"
            )
            st.session_state.selected_track = selected_track
        
        with col2:
            # Add dedicated search button for track switching
            st.write("")  # Add some spacing
            track_search_clicked = st.button(
                f"🔍 Search: {selected_track[:20]}..." if len(selected_track) > 20 else f"🔍 Search: {selected_track}",
                key="track_search_button",
                type="primary",
                use_container_width=True
            )
        
        st.markdown("---")
        
    else:
        st.session_state.selected_track = track_list[0]
else:
    st.session_state.selected_track = ""

# ggf. Label-Feld ...
live_container      = st.container()
secondary_container = st.container()

# --- Search button validation and criteria checking ---
app_state = AppState()
criteria = app_state.get_criteria()

# Provider lists
digital_providers   = [ItunesProvider(), BeatportProvider(), BandcampProvider(), TraxsourceProvider()]
secondary_providers = [DiscogsProvider()]  # Revibed wird separat über Button gesucht
revibed_provider = RevibedProvider()

# Check which platforms can search with current criteria
can_search_digital   = any(p.can_search(criteria) for p in digital_providers)
can_search_secondary = any(p.can_search(criteria) for p in secondary_providers)
can_search = can_search_digital or can_search_secondary

# Proactive reset: If search was done but cache is now invalid, reset immediately
# BUT: Don't reset if search is completed (inputs are disabled) - preserve results!
search_started = st.session_state.get("suche_gestartet", False)
digital_search_done = st.session_state.get("digital_search_done", False)
cache_valid = app_state.is_cache_valid()
search_completed = search_started and digital_search_done and cache_valid

print(f"🔍 RESET DEBUG: search_started={search_started}, digital_done={digital_search_done}, cache_valid={cache_valid}, search_completed={search_completed}")

if search_started and not cache_valid and not search_completed:
    
    print(f"🔄 DEBUG: Proactive reset triggered - search not completed yet")
    # Explicitly invalidate cache
    app_state.invalidate_cache()
    
    # Reset search state completely
    st.session_state.suche_gestartet = False
    st.session_state.digital_search_done = False
    st.session_state.secondary_search_done = False
    st.session_state.has_digital_hits = False
    st.session_state.show_digital = True
    st.session_state.discogs_revibed_mode = False
    st.session_state.results_digital = []
    st.session_state.results_discogs = []
    st.session_state.results_revibed = []
else:
    if search_completed:
        print(f"🔒 DEBUG: Search completed - preserving results despite cache invalidation")

# Show which platforms will be searched - use placeholder that can be cleared later
search_info_placeholder = st.empty()
st.session_state.search_info_placeholder = search_info_placeholder

if not st.session_state.get("suche_gestartet", False) and not app_state.is_cache_valid():
    if can_search:
        searchable_platforms = []
        if can_search_digital:
            searchable_platforms.extend([p.name for p in digital_providers if p.can_search(criteria)])
        if can_search_secondary:
            searchable_platforms.extend([p.name for p in secondary_providers if p.can_search(criteria)])
        search_info_placeholder.info(f"Ready to search: {', '.join(searchable_platforms)}")
    else:
        search_info_placeholder.warning("Please fill in minimum required fields to enable search.")
else:
    search_info_placeholder.empty()

# Search button - use placeholder that can be cleared later
search_button_placeholder = st.empty()
st.session_state.search_button_placeholder = search_button_placeholder

# Only show general search button when NOT in multi-track mode
if not st.session_state.get("suche_gestartet", False) and not app_state.is_cache_valid() and len(track_list) <= 1:
    with search_button_placeholder:
        search_clicked = st.button(
            "Save and Search",
            disabled=not can_search,
            key="btn_suche"
        )
else:
    search_button_placeholder.empty()
    search_clicked = False

if search_clicked or track_search_clicked:
    # IMMEDIATELY set search state to disable inputs AND start search
    print(f"🔘 DEBUG: Button clicked! Setting suche_gestartet = True and starting search")
    st.session_state.suche_gestartet = True
    
    # Clear the flag for next search
    if "inputs_disabled_rerun_done" in st.session_state:
        del st.session_state.inputs_disabled_rerun_done
    
    # Force cache invalidation when track search button is clicked
    if track_search_clicked:
        app_state.invalidate_cache()
    
    # Always check if cache is valid for current criteria
    # If criteria changed, invalidate cache and perform new search
    if not app_state.is_cache_valid():
        app_state.invalidate_cache()
        
        # Set search state
        st.session_state.track_for_search = st.session_state.selected_track
        # Clear the search info and button placeholders
        if hasattr(st.session_state, 'search_info_placeholder'):
            st.session_state.search_info_placeholder.empty()
        if hasattr(st.session_state, 'search_button_placeholder'):
            st.session_state.search_button_placeholder.empty()

        app_state.update_cache_criteria()
        
        # Reset containers and live results
        live_container.empty()
        secondary_container.empty()
        st.session_state.live_results = []
        st.session_state.mode_switch_button_shown = False  # Reset button flag for new search
        
        # Reset live results containers for new search
        if "live_results_containers" in st.session_state:
            st.session_state.live_results_containers = {}
        if "live_results_header_shown" in st.session_state:
            st.session_state.live_results_header_shown = False

        # Stage 1: Search digital platforms if criteria met
        if can_search_digital:
            # Starting optimized digital search
            st.session_state.show_digital = True  
            st.session_state.discogs_revibed_mode = False
            
            # Digital platforms parallel search (iTunes will be re-added later)
            
            # Show progress bar immediately when search starts
# Debug output removed
            with live_container:
                show_live_results()
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {executor.submit(search_platform_thread_safe, p, criteria): p 
                          for p in digital_providers if p.can_search(criteria)}
                
                # Live Updates während Threads laufen
                for future in as_completed(futures):
                    thread_result = future.result()
                    
                    if thread_result["status"] == "success":
                        entry = thread_result["result"]
                    else:
                        # Use structured error message instead of generic "Fehler"
                        error_msg = thread_result.get("error", "Unknown error")
                        error_title = f"🔧 {thread_result['provider']} Error: {str(error_msg)[:40]}..."
                        entry = {
                            "platform": thread_result["provider"],
                            "title": error_title,
                            "artist": "",
                            "album": "",
                            "label": "",
                            "price": "",
                            "cover_url": "",
                            "url": "",
                            "error": error_msg
                        }
                    
                    # SOFORT anzeigen sobald Thread fertig
                    st.session_state.live_results.append(entry)
                    st.session_state.results_digital.append(entry)
# Debug output removed
                    with live_container:
                        show_live_results()

            # Mark digital search as done
            st.session_state.digital_search_done = True
            
            # Check for real hits - updated to recognize new error handling messages
            real_hits = []
            for r in st.session_state.results_digital:
                title = (r.get("title") or "").strip().lower()
                # Old error patterns
                old_patterns = ("kein treffer", "", "fehler")
                # New structured error patterns from error handling system
                new_error_patterns = (
                    "❌", "🔴", "🔧", "📭", "🚫", "🐌", "⚡", "🔒", 
                    "not reachable", "nicht verfügbar", "not available",
                    "initialization failed", "browser error", "timeout",
                    "no search terms", "keine suchbegriffe"
                )
                
                # Check if this is a real hit (not an error message)
                is_error = (
                    title in old_patterns or 
                    any(pattern in title for pattern in new_error_patterns)
                )
                
                if not is_error:
                    real_hits.append(r)

            
            st.session_state.has_digital_hits = len(real_hits) > 0

            if st.session_state.has_digital_hits:
                # Stage 1 complete: Show final results
                if "live_progress_container" in st.session_state:
                    st.session_state.live_progress_container.empty()
                
                # Final call to show_live_results to display results
# Debug output removed
                with live_container:
                    show_live_results()
            elif can_search_secondary:
                # Stage 2: No digital hits -> hide digital container and switch to secondary platforms
# Debug output removed
                
                # Use the same clearing logic as mode-switch button (bewährte Funktion!)
                # Clear containers to remove live results and header
                live_container.empty()  # This removes the "Digital Results" header and any content
                # Don't clear secondary_container here since we'll use it immediately below
                
                if "live_results_containers" in st.session_state:
                    for container in st.session_state.live_results_containers.values():
                        container.empty()
                
                # Clear the header container as well
                if "live_results_header_container" in st.session_state:
                    st.session_state.live_results_header_container.empty()
                
                # Clear progress bar
                if "live_progress_container" in st.session_state:
                    st.session_state.live_progress_container.empty()
                
                # Set flags for secondary mode
                st.session_state.discogs_revibed_mode = True
                st.session_state.show_digital = False
                
                # Clear digital results completely to prevent re-display
                st.session_state.results_digital = []
                st.session_state.live_results = []
                
                # Search only Discogs automatically
                for p in secondary_providers:
                    if p.can_search(criteria):
                        result = p.search(criteria)
                        if p.name == "Discogs":
                            st.session_state.results_discogs = result.get("releases", [])  # Extract releases list from dict
                
                # Initialize empty revibed results - will be filled on button click
                if "results_revibed" not in st.session_state:
                    st.session_state.results_revibed = []
                
                # Use the same progress container as normal secondary search
                if "live_progress_container" not in st.session_state:
                    st.session_state.live_progress_container = st.empty()
                
                # Show progress bar exactly like normal secondary search
                searchable_secondary = [p for p in secondary_providers if p.can_search(criteria)]
                searchable_secondary.sort(key=lambda p: 0 if p.name == "Discogs" else 1)
                
                with st.session_state.live_progress_container.container():
                    progress_text = ", ".join([f"{p.name} ⏳" for p in searchable_secondary])
                    st.info(f"🔍 Searching: {progress_text}")
                    st.progress(0)
                
                # Search with progress updates (same as normal secondary search)
                for i, p in enumerate(searchable_secondary):
# Debug output removed
                    
                    # Update progress during search
                    with st.session_state.live_progress_container.container():
                        st.info(f"🔍 Searching: {p.name} ⏳")
                        st.progress(0.5)
                    
                    # Perform search
                    result = p.search(criteria)
                    if p.name == "Discogs":
                        st.session_state.results_discogs = result.get("releases", [])
# Debug output removed
                        
                        # Discogs results will be processed - gem message handled after loop
                        
                        # Show Discogs results immediately - mark as real gem since no digital hits but Discogs hits
                        with secondary_container:
                            show_discogs_block(st.session_state.results_discogs, st.session_state.track_for_search, is_real_gem=True)
                    
                    # Update progress after completion
                    with st.session_state.live_progress_container.container():
                        st.info(f"🔍 Searching: {p.name} ✅")
                        st.progress(1.0)
                
                # Clear progress bar after completion
                st.session_state.live_progress_container.empty()
                
                # Real gem message will be shown in show_discogs_block function
                
                st.session_state.secondary_search_done = True
                st.session_state.secondary_search_active = False  # Reset flag - same as normal secondary search
                st.session_state.discogs_just_rendered = True  # Prevent cached results from re-rendering in same run
                # Keep suche_gestartet = True for normal button functionality - CRITICAL for cached results logic!

        # If only secondary platforms can search
        elif can_search_secondary:
            st.session_state.discogs_revibed_mode = True
            st.session_state.show_digital = False
            
            # Use the same secondary search logic as auto-switch case
            if "live_progress_container" not in st.session_state:
                st.session_state.live_progress_container = st.empty()
            
            searchable_secondary = [p for p in secondary_providers if p.can_search(criteria)]
            searchable_secondary.sort(key=lambda p: 0 if p.name == "Discogs" else 1)
            
            with st.session_state.live_progress_container.container():
                progress_text = ", ".join([f"{p.name} ⏳" for p in searchable_secondary])
                st.info(f"🔍 Searching: {progress_text}")
                st.progress(0)
            
            for i, p in enumerate(searchable_secondary):
                with st.session_state.live_progress_container.container():
                    st.info(f"🔍 Searching: {p.name} ⏳")
                    st.progress(0.5)
                
                result = p.search(criteria)
                if p.name == "Discogs":
                    st.session_state.results_discogs = result.get("releases", [])
                    with secondary_container:
                        show_discogs_block(st.session_state.results_discogs, st.session_state.track_for_search)
                        st.session_state.discogs_just_rendered = True  # Prevent cached results from re-rendering
                
                with st.session_state.live_progress_container.container():
                    st.info(f"🔍 Searching: {p.name} ✅")
                    st.progress(1.0)
            
            st.session_state.live_progress_container.empty()
            
            # Initialize empty revibed results - will be filled on button click
            if "results_revibed" not in st.session_state:
                st.session_state.results_revibed = []
            
            st.session_state.secondary_search_done = True
            st.session_state.secondary_search_active = False

# Reset when search criteria changed (cache invalid but search was started)
elif st.session_state.suche_gestartet and not app_state.is_cache_valid():
    # Clear containers and reset all search-related state
    live_container.empty()
    secondary_container.empty()
    
    # Reset search state completely
    st.session_state.suche_gestartet = False
    st.session_state.digital_search_done = False
    st.session_state.secondary_search_done = False
    st.session_state.has_digital_hits = False
    st.session_state.show_digital = True
    st.session_state.discogs_revibed_mode = False
    st.session_state.results_digital = []
    st.session_state.results_discogs = []
    st.session_state.results_revibed = []

# Handle switch to cached secondary results - FORCE COMPLETE RESET
if st.session_state.get("switch_to_cached_secondary", False):
# Debug output removed
    st.session_state.switch_to_cached_secondary = False  # Reset flag
    
    # Change flags without container recreation
    st.session_state.discogs_revibed_mode = True
    st.session_state.show_digital = False
    
    # Clear all container states
    for key in list(st.session_state.keys()):
        if key.startswith(('live_results_', 'live_progress_', 'secondary_progress_')):
            del st.session_state[key]

# Handle switch back to digital results
if st.session_state.get("switch_to_digital", False):
# Debug output removed
    st.session_state.switch_to_digital = False  # Reset flag
    
    # Change flags for digital mode
    st.session_state.discogs_revibed_mode = False
    st.session_state.show_digital = True
    st.session_state.mode_switch_button_shown = False
    
    # Ensure digital_search_done is set
    if not st.session_state.get("digital_search_done", False):
        st.session_state.digital_search_done = True
    
    # Clear container states for clean switch
    for key in list(st.session_state.keys()):
        if key.startswith(('live_results_', 'live_progress_', 'secondary_progress_')):
            del st.session_state[key]

# Handle Revibed search trigger from button
if st.session_state.get("trigger_revibed_search", False):
# Debug output removed
    st.session_state.trigger_revibed_search = False  # Reset flag SOFORT
    
    # Search only Revibed if criteria met
    if revibed_provider.can_search(criteria):
        with st.spinner("🔍 Searching Revibed..."):
            results = revibed_provider.search(criteria)  # Now returns list
            st.session_state.results_revibed = results
# Debug output removed
    else:
        pass  # Revibed search skipped - criteria not met

# Handle secondary search trigger from mode switch button
# Debug output removed to reduce noise

if st.session_state.get("trigger_secondary_search", False) and can_search_secondary:
# Debug output removed
    st.session_state.trigger_secondary_search = False  # Reset flag
    
    # Clear containers to remove verblasste results and header (keep progress container for secondary search)
    live_container.empty()  # This removes the "Digital Results" header and any content in live_container
    # Don't clear secondary_container here since we'll use it immediately below for Discogs results
    
    if "live_results_containers" in st.session_state:
        for container in st.session_state.live_results_containers.values():
            container.empty()
    
    # Clear the header container as well
    if "live_results_header_container" in st.session_state:
        st.session_state.live_results_header_container.empty()
    
# Debug output removed
    
    # Switch to secondary mode
    st.session_state.discogs_revibed_mode = True
    st.session_state.show_digital = False
    
    # Use the same progress container as digital search for consistent UI position
    if "live_progress_container" not in st.session_state:
        st.session_state.live_progress_container = st.empty()
    
    # Show progress bar with platform status (same as digital search)
    searchable_secondary = [p for p in secondary_providers if p.can_search(criteria)]
    
    # Ensure Discogs comes first for better user experience (~0.3s vs ~2s)
    searchable_secondary.sort(key=lambda p: 0 if p.name == "Discogs" else 1)
    
    with st.session_state.live_progress_container.container():
        progress_text = ", ".join([f"{p.name} ⏳" for p in searchable_secondary])
        st.info(f"🔍 Searching: {progress_text}")
        st.progress(0)
    
    # Search only Discogs in secondary search (Revibed is now button-triggered)
    for i, p in enumerate(searchable_secondary):
# Debug output removed
        
        # Update progress during search
        with st.session_state.live_progress_container.container():
            st.info(f"🔍 Searching: {p.name} ⏳")
            st.progress(0.5)
        
        # Perform search
        result = p.search(criteria)
        if p.name == "Discogs":
            st.session_state.results_discogs = result.get("releases", [])
# Debug output removed
            # Show Discogs results immediately
            with secondary_container:
                show_discogs_block(st.session_state.results_discogs, st.session_state.track_for_search)
                st.session_state.discogs_just_rendered = True  # Prevent cached results from re-rendering
        
        # Update progress after completion
        with st.session_state.live_progress_container.container():
            st.info(f"🔍 Searching: {p.name} ✅")
            st.progress(1.0)
    
    # Clear progress bar after completion
    st.session_state.live_progress_container.empty()
    
    st.session_state.secondary_search_done = True
    st.session_state.secondary_search_active = False  # Reset flag - secondary search complete
    # Results are already displayed individually as they complete

# Display cached results if search already done and cache is valid
# Changed from elif to if to always show cached results
if st.session_state.suche_gestartet and app_state.is_cache_valid():
    # Don't show digital results if we're in secondary mode
    if st.session_state.show_digital and st.session_state.digital_search_done and not st.session_state.get("discogs_revibed_mode", False):
        # Show cached digital results via live container
# Debug output removed
        with live_container:
            show_live_results()
    else:
# Debug output removed
        # Ensure live container is empty when not showing digital results
        live_container.empty()
    
    discogs_just_rendered = st.session_state.get("discogs_just_rendered", False)
# Debug output removed
    
    if (st.session_state.discogs_revibed_mode and 
        st.session_state.secondary_search_done and
        not discogs_just_rendered):
# Debug output removed
        # Show cached secondary results - now completely separated
        with secondary_container:
            # Enhanced Discogs block (normal rendering)
# Debug output removed
            show_discogs_block(
                st.session_state.results_discogs, 
                st.session_state.track_for_search
            )
            # Set flag to prevent any duplicate rendering in the same run
            st.session_state.discogs_just_rendered = True
            # Revibed fragment only if search was triggered
            if st.session_state.results_revibed:
                show_revibed_fragment(st.session_state.results_revibed)
    else:
        pass  # Cached results conditions not met

# Mode switch buttons - placed at the very end, outside all containers
if (st.session_state.get("digital_search_done", False) and 
    st.session_state.get("has_digital_hits", False) and 
    can_search_secondary and
    st.session_state.get("show_digital", True)):
    
    if not st.session_state.get("secondary_search_done", False):
        # First time - show search button
# Debug output removed
        if st.button("🔄 Search on Discogs and Revibed", key="final_switch", type="primary"):
# Debug output removed
            st.session_state.trigger_secondary_search = True
            st.rerun()
    else:
        # Secondary search already done - show switch button for cached results
# Debug output removed
        if st.button("🔄 Switch to Discogs and Revibed", key="switch_cached", type="secondary"):
# Debug output removed
            # Set flag to trigger clean switch (bewährtes Pattern)
            st.session_state.switch_to_cached_secondary = True
            st.rerun()

# Zurück-Button ganz unten auf der Seite - außerhalb aller Container
# Wird angezeigt wenn wir im secondary mode sind UND digitale Hits existieren
if (st.session_state.get("discogs_revibed_mode", False) and 
    st.session_state.get("has_digital_hits", False)):
    st.markdown("---")
    if st.button("🔙 Zurück zu digitalen Shops", key="back_to_digital_bottom", type="secondary"):
# Debug output removed
        # Set flag to trigger clean switch (bewährtes Pattern)
        st.session_state.switch_to_digital = True
        st.rerun()

# Clear the discogs_just_rendered flag at the end of the script run
if "discogs_just_rendered" in st.session_state:
# Debug output removed
    del st.session_state.discogs_just_rendered

# # ganz unten, oberhalb des Endes von main.py
# if st.session_state.suche_gestartet and not search_clicked:
#     # wir sind in der Ergebnis-Ansicht
#     if st.session_state.show_digital and not st.session_state.discogs_revibed_mode:
#         # fülle digital_container aus dem gespeicherten State
#         digital_container.empty()
#         show_digital_block()
#     elif st.session_state.discogs_revibed_mode:
#         digital_container.empty()
#         show_discogs_and_revibed_block(
#             st.session_state.results_discogs,
#             st.session_state.track_for_search,
#             st.session_state.results_revibed
#         )
