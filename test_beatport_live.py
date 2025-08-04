#!/usr/bin/env python3
"""
Test live Beatport search with Catlow + Just Dancing
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from scrape_search import search_beatport

def test_beatport_live():
    """Test the actual Beatport scraper with the problematic search"""
    print("=" * 60)
    print("LIVE BEATPORT TEST: Catlow + Just Dancing")
    print("=" * 60)
    
    artist = "Catlow" 
    track = "Just Dancing"
    
    print(f"🎧 Testing: Artist='{artist}', Track='{track}'")
    print("Expected: Should show 'Kein Treffer' not 'nicht verfügbar'")
    
    try:
        result = search_beatport(artist, track)
        
        print(f"\n📊 Result count: {len(result)}")
        if result:
            first_result = result[0]
            print("🎯 First result:")
            for key, value in first_result.items():
                print(f"  {key}: '{value}'")
            
            # Check the title to see what type of response we got
            title = first_result.get('title', '')
            
            if title == 'Kein Treffer':
                print("✅ SUCCESS: Correct 'Kein Treffer' response")
            elif 'nicht verfügbar' in title:
                print("❌ PROBLEM: Shows 'nicht verfügbar' instead of 'Kein Treffer'")
            elif '❌' in title:
                print("❌ ERROR: Got error response")
            else:
                print("🤔 UNEXPECTED: Got actual result")
        else:
            print("❌ No results returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_beatport_live()