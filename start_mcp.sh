#!/bin/bash

# =============================================================================
#                     PERFORMIA MCP SERVER STARTUP
#              Pattern Recognition and Learning Service
# =============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║           PERFORMIA MCP - Musical Intelligence Server         ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo

# Navigate to external MCP directory
MCP_DIR="$(dirname "$0")/../Custom_MCP/Performia_MCP"

if [ ! -d "$MCP_DIR" ]; then
    echo -e "${RED}Error: Performia MCP not found at $MCP_DIR${NC}"
    echo -e "${YELLOW}Please ensure Custom_MCP is set up in the Projects directory${NC}"
    exit 1
fi

cd "$MCP_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing MCP dependencies...${NC}"
    npm install
fi

# Initialize database if needed
if [ ! -f "data/patterns.db" ]; then
    echo -e "${YELLOW}Initializing pattern database...${NC}"
    npm run db:init
fi

# Start the MCP server
echo -e "${GREEN}Starting Performia MCP Server...${NC}"
echo -e "${BLUE}• Pattern Recognition: Active${NC}"
echo -e "${BLUE}• Song Database: Ready${NC}"
echo -e "${BLUE}• Learning Mode: Enabled${NC}"
echo

npm start
