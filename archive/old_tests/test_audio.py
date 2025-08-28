#!/usr/bin/env python3
"""
Test audio output through the Performia system
"""

import time
from pythonosc import udp_client

# Connect to SuperCollider
client = udp_client.SimpleUDPClient("127.0.0.1", 57110)

print("🎵 Testing Performia Audio Output")
print("==================================")
print("Playing test sequence...")
print("")

# Test sequence
notes = [
    (60, "C"),   # C4
    (62, "D"),   # D4
    (64, "E"),   # E4
    (65, "F"),   # F4
    (67, "G"),   # G4
    (69, "A"),   # A4
    (71, "B"),   # B4
    (72, "C"),   # C5
]

print("Playing scale...")
for midi_note, note_name in notes:
    freq = 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
    print(f"  {note_name} ({freq:.1f} Hz)")
    
    # Create a simple sine synth
    client.send_message("/s_new", [
        "default",     # synth name (built-in)
        -1,         # node ID (auto)
        1,          # add action
        0,          # target
        "freq", freq,
        "amp", 0.3
    ])
    
    time.sleep(0.3)

print("")
print("✅ Audio test complete!")
print("")
print("If you heard a scale (C to C), then audio output is working!")
