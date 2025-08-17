# ui_helpers.py
import time

def show_live_results():
    """Display live search results as they come in from parallel threads"""
    import streamlit as st
    
    live_results = st.session_state.get("live_results", [])
    
    # Always show progress bar when search is started, even with no results yet
    if not live_results and st.session_state.get("suche_gestartet", False):
        # Use single persistent progress display
        if "live_progress_container" not in st.session_state:
            st.session_state.live_progress_container = st.empty()
        
        with st.session_state.live_progress_container.container():
            st.info("🔍 Starting search...")
            st.progress(0)  # Show 0% progress bar immediately
        return
    elif not live_results:
        return
    
    # Show progress bar with platform status
    platform_status = {}
    total_platforms = 4  # iTunes, Beatport, Bandcamp, Traxsource
    
    for result in live_results:
        platform = result.get("platform", "Unknown")
        title = result.get("title", "")
        
        # Check if this is a real result or error - updated for new error handling
        # Old error patterns
        old_error_patterns = ["kein treffer", "fehler", "", "❌ fehler"]
        # New structured error patterns from error handling system
        new_error_patterns = [
            "❌", "🔴", "🔧", "📭", "🚫", "🐌", "⚡", "🔒", 
            "not reachable", "nicht verfügbar", "not available",
            "initialization failed", "browser error", "timeout",
            "no search terms", "keine suchbegriffe"
        ]
        
        is_error = (
            title.lower() in old_error_patterns or 
            any(pattern in title.lower() for pattern in new_error_patterns)
        )
        
        if is_error:
            if "nicht verfügbar" in title.lower() or "not available" in title.lower():
                platform_status[platform] = "⚠️"
            else:
                platform_status[platform] = "❌"
        else:
            platform_status[platform] = "✅"
    
    # Build progress string
    progress_parts = []
    for platform in ["iTunes", "Beatport", "Bandcamp", "Traxsource"]:
        status = platform_status.get(platform, "⏳")
        progress_parts.append(f"{platform} {status}")
    
    progress_text = ", ".join(progress_parts)
    
    # Use single persistent progress display
    if "live_progress_container" not in st.session_state:
        st.session_state.live_progress_container = st.empty()
    
    with st.session_state.live_progress_container.container():
        st.info(f"🔍 Searching: {progress_text}")
        
        completed_count = len([p for p in platform_status.values() if p in ["✅", "❌", "⚠️"]])
        if completed_count > 0:
            st.progress(completed_count / total_platforms)
    
    # Show digital results immediately as they come in (each platform only once)
    PLACEHOLDER_COVER = "cover_placeholder.png"
    NO_HIT_COVER = "not_found.png"
    
    # Initialize containers for each platform if not exists
    if "live_results_containers" not in st.session_state:
        st.session_state.live_results_containers = {}
        st.session_state.live_results_header_shown = False
    
    # Show header only once - render in a container so it can be cleared
    if "live_results_header_container" not in st.session_state:
        st.session_state.live_results_header_container = st.empty()
    
    if live_results and not st.session_state.live_results_header_shown:
        with st.session_state.live_results_header_container.container():
            st.markdown("#### Digital Results")
        st.session_state.live_results_header_shown = True
    
    # Display only NEW results (not already displayed)
    displayed_platforms = set(st.session_state.live_results_containers.keys())
    
    for entry in live_results:
        platform_str = entry.get("platform", "")
        
        # Skip if this platform was already displayed
        if platform_str in displayed_platforms:
            continue
            
        # Create container for this platform
        st.session_state.live_results_containers[platform_str] = st.empty()
        
        # Display this platform's result
        with st.session_state.live_results_containers[platform_str].container():
            title_str = str(entry.get("title", ""))
            artist_str = str(entry.get("artist", ""))
            album_str = str(entry.get("album", ""))
            label_raw = entry.get("label", "")
            label_str = label_raw[0] if isinstance(label_raw, list) and label_raw else str(label_raw)
            price_str = str(entry.get("price", ""))
            cover_url = entry.get("cover_url", "") or entry.get("cover", "")
            release_url = entry.get("url", "").strip()
            
            # Image selection - show NO_HIT_COVER for no results, PLACEHOLDER for valid results without cover
            is_real_hit = is_valid_result(entry, check_empty_title=False)
            if not cover_url or not cover_url.strip():
                cover_url = PLACEHOLDER_COVER if is_real_hit else NO_HIT_COVER
            
            # Display result
            cols = st.columns([1, 5])
            with cols[0]:
                st.image(cover_url, width=92)
            with cols[1]:
                if release_url:
                    st.markdown(f"[**{platform_str}**]({release_url})")
                else:
                    from utils import get_platform_info
                    platform_url, _ = get_platform_info(platform_str)
                    st.markdown(f"[**{platform_str}**]({platform_url})")
                
                st.markdown(f"**{title_str}**")
                if artist_str:
                    st.markdown(f"{artist_str}")
                if album_str:
                    st.markdown(f"*{album_str}*")
                if label_str:
                    st.markdown(f"`{label_str}`")
                if price_str and release_url:
                    st.markdown(f"[{price_str}]({release_url})")
                elif price_str:
                    st.markdown(f":green[{price_str}]")
                
                # Preview functionality for iTunes
                if entry.get("preview") and is_real_hit:
                    st.audio(entry["preview"], format="audio/mp4")
            
            st.markdown("---")
    
    # Show mode switch button when there are digital hits (at least 1 real result)
    if st.session_state.get("digital_search_done", False):
        # Clear progress container when showing final digital results
        if "live_progress_container" in st.session_state:
            st.session_state.live_progress_container.empty()
        
        # Check if there are real hits - updated to recognize new error handling messages
        real_hits = []
        for r in st.session_state.get("live_results", []):
            title = (r.get("title") or "").strip().lower()
            # Old error patterns
            old_patterns = ("kein treffer", "", "fehler")
            # New structured error patterns from error handling system
            new_error_patterns = (
                "❌", "🔴", "🔧", "📭", "🚫", "🐌", "⚡", "🔒", 
                "not reachable", "nicht verfügbar", "not available",
                "initialization failed", "browser error", "timeout",
                "no search terms", "keine suchbegriffe"
            )
            
            # Check if this is a real hit (not an error message)
            is_error = (
                title in old_patterns or 
                any(pattern in title for pattern in new_error_patterns)
            )
            
            if not is_error:
                real_hits.append(r)
        
        # Button logic moved to main.py to avoid state issues
        # Just store that we have hits for main.py to use
        if len(real_hits) > 0:
            st.session_state.has_digital_hits_for_button = True

