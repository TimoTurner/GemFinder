"""
Gradio-compatible State Manager
Replaces Streamlit session_state with simple dictionary-based state management
"""

from providers import SearchCriteria
from typing import Dict, Any

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
    "last_search_criteria":    ""
}

class GradioAppState:
    """Gradio-compatible state manager without Streamlit dependencies"""
    
    def __init__(self):
        # Initialize with default values
        self.state = DEFAULT_KEYS.copy()
        self.search_cache_criteria = None
        
    def get(self, key: str, default=None):
        """Get state value"""
        return self.state.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set state value"""
        self.state[key] = value
    
    def update(self, values: Dict[str, Any]):
        """Update multiple state values"""
        self.state.update(values)
    
    def get_criteria(self) -> SearchCriteria:
        """Get current search criteria"""
        return SearchCriteria(
            title   = self.state.get("selected_track", ""),
            artist  = self.state.get("artist_input", ""),
            album   = self.state.get("album_input", ""),
            catalog = self.state.get("catalog_number_input", "")
        )
    
    def reset_search(self):
        """Reset search state"""
        input_keys = [
            "tracks_input", "artist_input", "album_input", "catalog_number_input",
            "selected_track", "track_for_search", "ocr_applied", "last_mode", "suche_gestartet",
            "show_search_info", "show_search_button"
        ]
        
        for key in input_keys:
            if key in DEFAULT_KEYS:
                self.state[key] = DEFAULT_KEYS[key]
    
    def is_cache_valid(self) -> bool:
        """Check if search cache is valid for current criteria"""
        current_criteria = self.get_criteria()
        criteria_string = f"{current_criteria.title}|{current_criteria.artist}|{current_criteria.album}|{current_criteria.catalog}"
        
        return (self.state.get("search_cache_valid", False) and 
                self.state.get("last_search_criteria", "") == criteria_string)
    
    def update_cache_criteria(self):
        """Update cache criteria with current search criteria"""
        current_criteria = self.get_criteria()
        criteria_string = f"{current_criteria.title}|{current_criteria.artist}|{current_criteria.album}|{current_criteria.catalog}"
        
        self.state["search_cache_valid"] = True
        self.state["last_search_criteria"] = criteria_string
    
    def invalidate_cache(self):
        """Invalidate search cache"""
        self.state["search_cache_valid"] = False
        self.state["last_search_criteria"] = ""