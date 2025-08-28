# Performia System Architecture v2.0

## System Overview

Performia is an ultra-low latency (<8ms) multi-agent musical performance system that enables real-time collaboration between AI agents and human musicians. The system achieves professional audio performance through process isolation, shared memory communication, and multi-core audio processing.

## Core Architecture Principles

### 1. Process Isolation
- **GUI Process**: User interface, visualization, control (low priority)
- **Control Process**: Agent AI, decision making, pattern generation (normal priority)  
- **Audio Process**: Sound synthesis, real-time processing (real-time priority)

### 2. Zero-Copy Communication
- Shared memory buffers for audio events
- Lock-free ring buffers for thread safety
- Atomic operations for synchronization

### 3. Multi-Core Audio Processing
- Supernova server with parallel groups
- Each agent assigned to dedicated CPU core
- No blocking between audio streams

## Detailed Component Architecture

### Audio Engine Layer

#### Supernova Configuration
```
┌──────────────────────────────────────────┐
│         Supernova Server (RT Priority)    │
├──────────────────────────────────────────┤
│  ParGroup 0 (CPU 0): Drum Agent          │
│  ParGroup 1 (CPU 1): Bass Agent          │
│  ParGroup 2 (CPU 2): Melody Agent        │
│  ParGroup 3 (CPU 3): Harmony Agent       │
│  ParGroup 4 (CPU 4): Input Analysis      │
├──────────────────────────────────────────┤
│  Audio Buses: 128 @ 48kHz                │
│  Control Rate: 750Hz (64 samples)        │
│  Hardware Buffer: 128 samples (2.6ms)    │
└──────────────────────────────────────────┘
```

#### SynthDef Architecture
- **Efficiency First**: Minimal CPU per voice
- **Modular Design**: Reusable components
- **Bus Routing**: Direct connections, no mixing latency
- **Resource Pooling**: Pre-allocated nodes

### Communication Layer

#### Shared Memory Layout
```
┌─────────────────────────────────────────┐
│       Shared Memory Buffer (1MB)        │
├─────────────────────────────────────────┤
│  Header (64 bytes)                      │
│  ├─ Write Position (atomic)             │
│  ├─ Read Positions[4] (per consumer)    │
│  └─ Sequence Numbers                    │
├─────────────────────────────────────────┤
│  Event Ring Buffer (1023KB)             │
│  ├─ Musical Events (32 bytes each)      │
│  │  ├─ Timestamp (8 bytes)             │
│  │  ├─ Agent ID (4 bytes)              │
│  │  ├─ Event Type (4 bytes)            │
│  │  ├─ Pitch/Drum (4 bytes)            │
│  │  ├─ Velocity (4 bytes)              │
│  │  └─ Parameters (8 bytes)            │
│  └─ Capacity: ~32,000 events           │
└─────────────────────────────────────────┘
```

#### OSC Protocol (Control Channel)
- **Pattern Changes**: High-level musical decisions
- **Tempo/Key Updates**: Global parameters
- **System Commands**: Start/stop/reset
- **Non-Critical Path**: Can tolerate 5-10ms latency

### Agent Intelligence Layer

#### Agent Architecture
```python
class MusicalAgent:
    def __init__(self, role, personality):
        self.shared_memory = SharedMemoryBuffer()
        self.pattern_engine = SCPatternController()
        self.decision_maker = AgentAI(personality)
    
    async def think(self):
        # AI decisions at 10-30Hz
        decision = await self.decision_maker.next_action()
        
    def act(self):
        # Write to shared memory (microseconds)
        self.shared_memory.write_event(decision)
```

#### Pattern Generation Strategy
- **SuperCollider Patterns**: Sample-accurate timing
- **Python Control**: High-level musical decisions
- **Hybrid Approach**:
  - SC: Micro-timing, note generation
  - Python: Phrase structure, harmony progression

### Input Processing Pipeline

#### Audio Input Chain
```
Guitar → Audio Interface → Supernova → Analysis
         (Quantum 2626)     (ParGroup 4)
                                ↓
                          Pitch Detection
                          Onset Detection  
                          Amplitude Tracking
                                ↓
                          Shared Memory
                                ↓
                          Agent Decisions
```

#### Latency Breakdown
- Hardware Buffer: 2.6ms (128 samples @ 48kHz)
- Analysis Window: 1.3ms (64 samples)
- Detection Algorithm: 0.5ms
- Memory Write: <0.01ms
- Agent Response: 0.5ms
- Sound Generation: 0.5ms
- **Total: ~5ms input to output**

