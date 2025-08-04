#!/usr/bin/env python3
"""
Test parallel search with house music that should work on all platforms
"""

import sys
sys.path.append('.')
from scrape_search import search_digital_releases_parallel

def test_house_parallel():
    print("Testing parallel search with house music...")
    
    # Use a house track that should work on Traxsource
    artist = "Armand Van Helden"
    track = "You Don't Know Me"
    album = ""
    catno = ""
    
    print(f"Searching for: {artist} - {track}")
    print("=" * 50)
    
    results = search_digital_releases_parallel(artist, track, album, catno)
    
    print("=" * 50)
    print(f"Total results: {len(results)}")
    
    success_count = 0
    for result in results:
        platform = result.get('platform', 'Unknown')
        title = result.get('title', 'No title')
        search_time = result.get('search_time', 0)
        
        is_success = ('Fehler' not in title and 'Kein Treffer' not in title and 
                     '❌' not in title and 'nicht verfügbar' not in title)
        status = '✅' if is_success else '❌'
        
        if is_success:
            success_count += 1
            
        print(f"{status} {platform}: {title} ({search_time}s)")
    
    print(f"\nSuccess rate: {success_count}/3 platforms working")

if __name__ == "__main__":
    test_house_parallel()