#!/bin/bash

echo "🎵 Starting Performia System v2.0"
echo "=================================="
echo ""

# Kill any existing Supernova processes
echo "Cleaning up any existing processes..."
pkill -f supernova 2>/dev/null
pkill -f "python.*process_manager" 2>/dev/null
sleep 1

# Start Supernova in background
echo "Starting Supernova audio server..."
/Applications/SuperCollider.app/Contents/Resources/supernova \
    -u 57110 \
    -z 64 \
    -Z 128 \
    -S 48000 \
    -t 4 \
    -m 262144 \
    -v 0 \
    -D 0 &

SUPERNOVA_PID=$!
echo "✓ Supernova started (PID: $SUPERNOVA_PID)"
sleep 2

# Start the process manager
echo ""
echo "Starting Process Manager..."
echo "This will launch:"
echo "  - Audio Process (real-time priority)"
echo "  - Control Process (AI agents)"  
echo "  - GUI Process (http://localhost:5001)"
echo ""

python src/core/process_manager.py &
MANAGER_PID=$!

echo "✓ Process Manager started (PID: $MANAGER_PID)"
echo ""
echo "=================================="
echo "System is starting up..."
echo "GUI will be available at: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop all processes"
echo "=================================="

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down Performia System..."
    kill $MANAGER_PID 2>/dev/null
    kill $SUPERNOVA_PID 2>/dev/null
    pkill -f supernova 2>/dev/null
    pkill -f "python.*process_manager" 2>/dev/null
    echo "✓ All processes stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Keep script running
while true; do
    # Check if processes are still running
    if ! kill -0 $SUPERNOVA_PID 2>/dev/null; then
        echo "⚠️  Supernova stopped unexpectedly!"
        cleanup
    fi
    if ! kill -0 $MANAGER_PID 2>/dev/null; then
        echo "⚠️  Process Manager stopped unexpectedly!"
        cleanup
    fi
    sleep 5
done