// Performia System GUI JavaScript

// Initialize Socket.IO connection
const socket = io();

// Global state
let systemRunning = false;
let currentMode = 'autonomous';
let latencyChart = null;
let activityChart = null;

// DOM elements
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const systemStatus = document.getElementById('system-status');
const latencyDisplay = document.getElementById('latency-display');
const cpuDisplay = document.getElementById('cpu-display');
const inputControls = document.getElementById('input-controls');
const tempoSlider = document.getElementById('tempo');
const tempoValue = document.getElementById('tempo-value');
const keySelect = document.getElementById('key');
const inputLevel = document.getElementById('input-level');
const chordDisplay = document.getElementById('chord-display');

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    initializeCharts();
    setupPersonalitySliders();
    setupModeButtons();
    setupPedalButtons();
    setupPresetButtons();
});

// Socket.IO event listeners
socket.on('connect', () => {
    console.log('Connected to Performia System');
});

socket.on('state_update', (state) => {
    updateSystemState(state);
});

socket.on('system_started', (data) => {
    systemRunning = true;
    updateControlStates();
    showNotification('System started successfully', 'success');
});

socket.on('system_stopped', () => {
    systemRunning = false;
    updateControlStates();
    showNotification('System stopped', 'info');
});

socket.on('metrics_update', (metrics) => {
    updateMetrics(metrics);
});

socket.on('input_update', (data) => {
    updateInputDisplay(data);
});

socket.on('agents_update', (agents) => {
    updateAgentStatus(agents);
});

socket.on('error', (data) => {
    showNotification(`Error: ${data.message}`, 'error');
});

// Initialize event listeners
function initializeEventListeners() {
    // Start/Stop buttons
    startBtn.addEventListener('click', startSystem);
    stopBtn.addEventListener('click', stopSystem);
    
    // Mode selector
    document.querySelectorAll('input[name="mode"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentMode = e.target.value;
            inputControls.style.display = currentMode === 'interactive' ? 'block' : 'none';
        });
    });
    
    // Tempo slider
    tempoSlider.addEventListener('input', (e) => {
        const tempo = e.target.value;
        tempoValue.textContent = tempo;
        if (systemRunning) {
            socket.emit('update_tempo', { tempo: parseInt(tempo) });
        }
    });
    
    // Key selector
    keySelect.addEventListener('change', (e) => {
        if (systemRunning) {
            socket.emit('update_key', { key: parseInt(e.target.value) });
        }
    });
}

// System control functions
function startSystem() {
    const enableMidi = document.querySelector('input[name="enable-midi"]:checked')?.value === 'true';
    
    socket.emit('start_system', {
        mode: currentMode,
        enable_midi: enableMidi
    });
}

function stopSystem() {
    socket.emit('stop_system');
}

function updateControlStates() {
    startBtn.disabled = systemRunning;
    stopBtn.disabled = !systemRunning;
    
    if (systemRunning) {
        systemStatus.textContent = '● System Online';
        systemStatus.classList.remove('offline');
        systemStatus.classList.add('online');
    } else {
        systemStatus.textContent = '● System Offline';
        systemStatus.classList.remove('online');
        systemStatus.classList.add('offline');
    }
}

// Update system state
function updateSystemState(state) {
    systemRunning = state.is_running;
    currentMode = state.mode;
    
    updateControlStates();
    
    // Update tempo
    if (state.tempo) {
        tempoSlider.value = state.tempo;
        tempoValue.textContent = state.tempo;
    }
    
    // Update key
    if (state.key !== undefined) {
        keySelect.value = state.key;
    }
    
    // Update mode radio buttons
    document.querySelector(`input[name="mode"][value="${currentMode}"]`).checked = true;
    inputControls.style.display = currentMode === 'interactive' ? 'block' : 'none';
}

// Update performance metrics
function updateMetrics(metrics) {
    // Update displays
    latencyDisplay.textContent = `Latency: ${metrics.latency.toFixed(1)}ms`;
    cpuDisplay.textContent = `CPU: ${metrics.cpu_usage.toFixed(0)}%`;
    
    // Update charts
    updateLatencyChart(metrics.latency);
    updateActivityChart(metrics.active_agents);
}

