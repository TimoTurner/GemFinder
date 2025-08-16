# import requests
# from bs4 import BeautifulSoup
# import json
from error_types import ErrorType, create_error, log_error


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

def beatport_strict_filter(search_artist, search_track, search_album, result_title, result_artist, result_album):
    """
    Word-based filtering for Beatport - at least one word from EACH search term must be found
    Prevents false matches like "PICASSO Extended Mix" for "Drum Starts - Picasso"
    """
    # Split search terms into words
    artist_words = search_artist.lower().split() if search_artist else []
    track_words = search_track.lower().split() if search_track else []
    album_words = search_album.lower().split() if search_album else []
    
    # Combined result content (normalized)
    result_content = f"{result_title} {result_artist} {result_album}".lower()
    
    # Check if at least one word from each search term is found
    artist_found = any(word in result_content for word in artist_words) if artist_words else True
    track_found = any(word in result_content for word in track_words) if track_words else True
    album_found = any(word in result_content for word in album_words) if album_words else True
    
    # Logic based on what search terms we have - BOTH terms must have matches
    if search_artist and search_track:
        return artist_found and track_found
    elif search_artist and search_album:
        return artist_found and album_found
    elif search_track and search_album:
        return track_found and album_found
    elif search_artist:
        return artist_found
    elif search_track:
        return track_found
    elif search_album:
        return album_found
    else:
        return False

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
def search_beatport(artist, track, album=""):
    """Beatport scraper with comprehensive error handling"""
    import time
    platform = "Beatport"
    start_time = time.time()
    
    try:
        # Input validation
        if not artist and not track and not album:
            error = create_error(
                ErrorType.VALIDATION_ERROR,
                platform,
                "No search parameters provided",
                artist=artist,
                track=track,
                album=album
            )
            log_error(error)
            return _beatport_error_result("❌ No search terms provided")
        
        # Dependency check
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import time
        except ImportError as e:
            error = create_error(
                ErrorType.DEPENDENCY_ERROR,
                platform,
                "Selenium dependencies not available",
                package="selenium",
                original_error=str(e)
            )
            log_error(error)
            return _beatport_error_result("🔧 Browser automation not available")
        
        # Build search query based on available parameters
        search_terms = []
        if artist:
            search_terms.append(artist)
        if track:
            search_terms.append(track)
        if album:
            search_terms.append(album)
        
        search_query = "%20".join(search_terms)
