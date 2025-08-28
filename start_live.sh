#!/bin/bash

# =============================================================================
#                     PERFORMIA LIVE MODE
#              Ultra-Low Latency Performance Mode
# =============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║              PERFORMIA - LIVE MODE (Performance)              ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo

echo -e "${RED}Performance Mode Optimizations:${NC}"
echo -e "• <8ms total system latency"
echo -e "• Lock-free shared memory"
echo -e "• Pattern cache in RAM"
echo -e "• Minimal logging"
echo

# Set performance governor
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${YELLOW}Setting CPU to performance mode...${NC}"
    sudo cpupower frequency-set -g performance 2>/dev/null || true
fi

# Start MCP in performance mode (cached patterns only)
echo -e "${BLUE}Starting MCP Performance Cache...${NC}"
export PERFORMIA_MODE="live"
export PERFORMIA_CACHE_ONLY="true"
cd ../Custom_MCP/Performia_MCP && npm start &
MCP_PID=$!

# Wait for MCP to load cache
sleep 2

# Start SuperCollider with minimum buffers
echo -e "${BLUE}Starting SuperCollider (Live Settings)...${NC}"
cd ..
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    scripts/start_server.sh --mode live --buffersize 64 &
else
    # Linux with JACK
    jackd -R -P90 -dalsa -dhw:0 -p64 -n2 -r48000 &
    sleep 2
    scripts/start_server.sh --mode live --buffersize 64 --jack &
fi
SC_PID=$!

# Start agents with realtime priority
echo -e "${BLUE}Starting Performance Agents...${NC}"
nice -n -20 python src/main.py --mode live &
AGENTS_PID=$!

# Start minimal GUI (optional)
echo -e "${BLUE}Starting Performance Monitor...${NC}"
cd gui && python app.py --mode live --minimal &
GUI_PID=$!

echo
echo -e "${GREEN}═════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}LIVE MODE ACTIVE - READY FOR PERFORMANCE${NC}"
echo -e "${GREEN}═════════════════════════════════════════════════════════════════${NC}"
echo
echo -e "Latency Target: <8ms"
echo -e "Pattern Cache: Loaded"
echo -e "Audio Engine: Optimized"
echo
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Stopping services...${NC}"
    kill $MCP_PID $SC_PID $AGENTS_PID $GUI_PID 2>/dev/null
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo cpupower frequency-set -g ondemand 2>/dev/null || true
    fi
    echo -e "${GREEN}All services stopped${NC}"
}

trap cleanup EXIT

# Wait for interrupt
wait
