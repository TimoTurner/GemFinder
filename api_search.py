def get_itunes_release_info(artist, track):
    # Dummy-Antwort: Immer "Kein Treffer"
    return {
        "platform": "iTunes",
        "title": "Kein Treffer",
        "artist": "",
        "album": "",
        "label": "",
        "price": "",
        "cover": "",
        "release_url": "",
        "preview": ""
    }

def get_discogs_release_info(catalog_number, artist, track, album):
    offers = []
    if "demo track b" in track.lower():
        offers = [
            {"seller": "VinylKing", "country": "Germany", "condition": "VG+", "price": "15", "currency": "EUR", "url": "https://discogs.com/demo-b-vgplus", "shipping": "5"},
            {"seller": "Collector", "country": "Netherlands", "condition": "NM", "price": "19", "currency": "EUR", "url": "https://discogs.com/demo-b-nm", "shipping": "6"}
        ]
    return {
        "offers": offers,
        "album": album,
        "artist": artist,
        "tracklist": [track],
        "want_have_ratio": "5/100",
        "label": "Dummy Label",
        "avg_price": "15.00"
    }
def search_discogs_releases(artist=None, track=None, album=None, catno=None):
    # Bei komplett leeren Eingaben keine Treffer simulieren
    if not (artist or track or album or catno):
        return []
    # Dummy-Releases wie gehabt
    return [
        {
            "id": str(i),
            "cover": "",
            "title": f"{track or album or 'Track'} Version {i+1}",
            "artist": artist,
            "tracklist": [track, f"{track} (Remix)"] if track else [],
            "label": [f"Label{i}"],
            "year": f"{2000+i}"
        }
        for i in range(10)
    ]

def get_discogs_release_details(release_id):
    # Simuliere ein reales Release
    return {
        "id": release_id,
        "title": f"Demo Release {release_id}",
        "tracklist": [
            {"position": "A1", "title": "Demo Track A", "duration": "4:20"},
            {"position": "B1", "title": "Demo Track B", "duration": "5:00"},
        ],
        "label": [f"Label{release_id}"],
        "year": f"{2000+int(release_id)}",
        "cover": "https://placehold.co/120x120"
    }

def get_discogs_offers(release_id):
    # Dummy-Angebote für verschiedene Länder und Währungen
    return [
        {
            "seller": {"username": "VinylKing"},
            "ships_from": "Germany",
            "condition": "NM",
            "price": "32",
            "shipping_price": "5",
            "uri": "https://discogs.com/offer1"
        },
        {
            "seller": {"username": "Collector"},
            "ships_from": "Netherlands",
            "condition": "VG+",
            "price": "29",
            "shipping_price": "6",
            "uri": "https://discogs.com/offer2"
        },
        {
            "seller": {"username": "BritCollector"},
            "ships_from": "United Kingdom",
            "condition": "VG+",
            "price": "30",
            "shipping_price": "6",
            "uri": "https://discogs.com/offer3"
        },
        {
            "seller": {"username": "StatesVinyl"},
            "ships_from": "United States",
            "condition": "VG+",
            "price": "35",
            "shipping_price": "10",
            "uri": "https://discogs.com/offer4"
        },
    ]

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
