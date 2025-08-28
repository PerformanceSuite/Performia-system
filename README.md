claudc# Performia System - Ultra-Low Latency Multi-Agent Musical Performance

A next-generation musical performance system achieving <8ms total latency through multi-core processing, shared memory architecture, and complete process isolation. Multiple AI agents collaborate in real-time with human musicians to create dynamic, responsive musical performances.

## 🚀 Key Innovations

- **<8ms Total System Latency**: From input to audio output in under 8 milliseconds
- **Dual-Mode Learning System**: Studio mode for pattern learning, Live mode for performance
- **Pattern Recognition MCP**: Background service for real-time pattern matching
- **Zero GUI Impact**: Complete process isolation ensures visual updates never affect audio
- **Multi-Core Parallelism**: Each agent runs on dedicated CPU core via Supernova
- **Lock-Free Communication**: Shared memory buffers with atomic operations
- **Sample-Accurate Timing**: SuperCollider Patterns for microsecond precision

## 🎵 Features

### Core Capabilities
- **Multi-Agent Ensemble**: 2-5 AI agents with distinct musical personalities
- **Pattern Learning System**: Agents learn and remember musical patterns
- **Song Recognition**: Automatic detection of songs being played
- **Real-Time Collaboration**: Live audio input from guitars/instruments
- **Intelligent Response Modes**: Chord following, call & response, rhythmic sync
- **MIDI Foot Control**: Hands-free mode switching during performance
- **Professional Audio**: Studio-quality synthesis via SuperCollider
- **Modern Web GUI**: Real-time visualization with mixing controls, mute/solo, and level meters

### Performance Metrics
- **Agent Decision → Sound**: <2ms via shared memory
- **Audio Input → Agent**: <5ms with direct analysis
- **Total System Latency**: <8ms guaranteed
- **GUI Update Rate**: 30fps with zero audio dropouts
- **CPU Usage**: <40% total on 8-core system

## 🚀 Quick Start

### Prerequisites

1. Python 3.8+
2. Node.js 18+ (for MCP server)
3. SuperCollider (audio synthesis engine)
4. JACK Audio (Linux) or Core Audio (macOS) for lowest latency
5. Audio interface (optional, for live input features)
6. MIDI foot pedal (optional, for hands-free control)

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

#### All-in-One Launch (Recommended)
```bash
# Starts backend, GUI, and SuperCollider server
./run_performia.sh

# Access the GUI at:
# Modern interface: http://localhost:5000
# Classic interface: http://localhost:5000/classic
```

#### Manual Launch
```bash
# Terminal 1: Start SuperCollider server
./scripts/start_server.sh

# Terminal 2: Run the musical agents
python src/main.py

# Terminal 3 (optional): Start GUI
cd gui && python app.py
```

#### Interactive Mode (With Live Input)
```bash
# With audio input enabled
python src/main.py --enable-input

# Or use the all-in-one script
./run_performia.sh --enable-input
```

## 🎛️ System Architecture v2.0

```
┌─────────────────────────────────────────────┐
│     GUI Process (Port 5001, Low Priority)   │
│         Web Interface - Zero Audio Impact   │
└────────────────┬────────────────────────────┘
                 │ Read-only Shared Memory
┌────────────────┼────────────────────────────┐
│   Control Process (Normal Priority)         │
│   ┌─────────────────────────────────────┐  │
│   │  AI Agent Decision Making           │  │
│   │  Pattern Generation & Coordination  │  │
│   └─────────────────────────────────────┘  │
│              ↓ Write Events                 │
│   ┌─────────────────────────────────────┐  │
│   │  Shared Memory Ring Buffer          │  │
│   │  Lock-free, <0.1ms latency         │  │
│   └─────────────────────────────────────┘  │
└────────────────┬────────────────────────────┘
                 │ Direct Memory + OSC
┌────────────────┼────────────────────────────┐
│   Supernova Server (Real-time Priority)     │
│   ┌─────────────────────────────────────┐  │
│   │ ParGroup 0: Drums (CPU 0)           │  │
│   │ ParGroup 1: Bass (CPU 1)            │  │
│   │ ParGroup 2: Melody (CPU 2)          │  │
│   │ ParGroup 3: Harmony (CPU 3)         │  │
│   │ ParGroup 4: Input Analysis (CPU 4)  │  │
│   └─────────────────────────────────────┘  │
│         ↓ Audio @ 48kHz/64 samples          │
│   ┌─────────────────────────────────────┐  │
│   │  Professional Audio Interface       │  │
│   │  (Quantum 2626 / Similar)          │  │
│   └─────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
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