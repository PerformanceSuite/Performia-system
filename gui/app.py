"""
Performia System Web GUI
Real-time control interface for the multi-agent musical performance system
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import asyncio
import json
import os
import sys
import threading
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.integration.input_system import InputSystem
except ImportError:
    InputSystem = None
    
try:
    from src.main_simple import PerformiaSystem
except ImportError:
    from src.main import PerformiaSystem
    
try:
    from src.personality.personality import Personality
except ImportError:
    Personality = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'performia-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global system state
system_state = {
    'is_running': False,
    'mode': 'autonomous',  # 'autonomous' or 'interactive'
    'listening_mode': 'chord_follow',
    'agents': {},
    'input_level': 0,
    'detected_chord': None,
    'tempo': 120,
    'key': 0,
    'performance_metrics': {
        'latency': 0,
        'cpu_usage': 0,
        'active_agents': 0
    }
}

# System instances
performia_system = None
input_system = None
monitor_thread = None

@app.route('/')
def index():
    """Serve the main GUI page"""
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('state_update', system_state)

@socketio.on('start_system')
def handle_start_system(data):
    """Start the Performia system"""
    global performia_system, input_system, system_state, monitor_thread
    
    mode = data.get('mode', 'autonomous')
    system_state['mode'] = mode
    
    try:
        if mode == 'interactive':
            # Start with input system
            input_system = InputSystem(
                enable_audio=True,
                enable_midi=data.get('enable_midi', True)
            )
            asyncio.run(input_system.initialize())
            input_system.set_listening_mode(system_state['listening_mode'])
            asyncio.run(input_system.start())
            
        # Start main Performia system
        performia_system = PerformiaSystem(enable_input=(mode == 'interactive'))
        performia_system.start_performance()
        
        system_state['is_running'] = True
        
        # Start monitoring thread
        if not monitor_thread or not monitor_thread.is_alive():
            monitor_thread = threading.Thread(target=monitor_system, daemon=True)
            monitor_thread.start()
        
        emit('system_started', {'status': 'success', 'mode': mode}, broadcast=True)
        emit('state_update', system_state, broadcast=True)
        
    except Exception as e:
        emit('error', {'message': str(e)}, broadcast=True)

@socketio.on('stop_system')
def handle_stop_system():
    """Stop the Performia system"""
    global performia_system, input_system, system_state
    
    try:
        if performia_system:
            performia_system.stop()
            performia_system = None
            
        if input_system:
            asyncio.run(input_system.stop())
            input_system = None
            
        system_state['is_running'] = False
        emit('system_stopped', {'status': 'success'}, broadcast=True)
        emit('state_update', system_state, broadcast=True)
        
    except Exception as e:
        emit('error', {'message': str(e)}, broadcast=True)

@socketio.on('update_agent')
def handle_update_agent(data):
    """Update an agent's personality"""
    agent_id = data.get('agent_id')
    personality_params = data.get('personality')
    
    if performia_system and agent_id:
        try:
            personality = Personality(**personality_params)
            performia_system.update_agent_personality(agent_id, personality)
            
            system_state['agents'][agent_id] = personality_params
            emit('agent_updated', {'agent_id': agent_id}, broadcast=True)
            emit('state_update', system_state, broadcast=True)
            
        except Exception as e:
            emit('error', {'message': str(e)})

@socketio.on('set_listening_mode')
def handle_set_listening_mode(data):
    """Change the listening mode"""
    mode = data.get('mode')
    
    if input_system and mode:
        try:
            input_system.set_listening_mode(mode)
            system_state['listening_mode'] = mode
            emit('listening_mode_changed', {'mode': mode}, broadcast=True)
            emit('state_update', system_state, broadcast=True)
            
        except Exception as e:
            emit('error', {'message': str(e)})

@socketio.on('trigger_pedal')
def handle_trigger_pedal(data):
    """Simulate MIDI pedal trigger"""
    pedal_type = data.get('pedal_type')  # 'sustain', 'mode', 'tap'
    
    if input_system:
        try:
            if pedal_type == 'sustain':
                input_system.toggle_listening()
            elif pedal_type == 'mode':
                input_system.cycle_mode()
            elif pedal_type == 'tap':
                input_system.tap_tempo()
                
            emit('pedal_triggered', {'pedal': pedal_type}, broadcast=True)
            
        except Exception as e:
            emit('error', {'message': str(e)})

@socketio.on('update_tempo')
def handle_update_tempo(data):
    """Update the system tempo"""
    tempo = data.get('tempo', 120)
    
    if performia_system:
        try:
            performia_system.set_tempo(tempo)
            system_state['tempo'] = tempo
            emit('tempo_changed', {'tempo': tempo}, broadcast=True)
            emit('state_update', system_state, broadcast=True)
            
        except Exception as e:
            emit('error', {'message': str(e)})

