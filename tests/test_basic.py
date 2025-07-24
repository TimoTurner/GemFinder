"""Basic tests for GemFinder application."""

import pytest
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all main modules can be imported."""
    try:
        import providers
        import state_manager
        import utils
        import api_search
        import scrape_search
        import ui_helpers
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_search_criteria():
    """Test SearchCriteria class basic functionality."""
    from providers import SearchCriteria
    
    criteria = SearchCriteria(
        title="test track",
        artist="test artist", 
        album="test album",
        catalog="test catalog"
    )
    
    assert criteria.title == "test track"
    assert criteria.artist == "test artist"
    assert criteria.album == "test album"
    assert criteria.catalog == "test catalog"

def test_app_state_initialization():
    """Test AppState initializes without errors."""
    from state_manager import AppState
    
    # This should not raise any exceptions
    app_state = AppState()
    assert app_state is not None

def test_fuzzy_match():
    """Test fuzzy matching utility function."""
    from utils import is_fuzzy_match
    
    # Test exact match
    assert is_fuzzy_match("test track", "test track") == True
    
    # Test case insensitive
    assert is_fuzzy_match("Test Track", "test track") == True
    
    # Test partial match
    assert is_fuzzy_match("test", "test track") == True
    
    # Test no match
    assert is_fuzzy_match("completely different", "test track") == False

def test_providers_can_search():
    """Test provider can_search methods."""
    from providers import SearchCriteria, ItunesProvider, DiscogsProvider
    
    # Test with valid criteria
    criteria = SearchCriteria(title="test", artist="artist")
    
    itunes = ItunesProvider()
    discogs = DiscogsProvider()
    
    # iTunes should be able to search with title and artist
    assert itunes.can_search(criteria) == True
    
    # Discogs should be able to search with title and artist  
    assert discogs.can_search(criteria) == True
    
    # Test with empty criteria
    empty_criteria = SearchCriteria()
    assert itunes.can_search(empty_criteria) == False
    assert discogs.can_search(empty_criteria) == False