#!/usr/bin/env python3
"""
Test parallel vs sequential scraping performance
"""

import time
import sys
sys.path.append('.')
from scrape_search import search_beatport, search_bandcamp, search_traxsource
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_sequential():
    """Test sequential scraping (current implementation)"""
    print("=== Sequential Scraping Test ===")
    
    artist = "Daft Punk"
    track = "One More Time"
    
    platforms = [
        ("Beatport", search_beatport),
        ("Bandcamp", search_bandcamp), 
        ("Traxsource", search_traxsource),
    ]
    
    start_time = time.time()
    results = []
    
    for name, func in platforms:
        try:
            print(f"Starting {name}...")
            result = func(artist, track)
            print(f"{name} completed: {result[0].get('title', 'No title')} ({result[0].get('search_time', 0)}s)")
            results.extend(result)
        except Exception as e:
            print(f"{name} error: {e}")
    
    total_time = time.time() - start_time
    print(f"Sequential total time: {total_time:.2f}s")
    print(f"Results count: {len(results)}")
    return results, total_time

def test_parallel():
    """Test true parallel scraping"""
    print("\n=== Parallel Scraping Test ===")
    
    artist = "Daft Punk"  
    track = "One More Time"
    
    platforms = [
        ("Beatport", search_beatport),
        ("Bandcamp", search_bandcamp),
        ("Traxsource", search_traxsource),
    ]
    
    start_time = time.time()
    results = []
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all tasks
        future_to_platform = {
            executor.submit(func, artist, track): name 
            for name, func in platforms
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_platform):
            platform_name = future_to_platform[future]
            try:
                result = future.result()
                print(f"{platform_name} completed: {result[0].get('title', 'No title')} ({result[0].get('search_time', 0)}s)")
                results.extend(result)
            except Exception as e:
                print(f"{platform_name} error: {e}")
    
    total_time = time.time() - start_time
    print(f"Parallel total time: {total_time:.2f}s")
    print(f"Results count: {len(results)}")
    return results, total_time

def main():
    print("Testing Digital Platform Scraping Performance...")
    
    # Test sequential
    seq_results, seq_time = test_sequential()
    
    # Test parallel  
    par_results, par_time = test_parallel()
    
    # Compare
    print(f"\n=== Performance Comparison ===")
    print(f"Sequential: {seq_time:.2f}s")
    print(f"Parallel:   {par_time:.2f}s")
    print(f"Speedup:    {seq_time/par_time:.1f}x faster")
    
    print(f"\n=== Results Analysis ===")
    print("Sequential results:")
    for result in seq_results:
        print(f"  {result['platform']}: {result['title']}")
    
    print("Parallel results:")
    for result in par_results:
        print(f"  {result['platform']}: {result['title']}")

if __name__ == "__main__":
    main()