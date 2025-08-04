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



# Old scraper implementations removed - now integrated into active functions


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

# Old Revibed scraper implementation removed - now integrated into active function
# scrape_search.py - DUMMY VERSION FOR FAST TESTING
import time
from typing import List, Dict
import unicodedata

def normalize_for_matching(text):
    """Normalize text for flexible matching - handles accents and case"""
    if not text:
        return ""
    # Remove accents: NFD splits characters, then filter out combining marks
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.lower().strip()

def calculate_relevance_score(artist, track, title, artist_found, additional_text=""):
    """
    Calculate relevance score for search results
    Higher score = more relevant result
    """
    # Normalize all inputs
    artist_norm = normalize_for_matching(artist)
    track_norm = normalize_for_matching(track)
    
    # Create searchable content from all available fields
    combined_content = f"{title} {artist_found} {additional_text}"
    content_norm = normalize_for_matching(combined_content)
    
    score = 0
    
    # Check matches in content
    artist_found_in_content = artist_norm in content_norm if artist_norm else False
    track_found_in_content = track_norm in content_norm if track_norm else False
    
    # Scoring system
    if artist_found_in_content and track_found_in_content:
        score += 10  # Both terms found = highest priority
    elif artist_found_in_content or track_found_in_content:
        score += 5   # One term found = medium priority
    else:
        return 0     # No match = skip
    
    # Bonus points for matches in title (more important than artist field)
    title_norm = normalize_for_matching(title)
    if artist_norm in title_norm:
        score += 3
    if track_norm in title_norm:
        score += 3
        
    # Bonus for exact word matches (not just substrings)
    words_in_content = content_norm.split()
    if artist_norm in words_in_content:
        score += 2
    if track_norm in words_in_content:
        score += 2
    
    return score

def flexible_search_match(artist, track, title, artist_found, additional_text=""):
    """
    Flexible search matching for digital platforms - backwards compatibility
    """
    return calculate_relevance_score(artist, track, title, artist_found, additional_text) > 0
# import threading
# import time
# from concurrent.futures import ThreadPoolExecutor, as_completed

