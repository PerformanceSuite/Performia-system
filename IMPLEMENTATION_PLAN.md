# Performia System - Implementation Plan v2.0

## Executive Summary
Ultra-low latency (<8ms) multi-agent musical system using Supernova (multi-core SuperCollider), shared memory communication, and process isolation for zero GUI impact on audio performance.

## Current State
- ✅ GUI working (simulated data) 
- ✅ Basic agents running (simplified version)
- ⚠️ SuperCollider installed but not connected
- ❌ Audio synthesis not producing sound
- ❌ Shared memory architecture not implemented
- ❌ Process isolation not configured
- ❌ Live audio input not connected
- ❌ MIDI control not active

---

## Technical Architecture Decisions

### Core Decisions Made
1. **Audio Engine**: Supernova (multi-core) instead of scsynth
2. **Pattern Generation**: SuperCollider Patterns (sample-accurate timing)
3. **Communication**: Hybrid shared memory (critical path) + OSC (control)
4. **Process Isolation**: Separate processes for GUI, Control, and Audio
5. **Priority Management**: Real-time priority for audio, normal for GUI

### Target Performance
- **Agent Decision → Sound**: <2ms (shared memory)
- **Input → Agent Response**: <5ms (direct analysis)
- **Total System Latency**: <8ms
- **GUI Updates**: 30fps with ZERO audio impact

---

## System Architecture

```
┌─────────────────────────────────────────────────┐
│                GUI Process                       │
│         (Normal Priority, Isolated)              │
│         Port 5001, Read-only Memory             │
└────────────────┬────────────────────────────────┘
                 │ Shared Memory (Read-only)
┌────────────────┼────────────────────────────────┐
│          Audio Control Process                   │
│         (High Priority Python)                   │
│   ┌─────────────────────────────────────┐       │
│   │  Agent Decision Making (AI/ML)      │       │
│   │  - Musical patterns                 │       │
│   │  - Harmonic decisions              │       │
│   │  - Inter-agent communication       │       │
│   └─────────────────────────────────────┘       │
│                 ↓                                │
│   ┌─────────────────────────────────────┐       │
│   │  Shared Memory Ring Buffer          │       │
│   │  (Lock-free, Wait-free)            │       │
│   │  - Note events                     │       │
│   │  - Timing information              │       │
│   │  - Agent states                    │       │
│   └─────────────────────────────────────┘       │
└────────────────┬────────────────────────────────┘
                 │ Direct Memory Access + OSC
┌────────────────┼────────────────────────────────┐
│           Supernova Server                       │
│         (Real-time Priority)                     │
│   ┌─────────────────────────────────────┐       │
│   │  ParGroup: Drums (CPU 0)            │       │
│   │  ParGroup: Bass (CPU 1)             │       │
│   │  ParGroup: Melody (CPU 2)           │       │
│   │  ParGroup: Harmony (CPU 3)          │       │
│   │  ParGroup: Input Analysis (CPU 4)   │       │
│   └─────────────────────────────────────┘       │
│            ↓ Audio Buses ↓                       │
│   ┌─────────────────────────────────────┐       │
│   │  Master Output → Quantum 2626       │       │
│   └─────────────────────────────────────┘       │
└──────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation - Supernova & Shared Memory (Week 1)

### 1.1 Supernova Setup (Day 1-2)
```bash
# Launch command for ultra-low latency
supernova -u 57110 -a 1024 -i 2 -o 2 \
  -z 64 -Z 128 -S 48000 \
  -m 262144 -n 4096 -d 256 \
  -t 4 -H "Quantum 2626"
```

**Parameters explained**:
- `-z 64`: Control block size (1.3ms @ 48kHz)
- `-Z 128`: Hardware buffer (2.6ms @ 48kHz)  
- `-t 4`: Use 4 threads for parallel groups
- `-H`: Hardware device selection

### 1.2 Shared Memory Implementation (Day 3-4)

**Create `src/memory/shared_buffer.py`**:
```python
import mmap
import struct
import ctypes
from multiprocessing import shared_memory

class AudioEventBuffer:
    """Lock-free ring buffer for audio events"""
    
    EVENT_SIZE = 32  # bytes per event
    BUFFER_SIZE = 1024 * 1024  # 1MB
    
    def __init__(self, name="PerformiaBuffer"):
        self.shm = shared_memory.SharedMemory(
            create=True, 
            size=self.BUFFER_SIZE,
            name=name
        )
        self.buffer = self.shm.buf
        self.write_pos = ctypes.c_uint64(0)
        self.read_pos = ctypes.c_uint64(0)
    
    def write_event(self, agent_id, event_type, pitch, velocity, timing):
        """Write musical event to buffer - ULTRA fast"""
        # Pack event data
        data = struct.pack('iiffq', 
            agent_id, event_type, pitch, velocity, timing
        )
        
        # Atomic write to ring buffer
        pos = self.write_pos.value % (self.BUFFER_SIZE - self.EVENT_SIZE)
        self.buffer[pos:pos+self.EVENT_SIZE] = data
        self.write_pos.value += self.EVENT_SIZE