import streamlit as st
from scrape_search import search_revibed, scrape_discogs_marketplace_offers
from selenium_scraper_deployment import selenium_filter_offers_parallel
# Passe den Import-Pfad hier an, je nachdem wo du get_platform_info und is_fuzzy_match definiert hast:
from api_search import search_discogs_releases, get_discogs_release_details, get_discogs_offers
from utils import (get_platform_info, is_fuzzy_match, CURRENCY_MAPPING, 
                   CONDITION_HIERARCHY, HIGH_QUALITY_CONDITIONS, parse_price)
import requests
from api_search import get_discogs_release_details
from bs4 import BeautifulSoup

def check_offer_shipping_availability(offer_url, user_country):
    """
    Check if an offer is available for shipping to user's country
    by fetching the offer page and parsing the shipping info.
    
    Returns: True if available, False if restricted
    """
    try:
        # Use more comprehensive headers to avoid 403 blocks
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
        
        # Quick timeout for faster processing
        response = requests.get(offer_url, timeout=5, headers=headers)
        
        if response.status_code == 403:
            print(f"403 Forbidden for {offer_url} - checking if URL indicates unavailability")
            # If we get 403, we can't check the content, but we can try to be conservative
            # For now, let's assume it's available and let the user decide
            return True
        elif response.status_code != 200:
            print(f"Failed to fetch offer page: {offer_url} (Status: {response.status_code})")
            return True  # Assume available if we can't check
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for shipping restrictions - check specifically in no_offer container
        no_offer_container = soup.find('div', class_='inline-buttons no_offer')
        
        if no_offer_container:
            # Look for pricing_info muted within the no_offer container
            pricing_info = no_offer_container.find('p', class_='pricing_info muted')
            if pricing_info:
                shipping_text = pricing_info.get_text().strip()
                print(f"Found shipping restriction in no_offer container: '{shipping_text}'")
                
                # Check for country restrictions
                user_country_name = {
                    'DE': 'Germany', 'US': 'United States', 'GB': 'United Kingdom',
                    'FR': 'France', 'NL': 'Netherlands', 'CA': 'Canada',
                    'AU': 'Australia', 'CH': 'Switzerland'
                }.get(user_country, user_country)
                
                # Check for unavailability patterns
                unavailable_patterns = [
                    f'Unavailable in {user_country_name}',
                    f'Not available in {user_country_name}',
                    f'No shipping to {user_country_name}',
                    'Does not ship to your country'
                ]
                
                for pattern in unavailable_patterns:
                    if pattern in shipping_text:
                        print(f"Offer restricted for {user_country_name}: {shipping_text}")
                        return False
        
        return True  # No restrictions found
        
    except Exception as e:
        print(f"Error checking shipping for {offer_url}: {e}")
        return True  # Assume available if error occurs

# --- Unified Hit Detection Logic ---
def is_valid_result(entry, check_empty_title=True):
    """Unified function to check if a result is valid (not a 'no hit' response) - updated for new error handling"""
    title = (entry.get("title") or "").strip().lower()
    
    # Old error patterns
    old_invalid_titles = ["kein treffer", "fehler / kein treffer", "", "nicht gesucht (angaben fehlen)", "fehler"]
    # New structured error patterns from error handling system
    new_error_patterns = [
        "❌", "🔴", "🔧", "📭", "🚫", "🐌", "⚡", "🔒", 
        "not reachable", "nicht verfügbar", "not available",
        "initialization failed", "browser error", "timeout",
        "no search terms", "keine suchbegriffe"
    ]
    
    is_invalid = (
        title in old_invalid_titles or 
        any(pattern in title for pattern in new_error_patterns)
    )
    
    if check_empty_title:
        return title and not is_invalid
    else:
        return not is_invalid

def get_user_location():
    """Get user location via IP for currency zone detection"""
    if 'user_location' in st.session_state:
        return st.session_state.user_location
    
    try:
        r = requests.get("https://ipinfo.io/json", timeout=3)
        if r.status_code == 200:
            data = r.json()
            location = {
                "country": data.get("country", "DE"),  # Default to Germany
                "city": data.get("city", "Unknown"),
                "currency": CURRENCY_MAPPING.get(data.get("country", "DE"), "EUR")
            }
            st.session_state.user_location = location
            return location
    except Exception as e:
        print(f"Location Error: {e}")
    
    # Default location
    default_location = {"country": "DE", "city": "Unknown", "currency": "EUR"}
    st.session_state.user_location = default_location
    return default_location


