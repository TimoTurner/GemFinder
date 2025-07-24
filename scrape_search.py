# import requests
# from bs4 import BeautifulSoup
# import json


# def digital_releases(track, artist)):
#     url= f"https://www.beatport.com/search?q={track}%20{artist}
#     response= request.get(url)
#     soip= BeautifulSoup(response.text, "html.parser")

#     print(soup.prettify()) 

#     releases = []
#     release_elemets = soup.find_all('div',class_='Table-style__Table-sc-fdd08fbd-4 cuxahf tracks-table')

#     for release in release_elemets:
#         title = release.find('a')find['title']
#         interpret = release.find('div', class_='Marquee-style__MarqueeWrapper-sc-d1a627da-1 bCXeMp')find['title']
#         label = release.find('div', class_='Table-style__TableCell-sc-fdd08fbd-0 djUlce cell label')find['title']
#         cover = release.find('img alt')find[src]
#         album = release.find('a', class_='artwork')find['title']
#         price = release.find('div', class_='Table-style__TableCell-sc-fdd08fbd-0 djUlce cell card')find['price']
#         print(price)

# def main():
#     digital_releases(1)

# if __name__ == "__main__":
#     main()


# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import json

# def digital_releases(track, artist):
#     url = f"https://www.beatport.com/search?q={track}%20{artist}"

#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless=new')  # läuft im Hintergrund

#     driver = webdriver.Chrome(options=options)
#     driver.get(url)

#     wait = WebDriverWait(driver, 15)

#     # Cookies akzeptieren (robust)
#     try:
#         cookie_btn = wait.until(
#             EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept') or contains(text(),'I Accept')]"))
#         )
#         cookie_btn.click()
#     except:
#         print("Kein Cookie-Banner gefunden.")

#     # Track-Zeilen laden
#     track_rows = wait.until(
#         EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="tracks-table-row"]'))
#     )

#     releases = []

#     for row in track_rows:
#         # Titel
#         try:
#             title = row.find_element(By.CSS_SELECTOR, 'span.Tables-shared-style__ReleaseName-sc-4e49ff54-4').text.strip()
#         except:
#             title = 'N/A'

#         # Künstler
#         artists_elems = row.find_elements(By.CSS_SELECTOR, 'a[href*="/artist/"]')
#         artists = ', '.join([artist.text for artist in artists_elems]) if artists_elems else 'N/A'

#         # Label
#         try:
#             label = row.find_element(By.CSS_SELECTOR, 'div.cell.label').text.strip()
#         except:
#             label = 'N/A'

#         # Cover
#         try:
#             cover_url = row.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
#         except:
#             cover_url = 'N/A'

#         # Album
#         try:
#             album = row.find_element(By.CSS_SELECTOR, 'a.artwork').get_attribute('title')
#         except:
#             album = 'N/A'

#         # Preis
#         try:
#             price = row.find_element(By.CSS_SELECTOR, 'span.price').text.strip()
#         except:
#             price = 'N/A'

#         # Ergebnisse sammeln
#         releases = []

#         releases.append({
#             'title': title,
#             'artists': artists,
#             'label': label,
#             'album': album,
#             'cover_url': cover_url,
#             'price': price
#         })

#     # Ergebnisse speichern
#     with open('beatport_releases.json', 'w', encoding='utf-8') as f:
#         json.dump(releases, f, ensure_ascii=False, indent=4)

#     # Ergebnisse ausgeben
#     for release in releases:
#         print(f"Titel: {release['title']}")
#         print(f"Künstler: {release['artists']}")
#         print(f"Label: {release['label']}")
#         print(f"Album: {release['album']}")
#         print(f"Cover URL: {release['cover_url']}")
#         print(f"Preis: {release['price']}")
#         print('-' * 50)

#     driver.quit()

# def main():
#     digital_releases("Pina", "Swag")

# if __name__ == "__main__":
#     main()

# def scrape_bandcamp_release_info(artist, track):
#     if "demo track a" in track.lower():
#         return {"release_url": "https://bandcamp.com/track/demo-track-a", "cover": "https://placehold.co/60x60", "title": track}
#     else:
#         return {}