# Performance timing only
        start_time = time.time()
        
        url = f"https://www.beatport.com/search/tracks?q={search_query}"
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # SMART SPEED OPTIMIZATIONS for <4s target
        options.add_argument('--disable-images')                    
        # Re-enable JavaScript - Beatport might need it for dynamic content
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI,VizDisplayCompositor')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-web-security')
        options.add_argument('--window-size=800,600')               # Even smaller
        options.add_argument('--page-load-strategy=eager')          # Less aggressive than 'none'
        
        # Network optimizations - block everything possible
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.plugins": 2,
            "profile.default_content_setting_values.popups": 2,
            "profile.default_content_setting_values.geolocation": 2,
            "profile.default_content_setting_values.media_stream": 2,
        })
        
        try:
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            error = create_error(
                ErrorType.BROWSER_ERROR,
                platform,
                "Failed to initialize Chrome WebDriver",
                original_error=str(e)
            )
            log_error(error)
            return [_beatport_error_result("🌐 Browser initialization failed")]
        
        try:
            # ULTIMATE SPEED PUSH for <4s target 
            driver.implicitly_wait(0.6)                  # 0.8s → 0.6s 
            driver.set_page_load_timeout(2.2)            # 2.5s → 2.2s
            wait = WebDriverWait(driver, 1.2)            # 1.5s → 1.2s
            
            driver.get(url)
            
        except Exception as e:
            try:
                driver.quit()
            except:
                pass
            
            # Smart timeout handling - distinguish between real failures and slow loading
            error_message = str(e).lower()
            if "timeout" in error_message:
                # Try one quick retry with slightly longer timeout for slow connections
                print(f"⚡ Beatport: Quick retry with extended timeout...")
                try:
                    driver.set_page_load_timeout(4.0)  # One-time extension
                    driver.get(url)
                    print(f"✅ Beatport: Retry successful!")
                    # Continue with normal flow - don't return error
                except Exception as retry_error:
                    # Real timeout issue
                    error = create_error(
                        ErrorType.SCRIPT_TIMEOUT,
                        platform,
                        f"Page load timeout for Beatport after retry: {url}",
                        timeout_duration=4.0,
                        retry_attempted=True,
                        url=url,
                        original_error=str(retry_error)
                    )
                    log_error(error)
                    return [_beatport_error_result("🔴 Beatport not reachable")]
            elif "network" in error_message or "dns" in error_message:
                error = create_error(
                    ErrorType.SITE_DOWN,
                    platform,
                    "Cannot reach Beatport website",
                    url=url,
                    original_error=str(e)
                )
            else:
                error = create_error(
                    ErrorType.BROWSER_ERROR,
                    platform,
                    f"Browser error accessing Beatport: {str(e)}",
                    url=url,
                    original_error=str(e)
                )
            
            log_error(error)
            return [_beatport_error_result("🔴 Beatport not reachable")]
        
        # SKIP cookie banner - waste of time for scraping
        # Cookie acceptance not needed for search results
        
        # Element detection with structured error handling
        rows = []
        try:
            print(f"🔍 Beatport: Waiting for tracks with 1.2s timeout...")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="tracks-list-item"]')))
            rows = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="tracks-list-item"]')
            print(f"✅ Beatport: Found {len(rows)} tracks with primary selector")
            
        except Exception as e:
            print(f"❌ Beatport: Primary selector timed out: {str(e)}")
            
            # Check if page loaded properly
            try:
                page_source = driver.page_source
                page_title = driver.title
                print(f"📄 Beatport: Page source length: {len(page_source)} chars")
                print(f"🔍 Beatport: Page title: '{page_title}'")
                
                # Determine if this is a site issue or structure change
                if len(page_source) < 1000:
                    error = create_error(
                        ErrorType.SITE_DOWN,
                        platform,
                        "Beatport page failed to load properly",
                        page_size=len(page_source),
                        page_title=page_title
                    )
                    log_error(error)
                    try:
                        driver.quit()
                    except:
                        pass
                    return [_beatport_error_result("🔴 Beatport not responding")]
                
                # Try fallback selector
                try:
                    rows = driver.find_elements(By.CSS_SELECTOR, 'div[class*="track"]')
                    print(f"🔄 Beatport: Fallback found {len(rows)} elements")
                    if not rows:
                        # Structure may have changed
                        error = create_error(
                            ErrorType.STRUCTURE_CHANGED,
                            platform,
                            "Beatport track selectors not found - site structure may have changed",
                            primary_selector='div[data-testid="tracks-list-item"]',
                            fallback_selector='div[class*="track"]',
                            page_title=page_title
                        )
                        log_error(error)
                except Exception as e2:
                    error = create_error(
                        ErrorType.SELECTOR_NOT_FOUND,
                        platform,
                        "All Beatport selectors failed",
                        primary_error=str(e),
                        fallback_error=str(e2)
                    )
                    log_error(error)
                    rows = []
                    
            except Exception as page_error:
                error = create_error(
                    ErrorType.BROWSER_ERROR,
                    platform,
                    f"Cannot access Beatport page content: {str(page_error)}",
                    original_error=str(page_error)
                )
                log_error(error)
                try:
                    driver.quit()
                except:
                    pass
                return [_beatport_error_result("🌐 Browser error")]
        
        if not rows:
            print(f"⚠️ Beatport: No rows found, analyzing page...")
            # SMART no-results detection - check specific indicators
            page_source = driver.page_source.lower()
            
            # More specific checks for actual "no results" vs false positives
            no_results_indicators = [
                "no tracks found",
                "0 results for", 
                "sorry, no results",
                "keine suchergebnisse"
            ]
            
            found_indicators = [indicator for indicator in no_results_indicators if indicator in page_source]
            print(f"🔍 Beatport: Found no-results indicators: {found_indicators}")
            
            is_no_results = any(indicator in page_source for indicator in no_results_indicators)
            
            # If page loaded but really no results (not just missing selector)
            if is_no_results and len(page_source) > 1000:
                print(f"📭 Beatport: Confirmed no results - legitimate 'no results' page")
                driver.quit()
                elapsed_time = time.time() - start_time
                print(f"⏱️ Beatport: Kein Treffer ({elapsed_time:.2f}s)")
                return [{
                    'platform': 'Beatport',
                    'title': 'Kein Treffer',
                    'artist': '',
                    'album': '',
                    'label': '',
                    'price': '',
                    'cover_url': '',
                    'url': '',
                    'search_time': elapsed_time
                }]
            
            # If not clearly "no results", it might be selector issue - return error
            print(f"🔧 Beatport: Not clearly 'no results' - might be selector/timing issue")
            driver.quit()
            elapsed_time = time.time() - start_time
            print(f"⏱️ Beatport: ❌ Selector issue - page loaded but tracks not found ({elapsed_time:.2f}s)")
            return [{
                'platform': 'Beatport',
                'title': '❌ Beatport Selector Update nötig',
                'artist': '',
                'album': '',
                'label': '',
                'price': '',
                'cover_url': '',
                'url': '',
                'search_time': elapsed_time
            }]
        
        if not rows:
            print("Beatport: No results found with any selector")
            return [{'platform': 'Beatport', 'title': 'No results found', 'artist': '', 'album': '', 'label': '', 'price': '', 'cover_url': '', 'url': '', 'search_time': 2.0}]
        
        candidates = []  # Collect candidates for relevance scoring
        
        print(f"🎵 Beatport: Processing {len(rows[:1])} track(s)...")
        
        # SPEED OPTIMIZATION: Process 1 result for <4s target
        # Beatport sorts well by relevance, first result usually best
        for row in rows[:1]:
            try:
                print(f"🎯 Beatport: Extracting title...")
                # Extract title from track name - new Beatport structure
                title_elem = row.find_element(By.CSS_SELECTOR, 'span.Lists-shared-style__ItemName-sc-cd3f7e11-7')
                title = title_elem.text.strip()
                print(f"✅ Beatport: Found title: '{title}'")
                
                # Extract artists - FIXED selector
                print(f"🎯 Beatport: Extracting artists...")
                artist_elems = row.find_elements(By.CSS_SELECTOR, 'a[href*="/artist/"]')
                artists = ', '.join([elem.text.strip() for elem in artist_elems]) if artist_elems else 'Unknown Artist'
                print(f"✅ Beatport: Found artists: '{artists}'")
                
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
                    price = ""  # No fallback price - leave empty if not found
                
                # FAST URL extraction - single optimized selector
                track_url = ""
                try:
                    # Use most reliable selector first
                    link_elem = row.find_element(By.CSS_SELECTOR, 'a[href*="/track/"]')
                    track_url = link_elem.get_attribute('href')
                except:
                    # Fast fallback - search within row for any track link
                    try:
                        all_links = row.find_elements(By.TAG_NAME, 'a')
                        for link in all_links[:2]:  # Check max 2 links for speed
                            href = link.get_attribute('href')
                            if href and '/track/' in href:
                                track_url = href
                                break
                    except:
                        track_url = f'https://www.beatport.com/search/tracks?q={artist}%20{track}'
                
                # Use Beatport-specific filtering (less strict than before)
                print(f"🎯 Beatport: Checking relevance filter...")
                print(f"    Search: artist='{artist}', track='{track}'")
                print(f"    Found: title='{title}', artists='{artists}'")
                is_relevant = beatport_strict_filter(artist, track, album, title, artists, album)
                print(f"✅ Beatport: Filter result: {is_relevant}")
                
                if is_relevant:  # Only include matches that pass Beatport filter
                    print(f"✅ Beatport: Track passed filter, adding to candidates")
                    candidate = {
                        'platform': 'Beatport',
                        'title': title,
                        'artist': artists,
                        'album': album,
                        'label': label,
                        'price': price,
                        'cover_url': cover_url,
                        'url': track_url,  # Use extracted real URL
                        'search_time': 2.0,
                        'relevance_score': 8  # Fixed score for valid matches
                    }
                    candidates.append(candidate)
                else:
                    print(f"❌ Beatport: Track failed filter, skipping")
            except Exception as e:
                print(f"❌ Beatport: Error processing result: {e}")
                continue
        
        driver.quit()
        elapsed_time = time.time() - start_time
        
        # Select best result based on relevance score
        if candidates:
            best_result = max(candidates, key=lambda x: x['relevance_score'])
            # Remove score from final result (internal use only)
            best_result.pop('relevance_score', None)
            best_result['search_time'] = elapsed_time
            print(f"⏱️ Beatport: {best_result['title']} ({elapsed_time:.2f}s)")
            return [best_result]
        else:
            print(f"❌ Beatport: No candidates passed filter")
            print(f"⏱️ Beatport: Kein Treffer ({elapsed_time:.2f}s)")
            return [{
                'platform': 'Beatport',
                'title': 'Kein Treffer',
                'artist': '',
                'album': '',
                'label': '',
                'price': '',
                'cover_url': '',
                'url': '',
                'search_time': elapsed_time
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
    
    except ImportError:
        # Test dummy for development when Selenium not available
        time.sleep(0.1)
        if artist.lower() in ["A", "a"] or track.lower() in ["A", "a"]:
            return [{
                'platform': 'Beatport',
                'title': f'TEST: {track}',
                'artist': f'TEST: {artist}',
                'album': f'TEST: {album}',
                'label': 'Test Label',
                'price': '$1.99',
                'cover_url': 'https://via.placeholder.com/150x150/0066FF/FFFFFF?text=TEST',
                'url': f'https://www.beatport.com/track/test/{track.lower()}',
                'search_time': 0.1
            }]
        return [_beatport_error_result("📭 Kein Treffer")]
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        error = create_error(
            ErrorType.UNKNOWN_ERROR,
            platform,
            f"Unexpected error in Beatport scraper: {str(e)}",
            elapsed_time=elapsed_time,
            original_error=str(e)
        )
        log_error(error)
        return [_beatport_error_result("❌ Beatport Suche nicht verfügbar")]

def _beatport_error_result(message: str) -> dict:
    """Helper function to create consistent Beatport error results"""
    return {
        'platform': 'Beatport',
        'title': message,
        'artist': '',
        'album': '',
        'label': '',
        'price': '',
        'cover_url': '',
        'url': '',
        'search_time': 0.0
    }

# --- BANDCAMP DUMMY ---
def extract_bandcamp_price(driver, item_url):
    """Extract price from individual Bandcamp track page with Track vs Album distinction"""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import re
    try:
        # Save current window handle
        main_window = driver.current_window_handle
        
        # Open new tab for price checking (optimized)
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        
        # ULTRA-FAST timeout for track page
        driver.set_page_load_timeout(2)         # 3s → 2s (-33%)
        driver.get(item_url)
        
        # AGGRESSIVE wait for buy section
        wait = WebDriverWait(driver, 2)         # 3s → 2s (-33%)
        
        try:
            # Wait for buy section to load
            buy_item = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.buyItem')))
            buy_text = buy_item.text.lower()
            
            # Check what type of purchase is available
            is_track_available = False
            is_album_only = False
            
            # Detect track vs album availability
            if 'buy digital track' in buy_text or 'digital track' in buy_text:
                is_track_available = True
            elif 'buy digital album' in buy_text or 'digital album' in buy_text:
                is_album_only = True
            
            # Check for "name your price" patterns
            nyp_phrases = ['name your price', 'nenne deinen preis', 'pay what you want']
            has_nyp = any(phrase in buy_text for phrase in nyp_phrases)
            
            if has_nyp and not any(currency in buy_text for currency in ['£', '$', '€']):
                price = "nyp (Track)" if is_track_available else "nyp (Album only)"
            else:
                # Look for price patterns
                price_patterns = [
                    r'(£\d+(?:\.\d{2})?)',
                    r'(\$\d+(?:\.\d{2})?)', 
                    r'(€\d+(?:\.\d{2})?)',
                ]
                
                extracted_price = ""
                for pattern in price_patterns:
                    matches = re.findall(pattern, buy_text)
                    if matches:
                        extracted_price = matches[0]  # Take first price found
                        break
                
                # Add context to price
                if extracted_price:
                    if is_track_available:
                        price = f"{extracted_price} (Track)"
                    elif is_album_only:
                        price = f"{extracted_price} (Album only)"
                    else:
                        price = extracted_price  # Fallback without context
                elif has_nyp:
                    price = "nyp (Track)" if is_track_available else "nyp (Album only)"
                else:
                    price = ""
                    
        except Exception as e:
            print(f"Timeout or error on Bandcamp track page: {e}")
            price = ""
        
        # Close the tab and switch back
        driver.close()
        driver.switch_to.window(main_window)
        
        return price
        
    except Exception as e:
# Performance timing only
        # Make sure we're back to main window
        try:
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return ""  # No fallback price

def search_bandcamp(artist, track):
    """Bandcamp scraper with comprehensive error handling"""
    import time
    platform = "Bandcamp"
    start_time = time.time()
    
    try:
        # Input validation
        if not artist and not track:
            error = create_error(
                ErrorType.VALIDATION_ERROR,
                platform,
                "No search parameters provided",
                artist=artist,
                track=track
            )
            log_error(error)
            return [_bandcamp_error_result("❌ No search terms provided")]
        
        # Dependency check
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import time
        except ImportError as e:
            error = create_error(
                ErrorType.DEPENDENCY_ERROR,
                platform,
                "Selenium dependencies not available",
                package="selenium",
                original_error=str(e)
            )
            log_error(error)
            return [_bandcamp_error_result("🔧 Browser automation not available")]
        
# Performance timing only
        start_time = time.time()
        
        url = f"https://bandcamp.com/search?q={artist}%20{track}"
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Bandcamp-specific balanced optimizations (not over-aggressive)
        options.add_argument('--page-load-strategy=eager')  # Keep this - it works
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-extensions')
        options.add_argument('--window-size=1280,720')  # Smaller window
        
        # Remove image blocking - can cause layout issues on Bandcamp
        # Keep notifications disabled only
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,  # Block notifications
            "profile.default_content_settings.popups": 0  # Block popups
        })
        
        try:
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            error = create_error(
                ErrorType.BROWSER_ERROR,
                platform,
                "Failed to initialize Chrome WebDriver for Bandcamp",
                original_error=str(e)
            )
            log_error(error)
            return [_bandcamp_error_result("🌐 Browser initialization failed")]
        
        try:
            # ULTRA-FAST timeouts for Bandcamp 
            driver.implicitly_wait(1)                    # 2s → 1s (-50%)
            driver.set_page_load_timeout(3)              # 4s → 3s (-25%)
            
            driver.get(url)
            
        except Exception as e:
            try:
                driver.quit()
            except:
                pass
            
            # Smart timeout handling for Bandcamp
            error_message = str(e).lower()
            if "timeout" in error_message:
                # Try one quick retry with slightly longer timeout
                print(f"⚡ Bandcamp: Quick retry with extended timeout...")
                try:
                    driver.set_page_load_timeout(5.0)  # One-time extension
                    driver.get(url)
                    print(f"✅ Bandcamp: Retry successful!")
                    # Continue with normal flow
                except Exception as retry_error:
                    error = create_error(
                        ErrorType.SCRIPT_TIMEOUT,
                        platform,
                        f"Page load timeout for Bandcamp after retry: {url}",
                        timeout_duration=5.0,
                        retry_attempted=True,
                        url=url,
                        original_error=str(retry_error)
                    )
                    log_error(error)
                    return [_bandcamp_error_result("🔴 Bandcamp not reachable")]
            elif "network" in error_message or "dns" in error_message:
                error = create_error(
                    ErrorType.SITE_DOWN,
                    platform,
                    "Cannot reach Bandcamp website",
                    url=url,
                    original_error=str(e)
                )
            else:
                error = create_error(
                    ErrorType.BROWSER_ERROR,
                    platform,
                    f"Browser error accessing Bandcamp: {str(e)}",
                    url=url,
                    original_error=str(e)
                )
            
            log_error(error)
            return [_bandcamp_error_result("🔴 Bandcamp not reachable")]
        
        # AGGRESSIVE wait time for <4s target
        wait = WebDriverWait(driver, 2)              # 4s → 2s (-50%)
        
        # Check if there are any results first, instead of waiting for elements that might not exist
        try:
            search_results = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.searchresult'))
            )
        except:
            # No search results found - check if this is "no results" or a real error
            page_source = driver.page_source.lower()
            if "no results" in page_source or "keine ergebnisse" in page_source or len(page_source) > 1000:
                # Page loaded successfully but no results found
