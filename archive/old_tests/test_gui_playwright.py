#!/usr/bin/env python3
"""
Test and launch Performia GUI using Playwright
"""

import subprocess
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def start_flask_server():
    """Start the Flask server as a subprocess"""
    cmd = [
        sys.executable,
        str(Path(__file__).parent / "gui" / "app_simple.py")
    ]
    
    print("🚀 Starting Flask server...")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give server time to start
    time.sleep(3)
    
    # Check if process is running
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        print(f"❌ Server failed to start!")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return None
        
    print("✅ Flask server started successfully")
    return process

def test_gui_with_playwright():
    """Use Playwright to open and test the GUI"""
    
    with sync_playwright() as p:
        # Launch browser
        print("🌐 Launching browser...")
        browser = p.chromium.launch(
            headless=False,  # Show browser window
            slow_mo=100  # Slow down actions for visibility
        )
        
        try:
            # Create new page
            page = browser.new_page()
            
            # Navigate to the GUI
            print("📍 Navigating to http://localhost:5001...")
            page.goto("http://localhost:5001", wait_until="networkidle")
            
            # Take a screenshot
            screenshot_path = Path(__file__).parent / "gui_screenshot.png"
            page.screenshot(path=str(screenshot_path))
            print(f"📸 Screenshot saved to {screenshot_path}")
            
            # Check page title
            title = page.title()
            print(f"📄 Page title: {title}")
            
            # Look for key elements
            print("\n🔍 Checking for key GUI elements...")
            
            # Check for main sections
            elements_to_check = [
                ("System Control panel", "[class*='system-control'], #system-control, .panel:has-text('System Control')"),
                ("Agent panels", "[class*='agent'], .agent-panel, .panel:has-text('Agent')"),
                ("Performance Metrics", "[class*='metrics'], #metrics, .panel:has-text('Performance')"),
                ("Input Monitor", "[class*='input'], #input-monitor, .panel:has-text('Input')")
            ]
            
            for name, selector in elements_to_check:
                try:
                    if page.locator(selector).first.is_visible(timeout=2000):
                        print(f"  ✅ Found: {name}")
                    else:
                        print(f"  ⚠️  Not visible: {name}")
                except:
                    print(f"  ❌ Missing: {name}")
            
            # Try to interact with controls
            print("\n🎛️  Testing interactions...")
            
            # Look for Start/Stop button
            start_button = page.locator("button:has-text('Start'), button:has-text('Stop'), #start-system, #stop-system").first
            if start_button.is_visible():
                print(f"  ✅ Found control button: {start_button.inner_text()}")
                # Click the button
                start_button.click()
                time.sleep(1)
                print(f"  🔄 Clicked button, new text: {start_button.inner_text()}")
            
            # Check for agent controls
            agent_sliders = page.locator("input[type='range'], .slider").all()
            print(f"  🎚️  Found {len(agent_sliders)} slider controls")
            
            # Keep browser open for manual inspection
            print("\n✨ GUI is now open in the browser!")
            print("📌 You can interact with it manually.")
            print("⌨️  Press Enter to close the browser and exit...")
            input()
            
        finally:
            browser.close()
            print("🔒 Browser closed")

def main():
    """Main function to run the GUI test"""
    flask_process = None
    
    try:
        # Start Flask server
        flask_process = start_flask_server()
        if not flask_process:
            return 1
            
        # Test GUI with Playwright
        test_gui_with_playwright()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⛔ Interrupted by user")
        return 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Clean up Flask process
        if flask_process:
            print("🛑 Stopping Flask server...")
            flask_process.terminate()
            flask_process.wait(timeout=5)
            print("✅ Flask server stopped")

if __name__ == "__main__":
    sys.exit(main())