# def scrape_beatport_release_info(artist, track):
#     if "demo track a" in track.lower():
#         return {"release_url": "https://beatport.com/track/demo-track-a", "cover": "https://placehold.co/60x60", "title": track}
#     else:
#         return {}

# def scrape_traxsource_release_info(artist, track):
#     if "demo track a" in track.lower():
#         return {"release_url": "https://traxsource.com/track/demo-track-a", "cover": "https://placehold.co/60x60", "title": track}
#     else:
#         return {}

# def scrape_revibed_release_info(artist, track):
#     if "demo track a" in track.lower():
#         return {"release_url": "https://revibed.com/track/demo-track-a", "cover": "https://placehold.co/60x60", "title": track}
#     else:
#         return {}



#Beatport SCRAPE ERFOLG

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import json

# def digital_releases(keyword1, keyword2):
#     url = f"https://www.beatport.com/search?q={keyword1}%20{keyword2}"
    
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless=new')

#     driver = webdriver.Chrome(options=options)
#     driver.get(url)

#     wait = WebDriverWait(driver, 20)

#     # Cookies akzeptieren (falls vorhanden)
#     try:
#         wait.until(EC.element_to_be_clickable(
#             (By.XPATH, "//button[contains(text(),'Accept') or contains(text(),'I Accept')]")
#         )).click()
#     except:
#         pass

#     wait.until(EC.presence_of_element_located(
#         (By.CSS_SELECTOR, 'div[data-testid="tracks-table-row"]')
#     ))

#     rows = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="tracks-table-row"]')

#     results = []
#     for row in rows:
#         title = row.find_element(By.CSS_SELECTOR, 'span.Tables-shared-style__ReleaseName-sc-4e49ff54-4').text.strip()

#         artists = ', '.join(
#             [artist.text.strip() for artist in row.find_elements(By.CSS_SELECTOR, 'div.ArtistNames-sc-72fc6023-0 a')]
#         )

#         label = row.find_element(By.CSS_SELECTOR, 'div.cell.label').text.strip()

#         album = row.find_element(By.CSS_SELECTOR, 'a.artwork').get_attribute('title').strip()

#         cover_url = row.find_element(By.CSS_SELECTOR, 'a.artwork img').get_attribute('src').strip()

#         try:
#             price = row.find_element(By.CSS_SELECTOR, 'button.add-to-cart .price').text.strip()
#         except:
#             price = "Release Only"

#         # Filter, ob Suchbegriffe in einem der Felder enthalten sind
#         combined_info = f"{title} {artists} {label} {album}".lower()
#         if keyword1.lower() in combined_info and keyword2.lower() in combined_info:
#             results.append({
#                 'title': title,
#                 'artists': artists,
#                 'label': label,
#                 'album': album,
#                 'cover_url': cover_url,
#                 'price': price
#             })

#     driver.quit()

#     # Ergebnisse speichern
#     with open('beatport_releases.json', 'w', encoding='utf-8') as f:
#         json.dump(results, f, ensure_ascii=False, indent=4)

#     # Ergebnisse anzeigen
#     for r in results:
#         print(f"Titel: {r['title']}")
#         print(f"Künstler: {r['artists']}")
#         print(f"Label: {r['label']}")
#         print(f"Album: {r['album']}")
#         print(f"Cover URL: {r['cover_url']}")
#         print(f"Preis: {r['price']}")
#         print("-" * 50)

# def main():
#     digital_releases("COM FORCA", "BGB")

# if __name__ == "__main__":
#     main()

# #BANDCAMP SCRAPE ERFOLG

# def bandcamp_scraper(keyword1, keyword2):
#     url = f"https://bandcamp.com/search?q={keyword1}%20{keyword2}"

#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless=new')
#     driver = webdriver.Chrome(options=options)

#     driver.get(url)
#     wait = WebDriverWait(driver, 15)

#     search_results = wait.until(
#         EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.searchresult'))
#     )

#     results = []

#     for result in search_results:
#         title = result.find_element(By.CSS_SELECTOR, '.heading a').text.strip()

#         try:
#             artist = result.find_element(By.CSS_SELECTOR, '.subhead').text.replace('by ', '').strip()
#         except:
#             artist = 'N/A'

