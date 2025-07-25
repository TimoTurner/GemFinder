"""
Selenium-based Discogs marketplace scraper to bypass 403 blocking
Uses real browser automation for individual offer page access
"""
import time
import re
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available - falling back to basic filtering")

def create_selenium_driver(headless: bool = True, aggressive: bool = True) -> webdriver.Chrome:
    """Create optimized Chrome driver for fast Discogs scraping"""
    options = Options()
    
    if headless:
        options.add_argument('--headless=new')
    
    # Performance optimizations
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-ipc-flooding-protection')
    
    # Disable unnecessary features for speed
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')  # Don't load images for faster loading
    options.add_argument('--disable-javascript')  # We only need HTML structure
    options.add_argument('--disable-css')  # Don't need CSS styling
    
    # Anti-detection measures (minimal)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Faster browser settings
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    options.add_argument('--window-size=1280,720')  # Smaller window for speed
    options.add_argument('--lang=en-US')
    
    # Page load strategy - keep 'eager' for reliability 
    options.page_load_strategy = 'eager'  # Don't wait for all resources but ensure HTML is loaded
    if aggressive:
        print("Selenium: Using AGGRESSIVE timeouts with 'eager' page load strategy")
    else:
        print("Selenium: Using SAFE mode")
    
    driver = webdriver.Chrome(options=options)
    
    # Set timeouts based on mode - but keep them reasonable for data extraction
    if aggressive:
        driver.set_page_load_timeout(2)    # Aggressive but not too risky: 2 seconds
        driver.implicitly_wait(0.3)        # Aggressive: 0.3 seconds
    else:
        driver.set_page_load_timeout(3)    # Conservative: 3 seconds
        driver.implicitly_wait(0.5)        # Conservative: 0.5 seconds
    
    # Remove automation indicators
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def selenium_extract_offer_details(offer_url: str, user_country: str = "DE") -> Optional[Dict]:
    """
    Extract shipping and availability details from individual offer page using Selenium
    (Creates new browser session - use selenium_extract_offer_details_with_driver for reuse)
    
    Args:
        offer_url: Full URL to the Discogs offer page
        user_country: User's country code for availability checking
        
    Returns:
        Dict with availability and shipping info, or None if unavailable
    """
    driver = None
    try:
        driver = create_selenium_driver(headless=True)
        return selenium_extract_offer_details_with_driver(driver, offer_url, user_country)
    finally:
        if driver:
            driver.quit()

def selenium_extract_offer_details_with_driver(driver, offer_url: str, user_country: str = "DE") -> Optional[Dict]:
    """
    Extract shipping and availability details using existing driver (for browser reuse)
    
    Args:
        driver: Existing Selenium WebDriver instance
        offer_url: Full URL to the Discogs offer page
        user_country: User's country code for availability checking
        
    Returns:
        Dict with availability and shipping info, or None if unavailable
    """
    try:
        print(f"Selenium: Accessing {offer_url}")
        start_time = time.time()
        driver.get(offer_url)
        
        # Wait for page content - using eager strategy means HTML is ready
        try:
            wait = WebDriverWait(driver, 1)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except TimeoutException:
            # Continue anyway 
            pass
        
        # Check for availability restrictions first
        country_name = get_country_name(user_country)
        
        # Quick check for German availability restrictions first (fastest method)
        try:
            unavailable_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'nicht erhältlich') or contains(text(), 'not available') or contains(text(), 'Unavailable')]")
            for element in unavailable_elements:
                element_text = element.text.strip()
                if f'{country_name.lower()}' in element_text.lower() or 'germany' in element_text.lower():
                    print(f"Selenium: Found availability restriction: {element_text}")
                    return None  # Filter out unavailable offers
        except Exception:
            pass  # Continue if availability check fails
        
        # Extract shipping information
        shipping_info = extract_shipping_with_selenium(driver, user_country)
        
        extraction_time = time.time() - start_time
        result = {
            'available': True,
            'shipping_cost': shipping_info.get('shipping_cost', 'Unknown'),
            'shipping_amount': shipping_info.get('shipping_amount', 0.0),
            'extraction_method': 'selenium',
            'extraction_time': extraction_time
        }
        
        print(f"Selenium: Extracted shipping - {result['shipping_cost']} ({extraction_time:.2f}s)")
        return result
        
    except TimeoutException:
        print("Selenium: Page load timeout")
        return {'available': True, 'shipping_cost': 'Unknown', 'shipping_amount': 0.0}
        
    except Exception as e:
        print(f"Selenium: Error extracting offer details - {e}")
        return {'available': True, 'shipping_cost': 'Unknown', 'shipping_amount': 0.0}

