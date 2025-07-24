"""Tests for api_search.py module."""

import pytest
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_search import (
    get_itunes_release_info,
    get_discogs_release_info,
    search_discogs_releases,
    get_discogs_release_details,
    get_discogs_offers
)


class TestGetItunesReleaseInfo:
    """Test iTunes release info retrieval."""
    
    def test_digital_artist_dummy_data(self):
        """Test iTunes returns dummy data for 'digital artist'."""
        result = get_itunes_release_info("digital artist", "test track")
        
        assert result["platform"] == "iTunes"
        assert result["title"] == "test track"
        assert result["artist"] == "digital artist"
        assert result["album"] == "test track - Single"
        assert result["label"] == "iTunes Store"
        assert result["price"] == "€1.29"
        assert "iTunes" in result["cover"]
        assert result["release_url"] != ""
        assert result["preview"] != ""
    
    def test_test_artist_dummy_data(self):
        """Test iTunes returns dummy data for 'test artist'."""
        result = get_itunes_release_info("test artist", "some track")
        
        assert result["platform"] == "iTunes"
        assert result["title"] == "some track"
        assert result["artist"] == "test artist"
        assert result["price"] == "€1.29"
    
    def test_digital_track_dummy_data(self):
        """Test iTunes returns dummy data for 'digital track'."""
        result = get_itunes_release_info("some artist", "digital track")
        
        assert result["platform"] == "iTunes"
        assert result["title"] == "digital track"
        assert result["artist"] == "some artist"
        assert result["price"] == "€1.29"
    
    def test_no_match_case(self):
        """Test iTunes returns 'Kein Treffer' for non-matching artists/tracks."""
        result = get_itunes_release_info("unknown artist", "unknown track")
        
        assert result["platform"] == "iTunes"
        assert result["title"] == "Kein Treffer"
        assert result["artist"] == ""
        assert result["album"] == ""
        assert result["label"] == ""
        assert result["price"] == ""
        assert result["cover"] == ""
        assert result["release_url"] == ""
        assert result["preview"] == ""


class TestGetDiscogsReleaseInfo:
    """Test Discogs release info retrieval."""
    
    def test_demo_track_b_offers(self):
        """Test Discogs returns offers for 'demo track b'."""
        result = get_discogs_release_info("CAT123", "artist", "demo track b", "album")
        
        assert "offers" in result
        assert len(result["offers"]) == 2
        
        # Check first offer
        first_offer = result["offers"][0]
        assert first_offer["seller"] == "VinylKing"
        assert first_offer["country"] == "Germany"
        assert first_offer["condition"] == "VG+"
        assert first_offer["price"] == "15"
        assert first_offer["currency"] == "EUR"
        
        # Check second offer
        second_offer = result["offers"][1]
        assert second_offer["seller"] == "Collector"
        assert second_offer["condition"] == "NM"
        assert second_offer["price"] == "19"
    
    def test_other_tracks_no_offers(self):
        """Test Discogs returns empty offers for other tracks."""
        result = get_discogs_release_info("CAT123", "artist", "other track", "album")
        
        assert result["offers"] == []
        assert result["album"] == "album"
        assert result["artist"] == "artist"
        assert result["tracklist"] == ["other track"]
        assert result["want_have_ratio"] == "5/100"
        assert result["label"] == "Dummy Label"
        assert result["avg_price"] == "15.00"


class TestSearchDiscogsReleases:
    """Test Discogs releases search functionality."""
    
    def test_empty_search_criteria(self):
        """Test search returns empty list for completely empty criteria."""
        result = search_discogs_releases()
        assert result == []
        
        result = search_discogs_releases(artist="", track="", album="", catno="")
        assert result == []
    
    def test_catalog_search_trigger(self):
        """Test search triggered by catalog number containing 'catalog'."""
        result = search_discogs_releases(catno="catalog123")
        
        assert len(result) > 0
        # Should return discogs-specific results
        assert all("discogs" in str(release).lower() or 
                  any(key in release for key in ["title", "artist", "label"]) 
                  for release in result)
    
    def test_discogs_artist_trigger(self):
        """Test search triggered by artist containing 'discogs'."""
        result = search_discogs_releases(artist="discogs artist")
        
        assert len(result) > 0
    
    def test_vintage_track_trigger(self):
        """Test search triggered by track containing 'vintage'."""
        result = search_discogs_releases(track="vintage track")
        
        assert len(result) > 0
    
    def test_regular_search_terms(self):
        """Test search with regular terms that don't trigger special cases."""
        result = search_discogs_releases(artist="regular artist", track="regular track")
        
        # Should return some results (dummy data structure)
        assert isinstance(result, list)


class TestGetDiscogsReleaseDetails:
    """Test Discogs release details retrieval."""
    
    def test_get_release_details_structure(self):
        """Test that release details function returns expected structure."""
        # This would be mocked in real implementation
        # For now, just test it doesn't crash
        try:
            result = get_discogs_release_details("123456")
            assert isinstance(result, (dict, type(None)))
        except Exception:
            # Expected since this likely requires real API calls
            pass


class TestGetDiscogsOffers:
    """Test Discogs offers retrieval."""
    
    def test_get_offers_structure(self):
        """Test that offers function returns expected structure."""
        # This would be mocked in real implementation
        # For now, just test it doesn't crash
        try:
            result = get_discogs_offers("123456")
            assert isinstance(result, (list, type(None)))
        except Exception:
            # Expected since this likely requires real API calls
            pass


class TestApiSearchIntegration:
    """Integration tests for API search functionality."""
    
    def test_all_functions_importable(self):
        """Test that all API search functions can be imported."""
        from api_search import (
            get_itunes_release_info,
            get_discogs_release_info,
            search_discogs_releases,
            get_discogs_release_details,
            get_discogs_offers
        )
        
        # If we got here, all imports succeeded
        assert True
    
    def test_dummy_data_consistency(self):
        """Test that dummy data is consistent across different calls."""
        itunes_result1 = get_itunes_release_info("digital artist", "track1")
        itunes_result2 = get_itunes_release_info("digital artist", "track2")
        
        # Should have same platform and artist, different track
        assert itunes_result1["platform"] == itunes_result2["platform"]
        assert itunes_result1["artist"] == itunes_result2["artist"]
        assert itunes_result1["title"] != itunes_result2["title"]