@socketio.on('update_key')
def handle_update_key(data):
    """Update the musical key"""
    key = data.get('key', 0)
    
    if performia_system:
        try:
            performia_system.set_key(key)
            system_state['key'] = key
            emit('key_changed', {'key': key}, broadcast=True)
            emit('state_update', system_state, broadcast=True)
            
        except Exception as e:
            emit('error', {'message': str(e)})

@socketio.on('test_tone')
def handle_test_tone():
    """Play a test tone"""
    try:
        if performia_system:
            performia_system.play_test_tone()
        emit('test_tone_played', broadcast=True)
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('set_audio_driver')
def handle_set_audio_driver(data):
    """Set audio driver"""
    driver = data.get('driver')
    try:
        if performia_system:
            performia_system.set_audio_driver(driver)
        emit('audio_driver_changed', {'driver': driver}, broadcast=True)
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('set_sample_rate')
def handle_set_sample_rate(data):
    """Set sample rate"""
    rate = data.get('rate')
    try:
        if performia_system:
            performia_system.set_sample_rate(rate)
        emit('sample_rate_changed', {'rate': rate}, broadcast=True)
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('set_buffer_size')
def handle_set_buffer_size(data):
    """Set buffer size"""
    size = data.get('size')
    try:
        if performia_system:
            performia_system.set_buffer_size(size)
        emit('buffer_size_changed', {'size': size}, broadcast=True)
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('mute_agent')
def handle_mute_agent(data):
    """Mute/unmute an agent"""
    agent = data.get('agent')
    muted = data.get('muted', False)
    try:
        if performia_system:
            performia_system.mute_agent(agent, muted)
        emit('agent_muted', {'agent': agent, 'muted': muted}, broadcast=True)
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('solo_agent')
def handle_solo_agent(data):
    """Solo/unsolo an agent"""
    agent = data.get('agent')
    solo = data.get('solo', False)
    try:
        if performia_system:
            performia_system.solo_agent(agent, solo)
        emit('agent_solo', {'agent': agent, 'solo': solo}, broadcast=True)
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('set_agent_volume')
def handle_set_agent_volume(data):
    """Set agent volume"""
    agent = data.get('agent')
    volume = data.get('volume', 0.7)
    try:
        if performia_system:
            performia_system.set_agent_volume(agent, volume)
        emit('agent_volume_changed', {'agent': agent, 'volume': volume}, broadcast=True)
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('set_parameter')
def handle_set_parameter(data):
    """Set performance parameter"""
    param = data.get('param')
    value = data.get('value')
    try:
        if performia_system:
            performia_system.set_parameter(param, value)
        emit('parameter_changed', {'param': param, 'value': value}, broadcast=True)
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('get_metrics')
def handle_get_metrics():
    """Get current system metrics"""
    try:
        metrics = {
            'latency': 5.3,  # Placeholder - will be replaced with actual metrics
            'cpu': 12.5,
            'memory': 256
        }
        
        # Get actual I/O levels if available
        audio_levels = {
            'input': -12.5,
            'output': -8.2
        }
        
        # Get agent levels
        agent_levels = {
            'drums': -10.5,
            'bass': -12.0,
            'melody': -15.3,
            'harmony': -14.2,
            'listener': -18.5
        }
        
        emit('system_metrics', metrics)
        emit('audio_levels', audio_levels)
        emit('agent_levels', agent_levels)
        
    except Exception as e:
        emit('error', {'message': str(e)})

def monitor_system():
    """Background thread to monitor system metrics"""
    while True:
        if system_state['is_running']:
            try:
                # Get performance metrics
                if performia_system:
                    metrics = performia_system.get_performance_metrics()
                    system_state['performance_metrics'] = metrics
                
                # Get input levels
                if input_system:
                    system_state['input_level'] = input_system.get_input_level()
                    system_state['detected_chord'] = input_system.get_detected_chord()
                
                # Get agent states
                if performia_system:
                    agents = performia_system.get_agent_states()
                    system_state['agents'] = agents
                
                # Emit updates to all clients
                socketio.emit('metrics_update', system_state['performance_metrics'])
                socketio.emit('input_update', {
                    'level': system_state['input_level'],
                    'chord': system_state['detected_chord']
                })
                socketio.emit('agents_update', system_state['agents'])
                
            except Exception as e:
                print(f"Monitor error: {e}")
        
        time.sleep(0.1)  # Update 10 times per second

@app.route('/api/status')
def api_status():
    """REST API endpoint for system status"""
    return jsonify(system_state)

@app.route('/api/presets')
def api_presets():
    """Get available personality presets"""
    presets_path = Path(__file__).parent.parent / 'config' / 'personalities.json'
    if presets_path.exists():
        with open(presets_path) as f:
            presets = json.load(f)
        return jsonify(presets)
    return jsonify({})

if __name__ == '__main__':
    port = 5001
    print(f"🎵 Starting Performia System GUI on http://localhost:{port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)