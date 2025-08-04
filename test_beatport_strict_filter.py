#!/usr/bin/env python3
"""
Test the new Beatport strict filtering logic
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from scrape_search import search_beatport

def test_beatport_strict_filter():
    """Test Beatport with different search combinations"""
    print("=" * 60)
    print("BEATPORT STRICT FILTER TEST")
    print("=" * 60)
    
    # Test cases: should be more precise now
    test_cases = [
        # Should find specific matches
        ("Catlow", "Just Dancing", ""),  # Should find exact or close matches only
        ("Pina", "Swag", ""),  # Previous working example
        
        # Should be more strict
        ("Popular Artist", "Common Word", ""),  # Should filter out loose matches
    ]
    
    for i, (artist, track, album) in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: Artist='{artist}', Track='{track}', Album='{album}' ---")
        
        try:
            result = search_beatport(artist, track, album)
            
            if result:
                first_result = result[0]
                title = first_result.get('title', '')
                found_artist = first_result.get('artist', '')
                found_album = first_result.get('album', '')
                
                print(f"📊 Result:")
                print(f"  Title: '{title}'")
                print(f"  Artist: '{found_artist}'")
                print(f"  Album: '{found_album}'")
                
                if title == 'Kein Treffer':
                    print("✅ No results (strict filtering working)")
                elif '❌' in title:
                    print("❌ Error occurred")
                else:
                    print("🎯 Found result - checking if it's relevant...")
                    # Manual check if the result makes sense
                    if artist.lower() in (title + found_artist + found_album).lower() and track.lower() in (title + found_artist + found_album).lower():
                        print("✅ Result appears relevant")
                    else:
                        print("❌ Result may not be relevant - strict filter may need adjustment")
            else:
                print("❌ No results returned")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_beatport_strict_filter()