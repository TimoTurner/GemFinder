#!/usr/bin/env python3
"""
Debug the page structure to find where shipping info is located
"""
from selenium_scraper import create_selenium_driver
from selenium.webdriver.common.by import By
import time

def debug_page_structure():
    driver = None
    try:
        driver = create_selenium_driver(headless=False)  # Show browser for debugging
        
        offer_url = "https://www.discogs.com/sell/item/3755020159"
        print(f"Loading: {offer_url}")
        
        driver.get(offer_url)
        time.sleep(3)  # Wait for page to load
        
        print("=" * 60)
        print("Looking for all elements that might contain shipping info...")
        
        # Find all elements that contain price-related text
        elements_with_euro = driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")
        
        print(f"Found {len(elements_with_euro)} elements containing '€':")
        for i, element in enumerate(elements_with_euro):
            try:
                text = element.text.strip()
                if text and len(text) < 100:  # Only short text
                    tag_name = element.tag_name
                    class_name = element.get_attribute('class') or 'no-class'
                    print(f"{i+1}. <{tag_name} class='{class_name}'> {text}")
            except:
                pass
        
        print("\n" + "=" * 60)
        print("Looking for elements with 'shipping' in class or text...")
        
        # Find elements with shipping in class name
        shipping_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'shipping') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'shipping')]")
        
        print(f"Found {len(shipping_elements)} shipping-related elements:")
        for i, element in enumerate(shipping_elements):
            try:
                text = element.text.strip()
                tag_name = element.tag_name
                class_name = element.get_attribute('class') or 'no-class'
                print(f"{i+1}. <{tag_name} class='{class_name}'> {text[:100]}...")
            except:
                pass
        
        print("\nPress Enter to continue...")
        input()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    debug_page_structure()