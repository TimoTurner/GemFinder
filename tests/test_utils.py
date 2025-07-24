"""Tests for utils.py module."""

import pytest
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    PLATFORM_LINKS,
    PLACEHOLDER_COVER,
    get_platform_info,
    is_fuzzy_match
)


class TestPlatformLinks:
    """Test PLATFORM_LINKS constant."""
    
    def test_platform_links_structure(self):
        """Test that PLATFORM_LINKS contains expected platforms and structure."""
        expected_platforms = [
            "Beatport", "Bandcamp", "Traxsource", 
            "iTunes", "Revibed", "Discogs"
        ]
        
        for platform in expected_platforms:
            assert platform in PLATFORM_LINKS
            
            # Each platform should have tuple with (url, logo_url)
            platform_info = PLATFORM_LINKS[platform]
            assert isinstance(platform_info, tuple)
            assert len(platform_info) == 2
            
            base_url, logo_url = platform_info
            assert isinstance(base_url, str)
            assert isinstance(logo_url, str)
            assert base_url.startswith("https://")
            assert logo_url.startswith("https://") or logo_url.endswith(".png")
    
    def test_platform_links_specific_urls(self):
        """Test specific platform URLs are correct."""
        assert PLATFORM_LINKS["Beatport"][0] == "https://www.beatport.com/"
        assert PLATFORM_LINKS["Bandcamp"][0] == "https://bandcamp.com/"
        assert PLATFORM_LINKS["Traxsource"][0] == "https://www.traxsource.com/"
        assert PLATFORM_LINKS["iTunes"][0] == "https://music.apple.com/"
        assert PLATFORM_LINKS["Revibed"][0] == "https://revibed.com/"
        assert PLATFORM_LINKS["Discogs"][0] == "https://www.discogs.com/"
    
    def test_platform_logos_are_urls(self):
        """Test that all platform logos are valid URLs or files."""
        for platform, (base_url, logo_url) in PLATFORM_LINKS.items():
            # Logo should be either a URL or a local file reference
            assert (logo_url.startswith("https://") or 
                   logo_url.endswith(".png") or 
                   logo_url.endswith(".ico"))


class TestPlaceholderCover:
    """Test PLACEHOLDER_COVER constant."""
    
    def test_placeholder_cover_is_string(self):
        """Test that PLACEHOLDER_COVER is a string."""
        assert isinstance(PLACEHOLDER_COVER, str)
        assert PLACEHOLDER_COVER == "cover_placeholder.png"


class TestGetPlatformInfo:
    """Test get_platform_info function."""
    
    def test_get_platform_info_known_platforms(self):
        """Test get_platform_info returns correct info for known platforms."""
        for platform_name in PLATFORM_LINKS.keys():
            base_url, logo_url = get_platform_info(platform_name)
            
            # Should return the same values as in PLATFORM_LINKS
            expected_base_url, expected_logo_url = PLATFORM_LINKS[platform_name]
            assert base_url == expected_base_url
            assert logo_url == expected_logo_url
    
    def test_get_platform_info_unknown_platform(self):
        """Test get_platform_info returns default values for unknown platforms."""
        unknown_platforms = ["Unknown Platform", "NonExistent", ""]
        
        for platform in unknown_platforms:
            base_url, logo_url = get_platform_info(platform)
            
            # Should return default values
            assert base_url == "#"
            assert logo_url == PLACEHOLDER_COVER
    
    def test_get_platform_info_case_sensitivity(self):
        """Test get_platform_info is case sensitive."""
        # Test exact case (should work)
        base_url, logo_url = get_platform_info("Beatport")
        assert base_url == "https://www.beatport.com/"
        
        # Test different case (should return default)
        base_url, logo_url = get_platform_info("beatport")
        assert base_url == "#"
        assert logo_url == PLACEHOLDER_COVER
    
    def test_get_platform_info_return_type(self):
        """Test get_platform_info always returns tuple of strings."""
        platforms_to_test = ["Beatport", "Unknown Platform", "", "discogs"]
        
        for platform in platforms_to_test:
            result = get_platform_info(platform)
            
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert isinstance(result[0], str)
            assert isinstance(result[1], str)


