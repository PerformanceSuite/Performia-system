#!/bin/bash

# Performia System - Quick Start Script

echo "🎵 PERFORMIA MUSICAL AGENT SYSTEM"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import autogen" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if SuperCollider is running
if ! pgrep -x "scsynth" > /dev/null; then
    echo "Starting SuperCollider server..."
    ./scripts/start_server.sh &
    sleep 3
fi

echo ""
echo "Starting Performia System..."
echo "Press Ctrl+C to stop"
echo ""

# Run the main program
python src/main.py
