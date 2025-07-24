"""Tests for providers.py module."""

import pytest
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from providers import (
    SearchCriteria,
    SearchProvider,
    DiscogsProvider,
    RevibedProvider,
    ItunesProvider,
    BeatportProvider,
    BandcampProvider,
    TraxsourceProvider,
    SearchManager
)


class TestSearchCriteria:
    """Test SearchCriteria class functionality."""
    
    def test_search_criteria_initialization_empty(self):
        """Test SearchCriteria initialization with no parameters."""
        criteria = SearchCriteria()
        
        assert criteria.title == ""
        assert criteria.artist == ""
        assert criteria.album == ""
        assert criteria.catalog == ""
    
    def test_search_criteria_initialization_with_values(self):
        """Test SearchCriteria initialization with values."""
        criteria = SearchCriteria(
            title="Test Track",
            artist="Test Artist",
            album="Test Album",
            catalog="TEST001"
        )
        
        assert criteria.title == "Test Track"
        assert criteria.artist == "Test Artist"
        assert criteria.album == "Test Album"
        assert criteria.catalog == "TEST001"
    
    def test_search_criteria_strips_whitespace(self):
        """Test SearchCriteria strips whitespace from inputs."""
        criteria = SearchCriteria(
            title="  Test Track  ",
            artist="  Test Artist  ",
            album="  Test Album  ",
            catalog="  TEST001  "
        )
        
        assert criteria.title == "Test Track"
        assert criteria.artist == "Test Artist"
        assert criteria.album == "Test Album"
        assert criteria.catalog == "TEST001"


class TestDiscogsProvider:
    """Test DiscogsProvider functionality."""
    
    def test_can_search_catalog_and_artist(self):
        """Test DiscogsProvider can search with catalog and artist."""
        provider = DiscogsProvider()
        criteria = SearchCriteria(catalog="TEST001", artist="Test Artist")
        
        assert provider.can_search(criteria) == True
    
    def test_can_search_catalog_and_album(self):
        """Test DiscogsProvider can search with catalog and album."""
        provider = DiscogsProvider()
        criteria = SearchCriteria(catalog="TEST001", album="Test Album")
        
        assert provider.can_search(criteria) == True
    
    def test_can_search_catalog_and_title(self):
        """Test DiscogsProvider can search with catalog and title."""
        provider = DiscogsProvider()
        criteria = SearchCriteria(catalog="TEST001", title="Test Track")
        
        assert provider.can_search(criteria) == True
    
    def test_can_search_title_and_artist(self):
        """Test DiscogsProvider can search with title and artist."""
        provider = DiscogsProvider()
        criteria = SearchCriteria(title="Test Track", artist="Test Artist")
        
        assert provider.can_search(criteria) == True
    
    def test_can_search_title_and_album(self):
        """Test DiscogsProvider can search with title and album."""
        provider = DiscogsProvider()
        criteria = SearchCriteria(title="Test Track", album="Test Album")
        
        assert provider.can_search(criteria) == True
    
    def test_can_search_artist_and_album(self):
        """Test DiscogsProvider can search with artist and album."""
        provider = DiscogsProvider()
        criteria = SearchCriteria(artist="Test Artist", album="Test Album")
        
        assert provider.can_search(criteria) == True
    
    def test_can_search_catalog_only(self):
        """Test DiscogsProvider can search with catalog only."""
        provider = DiscogsProvider()
        criteria = SearchCriteria(catalog="TEST001")
        
        assert provider.can_search(criteria) == True
    
    def test_cannot_search_empty_criteria(self):
        """Test DiscogsProvider cannot search with empty criteria."""
        provider = DiscogsProvider()
        criteria = SearchCriteria()
        
        assert provider.can_search(criteria) == False
    
    def test_cannot_search_single_field_except_catalog(self):
        """Test DiscogsProvider cannot search with single field except catalog."""
        provider = DiscogsProvider()
        
        assert provider.can_search(SearchCriteria(title="Test Track")) == False
        assert provider.can_search(SearchCriteria(artist="Test Artist")) == False
        assert provider.can_search(SearchCriteria(album="Test Album")) == False
    
    def test_search_returns_expected_structure(self):
        """Test DiscogsProvider search returns expected structure."""
        provider = DiscogsProvider()
        criteria = SearchCriteria(artist="test artist", title="test track")
        
        result = provider.search(criteria)
        
        # Check all expected keys are present
        expected_keys = ["platform", "title", "artist", "album", "label", "year", 
                        "format", "catno", "cover_url", "url", "tracklist"]
        for key in expected_keys:
            assert key in result
        
        assert result["platform"] == "Discogs"


