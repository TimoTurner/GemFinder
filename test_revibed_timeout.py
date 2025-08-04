#!/usr/bin/env python3
"""
Test Revibed scraper for timeout issues
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from scrape_search import search_revibed

def test_revibed_timeout():
    """Test Revibed with searches that should have no results"""
    print("=" * 60)
    print("REVIBED TIMEOUT TEST")
    print("=" * 60)
    
    # Test cases that should have no results
    test_cases = [
        ("NonExistentArtist123", "NonExistentAlbum456"),
        ("Catlow", ""),  # Artist only search
        ("", "SomeRandomAlbum"),  # Album only search
    ]
    
    for i, (artist, album) in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: artist='{artist}', album='{album}' ---")
        
        try:
            result = search_revibed(artist, album)
            
            if result:
                first_result = result[0]
                title = first_result.get('title', '')
                
                print(f"📊 Title: '{title}'")
                
                if title == 'Kein Treffer':
                    print("✅ SUCCESS: Shows 'Kein Treffer'")
                elif 'nicht verfügbar' in title:
                    print("❌ PROBLEM: Shows 'nicht verfügbar' - needs fixing")
                elif '❌' in title:
                    print("❌ ERROR: Shows error message")
                else:
                    print("🤔 UNEXPECTED: Got actual result")
            else:
                print("❌ No results returned")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_revibed_timeout()