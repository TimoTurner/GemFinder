#!/usr/bin/env python3
"""
Test the new parallel search function
"""

import sys
sys.path.append('.')
from scrape_search import search_digital_releases_parallel

def test_new_parallel():
    print("Testing improved parallel search function...")
    
    # Test with a track that should work on multiple platforms
    artist = "Daft Punk"
    track = "One More Time"
    album = ""
    catno = ""
    
    print(f"Searching for: {artist} - {track}")
    print("=" * 50)
    
    results = search_digital_releases_parallel(artist, track, album, catno)
    
    print("=" * 50)
    print(f"Total results: {len(results)}")
    
    for result in results:
        platform = result.get('platform', 'Unknown')
        title = result.get('title', 'No title')
        search_time = result.get('search_time', 0)
        status = '✅' if 'Fehler' not in title and 'Kein Treffer' not in title else '❌'
        print(f"{status} {platform}: {title} ({search_time}s)")

if __name__ == "__main__":
    test_new_parallel()