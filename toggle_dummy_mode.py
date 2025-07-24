#!/usr/bin/env python3
"""
Script to toggle between dummy and real API modes
Usage: python3 toggle_dummy_mode.py [enable|disable]
"""

import sys
import os

def toggle_scrape_search(enable_dummy=True):
    """Toggle dummy mode in scrape_search.py"""
    file_path = "scrape_search.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    if enable_dummy:
        # Enable dummy mode - comment out real scraper calls
        content = content.replace(
            "from discogs_scraper import create_discogs_scraper",
            "# from discogs_scraper import create_discogs_scraper  # DUMMY MODE"
        )
        content = content.replace(
            'print("Production scraper not available, using dummy data")',
            'print("DUMMY MODE: Using dummy data")'
        )
    else:
        # Disable dummy mode - enable real scraper calls  
        content = content.replace(
            "# from discogs_scraper import create_discogs_scraper  # DUMMY MODE",
            "from discogs_scraper import create_discogs_scraper"
        )
        content = content.replace(
            'print("DUMMY MODE: Using dummy data")',
            'print("Production scraper not available, using dummy data")'
        )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    mode = "DUMMY" if enable_dummy else "REAL"
    print(f"✅ {file_path}: {mode} mode enabled")


def toggle_api_search(enable_dummy=True):
    """Toggle dummy mode in api_search.py"""
    file_path = "api_search.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    if not enable_dummy:
        # For now, keep API search as dummy since we don't have real API implementations
        print(f"ℹ️ {file_path}: Keeping dummy mode (no real API implementations available)")
        return
    
    mode = "DUMMY" if enable_dummy else "REAL"
    print(f"✅ {file_path}: {mode} mode enabled")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['enable', 'disable']:
        print("Usage: python3 toggle_dummy_mode.py [enable|disable]")
        print("  enable  = Use dummy data (fast for testing)")  
        print("  disable = Use real APIs (slow but real data)")
        sys.exit(1)
    
    enable_dummy = sys.argv[1] == 'enable'
    
    print("🔧 TOGGLING DUMMY MODE")
    print("=" * 40)
    
    if enable_dummy:
        print("🎭 ENABLING DUMMY MODE (fast testing)")
    else:
        print("🌐 ENABLING REAL MODE (real data)")
    
    # Toggle different modules
    toggle_scrape_search(enable_dummy)
    toggle_api_search(enable_dummy)
    
    print("=" * 40)
    
    if enable_dummy:
        print("✅ DUMMY MODE ACTIVE")
        print("   - Fast testing with fake data")
        print("   - No external API calls")
        print("   - Predictable test results")
    else:
        print("✅ REAL MODE ACTIVE")  
        print("   - Real Discogs marketplace scraping")
        print("   - Actual prices and offers")
        print("   - Slower but authentic data")
        print("   - Requires internet connection")
    
    print(f"\n🚀 Ready to run: streamlit run main.py")


if __name__ == "__main__":
    main()