// Update input display
function updateInputDisplay(data) {
    // Update input level meter
    const level = Math.min(100, Math.max(0, data.level * 100));
    inputLevel.style.width = `${level}%`;
    
    // Update chord display
    chordDisplay.textContent = data.chord || '--';
}

// Update agent status
function updateAgentStatus(agents) {
    Object.entries(agents).forEach(([agentId, agentData]) => {
        const card = document.querySelector(`.agent-card[data-agent="${agentId}"]`);
        if (card) {
            const statusElement = card.querySelector('.agent-status');
            const activityText = card.querySelector('.activity-text');
            
            if (agentData.is_playing) {
                statusElement.classList.add('active');
                activityText.textContent = 'Playing';
            } else {
                statusElement.classList.remove('active');
                activityText.textContent = 'Idle';
            }
        }
    });
}

// Setup personality sliders
function setupPersonalitySliders() {
    document.querySelectorAll('.personality-slider').forEach(slider => {
        slider.addEventListener('input', (e) => {
            const value = (e.target.value / 100).toFixed(2);
            const valueDisplay = e.target.nextElementSibling;
            valueDisplay.textContent = value;
            
            if (systemRunning) {
                const agentCard = e.target.closest('.agent-card');
                const agentId = agentCard.dataset.agent;
                const param = e.target.dataset.param;
                
                // Collect all parameters for this agent
                const personality = {};
                agentCard.querySelectorAll('.personality-slider').forEach(s => {
                    personality[s.dataset.param] = s.value / 100;
                });
                
                socket.emit('update_agent', {
                    agent_id: agentId,
                    personality: personality
                });
            }
        });
    });
}

// Setup mode buttons
function setupModeButtons() {
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Update active state
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            // Emit mode change
            const mode = e.target.dataset.mode;
            socket.emit('set_listening_mode', { mode: mode });
        });
    });
}

// Setup pedal buttons
function setupPedalButtons() {
    document.querySelectorAll('.pedal-btn').forEach(btn => {
        btn.addEventListener('mousedown', (e) => {
            const pedalType = e.target.closest('.pedal-btn').dataset.pedal;
            socket.emit('trigger_pedal', { pedal_type: pedalType });
            
            // Visual feedback
            e.target.closest('.pedal-btn').style.background = 'var(--primary-color)';
            e.target.closest('.pedal-btn').style.color = 'white';
        });
        
        btn.addEventListener('mouseup', (e) => {
            // Reset visual
            setTimeout(() => {
                e.target.closest('.pedal-btn').style.background = '';
                e.target.closest('.pedal-btn').style.color = '';
            }, 100);
        });
    });
}

