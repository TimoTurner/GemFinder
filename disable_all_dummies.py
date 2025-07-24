#!/usr/bin/env python3
"""
Comprehensive script to disable ALL dummy modes across all files
This enables real API calls and scraping for Streamlit testing
"""

import os
import re

def disable_dummies_in_file(file_path):
    """Disable dummy modes in a specific file"""
    print(f"📝 Processing: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"   ⚠️ File not found, skipping")
        return
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # Common dummy patterns to disable
    patterns_to_fix = [
        # API search dummies - replace with actual API calls or disable dummy logic
        (r'def get_itunes_release_info\(artist, track\):\s*# Scenario A.*?else:\s*return.*?}', 
         'def get_itunes_release_info(artist, track):\n    # TODO: Implement real iTunes API\n    return {"platform": "iTunes", "title": "API Not Implemented", "artist": "", "album": "", "label": "", "price": "", "cover": "", "release_url": "", "preview": ""}'),
        
        # Scrape search dummies - enable real scraper
        (r'# from discogs_scraper import create_discogs_scraper.*?# DUMMY MODE',
         'from discogs_scraper import create_discogs_scraper'),
         
        (r'print\("DUMMY MODE: Using dummy data"\)',
         'print("Using production scraper")'),
         
        # Search function dummies - replace with real implementations where possible
        (r'def search_beatport\(artist, track\):\s*"""Fast dummy implementation.*?return.*?\]', 
         'def search_beatport(artist, track):\n    """Real Beatport search - TODO: Implement"""\n    return [{"platform": "Beatport", "title": "API Not Available", "artist": "", "album": "", "label": "", "price": "", "cover_url": "", "url": "", "search_time": 0.1}]'),
         
        (r'def search_bandcamp\(artist, track\):\s*"""Fast dummy implementation.*?return.*?\]',
         'def search_bandcamp(artist, track):\n    """Real Bandcamp search - TODO: Implement"""\n    return [{"platform": "Bandcamp", "title": "API Not Available", "artist": "", "album": "", "label": "", "price": "", "cover_url": "", "url": "", "search_time": 0.1}]'),
         
        (r'def search_traxsource\(artist, track\):\s*"""Fast dummy implementation.*?return.*?\]',
         'def search_traxsource(artist, track):\n    """Real Traxsource search - TODO: Implement"""\n    return [{"platform": "Traxsource", "title": "API Not Available", "artist": "", "album": "", "label": "", "price": "", "cover_url": "", "url": "", "search_time": 0.1}]'),
         
        (r'def search_revibed\(artist, album\):\s*"""Fast dummy implementation.*?return.*?\]',
         'def search_revibed(artist, album):\n    """Real Revibed search - TODO: Implement"""\n    return [{"platform": "Revibed", "title": "API Not Available", "artist": "", "album": "", "label": "", "price": "", "cover_url": "", "url": "", "search_time": 0.1}]'),
    ]
    
    # Apply regex replacements
    for pattern, replacement in patterns_to_fix:
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL | re.MULTILINE)
        if new_content != content:
            changes_made.append(f"Applied regex fix: {pattern[:50]}...")
            content = new_content
    
    # Specific line-by-line fixes
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Enable real scraper imports
        if '# from discogs_scraper import create_discogs_scraper' in line:
            line = line.replace('# ', '')
            changes_made.append(f"Line {i+1}: Enabled discogs_scraper import")
            
        # Replace dummy messages
        elif 'DUMMY MODE' in line or 'Fast dummy implementation' in line:
            if 'print(' in line:
                line = line.replace('DUMMY MODE: Using dummy data', 'Using production scraper')
                changes_made.append(f"Line {i+1}: Updated dummy message")
        
        # Enable Discogs offers scraping (disable dummy fallback)
        elif 'except ImportError:' in line and i < len(lines) - 1 and 'dummy' in lines[i+1].lower():
            # Comment out the ImportError fallback
            line = '        # ' + line + '  # DISABLED FOR REAL MODE'
            changes_made.append(f"Line {i+1}: Disabled ImportError fallback")
            
        # For API search - comment out dummy scenario logic
        elif ('# Scenario' in line or 'if artist.lower() in' in line) and 'search_discogs_releases' not in content:
            if not line.strip().startswith('#'):
                line = '    # ' + line + '  # DUMMY DISABLED'
                changes_made.append(f"Line {i+1}: Disabled dummy scenario")
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # Write back if changes were made
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"   ✅ Modified ({len(changes_made)} changes)")
        for change in changes_made[:3]:  # Show first 3 changes
            print(f"      - {change}")
        if len(changes_made) > 3:
            print(f"      - ... and {len(changes_made) - 3} more changes")
    else:
        print(f"   ℹ️ No changes needed")


def main():
    """Disable all dummies across all Python files"""
    print("🌐 DISABLING ALL DUMMY MODES")
    print("=" * 50)
    print("This will enable real API calls and scraping everywhere possible")
    print()
    
    # Files to process
    files_to_process = [
        'api_search.py',
        'scrape_search.py', 
        'providers.py',
        'ui_helpers.py',
        'text_extract.py',
        'state_manager.py',
        'utils.py',
        'main.py'
    ]
    
    processed = 0
    modified = 0
    
    for file_path in files_to_process:
        if os.path.exists(file_path):
            original_size = os.path.getsize(file_path)
            disable_dummies_in_file(file_path)
            new_size = os.path.getsize(file_path)
            
            if new_size != original_size:
                modified += 1
            processed += 1
        else:
            print(f"⚠️ File not found: {file_path}")
    
    print()
    print("=" * 50)
    print("🎯 SUMMARY")
    print(f"   Files processed: {processed}")
    print(f"   Files modified: {modified}")
    print()
    
    # Special handling for key integrations
    print("🔧 ENSURING KEY INTEGRATIONS ARE ACTIVE:")
    
    # Check if Discogs scraper is enabled
    try:
        with open('scrape_search.py', 'r') as f:
            scrape_content = f.read()
        
        if 'from discogs_scraper import create_discogs_scraper' in scrape_content:
            print("   ✅ Discogs marketplace scraper: ENABLED")
        else:
            print("   ❌ Discogs marketplace scraper: STILL DUMMY")
            
    except FileNotFoundError:
        print("   ⚠️ scrape_search.py not found")
    
    # Check UI helpers integration
    try:
        with open('ui_helpers.py', 'r') as f:
            ui_content = f.read()
            
        if 'scrape_discogs_marketplace_offers' in ui_content:
            print("   ✅ UI marketplace integration: ENABLED")
        else:
            print("   ❌ UI marketplace integration: NOT FOUND")
            
    except FileNotFoundError:
        print("   ⚠️ ui_helpers.py not found")
    
    print()
    print("🚀 READY FOR REAL DATA TESTING!")
    print("   Run: streamlit run main.py")
    print("   Expected behavior:")
    print("   - Real Discogs marketplace offers")
    print("   - Actual prices and conditions")
    print("   - Slower but authentic data")
    print("   - Location-based currency filtering")
    print("   - Quality filter toggle working")
    print()
    print("⚠️ Note: Some APIs (iTunes, Beatport, etc.) may show 'API Not Implemented'")
    print("   This is expected - focus on Discogs marketplace functionality")
    print()


if __name__ == "__main__":
    main()