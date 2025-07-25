#!/usr/bin/env python3
"""
Test script for aggressive Selenium optimizations with page_load_strategy = 'none'
This is experimental and might be unstable - for testing only!
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

def create_aggressive_selenium_driver(headless: bool = True):
    """EXPERIMENTAL: Create ultra-aggressive Chrome driver with page_load_strategy = 'none'"""
    options = Options()
    
    if headless:
        options.add_argument('--headless=new')
    
    # Performance optimizations
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-ipc-flooding-protection')
    
    # Disable unnecessary features for speed
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')
    options.add_argument('--disable-javascript')
    options.add_argument('--disable-css')
    
    # Anti-detection measures (minimal)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Browser settings
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    options.add_argument('--window-size=1280,720')
    options.add_argument('--lang=en-US')
    
    # EXPERIMENTAL: Ultra-fast page load strategy - RISKY!
    options.page_load_strategy = 'none'  # Don't wait for ANYTHING
    
    driver = webdriver.Chrome(options=options)
    
    # VERY aggressive timeouts
    driver.set_page_load_timeout(1)    # Reduced from 3 to 1 second
    driver.implicitly_wait(0.2)        # Reduced from 0.5 to 0.2 seconds
    
    # Remove automation indicators
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def aggressive_extract_shipping(driver, offer_url: str, max_wait_time: float = 1.5):
    """EXPERIMENTAL: Extract shipping with minimal waiting"""
    try:
        print(f"🚀 AGGRESSIVE: Accessing {offer_url}")
        start_time = time.time()
        
        driver.get(offer_url)
        
        # Since we use page_load_strategy = 'none', we need to wait a bit for content
        # But much less than normal selenium
        time.sleep(0.5)  # Minimal wait for critical content
        
        # Try to find shipping info immediately
        shipping_info = None
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts and not shipping_info:
            try:
                # Look for shipping spans
                reduced_spans = driver.find_elements(By.CSS_SELECTOR, 'span.reduced')
                for span in reduced_spans:
                    span_text = span.text.strip()
                    if span_text and '+' in span_text and ('versand' in span_text.lower() or 'shipping' in span_text.lower()):
                        shipping_info = parse_aggressive_shipping(span_text)
                        if shipping_info != 'Unknown':
                            break
                
                if not shipping_info:
                    # Quick wait and retry
                    time.sleep(0.3)
                    attempts += 1
                else:
                    break
                    
            except Exception as e:
                print(f"🚀 AGGRESSIVE: Attempt {attempts + 1} failed: {e}")
                time.sleep(0.2)
                attempts += 1
        
        total_time = time.time() - start_time
        
        result = {
            'shipping_cost': shipping_info or 'Unknown',
            'extraction_time': total_time,
            'attempts': attempts
        }
        
        print(f"🚀 AGGRESSIVE: Extracted in {total_time:.2f}s after {attempts} attempts: {result['shipping_cost']}")
        return result
        
    except Exception as e:
        total_time = time.time() - start_time
        print(f"🚀 AGGRESSIVE: Error after {total_time:.2f}s: {e}")
        return {
            'shipping_cost': 'Error',
            'extraction_time': total_time,
            'attempts': max_attempts
        }

def parse_aggressive_shipping(shipping_text: str) -> str:
    """Quick shipping parser for aggressive mode"""
    if not shipping_text:
        return 'Unknown'
    
    # Check for free shipping
    if any(indicator in shipping_text.lower() for indicator in ['free', 'kostenlos', 'gratis']):
        return 'Free'
    
    # Quick regex for Euro amounts
    euro_patterns = [
        r'\+\s*€\s*(\d+[,.]?\d*)\s*versand',
        r'\+\s*€\s*(\d+[,.]?\d*)\s*shipping',
        r'\+\s*€\s*(\d+[,.]?\d*)',
    ]
    
    for pattern in euro_patterns:
        match = re.search(pattern, shipping_text, re.IGNORECASE)
        if match:
            try:
                amount = float(match.group(1).replace(',', '.'))
                return f'€{amount:.2f}'
            except ValueError:
                continue
    
    return 'Unknown'

def test_aggressive_vs_normal():
    """Compare aggressive mode vs normal mode"""
    
    # Test URLs (real Discogs offer URLs for testing)
    test_urls = [
        'https://www.discogs.com/sell/item/3755020159',  # Known working URL
        'https://www.discogs.com/sell/item/2970857927',  # Another test URL
        'https://www.discogs.com/sell/item/2493706070',  # Third test URL
    ]
    
    print("=" * 80)
    print("🧪 TESTING AGGRESSIVE SELENIUM OPTIMIZATIONS")
    print("=" * 80)
    
    # Test 1: Normal mode (current implementation)
    print("\n1️⃣ NORMAL MODE (current implementation):")
    normal_driver = None
    normal_results = []
    normal_total_time = 0
    
    try:
        # Import from our existing module
        from selenium_scraper import create_selenium_driver, extract_shipping_with_selenium
        
        normal_driver = create_selenium_driver(headless=True)
        start_time = time.time()
        
        for url in test_urls:
            url_start = time.time()
            try:
                normal_driver.get(url)
                time.sleep(0.5)  # Current implementation wait
                shipping_info = extract_shipping_with_selenium(normal_driver)
                url_time = time.time() - url_start
                
                result = {
                    'url': url,
                    'shipping_cost': shipping_info.get('shipping_cost', 'Unknown'),
                    'time': url_time
                }
                normal_results.append(result)
                print(f"   ✅ {url.split('/')[-1]}: {result['shipping_cost']} ({url_time:.2f}s)")
                
            except Exception as e:
                url_time = time.time() - url_start
                result = {
                    'url': url,
                    'shipping_cost': f'Error: {str(e)[:50]}',
                    'time': url_time
                }
                normal_results.append(result)
                print(f"   ❌ {url.split('/')[-1]}: Error ({url_time:.2f}s)")
        
        normal_total_time = time.time() - start_time
        
    finally:
        if normal_driver:
            normal_driver.quit()
    
    # Test 2: Aggressive mode
    print(f"\n2️⃣ AGGRESSIVE MODE (page_load_strategy = 'none'):")
    aggressive_driver = None
    aggressive_results = []
    aggressive_total_time = 0
    
    try:
        aggressive_driver = create_aggressive_selenium_driver(headless=True)
        start_time = time.time()
        
        for url in test_urls:
            result = aggressive_extract_shipping(aggressive_driver, url)
            result['url'] = url
            aggressive_results.append(result)
            
            status = "✅" if result['shipping_cost'] not in ['Unknown', 'Error'] else "❌"
            print(f"   {status} {url.split('/')[-1]}: {result['shipping_cost']} ({result['extraction_time']:.2f}s)")
        
        aggressive_total_time = time.time() - start_time
        
    finally:
        if aggressive_driver:
            aggressive_driver.quit()
    
    # Results comparison
    print("\n" + "=" * 80)
    print("📊 PERFORMANCE COMPARISON")
    print("=" * 80)
    
    print(f"\n🐌 Normal Mode Total Time:     {normal_total_time:.2f} seconds")
    print(f"🚀 Aggressive Mode Total Time: {aggressive_total_time:.2f} seconds")
    
    if aggressive_total_time > 0:
        speedup = normal_total_time / aggressive_total_time
        print(f"⚡ Speed improvement:          {speedup:.1f}x faster")
    
    print(f"\n📈 Success Rate Comparison:")
    normal_success = sum(1 for r in normal_results if r['shipping_cost'] not in ['Unknown', 'Error'])
    aggressive_success = sum(1 for r in aggressive_results if r['shipping_cost'] not in ['Unknown', 'Error'])
    
    print(f"🐌 Normal Mode:     {normal_success}/{len(normal_results)} successful extractions")
    print(f"🚀 Aggressive Mode: {aggressive_success}/{len(aggressive_results)} successful extractions")
    
    print(f"\n🔍 Detailed Results:")
    for i, (normal, aggressive) in enumerate(zip(normal_results, aggressive_results)):
        url_id = normal['url'].split('/')[-1]
        print(f"   URL {url_id}:")
        print(f"      Normal:     {normal['shipping_cost']} ({normal['time']:.2f}s)")
        print(f"      Aggressive: {aggressive['shipping_cost']} ({aggressive['extraction_time']:.2f}s)")
    
    # Recommendation
    print(f"\n💡 RECOMMENDATION:")
    if aggressive_success >= normal_success and aggressive_total_time < normal_total_time * 0.7:
        print("   ✅ Aggressive mode looks promising! Consider implementing it.")
    elif aggressive_success < normal_success:
        print("   ⚠️  Aggressive mode has lower success rate. Stick with normal mode.")
    else:
        print("   🤔 Mixed results. More testing needed.")

if __name__ == "__main__":
    test_aggressive_vs_normal()