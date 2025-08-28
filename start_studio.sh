#!/bin/bash

# =============================================================================
#                     PERFORMIA STUDIO MODE
#              Pattern Learning and Practice Session
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
echo -e "${CYAN}║              PERFORMIA - STUDIO MODE (Learning)               ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo

echo -e "${YELLOW}Studio Mode Features:${NC}"
echo -e "• Pattern extraction and analysis"
echo -e "• Song structure learning"
echo -e "• Style fingerprinting"
echo -e "• No latency constraints"
echo

# Start MCP in learning mode
echo -e "${BLUE}Starting MCP Learning Service...${NC}"
export PERFORMIA_MODE="studio"
cd ../Custom_MCP/Performia_MCP && npm start &
MCP_PID=$!

# Wait for MCP to initialize
sleep 3

# Start SuperCollider with relaxed buffers
echo -e "${BLUE}Starting SuperCollider (Studio Settings)...${NC}"
cd ..
python scripts/start_server.sh --mode studio &
SC_PID=$!

# Start GUI
echo -e "${BLUE}Starting Web Interface...${NC}"
cd gui && python app.py --mode studio &
GUI_PID=$!

echo
echo -e "${GREEN}═════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Studio Mode Active - Ready for Learning${NC}"
echo -e "${GREEN}═════════════════════════════════════════════════════════════════${NC}"
echo
echo -e "Web Interface: http://localhost:5000"
echo -e "MCP API: http://localhost:3000"
echo
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for interrupt
wait