class TestRevibedProvider:
    """Test RevibedProvider functionality."""
    
    def test_can_search_with_album(self):
        """Test RevibedProvider can search with album."""
        provider = RevibedProvider()
        criteria = SearchCriteria(album="Test Album")
        
        assert provider.can_search(criteria) == True
    
    def test_can_search_with_artist(self):
        """Test RevibedProvider can search with artist."""
        provider = RevibedProvider()
        criteria = SearchCriteria(artist="Test Artist")
        
        assert provider.can_search(criteria) == True
    
    def test_can_search_with_both_album_and_artist(self):
        """Test RevibedProvider can search with both album and artist."""
        provider = RevibedProvider()
        criteria = SearchCriteria(album="Test Album", artist="Test Artist")
        
        assert provider.can_search(criteria) == True
    
    def test_cannot_search_empty_criteria(self):
        """Test RevibedProvider cannot search with empty criteria."""
        provider = RevibedProvider()
        criteria = SearchCriteria()
        
        assert provider.can_search(criteria) == False
    
    def test_cannot_search_with_only_title_or_catalog(self):
        """Test RevibedProvider cannot search with only title or catalog."""
        provider = RevibedProvider()
        
        assert provider.can_search(SearchCriteria(title="Test Track")) == False
        assert provider.can_search(SearchCriteria(catalog="TEST001")) == False
    
    def test_search_returns_expected_structure(self):
        """Test RevibedProvider search returns expected structure."""
        provider = RevibedProvider()
        criteria = SearchCriteria(artist="test artist")
        
        result = provider.search(criteria)
        
        # Check all expected keys are present
        expected_keys = ["platform", "title", "artist", "album", "label", 
                        "price", "cover_url", "url"]
        for key in expected_keys:
            assert key in result
        
        assert result["platform"] == "Revibed"


class TestItunesProvider:
    """Test ItunesProvider functionality."""
    
    def test_can_search_title_and_artist(self):
        """Test ItunesProvider can search with title and artist."""
        provider = ItunesProvider()
        criteria = SearchCriteria(title="Test Track", artist="Test Artist")
        
        assert provider.can_search(criteria) == True
    
    def test_can_search_title_and_album(self):
        """Test ItunesProvider can search with title and album."""
        provider = ItunesProvider()
        criteria = SearchCriteria(title="Test Track", album="Test Album")
        
        assert provider.can_search(criteria) == True
    
    def test_can_search_artist_and_album(self):
        """Test ItunesProvider can search with artist and album."""
        provider = ItunesProvider()
        criteria = SearchCriteria(artist="Test Artist", album="Test Album")
        
        assert provider.can_search(criteria) == True
    
    def test_cannot_search_single_fields(self):
        """Test ItunesProvider cannot search with single fields."""
        provider = ItunesProvider()
        
        assert provider.can_search(SearchCriteria(title="Test Track")) == False
        assert provider.can_search(SearchCriteria(artist="Test Artist")) == False
        assert provider.can_search(SearchCriteria(album="Test Album")) == False
        assert provider.can_search(SearchCriteria(catalog="TEST001")) == False
    
    def test_cannot_search_empty_criteria(self):
        """Test ItunesProvider cannot search with empty criteria."""
        provider = ItunesProvider()
        criteria = SearchCriteria()
        
        assert provider.can_search(criteria) == False
    
    def test_search_returns_expected_structure(self):
        """Test ItunesProvider search returns expected structure."""
        provider = ItunesProvider()
        criteria = SearchCriteria(artist="digital artist", title="test track")
        
        result = provider.search(criteria)
        
        # Check all expected keys are present
        expected_keys = ["platform", "title", "artist", "album", "label", 
                        "price", "cover_url", "url", "preview"]
        for key in expected_keys:
            assert key in result
        
        assert result["platform"] == "iTunes"


