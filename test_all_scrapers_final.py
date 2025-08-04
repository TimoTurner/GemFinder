#!/usr/bin/env python3
"""
Final test of all scrapers for timeout issues
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from scrape_search import search_beatport, search_bandcamp, search_traxsource, search_revibed

def test_all_scrapers_final():
    """Test all scrapers with searches that should have no results"""
    print("=" * 60)
    print("FINAL TEST: ALL SCRAPERS - NO RESULTS HANDLING")
    print("=" * 60)
    
    # Test search that should have no results
    artist = "NonExistentArtist12345"
    track = "NonExistentTrack67890" 
    
    scrapers = [
        ("Beatport", lambda: search_beatport(artist, track)),
        ("Bandcamp", lambda: search_bandcamp(artist, track)),
        ("Traxsource", lambda: search_traxsource(artist, track)),
        ("Revibed", lambda: search_revibed(artist, "NonExistentAlbum"))
    ]
    
    for scraper_name, scraper_func in scrapers:
        print(f"\n--- {scraper_name} ---")
        
        try:
            result = scraper_func()
            
            if result:
                title = result[0].get('title', '')
                
                if title == 'Kein Treffer':
                    print(f"✅ {scraper_name}: SUCCESS - Shows 'Kein Treffer'")
                elif 'nicht verfügbar' in title:
                    print(f"❌ {scraper_name}: PROBLEM - Shows 'nicht verfügbar'")
                elif '❌' in title:
                    print(f"⚠️ {scraper_name}: ERROR - Shows error message: {title}")
                else:
                    print(f"🤔 {scraper_name}: UNEXPECTED - Got result: {title}")
            else:
                print(f"❌ {scraper_name}: No results returned")
                
        except Exception as e:
            print(f"❌ {scraper_name}: Exception: {e}")
    
    print("\n" + "="*60)
    print("SUMMARY: All scrapers should show '✅ SUCCESS' above")
    print("="*60)

if __name__ == "__main__":
    test_all_scrapers_final()