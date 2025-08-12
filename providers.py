# providers.py
from abc import ABC, abstractmethod
from scrape_search import search_bandcamp, search_beatport, search_traxsource, search_revibed
from api_search import search_discogs_releases, get_discogs_release_details, get_itunes_release_info

class SearchCriteria:
    def __init__(self, title: str = "", artist: str = "", album: str = "", catalog: str = ""):
        self.title   = title.strip()
        self.artist  = artist.strip()
        self.album   = album.strip()
        self.catalog = catalog.strip()

class SearchProvider(ABC):
    name: str

    @abstractmethod
    def can_search(self, c: SearchCriteria) -> bool:
        """Prüft, ob genügend Felder für diese Plattform gesetzt sind."""

    @abstractmethod
    def search(self, c: SearchCriteria) -> dict:
        """Führt die Suche aus und liefert genau ein Ergebnis-Dict."""

# —————————————————————————————
# Discogs-Provider
# —————————————————————————————
class DiscogsProvider(SearchProvider):
    name = "Discogs"

    def can_search(self, c: SearchCriteria) -> bool:
        # Priority order as specified:
        # 1. Catalog number + Artist
        # 2. Catalog number + Album  
        # 3. Catalog number + Title
        # 4. Title + Artist
        # 5. Title + Album
        # 6. Artist + Album
        # 7. Catalog number (alone)
        return bool(
            (c.catalog and c.artist) or
            (c.catalog and c.album) or
            (c.catalog and c.title) or
            (c.title and c.artist) or
            (c.title and c.album) or
            (c.artist and c.album) or
            c.catalog
        )

    def search(self, c: SearchCriteria) -> dict:
        """Return releases in consistent dict format like other providers"""
        print(f"DiscogsProvider: Searching for artist='{c.artist}', title='{c.title}', album='{c.album}'")
        releases = search_discogs_releases(c.artist, c.title, c.album)
        print(f"DiscogsProvider: Returning {len(releases)} releases")
        
        # Return in consistent format with other providers
        return {
            "platform": self.name,
            "releases": releases if releases else [],
            "count": len(releases) if releases else 0,
            "has_results": len(releases) > 0 if releases else False
        }

# —————————————————————————————
# Revibed-Provider
# —————————————————————————————
class RevibedProvider(SearchProvider):
    name = "Revibed"

    def can_search(self, c: SearchCriteria) -> bool:
        # Priority order as specified:
        # 1. Album
        # 2. Artist
        return bool(c.album or c.artist)

    def search(self, c: SearchCriteria) -> dict:
        # search_revibed takes (artist, album) parameters
        # Priority: Album first, then Artist (as per Revibed search logic)
        print(f"RevibedProvider: Searching with artist='{c.artist}', album='{c.album}'")
        hits = search_revibed(c.artist, c.album)
        first = hits[0] if hits else {}
        
        print(f"RevibedProvider: Got {len(hits)} results, first result: {first}")
        
        return {
            "platform":  self.name,
            "title":     first.get("title","Kein Treffer"),
            "artist":    first.get("artist", c.artist),
            "album":     first.get("album", c.album),
            "label":     first.get("label", ""),  # Fixed: handle string labels properly
            "price":     first.get("price",""),
            "cover_url": first.get("cover_url",""),
            "url":       first.get("url",""),
        }

# —————————————————————————————
# Digital-Shop-Provider (iTunes, Beatport, Bandcamp, Traxsource)
# —————————————————————————————

class ItunesProvider(SearchProvider):
    name = "iTunes"
    def can_search(self, c: SearchCriteria) -> bool:
        # Digital platform criteria:
        # 1. Title + Artist
        # 2. Title + Album
        # 3. Artist + Album
        return bool(
            (c.title and c.artist) or
            (c.title and c.album) or
            (c.artist and c.album)
        )
    def search(self, c: SearchCriteria) -> dict:
        result = get_itunes_release_info(c.artist, c.title)
        result["platform"] = self.name
        return result

class BeatportProvider(SearchProvider):
    name = "Beatport"
    def can_search(self, c: SearchCriteria) -> bool:
        # Digital platform criteria:
        # 1. Title + Artist
        # 2. Title + Album
        # 3. Artist + Album
        return bool(
            (c.title and c.artist) or
            (c.title and c.album) or
            (c.artist and c.album)
        )
    def search(self, c: SearchCriteria) -> dict:
        hits = search_beatport(c.artist, c.title, c.album)
        entry = hits[0] if hits else {"platform":self.name,"title":"Kein Treffer"}
        entry["platform"] = self.name
        return entry

class BandcampProvider(SearchProvider):
    name = "Bandcamp"
    def can_search(self, c: SearchCriteria) -> bool:
        # Digital platform criteria:
        # 1. Title + Artist
        # 2. Title + Album
        # 3. Artist + Album
        return bool(
            (c.title and c.artist) or
            (c.title and c.album) or
            (c.artist and c.album)
        )
    def search(self, c: SearchCriteria) -> dict:
        hits = search_bandcamp(c.artist, c.title)
        entry = hits[0] if hits else {"platform":self.name,"title":"Kein Treffer"}
        entry["platform"] = self.name
        return entry

class TraxsourceProvider(SearchProvider):
    name = "Traxsource"
    def can_search(self, c: SearchCriteria) -> bool:
        # Digital platform criteria:
        # 1. Title + Artist
        # 2. Title + Album
        # 3. Artist + Album
        return bool(
            (c.title and c.artist) or
            (c.title and c.album) or
            (c.artist and c.album)
        )
    def search(self, c: SearchCriteria) -> dict:
        hits = search_traxsource(c.artist, c.title)
        entry = hits[0] if hits else {"platform":self.name,"title":"Kein Treffer"}
        entry["platform"] = self.name
        return entry

# —————————————————————————————
# Manager, der alle passenden Provider parallel startet
# —————————————————————————————
class SearchManager:
    def __init__(self, providers: list[SearchProvider]):
        self.providers = providers

    def run_all(self, criteria: SearchCriteria) -> list[dict]:
        results = []
        for p in self.providers:
            if p.can_search(criteria):
                results.append(p.search(criteria))
        return results