class TestBeatportProvider:
    """Test BeatportProvider functionality."""
    
    def test_can_search_requirements_same_as_itunes(self):
        """Test BeatportProvider has same search requirements as iTunes."""
        beatport = BeatportProvider()
        itunes = ItunesProvider()
        
        test_criteria = [
            SearchCriteria(title="Test Track", artist="Test Artist"),
            SearchCriteria(title="Test Track", album="Test Album"),
            SearchCriteria(artist="Test Artist", album="Test Album"),
            SearchCriteria(title="Test Track"),
            SearchCriteria(artist="Test Artist"),
            SearchCriteria(),
        ]
        
        for criteria in test_criteria:
            assert beatport.can_search(criteria) == itunes.can_search(criteria)
    
    def test_search_returns_expected_structure(self):
        """Test BeatportProvider search returns expected structure."""
        provider = BeatportProvider()
        criteria = SearchCriteria(artist="digital artist", title="test track")
        
        result = provider.search(criteria)
        
        assert result["platform"] == "Beatport"
        assert "title" in result


class TestBandcampProvider:
    """Test BandcampProvider functionality."""
    
    def test_can_search_requirements_same_as_itunes(self):
        """Test BandcampProvider has same search requirements as iTunes."""
        bandcamp = BandcampProvider()
        itunes = ItunesProvider()
        
        test_criteria = [
            SearchCriteria(title="Test Track", artist="Test Artist"),
            SearchCriteria(title="Test Track", album="Test Album"),
            SearchCriteria(artist="Test Artist", album="Test Album"),
            SearchCriteria(title="Test Track"),
            SearchCriteria(artist="Test Artist"),
            SearchCriteria(),
        ]
        
        for criteria in test_criteria:
            assert bandcamp.can_search(criteria) == itunes.can_search(criteria)
    
    def test_search_returns_expected_structure(self):
        """Test BandcampProvider search returns expected structure."""
        provider = BandcampProvider()
        criteria = SearchCriteria(artist="digital artist", title="test track")
        
        result = provider.search(criteria)
        
        assert result["platform"] == "Bandcamp"
        assert "title" in result


class TestTraxsourceProvider:
    """Test TraxsourceProvider functionality."""
    
    def test_can_search_requirements_same_as_itunes(self):
        """Test TraxsourceProvider has same search requirements as iTunes."""
        traxsource = TraxsourceProvider()
        itunes = ItunesProvider()
        
        test_criteria = [
            SearchCriteria(title="Test Track", artist="Test Artist"),
            SearchCriteria(title="Test Track", album="Test Album"),
            SearchCriteria(artist="Test Artist", album="Test Album"),
            SearchCriteria(title="Test Track"),
            SearchCriteria(artist="Test Artist"),
            SearchCriteria(),
        ]
        
        for criteria in test_criteria:
            assert traxsource.can_search(criteria) == itunes.can_search(criteria)
    
    def test_search_returns_expected_structure(self):
        """Test TraxsourceProvider search returns expected structure."""
        provider = TraxsourceProvider()
        criteria = SearchCriteria(artist="digital artist", title="test track")
        
        result = provider.search(criteria)
        
        assert result["platform"] == "Traxsource"
        assert "title" in result


