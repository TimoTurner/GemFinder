#!/usr/bin/env python3
"""
Test and compare Selenium scraping performance optimizations
"""
import time
from selenium_scraper import selenium_filter_offers, selenium_filter_offers_parallel

def test_selenium_performance():
    # Test with realistic dummy offers that need enhancement
    test_offers = [
        {
            'seller': f'seller_{i}',
            'condition': 'VG+',
            'price': f'€{10+i}.99',
            'shipping': 'N/A',  # Needs enhancement
            'offer_url': f'https://www.discogs.com/sell/item/375502015{i}',  # Realistic but non-existent URLs
            'price_amount': 10.0 + i,
            'price_currency': 'EUR'
        }
        for i in range(5)  # Test with 5 offers
    ]
    
    print(f"Testing performance with {len(test_offers)} offers that need enhancement")
    print("=" * 60)
    
    # Test 1: Sequential processing (browser reuse)
    print("1. Sequential processing with browser reuse:")
    start_time = time.time()
    sequential_results = selenium_filter_offers(test_offers, 'DE')
    sequential_time = time.time() - start_time
    print(f"   Time: {sequential_time:.2f} seconds")
    print(f"   Results: {len(sequential_results)} offers")
    print()
    
    # Test 2: Parallel processing  
    print("2. Parallel processing (3 browsers):")
    start_time = time.time()
    parallel_results = selenium_filter_offers_parallel(test_offers, 'DE', max_workers=3)
    parallel_time = time.time() - start_time
    print(f"   Time: {parallel_time:.2f} seconds")
    print(f"   Results: {len(parallel_results)} offers")
    print()
    
    # Performance comparison
    if sequential_time > 0:
        speedup = sequential_time / parallel_time if parallel_time > 0 else float('inf')
        print(f"Performance improvement: {speedup:.1f}x faster with parallel processing")
    
    print("\nRecommendation:")
    if parallel_time < sequential_time * 0.8:  # At least 20% improvement
        print("✅ Use parallel processing for best performance")
    else:
        print("ℹ️  Use sequential processing for reliability")

if __name__ == "__main__":
    test_selenium_performance()