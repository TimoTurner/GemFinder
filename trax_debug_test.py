#!/usr/bin/env python3
"""
Debug Traxsource test with detailed error reporting
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback

def debug_traxsource():
    print("Debug testing Traxsource...")
    
    try:
        artist = "house"
        track = "music"
        
        url = f"https://www.traxsource.com/search?term={artist}+{track}"
        print(f"URL: {url}")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        wait = WebDriverWait(driver, 10)
        
        print("Looking for .trk-row elements...")
        
        track_rows = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.trk-row'))
        )
        
        print(f"Found {len(track_rows)} track rows")
        
        if track_rows:
            first_row = track_rows[0]
            print("Analyzing first track row...")
            
            # Try to extract information from first row
            try:
                title = first_row.find_element(By.CSS_SELECTOR, 'div.title a').text.strip()
                print(f"Title: {title}")
            except Exception as e:
                print(f"Title extraction failed: {e}")
                
            try:
                artists = first_row.find_element(By.CSS_SELECTOR, 'div.artists').text.strip()
                print(f"Artists: {artists}")
            except Exception as e:
                print(f"Artists extraction failed: {e}")
                
            print("✅ Traxsource extraction SUCCESS")
            return True
        else:
            print("❌ No track rows found")
            return False
            
    except Exception as e:
        print(f"❌ Traxsource debug error: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    debug_traxsource()