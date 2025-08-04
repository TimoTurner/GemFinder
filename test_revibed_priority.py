#!/usr/bin/env python3
"""
Test Revibed priority logic: Artist > Album
"""

import sys
sys.path.append('.')
from scrape_search import search_revibed

def test_revibed_priority():
    print("Testing Revibed priority logic...")
    
    print("\n=== Test 1: Only Artist (costigane) ===")
    result1 = search_revibed("costigane", "")
    if result1:
        print(f"Result: {result1[0].get('title', 'No title')}")
        print(f"Status: {'SUCCESS' if result1[0].get('title') != 'Kein Treffer' else 'NO RESULTS'}")
    
    print("\n=== Test 2: Only Album (camera tricks) ===")  
    result2 = search_revibed("", "camera tricks")
    if result2:
        print(f"Result: {result2[0].get('title', 'No title')}")
        print(f"Status: {'SUCCESS' if result2[0].get('title') != 'Kein Treffer' else 'NO RESULTS'}")
    
    print("\n=== Test 3: Both Artist AND Album (should prioritize Artist) ===")
    result3 = search_revibed("costigane", "camera tricks")
    if result3:
        print(f"Result: {result3[0].get('title', 'No title')}")
        print(f"Status: {'SUCCESS' if result3[0].get('title') != 'Kein Treffer' else 'NO RESULTS'}")
        print("(Should be same as Test 1 - Artist priority)")

if __name__ == "__main__":
    test_revibed_priority()