class TestSearchManager:
    """Test SearchManager functionality."""
    
    def test_search_manager_initialization(self):
        """Test SearchManager can be initialized with providers."""
        providers = [ItunesProvider(), DiscogsProvider()]
        manager = SearchManager(providers)
        
        assert len(manager.providers) == 2
        assert isinstance(manager.providers[0], ItunesProvider)
        assert isinstance(manager.providers[1], DiscogsProvider)
    
    def test_run_all_with_valid_criteria(self):
        """Test SearchManager runs all applicable providers."""
        providers = [ItunesProvider(), BeatportProvider(), DiscogsProvider()]
        manager = SearchManager(providers)
        criteria = SearchCriteria(title="test track", artist="digital artist")
        
        results = manager.run_all(criteria)
        
        # All providers should be able to search with title + artist
        assert len(results) == 3
        
        platforms = [result["platform"] for result in results]
        assert "iTunes" in platforms
        assert "Beatport" in platforms
        assert "Discogs" in platforms
    
    def test_run_all_with_limited_criteria(self):
        """Test SearchManager only runs applicable providers."""
        providers = [ItunesProvider(), RevibedProvider(), DiscogsProvider()]
        manager = SearchManager(providers)
        criteria = SearchCriteria(artist="test artist")  # Only artist field
        
        results = manager.run_all(criteria)
        
        # Only RevibedProvider should be able to search with just artist
        assert len(results) == 1
        assert results[0]["platform"] == "Revibed"
    
    def test_run_all_with_empty_criteria(self):
        """Test SearchManager returns empty results for empty criteria."""
        providers = [ItunesProvider(), BeatportProvider(), DiscogsProvider(), RevibedProvider()]
        manager = SearchManager(providers)
        criteria = SearchCriteria()  # Empty criteria
        
        results = manager.run_all(criteria)
        
        # No provider should be able to search with empty criteria
        assert len(results) == 0
    
    def test_run_all_catalog_specific_search(self):
        """Test SearchManager handles catalog-specific searches."""
        providers = [DiscogsProvider(), ItunesProvider()]
        manager = SearchManager(providers)
        criteria = SearchCriteria(catalog="TEST001")  # Only catalog
        
        results = manager.run_all(criteria)
        
        # Only DiscogsProvider should handle catalog-only searches
        assert len(results) == 1
        assert results[0]["platform"] == "Discogs"


class TestProvidersIntegration:
    """Integration tests for providers functionality."""
    
    def test_all_providers_inherit_from_search_provider(self):
        """Test that all providers inherit from SearchProvider."""
        providers = [
            DiscogsProvider(),
            RevibedProvider(),
            ItunesProvider(),
            BeatportProvider(),
            BandcampProvider(),
            TraxsourceProvider()
        ]
        
        for provider in providers:
            assert isinstance(provider, SearchProvider)
            assert hasattr(provider, 'name')
            assert hasattr(provider, 'can_search')
            assert hasattr(provider, 'search')
    
    def test_all_providers_have_unique_names(self):
        """Test that all providers have unique names."""
        providers = [
            DiscogsProvider(),
            RevibedProvider(),
            ItunesProvider(),
            BeatportProvider(),
            BandcampProvider(),
            TraxsourceProvider()
        ]
        
        names = [provider.name for provider in providers]
        assert len(names) == len(set(names))  # All names should be unique
    
    def test_digital_providers_consistency(self):
        """Test that digital providers (iTunes, Beatport, Bandcamp, Traxsource) have consistent behavior."""
        digital_providers = [
            ItunesProvider(),
            BeatportProvider(),
            BandcampProvider(),
            TraxsourceProvider()
        ]
        
        test_criteria = [
            SearchCriteria(title="Test Track", artist="Test Artist"),
            SearchCriteria(title="Test Track", album="Test Album"),
            SearchCriteria(artist="Test Artist", album="Test Album"),
            SearchCriteria(title="Test Track"),
            SearchCriteria()
        ]
        
        # All digital providers should have identical can_search behavior
        for criteria in test_criteria:
            can_search_results = [provider.can_search(criteria) for provider in digital_providers]
            assert all(result == can_search_results[0] for result in can_search_results)
    
    def test_provider_search_methods_return_dictionaries(self):
        """Test that all provider search methods return dictionaries."""
        providers = [
            (DiscogsProvider(), SearchCriteria(artist="test artist", title="test track")),
            (RevibedProvider(), SearchCriteria(artist="test artist")),
            (ItunesProvider(), SearchCriteria(artist="digital artist", title="test track")),
            (BeatportProvider(), SearchCriteria(artist="digital artist", title="test track")),
            (BandcampProvider(), SearchCriteria(artist="digital artist", title="test track")),
            (TraxsourceProvider(), SearchCriteria(artist="digital artist", title="test track"))
        ]
        
        for provider, criteria in providers:
            if provider.can_search(criteria):
                result = provider.search(criteria)
                assert isinstance(result, dict)
                assert "platform" in result
                assert result["platform"] == provider.name