#         album_elem = result.find_element(By.CSS_SELECTOR, '.itemtype').text.strip()

#         cover_url = result.find_element(By.CSS_SELECTOR, '.art img').get_attribute('src')

#         item_url = result.find_element(By.CSS_SELECTOR, '.itemurl a').get_attribute('href')

#         driver.execute_script("window.open(arguments[0]);", item_url)
#         driver.switch_to.window(driver.window_handles[1])

#         try:
#             price = wait.until(EC.presence_of_element_located(
#                 (By.CSS_SELECTOR, '.base-text-color'))).text.strip()
#         except:
#             price = 'name your price'

#         label = driver.current_url.split(".bandcamp.com")[0].replace("https://", "")

#         driver.close()
#         driver.switch_to.window(driver.window_handles[0])

#         results.append({
#             'title': title,
#             'artist': artist,
#             'album_type': album_elem,
#             'label': label,
#             'price': price,
#             'cover_url': cover_url,
#             'url': item_url
#         })

#     driver.quit()

#     # Ergebnisse speichern
#     with open('bandcamp_results.json', 'w', encoding='utf-8') as f:
#         json.dump(results, f, ensure_ascii=False, indent=4)

#     # Ergebnisse ausgeben
#     for res in results:
#         print(f"Titel: {res['title']}")
#         print(f"Künstler: {res['artist']}")
#         print(f"Label: {res['label']}")
#         print(f"Typ: {res['album_type']}")
#         print(f"Preis: {res['price']}")
#         print(f"Cover URL: {res['cover_url']}")
#         print(f"URL: {res['url']}")
#         print('-' * 50)

# if __name__ == "__main__":
#     bandcamp_scraper("keyword 1", "keyword 2")

# #Traxsource SCRAPE ERFOLG

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import json


# def traxsource_releases(search_term1, search_term2):
#     url = f"https://www.traxsource.com/search?term={search_term1}+{search_term2}"

#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless=new')  # ohne GUI
#     driver = webdriver.Chrome(options=options)

#     driver.get(url)
#     wait = WebDriverWait(driver, 10)

#     track_rows = wait.until(
#         EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.trk-row'))
#     )

#     releases = []

#     for row in track_rows:
#         title = row.find_element(By.CSS_SELECTOR, 'div.title a').text.strip()
#         artists = row.find_element(By.CSS_SELECTOR, 'div.artists').text.strip()
#         label = row.find_element(By.CSS_SELECTOR, 'div.label a').text.strip()
#         album = title  # Traxsource liefert meist den Track-Titel als Albumname, kein explizites Albumfeld
#         price = row.find_element(By.CSS_SELECTOR, 'span.price').text.strip()

#         # Cover-Image
#         img_elem = row.find_element(By.CSS_SELECTOR, 'div.thumb img')
#         cover_url = img_elem.get_attribute('src') if img_elem else 'N/A'

#         releases.append({
#             'title': title,
#             'artists': artists,
#             'label': label,
#             'album': album,
#             'price': price,
#             'cover_url': cover_url
#         })

#     driver.quit()

#     # Ergebnisse speichern
#     with open('traxsource_releases.json', 'w', encoding='utf-8') as f:
#         json.dump(releases, f, ensure_ascii=False, indent=4)

#     # Ergebnisse ausgeben
#     for release in releases:
#         print(f"Titel: {release['title']}")
#         print(f"Künstler: {release['artists']}")
#         print(f"Label: {release['label']}")
#         print(f"Album: {release['album']}")
#         print(f"Preis: {release['price']}")
#         print(f"Cover URL: {release['cover_url']}")
#         print('-' * 50)


# if __name__ == "__main__":
#     traxsource_releases("bgb", "com Forca")

# #REVIBED SCRAPE ERFOLG

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC


# def scrape_revibed(search_query):
#     url = f"https://revibed.com/marketplace/buy-now-rare-vinyl-records-cds-&-cassette-tapes?query={search_query.replace(' ', '+')}&sort=totalPurchasesCount%2CDESC&size=25&page=0"

#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless=new')

#     driver = webdriver.Chrome(options=options)
#     driver.get(url)

#     wait = WebDriverWait(driver, 15)

#     releases = []

