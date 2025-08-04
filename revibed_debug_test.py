#!/usr/bin/env python3
"""
Debug Revibed test to find current selectors
"""

from selenium import webdriver
import time

def debug_revibed():
    print("Debug testing Revibed...")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Test with Pink Floyd - should have results
        search_query = "Pink Floyd The Wall"
        url = f"https://revibed.com/marketplace/buy-now-rare-vinyl-records-cds-&-cassette-tapes?query={search_query.replace(' ', '+')}&sort=totalPurchasesCount%2CDESC&size=25&page=0"
        
        print(f'URL: {url}')
        driver.get(url)
        time.sleep(15)  # Wait for dynamic loading
        
        print(f'Page title: {driver.title}')
        print(f'Current URL: {driver.current_url}')
        
        # Save page source
        with open('revibed_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
        print('Page source saved to revibed_page_source.html')
        
    finally:
        driver.quit()

if __name__ == '__main__':
    debug_revibed()