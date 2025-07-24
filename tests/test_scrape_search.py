"""Tests for scrape_search.py module."""

import pytest
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrape_search import (
    search_beatport,
    search_bandcamp,
    search_traxsource,
    search_revibed,
    search_digital_releases_parallel
)


class TestSearchBeatport:
    """Test Beatport search functionality."""
    
    def test_digital_artist_returns_results(self):
        """Test Beatport returns results for digital artist."""
        result = search_beatport("digital artist", "test track")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Beatport"
        assert result[0]["title"] == "test track (Original Mix)"
        assert result[0]["artist"] == "digital artist"
        assert result[0]["album"] == "test track EP"
        assert result[0]["label"] == "Digital Records"
        assert result[0]["price"] == "€2.49"
        assert "Beatport" in result[0]["cover_url"]
        assert result[0]["url"] != ""
        assert result[0]["search_time"] == 0.1
    
    def test_test_artist_returns_results(self):
        """Test Beatport returns results for test artist."""
        result = search_beatport("test artist", "some track")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Beatport"
        assert result[0]["title"] == "some track (Original Mix)"
        assert result[0]["artist"] == "test artist"
    
    def test_digital_track_returns_results(self):
        """Test Beatport returns results for digital track."""
        result = search_beatport("some artist", "digital track")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Beatport"
        assert result[0]["title"] == "digital track (Original Mix)"
        assert result[0]["artist"] == "some artist"
    
    def test_unknown_artist_returns_no_match(self):
        """Test Beatport returns 'Kein Treffer' for unknown artists."""
        result = search_beatport("unknown artist", "unknown track")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Beatport"
        assert result[0]["title"] == "Kein Treffer"
        assert result[0]["artist"] == ""
        assert result[0]["album"] == ""
        assert result[0]["label"] == ""
        assert result[0]["price"] == ""
        assert result[0]["cover_url"] == ""
        assert result[0]["url"] == ""


class TestSearchBandcamp:
    """Test Bandcamp search functionality."""
    
    def test_digital_artist_returns_results(self):
        """Test Bandcamp returns results for digital artist."""
        result = search_bandcamp("digital artist", "test track")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Bandcamp"
        assert result[0]["title"] == "test track"
        assert result[0]["artist"] == "digital artist"
        assert result[0]["album"] == "test track Single"
        assert result[0]["label"] == "independent-records"
        assert result[0]["price"] == "€3.00"
        assert "Bandcamp" in result[0]["cover_url"]
        assert "bandcamp.com" in result[0]["url"]
    
    def test_test_track_returns_results(self):
        """Test Bandcamp returns results for test track."""
        result = search_bandcamp("some artist", "test track")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Bandcamp"
        assert result[0]["title"] == "test track"
        assert result[0]["artist"] == "some artist"
    
    def test_unknown_artist_returns_no_match(self):
        """Test Bandcamp returns 'Kein Treffer' for unknown artists."""
        result = search_bandcamp("unknown artist", "unknown track")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Bandcamp"
        assert result[0]["title"] == "Kein Treffer"
        assert result[0]["artist"] == ""


class TestSearchTraxsource:
    """Test Traxsource search functionality."""
    
    def test_digital_artist_returns_results(self):
        """Test Traxsource returns results for digital artist."""
        result = search_traxsource("digital artist", "test track")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Traxsource"
        assert result[0]["title"] == "test track (Extended Mix)"
        assert result[0]["artist"] == "digital artist"
        assert result[0]["album"] == "test track"
        assert result[0]["label"] == "Deep House Label"
        assert result[0]["price"] == "$2.99"
        assert "Traxsource" in result[0]["cover_url"]
        assert "traxsource.com" in result[0]["url"]
    
    def test_test_artist_returns_results(self):
        """Test Traxsource returns results for test artist."""
        result = search_traxsource("test artist", "some track")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Traxsource"
        assert result[0]["title"] == "some track (Extended Mix)"
        assert result[0]["artist"] == "test artist"
    
    def test_unknown_artist_returns_no_match(self):
        """Test Traxsource returns 'Kein Treffer' for unknown artists."""
        result = search_traxsource("unknown artist", "unknown track")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Traxsource"
        assert result[0]["title"] == "Kein Treffer"
        assert result[0]["artist"] == ""


