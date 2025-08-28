#!/bin/bash

# Performia System - Start Supernova with optimal settings for ultra-low latency
# Target: <8ms total system latency with multi-core processing

echo "🎵 Starting Supernova for Performia System..."
echo "=========================================="

# Path to Supernova
SUPERNOVA="/Applications/SuperCollider.app/Contents/Resources/supernova"

# Check if Supernova exists
if [ ! -f "$SUPERNOVA" ]; then
    echo "❌ Supernova not found at: $SUPERNOVA"
    echo "Please install SuperCollider from https://supercollider.github.io"
    exit 1
fi

# Configuration for ultra-low latency
PORT=57110                  # OSC port
AUDIO_DEVICE=""             # Auto-select device (or specify "Quantum 2626")
SAMPLE_RATE=48000           # 48kHz sample rate
BLOCK_SIZE=64               # Control rate block size (1.3ms @ 48kHz)
HARDWARE_BUFFER=128         # Hardware buffer (2.6ms @ 48kHz)
NUM_INPUTS=2                # Stereo input
NUM_OUTPUTS=2               # Stereo output
NUM_AUDIO_BUS=128          # Audio buses
NUM_CONTROL_BUS=4096       # Control buses
NUM_BUFFERS=256            # Sample buffers
MEMORY_SIZE=262144         # Server memory (256MB)
NUM_WIRE_BUFS=64           # Wire buffers
RT_MEMORY=65536            # Real-time memory (64MB)
NUM_THREADS=4              # Parallel processing threads

# Build command
CMD="$SUPERNOVA \
    -u $PORT \
    -a 1024 \
    -i $NUM_INPUTS \
    -o $NUM_OUTPUTS \
    -z $BLOCK_SIZE \
    -Z $HARDWARE_BUFFER \
    -S $SAMPLE_RATE \
    -b $NUM_BUFFERS \
    -n $NUM_CONTROL_BUS \
    -d $NUM_AUDIO_BUS \
    -m $MEMORY_SIZE \
    -w $NUM_WIRE_BUFS \
    -r $RT_MEMORY \
    -t $NUM_THREADS \
    -v 0"

# Add hardware device if specified
if [ -n "$AUDIO_DEVICE" ]; then
    CMD="$CMD -H \"$AUDIO_DEVICE\""
fi

echo "Configuration:"
echo "  Sample Rate: $SAMPLE_RATE Hz"
echo "  Block Size: $BLOCK_SIZE samples ($(echo "scale=2; $BLOCK_SIZE * 1000 / $SAMPLE_RATE" | bc)ms)"
echo "  Hardware Buffer: $HARDWARE_BUFFER samples ($(echo "scale=2; $HARDWARE_BUFFER * 1000 / $SAMPLE_RATE" | bc)ms)"
echo "  Threads: $NUM_THREADS (multi-core processing)"
echo "  Memory: $(echo "scale=0; $MEMORY_SIZE / 1024" | bc)MB"
echo "  Target Latency: <8ms total"
echo ""
echo "Starting Supernova..."
echo "Command: $CMD"
echo ""

# Start Supernova
exec $CMD