#!/usr/bin/env python3
"""
Debug script to test Traxsource scraper with specific search terms
"""

import sys
import time
from scrape_search import search_traxsource

def test_traxsource_debug():
    """Test Traxsource scraper with debug output"""
    print("=" * 60)
    print("TRAXSOURCE DEBUG TEST")
    print("=" * 60)
    
    # Test case: Should return "Kein Treffer" not "nicht verfügbar"
    artist = "Catlow"
    track = "I just wanna"
    
    print(f"Testing search: Artist='{artist}', Track='{track}'")
    print(f"Expected: Should find no results and return 'Kein Treffer'")
    print(f"Browser test: https://www.traxsource.com/search?term={artist}+{track.replace(' ', '+')}")
    print("-" * 60)
    
    try:
        result = search_traxsource(artist, track)
        
        print("RESULT:")
        print(f"Platform: {result[0].get('platform', 'N/A')}")
        print(f"Title: {result[0].get('title', 'N/A')}")
        print(f"Artist: {result[0].get('artist', 'N/A')}")
        print(f"Search Time: {result[0].get('search_time', 'N/A')}")
        
        if result[0].get('title') == 'Kein Treffer':
            print("✅ SUCCESS: Scraper working correctly, no results found")
        elif 'nicht verfügbar' in result[0].get('title', ''):
            print("❌ ERROR: Scraper failed with exception")
        else:
            print("🤔 UNEXPECTED: Got actual result")
            
    except Exception as e:
        print(f"❌ SCRIPT ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    test_traxsource_debug()