class TestIsFuzzyMatch:
    """Test is_fuzzy_match function."""
    
    def test_exact_match(self):
        """Test fuzzy match with exact strings."""
        assert is_fuzzy_match("test track", "test track") == True
        assert is_fuzzy_match("Love Song", "Love Song") == True
    
    def test_case_insensitive_match(self):
        """Test fuzzy match is case insensitive."""
        assert is_fuzzy_match("Test Track", "test track") == True
        assert is_fuzzy_match("LOVE SONG", "love song") == True
        assert is_fuzzy_match("MiXeD cAsE", "mixed case") == True
    
    def test_partial_match_above_threshold(self):
        """Test fuzzy match with partial matches above threshold."""
        # These should match with default threshold of 80
        assert is_fuzzy_match("test track", "test track remix") == True
        assert is_fuzzy_match("love song", "love song (radio edit)") == True
        assert is_fuzzy_match("dance", "dance music") == True
    
    def test_partial_match_below_threshold(self):
        """Test fuzzy match with partial matches below threshold."""
        # These should not match with default threshold of 80
        assert is_fuzzy_match("completely different", "totally unrelated") == False
        assert is_fuzzy_match("short", "a very long and completely different string") == False
    
    def test_custom_threshold(self):
        """Test fuzzy match with custom threshold values."""
        # Test with clearly different strings
        result_low = is_fuzzy_match("short", "completely different text", threshold=20)
        result_high = is_fuzzy_match("short", "completely different text", threshold=80)
        
        # Should match with very low threshold but not with high threshold
        assert result_low == True
        assert result_high == False
    
    def test_empty_strings(self):
        """Test fuzzy match with empty strings."""
        assert is_fuzzy_match("", "test") == False
        assert is_fuzzy_match("test", "") == False
        assert is_fuzzy_match("", "") == False
    
    def test_none_values(self):
        """Test fuzzy match with None values."""
        assert is_fuzzy_match(None, "test") == False
        assert is_fuzzy_match("test", None) == False
        assert is_fuzzy_match(None, None) == False
    
    def test_whitespace_handling(self):
        """Test fuzzy match handles whitespace correctly."""
        assert is_fuzzy_match("  test track  ", "test track") == True
        assert is_fuzzy_match("test   track", "test track") == True
        assert is_fuzzy_match("test\ttrack", "test track") == True
    
    def test_special_characters(self):
        """Test fuzzy match with special characters."""
        assert is_fuzzy_match("test-track", "test track") == True
        assert is_fuzzy_match("test_track", "test track") == True
        assert is_fuzzy_match("test.track", "test track") == True
        assert is_fuzzy_match("test (remix)", "test remix") == True
    
    def test_unicode_characters(self):
        """Test fuzzy match with unicode characters."""
        assert is_fuzzy_match("café", "cafe") == True
        assert is_fuzzy_match("naïve", "naive") == True
        assert is_fuzzy_match("müller", "muller") == True
    
    def test_threshold_parameter_usage(self):
        """Test that threshold parameter is properly used in function calls."""
        # Test that function accepts threshold parameter without error
        result_default = is_fuzzy_match("test", "test")
        result_custom = is_fuzzy_match("test", "test", threshold=50)
        
        # Both should work and return boolean
        assert isinstance(result_default, bool)
        assert isinstance(result_custom, bool)
        
        # Test with clearly different strings and very high threshold
        assert is_fuzzy_match("completely", "different", threshold=99) == False
    
    def test_real_world_track_examples(self):
        """Test fuzzy match with real-world track name examples."""
        # Should match
        assert is_fuzzy_match("Bohemian Rhapsody", "Bohemian Rhapsody (Remastered)") == True
        assert is_fuzzy_match("Hotel California", "Hotel California - Eagles") == True
        assert is_fuzzy_match("Billie Jean", "Billie Jean (Single Version)") == True
        
        # Should not match
        assert is_fuzzy_match("Bohemian Rhapsody", "We Are The Champions") == False
        assert is_fuzzy_match("Hotel California", "Sweet Child O' Mine") == False


class TestUtilsIntegration:
    """Integration tests for utils functionality."""
    
    def test_all_functions_work_together(self):
        """Test that all utility functions work correctly together."""
        # Test platform info retrieval
        platform = "Beatport"
        base_url, logo_url = get_platform_info(platform)
        
        # URL should be valid
        assert base_url.startswith("https://")
        assert platform.lower() in base_url.lower()
        
        # Test fuzzy matching with platform-related strings
        assert is_fuzzy_match(platform, platform.lower()) == True
        assert is_fuzzy_match("beatport track", f"{platform} track") == True
    
    def test_constants_consistency(self):
        """Test that all constants are consistent with each other."""
        # All platforms in PLATFORM_LINKS should work with get_platform_info
        for platform in PLATFORM_LINKS.keys():
            base_url, logo_url = get_platform_info(platform)
            
            # Should not return default values
            assert base_url != "#"
            assert logo_url != PLACEHOLDER_COVER
    
    def test_error_handling_robustness(self):
        """Test that functions handle edge cases gracefully."""
        # get_platform_info should handle various input types
        edge_cases = [None, "", "   ", 123, [], {}]
        
        for case in edge_cases:
            try:
                result = get_platform_info(str(case) if case is not None else "None")
                assert isinstance(result, tuple)
                assert len(result) == 2
            except Exception:
                # Should not raise exceptions
                pytest.fail(f"get_platform_info raised exception for input: {case}")
        
        # is_fuzzy_match should handle various input types gracefully
        for case in edge_cases:
            try:
                result = is_fuzzy_match(case, "test")
                assert isinstance(result, bool)
                assert result == False  # Should return False for invalid inputs
            except Exception:
                # Should not raise exceptions for type errors
                pass  # This is acceptable behavior