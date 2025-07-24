"""
Production-ready Discogs marketplace scraper
Designed to handle anti-bot measures, scaling, and future challenges
"""

import time
import random
import json
import logging
from typing import List, Dict, Optional, Union
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, quote
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import threading
from functools import wraps
import hashlib


# Configuration class for easy maintenance
@dataclass
class ScraperConfig:
    """Configuration class for the Discogs scraper"""
    # Rate limiting
    min_delay: float = 2.0
    max_delay: float = 5.0
    request_timeout: int = 15
    
    # Retry settings
    max_retries: int = 3
    backoff_factor: float = 2.0
    
    # Browser settings
    headless: bool = True
    window_size: tuple = (1920, 1080)
    page_load_timeout: int = 30
    
    # Anti-bot measures
    rotate_user_agents: bool = True
    use_random_delays: bool = True
    simulate_human_behavior: bool = True
    
    # Proxy settings (for scaling)
    use_proxies: bool = False
    proxy_list: List[str] = None
    
    # Location settings
    user_country: str = "DE"
    
    # Caching
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    # Limits
    max_offers_per_release: int = 20
    max_concurrent_sessions: int = 3


class DiscogsScraper:
    """Production-ready Discogs marketplace scraper"""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.session_lock = threading.Lock()
        self.active_sessions = 0
        self.cache = {}
        self.setup_logging()
        
        # User agent rotation for anti-bot measures
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Robust CSS selectors with fallbacks
        self.selectors = {
            'marketplace_offers': [
                'table.mpitems tr.shortcut_navigable',
                '.marketplace_box .shortcut_navigable',
                'tr[data-item-id]',
                '.mpitems tr'
            ],
            'price': [
                '.price span.converted_price',
                '.price .price',
                'td.item_price .price',
                '.converted_price',
                '.price'
            ],
            'condition': [
                '.item_condition',
                'td.item_condition',
                '.condition'
            ],
            'seller': [
                '.seller_info a',
                '.seller a',
                'td.seller_info a'
            ],
            'shipping': [
                '.item_shipping .price',
                '.shipping_price',
                'td.item_shipping'
            ]
        }
    
    def setup_logging(self):
        """Setup logging for debugging and monitoring"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('discogs_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def rate_limit_decorator(func):
        """Decorator to apply rate limiting"""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.config.use_random_delays:
                delay = random.uniform(self.config.min_delay, self.config.max_delay)
                time.sleep(delay)
            return func(self, *args, **kwargs)
        return wrapper
    
    def get_cache_key(self, **kwargs) -> str:
        """Generate cache key from parameters"""
        key_data = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get data from cache if available and not expired"""
        if not self.config.enable_cache:
            return None
            
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.config.cache_ttl:
                self.logger.info(f"Cache hit for key: {cache_key[:8]}...")
                return data
            else:
                del self.cache[cache_key]
        return None
    
    def set_cache(self, cache_key: str, data: Dict):
        """Store data in cache"""
        if self.config.enable_cache:
            self.cache[cache_key] = (data, time.time())
    
    def create_driver(self) -> webdriver.Chrome:
        """Create a Chrome WebDriver with anti-bot measures"""
        options = Options()
        
        if self.config.headless:
            options.add_argument('--headless=new')
        
        # Anti-bot measures
        options.add_argument(f'--window-size={self.config.window_size[0]},{self.config.window_size[1]}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        if self.config.rotate_user_agents:
            user_agent = random.choice(self.user_agents)
            options.add_argument(f'--user-agent={user_agent}')
        
        # Proxy support for scaling
        if self.config.use_proxies and self.config.proxy_list:
            proxy = random.choice(self.config.proxy_list)
            options.add_argument(f'--proxy-server={proxy}')
        
        try:
            # Use webdriver-manager for automatic ChromeDriver management
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            except ImportError:
                # Fallback to system ChromeDriver
                driver = webdriver.Chrome(options=options)
            
            driver.set_page_load_timeout(self.config.page_load_timeout)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
        except Exception as e:
            self.logger.error(f"Failed to create driver: {e}")
            raise
    
    def find_element_with_fallback(self, driver, selectors: List[str], parent=None) -> Optional:
        """Try multiple selectors with fallback"""
        search_context = parent or driver
        
        for selector in selectors:
            try:
                element = search_context.find_element(By.CSS_SELECTOR, selector)
                return element
            except NoSuchElementException:
                continue
        return None
    
    def find_elements_with_fallback(self, driver, selectors: List[str], parent=None) -> List:
        """Try multiple selectors with fallback for multiple elements"""
        search_context = parent or driver
        
        for selector in selectors:
            try:
                elements = search_context.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return elements
            except NoSuchElementException:
                continue
        return []
    
    def simulate_human_behavior(self, driver):
        """Simulate human-like behavior"""
        if not self.config.simulate_human_behavior:
            return
            
        # Random scroll
        scroll_height = random.randint(100, 500)
        driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(random.uniform(0.5, 1.5))
        
        # Random mouse movement (using JavaScript)
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        driver.execute_script(f"""
            var event = new MouseEvent('mousemove', {{
                'clientX': {x},
                'clientY': {y}
            }});
            document.dispatchEvent(event);
        """)
    
    @rate_limit_decorator
    def scrape_marketplace_offers(self, release_id: str, max_offers: Optional[int] = None) -> Dict:
        """
        Scrape marketplace offers for a Discogs release
        
        Args:
            release_id: Discogs release ID
            max_offers: Maximum number of offers to return
            
        Returns:
            Dictionary with offers and metadata
        """
        max_offers = max_offers or self.config.max_offers_per_release
        cache_key = self.get_cache_key(release_id=release_id, max_offers=max_offers)
        
        # Check cache first
        cached_result = self.get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Check concurrent session limit
        with self.session_lock:
            if self.active_sessions >= self.config.max_concurrent_sessions:
                self.logger.warning("Max concurrent sessions reached, waiting...")
                time.sleep(random.uniform(5, 10))
            self.active_sessions += 1
        
        driver = None
        try:
            driver = self.create_driver()
            # Include user country for localized shipping calculations
            marketplace_url = f"https://www.discogs.com/sell/list?release_id={release_id}&ev=rb&country={self.config.user_country}"
            
            self.logger.info(f"Scraping offers for release {release_id}")
            driver.get(marketplace_url)
            
            # Wait for page to load and simulate human behavior
            time.sleep(random.uniform(2, 4))
            self.simulate_human_behavior(driver)
            
            # Wait for marketplace offers to load
            wait = WebDriverWait(driver, self.config.request_timeout)
            
            # Try to find offers with fallback selectors
            offer_elements = self.find_elements_with_fallback(
                driver, self.selectors['marketplace_offers']
            )
            
            if not offer_elements:
                self.logger.warning(f"No offers found for release {release_id}")
                result = {
                    'release_id': release_id,
                    'offers': [],
                    'total_offers': 0,
                    'scraped_at': time.time(),
                    'status': 'no_offers_found'
                }
                self.set_cache(cache_key, result)
                return result
            
            offers = []
            for i, offer_element in enumerate(offer_elements[:max_offers]):
                try:
                    offer_data = self.extract_offer_data(driver, offer_element)
                    if offer_data:
                        offers.append(offer_data)
                except Exception as e:
                    self.logger.warning(f"Failed to extract offer {i}: {e}")
                    continue
            
            result = {
                'release_id': release_id,
                'offers': offers,
                'total_offers': len(offers),
                'scraped_at': time.time(),
                'status': 'success'
            }
            
            self.set_cache(cache_key, result)
            self.logger.info(f"Successfully scraped {len(offers)} offers for release {release_id}")
            
            return result
            
        except TimeoutException:
            self.logger.error(f"Timeout scraping release {release_id}")
            return {
                'release_id': release_id,
                'offers': [],
                'total_offers': 0,
                'scraped_at': time.time(),
                'status': 'timeout_error'
            }
        except Exception as e:
            self.logger.error(f"Error scraping release {release_id}: {e}")
            return {
                'release_id': release_id,
                'offers': [],
                'total_offers': 0,
                'scraped_at': time.time(),
                'status': 'scraping_error',
                'error': str(e)
            }
        finally:
            if driver:
                driver.quit()
            with self.session_lock:
                self.active_sessions -= 1
    
    def extract_offer_data(self, driver, offer_element) -> Optional[Dict]:
        """Extract offer data from a single offer element"""
        try:
            offer = {}
            
            # Extract price
            price_element = self.find_element_with_fallback(
                driver, self.selectors['price'], offer_element
            )
            offer['price'] = price_element.text.strip() if price_element else 'N/A'
            
            # Extract condition
            condition_element = self.find_element_with_fallback(
                driver, self.selectors['condition'], offer_element
            )
            offer['condition'] = condition_element.text.strip() if condition_element else 'N/A'
            
            # Extract seller
            seller_element = self.find_element_with_fallback(
                driver, self.selectors['seller'], offer_element
            )
            if seller_element:
                offer['seller'] = seller_element.text.strip()
                offer['seller_url'] = seller_element.get_attribute('href')
            else:
                offer['seller'] = 'N/A'
                offer['seller_url'] = ''
            
            # Extract shipping
            shipping_element = self.find_element_with_fallback(
                driver, self.selectors['shipping'], offer_element
            )
            offer['shipping'] = shipping_element.text.strip() if shipping_element else 'N/A'
            
            # Extract offer URL - look for specific Discogs marketplace patterns
            offer_url = ''
            try:
                # Multiple strategies to find the offer URL
                
                # Strategy 1: Look for "Add to Cart" or "Buy Now" buttons with data attributes
                try:
                    buy_button = offer_element.find_element(By.CSS_SELECTOR, 'button.btn_add_to_cart, button[data-offer-id], input[data-offer-id]')
                    offer_id = buy_button.get_attribute('data-offer-id') or buy_button.get_attribute('data-item-id')
                    if offer_id:
                        offer_url = f"https://www.discogs.com/sell/item/{offer_id}"
                        self.logger.info(f"Found offer URL via button data-offer-id: {offer_url}")
                except NoSuchElementException:
                    pass
                
                # Strategy 2: Look for marketplace item links
                if not offer_url:
                    try:
                        marketplace_link = offer_element.find_element(By.CSS_SELECTOR, 'a[href*="/sell/item/"], a[href*="/marketplace/item/"]')
                        offer_url = marketplace_link.get_attribute('href')
                        if offer_url and not offer_url.startswith('http'):
                            offer_url = f"https://www.discogs.com{offer_url}"
                        self.logger.info(f"Found offer URL via marketplace link: {offer_url}")
                    except NoSuchElementException:
                        pass
                
                # Strategy 3: Look for any form with offer data
                if not offer_url:
                    try:
                        form = offer_element.find_element(By.CSS_SELECTOR, 'form[action*="cart"], form[data-offer]')
                        action = form.get_attribute('action')
                        if action:
                            offer_url = action if action.startswith('http') else f"https://www.discogs.com{action}"
                            self.logger.info(f"Found offer URL via form action: {offer_url}")
                    except NoSuchElementException:
                        pass
                        
                # Strategy 4: Extract from JavaScript or data attributes
                if not offer_url:
                    try:
                        # Look for data attributes that might contain offer info
                        data_attrs = ['data-listing-id', 'data-item-id', 'data-offer', 'id']
                        for attr in data_attrs:
                            offer_id = offer_element.get_attribute(attr)
                            if offer_id and offer_id.isdigit():
                                offer_url = f"https://www.discogs.com/sell/item/{offer_id}"
                                self.logger.info(f"Found offer URL via {attr}: {offer_url}")
                                break
                    except:
                        pass
                        
            except Exception as e:
                self.logger.warning(f"Error extracting offer URL: {e}")
                offer_url = ''
            
            offer['offer_url'] = offer_url
            
            # Additional metadata
            offer['scraped_at'] = time.time()
            
            return offer
            
        except Exception as e:
            self.logger.warning(f"Failed to extract offer data: {e}")
            return None
    
    def bulk_scrape_offers(self, release_ids: List[str], max_offers_per_release: int = 10) -> Dict[str, Dict]:
        """
        Scrape offers for multiple releases with intelligent batching
        
        Args:
            release_ids: List of Discogs release IDs
            max_offers_per_release: Max offers per release
            
        Returns:
            Dictionary mapping release_id to offers data
        """
        results = {}
        
        for i, release_id in enumerate(release_ids):
            self.logger.info(f"Processing release {i+1}/{len(release_ids)}: {release_id}")
            
            try:
                result = self.scrape_marketplace_offers(release_id, max_offers_per_release)
                results[release_id] = result
                
                # Add longer delay between releases to be respectful
                if i < len(release_ids) - 1:
                    delay = random.uniform(self.config.max_delay, self.config.max_delay * 2)
                    self.logger.info(f"Waiting {delay:.1f}s before next release...")
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"Failed to process release {release_id}: {e}")
                results[release_id] = {
                    'release_id': release_id,
                    'offers': [],
                    'total_offers': 0,
                    'scraped_at': time.time(),
                    'status': 'error',
                    'error': str(e)
                }
        
        return results
    
    def search_and_scrape(self, artist: str = None, track: str = None, album: str = None, 
                         catno: str = None, max_offers: int = 10) -> Dict:
        """
        Search for releases and scrape marketplace offers
        
        Args:
            artist: Artist name
            track: Track title
            album: Album title
            catno: Catalog number
            max_offers: Max offers to return
            
        Returns:
            Combined search and marketplace data
        """
        # First search for releases using existing API function
        try:
            from api_search import search_discogs_releases
            releases = search_discogs_releases(artist, track, album, catno)
            
            if not releases:
                return {
                    'search_results': [],
                    'marketplace_data': {},
                    'status': 'no_releases_found'
                }
            
            # Get marketplace offers for the first release
            first_release = releases[0]
            release_id = first_release.get('id')
            
            marketplace_data = {}
            if release_id:
                marketplace_data = self.scrape_marketplace_offers(release_id, max_offers)
            
            return {
                'search_results': releases,
                'marketplace_data': marketplace_data,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Error in search_and_scrape: {e}")
            return {
                'search_results': [],
                'marketplace_data': {},
                'status': 'error',
                'error': str(e)
            }
    
    def update_selectors(self, new_selectors: Dict[str, List[str]]):
        """Update CSS selectors for maintenance when Discogs changes their structure"""
        self.selectors.update(new_selectors)
        self.logger.info("CSS selectors updated")
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        self.logger.info("Cache cleared")
    
    def get_stats(self) -> Dict:
        """Get scraper statistics"""
        return {
            'cache_size': len(self.cache),
            'active_sessions': self.active_sessions,
            'config': asdict(self.config)
        }


# Factory function for easy integration
def create_discogs_scraper(headless: bool = True, enable_cache: bool = True, 
                          use_proxies: bool = False, proxy_list: List[str] = None,
                          user_country: str = "DE") -> DiscogsScraper:
    """
    Factory function to create a configured Discogs scraper
    
    Args:
        headless: Run browser in headless mode
        enable_cache: Enable caching
        use_proxies: Use proxy rotation
        proxy_list: List of proxy servers
        user_country: User's country code for shipping calculations
        
    Returns:
        Configured DiscogsScraper instance
    """
    config = ScraperConfig(
        headless=headless,
        enable_cache=enable_cache,
        use_proxies=use_proxies,
        proxy_list=proxy_list or [],
        user_country=user_country
    )
    
    return DiscogsScraper(config)


# Integration function for the existing codebase
def scrape_discogs_offers_integrated(release_id: str, max_offers: int = 10) -> List[Dict]:
    """
    Simple function for integration with existing codebase
    Returns just the offers list for compatibility
    """
    scraper = create_discogs_scraper()
    result = scraper.scrape_marketplace_offers(release_id, max_offers)
    return result.get('offers', [])


if __name__ == "__main__":
    # Example usage
    scraper = create_discogs_scraper()
    
    # Test scraping offers for a release
    result = scraper.scrape_marketplace_offers("12345", max_offers=5)
    print(json.dumps(result, indent=2))
    
    # Test combined search and scrape
    combined_result = scraper.search_and_scrape(
        artist="discogs artist", 
        track="vintage track", 
        max_offers=5
    )
    print(json.dumps(combined_result, indent=2))