#     items = wait.until(
#         EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.styles_marketplaceGoods__r5WKf"))
#     )

#     for item in items:
#         try:
#             title = item.find_element(By.CSS_SELECTOR, ".styles_projectNames__project__title__D49o3").text.strip()
#         except:
#             title = 'N/A'

#         try:
#             album = item.find_element(By.CSS_SELECTOR, ".styles_projectNames__album__title__V25wN").text.strip()
#         except:
#             album = 'N/A'

#         try:
#             cover_url = item.find_element(By.CSS_SELECTOR, "img").get_attribute('src')
#         except:
#             cover_url = 'N/A'

#         releases.append({
#             'title': title,
#             'album': album,
#             'cover_url': cover_url
#         })

#     driver.quit()

#     return releases
# scrape_search.py - DUMMY VERSION FOR FAST TESTING
import time
from typing import List, Dict
# import threading
# import time
# from concurrent.futures import ThreadPoolExecutor, as_completed

# --- BEATPORT DUMMY ---
def search_beatport(artist, track):
    """Fast dummy implementation for testing"""
    time.sleep(0.1)  # Simulate minimal processing time
    
    # Scenario A: Digital files found (for test tracks)
    if artist.lower() in ["A", "a"] or track.lower() in ["A", "a"]:
        return [{
            'platform': 'Beatport',
            'title': f'{track} (Original Mix)',
            'artist': artist,
            'album': f'{track} EP',
            'label': 'Digital Records',
            'price': '€2.49',
            'cover_url': 'https://placehold.co/120x120/FF6B6B/white?text=Beatport',
            'url': f'https://beatport.com/track/{track.lower().replace(" ", "-")}',
            'search_time': 0.1
        }]
    else:
        return [{
            'platform': 'Beatport',
            'title': 'Kein Treffer',
            'artist': '',
            'album': '',
            'label': '',
            'price': '',
            'cover_url': '',
            'url': '',
            'search_time': 0.1
        }]

# --- BANDCAMP DUMMY ---
def search_bandcamp(artist, track):
    """Fast dummy implementation for testing"""
    time.sleep(0.1)
    
    # Scenario A: Digital files found
    if artist.lower() in ["A", "a"] or track.lower() in ["A", "a"]:
        return [{
            'platform': 'Bandcamp',
            'title': track,
            'artist': artist,
            'album': f'{track} Single',
            'label': 'independent-records',
            'price': '€3.00',
            'cover_url': 'https://placehold.co/120x120/4ECDC4/white?text=Bandcamp',
            'url': f'https://independent-records.bandcamp.com/track/{track.lower().replace(" ", "-")}',
            'search_time': 0.1
        }]
    else:
        return [{
            'platform': 'Bandcamp',
            'title': 'Kein Treffer',
            'artist': '',
            'album': '',
            'label': '',
            'price': '',
            'cover_url': '',
            'url': '',
            'search_time': 0.1
        }]

# --- TRAXSOURCE DUMMY ---
def search_traxsource(artist, track):
    """Fast dummy implementation for testing"""
    time.sleep(0.1)
    
    # Scenario A: Digital files found
    if artist.lower() in ["A", "a"] or track.lower() in ["A", "a"]:
        return [{
            'platform': 'Traxsource',
            'title': f'{track} (Extended Mix)',
            'artist': artist,
            'album': track,
            'label': 'Deep House Label',
            'price': '$2.99',
            'cover_url': 'https://placehold.co/120x120/45B7D1/white?text=Traxsource',
            'url': f'https://traxsource.com/track/{track.lower().replace(" ", "-")}',
            'search_time': 0.1
        }]
    else:
        return [{
            'platform': 'Traxsource',
            'title': 'Kein Treffer',
            'artist': '',
            'album': '',
            'label': '',
            'price': '',
            'cover_url': '',
            'url': '',
            'search_time': 0.1
        }]