def extract_shipping_with_selenium(driver, user_country: str = "DE") -> Dict:
    """Extract shipping cost using Selenium element selection - focused on pricing areas only"""
    try:
        print("Selenium: Looking for shipping information in pricing areas...")
        
        # Strategy 1: Look for the specific 'reduced' span that contains shipping info
        try:
            # This is where Discogs shows the shipping cost: <span class='reduced'>+ €2,49 Versand</span>
            reduced_spans = driver.find_elements(By.CSS_SELECTOR, 'span.reduced')
            for span in reduced_spans:
                span_text = span.text.strip()
                # Skip empty spans immediately
                if not span_text:
                    continue
                # Only log non-empty spans
                print(f"Selenium: Found shipping span: '{span_text}'")
                if '+' in span_text and ('versand' in span_text.lower() or 'shipping' in span_text.lower()):
                    result = parse_selenium_shipping(span_text, user_country)
                    if result.get('shipping_cost') != 'Unknown':
                        return result
        except Exception as e:
            print(f"Selenium: Error scanning reduced spans: {e}")
        
        # Strategy 2: Look in table cells that contain pricing info
        try:
            # Look for table cells that contain pricing info
            price_cells = driver.find_elements(By.CSS_SELECTOR, 'td.item_price')
            for cell in price_cells:
                cell_text = cell.text.strip()
                print(f"Selenium: Price cell text: '{cell_text}'")
                
                # Look for shipping spans within price cells
                shipping_spans = cell.find_elements(By.CSS_SELECTOR, 'span.hide_mobile, span.reduced')
                for span in shipping_spans:
                    span_text = span.text.strip()
                    print(f"Selenium: Shipping span text: '{span_text}'")
                    if span_text and ('+' in span_text or 'shipping' in span_text.lower() or 'versand' in span_text.lower()):
                        result = parse_selenium_shipping(span_text)
                        if result.get('shipping_cost') != 'Unknown':
                            return result
        except Exception as e:
            print(f"Selenium: Error scanning price cells: {e}")
        
        # Strategy 2: Look for the pricing_info paragraph specifically  
        try:
            pricing_paragraphs = driver.find_elements(By.CSS_SELECTOR, 'p.pricing_info.muted')
            for p in pricing_paragraphs:
                p_text = p.text.strip()
                print(f"Selenium: Pricing paragraph: '{p_text}'")
                
                # Only process if it's short (not terms and conditions)
                if len(p_text) < 200 and ('+' in p_text or 'shipping' in p_text.lower()):
                    result = parse_selenium_shipping(p_text)
                    if result.get('shipping_cost') != 'Unknown':
                        return result
        except Exception as e:
            print(f"Selenium: Error scanning pricing paragraphs: {e}")
        
        # Strategy 3: Look for the actual offer buttons/actions area
        # This is where the add to cart functionality is, so shipping should be nearby
        try:
            offer_sections = driver.find_elements(By.CSS_SELECTOR, '.offer_actions, .inline-buttons')
            for section in offer_sections:
                section_text = section.text.strip()
                print(f"Selenium: Offer section: '{section_text[:100]}...'")
                
                # Look for shipping info in this section
                if len(section_text) < 500:  # Avoid long legal text
                    result = parse_selenium_shipping(section_text)
                    if result.get('shipping_cost') != 'Unknown':
                        return result
        except Exception as e:
            print(f"Selenium: Error scanning offer sections: {e}")
        
        # Strategy 4: Targeted XPath for price-related shipping only
        shipping_xpaths = [
            "//td[@class='item_price']//span[contains(text(), '+')]",
            "//p[@class='pricing_info']//span[contains(text(), '€') and string-length(text()) < 50]",
            "//*[contains(@class, 'price') and contains(text(), '+')]"
        ]
        
        for xpath in shipping_xpaths:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                for element in elements:
                    text = element.text.strip()
                    print(f"Selenium: XPath element: '{text}'")
                    if text and len(text) < 50:  # Short text only
                        result = parse_selenium_shipping(text)
                        if result.get('shipping_cost') != 'Unknown':
                            return result
            except Exception as e:
                print(f"Selenium: Error with XPath {xpath}: {e}")
                continue
        
        print("Selenium: No shipping information found in pricing areas")
        return {'shipping_cost': 'Unknown', 'shipping_amount': 0.0}
        
    except Exception as e:
        print(f"Selenium shipping extraction error: {e}")
        return {'shipping_cost': 'Unknown', 'shipping_amount': 0.0}