def ask_user_location():
    """Interactive location selection for better currency filtering"""
    st.markdown("### 📍 Your Location")
    
    # Auto-detect first
    auto_location = get_user_location()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Country selection
        country_options = {
            '🇩🇪 Germany': {'country': 'DE', 'currency': 'EUR'},
            '🇺🇸 United States': {'country': 'US', 'currency': 'USD'},
            '🇬🇧 United Kingdom': {'country': 'GB', 'currency': 'GBP'},
            '🇫🇷 France': {'country': 'FR', 'currency': 'EUR'},
            '🇳🇱 Netherlands': {'country': 'NL', 'currency': 'EUR'},
            '🇨🇦 Canada': {'country': 'CA', 'currency': 'CAD'},
            '🇦🇺 Australia': {'country': 'AU', 'currency': 'AUD'},
            '🇨🇭 Switzerland': {'country': 'CH', 'currency': 'CHF'},
            '🌍 Other': {'country': 'OTHER', 'currency': 'EUR'}
        }
        
        # Pre-select based on auto-detection
        auto_detected = "🇩🇪 Germany"  # Default
        for display_name, info in country_options.items():
            if info['country'] == auto_location['country']:
                auto_detected = display_name
                break
        
        selected_country = st.selectbox(
            "Select your country/region:",
            options=list(country_options.keys()),
            index=list(country_options.keys()).index(auto_detected),
            key="user_country_selector"
        )
        
        user_location = country_options[selected_country]
        user_location['city'] = auto_location.get('city', 'Unknown')
        
    with col2:
        st.markdown(f"**Currency:** {user_location['currency']}")
        st.markdown(f"**Detected:** {auto_location['city']}, {auto_location['country']}")
    
    # Update session state
    st.session_state.user_location = user_location
    return user_location


def filter_offers_by_currency(offers, preferred_currency):
    """Filter and sort offers by preferred currency"""
    # Parse all offers and add currency info
    parsed_offers = []
    
    for offer in offers:
        price_amount, price_currency = parse_price(offer.get('price', ''))
        shipping_amount, shipping_currency = parse_price(offer.get('shipping', ''))
        
        # Use price currency as primary
        offer_currency = price_currency
        
        parsed_offer = offer.copy()
        parsed_offer.update({
            'price_amount': price_amount,
            'price_currency': offer_currency,
            'shipping_amount': shipping_amount,
            'total_amount': price_amount + shipping_amount,
            'currency_match': offer_currency == preferred_currency
        })
        parsed_offers.append(parsed_offer)
    
    # Sort: preferred currency first, then by total price
    parsed_offers.sort(key=lambda x: (
        not x['currency_match'],  # Preferred currency first
        x['total_amount']         # Then by total price
    ))
    
    return parsed_offers


def filter_offers_by_condition(offers, high_quality_only=False):
    """Filter offers by condition quality"""
    if not high_quality_only:
        return offers
    
    filtered_offers = []
    for offer in offers:
        condition = offer.get('condition', '')
        
        # Extract main condition (sometimes includes sleeve condition)
        main_condition = condition.split('\n')[0] if '\n' in condition else condition
        main_condition = main_condition.replace('Zustand des Tonträgers: ', '').strip()
        
        if any(hq_condition in main_condition for hq_condition in HIGH_QUALITY_CONDITIONS):
            filtered_offers.append(offer)
    
    return filtered_offers

def search_discogs_offers_simplified(selected_release):
    """Simplified offers display - show offers for selected release"""
    
    # Get user location automatically (no selection UI)
    user_location = get_user_location()
    preferred_currency = user_location['currency']
    
    # Show location info
    st.caption(f"Detected location: {user_location.get('city', 'Unknown')}, {user_location['country']} ({preferred_currency})")
    
    # Add quality toggle
    high_quality_only = st.checkbox(
        "Show only VG+ or better",
        value=False,
        key=f"quality_toggle_{selected_release.get('id', 'unknown')}",
        help="Show only Mint, Near Mint, and Very Good Plus conditions"
    )
    
    # Get release info
    release_id = selected_release.get("id") or selected_release.get("uri", "").split("/")[-1]
    
    if not release_id:
        st.error("Release-ID nicht gefunden.")
        return
    
    # Load offers only if not already cached
    cache_key = f"all_offers_{release_id}"
    
    if cache_key not in st.session_state:
        start_time = time.time()
        # Show loading state only for initial load
        with st.spinner(f"Loading and filtering offers for shipping availability..."):
            try:
                # Use original scraper + Selenium enhancement for shipping/availability
                # PERFORMANCE OPTIMIZATION 4: Reduce max_offers für frühen Exit
                offers = scrape_discogs_marketplace_offers(release_id, max_offers=6, user_country=user_location['country'])
                print(f"Scraper returned {len(offers)} offers")
                
                # Enhance with Selenium using parallel processing for speed
                # Uses 5 parallel browsers to process offers simultaneously for maximum speed
                if offers:
                    offers = selenium_filter_offers_parallel(offers, user_location['country'], max_workers=5)
                    print(f"Selenium parallel filtered to {len(offers)} available offers")

                if not offers:
                    st.info("📭 No marketplace offers found for this release.")
                    return
                
                # Process offers - filter out unavailable ones based on shipping info
                preferred_currency_offers = []
                for i, offer in enumerate(offers):
                    
                    price_amount, price_currency = parse_price(offer.get('price', ''))
                    
                    # Filter currency
                    if price_currency and price_currency != preferred_currency:
                        print(f"Currency mismatch: got {price_currency}, expected {preferred_currency}")
                        continue
                    
                    # Simplified filter: Skip offers without valid total pricing
                    # Unavailable offers often have incomplete pricing information
                    shipping_info = offer.get('shipping', '')
                    
                    # Selenium should have already filtered problematic offers
                    # Only basic validation needed now  
                    if shipping_info == 'N/A' and not offer.get('selenium_enhanced'):
                        print(f"Skipping offer {i+1} - no shipping info and not Selenium-enhanced")
                        continue
                    
                    # Skip offers with suspiciously low prices that might indicate errors
                    if price_amount <= 0:
                        print(f"Skipping offer {i+1} - invalid price: {price_amount}")
                        continue
                    
                    # Parse shipping and calculate total
                    shipping_amount, shipping_currency = parse_price(offer.get('shipping', ''))
                    total_amount = price_amount + shipping_amount
                    
                    # Final validation: Skip offers without meaningful total price
                    if total_amount <= 0 or total_amount > 10000:  # Sanity check for extreme values
                        print(f"Skipping offer {i+1} - invalid total amount: {total_amount}")
                        continue
                    
                    offer_copy = offer.copy()
                    offer_copy.update({
                        'price_amount': price_amount,
                        'price_currency': price_currency,
                        'shipping_amount': shipping_amount,
                        'total_amount': total_amount
                    })
                    preferred_currency_offers.append(offer_copy)
                
                # Store all offers in session state for quality filtering
                st.session_state[cache_key] = preferred_currency_offers
                elapsed_time = time.time() - start_time
                print(f"⏱️ Offers search completed in {elapsed_time:.2f}s - found {len(preferred_currency_offers)} offers")
                
            except Exception as e:
                st.error(f"❌ Error loading offers: {str(e)}")
                return
    
    # Apply quality filter on cached data (no reload, instant filtering)
    try:
        if high_quality_only:
            preferred_currency_offers = filter_offers_by_condition(st.session_state[cache_key], high_quality_only)
        else:
            preferred_currency_offers = st.session_state[cache_key]
        
        # Sort by total price (item + shipping) - Discogs only sorts by item price
        preferred_currency_offers.sort(key=lambda x: x.get('total_amount', 0))
        
        # Display first 5 offers (performance optimization)
        if preferred_currency_offers:
            st.caption(f"Showing first 5 of {len(preferred_currency_offers)} available offers (sorted by lowest total price)")
            for i, offer in enumerate(preferred_currency_offers[:5], 1):
                display_single_offer_clean(offer, i, preferred_currency, selected_release)
        else:
            quality_msg = " in VG+ or better condition" if high_quality_only else ""
            st.info(f"No offers found in {preferred_currency}{quality_msg}.")
    
    except Exception as e:
        st.error(f"❌ Error loading offers: {str(e)}")

