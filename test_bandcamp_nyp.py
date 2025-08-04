#!/usr/bin/env python3
"""
Test Bandcamp "name your price" extraction
"""

def test_bandcamp_nyp():
    """Test Bandcamp name your price detection"""
    print("=" * 60)
    print("BANDCAMP 'NAME YOUR PRICE' TEST")
    print("=" * 60)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        
        # Test with a known "name your price" track
        # Let's use the Catlow track we found
        test_url = "https://catlow2.bandcamp.com/track/i-just-wanna-2"
        
        print(f"🎼 Testing URL: {test_url}")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(options=options)
        driver.get(test_url)
        
        # Wait for page to load
        time.sleep(2)
        
        print("🔍 Looking for price elements...")
        
        # Check all possible price-related selectors
        price_selectors = [
            # Buy section selectors
            '.buyItem',
            '.buyItem .price',
            '.buyItem span[data-currency]',
            '.buyItem .buyItemExtra .price',
            '.buyItemPackage .price',
            
            # General price selectors
            '[class*="price"]',
            'span.currency',
            '.buyStuff .price',
            
            # Name your price specific
            '.name-your-price',
            '.nyp',
            '[class*="nyp"]',
            '[class*="name-your-price"]',
            
            # Button text
            'button.buy-now',
            '.buy-link',
            '.download-link'
        ]
        
        found_elements = []
        
        for selector in price_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for i, elem in enumerate(elements):
                    text = elem.text.strip()
                    if text:
                        found_elements.append({
                            'selector': selector,
                            'text': text,
                            'element_index': i
                        })
                        print(f"✅ '{selector}' [{i}]: '{text}'")
            except Exception as e:
                print(f"❌ Error with '{selector}': {e}")
        
        # Look for specific "name your price" text in page source
        page_source = driver.page_source.lower()
        nyp_phrases = ['name your price', 'nyp', 'pay what you want', 'free download']
        
        print("\n🔍 Checking page source for NYP phrases...")
        for phrase in nyp_phrases:
            if phrase in page_source:
                print(f"✅ Found '{phrase}' in page source")
            else:
                print(f"❌ '{phrase}' not found")
        
        # Try to find the specific buy section
        print("\n🔍 Analyzing buy section structure...")
        try:
            buy_section = driver.find_element(By.CSS_SELECTOR, '.buyStuff')
            print("✅ Found .buyStuff section")
            print("HTML snippet:")
            print(buy_section.get_attribute('innerHTML')[:500] + "...")
        except:
            print("❌ .buyStuff section not found")
        
        driver.quit()
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bandcamp_nyp()