#!/usr/bin/env python3
"""
Real Scraper Test Script
Tests actual scraping functionality bypassing dummy mode
"""

import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_itunes_real():
    """Test real iTunes API"""
    print("🎵 Testing iTunes API...")
    try:
        import requests
        
        artist = "Daft Punk"
        track = "One More Time"
        
        print(f"Searching for: {artist} - {track}")
        start_time = time.time()
        
        query = f"{artist} {track}"
        url = "https://itunes.apple.com/search"
        params = {"term": query, "entity": "song", "limit": 1, "country": "DE"}
        
        response = requests.get(url, params=params, timeout=10)
        elapsed = time.time() - start_time
        
        print(f"iTunes API response: {elapsed:.2f}s, Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                r = data["results"][0]
                print(f"✅ iTunes SUCCESS: {r.get('trackName', '')} by {r.get('artistName', '')}")
                return True
            else:
                print("❌ iTunes: No results found")
                return False
        else:
            print(f"❌ iTunes API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ iTunes error: {e}")
        return False

def test_beatport_real():
    """Test real Beatport scraping"""
    print("🎧 Testing Beatport scraping...")
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        artist = "Carl Cox"
        track = "I Want You"  # Known track
        
        print(f"Searching for: {artist} - {track}")
        start_time = time.time()
        
        url = f"https://www.beatport.com/search/tracks?q={artist}%20{track}"
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        
        # Wait for search results
        results = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div[data-testid="tracks-list-item"]')
        ))
        
        elapsed = time.time() - start_time
        driver.quit()
        
        print(f"Beatport scraping: {elapsed:.2f}s, Found {len(results)} results")
        
        if results:
            print("✅ Beatport SUCCESS: Found search results")
            return True
        else:
            print("❌ Beatport: No results found")
            return False
            
    except Exception as e:
        print(f"❌ Beatport error: {e}")
        return False

def test_bandcamp_real():
    """Test real Bandcamp scraping"""
    print("🎸 Testing Bandcamp scraping...")
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        artist = "Radiohead"
        track = "Creep"  # Well-known track
        
        print(f"Searching for: {artist} - {track}")
        start_time = time.time()
        
        url = f"https://bandcamp.com/search?q={artist}%20{track}"
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        
        # Wait for search results
        results = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'li.searchresult')
        ))
        
        elapsed = time.time() - start_time
        driver.quit()
        
        print(f"Bandcamp scraping: {elapsed:.2f}s, Found {len(results)} results")
        
        if results:
            print("✅ Bandcamp SUCCESS: Found search results")
            return True
        else:
            print("❌ Bandcamp: No results found")
            return False
            
    except Exception as e:
        print(f"❌ Bandcamp error: {e}")
        return False

def test_traxsource_real():
    """Test real Traxsource scraping"""
    print("🏠 Testing Traxsource scraping...")
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        artist = "Armand Van Helden"
        track = "You Don't Know Me"  # Classic house track
        
        print(f"Searching for: {artist} - {track}")
        start_time = time.time()
        
        url = f"https://www.traxsource.com/search?term={artist}+{track}"
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        
        # Wait for search results
        results = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div.trk-row')
        ))
        
        elapsed = time.time() - start_time
        driver.quit()
        
        print(f"Traxsource scraping: {elapsed:.2f}s, Found {len(results)} results")
        
        if results:
            print("✅ Traxsource SUCCESS: Found search results")
            return True
        else:
            print("❌ Traxsource: No results found")
            return False
            
    except Exception as e:
        print(f"❌ Traxsource error: {e}")
        return False

