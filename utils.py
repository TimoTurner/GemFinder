# utils.py

from rapidfuzz import fuzz

# Kopiere hier dein PLATFORM_LINKS-Mapping aus main.py
PLATFORM_LINKS = {
    "Beatport": (
        "https://www.beatport.com/",
        "https://seeklogo.com/images/B/beatport-logo-1A5DCCBFAE-seeklogo.com.png"
    ),
    "Bandcamp": (
        "https://bandcamp.com/",
        "https://cdn-icons-png.flaticon.com/512/2111/2111624.png"
    ),
    "Traxsource": (
        "https://www.traxsource.com/",
        "https://cdn.traxsource.com/static/images/logos/apple-touch-icon-114x114.png"
    ),
    "iTunes": (
        "https://music.apple.com/",
        "https://upload.wikimedia.org/wikipedia/commons/d/de/ITunes_logo.png"
    ),
    "Revibed": (
        "https://revibed.com/",
        "https://revibed.com/favicon-32x32.png"
    ),
    "Discogs": (
        "https://www.discogs.com/",
        "https://upload.wikimedia.org/wikipedia/commons/0/09/Discogs_Logo.png"
    ),
}

PLACEHOLDER_COVER = "cover_placeholder.png"

# Currency mapping by country/region for marketplace display
CURRENCY_MAPPING = {
    # Eurozone countries
    'AT': 'EUR', 'BE': 'EUR', 'CY': 'EUR', 'EE': 'EUR', 'FI': 'EUR', 'FR': 'EUR',
    'DE': 'EUR', 'GR': 'EUR', 'IE': 'EUR', 'IT': 'EUR', 'LV': 'EUR', 'LT': 'EUR',
    'LU': 'EUR', 'MT': 'EUR', 'NL': 'EUR', 'PT': 'EUR', 'SK': 'EUR', 'SI': 'EUR',
    'ES': 'EUR', 'AD': 'EUR', 'MC': 'EUR', 'SM': 'EUR', 'VA': 'EUR',
    
    # Major currencies
    'US': 'USD', 'GB': 'GBP', 'CA': 'CAD', 'AU': 'AUD', 'JP': 'JPY',
    'CH': 'CHF', 'SE': 'SEK', 'NO': 'NOK', 'DK': 'DKK', 'PL': 'PLN',
    
    # Default fallback
    'DEFAULT': 'EUR'
}

# Condition quality hierarchy for Discogs offers
CONDITION_HIERARCHY = {
    'Mint (M)': 5,
    'Near Mint (NM or M-)': 4,
    'Very Good Plus (VG+)': 3,
    'Very Good (VG)': 2,
    'Good Plus (G+)': 1,
    'Good (G)': 0,
    'Fair (F)': -1,
    'Poor (P)': -2
}

# High quality conditions for filtering
HIGH_QUALITY_CONDITIONS = ['Mint (M)', 'Near Mint (NM or M-)', 'Very Good Plus (VG+)']

def get_platform_info(platform: str):
    """
    Liefert (base_url, logo_url) zu einer Plattform.
    """
    return PLATFORM_LINKS.get(platform, ("#", PLACEHOLDER_COVER))


def is_fuzzy_match(user_track: str, shop_title: str, threshold: int = 80) -> bool:
    """
    Vergleicht zwei Strings per fuzzy matching.
    """
    if not user_track or not shop_title:
        return False
    return fuzz.partial_ratio(user_track.lower(), shop_title.lower()) >= threshold


def parse_price(price_str: str) -> tuple[float, str]:
    """Parse price string and extract amount and currency"""
    if not price_str or price_str == 'N/A':
        return 0.0, 'EUR'
    
    # Remove whitespace
    price_str = price_str.strip()
    
    # Common currency symbols
    currency_symbols = {
        '€': 'EUR', '$': 'USD', '£': 'GBP', '¥': 'JPY',
        'CHF': 'CHF', 'SEK': 'SEK', 'NOK': 'NOK', 'DKK': 'DKK'
    }
    
    # Try to extract currency and amount
    for symbol, currency in currency_symbols.items():
        if symbol in price_str:
            try:
                amount = float(price_str.replace(symbol, '').replace(',', '.').strip())
                return amount, currency
            except ValueError:
                continue
    
    # Fallback: assume it's a number in EUR
    try:
        return float(price_str.replace(',', '.')), 'EUR'
    except ValueError:
        return 0.0, 'EUR'
