#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { execSync, exec } from 'child_process';
import { readFileSync, writeFileSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { z } from 'zod';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.dirname(__dirname);

// Create server instance
const server = new Server({
  name: 'performia-mcp',
  version: '1.0.0',
}, {
  capabilities: {
    tools: {},
  },
});

// Define tools
const tools = [
  {
    name: 'run_supercollider',
    description: 'Execute SuperCollider code directly',
    inputSchema: {
      type: 'object',
      properties: {
        code: {
          type: 'string',
          description: 'SuperCollider code to execute',
        },
      },
      required: ['code'],
    },
  },
  {
    name: 'start_performia',
    description: 'Start the Performia system with specified options',
    inputSchema: {
      type: 'object',
      properties: {
        enableInput: {
          type: 'boolean',
          description: 'Enable audio input system',
          default: false,
        },
        gui: {
          type: 'boolean',
          description: 'Start the GUI interface',
          default: true,
        },
      },
    },
  },
  {
    name: 'get_system_status',
    description: 'Get the current status of the Performia system',
    inputSchema: {
      type: 'object',
      properties: {},
    },
  },
  {
    name: 'calibrate_input',
    description: 'Run the audio input calibration script',
    inputSchema: {
      type: 'object',
      properties: {},
    },
  },
];

// Handle tools/list requests
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: tools,
}));

// Handle tools/call requests
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'run_supercollider': {
        const { code } = args;
        
        try {
          // Write code to temporary file and execute with sclang
          const tempFile = path.join(projectRoot, 'temp_sc.scd');
          writeFileSync(tempFile, code);
          
          const result = execSync(`sclang ${tempFile}`, {
            cwd: projectRoot,
            encoding: 'utf8',
            timeout: 30000,
          });
          
          return {
            content: [
              {
                type: 'text',
                text: `SuperCollider executed successfully:\n${result}`,
              },
            ],
          };
        } catch (error) {
          return {
            content: [
              {
                type: 'text',
                text: `Error executing SuperCollider: ${error.message}`,
              },
            ],
          };
        }
      }
      
      case 'start_performia': {
        const { enableInput, gui } = args;
        
        try {
          let command = 'python src/main.py';
          if (enableInput) {
            command += ' --enable-input';
          }
          
          // Start in background
          exec(command, {
            cwd: projectRoot,
          }, (error, stdout, stderr) => {
            if (error) {
              console.error(`Error: ${error}`);
            }
          });
          
          if (gui) {
            // Start GUI in background
            exec('./start_gui.sh', {
              cwd: projectRoot,
            });
          }
          
          return {
            content: [
              {
                type: 'text',
                text: `Performia system started with options:\n- Audio Input: ${enableInput ? 'Enabled' : 'Disabled'}\n- GUI: ${gui ? 'Started' : 'Not started'}`,
              },
            ],
          };
        } catch (error) {
          return {
            content: [
              {
                type: 'text',
                text: `Error starting Performia: ${error.message}`,
              },
            ],
          };
        }
      }
      
      case 'get_system_status': {
        try {
          // Check if Python process is running
          let pythonRunning = false;
          try {
            execSync('pgrep -f "python.*src/main.py"', { encoding: 'utf8' });
            pythonRunning = true;
          } catch (e) {
            // Process not found
          }
          
          // Check if SuperCollider is running
          let scRunning = false;
          try {
            execSync('pgrep -x scsynth', { encoding: 'utf8' });
            scRunning = true;
          } catch (e) {
            // Process not found
          }
          
          // Check if GUI is running
          let guiRunning = false;
          try {
            execSync('lsof -i :5173', { encoding: 'utf8' });
            guiRunning = true;
          } catch (e) {
            // Port not in use
          }
          
          return {
            content: [
              {
                type: 'text',
                text: `System Status:\n- Backend: ${pythonRunning ? '✓ Running' : '✗ Not running'}\n- SuperCollider: ${scRunning ? '✓ Running' : '✗ Not running'}\n- GUI: ${guiRunning ? '✓ Running on port 5173' : '✗ Not running'}`,
              },
            ],
          };
        } catch (error) {
          return {
            content: [
              {
                type: 'text',
                text: `Error checking status: ${error.message}`,
              },
            ],
          };
        }
      }
      
      case 'calibrate_input': {
        try {
          const result = execSync('python scripts/calibrate_input.py', {
            cwd: projectRoot,
            encoding: 'utf8',
            timeout: 60000,
          });
          
          return {
            content: [
              {
                type: 'text',
                text: `Calibration completed:\n${result}`,
              },
            ],
          };
        } catch (error) {
          return {
            content: [
              {
                type: 'text',
                text: `Error during calibration: ${error.message}`,
              },
            ],
          };
        }
      }
      
      default:
        return {
          content: [
            {
              type: 'text',
              text: `Unknown tool: ${name}`,
            },
          ],
        };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error executing tool: ${error.message}`,
        },
      ],
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});