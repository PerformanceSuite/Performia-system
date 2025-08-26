#!/bin/bash

# Performia Audio Input System Setup Script

echo "================================================"
echo "   PERFORMIA AUDIO INPUT SYSTEM SETUP"
echo "================================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check for SuperCollider
if command -v scsynth &> /dev/null; then
    echo "✓ SuperCollider found"
else
    echo "⚠ SuperCollider not found!"
    echo "  Please install SuperCollider:"
    echo "  macOS: brew install supercollider"
    echo "  Ubuntu: sudo apt-get install supercollider"
fi

# Check for JACK (optional but recommended)
if command -v jackd &> /dev/null; then
    echo "✓ JACK audio found (optional)"
else
    echo "ℹ JACK audio not found (optional, but recommended for lower latency)"
    echo "  macOS: brew install jack"
    echo "  Ubuntu: sudo apt-get install jackd2"
fi

# Create necessary directories
echo "Creating project directories..."
mkdir -p logs
mkdir -p recordings
mkdir -p data/patterns

echo ""
echo "================================================"
echo "   QUANTUM 2626 CONFIGURATION"
echo "================================================"
echo ""
echo "Please ensure your Presonus Quantum 2626 is:"
echo "  1. Connected via Thunderbolt"
echo "  2. Set to 48kHz sample rate"
echo "  3. Using lowest buffer size (64 samples)"
echo ""
echo "In Universal Control software:"
echo "  - Set Block Size to 64"
echo "  - Enable 'Low Latency Monitoring'"
echo "  - Route guitar input to channels 1-2"
echo ""

echo "================================================"
echo "   MIDI PEDAL SETUP"
echo "================================================"
echo ""
echo "Connect your MIDI pedal to the Quantum 2626"
echo "Default CC mappings:"
echo "  - CC64 (Sustain): Start/stop listening"
echo "  - CC65 (Portamento): Change mode"
echo "  - CC11 (Expression): Continuous control"
echo "  - CC80 (General): Tap tempo"
echo ""

echo "================================================"
echo "   TESTING THE SYSTEM"
echo "================================================"
echo ""
echo "To test the input system, run:"
echo "  python tests/test_input_system.py"
echo ""
echo "To start the full Performia system with input:"
echo "  python src/main.py --with-input"
echo ""

echo "Setup complete! 🎸🎵"
