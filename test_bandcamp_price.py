#!/usr/bin/env python3
"""
Test Bandcamp price extraction
"""

def test_bandcamp_price():
    """Test real Bandcamp price extraction"""
    print("=" * 60)
    print("BANDCAMP PRICE EXTRACTION TEST")
    print("=" * 60)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        
        artist = "Catlow"
        track = "I just wanna"
        
        print(f"🎼 Testing search: '{artist}' - '{track}'")
        url = f"https://bandcamp.com/search?q={artist}%20{track}"
        print(f"🔗 URL: {url}")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        search_results = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.searchresult'))
        )
        
        print(f"✅ Found {len(search_results)} search results")
        
        for i, result in enumerate(search_results[:2]):  # Check first 2 results
            try:
                title = result.find_element(By.CSS_SELECTOR, '.heading a').text.strip()
                print(f"\n--- Result {i+1}: {title} ---")
                
                # Look for price elements in different locations
                price_selectors = [
                    '.price',
                    '.buylink',
                    '.buy-link',
                    '[class*="price"]',
                    '[class*="buy"]'
                ]
                
                price_found = False 
                for selector in price_selectors:
                    try:
                        price_elements = result.find_elements(By.CSS_SELECTOR, selector)
                        if price_elements:
                            print(f"Found price elements with '{selector}': {len(price_elements)}")
                            for j, elem in enumerate(price_elements):
                                text = elem.text.strip()
                                if text:
                                    print(f"  Element {j+1}: '{text}'")
                                    price_found = True
                    except:
                        pass
                
                if not price_found:
                    print("❌ No price elements found in search result")
                    print("🔍 Full result HTML:")
                    print(result.get_attribute('outerHTML')[:500] + "...")
                    
            except Exception as e:
                print(f"❌ Error processing result {i+1}: {e}")
        
        driver.quit()
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bandcamp_price()