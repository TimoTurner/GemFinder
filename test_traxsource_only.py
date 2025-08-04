#!/usr/bin/env python3
"""
Simple Traxsource scraper test to analyze current structure
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_traxsource_simple():
    print("Testing Traxsource scraper directly...")
    
    try:
        artist = "David Guetta"
        track = "Titanium"
        
        url = f"https://www.traxsource.com/search?term={artist}+{track}"
        print(f"URL: {url}")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        
        print("Waiting for search results...")
        
        # Try different possible selectors
        selectors_to_try = [
            'div.trk-row',
            '.trk-row',
            'div[class*="track"]',
            'div[class*="row"]',
            '.track-item',
            '.result-item'
        ]
        
        results = None
        for selector in selectors_to_try:
            try:
                results = wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, selector)
                ))
                print(f"Found {len(results)} results with selector: {selector}")
                break
            except Exception as e:
                print(f"Selector {selector} failed: {e}")
                continue
        
        if results:
            print("✅ Traxsource scraping SUCCESS")
            
            # Save page source for analysis
            with open('traxsource_page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("Page source saved to traxsource_page_source.html")
            
            return True
        else:
            print("❌ No results found with any selector")
            return False
            
    except Exception as e:
        print(f"❌ Traxsource error: {e}")
        return False
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    test_traxsource_simple()