#!/usr/bin/env python3
"""
Debug the real Discogs offer to see what's being extracted
"""
from selenium_scraper import selenium_extract_offer_details

def debug_real_offer():
    # The actual URL from your debug output
    offer_url = "https://www.discogs.com/sell/item/3755020159"
    
    print(f"Debugging real offer: {offer_url}")
    print("=" * 60)
    
    # Extract details and see what the Selenium scraper finds
    result = selenium_extract_offer_details(offer_url, "DE")
    
    print(f"Result: {result}")

if __name__ == "__main__":
    debug_real_offer()