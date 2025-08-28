#!/bin/bash
# MCP Server Test Script

echo "Testing MCP Servers for Performia-system..."
echo "==========================================="
cd ~/Projects/Performia-system

# Load environment
source ~/.zshrc 2>/dev/null

# List all configured servers
echo ""
echo "Servers in configuration:"
cat ~/.claude.json | jq '.projects["/Users/danielconnolly/Projects/Performia-system"].mcpServers | keys' 2>/dev/null

echo ""
echo "Running claude mcp list:"
echo "------------------------"
claude mcp list

echo ""
echo "Summary:"
echo "--------"
echo "If servers show in 'claude mcp list' but not in /mcp UI,"
echo "it's a Claude Code display bug. The servers are still usable!"
