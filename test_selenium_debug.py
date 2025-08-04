#!/usr/bin/env python3
"""
Debug Selenium WebDriver setup
"""

def test_selenium_setup():
    """Test if Selenium and ChromeDriver are working"""
    print("=" * 60)
    print("SELENIUM DEBUG TEST")
    print("=" * 60)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        print("✅ Selenium import successful")
        
        # Test ChromeDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        print("🔄 Attempting to create ChromeDriver...")
        driver = webdriver.Chrome(options=options)
        print("✅ ChromeDriver created successfully")
        
        print("🔄 Testing simple webpage access...")
        driver.get("https://www.google.com")
        print("✅ Google access successful")
        
        print("🔄 Testing Traxsource access...")
        driver.get("https://www.traxsource.com/search?term=test")
        print(f"✅ Traxsource access successful, title: {driver.title}")
        
        driver.quit()
        print("✅ All Selenium tests passed")
        
    except ImportError as e:
        print(f"❌ Selenium import failed: {e}")
        print("Install with: pip install selenium")
        
    except Exception as e:
        print(f"❌ Selenium error: {e}")
        print("ChromeDriver might not be installed or not in PATH")
        print("Install ChromeDriver: https://chromedriver.chromium.org/")
        
        # Try to get more specific error info
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_selenium_setup()