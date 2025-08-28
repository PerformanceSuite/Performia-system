# Playwright MCP Server Installation Guide

## Overview
The Playwright MCP (Model Context Protocol) server enables browser automation capabilities within Claude, allowing for web scraping, testing, and automated interactions with web applications.

## Installation Steps

### 1. Install the Package
```bash
npm install -g @playwright/mcp
```

This installs version 0.0.35 (as of December 2024) to:
```
/Users/danielconnolly/.nvm/versions/node/v20.19.4/lib/node_modules/@playwright/mcp/
```

### 2. Install Browser Binaries
Navigate to the installation directory and install browsers:
```bash
cd /Users/danielconnolly/.nvm/versions/node/v20.19.4/lib/node_modules/@playwright/mcp
npx playwright install
```

This downloads:
- Chromium 140.0.7339.5 (129.6 MiB)
- Chromium Headless Shell (81.8 MiB)
- Firefox 141.0 (89.2 MiB)
- WebKit 26.0 (70.2 MiB)

Browsers are cached in: `/Users/danielconnolly/Library/Caches/ms-playwright/`

### 3. Configure MCP Server
Add to `/Users/danielconnolly/.config/claude/mcp_servers.json`:

```json
"playwright": {
    "command": "/Users/danielconnolly/.nvm/versions/node/v20.19.4/bin/node",
    "args": [
        "/Users/danielconnolly/.nvm/versions/node/v20.19.4/lib/node_modules/@playwright/mcp/index.js"
    ],
    "description": "Browser automation with Playwright",
    "enabled": true
}
```

### 4. Restart Claude
After configuration, restart Claude to activate the Playwright MCP server.

## Configuration Notes

### Important Files
- **MCP Configuration**: `~/.config/claude/mcp_servers.json`
- **Package Location**: `~/.nvm/versions/node/v20.19.4/lib/node_modules/@playwright/mcp/`
- **Browser Cache**: `~/Library/Caches/ms-playwright/`

### Common Issues

1. **Wrong Configuration File**: Do NOT use `claude_mcp_config.json` - this is deprecated
2. **Path Issues**: Always use full paths to node binary and package files
3. **Browser Not Found**: Run `npx playwright install` from the package directory

## Available Capabilities

Once installed, the Playwright MCP server provides:
- Browser automation (Chrome, Firefox, Safari/WebKit)
- Page navigation and interaction
- Screenshot capture
- Form filling and submission
- Web scraping
- Automated testing
- JavaScript execution in browser context

## Verification

To verify installation:
1. Check package is installed: `npm list -g @playwright/mcp`
2. Verify browsers: `ls ~/Library/Caches/ms-playwright/`
3. Confirm in MCP config: `cat ~/.config/claude/mcp_servers.json | grep playwright`

## Troubleshooting

### If MCP server doesn't appear in Claude:
1. Ensure Claude is fully restarted (not just reloaded)
2. Check the configuration syntax in `mcp_servers.json`
3. Verify node path matches your nvm installation

### If browser automation fails:
1. Re-install browsers: `npx playwright install --force`
2. Check disk space for browser cache
3. Verify no firewall blocking browser downloads

## Related MCP Servers

Other MCP servers configured in this system:
- `filesystem`: File system access
- `github`: GitHub integration
- `memory`: Knowledge graph
- `brave-search`: Web search
- `git`: Repository management
- `desktop-commander`: Desktop automation
- `performia`: Musical agent system control

---

*Documentation created: December 28, 2024*