#!/usr/bin/env python3
"""
Performia GUI Test and Demo Script
Shows the capabilities of the Performia System GUI
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:5001"

def check_server():
    """Check if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=2)
        if response.status_code == 200:
            print("✅ Performia GUI server is running!")
            return True
    except requests.exceptions.RequestException:
        print("❌ Server not responding. Please start the GUI first.")
        print("   Run: venv/bin/python gui/app_simple.py")
        return False
    return False

def display_status():
    """Display current system status"""
    response = requests.get(f"{BASE_URL}/api/status")
    status = response.json()
    
    print("\n" + "="*60)
    print("🎵 PERFORMIA SYSTEM STATUS")
    print("="*60)
    
    print(f"\n🎮 System State:")
    print(f"  • Running: {status['is_running']}")
    print(f"  • Mode: {status['mode']}")
    print(f"  • Listening Mode: {status['listening_mode']}")
    print(f"  • Tempo: {status['tempo']} BPM")
    print(f"  • Key: {status['key']}")
    
    print(f"\n🤖 Agent Status:")
    for agent_name, agent_data in status['agents'].items():
        active_icon = "🟢" if agent_data['active'] else "🔴"
        print(f"  {active_icon} {agent_name.capitalize()}:")
        print(f"      Aggression: {agent_data['aggression']:.1f}")
        print(f"      Creativity: {agent_data['creativity']:.1f}")
    
    print(f"\n📊 Performance Metrics:")
    metrics = status['performance_metrics']
    print(f"  • Latency: {metrics.get('latency', 0)}ms")
    print(f"  • CPU Usage: {metrics.get('cpu_usage', 0)}%")
    if 'memory_usage' in metrics:
        print(f"  • Memory: {metrics['memory_usage']}MB")
    if 'events_per_second' in metrics:
        print(f"  • Events/sec: {metrics['events_per_second']}")
    
    print(f"\n🎤 Input Monitor:")
    print(f"  • Level: {status['input_level']:.1%}")
    if status['detected_chord']:
        print(f"  • Detected Chord: {status['detected_chord']}")

def test_controls():
    """Test system controls via API"""
    print("\n" + "="*60)
    print("🎛️  TESTING SYSTEM CONTROLS")
    print("="*60)
    
    # Test starting the system
    print("\n▶️  Starting system...")
    response = requests.post(f"{BASE_URL}/api/start")
    if response.status_code == 200:
        print("✅ System started successfully")
    
    time.sleep(2)
    
    # Test changing mode
    print("\n🔄 Switching to interactive mode...")
    response = requests.post(f"{BASE_URL}/api/mode", 
                            json={"mode": "interactive"})
    if response.status_code == 200:
        print("✅ Mode changed successfully")
    
    # Test updating agent parameters
    print("\n🎚️  Updating agent parameters...")
    for agent in ["drums", "bass", "melody", "harmony"]:
        params = {
            "agent": agent,
            "aggression": 0.7,
            "creativity": 0.8
        }
        response = requests.post(f"{BASE_URL}/api/agent/update", json=params)
        if response.status_code == 200:
            print(f"  ✅ Updated {agent}")
    
    # Test stopping the system
    print("\n⏹️  Stopping system...")
    response = requests.post(f"{BASE_URL}/api/stop")
    if response.status_code == 200:
        print("✅ System stopped successfully")

def show_gui_features():
    """Display information about GUI features"""
    print("\n" + "="*60)
    print("🖥️  PERFORMIA GUI FEATURES")
    print("="*60)
    
    print("""
The Performia System GUI provides:

📊 Real-time Monitoring:
  • System status and performance metrics
  • Individual agent activity and parameters
  • Audio input level monitoring
  • Chord detection display
  • Latency and CPU usage graphs

🎛️  Control Interface:
  • Start/Stop system control
  • Mode switching (Autonomous/Interactive)
  • Listening mode selection
  • Per-agent parameter sliders:
    - Aggression (dynamics, dissonance)
    - Creativity (pattern variation, complexity)
  • Agent activation toggles

🎵 Musical Controls:
  • Tempo adjustment (60-180 BPM)
  • Key selection
  • Scale mode selection
  • Global dynamics control

📡 WebSocket Updates:
  • Real-time data streaming
  • 10Hz update rate for smooth visualization
  • Event-driven architecture

🎨 Visual Design:
  • Dark theme optimized for performance
  • Responsive layout
  • Color-coded agent indicators
  • Animated level meters
""")

def main():
    """Main demo function"""
    print("🎵 PERFORMIA SYSTEM GUI DEMO")
    print("="*60)
    
    # Check if server is running
    if not check_server():
        return 1
    
    print("\n🌐 GUI is available at: http://localhost:5001")
    print("📱 Open this URL in your browser to see the interface")
    
    # Display current status
    display_status()
    
    # Test controls
    try:
        response = input("\n❓ Would you like to test the control API? (y/n): ")
        if response.lower() == 'y':
            test_controls()
            time.sleep(2)
            display_status()
    except KeyboardInterrupt:
        print("\n⛔ Skipping control test")
    
    # Show features
    show_gui_features()
    
    print("\n✨ The Performia GUI is running!")
    print("📌 Keep this terminal open to maintain the server")
    print("🌐 Access the GUI at: http://localhost:5001")
    print("⌨️  Press Ctrl+C to stop the server")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
