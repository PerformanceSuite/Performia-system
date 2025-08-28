# Performia System - Project Structure

## Directory Layout

```
Performia-system/
│
├── src/                      # Core Python source code
│   ├── agents/              # Agent personalities and behaviors
│   ├── engine/              # Audio synthesis and SuperCollider interface
│   ├── memory/              # Shared memory and pattern storage
│   ├── personality/         # Personality system
│   └── utils/              # Helper functions
│
├── PerformiaJUCE/          # JUCE-based GUI (optional)
│   ├── Source/            # C++ source files
│   ├── JUCE/             # JUCE framework
│   └── build/            # Build artifacts
│
├── gui/                    # Web-based GUI
│   ├── static/           # Frontend assets
│   ├── templates/        # HTML templates
│   └── app.py           # Flask server
│
├── sc/                     # SuperCollider files
│   ├── synthdefs/       # Synthesis definitions
│   └── patterns/        # SC pattern templates
│
├── config/                # Configuration files
│   ├── config.yaml      # System configuration
│   └── personalities.json # Agent personality presets
│
├── tests/                 # Test suites
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── performance/    # Latency benchmarks
│
├── scripts/              # Utility scripts
│   ├── start_server.sh # Start SuperCollider
│   └── measure_latency.py # Performance testing
│
├── docs/                 # Documentation
│   ├── architecture/   # Architecture docs
│   ├── api/           # API documentation
│   └── tutorials/     # Usage guides
│
└── archive/             # Old/deprecated code
```

## Key Components

### 1. Core System (`src/`)
The main Python application that orchestrates the agents and manages real-time performance.

### 2. MCP Server (External)
**Location**: `../Custom_MCP/Performia_MCP/` (kept separate for IP protection)

Background service that handles:
- Pattern learning and recognition
- Song database management
- Knowledge transfer between Studio and Live modes
- Real-time pattern matching with <0.1ms lookup

**Note**: The MCP contains proprietary algorithms and is maintained separately to allow the main Performia system to be open-sourced while protecting intellectual property.

### 3. Audio Engine (`sc/`)
SuperCollider synthesis engine providing <15ms latency audio generation.

### 4. User Interfaces
- **Web GUI** (`gui/`): Primary control interface
- **JUCE GUI** (`PerformiaJUCE/`): Optional native GUI for advanced control

## Data Flow

```
Studio Mode:
Audio Input → Pattern Extraction → MCP Learning → Database Storage

Live Mode:
Human Input → Pattern Recognition → Agent Response → SuperCollider → Audio Output
                      ↑                      ↓
                  MCP Cache ← Pattern Database
```

## Running the System

### Studio Mode (Learning)
```bash
./scripts/start_studio.sh
```

### Live Mode (Performance)
```bash
./scripts/start_live.sh
```

### MCP Server (Background)
```bash
cd PerformiaMCP && npm start
```
