"""Tests for state_manager.py module."""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock streamlit before importing the module
class MockSessionState(dict):
    """Mock session state that supports both dict and attribute access"""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        self[name] = value

mock_streamlit = Mock()
mock_streamlit.session_state = MockSessionState()
sys.modules['streamlit'] = mock_streamlit

from state_manager import AppState, DEFAULT_KEYS
from providers import SearchCriteria


class TestDefaultKeys:
    """Test DEFAULT_KEYS constant."""
    
    def test_default_keys_structure(self):
        """Test that DEFAULT_KEYS contains expected keys and types."""
        expected_keys = [
            "results_digital", "results_discogs", "results_revibed",
            "suche_gestartet", "selected_track", "tracks_input",
            "artist_input", "album_input", "label_input",
            "catalog_number_input", "ocr_applied", "release_selected_idx",
            "release_confirmed", "log_opt_in", "track_for_search",
            "last_mode", "discogs_revibed_mode", "show_digital",
            "digital_search_done", "secondary_search_done",
            "has_digital_hits", "search_cache_valid", "last_search_criteria"
        ]
        
        for key in expected_keys:
            assert key in DEFAULT_KEYS
        
        # Check specific default values
        assert DEFAULT_KEYS["results_digital"] == []
        assert DEFAULT_KEYS["results_discogs"] == []
        assert DEFAULT_KEYS["results_revibed"] == []
        assert DEFAULT_KEYS["suche_gestartet"] == False
        assert DEFAULT_KEYS["selected_track"] == ""
        assert DEFAULT_KEYS["tracks_input"] == ""
        assert DEFAULT_KEYS["artist_input"] == ""
        assert DEFAULT_KEYS["album_input"] == ""
        assert DEFAULT_KEYS["catalog_number_input"] == ""
        assert DEFAULT_KEYS["last_search_criteria"] == ""


