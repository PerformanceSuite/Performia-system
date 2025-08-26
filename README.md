# Performia System

An ultra-low latency multi-agent musical performance system featuring 2-5 AI agents with distinct personalities, memories, and real-time musical collaboration capabilities.

## 🎵 Features

- **Ultra-Low Latency**: <15ms total system latency (3-7ms typical)
- **Multi-Agent Collaboration**: 2-5 agents performing together in real-time
- **Personality System**: Each agent has unique musical personality traits
- **Context-Aware Generation**: Agents respond to each other's musical phrases
- **Memory System**: Short-term and long-term pattern memory
- **Real-Time Synthesis**: Direct audio generation via SuperCollider

## 🚀 Quick Start

### Prerequisites

1. Python 3.8+
2. SuperCollider (audio synthesis engine)
3. JACK Audio (Linux) or Core Audio (macOS) for lowest latency

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

# Install SuperCollider (Ubuntu/Debian)
sudo apt-get install supercollider
```

### Running the System

```bash
# Terminal 1: Start SuperCollider server
./scripts/start_server.sh

# Terminal 2: Run the musical agents
python src/main.py
```

## 🎛️ System Architecture

```
┌─────────────────────────────────────────────┐
│           AutoGen Orchestration             │
├─────────────────────────────────────────────┤
│  Agent 1    Agent 2    Agent 3    Agent 4  │
│  (Drums)    (Bass)    (Melody)  (Harmony)  │
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

## 🎭 Agent Personalities

Each agent has personality traits that affect their musical behavior:

- **Aggression** (0-1): Affects dynamics, dissonance, and rhythmic intensity
- **Creativity** (0-1): Controls pattern variation and experimental choices
- **Responsiveness** (0-1): How much the agent responds to others
- **Stability** (0-1): Tendency to maintain patterns vs. change
- **Leader Tendency** (0-1): Likelihood to initiate musical phrases

## 📊 Performance Metrics

- **Agent Communication**: <0.1ms via shared memory
- **Audio Synthesis**: 2-5ms with 64-sample buffers  
- **Total System Latency**: 3-7ms (target: <15ms)
- **Concurrent Agents**: Up to 5 with maintained latency

## 🛠️ Configuration

Edit `config/config.yaml` to customize:
- Number of agents and roles
- Tempo and key signature
- Audio buffer sizes
- Personality parameters

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
│   │   └── harmony_agent.py    # Harmony specialist
│   ├── engine/
│   │   ├── supercollider.py    # SC integration
│   │   └── audio_engine.py     # Audio management
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
│   └── measure_latency.py     # Latency testing
├── tests/
│   └── test_latency.py       # Performance tests
├── docs/
│   ├── SETUP.md              # Detailed setup guide
│   ├── ARCHITECTURE.md       # System design
│   └── API.md                # API documentation
└── requirements.txt          # Python dependencies
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
```

### Adding New Agent Types

1. Create new agent class inheriting from `BaseMusicalAgent`
2. Define personality parameters
3. Implement `generate_and_play()` method
4. Register in agent factory

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

## 📚 Documentation

- [Setup Guide](docs/SETUP.md) - Detailed installation and configuration
- [Architecture](docs/ARCHITECTURE.md) - System design and components
- [API Reference](docs/API.md) - Programming interface

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to the main branch.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- AutoGen framework by Microsoft
- SuperCollider community
- Research papers on multi-agent musical systems

## 📧 Contact

For questions and support, please open an issue on GitHub.

---

**Built with ❤️ for real-time musical collaboration**
