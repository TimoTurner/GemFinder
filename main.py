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
from providers import (
    SearchManager,
    DiscogsProvider, RevibedProvider,
    BeatportProvider, BandcampProvider, TraxsourceProvider
)
from state_manager import AppState
from ui_helpers import (
    show_live_results,
    show_digital_block,
    show_discogs_and_revibed_block
)
from utils import get_platform_info, is_fuzzy_match

from state_manager import AppState

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

# Store scroll position in session state
if "scroll_position" not in st.session_state:
    st.session_state.scroll_position = 0

# --- Header ---
# st.image("record_mole_copy.png", width=220)
st.image(os.path.join(os.path.dirname(__file__), "record_mole_copy.png"), width=220)     
st.title("GEM DETECTOR")
live_placeholder    = st.empty()
digital_placeholder = st.empty()

# --- Mode-Auswahl + Reset (optional) ---
col_mode, col_reset = st.columns([5,1])
with col_mode:
    mode = st.radio("Choose Input Mode:", 
                    ("Manual Input","Take a picture","Upload photo"),
                    key="input_mode")
with col_reset:
    if st.button("Reset"):
        # Reset input fields and clear keyup component states
        app_state.reset_search()
        st.session_state.last_mode = mode
        
        # Force keyup components to reset by clearing their values AND keys
        st.session_state.tracks_input = ""
        st.session_state.artist_input = ""
        st.session_state.catalog_number_input = ""
        st.session_state.album_input = ""
        
        # Clear the keyup component keys to force them to reset
        keyup_keys = ["tracks_keyup", "artist_keyup", "catalog_keyup", "album_keyup", "track_select"]
        for key in keyup_keys:
            if key in st.session_state:
                del st.session_state[key]
        
        # Increment reset counter to force component recreation with new keys
        if "reset_counter" not in st.session_state:
            st.session_state.reset_counter = 0
        st.session_state.reset_counter += 1
        
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
    tracks_input = st_keyup(
        "Track(s) - separate multiple tracks with semicolon", 
        value=st.session_state.get("tracks_input", ""),
        key=f"tracks_keyup{reset_suffix}"
    )
    st.caption("Enter one or more track titles separated by semicolon (;)")
    if tracks_input != st.session_state.get("tracks_input", ""):
        st.session_state.tracks_input = tracks_input

    artist_input = st_keyup(
        "Artist", 
        value=st.session_state.get("artist_input", ""),
        key=f"artist_keyup{reset_suffix}"
    )
    if artist_input != st.session_state.get("artist_input", ""):
        st.session_state.artist_input = artist_input

    catalog_input = st_keyup(
        "Catalog Number", 
        value=st.session_state.get("catalog_number_input", ""),
        key=f"catalog_keyup{reset_suffix}"
    )
    if catalog_input != st.session_state.get("catalog_number_input", ""):
        st.session_state.catalog_number_input = catalog_input

    album_input = st_keyup(
        "Album", 
        value=st.session_state.get("album_input", ""),
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
    digital_providers   = [BeatportProvider(), BandcampProvider(), TraxsourceProvider()]
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
        # Show camera input for first photo
        camera_photo = st.camera_input("📸 Take a photo")
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
live_container    = st.container()
digital_container = st.container()

# --- Search button validation and criteria checking ---
app_state = AppState()
criteria = app_state.get_criteria()

# Provider lists
digital_providers   = [BeatportProvider(), BandcampProvider(), TraxsourceProvider()]
secondary_providers = [DiscogsProvider(), RevibedProvider()]

# Check which platforms can search with current criteria
can_search_digital   = any(p.can_search(criteria) for p in digital_providers)
can_search_secondary = any(p.can_search(criteria) for p in secondary_providers)
can_search = can_search_digital or can_search_secondary

# Proactive reset: If search was done but cache is now invalid, reset immediately
if st.session_state.get("suche_gestartet", False) and not app_state.is_cache_valid():
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
    # Force cache invalidation when track search button is clicked
    if track_search_clicked:
        app_state.invalidate_cache()
    
    # Always check if cache is valid for current criteria
    # If criteria changed, invalidate cache and perform new search
    if not app_state.is_cache_valid():
        app_state.invalidate_cache()
        
        # Set search state
        st.session_state.suche_gestartet = True
        st.session_state.track_for_search = st.session_state.selected_track
        # Clear the search info and button placeholders
        if hasattr(st.session_state, 'search_info_placeholder'):
            st.session_state.search_info_placeholder.empty()
        if hasattr(st.session_state, 'search_button_placeholder'):
            st.session_state.search_button_placeholder.empty()

        app_state.update_cache_criteria()
        
        # Reset containers and live results
        live_container.empty()
        digital_container.empty()
        st.session_state.live_results = []
        
        # Reset live results containers for new search
        if "live_results_containers" in st.session_state:
            st.session_state.live_results_containers = {}
        if "live_results_header_shown" in st.session_state:
            st.session_state.live_results_header_shown = False

        # Stage 1: Search digital platforms if criteria met
        if can_search_digital:
            print("🔍 DEBUG: Starting OPTIMIZED digital search path")
            st.session_state.show_digital = True  
            st.session_state.discogs_revibed_mode = False
            
            # Digital platforms parallel search (iTunes will be re-added later)
            print(f"🔍 DEBUG: Starting digital platforms in parallel")
            
            # Show progress bar immediately when search starts
            with live_container:
                show_live_results()
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(search_platform_thread_safe, p, criteria): p 
                          for p in digital_providers if p.can_search(criteria)}
                
                # Live Updates während Threads laufen
                for future in as_completed(futures):
                    thread_result = future.result()
                    
                    if thread_result["status"] == "success":
                        entry = thread_result["result"]
                    else:
                        entry = {
                            "platform": thread_result["provider"],
                            "title": "Fehler",
                            "artist": "",
                            "album": "",
                            "label": "",
                            "price": "",
                            "cover_url": "",
                            "url": "",
                            "error": thread_result["error"]
                        }
                    
                    # SOFORT anzeigen sobald Thread fertig
                    st.session_state.live_results.append(entry)
                    st.session_state.results_digital.append(entry)
                    with live_container:
                        show_live_results()

            # Mark digital search as done
            st.session_state.digital_search_done = True
            
            # Check for real hits
            real_hits = [
                r for r in st.session_state.results_digital
                if (r.get("title") or "").strip().lower() not in ("kein treffer", "", "fehler")
            ]

            
            st.session_state.has_digital_hits = len(real_hits) > 0

            if st.session_state.has_digital_hits:
                # Stage 1 complete: Live results already shown, just clear progress and show mode switch
                if "live_progress_container" in st.session_state:
                    st.session_state.live_progress_container.empty()
                
                with digital_container:
                    show_digital_block()
            elif can_search_secondary:
                # Stage 2: No digital hits -> automatically search secondary platforms
                live_container.empty()
                st.session_state.discogs_revibed_mode = True
                st.session_state.show_digital = False
                
                # Search secondary platforms
                for p in secondary_providers:
                    if p.can_search(criteria):
                        result = p.search(criteria)
                        if p.name == "Discogs":
                            st.session_state.results_discogs = result.get("releases", [])  # Extract releases list from dict
                        elif p.name == "Revibed":
                            st.session_state.results_revibed = [result]
                
                st.session_state.secondary_search_done = True
                with digital_container:
                    show_discogs_and_revibed_block(
                        st.session_state.results_discogs,
                        st.session_state.track_for_search,
                        st.session_state.results_revibed
                    )

        # If only secondary platforms can search
        elif can_search_secondary:
            st.session_state.discogs_revibed_mode = True
            st.session_state.show_digital = False
            
            # Search secondary platforms
            for p in secondary_providers:
                if p.can_search(criteria):
                    result = p.search(criteria)
                    if p.name == "Discogs":
                        st.session_state.results_discogs = result.get("releases", [])  # Extract releases list from dict
                    elif p.name == "Revibed":
                        st.session_state.results_revibed = [result]
            
            st.session_state.secondary_search_done = True
            with digital_container:
                show_discogs_and_revibed_block(
                    st.session_state.results_discogs,
                    st.session_state.track_for_search,
                    st.session_state.results_revibed
                )

# Reset when search criteria changed (cache invalid but search was started)
elif st.session_state.suche_gestartet and not app_state.is_cache_valid():
    # Clear containers and reset all search-related state
    live_container.empty()
    digital_container.empty()
    
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

# Display cached results if search already done and cache is valid
elif st.session_state.suche_gestartet and app_state.is_cache_valid():
    if st.session_state.show_digital and st.session_state.digital_search_done:
        # Show cached digital results
        with digital_container:
            show_digital_block()
    elif st.session_state.discogs_revibed_mode and st.session_state.secondary_search_done:
        # Show cached secondary results  
        with digital_container:
            show_discogs_and_revibed_block(
                st.session_state.results_discogs,
                st.session_state.track_for_search,
                st.session_state.results_revibed
            )


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
