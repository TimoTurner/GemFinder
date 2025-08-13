"""
Bandcamp Fallback Implementation
Provides a non-blocking fallback for Bandcamp searches
"""

def search_bandcamp_safe(artist, track):
    """Safe Bandcamp search with fallback"""
    try:
        # Import and attempt real Bandcamp search with timeout
        from scrape_search import search_bandcamp
        import signal
        
        class TimeoutException(Exception):
            pass
        
        def timeout_handler(signum, frame):
            raise TimeoutException("Bandcamp search timed out")
        
        # Set 8-second timeout for the entire operation
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(8)
        
        try:
            result = search_bandcamp(artist, track)
            signal.alarm(0)  # Cancel timeout
            return result if result else [{"platform": "Bandcamp", "title": "Kein Treffer"}]
        except TimeoutException:
            print("⏰ Bandcamp search timeout - using fallback")
            return [{"platform": "Bandcamp", "title": "Timeout - Service unavailable"}]
        except Exception as e:
            print(f"❌ Bandcamp search error: {e}")
            return [{"platform": "Bandcamp", "title": "Service temporarily unavailable"}]
        finally:
            signal.alarm(0)  # Ensure timeout is cancelled
            
    except ImportError:
        # Fallback if modules not available
        return [{"platform": "Bandcamp", "title": "Service unavailable"}]