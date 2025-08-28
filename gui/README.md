# Performia System GUI

A professional web-based control interface for the Performia System, providing real-time control and monitoring of the multi-agent musical performance system.

## Current Status (December 2024)

**🚧 UNDER ACTIVE DEVELOPMENT 🚧**

The GUI is functional but still being improved. Current implementation includes basic controls and monitoring, with more features being added.

## Working Features ✅

### System Control
- **Flask/SocketIO backend** with WebSocket real-time communication
- **Agent track controls** for Drums, Bass, Melody, Harmony, and Listener
- **Volume sliders** for each agent (0-100%)
- **Mute/Solo buttons** for each track
- **Test tone generator** for audio testing

### Audio Configuration
- **Audio driver selection** dropdown
- **Sample rate selection** (44.1kHz, 48kHz, 96kHz, 192kHz)
- **Buffer size selection** (64-1024 samples)

### Real-time Monitoring
- **Input/Output level meters** with dB display
- **Status bar** with connection indicator
- **Latency, CPU, and Memory usage** displays (placeholders)

### User Interface
- **Professional DAW-style dark theme**
- **Collapsible sidebars** for better screen usage
- **Responsive layout** adapts to screen size

## Features In Development 🔧

### System Control (TODO)
- [ ] Actual start/stop system functionality
- [ ] Mode selection (Autonomous/Interactive)
- [ ] Emergency stop button
- [ ] System reset functionality

### Agent Personality Control (TODO)
- [ ] Individual personality sliders per agent
- [ ] Aggression parameter control
- [ ] Creativity parameter control  
- [ ] Responsiveness parameter control
- [ ] Stability parameter control
- [ ] Preset management system

### Interactive Mode (TODO)
- [ ] Guitar/audio input monitoring
- [ ] Chord detection display
- [ ] Listening mode selection (Chord Follow, Call & Response, etc.)
- [ ] Virtual MIDI pedals

### Performance Monitoring (TODO)
- [ ] Real latency measurement from system
- [ ] Actual CPU usage monitoring
- [ ] Memory usage tracking
- [ ] Agent activity visualization
- [ ] Historical performance graphs

### Presets System (TODO)
- [ ] Jazz Ensemble preset
- [ ] Rock Band preset
- [ ] Ambient preset
- [ ] Experimental preset
- [ ] Classical preset
- [ ] Custom preset save/load

## Quick Start

### Installation

```bash
# Install Python dependencies
cd gui
pip install flask flask-socketio eventlet

# Install SuperCollider (if not already installed)
brew install supercollider  # macOS
```

### Running the GUI

```bash
# From the project root
cd gui
python app.py
```

Then open your browser to: **http://localhost:5001**

## Project Structure

```
gui/
├── app.py                 # Flask server with SocketIO
├── templates/
│   └── index.html        # Main HTML interface
├── static/
│   ├── style.css         # DAW-style dark theme
│   └── main.js           # Client-side JavaScript
├── old_versions_backup/   # Previous GUI versions (archived)
└── README.md             # This file
```

## API Endpoints

Currently implemented endpoints:

### HTTP Routes
- `GET /` - Main GUI interface
- `GET /static/<path>` - Static file serving

### WebSocket Events (Client → Server)
- `connect` - Initial connection
- `test_tone` - Trigger test tone
- `set_audio_driver` - Change audio driver
- `set_sample_rate` - Change sample rate
- `set_buffer_size` - Change buffer size
- `mute_agent` - Mute/unmute agent
- `solo_agent` - Solo/unsolo agent  
- `set_agent_volume` - Adjust agent volume
- `set_parameter` - Adjust personality parameter

### WebSocket Events (Server → Client)
- `state_update` - Full system state
- `audio_levels` - Real-time audio levels
- `system_metrics` - Performance metrics
- `error` - Error messages

## Development Notes

### Current Architecture
- **Backend**: Flask + Flask-SocketIO for WebSocket communication
- **Frontend**: Vanilla JavaScript with Socket.IO client
- **Styling**: Custom CSS with DAW-inspired dark theme
- **Update Rate**: 10Hz for real-time updates (planned)

### Known Issues
1. **System connection**: GUI runs but isn't fully connected to the actual Performia System yet
2. **Metrics**: Performance metrics are placeholders
3. **Agent control**: Agent parameters don't affect actual synthesis yet
4. **Audio I/O**: Level meters show placeholder data

### Next Steps
1. Complete backend integration with Performia System
2. Implement real agent personality control
3. Add performance monitoring from actual system
4. Create preset management system
5. Implement interactive mode features
6. Add visualization components
7. Improve error handling and user feedback

## Contributing

When working on the GUI:

1. **Test changes locally** before committing
2. **Maintain DAW aesthetic** - keep the professional audio interface look
3. **Preserve real-time performance** - avoid blocking operations
4. **Update this README** when adding new features
5. **Comment your code** - especially WebSocket events

## Technical Requirements

- Python 3.8+
- Modern web browser (Chrome, Firefox, Safari)
- SuperCollider (for audio synthesis)
- Low-latency audio interface (recommended)

## Troubleshooting

### GUI Won't Start
- Check Flask is installed: `pip install flask flask-socketio`
- Ensure port 5001 is available
- Check Python version (3.8+ required)

### Can't Connect to System
- Verify Performia System modules are in parent directory
- Check import paths in `app.py`
- Ensure all dependencies are installed

### No Audio
- SuperCollider must be installed and running
- Check audio driver selection in GUI
- Verify system audio settings

## Future Vision

The GUI will eventually provide:
- Complete visual control over all system parameters
- Real-time visualization of agent interactions
- Recording and playback capabilities
- MIDI integration
- Multi-user collaboration support
- Cloud-based preset sharing

---

**Status**: Under active development - expect frequent updates!

For the main Performia System documentation, see the parent directory README.