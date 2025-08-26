#!/bin/bash

# Start SuperCollider server with optimal settings for low latency

echo "🎵 Starting SuperCollider Server for Performia System"
echo "=================================================="

# Detect operating system
OS="$(uname -s)"

case "${OS}" in
    Linux*)
        echo "✓ Detected Linux system"
        # Check if JACK is available
        if command -v jackd &> /dev/null; then
            echo "✓ JACK audio system found"
            # Start JACK with optimal settings if not running
            if ! pgrep -x "jackd" > /dev/null; then
                echo "Starting JACK server..."
                jackd -R -P90 -dalsa -dhw:0 -r48000 -p64 -n2 &
                sleep 2
            fi
            # Start SuperCollider with JACK
            scsynth -u 57110 -H jack -i 0 -o 2 -b 64 -z 256 -m 65536
        else
            echo "⚠ JACK not found, using default audio"
            scsynth -u 57110 -b 64 -z 256 -m 65536
        fi
        ;;
    Darwin*)
        echo "✓ Detected macOS system"
        # Use Core Audio on macOS
        scsynth -u 57110 -H coreaudio -b 64 -z 256 -m 65536
        ;;
    MINGW*|CYGWIN*|MSYS*)
        echo "✓ Detected Windows system"
        # Windows command
        scsynth.exe -u 57110 -b 128 -z 256 -m 65536
        ;;
    *)
        echo "⚠ Unknown operating system: ${OS}"
        echo "Starting with default settings..."
        scsynth -u 57110 -b 128 -z 256 -m 65536
        ;;
esac