class TestAppState:
    """Test AppState class functionality."""
    
    def setup_method(self):
        """Reset session state before each test."""
        mock_streamlit.session_state.clear()
    
    def test_app_state_initialization(self):
        """Test AppState initialization sets all default keys."""
        app_state = AppState()
        
        # Check that all default keys are set in session state
        for key, default_value in DEFAULT_KEYS.items():
            assert key in mock_streamlit.session_state
            assert mock_streamlit.session_state[key] == default_value
    
    def test_app_state_initialization_preserves_existing_values(self):
        """Test AppState initialization doesn't overwrite existing session state values."""
        # Set some existing values
        mock_streamlit.session_state.artist_input = "Existing Artist"
        mock_streamlit.session_state.suche_gestartet = True
        
        app_state = AppState()
        
        # Existing values should be preserved
        assert mock_streamlit.session_state.artist_input == "Existing Artist"
        assert mock_streamlit.session_state.suche_gestartet == True
        
        # Missing values should be set to defaults
        assert mock_streamlit.session_state.album_input == ""
        assert mock_streamlit.session_state.results_digital == []
    
    def test_get_criteria_returns_search_criteria(self):
        """Test get_criteria returns properly formatted SearchCriteria."""
        # Set up session state values
        mock_streamlit.session_state.selected_track = "Test Track"
        mock_streamlit.session_state.artist_input = "Test Artist"
        mock_streamlit.session_state.album_input = "Test Album"
        mock_streamlit.session_state.catalog_number_input = "TEST001"
        
        app_state = AppState()
        criteria = app_state.get_criteria()
        
        assert isinstance(criteria, SearchCriteria)
        assert criteria.title == "Test Track"
        assert criteria.artist == "Test Artist"
        assert criteria.album == "Test Album"
        assert criteria.catalog == "TEST001"
    
    def test_get_criteria_with_empty_values(self):
        """Test get_criteria handles empty session state values."""
        app_state = AppState()
        criteria = app_state.get_criteria()
        
        assert isinstance(criteria, SearchCriteria)
        assert criteria.title == ""
        assert criteria.artist == ""
        assert criteria.album == ""
        assert criteria.catalog == ""
    
    def test_reset_search_clears_input_fields(self):
        """Test reset_search clears appropriate input fields."""
        # Set up some session state values
        mock_streamlit.session_state.tracks_input = "Track 1; Track 2"
        mock_streamlit.session_state.artist_input = "Artist Name"
        mock_streamlit.session_state.album_input = "Album Name"
        mock_streamlit.session_state.selected_track = "Track 1"
        mock_streamlit.session_state.suche_gestartet = True
        mock_streamlit.session_state.results_digital = [{"test": "data"}]  # Should not be cleared
        
        app_state = AppState()
        app_state.reset_search()
        
        # Input fields should be reset to defaults
        assert mock_streamlit.session_state.tracks_input == ""
        assert mock_streamlit.session_state.artist_input == ""
        assert mock_streamlit.session_state.album_input == ""
        assert mock_streamlit.session_state.selected_track == ""
        assert mock_streamlit.session_state.suche_gestartet == False
        
        # Results should be preserved (not in input_keys)
        assert mock_streamlit.session_state.results_digital == [{"test": "data"}]
    
    def test_invalidate_cache_resets_cache_flags(self):
        """Test invalidate_cache resets all cache-related flags and results."""
        # Set up cache state
        mock_streamlit.session_state.search_cache_valid = True
        mock_streamlit.session_state.digital_search_done = True
        mock_streamlit.session_state.secondary_search_done = True
        mock_streamlit.session_state.has_digital_hits = True
        mock_streamlit.session_state.results_digital = [{"test": "data"}]
        mock_streamlit.session_state.results_discogs = [{"discogs": "data"}]
        mock_streamlit.session_state.results_revibed = [{"revibed": "data"}]
        
        app_state = AppState()
        app_state.invalidate_cache()
        
        # All cache flags should be reset
        assert mock_streamlit.session_state.search_cache_valid == False
        assert mock_streamlit.session_state.digital_search_done == False
        assert mock_streamlit.session_state.secondary_search_done == False
        assert mock_streamlit.session_state.has_digital_hits == False
        
        # All results should be cleared
        assert mock_streamlit.session_state.results_digital == []
        assert mock_streamlit.session_state.results_discogs == []
        assert mock_streamlit.session_state.results_revibed == []
    
    def test_get_criteria_hash_generates_consistent_hash(self):
        """Test get_criteria_hash generates consistent hash for same criteria."""
        # Set up session state
        mock_streamlit.session_state.selected_track = "Test Track"
        mock_streamlit.session_state.artist_input = "Test Artist"
        mock_streamlit.session_state.album_input = "Test Album"
        mock_streamlit.session_state.catalog_number_input = "TEST001"
        
        app_state = AppState()
        hash1 = app_state.get_criteria_hash()
        hash2 = app_state.get_criteria_hash()
        
        # Should generate same hash for same criteria
        assert hash1 == hash2
        assert hash1 == "Test Track|Test Artist|Test Album|TEST001"
    
    def test_get_criteria_hash_without_track(self):
        """Test get_criteria_hash_without_track excludes track title."""
        # Set up session state
        mock_streamlit.session_state.selected_track = "Test Track"
        mock_streamlit.session_state.artist_input = "Test Artist"
        mock_streamlit.session_state.album_input = "Test Album"
        mock_streamlit.session_state.catalog_number_input = "TEST001"
        
        app_state = AppState()
        hash_without_track = app_state.get_criteria_hash_without_track()
        
        # Should exclude track title (first part)
        assert hash_without_track == "|Test Artist|Test Album|TEST001"
    
    def test_is_cache_valid_single_track_mode(self):
        """Test is_cache_valid in single track mode."""
        # Set up session state for single track
        mock_streamlit.session_state.tracks_input = "Single Track"  # Single track
        mock_streamlit.session_state.selected_track = "Single Track"
        mock_streamlit.session_state.artist_input = "Test Artist"
        mock_streamlit.session_state.album_input = "Test Album"
        mock_streamlit.session_state.catalog_number_input = "TEST001"
        mock_streamlit.session_state.search_cache_valid = True
        mock_streamlit.session_state.last_search_criteria = "Single Track|Test Artist|Test Album|TEST001"
        
        app_state = AppState()
        
        # Cache should be valid with matching criteria
        assert app_state.is_cache_valid() == True
        
        # Change criteria - cache should be invalid
        mock_streamlit.session_state.artist_input = "Different Artist"
        assert app_state.is_cache_valid() == False
    
    def test_is_cache_valid_multi_track_mode(self):
        """Test is_cache_valid in multi-track mode."""
        # Set up session state for multi-track
        mock_streamlit.session_state.tracks_input = "Track 1; Track 2"  # Multiple tracks
        mock_streamlit.session_state.selected_track = "Track 1"
        mock_streamlit.session_state.artist_input = "Test Artist"
        mock_streamlit.session_state.album_input = "Test Album"
        mock_streamlit.session_state.catalog_number_input = "TEST001"
        mock_streamlit.session_state.search_cache_valid = True
        mock_streamlit.session_state.last_search_criteria = "Track 1|Test Artist|Test Album|TEST001"
        
        app_state = AppState()
        
        # Cache should be valid even if track changes (multi-track mode)
        assert app_state.is_cache_valid() == True
        
        # Change selected track - should still be valid in multi-track mode
        mock_streamlit.session_state.selected_track = "Track 2"
        assert app_state.is_cache_valid() == True
        
        # Change non-track criteria - should be invalid
        mock_streamlit.session_state.artist_input = "Different Artist"
        assert app_state.is_cache_valid() == False
    
    def test_is_cache_valid_invalid_cache_flag(self):
        """Test is_cache_valid returns False when cache flag is False."""
        mock_streamlit.session_state.search_cache_valid = False
        mock_streamlit.session_state.last_search_criteria = "Track|Artist|Album|Catalog"
        
        app_state = AppState()
        
        assert app_state.is_cache_valid() == False
    
    def test_update_cache_criteria(self):
        """Test update_cache_criteria updates hash and sets valid flag."""
        # Set up session state
        mock_streamlit.session_state.selected_track = "Test Track"
        mock_streamlit.session_state.artist_input = "Test Artist"
        mock_streamlit.session_state.album_input = "Test Album"
        mock_streamlit.session_state.catalog_number_input = "TEST001"
        mock_streamlit.session_state.search_cache_valid = False
        mock_streamlit.session_state.last_search_criteria = ""
        
        app_state = AppState()
        app_state.update_cache_criteria()
        
        # Should update criteria hash and set cache as valid
        assert mock_streamlit.session_state.last_search_criteria == "Test Track|Test Artist|Test Album|TEST001"
        assert mock_streamlit.session_state.search_cache_valid == True
    
    def test_add_live_result_creates_list_if_not_exists(self):
        """Test add_live_result creates live_results list if it doesn't exist."""
        app_state = AppState()
        test_entry = {"platform": "Test", "title": "Test Track"}
        
        app_state.add_live_result(test_entry)
        
        assert 'live_results' in mock_streamlit.session_state
        assert mock_streamlit.session_state.live_results == [test_entry]
    
    def test_add_live_result_appends_to_existing_list(self):
        """Test add_live_result appends to existing live_results list."""
        # Set up existing live results
        mock_streamlit.session_state.live_results = [{"existing": "result"}]
        
        app_state = AppState()
        test_entry = {"platform": "Test", "title": "Test Track"}
        
        app_state.add_live_result(test_entry)
        
        assert len(mock_streamlit.session_state.live_results) == 2
        assert mock_streamlit.session_state.live_results[0] == {"existing": "result"}
        assert mock_streamlit.session_state.live_results[1] == test_entry


