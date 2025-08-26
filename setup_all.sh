#!/bin/bash

# =============================================================================
#                     PERFORMIA COMPLETE SYSTEM SETUP
#              All-in-one installation: Backend, GUI, Audio Input
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Detect OS
OS="Unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
fi

echo -e "${CYAN}"
echo "=============================================================="
echo "              PERFORMIA COMPLETE SYSTEM SETUP                "
echo "          Backend + GUI + Audio Input + Dependencies         "
echo "=============================================================="
echo -e "${NC}"
echo ""

# Check System Requirements
echo -e "${BLUE}Checking System Requirements...${NC}"
echo ""

# Python version check
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓${NC} Python $python_version found"
else
    echo -e "${RED}✗ Python 3.8+ required${NC}"
    exit 1
fi

# Node.js check (for GUI)
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js $node_version found"
else
    echo -e "${YELLOW}⚠${NC} Node.js not found (required for GUI)"
    echo "  Install: https://nodejs.org/"
fi

# SuperCollider check
if command -v scsynth &> /dev/null; then
    echo -e "${GREEN}✓${NC} SuperCollider found"
else
    echo -e "${YELLOW}⚠${NC} SuperCollider not found"
    if [[ "$OS" == "macOS" ]]; then
        echo "  Install: brew install supercollider"
    elif [[ "$OS" == "Linux" ]]; then
        echo "  Install: sudo apt-get install supercollider"
    fi
fi

# JACK check (optional)
if command -v jackd &> /dev/null; then
    echo -e "${GREEN}✓${NC} JACK audio found (optional)"
else
    echo -e "${YELLOW}ℹ${NC} JACK audio not found (optional, for lowest latency)"
fi

echo ""
echo -e "${BLUE}Setting Up Virtual Environment...${NC}"

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment exists"
fi

source venv/bin/activate

# Upgrade pip
pip install --upgrade pip --quiet

echo ""
echo -e "${BLUE}Installing Python Dependencies...${NC}"

# Create consolidated requirements.txt if not exists
cat > requirements_all.txt << 'EOF'
# ===========================================
# Core System Dependencies
# ===========================================
pyautogen>=0.2.0
numpy>=1.24.0
python-osc>=1.8.0
pyyaml>=6.0

# ===========================================
# Audio & Synthesis
# ===========================================
supercollider>=0.4.0
sounddevice>=0.4.6      # Audio input/output
librosa>=0.10.0         # Audio analysis
scipy>=1.10.0           # Signal processing
soundfile>=0.12.1       # Audio file I/O

# ===========================================
# MIDI Control
# ===========================================
mido>=1.3.0             # MIDI messages
python-rtmidi>=1.5.0    # MIDI backend

# ===========================================
# Performance Optimization
# ===========================================
uvloop>=0.17.0 ; platform_system != "Windows"
numba>=0.57.0           # JIT compilation
asyncio>=3.4.3

# ===========================================
# GUI Dependencies
# ===========================================
flask>=3.0.0            # Web server
flask-cors>=4.0.0       # CORS support
flask-socketio>=5.3.0   # WebSocket support
python-socketio>=5.10.0 # Socket.IO server
eventlet>=0.33.0        # Async networking

# ===========================================
# Testing & Development
# ===========================================
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-timeout>=2.1.0
black>=23.0.0
flake8>=6.0.0

# ===========================================
# Visualization & Monitoring
# ===========================================
matplotlib>=3.6.0       # Plotting
pygame>=2.1.0          # Real-time visualization
psutil>=5.9.0          # System monitoring

# ===========================================
# Optional: Machine Learning
# ===========================================
# tensorflow>=2.12.0    # Uncomment for ML features
# scikit-learn>=1.3.0   # Uncomment for ML features
EOF

echo "Installing backend dependencies..."
pip install -r requirements_all.txt

echo -e "${GREEN}✓${NC} Python dependencies installed"

echo ""
echo -e "${BLUE}Setting Up GUI...${NC}"

