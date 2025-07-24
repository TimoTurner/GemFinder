# state_manager.py
import streamlit as st
from providers import SearchCriteria

DEFAULT_KEYS = {
    "results_digital":        [],
    "results_discogs":         [],
    "results_revibed":         [],
    "suche_gestartet":         False,
    "selected_track":          "",
    "tracks_input":            "",
    "artist_input":            "",
    "album_input":             "",
    "label_input":             "",
    "catalog_number_input":    "",
    "ocr_applied":             False,
    "release_selected_idx":    0,
    "release_confirmed":       False,
    "log_opt_in":              False,
    "track_for_search":        "",
    "last_mode":               "Manual Input",
    "discogs_revibed_mode":    False,
    "show_digital":            True,
    "digital_search_done":     False,
    "secondary_search_done":   False,
    "has_digital_hits":        False,
    "search_cache_valid":      False,
    "last_search_criteria":    ""}

class AppState:
    def __init__(self):
        # Default-Init aller benötigten Keys
        for key, default in DEFAULT_KEYS.items():
            if key not in st.session_state:
                st.session_state[key] = default

    def get_criteria(self) -> SearchCriteria:
        return SearchCriteria(
            title   = st.session_state.get("selected_track", ""),
            artist  = st.session_state.artist_input,
            album   = st.session_state.album_input,
            catalog = st.session_state.catalog_number_input
        )

    def reset_search(self):
        # Only reset input fields, preserve search results and cache
        input_keys = [
            "tracks_input", "artist_input", "album_input", "catalog_number_input",
            "selected_track", "track_for_search", "ocr_applied", "last_mode", "suche_gestartet",
            "show_search_info", "show_search_button"
        ]
        for key in input_keys:
            if key in DEFAULT_KEYS:
                st.session_state[key] = DEFAULT_KEYS[key]
        

    def invalidate_cache(self):
        """Invalidate search cache when new search is performed"""
        st.session_state.search_cache_valid = False
        st.session_state.digital_search_done = False
        st.session_state.secondary_search_done = False
        st.session_state.has_digital_hits = False
        st.session_state.results_digital = []
        st.session_state.results_discogs = []
        st.session_state.results_revibed = []

    def get_criteria_hash(self) -> str:
        """Generate hash of current search criteria for cache validation"""
        criteria = self.get_criteria()
        return f"{criteria.title}|{criteria.artist}|{criteria.album}|{criteria.catalog}"

    def get_criteria_hash_without_track(self) -> str:
        """Generate hash excluding track title for multi-track scenarios"""
        criteria = self.get_criteria()
        return f"|{criteria.artist}|{criteria.album}|{criteria.catalog}"

    def is_cache_valid(self) -> bool:
        """Check if current cache is valid for current criteria"""
        # If we're in multi-track mode, ignore track changes for cache validation
        track_list = [t.strip() for t in st.session_state.get("tracks_input", "").split(';') if t.strip()]
        
        if len(track_list) > 1:
            # Multi-track mode: only check non-track fields
            current_hash = self.get_criteria_hash_without_track()
            last_hash_parts = st.session_state.get("last_search_criteria", "").split("|")
            if len(last_hash_parts) >= 4:
                last_hash_without_track = f"|{last_hash_parts[1]}|{last_hash_parts[2]}|{last_hash_parts[3]}"
                return (st.session_state.search_cache_valid and last_hash_without_track == current_hash)
        
        # Single track mode: normal validation
        current_hash = self.get_criteria_hash()
        return (st.session_state.search_cache_valid and 
                st.session_state.last_search_criteria == current_hash)

    def update_cache_criteria(self):
        """Update cache criteria hash"""
        st.session_state.last_search_criteria = self.get_criteria_hash()
        st.session_state.search_cache_valid = True

    def add_live_result(self, entry: dict):
        if "live_results" not in st.session_state:
            st.session_state.live_results = []
        st.session_state.live_results.append(entry)
