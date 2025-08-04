#!/usr/bin/env python3
"""
Test parallel search with Swag - Pina (should work on all digital platforms)
"""

import sys
sys.path.append('.')
from scrape_search import search_digital_releases_parallel

def test_swag_pina():
    print("Testing parallel search with Swag - Pina...")
    print("(Should get positive results on ALL digital platforms)")
    
    artist = "Swag"
    track = "Pina"
    album = ""
    catno = ""
    
    print(f"Searching for: {artist} - {track}")
    print("=" * 60)
    
    results = search_digital_releases_parallel(artist, track, album, catno)
    
    print("=" * 60)
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
    
    print(f"\n📊 Success rate: {success_count}/3 digital platforms working")
    
    if success_count == 3:
        print("🎉 PERFECT! All digital platforms found results!")
    elif success_count >= 2:
        print("✅ GOOD! Most platforms working")
    else:
        print("⚠️  Issues detected with digital scrapers")

if __name__ == "__main__":
    test_swag_pina()