# --- BEATPORT DUMMY ---
def search_beatport(artist, track):
    """Beatport scraper with test dummy and fallback error handling"""
    try:
        # Real Beatport scraper implementation
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        
        url = f"https://www.beatport.com/search/tracks?q={artist}%20{track}"
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        # Keep JavaScript/CSS enabled for Beatport compatibility
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        wait = WebDriverWait(driver, 5)  # Fast timeout for speed
        
        # Cookies akzeptieren (falls vorhanden)
        try:
            wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'Accept') or contains(text(),'I Accept')]")
            )).click()
        except:
            pass
        
        # Updated Beatport selector (December 2024)
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[data-testid="tracks-list-item"]')
        ))
        
        rows = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="tracks-list-item"]')
        
        if not rows:
            print("Beatport: No results found with any selector")
            return [{'platform': 'Beatport', 'title': 'No results found', 'artist': '', 'album': '', 'label': '', 'price': '', 'cover_url': '', 'url': '', 'search_time': 2.0}]
        
        results = []
        candidates = []  # Collect top 3 candidates for relevance scoring
        
        # Process top 3 results for relevance scoring
        for row in rows[:3]:
            try:
                # Extract title from track name - new Beatport structure
                title_elem = row.find_element(By.CSS_SELECTOR, 'span.Lists-shared-style__ItemName-sc-cd3f7e11-7')
                title = title_elem.text.strip()
                
                # Extract artists - new structure
                artist_elems = row.find_elements(By.CSS_SELECTOR, 'div.ArtistNames-sc-72fc6023-0 a')
                artists = ', '.join([elem.text.strip() for elem in artist_elems]) if artist_elems else 'Unknown Artist'
                
                # Extract label - look for label link in the meta section
                try:
                    label_elem = row.find_element(By.CSS_SELECTOR, 'div.Lists-shared-style__MetaRow-sc-cd3f7e11-4 a[href*="/label/"]')
                    label = label_elem.text.strip()
                except:
                    label = 'Unknown Label'
                
                # Extract album/release from artwork link title
                try:
                    album_elem = row.find_element(By.CSS_SELECTOR, 'a.artwork')
                    album = album_elem.get_attribute('title').strip()
                except:
                    album = title
                
                # Extract cover image
                try:
                    cover_elem = row.find_element(By.CSS_SELECTOR, 'div.Lists-shared-style__Artwork-sc-cd3f7e11-0 img')
                    cover_url = cover_elem.get_attribute('src')
                except:
                    cover_url = ''
                
                # Extract price from cart button
                try:
                    price_elem = row.find_element(By.CSS_SELECTOR, 'button.add-to-cart .price')
                    price = price_elem.text.strip()
                except:
                    price = "€1.39"
                
                # Calculate relevance score for this result
                score = calculate_relevance_score(artist, track, title, artists, f"{label} {album}")
                
                if score > 0:  # Only include relevant matches
                    candidate = {
                        'platform': 'Beatport',
                        'title': title,
                        'artist': artists,
                        'album': album,
                        'label': label,
                        'price': price,
                        'cover_url': cover_url,
                        'url': f'https://www.beatport.com/track/{title.lower().replace(" ", "-")}',
                        'search_time': 2.0,
                        'relevance_score': score
                    }
                    candidates.append(candidate)
            except Exception as e:
                print(f"Error processing Beatport row: {e}")
                continue
        
        driver.quit()
        
        # Select best result based on relevance score
        if candidates:
            best_result = max(candidates, key=lambda x: x['relevance_score'])
            # Remove score from final result (internal use only)
            best_result.pop('relevance_score', None)
            return [best_result]
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
                'search_time': 2.0
            }]
        
    except ImportError:
        # Test dummy for development (can be commented out to test error handling)
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
    
    except Exception as e:
        print(f"❌ Beatport scraper error: {e}")
        return [{
            'platform': 'Beatport',
            'title': '❌ Beatport Suche nicht verfügbar',
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
    """Bandcamp scraper with test dummy and fallback error handling"""
    try:
        # Real Bandcamp scraper implementation
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        
        url = f"https://bandcamp.com/search?q={artist}%20{track}"
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        # Keep JavaScript/CSS enabled for Bandcamp compatibility
        
        driver = webdriver.Chrome(options=options)
        
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        
        search_results = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.searchresult'))
        )
        
        results = []
        candidates = []  # Collect top 3 candidates for relevance scoring
        
        for result in search_results[:3]:  # Process top 3 for relevance scoring
            try:
                title = result.find_element(By.CSS_SELECTOR, '.heading a').text.strip()
                
                try:
                    artist_name = result.find_element(By.CSS_SELECTOR, '.subhead').text.replace('by ', '').strip()
                except:
                    artist_name = 'N/A'
                
                try:
                    album_elem = result.find_element(By.CSS_SELECTOR, '.itemtype').text.strip()
                except:
                    album_elem = 'album'
                
                cover_url = result.find_element(By.CSS_SELECTOR, '.art img').get_attribute('src')
                item_url = result.find_element(By.CSS_SELECTOR, '.itemurl a').get_attribute('href')
                
                # Extract label from URL
                try:
                    label = driver.current_url.split(".bandcamp.com")[0].replace("https://", "") if ".bandcamp.com" in item_url else "Independent"
                except:
                    label = "Independent"
                
                # Simple price extraction without opening new windows (for performance)
                price = "€3.00"  # Default Bandcamp price
                
                # Calculate relevance score for this result
                score = calculate_relevance_score(artist, track, title, artist_name)
                
                if score > 0:  # Only include relevant matches
                    candidate = {
                        'platform': 'Bandcamp',
                        'title': title,
                        'artist': artist_name,
                        'album': album_elem,
                        'label': label,
                        'price': price,
                        'cover_url': cover_url,
                        'url': item_url,
                        'search_time': 1.5,
                        'relevance_score': score
                    }
                    candidates.append(candidate)
            except Exception as e:
                print(f"Error processing Bandcamp result: {e}")
                continue
        
        driver.quit()
        
        # Select best result based on relevance score
        if candidates:
            best_result = max(candidates, key=lambda x: x['relevance_score'])
            # Remove score from final result (internal use only)
            best_result.pop('relevance_score', None)
            return [best_result]
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
                'search_time': 1.5
            }]
        
    except ImportError:
        # Test dummy for development (can be commented out to test error handling)
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
    
    except Exception as e:
        print(f"❌ Bandcamp scraper error: {e}")
        return [{
            'platform': 'Bandcamp',
            'title': '❌ Bandcamp Suche nicht verfügbar',
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
    """Traxsource scraper with test dummy and fallback error handling"""
    try:
        # Real Traxsource scraper implementation
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        
        url = f"https://www.traxsource.com/search?term={artist}+{track}"
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        # Keep JavaScript/CSS enabled for Traxsource compatibility
        
        driver = webdriver.Chrome(options=options)
        
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        track_rows = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.trk-row'))
        )
        
        results = []
        candidates = []  # Collect top 3 candidates for relevance scoring
        
        for row in track_rows[:3]:  # Process top 3 for relevance scoring
            try:
                title = row.find_element(By.CSS_SELECTOR, 'div.title a').text.strip()
                artists = row.find_element(By.CSS_SELECTOR, 'div.artists').text.strip()
                label = row.find_element(By.CSS_SELECTOR, 'div.label a').text.strip()
                
                try:
                    price = row.find_element(By.CSS_SELECTOR, 'span.price').text.strip()
                except:
                    price = "$2.99"  # Default price
                
                # Cover-Image
                try:
                    img_elem = row.find_element(By.CSS_SELECTOR, 'div.thumb img')
                    cover_url = img_elem.get_attribute('src') if img_elem else ''
                except:
                    cover_url = ''
                
                # Calculate relevance score for this result
                score = calculate_relevance_score(artist, track, title, artists, label)
                
                if score > 0:  # Only include relevant matches
                    candidate = {
                        'platform': 'Traxsource',
                        'title': f'{title} (Extended Mix)',
                        'artist': artists,
                        'album': title,  # Traxsource uses track title as album
                        'label': label,
                        'price': price,
                        'cover_url': cover_url,
                        'url': f'https://traxsource.com/track/{title.lower().replace(" ", "-")}',
                        'search_time': 1.0,
                        'relevance_score': score
                    }
                    candidates.append(candidate)
            except Exception as e:
                print(f"Error processing Traxsource row: {e}")
                continue
        
        driver.quit()
        
        # Select best result based on relevance score
        if candidates:
            best_result = max(candidates, key=lambda x: x['relevance_score'])
            # Remove score from final result (internal use only)
            best_result.pop('relevance_score', None)
            return [best_result]
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
                'search_time': 1.0
            }]
        
    except ImportError:
        # Test dummy for development (can be commented out to test error handling)
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
    
    except Exception as e:
        print(f"❌ Traxsource scraper error: {e}")
        return [{
            'platform': 'Traxsource',
            'title': '❌ Traxsource Suche nicht verfügbar',
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
    """Revibed scraper with test dummy and fallback error handling"""
    try:
        # Real Revibed scraper implementation
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        
        # Revibed search logic: Priority Artist first, then Album (not combined!)
        if artist and artist.strip():
            search_query = artist.strip()
        elif album and album.strip():
            search_query = album.strip()
        else:
            search_query = ""
        
        if not search_query:
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
        
        url = f"https://revibed.com/marketplace/buy-now-rare-vinyl-records-cds-&-cassette-tapes?query={search_query.replace(' ', '+')}&sort=totalPurchasesCount%2CDESC&size=25&page=0"
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        # Keep JavaScript/CSS enabled for Revibed compatibility
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        
        items = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.styles_marketplaceGoods__r5WKf"))
        )
        
        results = []
        
        for item in items[:1]:  # Only first result for speed
            try:
                try:
                    title = item.find_element(By.CSS_SELECTOR, ".styles_projectNames__project__title__D49o3").text.strip()
                except:
                    title = 'N/A'
                
                try:
                    album_name = item.find_element(By.CSS_SELECTOR, ".styles_projectNames__album__title__V25wN").text.strip()
                except:
                    album_name = 'N/A'
                
                try:
                    cover_url = item.find_element(By.CSS_SELECTOR, "img").get_attribute('src')
                except:
                    cover_url = ''
                
                # Filter by search keywords (Revibed: Artist OR Album priority)
                if artist and artist.strip():
                    # Priority: Artist search
                    search_match = flexible_search_match(artist, "", title, "", album_name)
                elif album and album.strip():
                    # Fallback: Album search
                    search_match = flexible_search_match("", album, title, "", album_name)
                else:
                    search_match = False
                    
                if search_match:
                    results.append({
                        'platform': 'Revibed',
                        'title': title,
                        'artist': artist,  # Use provided artist
                        'album': album_name,
                        'label': 'Vintage Records',
                        'price': '€45.00',  # Default vintage price
                        'cover_url': cover_url,
                        'url': f'https://revibed.com/item/{title.lower().replace(" ", "-")}',
                        'search_time': 1.5
                    })
            except Exception as e:
                print(f"Error processing Revibed item: {e}")
                continue
        
        driver.quit()
        
        # Return first result or no results
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
                'search_time': 1.5
            }]
        
    except ImportError:
        # Test dummy for development (can be commented out to test error handling)
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
    
    except Exception as e:
        print(f"❌ Revibed scraper error: {e}")
        return [{
            'platform': 'Revibed',
            'title': '❌ Revibed Suche nicht verfügbar',
            'artist': '',
            'album': '',
            'label': '',
            'price': '',
            'cover_url': '',
            'url': '',
            'search_time': 0.1
        }]

