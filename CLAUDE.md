# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Performia System is an ultra-low latency multi-agent musical performance system featuring:
- 2-5 AI agents with distinct personalities performing together in real-time
- Real-time audio input support for interactive performances with live musicians  
- <15ms total system latency (3-7ms typical)
- SuperCollider audio synthesis engine (using supernova for multi-core processing)
- AutoGen orchestration framework
- Modern web-based GUI with real-time visualization and mixing controls

## Key Commands

### Installation & Setup
```bash
# Complete system setup (backend + GUI + audio input)
chmod +x setup_all.sh && ./setup_all.sh

# Quick setup for input system only
chmod +x setup_input.sh && ./setup_input.sh

# Install Python dependencies in virtual environment
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### Running the System
```bash
# Run everything (backend + GUI) - Main launch command
./run_performia.sh

# Run backend only (standard mode - autonomous agents)
python src/main.py

# Run with audio input enabled
python src/main.py --enable-input

# Start GUI separately  
./start_gui.sh

# Access the GUI
# Modern GUI (default): http://localhost:5000
# Classic GUI: http://localhost:5000/classic
```

### Testing
```bash
# Run complete test suite
./test_all.sh

# Run pytest tests
pytest

# Test audio input system specifically
python tests/test_input_system.py

# Measure system latency
python scripts/measure_latency.py

# Calibrate input levels (for guitar/audio interface)
python scripts/calibrate_input.py
```

### Development
```bash
# Code formatting
black src/

# Linting
flake8 src/

# Type checking (if mypy configured)
mypy src/
```

## Architecture Overview

The system uses a multi-layer architecture optimized for ultra-low latency:

### Core Components

1. **Agent System** (`src/agents/`)
   - `BaseMusicalAgent` - Base class for all musical agents
   - `ensemble_manager.py` - Manages multi-agent coordination using AutoGen
   - `listener_agent.py` - Processes live audio input from guitar/instruments
   - Individual agents (drums, bass, melody, harmony) each with unique personalities

2. **Audio Engine** (`src/engine/`)
   - `supercollider.py` - SuperCollider integration for audio synthesis
   - Direct OSC communication for <5ms synthesis latency
   - Support for both SuperCollider and web audio backends

3. **Memory System** (`src/memory/`)
   - `shared_memory.py` - Lock-free ring buffers for <0.1ms agent communication
   - `pattern_memory.py` - Musical pattern storage and retrieval

4. **Input System** (`src/controllers/`, `src/analysis/`, `src/integration/`)
   - `audio_input.py` - Real-time audio capture from interfaces
   - `midi_controller.py` - MIDI pedal control for hands-free operation
   - `chord_detector.py` - Real-time chord recognition with <8ms latency
   - `input_system.py` - Coordinates input processing and agent responses

5. **Configuration** (`config/config.yaml`)
   - Central configuration for audio settings, agent personalities, MIDI mappings
   - Supports multiple listening modes (chord follow, call & response, etc.)

### Key Design Patterns

- **Lock-free Communication**: Agents communicate via shared memory buffers to minimize latency
- **Async Processing**: Uses asyncio for concurrent agent operations
- **Real-time Constraints**: Audio processing prioritized with dedicated threads
- **Modular Personalities**: Each agent has configurable traits (aggression, creativity, responsiveness, etc.)

## Important Configuration

The main configuration file is `config/config.yaml`:
- Audio buffer settings (sample_rate: 48000, block_size: 64 for lowest latency)
- Agent count and roles configuration
- Audio input device selection (e.g., "Presonus Quantum 2626")
- MIDI pedal mappings for control (sustain: CC64, mode: CC65, etc.)
- Performance settings (tempo, key, time signature)

## Audio Input Features

The system supports real-time interaction with live musicians:
- Guitar input with <8ms input-to-agent latency
- Advanced chord detection (major, minor, 7th, extended jazz chords)
- MIDI foot pedal control for hands-free mode switching
- Multiple response modes:
  - Chord Follow: Agents harmonize with detected chords
  - Call & Response: Agents respond to musical phrases
  - Rhythmic Sync: Lock to strumming patterns
  - Ambient Layer: Create atmospheric textures

## Dependencies

Key libraries used:
- `pyautogen`: Multi-agent orchestration framework
- `python-osc`: SuperCollider communication
- `librosa`: Audio analysis and feature extraction
- `sounddevice`: Real-time audio I/O
- `mido/python-rtmidi`: MIDI control
- `flask/flask-socketio`: Web GUI backend
- `numba`: JIT compilation for performance
- `numpy/scipy`: Signal processing

## Testing Approach

- Unit tests with pytest in `tests/` directory
- Performance/latency testing with `scripts/measure_latency.py`
- Audio input system testing with `tests/test_input_system.py`
- Use `pytest` for running the test suite
- Specific test files for components and input system validation

## Common Development Tasks

When adding new features:
1. New agent types: Inherit from `BaseMusicalAgent` and implement `generate_and_play()`
2. New listening modes: Modify `src/agents/listener_agent.py`
3. MIDI mappings: Update `config/config.yaml` pedal_mappings section
4. GUI features: Work in `gui/` directory with Flask/SocketIO setup
   - Modern GUI: `gui/templates/index_new.html`, `gui/static/style_new.css`, `gui/static/main_new.js`
   - Classic GUI: `gui/templates/index.html`, `gui/static/style.css`, `gui/static/main.js`

When debugging latency issues:
1. Check buffer sizes in config (reduce to 64 samples if possible)
2. Verify SuperCollider is running with real-time priority
3. Use `scripts/measure_latency.py` to identify bottlenecks
4. Monitor with performance_metrics logging enabled