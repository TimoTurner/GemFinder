import requests
import time
from functools import lru_cache

# iTunes API implementation
_itunes_session = None

def itunes_filter_result(search_artist, search_track, result_title, result_artist, result_album):
    """
    Moderate filtering for iTunes - one search term must match (less strict than Beatport)
    """
    from scrape_search import normalize_for_matching
    
    # Normalize search terms
    s_artist = normalize_for_matching(search_artist) if search_artist else ""
    s_track = normalize_for_matching(search_track) if search_track else ""
    
    # Normalize result fields
    r_title = normalize_for_matching(result_title) if result_title else ""
    r_artist = normalize_for_matching(result_artist) if result_artist else ""
    r_album = normalize_for_matching(result_album) if result_album else ""
    
    # Check if at least one search term is found in the result
    if s_artist and (s_artist in r_title or s_artist in r_artist or s_artist in r_album):
        return True
    if s_track and (s_track in r_title or s_track in r_artist or s_track in r_album):
        return True
    
    return False

def get_itunes_session():
    """Get or create global iTunes session optimized for Streamlit"""
    global _itunes_session
    if _itunes_session is None:
        _itunes_session = requests.Session()
        # Optimized adapter settings for Streamlit context
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=2,      # Reduced for Streamlit
            pool_maxsize=4,          # Smaller pool
            max_retries=0,           # No retries in ThreadPool context
            pool_block=False         # Don't block on pool exhaustion
        )
        _itunes_session.mount('https://', adapter)
        _itunes_session.headers.update({
            'User-Agent': 'GemFinder/1.0',
            'Accept': 'application/json',
            'Connection': 'close'    # Force connection close for Streamlit
        })
    return _itunes_session

