#!/usr/bin/env python3
"""
Quick test of Selenium scraper functionality
"""
from selenium_scraper import selenium_filter_offers, SELENIUM_AVAILABLE, parse_selenium_shipping

def test_shipping_parsing():
    """Test the shipping parsing logic specifically"""
    print("Testing shipping parsing logic...")
    
    test_cases = [
        "€9.99",  # Item price only - should return Unknown
        "+ €2.50 shipping",  # Clear shipping - should return €2.50
        "€15.00 + €3.00 shipping",  # Price + shipping - should return €3.00
        "Free shipping",  # Free shipping - should return Free
        "Kostenloser Versand",  # German free shipping
        "€9,99 plus €2,50 Versand",  # German with comma
    ]
    
    for test_text in test_cases:
        result = parse_selenium_shipping(test_text)
        print(f"Input: '{test_text}' -> Output: {result['shipping_cost']} ({result['shipping_amount']})")
    print()

def test_selenium_functionality():
    print(f"Selenium available: {SELENIUM_AVAILABLE}")
    
    # First test the parsing logic
    test_shipping_parsing()
    
    # Test with dummy offers (these will try to access real URLs)
    test_offers = [
        {
            'seller': 'test_seller',
            'condition': 'VG+',
            'price': '€15.00',
            'shipping': 'N/A',
            'offer_url': 'https://www.discogs.com/sell/item/123456',  # Non-existent URL for testing
            'price_amount': 15.0,
            'price_currency': 'EUR'
        },
        {
            'seller': 'test_seller2', 
            'condition': 'NM',
            'price': '€12.00',
            'shipping': '€2.50',  # Already has shipping, won't be enhanced
            'offer_url': 'https://www.discogs.com/sell/item/789012',
            'price_amount': 12.0,
            'price_currency': 'EUR'
        }
    ]
    
    print(f"Testing with {len(test_offers)} offers...")
    
    # Test filtering for Germany
    try:
        filtered_offers = selenium_filter_offers(test_offers, 'DE')
        print(f"Filtered offers: {len(filtered_offers)}")
        
        for i, offer in enumerate(filtered_offers):
            print(f"Offer {i+1}: {offer.get('shipping', 'N/A')} - Enhanced: {offer.get('selenium_enhanced', False)}")
            
    except Exception as e:
        print(f"Error testing Selenium: {e}")

if __name__ == "__main__":
    test_selenium_functionality()