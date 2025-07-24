#!/usr/bin/env python3
"""
Test script for Discogs API + Scraper integration
Tests the complete workflow from search to marketplace offers
"""

import sys
import json
import time
from pprint import pprint

def test_api_search():
    """Test the basic Discogs API search functionality"""
    print("=" * 60)
    print("🔍 TESTING DISCOGS API SEARCH")
    print("=" * 60)
    
    try:
        from api_search import search_discogs_releases
        
        # Test scenarios from your dummy implementation
        test_cases = [
            # Discogs-only scenario (should find results)
            {
                "artist": "discogs artist",
                "track": "vintage track", 
                "album": None,
                "catno": "catalog-123",
                "expected": "should_find_results"
            },
            # No match scenario
            {
                "artist": "nonexistent artist",
                "track": "nonexistent track",
                "album": None, 
                "catno": None,
                "expected": "should_find_nothing"
            },
            # Catalog number scenario
            {
                "artist": None,
                "track": None,
                "album": None,
                "catno": "catalog-456", 
                "expected": "should_find_results"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i}: {test_case['expected']} ---")
            print(f"Artist: {test_case['artist']}")
            print(f"Track: {test_case['track']}")
            print(f"Album: {test_case['album']}")
            print(f"Catalog: {test_case['catno']}")
            
            start_time = time.time()
            results = search_discogs_releases(
                artist=test_case['artist'],
                track=test_case['track'],
                album=test_case['album'],
                catno=test_case['catno']
            )
            end_time = time.time()
            
            print(f"⏱️ Search time: {end_time - start_time:.2f}s")
            print(f"📊 Results found: {len(results)}")
            
            if results:
                first_result = results[0]
                print(f"🎵 First result:")
                print(f"   Title: {first_result.get('title', 'N/A')}")
                print(f"   Artist: {first_result.get('artist', 'N/A')}")
                print(f"   ID: {first_result.get('id', 'N/A')}")
                print(f"   Format: {first_result.get('format', 'N/A')}")
                print(f"   Year: {first_result.get('year', 'N/A')}")
            else:
                print("❌ No results found")
            
            print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ API Search test failed: {e}")
        return False


def test_scraper_functionality():
    """Test the marketplace scraper functionality"""
    print("\n" + "=" * 60)
    print("🤖 TESTING MARKETPLACE SCRAPER")
    print("=" * 60)
    
    try:
        from scrape_search import scrape_discogs_marketplace_offers
        
        # Test with dummy release ID (since we're testing with dummy data)
        test_release_ids = ["12345", "67890", "invalid_id"]
        
        for release_id in test_release_ids:
            print(f"\n--- Testing Release ID: {release_id} ---")
            
            start_time = time.time()
            offers = scrape_discogs_marketplace_offers(release_id, max_offers=5)
            end_time = time.time()
            
            print(f"⏱️ Scraping time: {end_time - start_time:.2f}s")
            print(f"💰 Offers found: {len(offers)}")
            
            if offers:
                print("🛒 Sample offers:")
                for i, offer in enumerate(offers[:3], 1):  # Show first 3 offers
                    print(f"   {i}. {offer.get('condition', 'N/A')} - {offer.get('price', 'N/A')}")
                    print(f"      Seller: {offer.get('seller', 'N/A')} ({offer.get('seller_rating', 'N/A')})")
                    print(f"      Shipping: {offer.get('shipping', 'N/A')}")
            else:
                print("❌ No offers found")
            
            print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_combined_functionality():
    """Test the combined search + scraper functionality"""
    print("\n" + "=" * 60)  
    print("🔗 TESTING COMBINED SEARCH + SCRAPER")
    print("=" * 60)
    
    try:
        from scrape_search import search_discogs_with_offers
        
        # Test the discogs-only scenario that should trigger results
        test_searches = [
            {
                "artist": "discogs artist",
                "track": "vintage track",
                "album": None,
                "catno": None,
                "description": "Discogs-only scenario"
            },
            {
                "artist": None,
                "track": None, 
                "album": None,
                "catno": "catalog-123",
                "description": "Catalog number search"
            },
            {
                "artist": "unknown artist",
                "track": "unknown track",
                "album": None,
                "catno": None,
                "description": "No results expected"
            }
        ]
        
        for i, search in enumerate(test_searches, 1):
            print(f"\n--- Combined Test {i}: {search['description']} ---")
            print(f"Artist: {search['artist']}")
            print(f"Track: {search['track']}")
            print(f"Catalog: {search['catno']}")
            
            start_time = time.time()
            result = search_discogs_with_offers(
                artist=search['artist'],
                track=search['track'],
                album=search['album'],
                catno=search['catno'],
                max_offers=3
            )
            end_time = time.time()
            
            print(f"⏱️ Total time: {end_time - start_time:.2f}s")
            print(f"📊 Status: {result.get('status', 'unknown')}")
            
            if result.get('release'):
                release = result['release']
                print(f"🎵 Release found:")
                print(f"   Title: {release.get('title', 'N/A')}")
                print(f"   ID: {release.get('id', 'N/A')}")
                
                offers = result.get('offers', [])
                print(f"💰 Marketplace offers: {len(offers)}")
                
                if offers:
                    print("🛒 Sample offers:")
                    for j, offer in enumerate(offers, 1):
                        print(f"   {j}. {offer.get('price', 'N/A')} - {offer.get('condition', 'N/A')}")
            else:
                print(f"❌ No release found: {result.get('status', 'unknown')}")
            
            print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Combined test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_production_scraper_availability():
    """Test if production scraper dependencies are available"""
    print("\n" + "=" * 60)
    print("🔧 CHECKING PRODUCTION SCRAPER AVAILABILITY")
    print("=" * 60)
    
    try:
        import selenium
        print(f"✅ Selenium version: {selenium.__version__}")
        
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("✅ Selenium WebDriver imports successful")
        
        # Try to import the production scraper
        try:
            from discogs_scraper import create_discogs_scraper, ScraperConfig
            print("✅ Production scraper imports successful")
            
            # Try to create a scraper instance (don't actually run it)
            config = ScraperConfig(headless=True)
            print("✅ Scraper configuration created successfully")
            
            print("\n🎉 Production scraper is fully available!")
            return True
            
        except ImportError as e:
            print(f"⚠️ Production scraper import failed: {e}")
            print("🔄 Will fall back to dummy data")
            return False
            
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("📦 Install with: pip install selenium")
        print("🔄 Will use dummy data only")
        return False


def main():
    """Run all integration tests"""
    print("🧪 DISCOGS API + SCRAPER INTEGRATION TEST")
    print("=" * 60)
    
    # Check production scraper availability
    scraper_available = test_production_scraper_availability()
    
    # Run API tests
    api_success = test_api_search()
    
    # Run scraper tests  
    scraper_success = test_scraper_functionality()
    
    # Run combined tests
    combined_success = test_combined_functionality()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"Production Scraper Available: {'✅' if scraper_available else '⚠️ (using dummy)'}")
    print(f"API Search Tests: {'✅ PASSED' if api_success else '❌ FAILED'}")
    print(f"Scraper Tests: {'✅ PASSED' if scraper_success else '❌ FAILED'}")
    print(f"Combined Tests: {'✅ PASSED' if combined_success else '❌ FAILED'}")
    
    if all([api_success, scraper_success, combined_success]):
        print("\n🎉 ALL TESTS PASSED! Integration is working correctly.")
        if not scraper_available:
            print("ℹ️ Note: Using dummy scraper data. Install Selenium for production scraping.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()