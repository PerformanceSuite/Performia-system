#!/bin/bash

# Performia System GUI Launcher
# Starts the web-based control interface

echo "🎵 Performia System GUI Launcher"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Check if SuperCollider is running
if ! pgrep -x "scsynth" > /dev/null; then
    echo "Starting SuperCollider server..."
    ./scripts/start_server.sh &
    sleep 2
fi

# Start the GUI
echo ""
echo "🚀 Starting Performia GUI on http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""

cd gui
python app.py