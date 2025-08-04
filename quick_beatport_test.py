#!/usr/bin/env python3
"""
Quick Beatport selector test - save page source for analysis
"""

from selenium import webdriver
import time

def save_beatport_page():
    print('Saving Beatport page source for analysis...')
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get('https://www.beatport.com/search?q=Daft%20Punk%20One%20More%20Time')
        time.sleep(10)  # Wait for dynamic loading
        
        print(f'Page title: {driver.title}')
        print(f'Current URL: {driver.current_url}')
        
        # Save page source
        with open('beatport_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
        print('Page source saved to beatport_page_source.html')
        
        # Try some broad selectors
        print('\nTesting broad selectors:')
        
        # Test article tags (common for track listings)
        articles = driver.find_elements(webdriver.common.by.By.CSS_SELECTOR, 'article')
        print(f'Articles: {len(articles)}')
        
        # Test li elements (list items)
        lis = driver.find_elements(webdriver.common.by.By.CSS_SELECTOR, 'li')
        print(f'List items: {len(lis)}')
        
        # Test divs with data attributes
        data_divs = driver.find_elements(webdriver.common.by.By.CSS_SELECTOR, 'div[data-*]')
        print(f'Divs with data attributes: {len(data_divs)}')
        
        # Look for React-style class names
        react_elements = driver.find_elements(webdriver.common.by.By.CSS_SELECTOR, '[class*="Track"], [class*="Item"], [class*="Row"]')
        print(f'React-style elements: {len(react_elements)}')
        
        if react_elements:
            print('Sample React elements:')
            for i, elem in enumerate(react_elements[:5]):
                classes = elem.get_attribute('class')
                print(f'  {i}: {elem.tag_name} - {classes[:50]}...')
    
    finally:
        driver.quit()

if __name__ == '__main__':
    save_beatport_page()