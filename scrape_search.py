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
# scrape_search.py
import concurrent.futures
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def _get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

# --- BEATPORT ---
def search_beatport(artist, track):
    t0 = time.time()
    url = f"https://www.beatport.com/search?q={artist}%20{track}"
    driver = _get_driver()
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    results = []
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="tracks-table-row"]')))
        rows = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="tracks-table-row"]')
        for row in rows:
            try:
                title = row.find_element(By.CSS_SELECTOR, 'span.Tables-shared-style__ReleaseName-sc-4e49ff54-4').text.strip()
            except:
                title = ""
            try:
                artist_str = ', '.join([a.text.strip() for a in row.find_elements(By.CSS_SELECTOR, 'div.ArtistNames-sc-72fc6023-0 a')])
            except:
                artist_str = ""
            try:
                label = row.find_element(By.CSS_SELECTOR, 'div.cell.label').text.strip()
            except:
                label = ""
            try:
                album = row.find_element(By.CSS_SELECTOR, 'a.artwork').get_attribute('title').strip()
            except:
                album = ""
            try:
                cover_url = row.find_element(By.CSS_SELECTOR, 'a.artwork img').get_attribute('src').strip()
            except:
                cover_url = ""
            try:
                price = row.find_element(By.CSS_SELECTOR, 'button.add-to-cart .price').text.strip()
            except:
                price = "Release Only"
            try:
                track_url = row.find_element(By.CSS_SELECTOR, "a.artwork").get_attribute("href")
            except:
                track_url = ""
            results.append({
                'platform': 'Beatport',
                'title': title,
                'artist': artist_str,
                'album': album,
                'label': label,
                'price': price,
                'cover_url': cover_url,
                'url': track_url,
                'search_time': round(time.time() - t0, 2)
            })
        driver.quit()
        if results:
            return [results[0]]
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
                'search_time': round(time.time() - t0, 2)
            }]
    except Exception as e:
        print("Beatport error:", e)
        driver.quit()
        return [{
            'platform': 'Beatport',
            'title': 'Kein Treffer',
            'artist': '',
            'album': '',
            'label': '',
            'price': '',
            'cover_url': '',
            'url': '',
            'search_time': round(time.time() - t0, 2)
        }]

# --- BANDCAMP ---
def search_bandcamp(artist, track):
    t0 = time.time()
    url = f"https://bandcamp.com/search?q={artist}%20{track}"
    driver = _get_driver()
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    results = []
    try:
        search_results = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.searchresult'))
        )
        for result in search_results:
            try:
                title = result.find_element(By.CSS_SELECTOR, '.heading a').text.strip()
            except:
                title = ""
            try:
                artist_str = result.find_element(By.CSS_SELECTOR, '.subhead').text.replace('by ', '').strip()
            except:
                artist_str = ""
            try:
                album_elem = result.find_element(By.CSS_SELECTOR, '.itemtype').text.strip()
            except:
                album_elem = ""
            try:
                cover_url = result.find_element(By.CSS_SELECTOR, '.art img').get_attribute('src')
            except:
                cover_url = ""
            try:
                item_url = result.find_element(By.CSS_SELECTOR, '.itemurl a').get_attribute('href')
            except:
                item_url = ""
            price = None
            label = None
            if item_url:
                driver.execute_script("window.open(arguments[0]);", item_url)
                driver.switch_to.window(driver.window_handles[1])
                try:
                    price = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '.base-text-color'))).text.strip()
                except:
                    price = 'name your price'
                label = driver.current_url.split(".bandcamp.com")[0].replace("https://", "")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            results.append({
                'platform': 'Bandcamp',
                'title': title,
                'artist': artist_str,
                'album': album_elem,
                'label': label,
                'price': price,
                'cover_url': cover_url,
                'url': item_url,
                'search_time': round(time.time() - t0, 2)
            })
        driver.quit()
        if results:
            return [results[0]]
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
                'search_time': round(time.time() - t0, 2)
            }]
    except Exception as e:
        print("Bandcamp error:", e)
        driver.quit()
        return [{
            'platform': 'Bandcamp',
            'title': 'Kein Treffer',
            'artist': '',
            'album': '',
            'label': '',
            'price': '',
            'cover_url': '',
            'url': '',
            'search_time': round(time.time() - t0, 2)
        }]

