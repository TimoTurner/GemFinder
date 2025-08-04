#!/usr/bin/env python3
"""
Capture Traxsource page for analysis
"""

from selenium import webdriver
import time

def capture_traxsource_page():
    print("Capturing Traxsource page...")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get('https://www.traxsource.com/search?term=David+Guetta+Titanium')
        time.sleep(10)  # Wait for dynamic loading
        
        print(f'Page title: {driver.title}')
        print(f'Current URL: {driver.current_url}')
        
        # Save page source
        with open('traxsource_full_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
        print('Page source saved to traxsource_full_page.html')
        
    finally:
        driver.quit()

if __name__ == '__main__':
    capture_traxsource_page()