class TestStateManagerIntegration:
    """Integration tests for state manager functionality."""
    
    def setup_method(self):
        """Reset session state before each test."""
        mock_streamlit.session_state.clear()
    
    def test_full_workflow_state_management(self):
        """Test a complete workflow of state management operations."""
        app_state = AppState()
        
        # 1. Initial state should be clean
        criteria = app_state.get_criteria()
        assert criteria.title == ""
        assert criteria.artist == ""
        
        # 2. Set some search criteria
        mock_streamlit.session_state.selected_track = "Test Track"
        mock_streamlit.session_state.artist_input = "Test Artist"
        
        # 3. Update cache after search
        app_state.update_cache_criteria()
        assert app_state.is_cache_valid() == True
        
        # 4. Change criteria - cache should become invalid
        mock_streamlit.session_state.album_input = "New Album"
        assert app_state.is_cache_valid() == False
        
        # 5. Reset search
        app_state.reset_search()
        criteria = app_state.get_criteria()
        assert criteria.title == ""
        assert criteria.artist == ""
        assert criteria.album == ""
    
    def test_multi_track_vs_single_track_cache_behavior(self):
        """Test cache behavior differences between single and multi-track modes."""
        app_state = AppState()
        
        # Set up initial criteria
        mock_streamlit.session_state.artist_input = "Test Artist"
        mock_streamlit.session_state.album_input = "Test Album"
        mock_streamlit.session_state.catalog_number_input = "TEST001"
        
        # Test single track mode
        mock_streamlit.session_state.tracks_input = "Single Track"
        mock_streamlit.session_state.selected_track = "Single Track"
        app_state.update_cache_criteria()
        assert app_state.is_cache_valid() == True
        
        # Change track in single mode - should invalidate cache
        mock_streamlit.session_state.selected_track = "Different Track"
        assert app_state.is_cache_valid() == False
        
        # Switch to multi-track mode
        mock_streamlit.session_state.tracks_input = "Track 1; Track 2"
        mock_streamlit.session_state.selected_track = "Track 1"
        app_state.update_cache_criteria()
        assert app_state.is_cache_valid() == True
        
        # Change track in multi-track mode - should keep cache valid
        mock_streamlit.session_state.selected_track = "Track 2"
        assert app_state.is_cache_valid() == True
    
    def test_session_state_preservation_across_operations(self):
        """Test that session state is properly preserved across different operations."""
        app_state = AppState()
        
        # Set up some state
        mock_streamlit.session_state.results_digital = [{"test": "result"}]
        mock_streamlit.session_state.artist_input = "Test Artist"
        mock_streamlit.session_state.suche_gestartet = True
        
        # Reset search should preserve results but clear inputs
        app_state.reset_search()
        assert mock_streamlit.session_state.results_digital == [{"test": "result"}]
        assert mock_streamlit.session_state.artist_input == ""
        assert mock_streamlit.session_state.suche_gestartet == False
        
        # Restore some state and invalidate cache
        mock_streamlit.session_state.results_digital = [{"test": "result"}]
        app_state.invalidate_cache()
        assert mock_streamlit.session_state.results_digital == []