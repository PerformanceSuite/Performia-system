# Performia System GUI

A modern web-based control interface for the Performia System, providing real-time control and monitoring of the multi-agent musical performance system.

## Features

### 🎛️ System Control
- **One-click start/stop** of the entire system
- **Mode selection**: Autonomous or Interactive (with guitar input)
- **Real-time status monitoring**: Latency, CPU usage, active agents

### 🎸 Interactive Mode Controls
- **Input level meter** with real-time visualization
- **Chord detection display** showing recognized chords
- **Four listening modes**: Chord Follow, Call & Response, Rhythmic Sync, Ambient Layer
- **Virtual MIDI pedals** for hands-free control simulation

### 🎭 Agent Personality Control
- **Live adjustment** of all personality parameters per agent
- **Visual feedback** showing agent activity status
- **Real-time parameter updates** without system restart

### 📊 Performance Monitoring
- **Latency graph** showing system performance over time
- **Agent activity visualization** with color-coded bars
- **Live metrics updates** at 10Hz refresh rate

### 🎨 Presets
- **Jazz Ensemble**: Smooth, creative, responsive
- **Rock Band**: Aggressive, stable, driving
- **Ambient**: Ethereal, evolving, atmospheric
- **Experimental**: Chaotic, creative, unpredictable
- **Classical**: Structured, stable, harmonious

## Quick Start

### Option 1: Use the launcher script
```bash
chmod +x start_gui.sh
./start_gui.sh
```

### Option 2: Manual start
```bash
# Install dependencies
pip install flask flask-socketio eventlet

# Start the GUI server
cd gui
python app.py
```

Then open your browser to: **http://localhost:5000**

## Interface Overview

### Main Controls
- **Start/Stop System**: Primary system control
- **Mode Selection**: Choose between autonomous and interactive modes
- **Tempo Control**: Adjust BPM from 60-180
- **Key Selection**: Choose musical key

### Input Section (Interactive Mode)
- **Input Level Meter**: Shows real-time audio input level
- **Chord Display**: Shows detected chord in large text
- **Listening Mode Buttons**: Quick mode switching
- **Virtual Pedals**: Simulate MIDI pedal actions

### Agent Cards
Each agent has individual controls for:
- Aggression (dynamics, dissonance)
- Creativity (pattern variation)
- Responsiveness (interaction level)
- Stability (pattern consistency)

### Charts Section
- **Latency Chart**: Historical latency tracking
- **Activity Chart**: Agent activity levels

## Keyboard Shortcuts

- `Space`: Start/Stop system
- `1-4`: Select listening mode (in interactive mode)
- `P`: Trigger sustain pedal
- `M`: Cycle listening mode
- `T`: Tap tempo

## API Endpoints

The GUI also exposes REST API endpoints:

- `GET /api/status`: Current system status
- `GET /api/presets`: Available personality presets
- `POST /api/start`: Start the system
- `POST /api/stop`: Stop the system
- `POST /api/agent/:id/personality`: Update agent personality
- `POST /api/tempo`: Set tempo
- `POST /api/key`: Set musical key

## WebSocket Events

The GUI uses Socket.IO for real-time communication:

### Client → Server Events
- `start_system`: Start with specified mode
- `stop_system`: Stop the system
- `update_agent`: Update agent personality
- `set_listening_mode`: Change listening mode
- `trigger_pedal`: Simulate pedal press
- `update_tempo`: Change tempo
- `update_key`: Change musical key

### Server → Client Events
- `state_update`: Full system state
- `system_started`: Confirmation of start
- `system_stopped`: Confirmation of stop
- `metrics_update`: Performance metrics
- `input_update`: Audio input level and chord
- `agents_update`: Agent activity status
- `error`: Error messages

## Customization

### Adding New Presets

Edit the presets object in `static/main.js`:

```javascript
const presets = {
    mypreset: {
        drums: { aggression: 0.5, creativity: 0.5, ... },
        bass: { aggression: 0.5, creativity: 0.5, ... },
        // etc.
    }
};
```

### Changing Color Scheme

Edit CSS variables in `static/style.css`:

```css
:root {
    --primary-color: #your-color;
    --bg-primary: #your-background;
    /* etc. */
}
```

### Adding New Listening Modes

1. Add mode to the HTML template
2. Register handler in `main.js`
3. Implement mode logic in backend

## Troubleshooting

### GUI Won't Start
- Check Flask is installed: `pip install flask flask-socketio`
- Ensure port 5000 is available
- Check Python version (3.8+ required)

### Can't Connect to System
- Verify Performia System is in the parent directory
- Check import paths in `app.py`
- Ensure all dependencies are installed

### Real-time Updates Not Working
- Check WebSocket connection in browser console
- Verify eventlet is installed
- Try different browser if issues persist

### Audio Input Not Showing
- Ensure interactive mode is selected
- Check audio interface is connected
- Verify input system is initialized

## Performance Tips

### For Best Performance
- Use Chrome or Firefox (latest versions)
- Keep charts visible for monitoring
- Close unnecessary browser tabs
- Run on same machine as Performia System

### Reducing Latency
- Minimize update frequency if needed
- Disable charts if not monitoring
- Use wired network connection
- Close other applications

## Development

### Project Structure
```
gui/
├── app.py              # Flask server and Socket.IO
├── templates/
│   └── index.html      # Main interface
├── static/
│   ├── style.css       # Styling
│   └── main.js         # Client-side logic
└── README.md           # This file
```

### Extending the GUI

1. **Add new controls**: Edit `index.html`
2. **Add handlers**: Update `main.js` and `app.py`
3. **Style changes**: Modify `style.css`
4. **New features**: Extend Socket.IO events

### Testing

```bash
# Run in development mode
export FLASK_ENV=development
python app.py

# Run tests
pytest tests/test_gui.py
```

## Browser Compatibility

- **Chrome/Edge**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: Full support
- **Mobile browsers**: Basic support (touch events)

## Security Notes

- GUI binds to 0.0.0.0 for network access
- No authentication by default
- Add authentication for production use
- Use HTTPS for remote access

## Credits

- Built with Flask and Socket.IO
- Charts powered by Chart.js
- Icons and styling inspired by modern DAW interfaces
- Real-time architecture based on professional audio software

## License

MIT License - Part of the Performia System

## Support

For issues or questions about the GUI:
1. Check this README
2. See main Performia documentation
3. Open an issue on GitHub

---

**Enjoy controlling your AI musical ensemble! 🎵🎛️**