# --- TRAXSOURCE ---
def search_traxsource(artist, track):
    t0 = time.time()
    url = f"https://www.traxsource.com/search?term={artist}+{track}"
    driver = _get_driver()
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    results = []
    try:
        track_rows = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.trk-row'))
        )
        for row in track_rows:
            try:
                title = row.find_element(By.CSS_SELECTOR, 'div.title a').text.strip()
            except:
                title = ""
            try:
                artist_str = row.find_element(By.CSS_SELECTOR, 'div.artists').text.strip()
            except:
                artist_str = ""
            try:
                label = row.find_element(By.CSS_SELECTOR, 'div.label a').text.strip()
            except:
                label = ""
            try:
                price = row.find_element(By.CSS_SELECTOR, 'span.price').text.strip()
            except:
                price = ""
            try:
                img_elem = row.find_element(By.CSS_SELECTOR, 'div.thumb img')
                cover_url = img_elem.get_attribute('src') if img_elem else ''
            except:
                cover_url = ""
            try:
                track_url = row.find_element(By.CSS_SELECTOR, 'div.title a').get_attribute('href')
            except:
                track_url = ""
            results.append({
                'platform': 'Traxsource',
                'title': title,
                'artist': artist_str,
                'album': title,
                'label': label,
                'price': price,
                'cover_url': cover_url,
                'url': track_url,
                'search_time': round(time.time() - t0, 2)
            })
        driver.quit()
        if results:
            return [results[0]]
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
                'search_time': round(time.time() - t0, 2)
            }]
    except Exception as e:
        print("Traxsource error:", e)
        driver.quit()
        return [{
            'platform': 'Traxsource',
            'title': 'Kein Treffer',
            'artist': '',
            'album': '',
            'label': '',
            'price': '',
            'cover_url': '',
            'url': '',
            'search_time': round(time.time() - t0, 2)
        }]

# --- REVIBED ---
def search_revibed(artist, album):
    query_term = ""
    if album:
        query_term = album
    elif artist:
        query_term = artist
    else:
        return [{
            'platform': 'Revibed',
            'title': '',
            'artist': '',
            'album': '',
            'label': '',
            'price': '',
            'cover_url': '',
            'url': '',
            'search_time': 0.0,
            'message': "Für Revibed-Suche muss mindestens Album ODER Artist ausgefüllt sein."
        }]
    t0 = time.time()
    url = f"https://revibed.com/marketplace/buy-now-rare-vinyl-records-cds-&-cassette-tapes?query={query_term.replace(' ', '+')}&sort=totalPurchasesCount%2CDESC&size=25&page=0"
    driver = _get_driver()
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    results = []
    try:
        items = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.styles_marketplaceGoods__r5WKf"))
        )
        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, ".styles_projectNames__project__title__D49o3").text.strip()
            except:
                title = ''
            try:
                album_val = item.find_element(By.CSS_SELECTOR, ".styles_projectNames__album__title__V25wN").text.strip()
            except:
                album_val = ''
            try:
                cover_url = item.find_element(By.CSS_SELECTOR, "img").get_attribute('src')
            except:
                cover_url = ''
            try:
                item_url = item.find_element(By.CSS_SELECTOR, "a").get_attribute('href')
            except:
                item_url = ''
            results.append({
                'platform': 'Revibed',
                'title': title,
                'artist': '',  # Revibed hat selten Artists im Listing!
                'album': album_val,
                'label': '',
                'price': '',
                'cover_url': cover_url,
                'url': item_url,
                'search_time': round(time.time() - t0, 2)
            })
        driver.quit()
        if results:
            return [results[0]]
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
                'search_time': round(time.time() - t0, 2)
            }]
        
    except Exception as e:
        print("Revibed error:", e)
        driver.quit()
        return [{
            'platform': 'Revibed',
            'title': 'Kein Treffer',
            'artist': '',
            'album': '',
            'label': '',
            'price': '',
            'cover_url': '',
            'url': '',
            'search_time': round(time.time() - t0, 2)
        }]

        driver.quit()
        if results:
            return [results[0]]
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
                'search_time': round(time.time() - t0, 2)
            }]
        
    except Exception as e:
        print("Revibed error:", e)
        driver.quit()
        return [{
            'platform': 'Revibed',
            'title': 'Kein Treffer',
            'artist': '',
            'album': '',
            'label': '',
            'price': '',
            'cover_url': '',
            'url': '',
            'search_time': round(time.time() - t0, 2)
        }]

# ----- Zentrale parallele Wrapperfunktion -----
def search_digital_releases_parallel(artist, track, album, catno):
    platforms = [
        ("Beatport", lambda a, t, al, cn: search_beatport(a, t)),
        ("Bandcamp", lambda a, t, al, cn: search_bandcamp(a, t)),
        ("Traxsource", lambda a, t, al, cn: search_traxsource(a, t)),
    ]
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_platform = {
            executor.submit(func, artist, track, album, catno): name for name, func in platforms
        }
        for future in concurrent.futures.as_completed(future_to_platform):
            name = future_to_platform[future]
            try:
                result = future.result(timeout=8)
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
                    "search_time": 0.0
                })
    return results
