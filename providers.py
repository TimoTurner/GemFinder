# providers.py
from abc import ABC, abstractmethod
from scrape_search import search_bandcamp, search_beatport, search_traxsource, search_revibed
from api_search import get_itunes_release_info, search_discogs_releases, get_discogs_release_details, get_discogs_offers

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
        # search_revibed nimmt (artist, album)-Parameter
        artist = "" if c.album else c.artist
        hits = search_revibed(artist, c.album)
        first = hits[0] if hits else {}
        return {
            "platform":  self.name,
            "title":     first.get("title","Kein Treffer"),
            "artist":    first.get("artist", c.artist),
            "album":     first.get("album", c.album),
            "label":     (first.get("label") or [""])[0],
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
        # Priority order as specified:
        # 1. Title + Artist
        # 2. Title + Album
        # 3. Artist + Album
        return bool(
            (c.title and c.artist) or
            (c.title and c.album) or
            (c.artist and c.album)
        )
    def search(self, c: SearchCriteria) -> dict:
        info = get_itunes_release_info(c.artist, c.title)
        if info and info.get("release_url"):
            return {
                "platform":  self.name,
                "title":     info.get("title",""),
                "artist":    info.get("artist",c.artist),
                "album":     info.get("album",""),
                "label":     info.get("label",""),
                "price":     info.get("price",""),
                "cover_url": info.get("cover",""),
                "url":       info.get("release_url",""),
                "preview":   info.get("preview","")
            }
        else:
            return {
                "platform": self.name,
                "title":    "Kein Treffer",
                "artist":   c.artist,
                "album":    c.album,
                "label":    "",
                "price":    "",
                "cover_url":"",
                "url":      "",
                "preview":  ""
            }

class BeatportProvider(SearchProvider):
    name = "Beatport"
    def can_search(self, c: SearchCriteria) -> bool:
        # Same criteria as iTunes:
        # 1. Title + Artist
        # 2. Title + Album
        # 3. Artist + Album
        return bool(
            (c.title and c.artist) or
            (c.title and c.album) or
            (c.artist and c.album)
        )
    def search(self, c: SearchCriteria) -> dict:
        hits = search_beatport(c.artist, c.title)
        entry = hits[0] if hits else {"platform":self.name,"title":"Kein Treffer"}
        entry["platform"] = self.name
        return entry

class BandcampProvider(SearchProvider):
    name = "Bandcamp"
    def can_search(self, c: SearchCriteria) -> bool:
        # Same criteria as iTunes:
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
        # Same criteria as iTunes:
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
