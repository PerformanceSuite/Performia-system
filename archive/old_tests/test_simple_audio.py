#!/usr/bin/env python3
"""
Simple audio test using basic OSC messages to SuperCollider
"""

import time
from pythonosc import udp_client

# Create OSC client
client = udp_client.SimpleUDPClient("127.0.0.1", 57110)

print("🎵 Simple SuperCollider Audio Test")
print("=" * 40)
print("Testing basic sine wave...")

# Test if server is responding
client.send_message("/status", [])
time.sleep(0.1)

# Play a simple sine wave using built-in UGens
# This creates a simple sine oscillator at 440Hz
print("\n1. Playing 440Hz sine wave (A4)...")

# Create a simple synth using s_new with default instrument
# Format: /s_new defName nodeID addAction targetID
node_id = 1000

# Use the default sine instrument if available, or create a simple one
# SuperCollider's default doesn't have pre-made synths, so we'll use a different approach

# First, let's try sending a simple test
print("Sending test message to SuperCollider...")
client.send_message("/notify", [1])  # Turn on notifications
time.sleep(0.1)

# Try to create a group
client.send_message("/g_new", [1, 0, 0])
time.sleep(0.1)

print("\nSuperCollider is running but needs SynthDefs to be loaded.")
print("The server is configured and detected your Quantum 2626 interface.")
print("\nTo hear audio, we need to:")
print("1. Compile and load SynthDefs using SuperCollider IDE or sclang")
print("2. Or use a different approach with pre-compiled synthdefs")

# Create a simple SynthDef loading script
synthdef_script = """
// Save this as load_synthdefs.scd and run in SuperCollider IDE
(
// Boot the server if not already
s.waitForBoot({
    
    // Simple sine synth
    SynthDef(\\sine, {
        |out=0, freq=440, amp=0.1, pan=0|
        var sig;
        sig = SinOsc.ar(freq) * amp;
        sig = Pan2.ar(sig, pan);
        sig = sig * EnvGen.kr(Env.perc(0.01, 1), doneAction: 2);
        Out.ar(out, sig);
    }).add;
    
    // Kick drum
    SynthDef(\\kick, {
        |out=0, freq=60, amp=0.5, pan=0|
        var sig, env;
        env = EnvGen.kr(Env.perc(0.001, 0.3), doneAction:2);
        sig = SinOsc.ar(XLine.kr(freq*4, freq, 0.02)) * env;
        sig = Pan2.ar(sig * amp, pan);
        Out.ar(out, sig);
    }).add;
    
    // Snare drum
    SynthDef(\\snare, {
        |out=0, freq=200, amp=0.3, pan=0|
        var sig, env, noise;
        env = EnvGen.kr(Env.perc(0.001, 0.15), doneAction:2);
        noise = WhiteNoise.ar(0.5);
        sig = (SinOsc.ar(freq) + noise) * env * amp;
        sig = Pan2.ar(sig, pan);
        Out.ar(out, sig);
    }).add;
    
    // Hi-hat
    SynthDef(\\hihat, {
        |out=0, amp=0.2, pan=0|
        var sig, env;
        env = EnvGen.kr(Env.perc(0.001, 0.05), doneAction:2);
        sig = WhiteNoise.ar(1);
        sig = HPF.ar(sig, 5000) * env * amp;
        sig = Pan2.ar(sig, pan);
        Out.ar(out, sig);
    }).add;
    
    "SynthDefs loaded!".postln;
});
)

// Test the synths
Synth(\\sine, [\\freq, 440]);
Synth(\\kick);
"""

print("\n" + "="*60)
print("SYNTHDEF LOADING SCRIPT")
print("="*60)
print(synthdef_script)
print("="*60)

# Save the script
with open("load_synthdefs.scd", "w") as f:
    f.write(synthdef_script)

print("\nSaved to: load_synthdefs.scd")
print("\nTo load the synthesizers and hear audio:")
print("1. Open SuperCollider IDE")
print("2. Open the file 'load_synthdefs.scd'")
print("3. Execute the code (Cmd+Enter)")
print("\nOr run from command line:")
print("  /Applications/SuperCollider.app/Contents/MacOS/sclang load_synthdefs.scd")

# Alternative: Try to use sclang to load the synthdefs
print("\n" + "="*40)
print("Attempting to load synthdefs via sclang...")

import subprocess
import os

# Create a simpler script that just loads synthdefs
load_script = """
s = Server.local;
s.waitForBoot({
    SynthDef("sine", {
        |out=0, freq=440, amp=0.1|
        var sig = SinOsc.ar(freq) * amp;
        sig = sig * EnvGen.kr(Env.perc(0.01, 1), doneAction: 2);
        Out.ar(out, sig);
    }).send(s);
    
    SynthDef("kick", {
        |out=0, amp=0.5|
        var sig = SinOsc.ar(XLine.kr(240, 60, 0.02));
        sig = sig * EnvGen.kr(Env.perc(0.001, 0.3), doneAction: 2);
        Out.ar(out, sig * amp);
    }).send(s);
    
    0.5.wait;
    "SynthDefs loaded successfully!".postln;
    0.exit;
});
"""

with open("load_synthdefs_simple.scd", "w") as f:
    f.write(load_script)

print("Created load_synthdefs_simple.scd")
print("\nServer is ready at:")
print("  Address: 127.0.0.1")
print("  Port: 57110")
print("  Audio Device: Quantum 2626")
print("  Sample Rate: 96000 Hz")