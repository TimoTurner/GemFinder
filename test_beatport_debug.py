#!/usr/bin/env python3
"""
Debug Beatport scraper specifically for Catlow + Just Dancing
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_beatport_debug():
    """Debug Beatport scraper step by step"""
    print("=" * 60)
    print("BEATPORT DEBUG: Catlow + Just Dancing")
    print("=" * 60)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        
        artist = "Catlow"
        track = "Just Dancing"
        
        print(f"🎧 Testing: '{artist}' - '{track}'")
        start_time = time.time()
        
        url = f"https://www.beatport.com/search?q={artist}+{track}"
        print(f"🔗 URL: {url}")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        print("🔄 Creating driver...")
        driver = webdriver.Chrome(options=options)
        
        print("🔄 Loading page...")
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        print("🔄 Waiting for track rows...")
        
        # This is the exact selector from the scraper
        try:
            track_rows = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.bucket-item.ec-item'))
            )
            print(f"✅ Found {len(track_rows)} track rows")
            
            if len(track_rows) == 0:
                print("📭 No results - should return 'Kein Treffer'")
            else:
                print("🎯 Processing first result...")
                
                # Try to extract data from first result like the scraper does
                row = track_rows[0]
                
                try:
                    title_elem = row.find_element(By.CSS_SELECTOR, 'p.buk-track-title')
                    title = title_elem.text.strip()
                    print(f"  Title: '{title}'")
                except Exception as e:
                    print(f"  ❌ Title error: {e}")
                
                try:
                    artists_elem = row.find_element(By.CSS_SELECTOR, 'p.buk-track-artists')
                    artists = artists_elem.text.strip()
                    print(f"  Artists: '{artists}'")
                except Exception as e:
                    print(f"  ❌ Artists error: {e}")
                
                try:
                    price_elem = row.find_element(By.CSS_SELECTOR, 'button.add-to-cart .price')
                    price = price_elem.text.strip()
                    print(f"  Price: '{price}'")
                except Exception as e:
                    print(f"  ❌ Price error: {e}")
                    
        except Exception as e:
            print(f"❌ Failed to find track rows: {e}")
            
            # Check what's actually on the page
            page_source = driver.page_source
            print(f"📄 Page loaded: {len(page_source)} characters")
            
            if "no results" in page_source.lower() or "keine ergebnisse" in page_source.lower():
                print("📭 Page shows 'no results'")
            elif "access denied" in page_source.lower() or "blocked" in page_source.lower():
                print("🚫 Page shows access blocked")
            else:
                print("🤔 Page loaded but track rows not found")
                
                # Try alternative selectors
                alt_selectors = ['.track-row', '.search-result', '[class*="track"]', '[class*="item"]']
                for selector in alt_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        print(f"  Alternative '{selector}': {len(elements)} elements")
                    except:
                        pass
        
        driver.quit()
        elapsed = time.time() - start_time
        print(f"⏱️ Total time: {elapsed:.3f}s")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_beatport_debug()