def parse_selenium_shipping(shipping_text: str, user_country: str = "DE") -> Dict:
    """Parse shipping cost from extracted text - strict validation to avoid item prices"""
    if not shipping_text:
        return {'shipping_cost': 'Unknown', 'shipping_amount': 0.0}
    
    print(f"Selenium: Parsing shipping text: '{shipping_text}'")
    
    # Check for free shipping
    free_indicators = ['free', 'kostenlos', 'gratis', 'free shipping', 'kostenloser versand']
    if any(indicator in shipping_text.lower() for indicator in free_indicators):
        print("Selenium: Found free shipping")
        return {'shipping_cost': 'Free', 'shipping_amount': 0.0}
    
    # Only extract if text contains clear shipping indicators
    shipping_indicators = ['+', 'shipping', 'versand', 'plus']
    has_shipping_indicator = any(indicator in shipping_text.lower() for indicator in shipping_indicators)
    
    if not has_shipping_indicator:
        print(f"Selenium: No shipping indicators found in '{shipping_text}'")
        return {'shipping_cost': 'Unknown', 'shipping_amount': 0.0}
    
    # Get expected currency based on user country
    expected_currencies = get_expected_currencies(user_country)
    
    # Build patterns dynamically based on user's currency zone
    patterns = []
    
    # Add patterns for each expected currency
    for currency_symbol, currency_code in expected_currencies:
        if currency_symbol == '€':
            patterns.extend([
                rf'\+\s*{re.escape(currency_symbol)}\s*(\d+[,.]?\d*)\s*versand',  # + €2,49 Versand
                rf'\+\s*{re.escape(currency_symbol)}\s*(\d+[,.]?\d*)\s*shipping',  # + €2.50 shipping
                rf'\+\s*{re.escape(currency_symbol)}\s*(\d+[,.]?\d*)',  # + €2.50
            ])
        else:
            patterns.extend([
                rf'\+\s*{re.escape(currency_symbol)}\s*(\d+[,.]?\d*)\s*shipping',  # + $2.50 shipping
                rf'\+\s*{re.escape(currency_symbol)}\s*(\d+[,.]?\d*)',  # + $2.50
            ])
    
    # Add generic fallback patterns
    patterns.extend([
        r'\+\s*(\d+[,.]?\d*)\s*€\s*versand',  # + 2,49 € Versand
        r'shipping[:\s]*[€$£]\s*(\d+[,.]?\d*)',  # shipping: €2.50
    ])
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, shipping_text, re.IGNORECASE)
        if match:
            try:
                amount = float(match.group(1).replace(',', '.'))
                
                # Detect currency from the text
                if '€' in shipping_text:
                    currency = '€'
                elif '$' in shipping_text:
                    currency = '$'
                elif '£' in shipping_text:
                    currency = '£'
                elif '¥' in shipping_text:
                    currency = '¥'
                else:
                    # Use first expected currency for user's country
                    expected = get_expected_currencies(user_country)
                    currency = expected[0][0] if expected else '€'
                
                print(f"Selenium: Extracted shipping with pattern {i+1}: {currency}{amount:.2f}")
                return {
                    'shipping_cost': f'{currency}{amount:.2f}',
                    'shipping_amount': amount
                }
            except ValueError:
                continue
    
    print(f"Selenium: Could not extract shipping amount from '{shipping_text}'")
    return {'shipping_cost': 'Unknown', 'shipping_amount': 0.0}

