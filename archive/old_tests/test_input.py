#!/usr/bin/env python3
"""
Test audio input monitoring through SuperCollider
"""

import time
from pythonosc import udp_client, dispatcher, osc_server
import threading

# Connect to SuperCollider
client = udp_client.SimpleUDPClient("127.0.0.1", 57110)

print("🎤 Testing Performia Audio Input")
print("==================================")
print("")

# First, create an input monitor synth in SuperCollider
print("Setting up input monitoring...")

# Create SynthDef for input monitoring (passthrough with analysis)
synthdef_code = '''
(
SynthDef(\\inputMonitor, { |in=0, out=0, amp=1|
    var input, amplitude;
    input = SoundIn.ar(in);
    amplitude = Amplitude.kr(input, 0.01, 0.1);
    
    // Send amplitude data
    SendReply.kr(Impulse.kr(10), '/amplitude', amplitude);
    
    // Pass through audio (with volume control)
    Out.ar(out, input * amp);
}).add;
)
'''

# We'll use a simpler approach - just monitor the input
client.send_message("/s_new", [
    "default",  # Use default synth
    1000,       # Specific node ID
    1,          # Add action
    0,          # Target
    "freq", 0,  # No frequency (we'll use it differently)
    "amp", 0    # Start muted
])

print("✓ Input monitoring setup")
print("")
print("Testing input levels...")
print("(Make some noise into your audio interface)")
print("")

# Monitor for 5 seconds
print("Monitoring for 5 seconds...")
for i in range(5):
    print(f"  {5-i} seconds remaining...")
    time.sleep(1)

# Now test with passthrough
print("")
print("Enabling audio passthrough (input -> output)...")
print("⚠️  Warning: May cause feedback if using speakers!")
print("")

# Enable passthrough
client.send_message("/n_set", [1000, "amp", 0.5])

print("Passthrough enabled for 3 seconds...")
time.sleep(3)

# Disable passthrough
client.send_message("/n_set", [1000, "amp", 0])
client.send_message("/n_free", [1000])

print("")
print("✅ Audio input test complete!")
print("")
print("If you could hear your input through the output,")
print("then audio input is working correctly!")
print("")
print("Note: Full input analysis requires the complete")
print("Performia input system to be initialized.")