def search_discogs_offers(release, selected_release):
    """Search and display Discogs offers for selected release with updated scraper integration"""
    st.markdown("---")
    st.markdown("### 🛒 Discogs Marketplace Offers")
    
    # Get user location preference
    user_location = ask_user_location()
    preferred_currency = user_location['currency']
    
    # Get release info
    release_title = selected_release.get('title', 'Unknown Release')
    release_id = selected_release.get("id") or selected_release.get("uri", "").split("/")[-1]
    
    if not release_id:
        st.error("Release-ID nicht gefunden.")
        return
    
    # Quality filter toggle and controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**Searching offers for:** {release_title}")
    
    with col2:
        high_quality_only = st.checkbox(
            "Only VG+ or better",
            value=False,
            key=f"quality_filter_{release_id}",
            help="Show only Mint, Near Mint, and Very Good Plus conditions"
        )
    
    with col3:
        if st.button("🔄 Refresh Offers", key=f"refresh_{release_id}"):
            # Clear any cached data for this release
            if hasattr(st.session_state, 'marketplace_cache'):
                cache_key = f"{release_id}_15"
                if cache_key in st.session_state.marketplace_cache:
                    del st.session_state.marketplace_cache[cache_key]
    
    # Show loading state
    with st.spinner(f"Searching marketplace offers... (Currency: {preferred_currency})"):
        try:
            # Get offers from production scraper
            offers = scrape_discogs_marketplace_offers(release_id, max_offers=15)
            
            if not offers:
                st.info("📭 No marketplace offers found for this release.")
                return
            
            # Apply filters
            filtered_offers = filter_offers_by_condition(offers, high_quality_only)
            currency_filtered_offers = filter_offers_by_currency(filtered_offers, preferred_currency)
            
            # Display statistics
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            
            with col_stats1:
                st.metric("Total Offers", len(offers))
            
            with col_stats2:
                preferred_currency_count = sum(1 for offer in currency_filtered_offers 
                                             if offer.get('currency_match', False))
                st.metric(f"{preferred_currency} Offers", preferred_currency_count)
            
            with col_stats3:
                if high_quality_only:
                    st.metric("High Quality", len(filtered_offers))
                else:
                    st.metric("After Filters", len(currency_filtered_offers))
            
            # Display offers
            if currency_filtered_offers:
                st.markdown("**📋 Marketplace Offers** (sorted by currency preference & price):")
                
                for i, offer in enumerate(currency_filtered_offers[:15], 1):
                    display_single_offer(offer, i, preferred_currency)
                
                # Show summary of currency distribution
                if len(currency_filtered_offers) > 0:
                    currency_stats = {}
                    for offer in currency_filtered_offers:
                        curr = offer.get('price_currency', 'Unknown')
                        currency_stats[curr] = currency_stats.get(curr, 0) + 1
                    
                    if len(currency_stats) > 1:
                        st.caption(f"💱 Currency distribution: {dict(currency_stats)}")
            
            else:
                if high_quality_only:
                    st.info("🔍 No offers found in VG+ or better condition. Try unchecking the quality filter.")
                else:
                    st.info("📭 No offers match your location preferences.")
        
        except Exception as e:
            st.error(f"❌ Error loading marketplace offers: {str(e)}")
            st.caption("This might be due to rate limiting or connection issues. Try refreshing in a moment.")


