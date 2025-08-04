#!/usr/bin/env python3
"""
Detailed Traxsource scraper debug
"""

def test_traxsource_detailed():
    """Detailed test of Traxsource scraper logic"""
    print("=" * 60)
    print("DETAILED TRAXSOURCE TEST")
    print("=" * 60)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        
        artist = "Catlow"
        track = "I just wanna"
        
        print(f"🎶 Testing search: '{artist}' - '{track}'")
        start_time = time.time()
        
        url = f"https://www.traxsource.com/search?term={artist}+{track}"
        print(f"🔗 URL: {url}")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(options=options)
        print("✅ Driver created")
        
        driver.get(url)
        print("✅ Page loaded")
        
        wait = WebDriverWait(driver, 10)
        print("🔄 Waiting for track rows...")
        
        # This is where the original scraper might fail
        try:
            track_rows = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.trk-row'))
            )
            print(f"✅ Found {len(track_rows)} track rows")
            
            if len(track_rows) == 0:
                print("📭 No results found - should return 'Kein Treffer'")
            else:
                print("🎯 Results found - processing...")
                
        except Exception as e:
            print(f"❌ Failed to find track rows: {e}")
            print("🔍 Let's check what's actually on the page...")
            
            # Check page source for debugging
            page_source = driver.page_source
            if "No results found" in page_source or "no tracks found" in page_source.lower():
                print("📭 Page shows 'No results' - should return 'Kein Treffer'")
            else:
                print("🤔 Page loaded but selector 'div.trk-row' not found")
                print("This could be a selector issue or page structure change")
                
                # Try alternative selectors
                try:
                    alt_results = driver.find_elements(By.CSS_SELECTOR, '.search-result')
                    print(f"Alternative selector '.search-result': {len(alt_results)} elements")
                except:
                    pass
                    
                try:
                    alt_results2 = driver.find_elements(By.CSS_SELECTOR, '[class*="track"]')
                    print(f"Alternative selector '[class*=\"track\"]': {len(alt_results2)} elements")
                except:
                    pass
        
        driver.quit()
        elapsed_time = time.time() - start_time
        print(f"⏱️ Total time: {elapsed_time:.3f}s")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_traxsource_detailed()