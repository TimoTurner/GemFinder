#!/usr/bin/env python3
"""
Test new Beatport word-based filtering logic
"""

def normalize_for_matching(text):
    """Simple normalize function for testing"""
    if not text:
        return ""
    return text.lower().strip()

def beatport_word_filter(search_artist, search_track, search_album, result_title, result_artist, result_album):
    """
    Word-based filtering: At least one word from EACH search term must be found
    """
    # Split search terms into words
    artist_words = search_artist.lower().split() if search_artist else []
    track_words = search_track.lower().split() if search_track else []
    album_words = search_album.lower().split() if search_album else []
    
    # Combined result content
    result_content = f"{result_title} {result_artist} {result_album}".lower()
    
    print(f"    Search words: artist={artist_words}, track={track_words}")
    print(f"    Result content: '{result_content}'")
    
    # Check if at least one word from each search term is found
    artist_found = any(word in result_content for word in artist_words) if artist_words else True
    track_found = any(word in result_content for word in track_words) if track_words else True
    album_found = any(word in result_content for word in album_words) if album_words else True
    
    print(f"    Matches: artist_found={artist_found}, track_found={track_found}, album_found={album_found}")
    
    # Logic based on what search terms we have
    if search_artist and search_track:
        result = artist_found and track_found
    elif search_artist and search_album:
        result = artist_found and album_found
    elif search_track and search_album:
        result = track_found and album_found
    elif search_artist:
        result = artist_found
    elif search_track:
        result = track_found
    else:
        result = False
    
    print(f"    Final result: {result}")
    return result

def test_beatport_word_filter():
    """Test cases for the word-based filter"""
    print("=" * 60)
    print("BEATPORT WORD-BASED FILTER TEST")
    print("=" * 60)
    
    test_cases = [
        # Problem case that should be filtered out
        {
            "name": "Problem case: 'Drum Starts - Picasso' vs 'PICASSO Extended Mix'",
            "search": ("Drum Starts", "Picasso", ""),
            "result": ("PICASSO Extended Mix", "KENO", "Visions Of: Tech House Vol. 52"),
            "expected": False,  # Should be filtered out
            "reason": "Has 'picasso' but no 'drum' or 'starts'"
        },
        
        # Cases that should pass
        {
            "name": "Good match: 'All I want - Weekender'",
            "search": ("All I want", "Weekender", ""),
            "result": ("Weekender (Original Mix)", "All I Want", "Summer Vibes EP"),
            "expected": True,
            "reason": "Has 'weekender' and 'all'"
        },
        
        {
            "name": "Partial match: 'Catlow - Just Dancing'",
            "search": ("Catlow", "Just Dancing", ""),
            "result": ("Just Dancing (Extended Mix)", "Catlow", "Night Sessions"),
            "expected": True,
            "reason": "Has 'catlow' and 'just' or 'dancing'"
        },
        
        # Edge cases
        {
            "name": "Single word artist: 'Picasso'",
            "search": ("Picasso", "Track Name", ""),
            "result": ("Some Track", "Picasso", "Album"),
            "expected": True,
            "reason": "Artist matches exactly"
        },
        
        {
            "name": "No matches at all",
            "search": ("NonExistent", "Artist", ""),  
            "result": ("Completely Different", "Track", "Album"),
            "expected": False,
            "reason": "No words match"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {case['name']} ---")
        print(f"Search: artist='{case['search'][0]}', track='{case['search'][1]}'")
        print(f"Result: title='{case['result'][0]}', artist='{case['result'][1]}', album='{case['result'][2]}'")
        print(f"Expected: {case['expected']} ({case['reason']})")
        
        actual = beatport_word_filter(
            case['search'][0], case['search'][1], case['search'][2],
            case['result'][0], case['result'][1], case['result'][2]
        )
        
        if actual == case['expected']:
            print(f"✅ PASS")
        else:
            print(f"❌ FAIL - got {actual}, expected {case['expected']}")

if __name__ == "__main__":
    test_beatport_word_filter()