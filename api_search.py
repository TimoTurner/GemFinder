import requests
import time
from functools import lru_cache

# Global session for connection pooling - avoids Streamlit interference  
_itunes_session = None

def get_itunes_session():
    """Get or create global iTunes session for connection pooling"""
    global _itunes_session
    if _itunes_session is None:
        _itunes_session = requests.Session()
        # Configure for fast connections
        _itunes_session.timeout = 2
        # Keep-alive and connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=1,
            pool_maxsize=1,
            max_retries=0
        )
        _itunes_session.mount('https://', adapter)
    return _itunes_session

def get_itunes_release_info(artist, track):
    """iTunes API with test dummy and fallback error handling"""
    
    try:
        # Real iTunes API implementation
        
        print("Calling iTunes API...")
        t0 = time.time()
        
        query = f"{artist} {track}"
        url = "https://itunes.apple.com/search"
        params = {"term": query, "entity": "song", "limit": 1, "country": "DE"}
        
        session = get_itunes_session()
        response = session.get(url, params=params, timeout=2)
        print(f"iTunes API response: {time.time() - t0:.2f}s, Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                r = data["results"][0]
                return {
                    "platform": "iTunes",
                    "title": r.get("trackName", ""),
                    "artist": r.get("artistName", ""),
                    "album": r.get("collectionName", ""),
                    "label": "iTunes Store",
                    "price": f"{r.get('trackPrice', '')} {r.get('currency', '')}" if r.get("trackPrice") else "",
                    "cover": r.get("artworkUrl100", ""),
                    "release_url": r.get("trackViewUrl", ""),
                    "preview": r.get("previewUrl", "")
                }
        
        # No results found
        return {"platform": "iTunes", "title": "Kein Treffer", "artist": "", "album": "", "label": "", "price": "", "cover": "", "release_url": "", "preview": ""}
        
    except ImportError:
        # Test dummy for development (can be commented out to test error handling)
        print("Calling iTunes (with dummy data for test keywords)...")
        time.sleep(0.1)  # Simulate API call delay
        
        # Digital scenario test keywords
        if artist.lower() in ["A", "a"] or track.lower() in ["A", "a"]:
            return {
                "platform": "iTunes",
                "title": track,
                "artist": artist,
                "album": f"{track} - Single",
                "label": "iTunes Store",
                "price": "€1.29",
                "cover": "https://placehold.co/120x120/007AFF/white?text=iTunes",
                "release_url": f"https://itunes.apple.com/track/{track.lower().replace(' ', '-')}",
                "preview": f"https://audio-ssl.itunes.apple.com/preview/{track.lower().replace(' ', '-')}.m4a"
            }
        
        # For all other cases, return "Kein Treffer"
        return {"platform": "iTunes", "title": "Kein Treffer", "artist": "", "album": "", "label": "", "price": "", "cover": "", "release_url": "", "preview": ""}
    
    except Exception as e:
        print(f"❌ iTunes API error: {e}")
        return {"platform": "iTunes", "title": "❌ iTunes Suche nicht verfügbar", "artist": "", "album": "", "label": "", "price": "", "cover": "", "release_url": "", "preview": ""}

# Old iTunes API implementation removed - now integrated into active function

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
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"Discogs API Response: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            print(f"Found {len(results)} results from Discogs API")
            
            # Convert API response to expected format
            formatted_results = []
            for i, result in enumerate(results[:10]):  # Always show first 10 results
                # Debug: Print first few results to understand structure and filtering
                if i < 3:
                    print(f"Result {i+1}: {result}")
                
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
            
            print(f"Final formatted results count: {len(formatted_results)}")
            for i, res in enumerate(formatted_results[:3]):
                print(f"Formatted result {i+1}: ID={res['id']}, Title={res['title']}, Cover={res['cover']}")
            
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

# #############itunes results können noch mit fuzzymatching verbessert werden 

# def get_itunes_release_info(artist, track):
#     print("get_itunes_release_info AUFRUFEN")
#     import requests
#     import time
#     t0 = time.time()
#     print("Starte iTunes-Request")
#     query = f"{artist} {track}"
#     url = "https://itunes.apple.com/search"
#     params = {"term": query, "entity": "song", "limit": 1, "country": "DE"}
#     try:
#         response = requests.get(url, params=params, timeout=3)
#         print("Antwort iTunes:", time.time() - t0, "Sekunden", response.status_code)
#         if response.status_code == 200:
#             data = response.json()
#             if data.get("results"):
#                 r = data["results"][0]
#                 return {
#                     "release_url": r.get("trackViewUrl", ""),
#                     "cover": r.get("artworkUrl100", ""),
#                     "title": r.get("trackName", ""),
#                     "artist": r.get("artistName", ""),
#                     "preview": r.get("previewUrl", ""),
#                     "price": f"{r.get('trackPrice','')} {r.get('currency','')}" if r.get("trackPrice") else "",
#                     "price_url": r.get("trackViewUrl", "")
#                 }
#     except Exception as e:
#         print("Fehler bei iTunes-API:", e)
#     return {}