def display_single_offer(offer, index, preferred_currency):
    """Display a single marketplace offer"""
    
    # Parse offer data
    price_amount = offer.get('price_amount', 0)
    price_currency = offer.get('price_currency', 'EUR')
    shipping_amount = offer.get('shipping_amount', 0)
    total_amount = offer.get('total_amount', price_amount + shipping_amount)
    
    condition = offer.get('condition', 'Unknown')
    seller = offer.get('seller', 'Unknown')
    seller_rating = offer.get('seller_rating', '')
    country = offer.get('country', '')
    
    # Clean up condition text (remove German labels)
    clean_condition = condition.replace('Zustand des Tonträgers: ', '').replace('Zustand der Hülle: ', ' / ').strip()
    
    # Create offer URL
    offer_url = offer.get('offer_url', '#')
    if offer_url == '#' and seller != 'Unknown':
        offer_url = f"https://www.discogs.com/seller/{seller}"
    
    # Currency preference indicator
    currency_icon = "🎯" if price_currency == preferred_currency else "💱"
    
    # Quality indicator
    quality_score = CONDITION_HIERARCHY.get(clean_condition.split('\n')[0].split(' /')[0], 0)
    if quality_score >= 3:
        quality_icon = "💎"  # High quality
    elif quality_score >= 1:
        quality_icon = "✨"  # Good quality
    else:
        quality_icon = "📦"  # Lower quality
    
    # Format prices - handle string and numeric values
    try:
        price_val = float(price_amount) if price_amount else 0
        price_str = f"{price_val:.2f} {price_currency}"
    except (ValueError, TypeError):
        price_str = f"{price_amount} {price_currency}" if price_amount else f"0.00 {price_currency}"
    
    try:
        shipping_val = float(shipping_amount) if shipping_amount else 0
        shipping_str = f"{shipping_val:.2f} {price_currency}" if shipping_val > 0 else "Free"
    except (ValueError, TypeError):
        shipping_str = str(shipping_amount) if shipping_amount and shipping_amount != "0" else "Free"
    
    try:
        total_val = float(total_amount) if total_amount else (price_val + shipping_val)
        total_str = f"{total_val:.2f} {price_currency}"
    except (ValueError, TypeError):
        total_str = f"{total_amount} {price_currency}" if total_amount else price_str
    
    # Display the offer
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Main offer info
            st.markdown(f"""
            **{index}.** {currency_icon} **[{total_str}]({offer_url})** {quality_icon}  
            📀 *{clean_condition}*  
            👤 *{seller}* {f"({seller_rating})" if seller_rating else ""} {f"🌍 {country}" if country else ""}
            """)
        
        with col2:
            # Price breakdown
            st.markdown(f"""
            💰 **{price_str}**  
            🚚 *+ {shipping_str}*
            """)
        
        # Add separator
        if index < 15:  # Don't add separator after last item
            st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #eee;'>", 
                       unsafe_allow_html=True)

def display_single_offer_clean(offer, index, preferred_currency, selected_release):
    """Display a single marketplace offer without emojis and with correct links"""
    
    # Parse offer data
    price_amount = offer.get('price_amount', 0)
    price_currency = offer.get('price_currency', 'EUR')
    shipping_amount = offer.get('shipping_amount', 0)
    total_amount = offer.get('total_amount', price_amount + shipping_amount)
    
    condition = offer.get('condition', 'Unknown')
    seller = offer.get('seller', 'Unknown')
    seller_rating = offer.get('seller_rating', '')
    country = offer.get('country', '')
    
    # Clean up condition text
    clean_condition = condition.replace('Zustand des Tonträgers: ', '').replace('Zustand der Hülle: ', ' / ').strip()
    
    # Use specific offer URL instead of release URL
    offer_url = offer.get('offer_url', '')
    if not offer_url:
        # Fallback to release URL if offer URL not available
        release_uri = selected_release.get('uri', '')
        offer_url = f"https://www.discogs.com{release_uri}" if release_uri else "#"
    
    # Format prices - handle string and numeric values
    try:
        price_val = float(price_amount) if price_amount else 0
        price_str = f"{price_val:.2f} {price_currency}"
    except (ValueError, TypeError):
        price_str = f"{price_amount} {price_currency}" if price_amount else f"0.00 {price_currency}"
    
    try:
        shipping_val = float(shipping_amount) if shipping_amount else 0
        shipping_str = f"{shipping_val:.2f} {price_currency}" if shipping_val > 0 else "Free"
    except (ValueError, TypeError):
        shipping_str = str(shipping_amount) if shipping_amount and shipping_amount != "0" else "Free"
    
    try:
        total_val = float(total_amount) if total_amount else (price_val + shipping_val)
        total_str = f"{total_val:.2f} {price_currency}"
    except (ValueError, TypeError):
        total_str = f"{total_amount} {price_currency}" if total_amount else price_str
    
    # Display the offer without emojis
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Main offer info without emojis
            st.markdown(f"""
            **{index}.** **[{total_str}]({offer_url})**  
            *{clean_condition}*  
            *{seller}* {f"({seller_rating})" if seller_rating else ""} {f"{country}" if country else ""}
            """)
        
        with col2:
            # Price breakdown
            st.markdown(f"""
            **{price_str}**  
            *+ {shipping_str}*
            """)
        
        # Add separator
        if index < 10:  # Don't add separator after last item
            st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #eee;'>", 
                       unsafe_allow_html=True)