# Check if GUI directory exists
if [ -d "gui" ]; then
    cd gui
    
    # Install npm dependencies
    if [ -f "package.json" ]; then
        echo "Installing GUI dependencies..."
        npm install
        echo -e "${GREEN}✓${NC} GUI dependencies installed"
    else
        echo "Creating GUI package.json..."
        cat > package.json << 'EOF'
{
  "name": "performia-gui",
  "version": "1.0.0",
  "description": "Web GUI for Performia System",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "build": "webpack --mode production"
  },
  "dependencies": {
    "express": "^4.18.0",
    "socket.io": "^4.6.0",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "nodemon": "^3.0.0",
    "webpack": "^5.89.0",
    "webpack-cli": "^5.1.0"
  }
}
EOF
        npm install
        echo -e "${GREEN}✓${NC} GUI setup complete"
    fi
    
    cd ..
else
    echo -e "${YELLOW}⚠${NC} GUI directory not found, creating basic structure..."
    mkdir -p gui
    # Create basic GUI files (can be expanded)
fi

echo ""
echo -e "${BLUE}Creating Project Directories...${NC}"

# Create all necessary directories
directories=(
    "logs"
    "recordings"
    "data/patterns"
    "data/memories"
    "sc/synthdefs"
    "config/presets"
    "tests/fixtures"
    "docs/api"
    "scripts/utils"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    echo -e "  ${GREEN}✓${NC} Created $dir"
done

echo ""
echo -e "${BLUE}Setting Up Configuration Files...${NC}"

# Create main config if not exists
if [ ! -f "config/config.yaml" ]; then
    cat > config/config.yaml << 'EOF'
# Performia System Configuration
# Complete setup with all features enabled

# ==========================================
# Audio Configuration
# ==========================================
audio:
  sample_rate: 48000
  block_size: 64          # Lowest latency setting
  hardware_buffer: 128
  server: supercollider
  output_device: default
  input_device: default   # Set to your interface name

# ==========================================
# Agent Configuration
# ==========================================
agents:
  count: 4
  roles:
    - drums
    - bass
    - melody
    - harmony
    - listener  # Audio input processor
  
  personalities:
    default:
      aggression: 0.5
      creativity: 0.7
      responsiveness: 0.8
      stability: 0.6
      leader_tendency: 0.4

# ==========================================
# Performance Settings
# ==========================================
performance:
  tempo: 120
  key: 0              # C major (0-11 for C-B)
  time_signature: [4, 4]
  mode: 0             # 0=major, 1=minor, etc.
  
# ==========================================
# Audio Input Configuration
# ==========================================
input:
  enabled: true
  device_name: "Quantum 2626"  # Your audio interface
  channels: [0, 1]              # Stereo input channels
  gain: 1.0
  noise_gate: -60               # dB
  
  analysis:
    hop_length: 512
    confidence_threshold: 0.8
    chord_detection: true
    onset_detection: true
    pitch_tracking: true
    
  response_modes:
    - chord_follow
    - call_response
    - rhythmic_sync
    - ambient_layer

# ==========================================
# MIDI Configuration
# ==========================================
midi:
  enabled: true
  input_port: "Quantum 2626"  # Your MIDI interface
  
  pedal_mappings:
    sustain: 64           # CC64 - Start/stop listening
    mode_select: 65       # CC65 - Change response mode
    expression: 11        # CC11 - Control intensity
    tap_tempo: 80         # CC80 - Set tempo
    
# ==========================================
# System Performance
# ==========================================
latency:
  target_ms: 15
  measurement: true
  optimization: aggressive
  
  # Detailed latency targets
  agent_communication_ms: 0.1
  audio_synthesis_ms: 5
  input_analysis_ms: 5
  total_system_ms: 15
  
# ==========================================
# Memory Configuration
# ==========================================
memory:
  use_shared: true
  buffer_size: 1024
  pattern_memory: 32
  input_buffer_size: 4096
  phrase_buffer_size: 64
  
# ==========================================
# Logging Configuration
# ==========================================
logging:
  level: INFO
  file: logs/performia.log
  console: true
  log_analysis: false    # Set true for debug
  log_midi: true
  performance_metrics: true

# ==========================================
# GUI Configuration
# ==========================================
gui:
  enabled: true
  port: 5000
  auto_open_browser: true
  update_rate_ms: 100
  theme: dark
EOF
    echo -e "${GREEN}✓${NC} Created config.yaml"
else
    echo -e "${GREEN}✓${NC} config.yaml already exists"
fi

echo ""
echo -e "${BLUE}Creating Launch Scripts...${NC}"

# Create master run script
cat > run_performia.sh << 'EOF'
#!/bin/bash

# Performia Master Launch Script
# Starts all components: Backend, Audio Engine, GUI

echo "Starting Performia System..."

# Function to cleanup on exit
cleanup() {
    echo "Shutting down Performia..."
    pkill -f "python.*main.py"
    pkill -f "node.*server.js"
    pkill scsynth
    exit 0
}

trap cleanup INT TERM

# Start SuperCollider server in background
echo "Starting SuperCollider server..."
scsynth -u 57110 &
SCSYNTH_PID=$!
sleep 2

# Start the main Python backend
echo "Starting Performia backend..."
source venv/bin/activate
python src/main.py --enable-all &
PYTHON_PID=$!

# Start the GUI server (if exists)
if [ -d "gui" ]; then
    echo "Starting GUI server..."
    cd gui
    npm start &
    GUI_PID=$!
    cd ..
    
    # Open browser after a delay
    sleep 3
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open http://localhost:5000
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open http://localhost:5000
    fi
fi

echo ""
echo "============================================"
echo "   Performia System Running!"
echo "   GUI: http://localhost:5000"
echo "   Press Ctrl+C to stop all components"
echo "============================================"
echo ""

# Wait for any process to exit
wait
EOF

chmod +x run_performia.sh
echo -e "${GREEN}✓${NC} Created run_performia.sh"

# Create test script
cat > test_all.sh << 'EOF'
#!/bin/bash

# Complete test suite for Performia

echo "Running Performia Test Suite..."
echo ""

source venv/bin/activate

# Test imports
echo "Testing module imports..."
python -c "import src.main; print('✓ Main module OK')"
python -c "import src.agents; print('✓ Agents module OK')"
python -c "import src.engine; print('✓ Engine module OK')"

# Test audio system
echo ""
echo "Testing audio system..."
python tests/test_latency.py

# Test input system (if available)
if [ -f "tests/test_input_system.py" ]; then
    echo ""
    echo "Testing input system..."
    python tests/test_input_system.py
fi

# Run pytest
echo ""
echo "Running pytest suite..."
pytest tests/ -v

echo ""
echo "All tests complete!"
EOF

chmod +x test_all.sh
echo -e "${GREEN}✓${NC} Created test_all.sh"

echo ""
echo -e "${CYAN}=============================================================="
echo -e "              SETUP COMPLETE! 🎉"
echo -e "==============================================================${NC}"
echo ""
echo -e "${BLUE}Quick Start Commands:${NC}"
echo ""
echo "  ${GREEN}./run_performia.sh${NC}     - Start everything (backend + GUI)"
echo "  ${GREEN}./test_all.sh${NC}          - Run all tests"
echo "  ${GREEN}python src/main.py${NC}     - Start backend only"
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo ""
echo "  Edit ${CYAN}config/config.yaml${NC} to customize:"
echo "    • Audio interface settings"
echo "    • Agent personalities"
echo "    • MIDI pedal mappings"
echo "    • Response modes"
echo ""

# Check for audio interface
echo -e "${BLUE}Audio Interface Setup:${NC}"
echo ""
if [[ "$OS" == "macOS" ]]; then
    # Check for Quantum 2626
    if system_profiler SPUSBDataType | grep -q "Quantum"; then
        echo -e "${GREEN}✓${NC} Presonus Quantum detected!"
    else
        echo -e "${YELLOW}ℹ${NC} No Quantum 2626 detected"
    fi
fi

echo "  Configure your audio interface:"
echo "    1. Set sample rate to 48kHz"
echo "    2. Set buffer size to 64 samples"
echo "    3. Route guitar to inputs 1-2"
echo "    4. Connect MIDI pedals"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "  1. Run ${GREEN}./run_performia.sh${NC} to start the system"
echo "  2. The GUI will open at http://localhost:5000"
echo "  3. Press sustain pedal to start listening to your guitar!"
echo ""
echo -e "${CYAN}Happy jamming! 🎸🎵${NC}"