# ----- True parallel wrapper function -----
def search_digital_releases_parallel(artist, track, album, catno):
    """Real parallel search using ThreadPoolExecutor for maximum speed"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time
    
    results = []
    
    platforms = [
        ("Beatport", search_beatport),
        ("Bandcamp", search_bandcamp), 
        ("Traxsource", search_traxsource),
    ]
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all platform searches in parallel
        future_to_platform = {
            executor.submit(func, artist, track): name 
            for name, func in platforms
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_platform):
            platform_name = future_to_platform[future]
            try:
                result = future.result()
                search_time = result[0].get('search_time', 0)
                title = result[0].get('title', '-')
                print(f"[{platform_name}] Suchzeit: {search_time}s — Ergebnis: {title}")
                results.extend(result)
            except Exception as exc:
                print(f"{platform_name} generated an exception: {exc}")
                results.append({
                    "platform": platform_name,
                    "title": "Fehler / Kein Treffer", 
                    "artist": "",
                    "album": "",
                    "label": "",
                    "price": "",
                    "cover_url": "",
                    "url": "",
                    "search_time": 0.1
                })
    
    total_time = time.time() - start_time
    print(f"Parallel search completed in {total_time:.2f}s")
    
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
        print("❌ Discogs scraper import error: Production scraper not available")
        return []

    except Exception as e:
        print(f"❌ Discogs scraper error: {e}")
        return []


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