# show_digital_block() function removed - functionality moved to show_live_results()
    
    # COMMENTED OUT: Original duplicate display code
    # PLACEHOLDER_COVER = "cover_placeholder.png"   # neutrales Bild
    # NO_HIT_COVER     = "not_found.png"            # durchgestrichenes Bild
    # 
    # all_results = st.session_state.results_digital
    # user_track  = st.session_state.track_for_search.strip()

    # # Use unified hit detection
    # def is_real_hit(entry):
    #     return is_valid_result(entry, check_empty_title=False)
    # 
    # # real_hits = [
    # #     entry for entry in all_results
    # #     if is_real_hit(entry) and entry.get("platform","").lower() != "itunes"
    # # ]
    # real_hits = [
    #     r for r in st.session_state.results_digital
    #     if (r.get("title") or "").strip().lower() not in ("kein treffer", "", "fehler")
    # ]
    # 
    # any_hit = len(real_hits) > 0
    # 
    # # Display all digital results in order of availability
    # for entry in all_results:
    #     platform_str = entry.get("platform", "")
    #     title_str    = str(entry.get("title", ""))
    #     artist_str   = str(entry.get("artist", ""))
    #     album_str    = str(entry.get("album", ""))
    #     label_raw    = entry.get("label", "")
    #     label_str    = label_raw[0] if isinstance(label_raw, list) and label_raw else str(label_raw)
    #     price_str    = str(entry.get("price", ""))
    #     cover_url    = entry.get("cover_url", "") or entry.get("cover", "")
    #     release_url  = entry.get("url", "").strip()
    #     platform_url, _ = get_platform_info(platform_str)
    # 
    #     # Bildauswahl
    #     if not cover_url or not cover_url.strip():
    #         cover_url = NO_HIT_COVER if not is_real_hit(entry) else PLACEHOLDER_COVER
    # 
    #     # Fuzzy Matching für Beatport
    #     highlight = (platform_str == "Beatport" and is_fuzzy_match(user_track, title_str))
    # 
    #     cols = st.columns([1, 5])
    #     with cols[0]:
    #         st.image(cover_url, width=92)
    #     with cols[1]:
    #         if release_url:
    #             st.markdown(f"[**{platform_str}**]({release_url})", unsafe_allow_html=True)
    #         else:
    #             st.markdown(f"[**{platform_str}**]({platform_url})", unsafe_allow_html=True)
    # 
    #         if highlight:
    #             st.markdown(f":red[**{title_str}**]")
    #         else:
    #             st.markdown(f"**{title_str}**]")
    # 
    #         if artist_str:
    #             st.markdown(f"{artist_str}")
    #         if album_str:
    #             st.markdown(f"*{album_str}*")
    #         if label_str:
    #             st.markdown(f"`{label_str}`")
    #         if price_str and release_url:
    #             st.markdown(f"[{price_str}]({release_url})", unsafe_allow_html=True)
    #         elif price_str:
    #             st.markdown(f":green[{price_str}]")
    #         Preview functionality removed with iTunes
    #             st.audio(entry["preview"], format="audio/mp4")
    # 
    #     st.markdown("---")
    # 
    # # Only show mode switch button when there are digital hits
    # if any_hit:
    #     # Button logic: search vs switch mode
    #     if not st.session_state.get("secondary_search_done", False):
    #         # First time clicking - perform search
    #         if st.button("Search on Discogs and Revibed", key="discogs_search_digital"):
    #             st.session_state.discogs_revibed_mode = True
    #             st.session_state.show_digital         = False
    #             artist  = st.session_state.artist_input.strip()
    #             album   = st.session_state.album_input.strip()
    #             track   = st.session_state.track_for_search.strip()
    #             
    #             # Search is now handled by provider system in main.py
    #             # st.session_state.results_discogs will be set by DiscogsProvider
    #             if album:
    #                 st.session_state.results_revibed = search_revibed('', album)
    #             elif artist:
    #                 st.session_state.results_revibed = search_revibed(artist, '')
    #             else:
    #                 st.session_state.results_revibed = [{
    #                     'platform': 'Revibed',
    #                     'title':'','artist':'','album':'','label':'','price':'',
    #                     'cover_url':'','url':'','search_time':0.0,
    #                     'message': "Für Revibed-Suche mindestens Album ODER Artist ausfüllen."
    #                 }]
    #             
    #             st.session_state.secondary_search_done = True
    #             st.rerun()
    #     else:
    #         # Search already done - just switch view
    #         if st.button("Zu Discogs und Revibed wechseln", key="switch_to_secondary"):
    #             st.session_state.discogs_revibed_mode = True
    #             st.session_state.show_digital         = False
    #             st.rerun()

# Create intensity-based colors for Have/Want like Discogs
def get_intensity_color(count, color_type):
    if count == "-" or count == 0:
        return f":{color_type}[{count}]"
    
    try:
        num = int(count)
        if color_type == "green":  # Have count
            if num < 10:
                return f":green[{count}]"
            elif num < 100:
                return f"**:green[{count}]**"  # Darker green
            else:
                return f"**:green[{count}]**"  # Very dark green
        else:  # Want count - use red instead of orange
            if num < 10:
                return f":red[{count}]"
            elif num < 100:
                return f"**:red[{count}]**"  # Darker red
            else:
                return f"**:red[{count}]**"  # Very dark red
    except:
        return f":{color_type}[{count}]"



