#!/bin/bash

# Performia Master Launch Script
# Starts all components: Backend, Audio Engine, GUI

echo "Starting Performia System..."

# Function to cleanup on exit
cleanup() {
    echo "Shutting down Performia..."
    pkill -f "python.*main.py"
    pkill -f "python.*app.py"
    pkill scsynth
    exit 0
}

trap cleanup INT TERM

# Start SuperCollider server in background
echo "Starting SuperCollider server..."
SCSYNTH_PATH="/Applications/SuperCollider.app/Contents/Resources/scsynth"
if [ -f "$SCSYNTH_PATH" ]; then
    $SCSYNTH_PATH -u 57110 &
    SCSYNTH_PID=$!
    sleep 2
    echo "✓ SuperCollider server started"
    
    # Load SynthDefs
    echo "Loading SynthDefs..."
    if [ -f scripts/auto_load_synthdefs.py ]; then
        python scripts/auto_load_synthdefs.py 2>/dev/null || true
    fi
else
    echo "⚠ SuperCollider server not found, continuing without audio"
fi

# Start the main Python backend
echo "Starting Performia backend..."
source venv/bin/activate
python src/main_simple.py --enable-all &
PYTHON_PID=$!

# Start the GUI server (if exists)
if [ -d "gui" ]; then
    echo "Starting GUI server..."
    cd gui
    python app.py &
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