// Setup preset buttons
function setupPresetButtons() {
    const presets = {
        jazz: {
            drums: { aggression: 0.3, creativity: 0.7, responsiveness: 0.6, stability: 0.5 },
            bass: { aggression: 0.2, creativity: 0.6, responsiveness: 0.8, stability: 0.7 },
            melody: { aggression: 0.1, creativity: 0.9, responsiveness: 0.5, stability: 0.3 },
            harmony: { aggression: 0.1, creativity: 0.8, responsiveness: 0.9, stability: 0.6 }
        },
        rock: {
            drums: { aggression: 0.8, creativity: 0.3, responsiveness: 0.5, stability: 0.8 },
            bass: { aggression: 0.6, creativity: 0.3, responsiveness: 0.6, stability: 0.9 },
            melody: { aggression: 0.7, creativity: 0.5, responsiveness: 0.4, stability: 0.6 },
            harmony: { aggression: 0.5, creativity: 0.4, responsiveness: 0.7, stability: 0.7 }
        },
        ambient: {
            drums: { aggression: 0.1, creativity: 0.5, responsiveness: 0.3, stability: 0.2 },
            bass: { aggression: 0.1, creativity: 0.7, responsiveness: 0.4, stability: 0.8 },
            melody: { aggression: 0.05, creativity: 0.9, responsiveness: 0.6, stability: 0.3 },
            harmony: { aggression: 0.05, creativity: 0.95, responsiveness: 0.7, stability: 0.4 }
        },
        experimental: {
            drums: { aggression: 0.6, creativity: 0.9, responsiveness: 0.7, stability: 0.2 },
            bass: { aggression: 0.5, creativity: 0.95, responsiveness: 0.8, stability: 0.1 },
            melody: { aggression: 0.4, creativity: 1.0, responsiveness: 0.9, stability: 0.1 },
            harmony: { aggression: 0.3, creativity: 1.0, responsiveness: 0.95, stability: 0.15 }
        },
        classical: {
            drums: { aggression: 0.2, creativity: 0.2, responsiveness: 0.4, stability: 0.9 },
            bass: { aggression: 0.1, creativity: 0.3, responsiveness: 0.5, stability: 0.95 },
            melody: { aggression: 0.15, creativity: 0.4, responsiveness: 0.6, stability: 0.8 },
            harmony: { aggression: 0.1, creativity: 0.35, responsiveness: 0.8, stability: 0.85 }
        }
    };
    
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const presetName = e.target.dataset.preset;
            const preset = presets[presetName];
            
            if (preset) {
                // Apply preset to all agents
                Object.entries(preset).forEach(([agentId, params]) => {
                    const card = document.querySelector(`.agent-card[data-agent="${agentId}"]`);
                    if (card) {
                        Object.entries(params).forEach(([param, value]) => {
                            const slider = card.querySelector(`.personality-slider[data-param="${param}"]`);
                            if (slider) {
                                slider.value = value * 100;
                                slider.nextElementSibling.textContent = value.toFixed(2);
                            }
                        });
                        
                        // Emit update if system is running
                        if (systemRunning) {
                            socket.emit('update_agent', {
                                agent_id: agentId,
                                personality: params
                            });
                        }
                    }
                });
                
                showNotification(`Applied ${presetName} preset`, 'success');
            }
        });
    });
}

// Initialize charts
function initializeCharts() {
    // Latency chart
    const latencyCtx = document.getElementById('latency-chart').getContext('2d');
    latencyChart = new Chart(latencyCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Latency (ms)',
                data: [],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 20,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#cbd5e1'
                    }
                }
            }
        }
    });
    
    // Activity chart
    const activityCtx = document.getElementById('activity-chart').getContext('2d');
    activityChart = new Chart(activityCtx, {
        type: 'bar',
        data: {
            labels: ['Drums', 'Bass', 'Melody', 'Harmony'],
            datasets: [{
                label: 'Agent Activity',
                data: [0, 0, 0, 0],
                backgroundColor: [
                    'rgba(239, 68, 68, 0.7)',
                    'rgba(245, 158, 11, 0.7)',
                    'rgba(16, 185, 129, 0.7)',
                    'rgba(139, 92, 246, 0.7)'
                ],
                borderColor: [
                    '#ef4444',
                    '#f59e0b',
                    '#10b981',
                    '#8b5cf6'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#cbd5e1'
                    }
                }
            }
        }
    });
}

// Update latency chart
function updateLatencyChart(latency) {
    if (!latencyChart) return;
    
    const now = new Date().toLocaleTimeString();
    latencyChart.data.labels.push(now);
    latencyChart.data.datasets[0].data.push(latency);
    
    // Keep only last 20 data points
    if (latencyChart.data.labels.length > 20) {
        latencyChart.data.labels.shift();
        latencyChart.data.datasets[0].data.shift();
    }
    
    latencyChart.update();
}

// Update activity chart
function updateActivityChart(activeAgents) {
    if (!activityChart) return;
    
    // Simulate activity levels (in real implementation, get from backend)
    const activity = [
        Math.random() * 100,
        Math.random() * 100,
        Math.random() * 100,
        Math.random() * 100
    ];
    
    activityChart.data.datasets[0].data = activity;
    activityChart.update();
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    // Set background color based on type
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        info: '#6366f1',
        warning: '#f59e0b'
    };
    notification.style.background = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);