def show_discogs_block(releases, track_for_search, is_real_gem=False):
    """Enhanced Discogs block with all features - consolidated from combined version"""
    PLACEHOLDER_COVER = "cover_placeholder.png"
    NO_HIT_COVER = "not_found.png"
    
    # Show real gem message if this is a real gem scenario
    if is_real_gem and releases:
        st.success("🎉 **You found a real gem!** 💎")
        # Auto-play audio using JavaScript with MP3
        try:
            with open("small-applause.mp3", "rb") as audio_file:
                audio_data = audio_file.read()
            import base64
            audio_b64 = base64.b64encode(audio_data).decode()
            
            # Use JavaScript to force audio playback with MP3
            st.markdown(f"""
            <script>
            setTimeout(function() {{
                var audio = new Audio('data:audio/mp3;base64,{audio_b64}');
                audio.volume = 0.7;
                audio.play().catch(function(e) {{
                    console.log('Audio play failed:', e);
                }});
            }}, 200);
            </script>
            """, unsafe_allow_html=True)
            pass  # Audio setup completed
        except Exception as e:
            pass  # Audio setup failed silently
    
    # Enhanced headers on same line (from combined version)
    header_col1, header_col2 = st.columns([1, 1])
    with header_col1:
        st.markdown("#### Discogs Releases")
    with header_col2:
        st.markdown("#### Available offers in your currency")
    
    # Debug info for monitoring (from combined version)
    pass
    
    if releases:
        # Two-column layout: Release info on left, offers on right
        release_col, offers_col = st.columns([1, 1])
        
        with release_col:
            # Initialize state properly to avoid first-load issues
            if "release_selected_idx" not in st.session_state:
                st.session_state.release_selected_idx = 0
                
            # Radio button selection with hidden label for accessibility
            selected_idx = st.radio(
                "Select Release",  # Non-empty label
                options=list(range(len(releases))),
                index=st.session_state.get("release_selected_idx", 0),
                format_func=lambda i: (
                    f"{releases[i].get('title', '-')}"
                    f" – {releases[i].get('label', ['-'])[0] if releases[i].get('label') else '-'}"
                    f" ({releases[i].get('year', '-')})"
                ),
                key="release_select",
                label_visibility="hidden"
            )
            
            # Check if selection changed - ADD RERUN but keep offers persistent
            if selected_idx != st.session_state.get("release_selected_idx", 0):
                pass
                st.session_state.release_selected_idx = selected_idx
                # DON'T reset offers display - let them persist so buttons keep working
                # st.session_state.show_offers = False  # KEEP DISABLED - this was breaking buttons
                # st.session_state.offers_for_release = None  # KEEP DISABLED - this was breaking buttons
                st.rerun()  # Add rerun for immediate radio button response
            else:
                st.session_state.release_selected_idx = selected_idx

            # Cover and details for selected release
            if selected_idx < len(releases):
                r = releases[selected_idx]
                
                # Cover image - API returns cover_image as primary field
                cover_url = r.get("cover_image") or r.get("cover") or r.get("thumb")
                if not cover_url or not cover_url.strip():
                    cover_url = PLACEHOLDER_COVER
                st.image(cover_url, width=200)

                # Detailed metadata
                label_raw = r.get("label", ["-"])
                label_str = label_raw[0] if isinstance(label_raw, list) and label_raw else str(label_raw)
                format_list = r.get("format", [])
                format_str  = ", ".join(format_list) if isinstance(format_list, list) else str(format_list)
                year_str    = r.get("year", "-")
                catno_str   = r.get("catno", "-")
                title_str   = r.get("title", "-")
                url         = r.get("uri") or r.get("url") or ""
                community   = r.get("community", "-")

                # Display detailed info with consistent compact spacing
                st.markdown(f"**{title_str}**  \n**Label:** `{label_str}`  \n**Jahr:** {year_str}  \n**Format:** {format_str}  \n**Katalog:** `{catno_str}`")
                
                # Have/Want ratio - get from API details with caching
                release_id = r.get("id")
                # if release_id:
                #     # Cache release details to avoid repeated API calls
                #     cache_key = f"release_details_{release_id}"
                #     # if cache_key not in st.session_state:
                #     #     try:
                #     #         print(f"Fetching release details for {release_id} (not cached)")
                #     #         details = get_discogs_release_details(release_id)
                #     #         st.session_state[cache_key] = details
                #     #     except Exception as e:
                #     #         print(f"Error getting release details: {e}")
                #     #         st.session_state[cache_key] = {}
                #     # else:
                #     #     print(f"Using cached release details for {release_id}")
                    
                #     details = st.session_state[cache_key]
                #     # community = details.get("community", {})
                #     have_count = community.get("have", r.get("community", {}).get("have", "-"))
                #     want_count = community.get("want", r.get("community", {}).get("want", "-"))
                # else:
                community = r.get("community", {})
                have_count = community.get("have", "-")
                want_count = community.get("want", "-")
                                
                have_color = get_intensity_color(have_count, "green")
                want_color = get_intensity_color(want_count, "red")
                
                # Compact display with consistent line spacing
                search_info = []
                search_info.append(f"**Have/Want:** {have_color}/{want_color}")
                
                if st.session_state.artist_input:
                    search_info.append(f"**Artist:** {st.session_state.artist_input}")
                if st.session_state.album_input:
                    search_info.append(f"**Album:** {st.session_state.album_input}")
                if track_for_search:
                    search_info.append(f"**Track:** {track_for_search}")
                
                if url:
                    search_info.append(f"[Discogs Release →](https://www.discogs.com{url})")
                
                # Display all search info with compact spacing like metadata
                st.markdown("  \n".join(search_info))

        # Show offers in right column using fragment for auto-update
        with offers_col:
            show_offers_fragment(releases, selected_idx)

        # Show full tracklist in the release column
        if selected_idx < len(releases):
            r = releases[selected_idx]
            
            # Get full tracklist from details API with on-demand loading
            release_id = r.get("id")
            if release_id:
                # Load tracklist on-demand when user selects a release
                cache_key = f"release_details_{release_id}"
                if cache_key in st.session_state:
                    details = st.session_state[cache_key]
                    full_tracklist = details.get("tracklist", [])
                else:
                    # Load tracklist details now (on-demand)
                    try:
                        print(f"Loading tracklist details for release {release_id}...")
                        from api_search import get_discogs_release_details
                        details = get_discogs_release_details(release_id)
                        st.session_state[cache_key] = details
                        full_tracklist = details.get("tracklist", [])
                    except Exception as e:
                        print(f"Error loading tracklist: {e}")
                        full_tracklist = []
            else:
                full_tracklist = []
            
            with release_col:
                if full_tracklist:
                    st.markdown("## **Tracklist**")
                    tracklist_text = ""
                    for t in full_tracklist:
                        if isinstance(t, dict):
                            position = t.get("position", "")
                            track_title = t.get("title", "")
                            duration = t.get("duration", "")
                        else:
                            position = ""
                            track_title = str(t)
                            duration = ""
                        
                        # Check if this is the searched track (flexible matching)
                        def is_track_match(search_term, track_title):
                            if not search_term or not track_title:
                                return False
                            
                            # Normalize both strings for comparison
                            search_clean = search_term.lower().strip()
                            track_clean = track_title.lower().strip()
                            
                            # Direct match
                            if search_clean == track_clean:
                                return True
                            
                            # Remove common remix/version suffixes for comparison
                            remix_patterns = [
                                r'\s*\(.*remix.*\)', r'\s*\(.*mix.*\)', r'\s*\(.*edit.*\)',
                                r'\s*\(.*version.*\)', r'\s*\(original\)', r'\s*\(feat\..*\)',
                                r'\s*feat\..*', r'\s*featuring.*', r'\s*ft\..*'
                            ]
                            
                            import re
                            track_base = track_clean
                            search_base = search_clean
                            
                            for pattern in remix_patterns:
                                track_base = re.sub(pattern, '', track_base).strip()
                                search_base = re.sub(pattern, '', search_base).strip()
                            
                            # Check if base versions match
                            if search_base == track_base:
                                return True
                            
                            # Check if search term is contained in track title (partial match)
                            if search_base in track_base or track_base in search_base:
                                return True
                            
                            return False
                        
                        if is_track_match(track_for_search, track_title):
                            # Highlight searched track in red
                            track_line = f"{position} {track_title}" if position else track_title
                            tracklist_text += f":red[**{track_line}**]  \n"
                        else:
                            track_line = f"{position} {track_title}" if position else track_title
                            tracklist_text += f"{track_line}  \n"
                    
                    st.markdown(tracklist_text)
                
                # Show video samples if available
                release_id = r.get("id")
                videos = []
                if release_id:
                    cache_key = f"release_details_{release_id}"
                    if cache_key in st.session_state:
                        details = st.session_state[cache_key]
                        videos = details.get("videos", [])
                
                if videos:
                    st.markdown("## **Video Samples**")
                    
                    # Collect all video links with compact spacing
                    video_links = []
                    for video in videos:
                        video_url = video.get("uri", "")
                        video_title = video.get("title", "Sample")
                        video_duration = video.get("duration", 0)
                        
                        if video_url:
                            # Format duration if available
                            duration_str = f" ({video_duration}s)" if video_duration > 0 else ""
                            
                            # Create clickable link without emoji
                            video_links.append(f"[{video_title}{duration_str}]({video_url})")
                    
                    # Display all video links with compact spacing like metadata
                    if video_links:
                        st.markdown("  \n".join(video_links))
                
                # Move search button below tracklist - back to simple working keys
                search_button_key = f"search_offers_btn_{selected_idx}"
                current_offers_state = st.session_state.get("show_offers", False)
                current_offers_release = st.session_state.get("offers_for_release", None)
                
                if st.button("Search for Offers", key=search_button_key):
                    st.session_state.show_offers = True
                    st.session_state.offers_for_release = selected_idx
                    st.rerun()
                
        st.markdown("---")
    else:
        st.image(NO_HIT_COVER, width=92)
        st.info("Keine Discogs-Releases gefunden.")
        st.warning("Please check your spelling")
    
    # Revibed search button - ALWAYS available, independent of Discogs results
    revibed_button_key = f"search_revibed_btn_global"  # Global key since it's not tied to specific release
    st.markdown("### Revibed Search")
    if st.button("Search on revibed to artist or album", key=revibed_button_key):
        st.session_state.trigger_revibed_search = True
        st.rerun()
    
    # Revibed search handled by main.py handler

