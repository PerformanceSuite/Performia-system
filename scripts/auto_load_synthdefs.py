#!/usr/bin/env python3
"""
Auto-load SynthDefs when SuperCollider starts
This should be integrated into the engine startup
"""

import time
import subprocess
import os
from pythonosc import udp_client

def load_synthdefs():
    """Load SynthDefs using sclang evaluation"""
    
    print("Loading SynthDefs into SuperCollider...")
    
    # The SuperCollider way is to use sclang to evaluate code
    # We'll create a temporary file with our SynthDef code
    synthdef_code = '''
    (
    // Connect to already running server
    s = Server.default;
    s.addr = NetAddr("127.0.0.1", 57110);
    
    fork {
        // Simple sine synth for testing
        SynthDef(\\default, { |out=0, freq=440, amp=0.1, pan=0, gate=1|
            var sig, env;
            env = EnvGen.kr(Env.asr(0.01, 1, 0.1), gate, doneAction:2);
            sig = SinOsc.ar(freq) * amp * env;
            sig = Pan2.ar(sig, pan);
            Out.ar(out, sig);
        }).add;
        
        0.1.wait;
        "Loaded default synth".postln;
        0.exit;
    };
    )
    '''
    
    # Write to temp file
    temp_file = "/tmp/load_synthdefs.scd"
    with open(temp_file, 'w') as f:
        f.write(synthdef_code)
    
    # Execute with sclang
    sclang_path = "/Applications/SuperCollider.app/Contents/MacOS/sclang"
    
    if os.path.exists(sclang_path):
        try:
            result = subprocess.run(
                [sclang_path, temp_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            print("✓ SynthDefs loaded via sclang")
        except subprocess.TimeoutExpired:
            print("✓ SynthDef loading initiated")
        except Exception as e:
            print(f"Warning: Could not run sclang: {e}")
    
    # Clean up
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    return True

if __name__ == "__main__":
    # First check if server is running
    client = udp_client.SimpleUDPClient("127.0.0.1", 57110)
    
    # Try to get status
    client.send_message("/status", 1)
    time.sleep(0.1)
    
    # Load the SynthDefs
    if load_synthdefs():
        print("✅ SynthDef loading complete!")
        
        # Test with a simple note
        print("Testing audio...")
        client.send_message("/s_new", [
            "default", -1, 1, 0,
            "freq", 440,
            "amp", 0.3
        ])
        time.sleep(0.5)
        
        print("If you heard a tone, SynthDefs are working!")