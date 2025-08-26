"""
Simple Performia System Web GUI - Standalone Test Version
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import time
import threading
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'performia-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Simulated system state
system_state = {
    'is_running': False,
    'mode': 'autonomous',
    'listening_mode': 'chord_follow',
    'agents': {
        'drums': {'aggression': 0.5, 'creativity': 0.7, 'active': False},
        'bass': {'aggression': 0.4, 'creativity': 0.6, 'active': False},
        'melody': {'aggression': 0.3, 'creativity': 0.8, 'active': False},
        'harmony': {'aggression': 0.2, 'creativity': 0.9, 'active': False}
    },
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

monitor_thread = None
stop_event = threading.Event()

@app.route('/')
def index():
    """Serve the main GUI page"""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('state_update', system_state)

@socketio.on('start_system')
def handle_start_system(data):
    """Start the simulated system"""
    global system_state, monitor_thread, stop_event
    
    mode = data.get('mode', 'autonomous')
    system_state['mode'] = mode
    system_state['is_running'] = True
    
    # Activate agents
    for agent in system_state['agents']:
        system_state['agents'][agent]['active'] = True
    
    # Start monitoring thread
    stop_event.clear()
    if not monitor_thread or not monitor_thread.is_alive():
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
    
    emit('system_started', {'status': 'success', 'mode': mode}, broadcast=True)
    emit('state_update', system_state, broadcast=True)

@socketio.on('stop_system')
def handle_stop_system():
    """Stop the simulated system"""
    global system_state, stop_event
    
    system_state['is_running'] = False
    stop_event.set()
    
    # Deactivate agents
    for agent in system_state['agents']:
        system_state['agents'][agent]['active'] = False
    
    emit('system_stopped', {'status': 'success'}, broadcast=True)
    emit('state_update', system_state, broadcast=True)

@socketio.on('update_agent')
def handle_update_agent(data):
    """Update an agent's personality"""
    agent_id = data.get('agent_id')
    personality_params = data.get('personality')
    
    if agent_id in system_state['agents']:
        system_state['agents'][agent_id].update(personality_params)
        emit('agent_updated', {'agent_id': agent_id}, broadcast=True)
        emit('state_update', system_state, broadcast=True)

@socketio.on('set_listening_mode')
def handle_set_listening_mode(data):
    """Change the listening mode"""
    mode = data.get('mode')
    system_state['listening_mode'] = mode
    emit('listening_mode_changed', {'mode': mode}, broadcast=True)
    emit('state_update', system_state, broadcast=True)

@socketio.on('update_tempo')
def handle_update_tempo(data):
    """Update the system tempo"""
    tempo = data.get('tempo', 120)
    system_state['tempo'] = tempo
    emit('tempo_changed', {'tempo': tempo}, broadcast=True)
    emit('state_update', system_state, broadcast=True)

@socketio.on('update_key')
def handle_update_key(data):
    """Update the musical key"""
    key = data.get('key', 0)
    system_state['key'] = key
    emit('key_changed', {'key': key}, broadcast=True)
    emit('state_update', system_state, broadcast=True)

def monitor_system():
    """Background thread to simulate system metrics"""
    while not stop_event.is_set():
        if system_state['is_running']:
            # Simulate performance metrics
            system_state['performance_metrics']['latency'] = random.uniform(5, 15)
            system_state['performance_metrics']['cpu_usage'] = random.uniform(20, 60)
            system_state['performance_metrics']['active_agents'] = sum(
                1 for a in system_state['agents'].values() if a.get('active', False)
            )
            
            # Simulate input in interactive mode
            if system_state['mode'] == 'interactive':
                system_state['input_level'] = random.uniform(0, 0.8)
                if random.random() > 0.7:
                    chords = ['C', 'G', 'Am', 'F', 'Dm', 'Em', 'Cmaj7', 'G7']
                    system_state['detected_chord'] = random.choice(chords)
            
            # Emit updates to all clients
            socketio.emit('metrics_update', system_state['performance_metrics'])
            socketio.emit('input_update', {
                'level': system_state['input_level'],
                'chord': system_state['detected_chord']
            })
            socketio.emit('agents_update', system_state['agents'])
        
        time.sleep(0.1)  # Update 10 times per second

@app.route('/api/status')
def api_status():
    """REST API endpoint for system status"""
    return jsonify(system_state)

if __name__ == '__main__':
    port = 5001
    print(f"🎵 Starting Performia System GUI (Demo Mode) on http://localhost:{port}")
    print("   This is a demonstration version with simulated data")
    print("   Press Ctrl+C to stop")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)