def parse_shipping_from_text(html_content: str) -> Dict:
    """Fallback: parse shipping from raw HTML content with better patterns"""
    print("Selenium: Parsing shipping from page source...")
    
    # More specific patterns that avoid item prices
    patterns = [
        r'\+\s*€\s*(\d+[,.]?\d*)\s*shipping',  # + €2.50 shipping
        r'\+\s*(\d+[,.]?\d*)\s*€\s*shipping',  # + 2.50 € shipping  
        r'shipping[:\s]*\+?\s*€\s*(\d+[,.]?\d*)',  # shipping: €2.50
        r'versand[:\s]*\+?\s*€\s*(\d+[,.]?\d*)',  # versand: €2.50
        r'<span[^>]*shipping[^>]*>.*?€\s*(\d+[,.]?\d*)',  # <span class="shipping">€2.50</span>
        r'item_shipping[^>]*>.*?€\s*(\d+[,.]?\d*)',  # item_shipping class content
    ]
    
    for i, pattern in enumerate(patterns):
        matches = re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            try:
                amount = float(match.group(1).replace(',', '.'))
                print(f"Selenium: Found shipping with pattern {i+1}: €{amount:.2f}")
                return {
                    'shipping_cost': f'€{amount:.2f}',
                    'shipping_amount': amount
                }
            except ValueError:
                continue
    
    # Check for free shipping indicators
    free_patterns = [
        'free shipping', 'kostenloser versand', 'gratis versand',
        'shipping.*free', 'versand.*kostenlos'
    ]
    for pattern in free_patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            print("Selenium: Found free shipping in page source")
            return {'shipping_cost': 'Free', 'shipping_amount': 0.0}
    
    print("Selenium: No shipping information found in page source")
    return {'shipping_cost': 'Unknown', 'shipping_amount': 0.0}

def get_country_name(country_code: str) -> str:
    """Convert country code to full name"""
    country_mapping = {
        'DE': 'Germany',
        'US': 'United States',
        'GB': 'United Kingdom', 
        'FR': 'France',
        'NL': 'Netherlands',
        'CA': 'Canada',
        'AU': 'Australia',
        'CH': 'Switzerland'
    }
    return country_mapping.get(country_code.upper(), country_code)

def get_expected_currencies(country_code: str) -> list:
    """Get expected currency symbols for a country"""
    currency_mapping = {
        # Eurozone countries
        'DE': [('€', 'EUR')], 'FR': [('€', 'EUR')], 'NL': [('€', 'EUR')], 
        'IT': [('€', 'EUR')], 'ES': [('€', 'EUR')], 'AT': [('€', 'EUR')],
        
        # Other major currencies
        'US': [('$', 'USD')], 'CA': [('CA$', 'CAD'), ('$', 'CAD')],
        'GB': [('£', 'GBP')], 'AU': [('AU$', 'AUD'), ('$', 'AUD')],
        'CH': [('CHF', 'CHF')], 'JP': [('¥', 'JPY')],
        
        # Default fallback
        'DEFAULT': [('€', 'EUR'), ('$', 'USD'), ('£', 'GBP')]
    }
    
    return currency_mapping.get(country_code.upper(), currency_mapping['DEFAULT'])

def selenium_filter_offers(offers: List[Dict], user_country: str) -> List[Dict]:
    """
    Filter offers using Selenium-based individual page access with browser reuse
    
    Args:
        offers: List of offers from main marketplace scraper
        user_country: User's country code
        
    Returns:
        Filtered list of available offers with enhanced shipping data
    """
    if not offers:
        return []
    
    if not SELENIUM_AVAILABLE:
        print("Selenium not available - returning offers without enhancement")
        return offers
    
    enhanced_offers = []
    offers_to_process = []
    
    # First pass: identify offers that need enhancement
    for offer in offers:
        needs_enhancement = (
            offer.get('shipping') == 'N/A' or 
            not offer.get('shipping') or
            offer.get('shipping', '').strip() == ''
        )
        
        if needs_enhancement and offer.get('offer_url'):
            offers_to_process.append(offer)
        else:
            enhanced_offers.append(offer)
    
    if not offers_to_process:
        return enhanced_offers
    
    print(f"Selenium: Processing {len(offers_to_process)} offers with reused browser session")
    
    # Create a single browser session for all offers
    driver = None
    try:
        driver = create_selenium_driver(headless=True)
        
        for i, offer in enumerate(offers_to_process):
            print(f"Selenium: Enhancing offer {i+1}/{len(offers_to_process)}")
            
            try:
                details = selenium_extract_offer_details_with_driver(driver, offer.get('offer_url'), user_country)
                
                if details is None:
                    # Offer is not available, skip it
                    print(f"Selenium: Offer {i+1} not available in {user_country}")
                    continue
                
                # Enhance offer with Selenium data
                enhanced = offer.copy()
                if details.get('shipping_cost', 'Unknown') != 'Unknown':
                    enhanced['shipping'] = details['shipping_cost']
                    enhanced['shipping_amount'] = details.get('shipping_amount', 0.0)
                    enhanced['total_amount'] = enhanced.get('price_amount', 0) + details.get('shipping_amount', 0.0)
                    enhanced['selenium_enhanced'] = True
                
                enhanced_offers.append(enhanced)
            except Exception as e:
                print(f"Selenium: Error processing offer {i+1}: {e}")
                # On error, keep original offer
                enhanced_offers.append(offer)
            
            # No delay needed with browser reuse
        
    finally:
        if driver:
            driver.quit()
    
    print(f"Selenium: Filtered to {len(enhanced_offers)} available offers")
    return enhanced_offers

