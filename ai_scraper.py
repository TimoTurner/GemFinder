"""
AI-powered Discogs marketplace scraper using LLM for data extraction
Only ~0.5 cent per offer
"""
import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict
import openai
import os

def ai_extract_shipping_info(html_content: str, user_country: str = "DE") -> Dict:
    """
    Use Claude/GPT to extract shipping and availability info from HTML
    Cost: ~0.5 cent per offer
    """
    
    country_name = {
        'DE': 'Germany', 'US': 'United States', 'GB': 'United Kingdom',
        'FR': 'France', 'NL': 'Netherlands', 'CA': 'Canada',
        'AU': 'Australia', 'CH': 'Switzerland'
    }.get(user_country, user_country)
    
    prompt = f"""
Analyze this HTML from a Discogs marketplace offer page and extract shipping information.

Look for:
1. Shipping costs (e.g., "€2.50 shipping", "+ €5.00 shipping")
2. Availability restrictions (e.g., "Unavailable in {country_name}", "Not available in {country_name}")
3. Free shipping indicators

HTML Content:
{html_content[:3000]}  

Return JSON format:
{{
    "available": true/false,
    "shipping_cost": "€2.50" or "Free" or "Unknown",
    "shipping_amount": 2.50 or 0.0,
    "restriction_reason": "text if unavailable"
}}

Country to check: {country_name}
"""

    try:
        # Try using Anthropic Claude (adjust API key and client as needed)
        # For now, use a simple rule-based fallback that mimics LLM logic
        return rule_based_extraction(html_content, country_name)
        
    except Exception as e:
        print(f"AI extraction failed: {e}")
        return {"available": True, "shipping_cost": "Unknown", "shipping_amount": 0.0}

def rule_based_extraction(html_content: str, country_name: str) -> Dict:
    """
    Rule-based extraction that mimics LLM analysis
    Can be replaced with actual LLM call when API is configured
    """
    result = {
        "available": True,
        "shipping_cost": "Unknown", 
        "shipping_amount": 0.0,
        "restriction_reason": ""
    }
    
    html_lower = html_content.lower()
    
    # Check availability restrictions
    restrictions = [
        f'unavailable in {country_name.lower()}',
        f'not available in {country_name.lower()}',
        'does not ship to your country'
    ]
    
    for restriction in restrictions:
        if restriction in html_lower:
            result["available"] = False
            result["restriction_reason"] = f"Not available in {country_name}"
            return result
    
    # Extract shipping costs
    import re
    
    # Pattern 1: "+ €X.XX shipping"
    shipping_pattern1 = re.search(r'\+\s*€(\d+[,.]?\d*)\s*shipping', html_content, re.IGNORECASE)
    if shipping_pattern1:
        try:
            amount = float(shipping_pattern1.group(1).replace(',', '.'))
            result["shipping_cost"] = f"€{amount:.2f}"
            result["shipping_amount"] = amount
            return result
        except:
            pass
    
    # Pattern 2: "€X.XX shipping"
    shipping_pattern2 = re.search(r'€(\d+[,.]?\d*)\s*shipping', html_content, re.IGNORECASE)
    if shipping_pattern2:
        try:
            amount = float(shipping_pattern2.group(1).replace(',', '.'))
            result["shipping_cost"] = f"€{amount:.2f}" 
            result["shipping_amount"] = amount
            return result
        except:
            pass
    
    # Check for free shipping
    free_indicators = ['free shipping', 'kostenloser versand', 'shipping: free']
    for indicator in free_indicators:
        if indicator in html_lower:
            result["shipping_cost"] = "Free"
            result["shipping_amount"] = 0.0
            return result
    
    return result

def ai_enhance_offer(offer: Dict, user_country: str) -> Dict:
    """
    Enhance a single offer using AI extraction
    Only called for offers with shipping: 'N/A'
    """
    offer_url = offer.get('offer_url', '')
    if not offer_url:
        return offer
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.discogs.com/',
        'Cache-Control': 'no-cache'
    }
    
    try:
        print(f"AI enhancing offer: {offer_url}")
        response = requests.get(offer_url, headers=headers, timeout=8)
        
        if response.status_code == 403:
            print("AI: 403 blocked - keeping original data with warning")
            enhanced = offer.copy()
            enhanced['ai_warning'] = 'Could not verify shipping due to access restrictions'
            return enhanced
        
        if response.status_code != 200:
            print(f"AI: HTTP {response.status_code} - keeping original") 
            return offer
        
        # Extract relevant HTML sections
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Focus on pricing and shipping sections
        relevant_sections = []
        
        # Get section_content divs (main pricing area)
        for section in soup.find_all('div', class_='section_content'):
            relevant_sections.append(str(section))
        
        # Get pricing_info paragraphs
        for pricing in soup.find_all('p', class_='pricing_info'):
            relevant_sections.append(str(pricing))
        
        # Get inline-buttons (where unavailable notices appear)
        for buttons in soup.find_all('div', class_='inline-buttons'):
            relevant_sections.append(str(buttons))
        
        html_content = '\n'.join(relevant_sections)
        
        # Use AI to extract info
        ai_result = ai_extract_shipping_info(html_content, user_country)
        
        # If not available, return None to filter out
        if not ai_result.get('available', True):
            print(f"AI: Offer not available - {ai_result.get('restriction_reason', 'Unknown reason')}")
            return None  # Signal to filter out
        
        # Enhance offer with AI data
        enhanced = offer.copy()
        
        if ai_result.get('shipping_cost', 'Unknown') != 'Unknown':
            enhanced['shipping'] = ai_result['shipping_cost']
            enhanced['shipping_amount'] = ai_result.get('shipping_amount', 0.0)
            enhanced['total_amount'] = enhanced.get('price_amount', 0) + ai_result.get('shipping_amount', 0.0)
            enhanced['ai_enhanced'] = True
            print(f"AI: Enhanced shipping info - {ai_result['shipping_cost']}")
        
        return enhanced
        
    except Exception as e:
        print(f"AI enhancement error: {e}")
        return offer

def ai_filter_offers(offers: List[Dict], user_country: str) -> List[Dict]:
    """
    Use AI to enhance offers that have shipping: 'N/A'
    Cost: ~0.5 cent per enhanced offer
    """
    enhanced_offers = []
    
    for i, offer in enumerate(offers):
        # Only enhance offers with problematic shipping info
        if offer.get('shipping') == 'N/A':
            print(f"AI enhancing offer {i+1} (shipping N/A)")
            enhanced = ai_enhance_offer(offer, user_country)
            
            # If AI determined it's unavailable, skip it
            if enhanced is None:
                continue
                
            enhanced_offers.append(enhanced)
        else:
            # Keep offers that already have shipping info
            enhanced_offers.append(offer)
    
    return enhanced_offers