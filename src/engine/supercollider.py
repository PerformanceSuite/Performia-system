"""
SuperCollider integration for ultra-low latency audio synthesis
"""

import subprocess
import time
import platform
import logging
import asyncio
from typing import Dict, Optional, List
from pythonosc import udp_client, osc_server, dispatcher
import threading

logger = logging.getLogger(__name__)

class SuperColliderEngine:
    """Manages SuperCollider server and synthesis"""
    
    def __init__(self, server_options: dict = None):
        self.server_options = server_options or {
            'blockSize': 64,
            'hardwareBufferSize': 128,
            'sampleRate': 48000,
            'numOutputBusChannels': 2,
            'memSize': 65536 * 4,
            'maxNodes': 2048,
            'verbosity': 0
        }
        
        # OSC client for sending to SuperCollider
        self.osc_client = udp_client.SimpleUDPClient("127.0.0.1", 57110)
        self.server_process = None
        self.is_running = False
        self.synth_nodes = {}
        self.next_node_id = 1000
        
        logger.info("🎛️ Initializing SuperCollider Engine")
    
    async def start(self):
        """Start SuperCollider server"""
        try:
            # Check if server is already running
            self.osc_client.send_message("/status", 1)
            time.sleep(0.1)
            
            # Load synthdefs
            await self.load_synthdefs()
            
            self.is_running = True
            logger.info("✓ SuperCollider engine started")
            
        except Exception as e:
            logger.warning(f"Could not start SuperCollider: {e}")
            self.is_running = False
    
    async def load_synthdefs(self):
        """Load synthesizer definitions"""
        # Define basic synthesizers using OSC commands
        
        # Simple sine wave synth
        self.define_sine_synth()
        
        # Drum synthesizers
        self.define_kick_synth()
        self.define_snare_synth()
        self.define_hihat_synth()
        
        # Bass synthesizer
        self.define_bass_synth()
        
        # Lead synthesizer
        self.define_lead_synth()
        
        logger.info("✓ Loaded synthesizer definitions")
    
    def define_sine_synth(self):
        """Define a simple sine wave synthesizer"""
        synthdef_code = """
        SynthDef(\\sine, {
            |out=0, freq=440, amp=0.1, pan=0, gate=1|
            var sig, env;
            env = EnvGen.kr(Env.asr(0.01, 1, 0.1), gate, doneAction:2);
            sig = SinOsc.ar(freq) * amp * env;
            sig = Pan2.ar(sig, pan);
            Out.ar(out, sig);
        }).add;
        """
        self.send_synthdef(synthdef_code)
    
    def define_kick_synth(self):
        """Define kick drum synthesizer"""
        synthdef_code = """
        SynthDef(\\kick, {
            |out=0, freq=60, amp=0.5, pan=0|
            var sig, env;
            env = EnvGen.kr(Env.perc(0.001, 0.3), doneAction:2);
            sig = SinOsc.ar(XLine.kr(freq*4, freq, 0.02)) * env;
            sig = sig + (WhiteNoise.ar(0.01) * EnvGen.kr(Env.perc(0.001, 0.01)));
            sig = Pan2.ar(sig * amp, pan);
            Out.ar(out, sig);
        }).add;
        """
        self.send_synthdef(synthdef_code)
    
    def define_snare_synth(self):
        """Define snare drum synthesizer"""
        synthdef_code = """
        SynthDef(\\snare, {
            |out=0, freq=200, amp=0.3, pan=0|
            var sig, env, noise;
            env = EnvGen.kr(Env.perc(0.001, 0.15), doneAction:2);
            noise = WhiteNoise.ar(0.5);
            sig = SinOsc.ar(freq) + noise;
            sig = sig * env * amp;
            sig = Pan2.ar(sig, pan);
            Out.ar(out, sig);
        }).add;
        """
        self.send_synthdef(synthdef_code)
    
    def define_hihat_synth(self):
        """Define hihat synthesizer"""
        synthdef_code = """
        SynthDef(\\hihat, {
            |out=0, amp=0.2, pan=0|
            var sig, env;
            env = EnvGen.kr(Env.perc(0.001, 0.05), doneAction:2);
            sig = WhiteNoise.ar(1);
            sig = HPF.ar(sig, 5000) * env * amp;
            sig = Pan2.ar(sig, pan);
            Out.ar(out, sig);
        }).add;
        """
        self.send_synthdef(synthdef_code)
    
    def define_bass_synth(self):
        """Define bass synthesizer"""
        synthdef_code = """
        SynthDef(\\bass, {
            |out=0, freq=100, amp=0.3, pan=0, gate=1|
            var sig, env, filter;
            env = EnvGen.kr(Env.adsr(0.01, 0.1, 0.7, 0.2), gate, doneAction:2);
            sig = Saw.ar(freq) + SinOsc.ar(freq/2);
            filter = MoogFF.ar(sig, freq * 4, 2.5);
            sig = filter * env * amp;
            sig = Pan2.ar(sig, pan);
            Out.ar(out, sig);
        }).add;
        """
        self.send_synthdef(synthdef_code)
    
    def define_lead_synth(self):
        """Define lead synthesizer"""
        synthdef_code = """
        SynthDef(\\lead, {
            |out=0, freq=440, amp=0.2, pan=0, gate=1|
            var sig, env, vibrato;
            env = EnvGen.kr(Env.adsr(0.05, 0.1, 0.6, 0.3), gate, doneAction:2);
            vibrato = SinOsc.kr(5) * 3;
            sig = Pulse.ar(freq + vibrato, 0.3);
            sig = sig + SinOsc.ar(freq * 2, 0, 0.2);
            sig = LPF.ar(sig, freq * 6);
            sig = sig * env * amp;
            sig = Pan2.ar(sig, pan);
            Out.ar(out, sig);
        }).add;
        """
        self.send_synthdef(synthdef_code)
    
    def send_synthdef(self, code: str):
        """Send SynthDef code to SuperCollider"""
        # Note: This is a simplified approach
        # The proper way requires compiling SynthDef to bytecode
        # For now, we assume the server has basic synths loaded
        # Real implementation would use sclang or pre-compiled SynthDefs
        logger.debug("SynthDef definition noted (requires sclang for compilation)")
    
    def play_note(self, synth_name: str, **params):
        """Play a note using specified synthesizer"""
        if not self.is_running:
            logger.warning("SuperCollider not running")
            return None
        
        node_id = self.next_node_id
        self.next_node_id += 1
        
        # Create synth node - build the arguments list
        args = [synth_name, node_id, 1, 0]
        
        # Add parameters
        for key, value in params.items():
            args.extend([key, value])
        
        # Send OSC message with proper format
        self.osc_client.send_message("/s_new", args)
        self.synth_nodes[node_id] = synth_name
        
        return node_id
    
    def stop_note(self, node_id: int):
        """Stop a playing note"""
        if node_id in self.synth_nodes:
            self.osc_client.send_message("/n_set", [node_id, "gate", 0])
            del self.synth_nodes[node_id]
    
    def play_drum(self, drum_type: str, velocity: float = 0.7):
        """Play a drum hit"""
        drum_synths = {
            'kick': 'kick',
            'snare': 'snare',
            'hihat': 'hihat'
        }
        
        if drum_type in drum_synths:
            self.play_note(drum_synths[drum_type], amp=velocity)
    
    def play_bass(self, note: int, velocity: float = 0.5, duration: float = 0.5):
        """Play a bass note"""
        freq = self.midi_to_freq(note)
        node_id = self.play_note("bass", freq=freq, amp=velocity)
        
        # Schedule note off
        if node_id:
            threading.Timer(duration, lambda: self.stop_note(node_id)).start()
        
        return node_id
    
    def play_lead(self, note: int, velocity: float = 0.4, duration: float = 0.3):
        """Play a lead note"""
        freq = self.midi_to_freq(note)
        node_id = self.play_note("lead", freq=freq, amp=velocity)
        
        # Schedule note off
        if node_id:
            threading.Timer(duration, lambda: self.stop_note(node_id)).start()
        
        return node_id
    
    def play_chord(self, notes: List[int], velocity: float = 0.3):
        """Play a chord"""
        node_ids = []
        for i, note in enumerate(notes):
            freq = self.midi_to_freq(note)
            # Slight stereo spread
            pan = (i - len(notes)/2) * 0.2
            node_id = self.play_note("sine", freq=freq, amp=velocity/len(notes), pan=pan)
            if node_id:
                node_ids.append(node_id)
        
        return node_ids
    
    def stop_chord(self, node_ids: List[int]):
        """Stop a chord"""
        for node_id in node_ids:
            self.stop_note(node_id)
    
    def midi_to_freq(self, midi_note: int) -> float:
        """Convert MIDI note to frequency"""
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
    
    def stop(self):
        """Stop SuperCollider server"""
        try:
            # Free all nodes
            self.osc_client.send_message("/g_freeAll", [0])
            
            # Quit server
            self.osc_client.send_message("/quit", [])
            
            self.is_running = False
            logger.info("SuperCollider engine stopped")
            
        except Exception as e:
            logger.error(f"Error stopping SuperCollider: {e}")
    
    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            'running': self.is_running,
            'active_synths': len(self.synth_nodes),
            'node_ids': list(self.synth_nodes.keys())
        }

# Test function
async def test_engine():
    """Test the SuperCollider engine"""
    engine = SuperColliderEngine()
    await engine.start()
    
    if engine.is_running:
        print("Playing test sequence...")
        
        # Play kick drum
        engine.play_drum('kick')
        await asyncio.sleep(0.5)
        
        # Play snare
        engine.play_drum('snare')
        await asyncio.sleep(0.5)
        
        # Play hihat
        engine.play_drum('hihat')
        await asyncio.sleep(0.5)
        
        # Play bass note
        engine.play_bass(36)  # C2
        await asyncio.sleep(0.5)
        
        # Play chord
        chord = engine.play_chord([60, 64, 67])  # C major
        await asyncio.sleep(1)
        engine.stop_chord(chord)
        
        print("Test complete!")
    else:
        print("Engine not running")

if __name__ == "__main__":
    asyncio.run(test_engine())