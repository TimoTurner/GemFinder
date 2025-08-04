#!/usr/bin/env python3
"""
Test individual scrapers with Swag - Pina to debug results
"""

import sys
sys.path.append('.')
from scrape_search import search_beatport, search_bandcamp, search_traxsource

def test_individual_scrapers():
    print("Testing individual scrapers with Swag - Pina...")
    
    artist = "Swag"
    track = "Pina"
    
    scrapers = [
        ("Beatport", search_beatport),
        ("Bandcamp", search_bandcamp),
        ("Traxsource", search_traxsource)
    ]
    
    for name, scraper in scrapers:
        print(f"\n=== Testing {name} individually ===")
        try:
            result = scraper(artist, track)
            title = result[0].get('title', 'No title')
            search_time = result[0].get('search_time', 0)
            
            is_success = ('Fehler' not in title and 'Kein Treffer' not in title and 
                         '❌' not in title and 'nicht verfügbar' not in title)
            status = '✅' if is_success else '❌'
            
            print(f"{status} {name}: {title} ({search_time}s)")
            
            if is_success:
                # Show more details for successful results
                artist_found = result[0].get('artist', '')
                album = result[0].get('album', '')
                label = result[0].get('label', '')
                price = result[0].get('price', '')
                
                print(f"   Artist: {artist_found}")
                print(f"   Album: {album}")
                print(f"   Label: {label}")
                print(f"   Price: {price}")
                
        except Exception as e:
            print(f"❌ {name} error: {e}")

if __name__ == "__main__":
    test_individual_scrapers()