```

### 1.3 SuperCollider Memory Reader Plugin (Day 5)

**Create `sc/PerformiaMemoryReader.sc`**:
```supercollider
PerformiaMemoryReader : UGen {
    *ar { |bufferName="PerformiaBuffer"|
        ^this.multiNew('audio', bufferName)
    }
    
    checkInputs {
        // Read shared memory every control block
        // Parse events and trigger synths
    }
}
```

---

## Phase 2: Musical Intelligence with SC Patterns (Week 2)

### 2.1 Pattern System Architecture (Day 1-2)

**Create `sc/patterns/AgentPatterns.scd`**:
```supercollider
// Drum Agent Pattern
Pdef(\drumAgent,
    Pbind(
        \instrument, \drum,
        \type, \note,
        \dur, Pseq([0.25, 0.25, 0.5], inf),
        \drum, Prand([\kick, \snare, \hihat], inf),
        \amp, Pwhite(0.7, 1.0),
        \group, ~drumGroup,
        \out, ~drumBus
    )
);

// Bass Agent Pattern  
Pdef(\bassAgent,
    Pbind(
        \instrument, \bass,
        \degree, Pseq([0, 0, 4, 5], inf),
        \dur, Pseq([0.5, 0.5, 0.25, 0.75], inf),
        \octave, 3,
        \legato, 0.9,
        \group, ~bassGroup,
        \out, ~bassBus
    )
);
```

### 2.2 SynthDef Library (Day 3-4)

**Create `sc/synthdefs/CoreSynths.scd`**:
```supercollider
// Ultra-fast kick drum
SynthDef(\kick, { |out=0, amp=1|
    var sig, env;
    env = EnvGen.kr(Env.perc(0.001, 0.3), doneAction: 2);
    sig = SinOsc.ar(XLine.kr(800, 40, 0.01));
    sig = sig + (WhiteNoise.ar(0.1) * EnvGen.kr(Env.perc(0.001, 0.01)));
    Out.ar(out, sig * env * amp);
}).add;

// Sub bass with filter
SynthDef(\bass, { |out=0, freq=100, amp=0.8, cutoff=1000, res=0.5|
    var sig, env;
    env = EnvGen.kr(Env.adsr(0.001, 0.1, 0.7, 0.2), \gate.kr(1), doneAction: 2);
    sig = Saw.ar(freq) + SinOsc.ar(freq * 0.5, 0, 0.5);
    sig = RLPF.ar(sig, cutoff, res);
    Out.ar(out, sig * env * amp);
}).add;
```

### 2.3 Pattern Control from Python (Day 5)

**Create `src/patterns/pattern_controller.py`**:
```python
class PatternController:
    def __init__(self, osc_client):
        self.osc = osc_client
        
    def set_drum_pattern(self, pattern_name):
        # Send high-level pattern change
        self.osc.send_message("/pattern/drum", pattern_name)
        
    def set_harmonic_progression(self, chords):
        # Update harmonic context
        self.osc.send_message("/harmony/chords", chords)
```

---

## Phase 3: Process Isolation & Priority (Week 2)

### 3.1 Process Manager (Day 6-7)

**Create `src/core/process_manager.py`**:
```python
import multiprocessing as mp
import os
import psutil

class PerformiaProcessManager:
    def __init__(self):
        self.gui_process = None
        self.audio_process = None
        self.control_process = None
        self.shared_buffer = None
        
    def start(self):
        # Create shared memory
        self.shared_buffer = AudioEventBuffer()
        
        # Start processes with proper priority
        self.audio_process = mp.Process(
            target=self.run_audio_engine,
            name="PerformiaAudio"
        )
        self.audio_process.start()
        
        # Set real-time priority for audio
        p = psutil.Process(self.audio_process.pid)
        p.nice(-20)  # Highest priority on Unix
        
        # Start control process (normal priority)
        self.control_process = mp.Process(
            target=self.run_control_system,
            name="PerformiaControl"
        )
        self.control_process.start()
        
        # Start GUI (low priority)
        self.gui_process = mp.Process(
            target=self.run_gui,
            name="PerformiaGUI"
        )
        self.gui_process.start()
        p = psutil.Process(self.gui_process.pid)
        p.nice(10)  # Lower priority
```

---

## Phase 4: Audio Input Integration (Week 3)

### 4.1 Real-time Analysis in SuperCollider (Day 1-2)

**Create `sc/input/InputAnalysis.scd`**:
```supercollider
// Real-time pitch detection with ultra-low latency
SynthDef(\inputAnalyzer, { |in=0, out=0|
    var input, pitch, hasFreq, amplitude, onset;
    
    input = SoundIn.ar(in);
    amplitude = Amplitude.kr(input, 0.001, 0.01);
    
    # pitch, hasFreq = Pitch.kr(input, 
        initFreq: 440,
        minFreq: 80,
        maxFreq: 2000,
        execFreq: 100,  // Fast tracking
        maxBinsPerOctave: 16,
        ampThreshold: 0.02,
        peakThreshold: 0.5
    );
    
    onset = Onsets.kr(FFT(LocalBuf(512), input), 0.5);
    
    // Send to shared memory
    SendReply.kr(Impulse.kr(100), '/pitch', [pitch, hasFreq, amplitude]);
    SendReply.kr(onset, '/onset', amplitude);
}).add;
```

### 4.2 MIDI Integration (Day 3)

**Update `src/controllers/midi_controller.py`**:
```python
import mido
from threading import Thread