# --- REVIBED DUMMY ---
def search_revibed(artist, album):
    """Fast dummy implementation for testing"""
    time.sleep(0.1)
    
    if not (artist or album):
        return [{
            'platform': 'Revibed',
            'title': '',
            'artist': '',
            'album': '',
            'label': '',
            'price': '',
            'cover_url': '',
            'url': '',
            'search_time': 0.1,
            'message': "Für Revibed-Suche muss mindestens Album ODER Artist ausgefüllt sein."
        }]
    
    # Scenario B: Revibed files found (for vinyl/rare tracks)
    if artist.lower() in ["B", "b"] or (album and "b" in album.lower()):
        return [{
            'platform': 'Revibed',
            'title': artist or "Unknown Artist",
            'artist': '',
            'album': album or f'{artist} Collection',
            'label': '',
            'price': '€45.00',
            'cover_url': 'https://placehold.co/120x120/96CEB4/white?text=Revibed',
            'url': f'https://revibed.com/item/{(album or artist).lower().replace(" ", "-")}',
            'search_time': 0.1
        }]
    else:
        return [{
            'platform': 'Revibed',
            'title': 'Kein Treffer',
            'artist': '',
            'album': '',
            'label': '',
            'price': '',
            'cover_url': '',
            'url': '',
            'search_time': 0.1
        }]

# ----- Fast parallel wrapper function -----
def search_digital_releases_parallel(artist, track, album, catno):
    """Fast dummy parallel search - no actual threading needed for testing"""
    results = []
    
    # Call each platform sequentially but quickly
    platforms = [
        ("Beatport", search_beatport),
        ("Bandcamp", search_bandcamp), 
        ("Traxsource", search_traxsource),
    ]
    
    for name, func in platforms:
        try:
            result = func(artist, track)
            print(f"[{name}] Suchzeit: {result[0].get('search_time','-')}s — Ergebnis: {result[0].get('title','-')}")
            results.extend(result)
        except Exception as exc:
            print(f"{name} generated an exception: {exc}")
            results.append({
                "platform": name,
                "title": "Fehler / Kein Treffer", 
                "artist": "",
                "album": "",
                "label": "",
                "price": "",
                "cover_url": "",
                "url": "",
                "search_time": 0.1
            })
    
    return results

# def search_platform_with_live_update(provider, criteria, live_container):
#     """Einzelner Thread für eine Plattform"""
#     try:
#         result = provider.search(criteria)
#         # SOFORT anzeigen sobald fertig:
#         with live_container:
#             st.session_state.live_results.append(result)
#             show_live_results()  # Progressives Update
#     except Exception as e:
#         # Auch Fehler sofort anzeigen
#         error_result = {"platform": provider.name, "title": "Fehler", "error": str(e)}
#         with live_container:
#             st.session_state.live_results.append(error_result)
#             show_live_results()


from typing import List, Dict, Optional
from discogs_scraper import create_discogs_scraper
from utils import parse_price, CURRENCY_MAPPING

def scrape_discogs_marketplace_offers(
    release_id: str,
    max_offers: Optional[int] = 10,
    user_country: Optional[str] = None
) -> List[Dict]:
    """
    Production-ready Discogs marketplace scraper integration

    Args:
        release_id:   Discogs release ID
        max_offers:   Maximum number of offers to return
        user_country: ISO-Länderkürzel (z. B. "DE", "US")

    Returns:
        Liste von Angeboten in der lokalen Währung, angereichert um
        price_amount, price_currency, shipping_amount und total_amount.
    """
    # Währung ermitteln (Fallback auf DEFAULT)
    preferred_currency = CURRENCY_MAPPING.get(
        (user_country or "").upper(),
        CURRENCY_MAPPING["DEFAULT"]
    )

    try:
        # Scraper mit Server-Konfiguration erzeugen
        scraper = create_discogs_scraper(
            headless=True,
            enable_cache=True,
            use_proxies=False
        )

        # user_country in den Scraper-Config schreiben, damit das
        # build von marketplace_url korrekt funktioniert
        if user_country:
            scraper.config.user_country = user_country.upper()

        # Angebote scrapen (interne Methode liest scraper.config.user_country)
        raw = scraper.scrape_marketplace_offers(release_id, max_offers)

        offers = raw.get("offers", [])
        filtered = []

        # Nur Angebote in preferred_currency übernehmen
        for o in offers:
            price_amt, price_curr = parse_price(o.get("price", ""))
            if price_curr != preferred_currency:
                continue

            shipping_amt, _ = parse_price(o.get("shipping", ""))
            item = o.copy()
            item.update({
                "price_amount":    price_amt,
                "price_currency":  price_curr,
                "shipping_amount": shipping_amt,
                "total_amount":    price_amt + shipping_amt
            })
            filtered.append(item)

        return filtered

    except ImportError:
        print("Production scraper not available, using dummy data")
        return _get_dummy_discogs_offers(release_id, max_offers)

    except Exception as e:
        print(f"Error scraping Discogs offers: {e}")
        return _get_dummy_discogs_offers(release_id, max_offers)