def get_itunes_release_info(artist, track):
    """iTunes API search with optimized implementation for Streamlit"""
    import socket
    import time
    
    try:
        print(f"🎵 iTunes API search: '{artist}' - '{track}'")
        t0 = time.time()
        
        query = f"{artist} {track}"
        url = "https://itunes.apple.com/search"
        params = {"term": query, "entity": "song", "limit": 3, "country": "DE"}  # Get 3 results for filtering
        
        print(f"⏱️ Setup time: {time.time()-t0:.3f}s")
        
        # Force IPv4 to avoid IPv6 timeout delays
        original_getaddrinfo = socket.getaddrinfo
        def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
            return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
        socket.getaddrinfo = getaddrinfo_ipv4_only
        
        try:
            session = get_itunes_session()
            t1 = time.time()
            print(f"⏱️ Session get time: {t1-t0:.3f}s")
            
            # Retry logic for Streamlit context
            for attempt in range(2):  # 2 attempts max
                try:
                    t_request = time.time()
                    print(f"🔧 Attempt {attempt + 1}: Starting iTunes request")
                    
                    # Shorter connect timeout, longer read timeout for API responses
                    response = session.get(url, params=params, timeout=(2, 8))
                    
                    t2 = time.time()
                    print(f"⏱️ HTTP request time: {t2-t_request:.3f}s")
                    break
                except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as e:
                    attempt_time = time.time() - t_request
                    print(f"❌ Attempt {attempt + 1} failed after {attempt_time:.3f}s: {e}")
                    if attempt == 1:  # Last attempt
                        raise e
                    time.sleep(0.1)  # Brief pause before retry
        finally:
            # Restore original getaddrinfo
            socket.getaddrinfo = original_getaddrinfo
        
        elapsed = time.time() - t0
        print(f"✅ iTunes API total time: {elapsed:.3f}s, Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                print(f"🎯 iTunes found {len(results)} results, filtering...")
                
                # Filter results to find the most relevant one
                filtered_candidates = []
                for i, r in enumerate(results):
                    track_name = r.get("trackName", "")
                    artist_name = r.get("artistName", "")
                    album_name = r.get("collectionName", "")
                    
                    print(f"  Result {i+1}: '{track_name}' by '{artist_name}'")
                    
                    # Apply iTunes filter (moderate strictness)
                    if itunes_filter_result(artist, track, track_name, artist_name, album_name):
                        print(f"    ✅ Passed filter")
                        filtered_candidates.append(r)
                    else:
                        print(f"    ❌ Filtered out - not relevant")
                
                if filtered_candidates:
                    # Take the first filtered result (iTunes usually orders by relevance)
                    r = filtered_candidates[0]
                    print(f"🎯 iTunes selected: {r.get('trackName', 'No Title')}")
                    return {
                        "platform": "iTunes",
                        "title": r.get("trackName", ""),
                        "artist": r.get("artistName", ""),
                        "album": r.get("collectionName", ""),
                        "label": "iTunes Store",
                        "price": f"{r.get('trackPrice', '')} {r.get('currency', '')}".strip() if r.get("trackPrice") else "",
                        "cover_url": r.get("artworkUrl100", ""),
                        "url": r.get("trackViewUrl", ""),
                        "preview": r.get("previewUrl", "")
                    }
                else:
                    print("📭 iTunes: All results filtered out - no relevant matches")
            else:
                print("📭 iTunes: No results in response")
        else:
            print(f"❌ iTunes API error: Status {response.status_code}")
        
        return {
            "platform": "iTunes", 
            "title": "Kein Treffer", 
            "artist": "", 
            "album": "", 
            "label": "", 
            "price": "", 
            "cover_url": "", 
            "url": "", 
            "preview": ""
        }
        
    except Exception as e:
        elapsed = time.time() - t0 if 't0' in locals() else 0
        print(f"❌ iTunes API error after {elapsed:.3f}s: {e}")
        return {
            "platform": "iTunes", 
            "title": "❌ iTunes Suche nicht verfügbar", 
            "artist": "", 
            "album": "", 
            "label": "", 
            "price": "", 
            "cover_url": "", 
            "url": "", 
            "preview": ""
        }

def search_discogs_releases(artist=None, track=None, album=None, catno=None):
    """Real Discogs API implementation"""
    import os
    import requests
    from dotenv import load_dotenv
    
    # Load environment variables
    try:
        load_dotenv()
    except ImportError:
        pass
    
    # Discogs database/search API now requires authentication (since 2024)
    DISCOGS_USER_TOKEN = os.environ.get("DISCOGS_USER_TOKEN")
    
    if not DISCOGS_USER_TOKEN:
        print("❌ Discogs API error: Authentication required")
        print("   The Discogs database search API now requires a user token")
        return []
    
    # Build search query - Discogs API works better with simple terms
    query_parts = []
    if artist:
        query_parts.append(artist)
    if track:
        query_parts.append(track)
    if album:
        query_parts.append(album)
    if catno:
        query_parts.append(catno)
    
    if not query_parts:
        return []
    
    # Simple space-separated query works better than field-specific syntax
    query = " ".join(query_parts)
    
    try:
        url = "https://api.discogs.com/database/search"
        headers = {
            "Authorization": f"Discogs token={DISCOGS_USER_TOKEN}",
            "User-Agent": "GemFinderApp/1.0"
        }
        params = {
            "q": query,
            # Remove type filter to get all results like browser
            "per_page": 15,  # Get 15 raw results to ensure 10 good ones after filtering
            "page": 1
        }
        
        print(f"Searching Discogs API for: '{query}'")
        
        # Apply same IPv4 optimization as iTunes
        import socket
        original_getaddrinfo = socket.getaddrinfo
        def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
            return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
        socket.getaddrinfo = getaddrinfo_ipv4_only
        
        try:
            # Use optimized session with same settings as iTunes
            session = requests.Session()
            session.headers.update({
                'Connection': 'close'  # Force connection close for Streamlit
            })
            
            # Optimized timeouts: 2s connect, 8s read (same as iTunes)
            response = session.get(url, headers=headers, params=params, timeout=(2, 8))
        finally:
            # Restore original getaddrinfo
            socket.getaddrinfo = original_getaddrinfo
        
        print(f"Discogs API Response: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            # Convert API response to expected format
            formatted_results = []
            for i, result in enumerate(results[:10]):  # Always show first 10 results
                
                # Accept both releases and masters (like browser does)
                resource_url = result.get("resource_url", "")
                result_type = result.get("type", "")
                
                # Only skip artists and labels, keep releases and masters
                if result_type in ["artist", "label"]:
                    print(f"Skipping {result_type} result: {result.get('title', 'no title')}")
                    continue
                
                # Extract artist from title if available
                title = result.get("title", "")
                if " - " in title:
                    artist_from_title = title.split(" - ")[0]
                    release_title = title.split(" - ", 1)[1] if len(title.split(" - ", 1)) > 1 else title
                else:
                    artist_from_title = artist or "Unknown Artist"
                    release_title = title
                
                # Better cover image handling
                cover_image = result.get("cover_image") or result.get("thumb") or ""
                
                formatted_results.append({
                    "id": str(result.get("id", "")),
                    "cover": cover_image,
                    "thumb": result.get("thumb", cover_image),
                    "title": release_title,
                    "artist": artist_from_title,
                    "tracklist": [],  # Would need separate API call for full tracklist
                    "label": result.get("label", []),
                    "year": result.get("year", ""),
                    "format": result.get("format", []),
                    "catno": result.get("catno", ""),
                    "uri": result.get("uri", ""),
                    "type": result.get("type", ""),  # Add type for debugging
                    "community": result.get("community", {})  # Extract community data if availabl
                })
            
            # Formatted results ready
            
            return formatted_results
        else:
            print(f"Discogs API error: {response.status_code}")
            if response.status_code == 401:
                print("Discogs API authentication error - API may be restricted")
            elif response.status_code == 429:
                print("Rate limit exceeded - wait and try again")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response text: {response.text}")
            
    except Exception as e:
        print(f"Discogs API error: {e}")
    
    # Return empty list if API fails
    return []

def get_discogs_release_details(release_id):
    """Real Discogs API implementation for release details"""
    import os
    import requests
    from dotenv import load_dotenv
    
    # Load environment variables
    try:
        load_dotenv()
    except ImportError:
        pass
    
    DISCOGS_USER_TOKEN = os.environ.get("DISCOGS_USER_TOKEN")
    
    if not DISCOGS_USER_TOKEN:
        print("❌ Discogs API error: Authentication required")
        return {
            "id": release_id,
            "title": f"Release {release_id}",
            "tracklist": [],
            "label": ["Unknown"],
            "year": "",
            "format": ["Unknown"],
            "cover": ""
        }
    
    try:
        url = f"https://api.discogs.com/releases/{release_id}"
        headers = {
            "Authorization": f"Discogs token={DISCOGS_USER_TOKEN}",
            "User-Agent": "GemFinderApp/1.0"
        }
        
        print(f"Getting Discogs release details for ID: {release_id}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Format tracklist
            tracklist = []
            for track in data.get("tracklist", []):
                tracklist.append({
                    "position": track.get("position", ""),
                    "title": track.get("title", ""),
                    "duration": track.get("duration", "")
                })
            
            return {
                "id": str(data.get("id", release_id)),
                "title": data.get("title", ""),
                "tracklist": tracklist,
                "label": data.get("labels", [{"name": "Unknown"}])[0].get("name", "Unknown") if data.get("labels") else ["Unknown"],
                "year": data.get("year", ""),
                "format": [f.get("name", "") for f in data.get("formats", [])],
                "cover": data.get("images", [{}])[0].get("uri", "") if data.get("images") else "",
                "community": data.get("community", {})  # Add community data
            }
        else:
            print(f"Discogs API error: {response.status_code}")
            
    except Exception as e:
        print(f"Discogs API error: {e}")
    
    # Fallback
    return {
        "id": release_id,
        "title": f"Release {release_id}",
        "tracklist": [],
        "label": ["Unknown"],
        "year": "",
        "format": ["Unknown"],
        "cover": ""
    }

def get_discogs_offers(release_id, currency="EUR", country="DE"):
    """
    DEPRECATED: Discogs Marketplace API is not publicly available.
    
    This function was based on the assumption that Discogs provides a marketplace API,
    but research shows that Discogs discontinued/never provided public access to 
    marketplace listings via API. Web scraping is the only option.
    
    Returns empty list to maintain compatibility.
    """
    print("⚠️ Discogs Marketplace API is not available - use web scraping instead")
    return []

##################################################################Dummy Ende
# import os
# import requests
# from dotenv import load_dotenv

# # ENV laden (optional)
# load_dotenv()

# DISCOGS_USER_TOKEN = os.environ.get("DISCOGS_USER_TOKEN")
# DISCOGS_CONSUMER_KEY = os.environ.get("DISCOGS_CONSUMER_KEY")
# DISCOGS_CONSUMER_SECRET = os.environ.get("DISCOGS_CONSUMER_SECRET")

# def get_discogs_release_info(artist=None, track=None, catalog_number=None, album=None, label=None):
#     """
#     Kombinierte Suche auf Discogs. Gibt Liste von Release-Dicts zurück.
#     """
#     url = "https://api.discogs.com/database/search"
#     query = " ".join(filter(None, [artist, track, catalog_number, album, label]))
#     params = {
#         "q": query,
#         "key": DISCOGS_CONSUMER_KEY,
#         "secret": DISCOGS_CONSUMER_SECRET,
#         "per_page": 10,
#         "page": 1,
#     }
#     headers = {
#         "Authorization": f"Discogs token={DISCOGS_USER_TOKEN}",
#         "User-Agent": "GemFinderApp/1.0"
#     }
#     try:
#         response = requests.get(url, params=params, headers=headers)
#         if response.status_code == 200:
#             return response.json().get("results", [])[:10]
#     except Exception as e:
#         print(f"Discogs API Error: {e}")
#     return []

# # Alias, damit auch alte Aufrufe weiter funktionieren
# def search_discogs_releases(artist=None, track=None, catno=None, album=None, label=None):
#     return get_discogs_release_info(artist, track, catalog_number, album, label)

# def get_discogs_offers(release_id, currency="EUR"):
#     url = "https://api.discogs.com/marketplace/search"
#     headers = {
#         "Authorization": f"Discogs token={DISCOGS_USER_TOKEN}",
#         "User-Agent": "GemFinderApp/1.0"
#     }
#     params = {"release_id": release_id, "currency": currency}
#     try:
#         response = requests.get(url, headers=headers, params=params)
#         print("Discogs Marketplace API-URL:", response.url)
#         print("Status:", response.status_code)
#         print("Antwort:", response.text)
#         if response.status_code == 200:
#             data = response.json()
#             # Die Angebote sind hier direkt in "results"
#             return data.get("results", [])
#     except Exception as e:
#         print(f"Discogs API Error: {e}")
#     return []

# def get_discogs_release_details(release_id):
#     """
#     Holt alle Details (inkl. Tracklist) für ein Release von Discogs.
#     """
#     url = f"https://api.discogs.com/releases/{release_id}"
#     headers = {
#         "Authorization": f"Discogs token={DISCOGS_USER_TOKEN}",
#         "User-Agent": "GemFinderApp/1.0"
#     }
#     try:
#         response = requests.get(url, headers=headers, timeout=3)
#         if response.status_code == 200:
#             return response.json()
#     except Exception as e:
#         print(f"Discogs API Error: {e}")
#     return {}

# Old commented iTunes code removed
