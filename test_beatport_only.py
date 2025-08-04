#!/usr/bin/env python3
"""
Simple Beatport scraper test
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_beatport_simple():
    print("Testing Beatport scraper directly...")
    
    try:
        artist = "Daft Punk"
        track = "One More Time"
        
        url = f"https://www.beatport.com/search/tracks?q={artist}%20{track}"
        print(f"URL: {url}")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        wait = WebDriverWait(driver, 10)
        
        print("Waiting for track list items...")
        
        # Wait for track results
        tracks = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div[data-testid="tracks-list-item"]')
        ))
        
        print(f"Found {len(tracks)} tracks")
        
        if tracks:
            first_track = tracks[0]
            
            # Try to extract information
            try:
                title_elem = first_track.find_element(By.CSS_SELECTOR, 'span.Lists-shared-style__ItemName-sc-cd3f7e11-7')
                title = title_elem.text.strip()
                print(f"Title: {title}")
            except Exception as e:
                print(f"Title extraction error: {e}")
            
            try:
                artist_elems = first_track.find_elements(By.CSS_SELECTOR, 'div.ArtistNames-sc-72fc6023-0 a')
                artists = ', '.join([elem.text.strip() for elem in artist_elems]) if artist_elems else 'Unknown Artist'
                print(f"Artists: {artists}")
            except Exception as e:
                print(f"Artist extraction error: {e}")
                
            try:
                price_elem = first_track.find_element(By.CSS_SELECTOR, 'button.add-to-cart .price')
                price = price_elem.text.strip()
                print(f"Price: {price}")
            except Exception as e:
                print(f"Price extraction error: {e}")
                
            print("✅ Beatport scraping SUCCESS")
            return True
        else:
            print("❌ No tracks found")
            return False
            
    except Exception as e:
        print(f"❌ Beatport error: {e}")
        return False
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    test_beatport_simple()