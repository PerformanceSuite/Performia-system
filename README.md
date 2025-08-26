# Performia System

An ultra-low latency multi-agent musical performance system featuring 2-5 AI agents with distinct personalities, memories, and real-time musical collaboration capabilities. Now with **real-time audio input** support for interactive performances with live musicians.

## 🎵 Features

### Core Features
- **Ultra-Low Latency**: <15ms total system latency (3-7ms typical)
- **Multi-Agent Collaboration**: 2-5 agents performing together in real-time
- **Personality System**: Each agent has unique musical personality traits
- **Context-Aware Generation**: Agents respond to each other's musical phrases
- **Memory System**: Short-term and long-term pattern memory
- **Real-Time Synthesis**: Direct audio generation via SuperCollider

### 🎸 NEW: Live Audio Input Integration
- **Real-Time Guitar Analysis**: <8ms input-to-agent latency
- **Advanced Chord Detection**: Supports extended jazz chords (maj7, m9, etc.)
- **MIDI Pedal Control**: Trigger listening modes with foot pedals
- **Multiple Response Modes**: Chord Follow, Call & Response, Rhythmic Sync, Ambient Layer
- **Phrase Detection**: Agents understand musical phrases and respond contextually
- **Professional Audio Interface Support**: Optimized for Presonus Quantum 2626

## 🚀 Quick Start

### Prerequisites

1. Python 3.8+
2. SuperCollider (audio synthesis engine)
3. JACK Audio (Linux) or Core Audio (macOS) for lowest latency
4. Audio interface (optional, for live input features)
5. MIDI foot pedal (optional, for hands-free control)

### Installation

```bash
# Clone the repository
git clone https://github.com/PerformanceSuite/Performia-system.git
cd Performia-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install SuperCollider (macOS)
brew install supercollider
brew install portaudio  # For audio input support

# Install SuperCollider (Ubuntu/Debian)
sudo apt-get install supercollider
sudo apt-get install portaudio19-dev

# For audio input features, run setup script
chmod +x setup_input.sh
./setup_input.sh
```

### Running the System

#### Standard Mode (Autonomous Agents)
```bash
# Terminal 1: Start SuperCollider server
./scripts/start_server.sh

# Terminal 2: Run the musical agents
python src/main.py
```

#### Interactive Mode (With Live Input)
```bash
# Terminal 1: Start SuperCollider with input support
./scripts/start_server.sh --input

# Terminal 2: Run with input system enabled
python src/main.py --enable-input

# Or use the all-in-one script
./run_with_input.sh
```

## 🎛️ System Architecture

```
┌─────────────────────────────────────────────┐
│         Live Audio Input (NEW)              │
│   Guitar → Audio Interface → Analysis       │
│         MIDI Pedal → Control                │
├─────────────────────────────────────────────┤
│           AutoGen Orchestration             │
├─────────────────────────────────────────────┤
│  Agent 1    Agent 2    Agent 3    Agent 4  │
│  (Drums)    (Bass)    (Melody)  (Harmony)  │
│         + Listener Agent (NEW)              │
├─────────────────────────────────────────────┤
│        Shared Memory (Lock-Free)            │
│        < 0.1ms communication                │
├─────────────────────────────────────────────┤
│         SuperCollider Engine                │
│         2-5ms synthesis                     │
├─────────────────────────────────────────────┤
│         Audio Output (JACK/Core)            │
└─────────────────────────────────────────────┘
```

## 🎸 Audio Input Features

### Listening Modes

1. **Chord Follow Mode**: Agents harmonize with detected chord progressions
2. **Call & Response Mode**: Play a phrase, agents respond musically  
3. **Rhythmic Sync Mode**: Agents lock to your strumming patterns
4. **Ambient Layer Mode**: Creates atmospheric textures based on input

### MIDI Pedal Controls

- **Sustain Pedal (CC64)**: Start/stop listening to audio input
- **Mode Pedal (CC65)**: Cycle through listening modes
- **Expression Pedal (CC11)**: Control agent intensity/parameters
- **Tap Tempo (CC80)**: Manually set the tempo

### Audio Analysis Capabilities

- Pitch detection with <5ms latency
- Chord recognition (major, minor, 7th, extended jazz chords)
- Onset detection for rhythm tracking
- Dynamic level monitoring
- Phrase boundary detection

## 🎭 Agent Personalities

Each agent has personality traits that affect their musical behavior:

- **Aggression** (0-1): Affects dynamics, dissonance, and rhythmic intensity
- **Creativity** (0-1): Controls pattern variation and experimental choices
- **Responsiveness** (0-1): How much the agent responds to others
- **Stability** (0-1): Tendency to maintain patterns vs. change
- **Leader Tendency** (0-1): Likelihood to initiate musical phrases

The **Listener Agent** (NEW) has additional traits:
- **Input Sensitivity** (0-1): How closely it follows input audio
- **Interpretation Style**: Literal vs. abstract response to input

## 📊 Performance Metrics

### Core System
- **Agent Communication**: <0.1ms via shared memory
- **Audio Synthesis**: 2-5ms with 64-sample buffers  
- **Total System Latency**: 3-7ms (target: <15ms)
- **Concurrent Agents**: Up to 5 with maintained latency

### Audio Input System (NEW)
- **Hardware Input Latency**: 1-2ms (Quantum 2626 @ 64 samples)
- **Analysis Latency**: 5-6ms (pitch/chord detection)
- **Input-to-Agent**: <8ms total
- **Input-to-Audio Output**: <12ms with synthesis

## 🛠️ Configuration