class MIDIPedalController:
    def __init__(self, shared_buffer):
        self.buffer = shared_buffer
        self.mode = 'chord_follow'
        self.listening = False
        
    def start(self):
        # Open MIDI input
        self.port = mido.open_input('Quantum 2626 MIDI')
        
        # Start listening thread
        Thread(target=self._midi_loop, daemon=True).start()
        
    def _midi_loop(self):
        for msg in self.port:
            if msg.type == 'control_change':
                if msg.control == 64:  # Sustain pedal
                    self.listening = msg.value > 63
                    self.buffer.write_event(
                        agent_id=0,
                        event_type=1,  # Control event
                        pitch=0,
                        velocity=msg.value,
                        timing=time.time_ns()
                    )
```

---

## Phase 5: Integration & Testing (Week 4)

### 5.1 Main System Integration (Day 1-2)

**Update `src/main.py`**:
```python
async def main():
    # Initialize process manager
    manager = PerformiaProcessManager()
    
    # Start all processes
    manager.start()
    
    # Wait for initialization
    await asyncio.sleep(1)
    
    # Start performance
    logger.info("🎵 Performia System Running")
    logger.info(f"Audio Latency: <8ms target")
    
    # Monitor performance
    while True:
        latency = manager.measure_latency()
        if latency > 8:
            logger.warning(f"Latency spike: {latency}ms")
        await asyncio.sleep(0.1)
```

### 5.2 Latency Measurement (Day 3)

**Create `scripts/measure_system_latency.py`**:
```python
def measure_total_latency():
    """Measure actual system latency"""
    # Send test impulse to input
    # Measure time until output
    # Should be <8ms
    pass
```

---

## Implementation Schedule

### Week 1: Foundation
- [x] Day 1-2: Supernova setup and configuration
- [ ] Day 3-4: Shared memory implementation
- [ ] Day 5: SC memory reader plugin
- [ ] Day 6-7: Basic testing

### Week 2: Musical Intelligence & Process Isolation
- [ ] Day 1-2: SC Pattern system
- [ ] Day 3-4: SynthDef library
- [ ] Day 5: Pattern control from Python
- [ ] Day 6-7: Process isolation implementation

### Week 3: Input System
- [ ] Day 1-2: SC input analysis
- [ ] Day 3: MIDI integration
- [ ] Day 4-5: Connect to agents
- [ ] Day 6-7: Testing

### Week 4: Polish & Optimization
- [ ] Day 1-2: System integration
- [ ] Day 3: Latency measurement
- [ ] Day 4-5: Performance optimization
- [ ] Day 6-7: Documentation & demo

---

## Quick Start (Once Complete)

```bash
# 1. Start Supernova with optimal settings
./scripts/start_supernova.sh

# 2. Launch Performia system
python src/main.py --multiprocess --realtime

# 3. GUI automatically opens at http://localhost:5001

# 4. System is ready for guitar input and MIDI control!
```

---

## Success Metrics

### Performance Targets
- ✓ Agent Decision → Sound: <2ms
- ✓ Input → Agent Response: <5ms  
- ✓ Total System Latency: <8ms
- ✓ GUI: 30fps, zero audio impact
- ✓ CPU Usage: <40% total
- ✓ No audio dropouts at 64-sample buffer

### Musical Quality
- ✓ Sample-accurate timing
- ✓ Coherent harmonic progressions
- ✓ Responsive to input dynamics
- ✓ Rich, professional sound quality

---

## Critical Files to Create/Modify

### New Files Required
- `src/memory/shared_buffer.py` - Shared memory implementation
- `src/core/process_manager.py` - Process isolation
- `sc/patterns/*.scd` - SC Pattern definitions
- `sc/synthdefs/*.scd` - Optimized SynthDefs
- `sc/PerformiaMemoryReader.sc` - Memory reader UGen

### Files to Update
- `src/main.py` - Multi-process architecture
- `src/engine/supercollider.py` - Supernova integration
- `gui/app.py` - Read-only shared memory access
- `config/config.yaml` - Add supernova settings

---

## Next Immediate Actions

1. **Stop any running processes**:
```bash
pkill -f python
pkill -f scsynth
pkill -f supernova
```

2. **Test Supernova installation**:
```bash
which supernova
supernova -v
```

3. **Create shared memory test**:
```python
# test_shared_memory.py
from src.memory.shared_buffer import AudioEventBuffer
buffer = AudioEventBuffer()
buffer.write_event(1, 1, 60.0, 0.8, 0)
print("Shared memory test successful!")
```

4. **Begin Phase 1 implementation**

---

This plan provides a clear path to achieving <8ms latency with zero GUI impact using modern architecture patterns and SuperCollider's most advanced features.