#!/usr/bin/env python3
"""
Test Script: iTunes API Threading Performance
Vergleich Sequential vs Parallel Session-Handling
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor
from api_search import get_itunes_release_info, get_itunes_session

def test_sequential_calls():
    """Test: 3 Sequential iTunes API Calls"""
    print("\n=== SEQUENTIAL TEST ===")
    times = []
    
    for i in range(3):
        start = time.time()
        result = get_itunes_release_info("TestArtist", f"TestTrack{i}")
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"Call {i+1}: {elapsed:.2f}s - {result.get('title', 'ERROR')}")
    
    print(f"Sequential Average: {sum(times)/len(times):.2f}s")
    return times

def test_parallel_calls():
    """Test: 3 Parallel iTunes API Calls (wie in Live-Search)"""
    print("\n=== PARALLEL TEST (wie Live-Search) ===")
    times = []
    
    def single_call(track_num):
        start = time.time()
        result = get_itunes_release_info("TestArtist", f"TestTrack{track_num}")
        elapsed = time.time() - start
        return elapsed, result
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(single_call, i) for i in range(3)]
        
        for i, future in enumerate(futures):
            elapsed, result = future.result()
            times.append(elapsed)
            print(f"Thread {i+1}: {elapsed:.2f}s - {result.get('title', 'ERROR')}")
    
    print(f"Parallel Average: {sum(times)/len(times):.2f}s")
    return times

def test_session_sharing():
    """Test: Session-Sharing zwischen Threads"""
    print("\n=== SESSION SHARING TEST ===")
    
    def check_session_id():
        session = get_itunes_session()
        return f"Thread {threading.current_thread().ident}: Session ID {id(session)}"
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(check_session_id) for _ in range(3)]
        
        for future in futures:
            print(future.result())

def test_direct_api_speed():
    """Test: Raw iTunes API ohne Session-Overhead"""
    print("\n=== RAW API TEST ===")
    import requests
    
    start = time.time()
    response = requests.get(
        "https://itunes.apple.com/search",
        params={"term": "test", "entity": "song", "limit": 1, "country": "DE"},
        timeout=2
    )
    elapsed = time.time() - start
    
    print(f"Raw requests.get(): {elapsed:.2f}s")
    print(f"Status: {response.status_code}")
    return elapsed

if __name__ == "__main__":
    print("iTunes Threading Performance Test")
    print("=" * 50)
    
    # 1. Raw API Speed Test
    raw_time = test_direct_api_speed()
    
    # 2. Sequential Test (wie früher)
    seq_times = test_sequential_calls()
    
    # 3. Parallel Test (wie Live-Search)
    par_times = test_parallel_calls()
    
    # 4. Session Sharing Test
    test_session_sharing()
    
    # 5. Analyse
    print("\n=== ANALYSE ===")
    print(f"Raw API Zeit: {raw_time:.2f}s")
    print(f"Sequential Durchschnitt: {sum(seq_times)/len(seq_times):.2f}s")
    print(f"Parallel Durchschnitt: {sum(par_times)/len(par_times):.2f}s")
    
    if sum(par_times)/len(par_times) > sum(seq_times)/len(seq_times):
        print("❌ PROBLEM: Parallel ist langsamer als Sequential!")
        print("   → Thread-Session-Isolation vermutet")
    else:
        print("✅ Parallel Performance OK")