Edit `config/config.yaml` to customize:
- Number of agents and roles
- Tempo and key signature
- Audio buffer sizes
- Personality parameters
- Input device selection (NEW)
- MIDI pedal mappings (NEW)
- Analysis parameters (NEW)

### Audio Interface Setup (NEW)

For Presonus Quantum 2626 or similar interfaces:

1. Set sample rate to 48kHz
2. Use minimum buffer size (64 samples)
3. Route guitar to inputs 1-2
4. Connect MIDI pedals to MIDI input
5. Enable "Low Latency Monitoring" mode

## 📁 Project Structure

```
Performia-system/
├── src/
│   ├── main.py                 # Entry point
│   ├── agents/
│   │   ├── base_agent.py       # Base musical agent
│   │   ├── drum_agent.py       # Drum specialist
│   │   ├── bass_agent.py       # Bass specialist
│   │   ├── melody_agent.py     # Melody specialist
│   │   ├── harmony_agent.py    # Harmony specialist
│   │   └── listener_agent.py   # Input processor (NEW)
│   ├── analysis/               # Audio analysis (NEW)
│   │   ├── audio_analyzer.py   # Real-time analysis
│   │   ├── chord_detector.py   # Chord recognition
│   │   └── phrase_detector.py  # Phrase boundaries
│   ├── controllers/            # Input control (NEW)
│   │   ├── audio_input.py      # Audio interface
│   │   └── midi_controller.py  # MIDI pedal handler
│   ├── engine/
│   │   ├── supercollider.py    # SC integration
│   │   └── audio_engine.py     # Audio management
│   ├── integration/            # System integration (NEW)
│   │   └── input_system.py     # Input coordination
│   ├── memory/
│   │   ├── shared_memory.py    # Lock-free buffers
│   │   └── pattern_memory.py   # Musical patterns
│   └── personality/
│       └── personality.py      # Personality system
├── config/
│   ├── config.yaml             # Main configuration
│   └── personalities.json      # Personality presets
├── scripts/
│   ├── start_server.sh        # Start SC server
│   ├── measure_latency.py     # Latency testing
│   └── calibrate_input.py     # Input calibration (NEW)
├── sc/                         # SuperCollider files (NEW)
│   └── audio_input.scd         # Input processing
├── tests/
│   ├── test_latency.py        # Performance tests
│   └── test_input_system.py   # Input tests (NEW)
├── docs/
│   ├── SETUP.md               # Detailed setup guide
│   ├── ARCHITECTURE.md        # System design
│   ├── API.md                 # API documentation
│   └── audio_input_integration.md  # Input guide (NEW)
├── setup_input.sh             # Input setup script (NEW)
├── run_with_input.sh          # Run with input (NEW)
└── requirements.txt           # Python dependencies
```

## 🔧 Development

### Running Tests

```bash
# Run all tests
pytest

# Run latency tests
python scripts/measure_latency.py

# Test SuperCollider connection
python tests/test_sc_connection.py

# Test audio input system (NEW)
python tests/test_input_system.py

# Calibrate input levels (NEW)
python scripts/calibrate_input.py
```

### Adding New Agent Types

1. Create new agent class inheriting from `BaseMusicalAgent`
2. Define personality parameters
3. Implement `generate_and_play()` method
4. Register in agent factory

### Customizing Input Response (NEW)

1. Edit `src/agents/listener_agent.py` for custom response strategies
2. Modify chord detection in `src/analysis/chord_detector.py`
3. Add new MIDI mappings in `config/config.yaml`

## 🐛 Troubleshooting

### High Latency Issues

1. Reduce audio buffer size to 64 samples
2. Enable real-time scheduling
3. Check CPU governor settings
4. Disable WiFi/Bluetooth during performance

### Audio Glitches

1. Increase buffer size slightly (128 samples)
2. Check for competing audio applications
3. Verify JACK/Core Audio configuration

### Input System Issues (NEW)

1. **No Input Detected**: Check interface routing and gain levels
2. **MIDI Not Working**: Run `python -c "import mido; print(mido.get_input_names())"`
3. **High Input Latency**: Reduce buffer size in audio interface settings
4. **Poor Chord Detection**: Ensure clean guitar signal, adjust confidence threshold

## 📚 Documentation

- [Setup Guide](docs/SETUP.md) - Detailed installation and configuration
- [Architecture](docs/ARCHITECTURE.md) - System design and components
- [API Reference](docs/API.md) - Programming interface
- [Audio Input Guide](docs/audio_input_integration.md) - Live input setup and usage (NEW)

## 🎮 Usage Examples

### Basic Performance
```python
from src.main import PerformiaSystem

system = PerformiaSystem()
system.start_performance(duration_minutes=5)
```

### Interactive Session with Guitar (NEW)
```python
from src.integration import InputSystem

# Initialize with input
system = InputSystem(enable_audio=True, enable_midi=True)
system.set_listening_mode('chord_follow')
system.start()

# System now responds to your playing!
```

### Custom Personality
```python
from src.personality import Personality

jazzy = Personality(
    aggression=0.3,
    creativity=0.9,
    responsiveness=0.7,
    stability=0.5
)
system.add_agent('jazz_piano', personality=jazzy)
```

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to the main branch.

### Areas for Contribution

- New agent personality types
- Additional listening modes
- Visual interface development
- Machine learning integration
- Performance optimizations

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- AutoGen framework by Microsoft
- SuperCollider community
- librosa for audio analysis
- Research papers on multi-agent musical systems
- The open-source audio processing community

## 📧 Contact

For questions and support, please open an issue on GitHub.

---

**Built with ❤️ for real-time musical collaboration between humans and AI**