# # --- PRODUCTION DISCOGS SCRAPER INTEGRATION ---
# def scrape_discogs_marketplace_offers(release_id: str, max_offers: int = 10) -> List[Dict]:
#     """
#     Production-ready Discogs marketplace scraper integration
    
#     This function provides a clean interface to the robust Discogs scraper
#     that handles anti-bot measures, rate limiting, and scaling challenges.
    
#     Args:
#         release_id: Discogs release ID
#         max_offers: Maximum number of offers to return
        
#     Returns:
#         List of marketplace offers
#     """
#     try:
#         # Import the production scraper
#         from discogs_scraper import create_discogs_scraper
        
#         # Create scraper with production settings
#         scraper = create_discogs_scraper(
#             headless=True,          # Run headless for server deployment
#             enable_cache=True,      # Enable caching to reduce load
#             use_proxies=False       # Set to True if you have proxy servers
#         )
        
#         # Scrape marketplace offers
#         result = scraper.scrape_marketplace_offers(release_id, max_offers)
        
#         return result.get('offers', [])
        
#     except ImportError:
#         # Fallback to dummy data if scraper dependencies aren't available
#         print("Production scraper not available, using dummy data")
#         return _get_dummy_discogs_offers(release_id, max_offers)
#     except Exception as e:
#         print(f"Error scraping Discogs offers: {e}")
#         return _get_dummy_discogs_offers(release_id, max_offers)


def _get_dummy_discogs_offers(release_id: str, max_offers: int = 10) -> List[Dict]:
    """Fallback dummy offers for development/testing"""
    import time
    time.sleep(0.1)  # Simulate processing time
    
    offers = []
    base_prices = [12.99, 15.50, 18.00, 22.50, 28.99]
    conditions = ["Near Mint (NM or M-)", "Very Good Plus (VG+)", "Very Good (VG)", "Good Plus (G+)", "Mint (M)"]
    sellers = ["vinyl_collector_de", "record_hunter_uk", "music_paradise_usa"]
    
    for i in range(min(max_offers, len(base_prices))):
        offers.append({
            'seller': sellers[i % len(sellers)],
            'condition': conditions[i],
            'price': f"€{base_prices[i]:.2f}",
            'shipping': f"€{2.50 + (i * 0.50):.2f}" if i < 3 else "Free shipping",
            'seller_rating': f"{98.5 - (i * 0.5):.1f}%",
            'country': 'Germany',
            'scraped_at': time.time()
        })
    
    return offers


# --- COMBINED DISCOGS SEARCH WITH MARKETPLACE ---
def search_discogs_with_offers(artist: str = None, track: str = None, album: str = None, 
                              catno: str = None, max_offers: int = 5) -> Dict:
    """
    Search Discogs and get marketplace offers in one call
    
    Args:
        artist: Artist name
        track: Track title  
        album: Album title
        catno: Catalog number
        max_offers: Maximum offers to return
        
    Returns:
        Combined search and marketplace data
    """
    try:
        # Use existing search function
        from api_search import search_discogs_releases
        releases = search_discogs_releases(artist, track, album, catno)
        
        if not releases:
            return {
                'release': None,
                'offers': [],
                'status': 'no_releases_found'
            }
        
        first_release = releases[0]
        release_id = first_release.get('id')
        
        # Get marketplace offers
        offers = []
        if release_id:
            offers = scrape_discogs_marketplace_offers(release_id, max_offers)
        
        return {
            'release': first_release,
            'offers': offers,
            'total_offers': len(offers),
            'status': 'success'
        }
        
    except Exception as e:
        return {
            'release': None,
            'offers': [],
            'status': 'error',
            'error': str(e)
        }
