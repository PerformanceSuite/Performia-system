#!/usr/bin/env python3
"""
Capture screenshots of the Performia GUI for analysis
"""

from playwright.sync_api import sync_playwright
import time

def capture_gui():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        
        # Create context with larger viewport
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1,
        )
        
        page = context.new_page()
        
        print("📍 Navigating to Performia GUI...")
        page.goto("http://localhost:3001", wait_until="networkidle")
        
        # Wait for content to load
        time.sleep(2)
        
        # Take full page screenshot
        print("📸 Taking screenshot...")
        page.screenshot(path="gui_screenshot_full.png", full_page=True)
        print("✅ Screenshot saved as gui_screenshot_full.png")
        
        # Take viewport screenshot
        page.screenshot(path="gui_screenshot_viewport.png")
        print("✅ Screenshot saved as gui_screenshot_viewport.png")
        
        # Analyze the page structure
        print("\n🔍 Analyzing page structure...")
        
        # Check for main elements
        elements = {
            "Logo": "h1",
            "Agent strips": ".grid",
            "Eye toggles": "button",
            "Sliders": "input[type='range']",
            "Sidebar": "aside",
        }
        
        for name, selector in elements.items():
            count = page.locator(selector).count()
            print(f"  {name}: {count} found")
        
        # Check layout issues
        print("\n🎨 Checking layout...")
        viewport_size = page.viewport_size
        print(f"  Viewport: {viewport_size['width']}x{viewport_size['height']}")
        
        # Check if content overflows
        body = page.locator("body").first
        body_size = body.bounding_box()
        if body_size:
            print(f"  Body size: {body_size['width']}x{body_size['height']}")
        
        print("\n✨ Analysis complete!")
        print("📌 Browser will stay open for manual inspection.")
        print("Press Enter to close...")
        input()
        
        browser.close()

if __name__ == "__main__":
    capture_gui()