def test_revibed_real():
    """Test real Revibed scraping"""
    print("💿 Testing Revibed scraping...")
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        artist = "Beatles"
        album = "Abbey Road"  # Well-known artist/album
        
        print(f"Searching for: {artist} - {album}")
        start_time = time.time()
        
        search_query = f"{artist} {album}".replace(' ', '+')
        url = f"https://revibed.com/marketplace/buy-now-rare-vinyl-records-cds-&-cassette-tapes?query={search_query}&sort=totalPurchasesCount%2CDESC&size=25&page=0"
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        
        # Wait for search results
        results = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div.styles_marketplaceGoods__r5WKf")
        ))
        
        elapsed = time.time() - start_time
        driver.quit()
        
        print(f"Revibed scraping: {elapsed:.2f}s, Found {len(results)} results")
        
        if results:
            print("✅ Revibed SUCCESS: Found search results")
            return True
        else:
            print("❌ Revibed: No results found")
            return False
            
    except Exception as e:
        print(f"❌ Revibed error: {e}")
        return False

def test_discogs_real():
    """Test real Discogs API"""
    print("💽 Testing Discogs API...")
    try:
        import os
        import requests
        from dotenv import load_dotenv
        
        # Load environment variables
        try:
            load_dotenv()
        except ImportError:
            pass
        
        DISCOGS_USER_TOKEN = os.environ.get("DISCOGS_USER_TOKEN")
        
        if not DISCOGS_USER_TOKEN:
            print("❌ Discogs API: No user token found in environment")
            return False
        
        artist = "The Beatles"
        track = "Hey Jude"
        
        print(f"Searching for: {artist} - {track}")
        start_time = time.time()
        
        query = f"{artist} {track}"
        url = "https://api.discogs.com/database/search"
        headers = {
            "Authorization": f"Discogs token={DISCOGS_USER_TOKEN}",
            "User-Agent": "GemFinderApp/1.0"
        }
        params = {
            "q": query,
            "per_page": 5,
            "page": 1
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        elapsed = time.time() - start_time
        
        print(f"Discogs API response: {elapsed:.2f}s, Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            print(f"✅ Discogs SUCCESS: Found {len(results)} results")
            return True
        else:
            print(f"❌ Discogs API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Discogs error: {e}")
        return False

def run_parallel_tests():
    """Run all scraper tests in parallel"""
    print("🚀 Starting parallel scraper tests...")
    print("=" * 50)
    
    test_functions = [
        test_itunes_real,
        test_beatport_real,
        test_bandcamp_real,
        test_traxsource_real,
        test_revibed_real,
        test_discogs_real
    ]
    
    results = {}
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        # Submit all tests
        future_to_test = {executor.submit(test_func): test_func.__name__ for test_func in test_functions}
        
        # Collect results as they complete
        for future in as_completed(future_to_test):
            test_name = future_to_test[future]
            try:
                result = future.result()
                results[test_name] = result
                print(f"✓ {test_name} completed")
            except Exception as exc:
                print(f"✗ {test_name} generated an exception: {exc}")
                results[test_name] = False
    
    total_time = time.time() - start_time
    
    print("=" * 50)
    print("🏁 FINAL RESULTS:")
    print("=" * 50)
    
    success_count = 0
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if success:
            success_count += 1
    
    print("=" * 50)
    print(f"📊 Summary: {success_count}/{len(results)} tests passed")
    print(f"⏱️ Total time: {total_time:.2f}s")
    print("=" * 50)
    
    return results

if __name__ == "__main__":
    print("🧪 Real Scraper Test Suite")
    print("Testing actual APIs and scrapers (bypassing dummy mode)")
    print()
    
    # Check if we should run individual tests
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        if test_name == "itunes":
            test_itunes_real()
        elif test_name == "beatport":
            test_beatport_real()
        elif test_name == "bandcamp":
            test_bandcamp_real()
        elif test_name == "traxsource":
            test_traxsource_real()
        elif test_name == "revibed":
            test_revibed_real()
        elif test_name == "discogs":
            test_discogs_real()
        else:
            print("Usage: python test_real_scrapers.py [itunes|beatport|bandcamp|traxsource|revibed|discogs]")
    else:
        # Run all tests in parallel
        run_parallel_tests()