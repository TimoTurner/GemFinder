#!/usr/bin/env python3
"""
Test the fixed Bandcamp NYP price extraction
"""

def test_bandcamp_price_extraction():
    """Test the updated Bandcamp price extraction logic"""
    print("=" * 60)
    print("BANDCAMP NYP PRICE EXTRACTION TEST")
    print("=" * 60)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        import time
        import re
        
        # Test URLs
        test_urls = [
            "https://catlow2.bandcamp.com/track/i-just-wanna-2",  # £1 GBP oder mehr
            "https://catlow2.bandcamp.com/track/just-dancing"     # name your price
        ]
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(options=options)
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n--- Test {i}: {url} ---")
            
            # Open new tab
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url)
            time.sleep(2)
            
            # Apply the same logic as in extract_bandcamp_price
            try:
                buy_item = driver.find_element(By.CSS_SELECTOR, '.buyItem')
                buy_text = buy_item.text.lower()
                
                print(f"📄 Buy section text:\n{buy_text[:200]}...")
                
                # Check for "name your price" patterns without minimum
                nyp_phrases = ['name your price', 'nenne deinen preis', 'pay what you want']
                if any(phrase in buy_text for phrase in nyp_phrases) and not any(currency in buy_text for currency in ['£', '$', '€']):
                    price = "nyp"
                    print("✅ Result: nyp (name your price without minimum)")
                else:
                    # Look for minimum price patterns
                    price_patterns = [
                        r'(£\d+(?:\.\d{2})?)\s*gbp',
                        r'(\$\d+(?:\.\d{2})?)\s*usd', 
                        r'(€\d+(?:\.\d{2})?)',
                        r'(\d+(?:\.\d{2})?)\s*(gbp|usd|eur)'
                    ]
                    
                    price = ""
                    for pattern in price_patterns:
                        matches = re.findall(pattern, buy_text, re.IGNORECASE)
                        if matches:
                            if isinstance(matches[0], tuple):
                                price = matches[0][0]  # Extract price part from tuple
                            else:
                                price = matches[0]
                            print(f"✅ Found price pattern '{pattern}': {matches}")
                            break
                    
                    # If no specific price but mentions "oder mehr" or "or more", it's nyp
                    if not price and ('oder mehr' in buy_text or 'or more' in buy_text):
                        price = "nyp"
                        print("✅ Result: nyp (mentions 'oder mehr/or more' without specific price)")
                    elif price:
                        print(f"✅ Result: {price} (minimum price)")
                    else:
                        print("❌ Result: '' (no price found)")
                
                print(f"🎯 Final price: '{price}'")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Close tab
            driver.close()
            if len(driver.window_handles) > 0:
                driver.switch_to.window(driver.window_handles[0])
        
        driver.quit()
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bandcamp_price_extraction()