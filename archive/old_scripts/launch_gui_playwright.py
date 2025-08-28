#!/usr/bin/env python3
"""
Launch Performia GUI with Playwright browser automation
"""

import subprocess
import time
import os
import sys

def install_playwright():
    """Install Playwright in the system Python"""
    print("📦 Installing Playwright...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--user", "playwright"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    print("✅ Playwright installed!")

def launch_gui():
    """Launch the GUI using Playwright"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("⚠️  Playwright not found, installing...")
        install_playwright()
        from playwright.sync_api import sync_playwright
    
    # Check if GUI server is running
    import requests
    try:
        response = requests.get("http://localhost:5001/api/status", timeout=1)
        if response.status_code == 200:
            print("✅ GUI server already running!")
    except:
        print("❌ GUI server not responding at port 5001")
        print("Please run: cd gui && python app_simple.py")
        return
    
    # Launch browser with Playwright
    print("🌐 Launching browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1,
        )
        
        page = context.new_page()
        
        print("📍 Opening Performia GUI...")
        page.goto("http://localhost:5001", wait_until="networkidle")
        
        print("✨ GUI loaded successfully!")
        print("\n🎵 PERFORMIA SYSTEM GUI")
        print("=" * 50)
        print("The GUI is now open in your browser.")
        print("You can interact with:")
        print("  • System start/stop controls")
        print("  • Agent personality sliders")
        print("  • Mode selection (Autonomous/Interactive)")
        print("  • Real-time performance metrics")
        print("\nThe GUI will stay open until you close it.")
        print("Press Ctrl+C to exit.")
        
        # Keep browser open
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Closing browser...")
            browser.close()

if __name__ == "__main__":
    # First ensure requests is installed
    subprocess.run([sys.executable, "-m", "pip", "install", "--user", "requests"], 
                   capture_output=True)
    launch_gui()
