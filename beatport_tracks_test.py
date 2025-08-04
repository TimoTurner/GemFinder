#!/usr/bin/env python3
"""
Test Beatport tracks page specifically to find the right selectors
"""

from selenium import webdriver
import time

def test_beatport_tracks_page():
    print('Testing Beatport tracks page specifically...')
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Try the tracks search page directly
        driver.get('https://www.beatport.com/search/tracks?q=Daft+Punk+One+More+Time')
        time.sleep(10)  # Wait for dynamic loading
        
        print(f'Page title: {driver.title}')
        print(f'Current URL: {driver.current_url}')
        
        # Save page source
        with open('beatport_tracks_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
        print('Tracks page source saved to beatport_tracks_source.html')
        
        # Try to find track-related elements
        print('\nTesting track selectors:')
        
        # Common track table selectors
        track_selectors = [
            'div[data-testid="tracks-table-row"]',
            'div[data-testid="track-row"]',
            'div[class*="track"]',
            'tr[class*="track"]',
            '.track-row',
            '[data-testid*="track"]'
        ]
        
        for selector in track_selectors:
            try:
                elements = driver.find_elements(webdriver.common.by.By.CSS_SELECTOR, selector)
                print(f'{selector}: {len(elements)} elements')
                if elements and len(elements) > 0:
                    print(f'  First element class: {elements[0].get_attribute("class")}')
            except Exception as e:
                print(f'{selector}: Error - {e}')
    
    finally:
        driver.quit()

if __name__ == '__main__':
    test_beatport_tracks_page()