### GUI Architecture

#### Read-Only Shared Memory Access
```javascript
class GUIDataReader {
    constructor() {
        this.sharedMem = new SharedMemoryReader('PerformiaBuffer')
        this.updateRate = 30 // fps
    }
    
    readAgentStates() {
        // Non-blocking read from shared memory
        return this.sharedMem.readLatest()
    }
}
```

#### WebSocket Updates
- 30fps update rate
- Compressed JSON payloads
- Client-side interpolation
- No impact on audio thread

## Performance Optimizations

### Memory Management
- **Pre-allocation**: All buffers allocated at startup
- **Object Pooling**: Reuse event objects
- **Zero GC**: No garbage collection in audio path
- **Cache Alignment**: 64-byte aligned structures

### Threading Model
```
Main Thread (Python)
├─ GUI Thread (Flask/SocketIO)
├─ Agent Thread Pool (4 threads)
│  ├─ Agent 0 (Drums)
│  ├─ Agent 1 (Bass)
│  ├─ Agent 2 (Melody)
│  └─ Agent 3 (Harmony)
└─ Audio Thread (Supernova control)
```

### CPU Affinity
- Audio: Cores 0-3 (isolated)
- Agents: Cores 4-5 (shared)
- GUI: Cores 6-7 (best effort)
- System: Core 7 (interrupts)

## Scalability Considerations

### Horizontal Scaling
- Add more agents: Increase shared memory size
- More CPU cores: Extend ParGroup allocation
- Multiple machines: Network bridge for distributed ensemble

### Vertical Scaling
- Lower latency: Reduce buffer to 32 samples
- Higher quality: Increase sample rate to 96kHz
- More complex synthesis: Add DSP cores

## Security & Safety

### Process Isolation Benefits
- GUI crash cannot affect audio
- Agent failure isolated to single thread
- Shared memory protected by OS

### Audio Safety
- Limiter on master bus
- Automatic gain reduction
- DC offset removal
- Click/pop suppression

## Monitoring & Debugging

### Performance Metrics
```python
class PerformanceMonitor:
    metrics = {
        'audio_latency': RingBuffer(1000),
        'agent_decision_time': RingBuffer(1000),
        'memory_usage': RingBuffer(100),
        'cpu_per_core': [RingBuffer(100) for _ in range(8)]
    }
```

### Debug Interfaces
- OSC message logging
- Shared memory dump utility
- Agent decision replay
- Latency measurement tools

## Implementation Phases

### Phase 1: Foundation (Week 1)
- Supernova setup and testing
- Shared memory implementation
- Basic process isolation

### Phase 2: Intelligence (Week 2)
- SC Pattern system
- Agent decision making
- Inter-agent communication

### Phase 3: Integration (Week 3)
- Audio input pipeline
- MIDI control system
- Full system integration

### Phase 4: Optimization (Week 4)
- Latency optimization
- Performance tuning
- Production hardening

## Technology Stack

### Core Technologies
- **Language**: Python 3.11+ (with asyncio)
- **Audio Engine**: SuperCollider 3.13+ (Supernova)
- **IPC**: multiprocessing.shared_memory
- **GUI**: Flask + SocketIO + React
- **AI/ML**: PyTorch for agent intelligence

### Key Libraries
- **pythonosc**: OSC communication
- **numpy**: Signal processing
- **numba**: JIT compilation
- **psutil**: Process management
- **mido**: MIDI handling

## Configuration Management

### Runtime Configuration
```yaml
audio:
  engine: supernova
  sample_rate: 48000
  block_size: 64
  hardware_buffer: 128
  cpu_cores: 4

memory:
  buffer_size: 1048576  # 1MB
  event_size: 32
  ring_buffers: 4

performance:
  target_latency_ms: 8
  gui_fps: 30
  agent_think_rate: 20
```

## Deployment Architecture

### Development Setup
- Single machine, all processes local
- Reduced core allocation
- Debug logging enabled

### Production Setup
- Dedicated audio machine
- Network-attached GUI
- Redundant agent processes
- Real-time kernel patches

## Future Enhancements

### Planned Features
- Distributed ensemble (network agents)
- Machine learning optimization
- Visual programming interface
- Recording and playback system

### Research Areas
- Sub-millisecond latency techniques
- Quantum computing for pattern generation
- Neural audio synthesis
- Gesture recognition integration