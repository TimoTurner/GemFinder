"""
Better Discogs Marketplace Scraper with proper shipping extraction
Based on research from decodo.com guide and CSS selectors
"""
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
from utils import parse_price

def scrape_discogs_marketplace_better(release_id: str, user_country: str = "DE", max_offers: int = 15) -> List[Dict]:
    """
    Improved Discogs marketplace scraper that properly extracts shipping costs
    and detects unavailable offers.
    
    Args:
        release_id: Discogs release ID
        user_country: User's country code (e.g., "DE")
        max_offers: Maximum number of offers to return
        
    Returns:
        List of marketplace offers with proper shipping information
    """
    marketplace_url = f"https://www.discogs.com/sell/release/{release_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        print(f"Scraping marketplace for release {release_id}...")
        response = requests.get(marketplace_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Failed to fetch marketplace page: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        offers = []
        
        # Find all marketplace items - updated selector based on current Discogs structure
        marketplace_items = soup.find_all('tr', class_='shortcut_navigable')
        
        if not marketplace_items:
            # Fallback: try alternative selectors
            marketplace_items = soup.find_all('tr', attrs={'data-release-id': True})
        
        print(f"Found {len(marketplace_items)} marketplace items")
        
        for i, item in enumerate(marketplace_items[:max_offers]):
            try:
                offer_data = extract_offer_data(item, i+1, user_country)
                if offer_data:
                    offers.append(offer_data)
            except Exception as e:
                print(f"Error parsing offer {i+1}: {e}")
                continue
        
        print(f"Successfully parsed {len(offers)} offers")
        return offers
        
    except Exception as e:
        print(f"Error scraping marketplace: {e}")
        return []

def extract_offer_data(item_element, index: int, user_country: str) -> Dict:
    """Extract offer data from a marketplace item element"""
    
    offer_data = {
        'price': '',
        'condition': '',
        'seller': '',
        'seller_url': '',
        'shipping': '',
        'offer_url': '',
        'scraped_at': time.time(),
        'price_amount': 0.0,
        'price_currency': '',
        'shipping_amount': 0.0,
        'total_amount': 0.0
    }
    
    try:
        # Extract price - multiple possible selectors
        price_element = (
            item_element.find('span', class_='price') or
            item_element.find('td', class_='item_price') or
            item_element.find('span', attrs={'data-currency': True})
        )
        
        if price_element:
            price_text = price_element.get_text().strip()
            offer_data['price'] = price_text
            price_amount, price_currency = parse_price(price_text)
            offer_data['price_amount'] = price_amount
            offer_data['price_currency'] = price_currency
        
        # Extract shipping - key improvement over original scraper
        shipping_element = (
            item_element.find('span', class_='item_shipping') or
            item_element.find('td', class_='item_price').find('span', class_='hide_mobile') if item_element.find('td', class_='item_price') else None or
            item_element.find('span', string=lambda text: text and 'shipping' in text.lower())
        )
        
        if shipping_element:
            shipping_text = shipping_element.get_text().strip()
            offer_data['shipping'] = shipping_text
            
            # Parse shipping amount
            if '+' in shipping_text and 'shipping' in shipping_text.lower():
                # Extract numerical part from "+ €2.50 shipping" format
                shipping_amount, shipping_currency = parse_price(shipping_text.replace('+', '').replace('shipping', '').strip())
            else:
                shipping_amount, shipping_currency = parse_price(shipping_text)
            
            offer_data['shipping_amount'] = shipping_amount
        else:
            # Check for "no shipping" indicators
            no_shipping_indicators = item_element.find_all(string=lambda text: 
                text and any(indicator in text.lower() for indicator in ['free shipping', 'no shipping cost', 'kostenloser versand'])
            )
            
            if no_shipping_indicators:
                offer_data['shipping'] = 'Free'
                offer_data['shipping_amount'] = 0.0
            else:
                offer_data['shipping'] = 'N/A'
                offer_data['shipping_amount'] = 0.0
        
        # Check for availability restrictions
        availability_restrictions = item_element.find_all(string=lambda text:
            text and any(restriction in text for restriction in [
                f'Unavailable in {get_country_name(user_country)}',
                f'Not available in {get_country_name(user_country)}',
                'Does not ship to your country'
            ])
        )
        
        if availability_restrictions:
            print(f"Offer {index} not available in {user_country}: {availability_restrictions[0]}")
            return None  # Skip unavailable offers
        
        # Extract condition
        condition_element = (
            item_element.find('span', class_='item_condition') or
            item_element.find('td', class_='item_description').find('p', class_='item_condition') if item_element.find('td', class_='item_description') else None
        )
        
        if condition_element:
            offer_data['condition'] = condition_element.get_text().strip()
        
        # Extract seller info
        seller_element = item_element.find('a', href=lambda href: href and '/seller/' in href)
        if seller_element:
            offer_data['seller'] = seller_element.get_text().strip()
            offer_data['seller_url'] = f"https://www.discogs.com{seller_element.get('href')}"
        
        # Extract offer URL
        offer_link = item_element.find('a', href=lambda href: href and '/sell/item/' in href)
        if offer_link:
            offer_data['offer_url'] = f"https://www.discogs.com{offer_link.get('href')}"
        
        # Calculate total amount
        offer_data['total_amount'] = offer_data['price_amount'] + offer_data['shipping_amount']
        
        print(f"Parsed offer {index}: {offer_data['price']} + {offer_data['shipping']} = {offer_data['total_amount']} {offer_data['price_currency']}")
        
        return offer_data
        
    except Exception as e:
        print(f"Error extracting offer data: {e}")
        return None

def get_country_name(country_code: str) -> str:
    """Convert country code to full name for availability checking"""
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