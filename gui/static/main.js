// Performia GUI - Main JavaScript
const socket = io();

// State management
let isConnected = false;
let muteStates = {};
let soloStates = {};
let agentVolumes = {
    drums: 70,
    bass: 70,
    melody: 70,
    harmony: 70,
    listener: 70
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeControls();
    setupSocketHandlers();
    startMetricsUpdate();
});

// Initialize all controls
function initializeControls() {
    // Test tone button
    document.getElementById('testToneBtn').addEventListener('click', () => {
        socket.emit('test_tone');
    });
    
    // Audio settings
    document.getElementById('audioDriver').addEventListener('change', (e) => {
        socket.emit('set_audio_driver', { driver: e.target.value });
    });
    
    document.getElementById('sampleRate').addEventListener('change', (e) => {
        socket.emit('set_sample_rate', { rate: parseInt(e.target.value) });
    });
    
    document.getElementById('bufferSize').addEventListener('change', (e) => {
        socket.emit('set_buffer_size', { size: parseInt(e.target.value) });
    });
    
    // Track controls
    document.querySelectorAll('.btn-mute').forEach(btn => {
        const agent = btn.dataset.agent;
        muteStates[agent] = false;
        
        btn.addEventListener('click', () => {
            muteStates[agent] = !muteStates[agent];
            btn.classList.toggle('active', muteStates[agent]);
            socket.emit('mute_agent', { agent, muted: muteStates[agent] });
        });
    });
    
    document.querySelectorAll('.btn-solo').forEach(btn => {
        const agent = btn.dataset.agent;
        soloStates[agent] = false;
        
        btn.addEventListener('click', () => {
            soloStates[agent] = !soloStates[agent];
            btn.classList.toggle('active', soloStates[agent]);
            socket.emit('solo_agent', { agent, solo: soloStates[agent] });
        });
    });
    
    // Volume sliders
    ['drums', 'bass', 'melody', 'harmony', 'listener'].forEach(agent => {
        const slider = document.getElementById(`${agent}Volume`);
        if (slider) {
            slider.addEventListener('input', (e) => {
                agentVolumes[agent] = e.target.value;
                socket.emit('set_agent_volume', { agent, volume: e.target.value / 100 });
            });
        }
    });
    
    // Parameter sliders
    ['aggression', 'creativity', 'responsiveness', 'stability'].forEach(param => {
        const slider = document.getElementById(param);
        if (slider) {
            slider.addEventListener('input', (e) => {
                socket.emit('set_parameter', { param, value: e.target.value / 100 });
            });
        }
    });
}

// Socket.io event handlers
function setupSocketHandlers() {
    socket.on('connect', () => {
        isConnected = true;
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', () => {
        isConnected = false;
        updateConnectionStatus(false);
    });
    
    socket.on('audio_levels', (data) => {
        updateAudioLevels(data);
    });
    
    socket.on('agent_levels', (data) => {
        updateAgentLevels(data);
    });
    
    socket.on('system_metrics', (data) => {
        updateSystemMetrics(data);
    });
}

// Update connection status
function updateConnectionStatus(connected) {
    const indicator = document.getElementById('statusIndicator');
    const text = document.getElementById('statusText');
    
    if (connected) {
        indicator.classList.add('connected');
        text.textContent = 'Connected';
    } else {
        indicator.classList.remove('connected');
        text.textContent = 'Disconnected';
    }
}

// Update audio I/O levels
function updateAudioLevels(data) {
    // Input level
    if (data.input !== undefined) {
        const inputPercent = dbToPercent(data.input);
        document.getElementById('inputLevel').style.width = `${inputPercent}%`;
        document.getElementById('inputValue').textContent = formatDb(data.input);
    }
    
    // Output level
    if (data.output !== undefined) {
        const outputPercent = dbToPercent(data.output);
        document.getElementById('outputLevel').style.width = `${outputPercent}%`;
        document.getElementById('outputValue').textContent = formatDb(data.output);
    }
}

// Update individual agent levels
function updateAgentLevels(data) {
    Object.entries(data).forEach(([agent, level]) => {
        const levelBar = document.getElementById(`${agent}Level`);
        if (levelBar) {
            const percent = dbToPercent(level);
            levelBar.style.width = `${percent}%`;
        }
    });
}

// Update system metrics
function updateSystemMetrics(data) {
    if (data.latency !== undefined) {
        document.getElementById('latencyDisplay').textContent = `${data.latency.toFixed(1)} ms`;
    }
    
    if (data.cpu !== undefined) {
        document.getElementById('cpuDisplay').textContent = `${data.cpu.toFixed(0)}%`;
    }
    
    if (data.memory !== undefined) {
        document.getElementById('memoryDisplay').textContent = `${data.memory.toFixed(0)} MB`;
    }
}

// Utility functions
function dbToPercent(db) {
    // Convert dB to percentage for meter display
    // -60dB = 0%, 0dB = 100%
    if (db <= -60) return 0;
    if (db >= 0) return 100;
    return (db + 60) / 60 * 100;
}

function formatDb(db) {
    if (db <= -60) return '-∞ dB';
    return `${db.toFixed(1)} dB`;
}

// Sidebar toggle
window.toggleSidebar = function(side) {
    const sidebar = side === 'left' ? 
        document.getElementById('leftSidebar') : 
        document.getElementById('rightSidebar');
    
    sidebar.classList.toggle('collapsed');
    
    // Update toggle icon
    const icon = sidebar.querySelector('.toggle-icon');
    if (side === 'left') {
        icon.textContent = sidebar.classList.contains('collapsed') ? '▶' : '◀';
    } else {
        icon.textContent = sidebar.classList.contains('collapsed') ? '◀' : '▶';
    }
};

// Request metrics updates periodically
function startMetricsUpdate() {
    setInterval(() => {
        if (isConnected) {
            socket.emit('get_metrics');
        }
    }, 100); // Update at 10Hz
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Space bar for play/pause
    if (e.code === 'Space' && e.target.tagName !== 'INPUT') {
        e.preventDefault();
        socket.emit('toggle_playback');
    }
    
    // T for test tone
    if (e.key === 't' || e.key === 'T') {
        socket.emit('test_tone');
    }
    
    // Number keys for agent mute
    if (e.key >= '1' && e.key <= '5') {
        const agents = ['drums', 'bass', 'melody', 'harmony', 'listener'];
        const agent = agents[parseInt(e.key) - 1];
        const btn = document.querySelector(`.btn-mute[data-agent="${agent}"]`);
        if (btn) btn.click();
    }
});