def selenium_filter_offers_parallel(offers: List[Dict], user_country: str, max_workers: int = 3) -> List[Dict]:
    """
    Filter offers using parallel Selenium processing for maximum speed
    Sorts by price first to ensure cheapest offers are processed first
    
    Args:
        offers: List of offers from main marketplace scraper
        user_country: User's country code
        max_workers: Number of parallel browser sessions (default 3)
        
    Returns:
        Filtered list of available offers with enhanced shipping data
    """
    if not offers:
        return []
    
    if not SELENIUM_AVAILABLE:
        print("Selenium not available - returning offers without enhancement")
        return offers
    
    enhanced_offers = []
    offers_to_process = []
    
    # First pass: identify offers that need enhancement
    for offer in offers:
        needs_enhancement = (
            offer.get('shipping') == 'N/A' or 
            not offer.get('shipping') or
            offer.get('shipping', '').strip() == ''
        )
        
        if needs_enhancement and offer.get('offer_url'):
            offers_to_process.append(offer)
        else:
            enhanced_offers.append(offer)
    
    if not offers_to_process:
        return enhanced_offers
    
    # SMART OPTIMIZATION: Sort by price first to process cheapest offers first
    # This ensures users see the best deals even with early exit at 5 offers
    offers_to_process.sort(key=lambda x: x.get('price_amount', float('inf')))
    print(f"Selenium: Sorted {len(offers_to_process)} offers by price - processing cheapest first")
    
    print(f"Selenium: Processing {len(offers_to_process)} offers with {max_workers} parallel browsers")
    
    def process_offer_with_new_driver(offer):
        """Process a single offer with its own driver instance using aggressive mode"""
        driver = None
        try:
            # Create aggressive driver for maximum speed
            driver = create_selenium_driver(headless=True, aggressive=True)
            details = selenium_extract_offer_details_with_driver(driver, offer.get('offer_url'), user_country)
            
            if details is None:
                return None  # Offer not available
            
            # Enhance offer with Selenium data
            enhanced = offer.copy()
            if details.get('shipping_cost', 'Unknown') != 'Unknown':
                enhanced['shipping'] = details['shipping_cost']
                enhanced['shipping_amount'] = details.get('shipping_amount', 0.0)
                enhanced['total_amount'] = enhanced.get('price_amount', 0) + details.get('shipping_amount', 0.0)
                enhanced['selenium_enhanced'] = True
                enhanced['extraction_time'] = details.get('extraction_time', 0)
            
            return enhanced
        except Exception as e:
            print(f"Selenium: Error processing offer: {e}")
            return offer  # Return original on error
        finally:
            if driver:
                driver.quit()
    
    # Process offers in parallel with early exit optimization
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_offer = {executor.submit(process_offer_with_new_driver, offer): offer 
                          for offer in offers_to_process}
        
        processed_count = 0
        for future in as_completed(future_to_offer):
            result = future.result()
            if result is not None:
                enhanced_offers.append(result)
                processed_count += 1
                
                # Early exit if we have enough good offers (5+ offers for speed)
                if len(enhanced_offers) >= 5:
                    print(f"Selenium: Early exit - found {len(enhanced_offers)} good offers (sorted by price)")
                    # Cancel remaining futures for speed
                    for remaining_future in future_to_offer:
                        if not remaining_future.done():
                            remaining_future.cancel()
                    break
    
    print(f"Selenium: Parallel processing completed - {len(enhanced_offers)} available offers")
    return enhanced_offers