class TestSearchRevibed:
    """Test Revibed search functionality."""
    
    def test_empty_criteria_returns_message(self):
        """Test Revibed returns message for empty search criteria."""
        result = search_revibed("", "")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Revibed"
        assert "Album ODER Artist" in result[0]["message"]
        assert result[0]["title"] == ""
    
    def test_vinyl_artist_returns_results(self):
        """Test Revibed returns results for vinyl artist."""
        result = search_revibed("vinyl artist", "some album")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Revibed"
        assert result[0]["title"] == "vinyl artist"
        assert result[0]["album"] == "some album"
        assert result[0]["price"] == "€45.00"
        assert "Revibed" in result[0]["cover_url"]
        assert "revibed.com" in result[0]["url"]
    
    def test_rare_artist_returns_results(self):
        """Test Revibed returns results for rare artist."""
        result = search_revibed("rare artist", "")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Revibed"
        assert result[0]["title"] == "rare artist"
        assert result[0]["album"] == "rare artist Collection"
    
    def test_vinyl_album_returns_results(self):
        """Test Revibed returns results for vinyl album."""
        result = search_revibed("some artist", "vinyl collection")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Revibed"
        assert result[0]["title"] == "some artist"
        assert result[0]["album"] == "vinyl collection"
    
    def test_regular_artist_returns_no_match(self):
        """Test Revibed returns 'Kein Treffer' for regular artists."""
        result = search_revibed("regular artist", "regular album")
        
        assert len(result) == 1
        assert result[0]["platform"] == "Revibed"
        assert result[0]["title"] == "Kein Treffer"
        assert result[0]["artist"] == ""
        assert result[0]["album"] == ""


class TestSearchDigitalReleasesParallel:
    """Test parallel digital releases search functionality."""
    
    def test_parallel_search_returns_multiple_platforms(self):
        """Test parallel search returns results from all platforms."""
        results = search_digital_releases_parallel("digital artist", "test track", "test album", "")
        
        # Should have results from Beatport, Bandcamp, and Traxsource
        assert len(results) == 3
        
        platforms = [result["platform"] for result in results]
        assert "Beatport" in platforms
        assert "Bandcamp" in platforms
        assert "Traxsource" in platforms
    
    def test_parallel_search_with_digital_terms(self):
        """Test parallel search with digital terms returns valid results."""
        results = search_digital_releases_parallel("test artist", "digital track", "", "")
        
        # All platforms should return actual results (not 'Kein Treffer')
        for result in results:
            assert result["title"] != "Kein Treffer"
            assert result["artist"] != ""
            assert result["search_time"] == 0.1
    
    def test_parallel_search_with_unknown_terms(self):
        """Test parallel search with unknown terms returns 'Kein Treffer'."""
        results = search_digital_releases_parallel("unknown artist", "unknown track", "", "")
        
        # All platforms should return 'Kein Treffer'
        for result in results:
            assert result["title"] == "Kein Treffer"
            assert result["artist"] == ""
    
    def test_parallel_search_structure_consistency(self):
        """Test that all results have consistent structure."""
        results = search_digital_releases_parallel("test artist", "test track", "", "")
        
        required_keys = ["platform", "title", "artist", "album", "label", "price", "cover_url", "url", "search_time"]
        
        for result in results:
            for key in required_keys:
                assert key in result


class TestScrapeSearchIntegration:
    """Integration tests for scrape search functionality."""
    
    def test_all_functions_importable(self):
        """Test that all scrape search functions can be imported."""
        from scrape_search import (
            search_beatport,
            search_bandcamp,
            search_traxsource,
            search_revibed,
            search_digital_releases_parallel
        )
        
        # If we got here, all imports succeeded
        assert True
    
    def test_response_time_consistency(self):
        """Test that all platform searches have consistent response times."""
        platforms = [
            ("Beatport", search_beatport),
            ("Bandcamp", search_bandcamp),
            ("Traxsource", search_traxsource)
        ]
        
        for name, func in platforms:
            result = func("test artist", "test track")
            assert result[0]["search_time"] == 0.1
    
    def test_dummy_data_consistency(self):
        """Test that dummy data is consistent across different calls."""
        beatport_result1 = search_beatport("digital artist", "track1")
        beatport_result2 = search_beatport("digital artist", "track2")
        
        # Should have same platform and artist, different track
        assert beatport_result1[0]["platform"] == beatport_result2[0]["platform"]
        assert beatport_result1[0]["artist"] == beatport_result2[0]["artist"]
        assert beatport_result1[0]["title"] != beatport_result2[0]["title"]
        
    def test_revibed_unique_requirements(self):
        """Test that Revibed has unique search requirements compared to other platforms."""
        # Test with artists that don't trigger dummy data
        revibed_result = search_revibed("regular artist", "")
        beatport_result = search_beatport("regular artist", "")
        
        # Both should return no match for regular artist (dummy implementations are restrictive)
        assert revibed_result[0]["title"] == "Kein Treffer"
        assert beatport_result[0]["title"] == "Kein Treffer"
        
        # Test Revibed with vinyl artist (should work)
        revibed_vinyl_result = search_revibed("vinyl artist", "")
        assert revibed_vinyl_result[0]["title"] != "Kein Treffer"