# Performance timing only
                driver.quit()
                elapsed_time = time.time() - start_time
                return [{
                    'platform': 'Bandcamp',
                    'title': 'Kein Treffer',
                    'artist': '',
                    'album': '',
                    'label': '',
                    'price': '',
                    'cover_url': '',
                    'url': '',
                    'search_time': elapsed_time
                }]
            else:
                # Real error - page didn't load properly
                raise Exception("Page did not load properly")
        
        results = []
        candidates = []  # Collect top 3 candidates for relevance scoring
        
        for result in search_results[:1]:  # SPEED: Only 1 result - Bandcamp sorts very well by relevance
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
                    label = item_url.split(".bandcamp.com")[0].replace("https://", "") if ".bandcamp.com" in item_url else "Independent"
                except:
                    label = "Independent"
                
                # Extract real price from individual track page (only for relevant results)
                # Pre-calculate relevance to avoid unnecessary price extraction
                temp_score = calculate_relevance_score(artist, track, title, artist_name)
                if temp_score > 0:
                    price = extract_bandcamp_price(driver, item_url)
                else:
                    price = ""  # Skip price extraction for irrelevant results
                
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
        elapsed_time = time.time() - start_time
        
        # Select best result based on relevance score
        if candidates:
            best_result = max(candidates, key=lambda x: x['relevance_score'])
            # Remove score from final result (internal use only)
            best_result.pop('relevance_score', None)
            best_result['search_time'] = elapsed_time
            print(f"⏱️ Bandcamp: {best_result['title']} ({elapsed_time:.2f}s)")
            return [best_result]
        else:
            print(f"⏱️ Bandcamp: Kein Treffer ({elapsed_time:.2f}s)")
            return [{
                'platform': 'Bandcamp',
                'title': 'Kein Treffer',
                'artist': '',
                'album': '',
                'label': '',
                'price': '',
                'cover_url': '',
                'url': '',
                'search_time': elapsed_time
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
    
    except ImportError:
        # Test dummy for development when Selenium not available
        time.sleep(0.1)
        if artist.lower() in ["A", "a"] or track.lower() in ["A", "a"]:
            return [{
                'platform': 'Bandcamp',
                'title': f'TEST: {track}',
                'artist': f'TEST: {artist}',
                'album': f'TEST Album',
                'label': 'Independent',
                'price': 'nyp',
                'cover_url': 'https://via.placeholder.com/150x150/629AA0/FFFFFF?text=TEST',
                'url': f'https://bandcamp.com/search?q={track.lower()}',
                'search_time': 0.1
            }]
        return [_bandcamp_error_result("📭 Kein Treffer")]
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        error = create_error(
            ErrorType.UNKNOWN_ERROR,
            platform,
            f"Unexpected error in Bandcamp scraper: {str(e)}",
            elapsed_time=elapsed_time,
            original_error=str(e)
        )
        log_error(error)
        return [_bandcamp_error_result("❌ Bandcamp Suche nicht verfügbar")]

def _bandcamp_error_result(message: str) -> dict:
    """Helper function to create consistent Bandcamp error results"""
    return {
        'platform': 'Bandcamp',
        'title': message,
        'artist': '',
        'album': '',
        'label': '',
        'price': '',
        'cover_url': '',
        'url': '',
        'search_time': 0.0
    }

# --- TRAXSOURCE DUMMY ---
def search_traxsource(artist, track):
    """Traxsource scraper with comprehensive error handling"""
    import time
    platform = "Traxsource"
    start_time = time.time()
    
    try:
        # Input validation
        if not artist and not track:
            error = create_error(
                ErrorType.VALIDATION_ERROR,
                platform,
                "No search parameters provided",
                artist=artist,
                track=track
            )
            log_error(error)
            return [_traxsource_error_result("❌ No search terms provided")]
        
        # Dependency check
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import time
        except ImportError as e:
            error = create_error(
                ErrorType.DEPENDENCY_ERROR,
                platform,
                "Selenium dependencies not available",
                package="selenium",
                original_error=str(e)
            )
            log_error(error)
            return [_traxsource_error_result("🔧 Browser automation not available")]
        
# Performance timing only
        start_time = time.time()
        
        url = f"https://www.traxsource.com/search?term={artist}+{track}"
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Traxsource-specific speed optimizations
        options.add_argument('--page-load-strategy=eager')  # Don't wait for all resources
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--window-size=1280,720')  # Smaller window for speed
        
        try:
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            error = create_error(
                ErrorType.BROWSER_ERROR,
                platform,
                "Failed to initialize Chrome WebDriver for Traxsource",
                original_error=str(e)
            )
            log_error(error)
            return [_traxsource_error_result("🌐 Browser initialization failed")]
        
        try:
            # Aggressive timeouts for Traxsource (since IPv4 optimization not needed)
            driver.implicitly_wait(2)
            driver.set_page_load_timeout(6)  # Traxsource is slow, but 6s should be enough
            
            driver.get(url)
            
        except Exception as e:
            try:
                driver.quit()
            except:
                pass
            
            # Smart timeout handling for Traxsource  
            error_message = str(e).lower()
            if "timeout" in error_message:
                # Try one quick retry with extended timeout (Traxsource is notoriously slow)
                print(f"⚡ Traxsource: Quick retry with extended timeout...")
                try:
                    driver.set_page_load_timeout(8.0)  # Longer extension for Traxsource
                    driver.get(url)
                    print(f"✅ Traxsource: Retry successful!")
                    # Continue with normal flow
                except Exception as retry_error:
                    error = create_error(
                        ErrorType.SCRIPT_TIMEOUT,
                        platform,
                        f"Page load timeout for Traxsource after retry: {url}",
                        timeout_duration=8.0,
                        retry_attempted=True,
                        url=url,
                        original_error=str(retry_error)
                    )
                    log_error(error)
                    return [_traxsource_error_result("🔴 Traxsource not reachable")]
            elif "network" in error_message or "dns" in error_message:
                error = create_error(
                    ErrorType.SITE_DOWN,
                    platform,
                    "Cannot reach Traxsource website",
                    url=url,
                    original_error=str(e)
                )
            else:
                error = create_error(
                    ErrorType.BROWSER_ERROR,
                    platform,
                    f"Browser error accessing Traxsource: {str(e)}",
                    url=url,
                    original_error=str(e)
                )
            
            log_error(error)
            return [_traxsource_error_result("🔴 Traxsource not reachable")]
        
        # Reduced wait time since we're not getting IPv6 benefits
        wait = WebDriverWait(driver, 4)  # 10s → 4s
        
        # Optimized element loading - don't wait for ALL elements
        try:
            # Wait for first track row to appear, then get up to 3 results quickly
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.trk-row')))
            track_rows = driver.find_elements(By.CSS_SELECTOR, 'div.trk-row')[:3]  # Only process first 3
        except:
            # No track rows found - check if this is "no results" or a real error
            page_source = driver.page_source.lower()
            if "no results" in page_source or "no tracks found" in page_source or len(page_source) > 1000:
                # Page loaded successfully but no results found
# Performance timing only
                driver.quit()
                elapsed_time = time.time() - start_time
                return [{
                    'platform': 'Traxsource',
                    'title': 'Kein Treffer',
                    'artist': '',
                    'album': '',
                    'label': '',
                    'price': '',
                    'cover_url': '',
                    'url': '',
                    'search_time': elapsed_time
                }]
            else:
                # Real error - page didn't load properly
                raise Exception("Page did not load properly")
        
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
                
                # Extract real track URL from the page
                track_url = ""
                try:
                    # Try different selectors for Traxsource track links
                    link_selectors = [
                        'div.title a',             # Most common - title link
                        'a[href*="/title/"]',      # Direct title link
                        '.trk-cell .title a',     # Track cell title link  
                        'a.track-link'             # Generic track link class
                    ]
                    
                    for selector in link_selectors:
                        try:
                            link_elem = row.find_element(By.CSS_SELECTOR, selector)
                            href = link_elem.get_attribute('href')
                            if href and ('/title/' in href or '/track/' in href):
                                track_url = href
                                break
                        except:
                            continue
                    
                    # If no direct link found, try all links in row
                    if not track_url:
                        all_links = row.find_elements(By.TAG_NAME, 'a')
                        for link in all_links:
                            href = link.get_attribute('href')
                            if href and ('/title/' in href or '/track/' in href):
                                track_url = href
                                break
                    
                    # Fallback: construct URL if no real link found
                    if not track_url:
                        track_url = f'https://traxsource.com/track/{title.lower().replace(" ", "-")}'
                        
                except Exception as e:
                    print(f"Error extracting Traxsource URL: {e}")
                    track_url = f'https://traxsource.com/track/{title.lower().replace(" ", "-")}'
                
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
                        'url': track_url,  # Use extracted real URL
                        'search_time': 1.0,
                        'relevance_score': score
                    }
                    candidates.append(candidate)
            except Exception as e:
                print(f"Error processing Traxsource row: {e}")
                continue
        
        driver.quit()
        elapsed_time = time.time() - start_time
        
        # Select best result based on relevance score
        if candidates:
            best_result = max(candidates, key=lambda x: x['relevance_score'])
            # Remove score from final result (internal use only)
            best_result.pop('relevance_score', None)
            best_result['search_time'] = elapsed_time
            print(f"⏱️ Traxsource: {best_result['title']} ({elapsed_time:.2f}s)")
            return [best_result]
        else:
            print(f"⏱️ Traxsource: Kein Treffer ({elapsed_time:.2f}s)")
            return [{
                'platform': 'Traxsource',
                'title': 'Kein Treffer',
                'artist': '',
                'album': '',
                'label': '',
                'price': '',
                'cover_url': '',
                'url': '',
                'search_time': elapsed_time
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
    
    except ImportError:
        # Test dummy for development when Selenium not available
        time.sleep(0.1)
        if artist.lower() in ["A", "a"] or track.lower() in ["A", "a"]:
            return [{
                'platform': 'Traxsource',
                'title': f'TEST: {track}',
                'artist': f'TEST: {artist}',
                'album': f'TEST Album',
                'label': 'Test House Label',
                'price': '$2.99',
                'cover_url': 'https://via.placeholder.com/150x150/FF6600/FFFFFF?text=TEST',
                'url': f'https://traxsource.com/search?term={track.lower()}',
                'search_time': 0.1
            }]
        return [_traxsource_error_result("📭 Kein Treffer")]
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        error = create_error(
            ErrorType.UNKNOWN_ERROR,
            platform,
            f"Unexpected error in Traxsource scraper: {str(e)}",
            elapsed_time=elapsed_time,
            original_error=str(e)
        )
        log_error(error)
        return [_traxsource_error_result("❌ Traxsource Suche nicht verfügbar")]

def _traxsource_error_result(message: str) -> dict:
    """Helper function to create consistent Traxsource error results"""
    return {
        'platform': 'Traxsource',
        'title': message,
        'artist': '',
        'album': '',
        'label': '',
        'price': '',
        'cover_url': '',
        'url': '',
        'search_time': 0.0
    }

# --- REVIBED DUMMY ---
def search_revibed(artist, album):
    """Revibed scraper with comprehensive error handling"""
    import time
    platform = "Revibed"
    start_time = time.time()
    
    try:
        # Input validation - Revibed focuses on artist or album, not track
        if not artist and not album:
            error = create_error(
                ErrorType.VALIDATION_ERROR,
                platform,
                "No search parameters provided - Revibed requires artist or album",
                artist=artist,
                album=album
            )
            log_error(error)
            return [_revibed_error_result("❌ No search terms provided")]
        
        # Dependency check
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import time
        except ImportError as e:
            error = create_error(
                ErrorType.DEPENDENCY_ERROR,
                platform,
                "Selenium dependencies not available",
                package="selenium",
                original_error=str(e)
            )
            log_error(error)
            return [_revibed_error_result("🔧 Browser automation not available")]
        
# Performance timing only
        start_time = time.time()
        
        # Revibed search logic: Priority Artist first, then Album (not combined!)
        if artist and artist.strip():
            search_query = artist.strip()
        elif album and album.strip():
            search_query = album.strip()
        else:
            search_query = ""
        
        if not search_query:
            error = create_error(
                ErrorType.VALIDATION_ERROR,
                platform,
                "Empty search query after processing",
                artist=artist,
                album=album,
                processed_query=search_query
            )
            log_error(error)
            return [_revibed_error_result("❌ Empty search query")]
        
        # FIXED URL structure for Revibed (corrected format)
        encoded_query = search_query.replace(' ', '+')
        url = f"https://revibed.com/marketplace/buy-now-rare-vinyl-records-cds-&-cassette-tapes?query={encoded_query}&sort=totalPurchasesCount%2CDESC&size=25&page=0"
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # ULTRA AGGRESSIVE SPEED OPTIMIZATIONS for <4s target (Revibed specific)
        options.add_argument('--disable-images')
        # options.add_argument('--disable-javascript')  # Disabled for now - might break selectors
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI,VizDisplayCompositor')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-background-networking')
        options.add_argument('--aggressive-cache-discard')
        options.add_argument('--window-size=800,600')
        options.add_argument('--page-load-strategy=none')  # Don't wait for full page load
        
        # Network optimizations
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.plugins": 2,
            "profile.default_content_setting_values.popups": 2,
        })
        
        try:
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            error = create_error(
                ErrorType.BROWSER_ERROR,
                platform,
                "Failed to initialize Chrome WebDriver for Revibed",
                original_error=str(e)
            )
            log_error(error)
            return [_revibed_error_result("🌐 Browser initialization failed")]
        
        try:
            setup_time = time.time() - start_time
            print(f"DEBUG Revibed: Driver setup took {setup_time:.2f}s")
            
            # ULTRA AGGRESSIVE TIMEOUTS for <4s target (Revibed specific)
            driver.implicitly_wait(0.3)                  # 0.8s → 0.3s (ultra fast for elements)
            driver.set_page_load_timeout(2.5)            # 3s → 2.5s 
            
            page_load_start = time.time()
            driver.get(url)
            page_load_time = time.time() - page_load_start
            
        except Exception as e:
            try:
                driver.quit()
            except:
                pass
            
            # Smart timeout handling for Revibed
            error_message = str(e).lower()
            if "timeout" in error_message:
                # Try one quick retry with extended timeout
                print(f"⚡ Revibed: Quick retry with extended timeout...")
                try:
                    driver.set_page_load_timeout(4.5)  # Extension for Revibed
                    driver.get(url)
                    print(f"✅ Revibed: Retry successful!")
                    # Continue with normal flow
                except Exception as retry_error:
                    error = create_error(
                        ErrorType.SCRIPT_TIMEOUT,
                        platform,
                        f"Page load timeout for Revibed after retry: {url}",
                        timeout_duration=4.5,
                        retry_attempted=True,
                        url=url,
                        original_error=str(retry_error)
                    )
                    log_error(error)
                    return [_revibed_error_result("🔴 Revibed not reachable")]
            elif "network" in error_message or "dns" in error_message:
                error = create_error(
                    ErrorType.SITE_DOWN,
                    platform,
                    "Cannot reach Revibed website",
                    url=url,
                    original_error=str(e)
                )
            else:
                error = create_error(
                    ErrorType.BROWSER_ERROR,
                    platform,
                    f"Browser error accessing Revibed: {str(e)}",
                    url=url,
                    original_error=str(e)
                )
            
            log_error(error)
            return [_revibed_error_result("🔴 Revibed not reachable")]
        print(f"DEBUG Revibed: Page load took {page_load_time:.2f}s")
        
        wait = WebDriverWait(driver, 0.8)            # 1.5s → 0.8s (ultra fast)
        
        # Check if there are any results first, instead of waiting for elements that might not exist
        try:
            element_wait_start = time.time()
            # FIXED selector - old one was outdated
            items = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='marketplace']"))
            )
            element_wait_time = time.time() - element_wait_start
            print(f"DEBUG Revibed: Element wait took {element_wait_time:.2f}s, found {len(items)} items")
        except:
            # No items found - check if this is "no results" or a real error
            page_source = driver.page_source.lower()
            if "no results" in page_source or "keine ergebnisse" in page_source or len(page_source) > 1000:
                # Page loaded successfully but no results found
                driver.quit()
                elapsed_time = time.time() - start_time
                return [{
                    'platform': 'Revibed',
                    'title': 'Kein Treffer',
                    'artist': '',
                    'album': '',
                    'label': '',
                    'price': '',
                    'cover_url': '',
                    'url': '',
                    'search_time': elapsed_time
                }]
            else:
                # Real error - page didn't load properly
                raise Exception("Page did not load properly")
        
        results = []
        
        processing_start = time.time()
        
        # ULTRA SPEED HACK: Check page source for search terms first
        page_text = driver.page_source.lower()
        search_terms = []
        if artist and artist.strip():
            search_terms.append(artist.lower())
        if album and album.strip():
            search_terms.append(album.lower())
        
        # Early exit if no search terms found in entire page
        found_terms = [term for term in search_terms if term in page_text]
        print(f"DEBUG Revibed: Search terms {search_terms}, found terms: {found_terms}")
        
        if search_terms and not found_terms:
            print(f"DEBUG Revibed: No search terms found in page source, early exit")
            driver.quit()
            processing_time = time.time() - processing_start
            print(f"DEBUG Revibed: Processing took {processing_time:.2f}s")
            elapsed_time = time.time() - start_time
            print(f"⏱️ Revibed: Kein Treffer ({elapsed_time:.2f}s)")
            return [{
                'platform': 'Revibed',
                'title': 'Kein Treffer',
                'artist': '',
                'album': '',
                'label': '',
                'price': '',
                'cover_url': '',
                'url': '',
                'search_time': elapsed_time
            }]
        
        for item in items[:1]:  # ULTRA SPEED: Only 1 result for <4s target (was 2)
            try:
                # ULTRA FAST extraction - minimal DOM queries
                element_start = time.time()
                
                # Only do expensive DOM queries if quick match succeeded
                try:
                    title = item.find_element(By.CSS_SELECTOR, ".styles_projectNames__project__title__D49o3").text.strip()
                except:
                    title = 'N/A'
                
                try:
                    album_name = item.find_element(By.CSS_SELECTOR, ".styles_projectNames__album__title__V25wN").text.strip()
                except:
                    album_name = 'N/A'
                
                print(f"DEBUG Revibed: Element extraction took {time.time() - element_start:.2f}s")
                
                # Optimized image extraction
                try:
                    cover_url = item.find_element(By.CSS_SELECTOR, "img").get_attribute('src')
                except:
                    cover_url = ''
                
                # Enhanced price extraction with debugging
                try:
                    price_elem = item.find_element(By.CSS_SELECTOR, ".styles_marketplaceGoods__price__content__NwHxk")
                    price = price_elem.text.strip()
                    print(f"DEBUG Revibed: Found price with specific selector: {price}")
                except:
                    try:
                        # Alternative selector: any element with 'price' in class
                        price_elem = item.find_element(By.CSS_SELECTOR, "[class*='price']")
                        price = price_elem.text.strip()
                        print(f"DEBUG Revibed: Found price with generic selector: {price}")
                    except:
                        try:
                            # Try broader price selectors - look for actual prices first
                            price_candidates = item.find_elements(By.CSS_SELECTOR, "*")
                            found_prices = []
                            
                            for elem in price_candidates:
                                elem_text = elem.text.strip()
                                class_name = elem.get_attribute('class') or ''
                                
                                # Look for actual currency symbols first
                                if '€' in elem_text or '$' in elem_text:
                                    found_prices.append((elem_text, 'currency', class_name))
                                elif 'price' in class_name.lower() and elem_text:
                                    found_prices.append((elem_text, 'class', class_name))
                            
                            # Prefer actual currency over button text
                            if found_prices:
                                # Sort by priority: currency symbols first
                                found_prices.sort(key=lambda x: 0 if x[1] == 'currency' else 1)
                                price = found_prices[0][0]
                                print(f"DEBUG Revibed: Found price: {price} (type: {found_prices[0][1]}, class: {found_prices[0][2]})")
                            else:
                                price = "see link"
                                print("DEBUG Revibed: No price found with any selector")
                        except:
                            price = "see link"
                            print("DEBUG Revibed: Exception during price search")
                
                # Fast label extraction
                label = ""  # Skip for speed
                
                # Extract URL quickly
                try:
                    url_elem = item.find_element(By.CSS_SELECTOR, "a")
                    release_url = url_elem.get_attribute('href')
                    if release_url and not release_url.startswith('http'):
                        release_url = 'https://revibed.com' + release_url
                except:
                    release_url = f'https://revibed.com/item/{title.lower().replace(" ", "-")}'
                
                # FAST filter for <4s target - simplified matching
                search_match = False
                if artist and artist.strip():
                    # Priority: Artist search - simple case-insensitive contains check
                    artist_lower = artist.lower()
                    title_lower = title.lower()
                    album_lower = album_name.lower()
                    search_match = artist_lower in title_lower or artist_lower in album_lower
                elif album and album.strip():
                    # Fallback: Album search - simple case-insensitive contains check  
                    album_search_lower = album.lower()
                    title_lower = title.lower()
                    album_lower = album_name.lower()
                    search_match = album_search_lower in title_lower or album_search_lower in album_lower
                    
                if search_match:
                    results.append({
                        'platform': 'Revibed',
                        'title': title,
                        'artist': artist,  # Use provided artist
                        'album': album_name,
                        'label': label,
                        'price': price,
                        'cover_url': cover_url,
                        'url': release_url,  # Use extracted real URL
                        'search_time': 1.5
                    })
            except Exception as e:
                print(f"Error processing Revibed item: {e}")
                continue
        
        driver.quit()
        processing_time = time.time() - processing_start
        print(f"DEBUG Revibed: Processing took {processing_time:.2f}s")
        elapsed_time = time.time() - start_time
        
        # Return up to 3 results or no results
        if results:
            # Add search time to all results
            for result in results:
                result['search_time'] = elapsed_time
            print(f"⏱️ Revibed: {len(results)} Treffer ({elapsed_time:.2f}s)")
            return results
        else:
            print(f"⏱️ Revibed: Kein Treffer ({elapsed_time:.2f}s)")
            return [{
                'platform': 'Revibed',
                'title': 'Kein Treffer',  
                'artist': '',
                'album': '',
                'label': '',
                'price': '',
                'cover_url': '',
                'url': '',
                'search_time': elapsed_time
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
    
    except ImportError:
        # Test dummy for development when Selenium not available
        time.sleep(0.1)
        if artist and (artist.lower() in ["A", "a"] or album and album.lower() in ["A", "a"]):
            return [{
                'platform': 'Revibed',
                'title': f'TEST: {album or "Test Album"}',
                'artist': f'TEST: {artist or "Test Artist"}',
                'album': f'TEST: {album or "Test Album"}',
                'label': 'Test Vinyl Label',
                'price': '€25.00',
                'cover_url': 'https://via.placeholder.com/150x150/8B4513/FFFFFF?text=TEST',
                'url': f'https://revibed.com/item/test-{(album or artist or "test").lower()}',
                'search_time': 0.1
            }]
        return [_revibed_error_result("📭 Kein Treffer")]
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        error = create_error(
            ErrorType.UNKNOWN_ERROR,
            platform,
            f"Unexpected error in Revibed scraper: {str(e)}",
            elapsed_time=elapsed_time,
            original_error=str(e)
        )
        log_error(error)
        return [_revibed_error_result("❌ Revibed Suche nicht verfügbar")]

def _revibed_error_result(message: str) -> dict:
    """Helper function to create consistent Revibed error results"""
    return {
        'platform': 'Revibed',
        'title': message,
        'artist': '',
        'album': '',
        'label': '',
        'price': '',
        'cover_url': '',
        'url': '',
        'search_time': 0.0
    }

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
                # Use structured error message instead of generic "Fehler"
                error_title = f"🔧 {platform_name} Exception: {str(exc)[:50]}..."
                results.append({
                    "platform": platform_name,
                    "title": error_title, 
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
        # Scraper mit Performance-optimierter Konfiguration erzeugen
        scraper = create_discogs_scraper(
            headless=True,
            enable_cache=True,
            use_proxies=False
        )
        
        # PERFORMANCE OPTIMIZATION 1: Deaktiviere Anti-Bot Delays für GemFinder
        scraper.config.use_random_delays = False
        scraper.config.simulate_human_behavior = False
        print(f"🚀 Performance Mode: Anti-bot delays disabled for speed")

        # user_country in den Scraper-Config schreiben, damit das
        # build von marketplace_url korrekt funktioniert
        if user_country:
            scraper.config.user_country = user_country.upper()

        # Angebote scrapen (interne Methode liest scraper.config.user_country)
        raw = scraper.scrape_marketplace_offers(release_id, max_offers)

        offers = raw.get("offers", [])
        filtered = []

        # PERFORMANCE OPTIMIZATION 3: Early currency filter to avoid processing irrelevant offers
        print(f"🔍 Filtering {len(offers)} offers for currency {preferred_currency}")
        
        for o in offers:
            price_amt, price_curr = parse_price(o.get("price", ""))
            if price_curr != preferred_currency:
                continue  # Skip early - no processing needed

            shipping_amt, _ = parse_price(o.get("shipping", ""))
            item = o.copy()
            item.update({
                "price_amount":    price_amt,
                "price_currency":  price_curr,
                "shipping_amount": shipping_amt,
                "total_amount":    price_amt + shipping_amt
            })
            filtered.append(item)
            
            # Early exit if we have enough offers (performance optimization)
            if len(filtered) >= max_offers:
                print(f"🚀 Early exit: Found {len(filtered)} offers in {preferred_currency}")
                break

        return filtered

    except ImportError:
# Performance timing only
        return []

    except Exception as e:
# Performance timing only
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