# Legacy show_revibed_block() removed - now using unified show_revibed_fragment() everywhere

# Legacy combined function removed - now fully separated into:
# - show_discogs_block() for enhanced Discogs display
# - show_revibed_fragment() for parallel Revibed loading

@st.fragment
def show_offers_fragment(releases, selected_idx):
    """Fragment für Offers-Anzeige - Event-basierte Updates"""
    # Track state changes for immediate updates
    offers_state = st.session_state.get("show_offers", False)
    offers_release = st.session_state.get("offers_for_release", None)
    
    # Only log when state changes to reduce spam
    should_show_offers = (selected_idx < len(releases) and offers_state and offers_release == selected_idx)
    
    if should_show_offers:
        search_discogs_offers_simplified(releases[selected_idx])
    elif selected_idx < len(releases):
        st.info("Click 'Search for Offers' to see marketplace listings")

# Revibed search fragment entfernt - zurück zum Handler-System

@st.fragment
def show_revibed_fragment(revibed_results):
    """Pure Revibed fragment with back button - enables parallel loading"""
    # Check if there are any Revibed hits for display logic
    def is_real_revibed_hit(entry):
        return is_valid_result(entry, check_empty_title=True)
    
    real_revibed_hits = [r for r in revibed_results if is_real_revibed_hit(r)]
    has_revibed_hits = len(real_revibed_hits) > 0
    
    st.markdown("#### Revibed Results")
    
    if has_revibed_hits:
        # Use same layout as digital platforms
        for entry in real_revibed_hits:
            # Extract data
            title_str = str(entry.get("title", ""))
            artist_str = str(entry.get("artist", ""))
            album_str = str(entry.get("album", ""))
            label_str = str(entry.get("label", ""))
            price_str = str(entry.get("price", ""))
            cover_url = entry.get("cover_url", "") or entry.get("cover", "")
            release_url = entry.get("url", "").strip()
            
            # Use placeholder if no cover
            if not cover_url or not cover_url.strip():
                cover_url = "cover_placeholder.png"
            
            # Display result with same columns layout as digital platforms
            cols = st.columns([1, 5])
            with cols[0]:
                st.image(cover_url, width=92)
            with cols[1]:
                if release_url:
                    st.markdown(f"[**Revibed**]({release_url})")
                else:
                    st.markdown("**Revibed**")
                
                if title_str:
                    st.markdown(f"**{title_str}**")
                if artist_str:
                    st.markdown(f"{artist_str}")
                if album_str:
                    st.markdown(f"*{album_str}*")
                if label_str:
                    st.markdown(f"`{label_str}`")
                if price_str and release_url:
                    st.markdown(f"[{price_str}]({release_url})")
                elif price_str:
                    st.markdown(f":green[{price_str}]")
            
            st.markdown("---")
    else:
        # Show no results with same layout as digital platforms
        cols = st.columns([1, 5])
        with cols[0]:
            st.image("not_found.png", width=92)
        with cols[1]:
            st.markdown("**Revibed**")
            st.markdown("Keine Treffer")
        st.markdown("---")

    # Zurück-Button ist jetzt außerhalb des Fragments in main.py implementiert
