#!/usr/bin/env python3
"""
Debug why Swag - Pina isn't found on Bandcamp and Traxsource
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def debug_bandcamp_search():
    print("=== Debugging Bandcamp Search ===")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Test exact search like on website
        url = "https://bandcamp.com/search?q=Swag%20Pina"
        print(f"URL: {url}")
        
        driver.get(url)
        time.sleep(10)
        
        print(f"Page title: {driver.title}")
        
        # Look for results with our current selector
        try:
            results = driver.find_elements(By.CSS_SELECTOR, 'li.searchresult')
            print(f"Found {len(results)} results with 'li.searchresult'")
            
            if results:
                for i, result in enumerate(results[:3]):
                    try:
                        title = result.find_element(By.CSS_SELECTOR, '.heading a').text.strip()
                        print(f"  Result {i+1}: {title}")
                    except Exception as e:
                        print(f"  Result {i+1}: Error extracting - {e}")
            else:
                print("  No results found!")
                
                # Try to find ANY results with different selectors
                all_items = driver.find_elements(By.CSS_SELECTOR, 'li')
                print(f"  Found {len(all_items)} <li> elements total")
                
                # Save page source for analysis
                with open('bandcamp_debug.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("  Page source saved to bandcamp_debug.html")
                
        except Exception as e:
            print(f"Bandcamp selector error: {e}")
    
    finally:
        driver.quit()

def debug_traxsource_search():
    print("\n=== Debugging Traxsource Search ===")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Test exact search like on website
        url = "https://www.traxsource.com/search?term=Swag+Pina"
        print(f"URL: {url}")
        
        driver.get(url)
        time.sleep(10)
        
        print(f"Page title: {driver.title}")
        
        # Look for results with our current selector
        try:
            results = driver.find_elements(By.CSS_SELECTOR, 'div.trk-row')
            print(f"Found {len(results)} results with 'div.trk-row'")
            
            if results:
                for i, result in enumerate(results[:3]):
                    try:
                        title = result.find_element(By.CSS_SELECTOR, 'div.title a').text.strip()
                        print(f"  Result {i+1}: {title}")
                    except Exception as e:
                        print(f"  Result {i+1}: Error extracting - {e}")
            else:
                print("  No results found!")
                
                # Check if there's a "no results" message
                try:
                    no_results = driver.find_element(By.XPATH, "//*[contains(text(), 'No results')]")
                    print(f"  Found 'No results' message: {no_results.text}")
                except:
                    print("  No 'No results' message found")
                
                # Save page source for analysis
                with open('traxsource_debug.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("  Page source saved to traxsource_debug.html")
                
        except Exception as e:
            print(f"Traxsource selector error: {e}")
    
    finally:
        driver.quit()

def main():
    print("Debugging Swag - Pina search on Bandcamp and Traxsource...")
    print("This will test the exact URLs and selectors our scrapers use.")
    
    debug_bandcamp_search()
    debug_traxsource_search()
    
    print("\nNext steps:")
    print("1. Check the saved HTML files for actual search results")
    print("2. Verify if the selectors need updating")
    print("3. Check if search URLs need modification")

if __name__ == "__main__":
    main()