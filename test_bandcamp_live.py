#!/usr/bin/env python3
"""
Test live Bandcamp search with Catlow + Just Dancing
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from scrape_search import search_bandcamp

def test_bandcamp_live():
    """Test the actual Bandcamp scraper with the problematic search"""
    print("=" * 60)
    print("LIVE BANDCAMP TEST: Catlow + Just Dancing")
    print("=" * 60)
    
    artist = "Catlow" 
    track = "Just Dancing"
    
    print(f"🎼 Testing: Artist='{artist}', Track='{track}'")
    print("Expected: Should find result with price='nyp'")
    
    try:
        result = search_bandcamp(artist, track)
        
        print(f"\n📊 Result count: {len(result)}")
        if result:
            first_result = result[0]
            print("🎯 First result:")
            for key, value in first_result.items():
                print(f"  {key}: '{value}'")
            
            # Check if this is a valid result
            title = first_result.get('title', '')
            price = first_result.get('price', '')
            
            if title.lower() in ['kein treffer', 'fehler']:
                print("❌ Got 'no results' response")
            elif '❌' in title:
                print("❌ Got error response")
            elif price == 'nyp':
                print("✅ SUCCESS: Found NYP price")
            elif price:
                print(f"✅ SUCCESS: Found price: {price}")
            else:
                print("🤔 ISSUE: Found result but no price")
        else:
            print("❌ No results returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bandcamp_live()