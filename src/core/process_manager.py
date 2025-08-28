"""
Process isolation manager for zero GUI impact on audio performance
Manages separate processes with appropriate priorities
"""

import multiprocessing as mp
import asyncio
import os
import sys
import signal
import logging
import time
from typing import Optional, Dict, Any
from pathlib import Path

# Platform-specific imports
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    logging.warning("psutil not installed - process priority management disabled")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.memory.shared_buffer import AudioEventBuffer, EventType
from src.engine.supercollider import SuperColliderEngine

logger = logging.getLogger(__name__)

class ProcessPriority:
    """Platform-independent process priority settings"""
    REALTIME = -20  # Highest priority (Unix nice value)
    HIGH = -10
    NORMAL = 0
    LOW = 10
    IDLE = 19  # Lowest priority

class PerformiaProcess(mp.Process):
    """Base class for Performia system processes"""
    
    def __init__(self, name: str, priority: int = ProcessPriority.NORMAL):
        super().__init__(name=name)
        self.priority = priority
        self.shared_buffer = None
        self.running = mp.Event()
        self.stats = mp.Manager().dict()
        
    def setup_priority(self):
        """Set process priority based on platform"""
        if not HAS_PSUTIL:
            return
            
        try:
            p = psutil.Process(os.getpid())
            
            # Set nice value on Unix-like systems
            if hasattr(p, 'nice'):
                p.nice(self.priority)
                logger.info(f"{self.name}: Set priority to {self.priority}")
            
            # Windows priority classes
            elif sys.platform == 'win32':
                priority_class = {
                    ProcessPriority.REALTIME: psutil.REALTIME_PRIORITY_CLASS,
                    ProcessPriority.HIGH: psutil.HIGH_PRIORITY_CLASS,
                    ProcessPriority.NORMAL: psutil.NORMAL_PRIORITY_CLASS,
                    ProcessPriority.LOW: psutil.BELOW_NORMAL_PRIORITY_CLASS,
                    ProcessPriority.IDLE: psutil.IDLE_PRIORITY_CLASS
                }.get(self.priority, psutil.NORMAL_PRIORITY_CLASS)
                
                p.nice(priority_class)
                
        except Exception as e:
            logger.warning(f"Could not set process priority: {e}")
    
    def setup_cpu_affinity(self, cpu_list: list):
        """Pin process to specific CPU cores"""
        if not HAS_PSUTIL:
            return
            
        try:
            p = psutil.Process(os.getpid())
            if hasattr(p, 'cpu_affinity'):
                p.cpu_affinity(cpu_list)
                logger.info(f"{self.name}: Pinned to CPUs {cpu_list}")
        except Exception as e:
            logger.warning(f"Could not set CPU affinity: {e}")
    
    def run(self):
        """Process main loop - override in subclasses"""
        self.setup_priority()
        self.running.set()
        
        try:
            # Connect to shared memory
            self.shared_buffer = AudioEventBuffer("PerformiaBuffer", create=False)
            logger.info(f"{self.name}: Connected to shared buffer")
            
            # Run main loop
            self.main_loop()
            
        except Exception as e:
            logger.error(f"{self.name} error: {e}")
        finally:
            self.cleanup()
    
    def main_loop(self):
        """Override this in subclasses"""
        pass
    
    def cleanup(self):
        """Clean up resources"""
        if self.shared_buffer:
            self.shared_buffer.close()
        self.running.clear()

class AudioProcess(PerformiaProcess):
    """Audio synthesis process - highest priority"""
    
    def __init__(self):
        super().__init__("AudioProcess", ProcessPriority.REALTIME)
        self.sc_engine = None
        
    def main_loop(self):
        """Audio process main loop"""
        # Pin to first 4 CPU cores for audio processing
        self.setup_cpu_affinity([0, 1, 2, 3])
        
        # Start SuperCollider engine
        logger.info("Starting SuperCollider engine...")
        
        # Connect to already-running Supernova server
        logger.info("Connecting to Supernova server on port 57110...")
        
        # Initialize OSC client for SuperCollider communication
        from pythonosc import udp_client
        self.osc_client = udp_client.SimpleUDPClient("127.0.0.1", 57110)
        
        # Send test message
        try:
            self.osc_client.send_message("/status", 1)
            logger.info("✓ Connected to Supernova")
        except Exception as e:
            logger.warning(f"Could not connect to Supernova: {e}")
        
        # Monitor shared memory for events
        reader_id = 0  # Audio process uses reader 0
        
        while self.running.is_set():
            events = self.shared_buffer.read_events(reader_id, max_events=50)
            
            for event in events:
                timestamp, agent_id, event_type, pitch, velocity, duration, flags = event
                
                # Process musical events
                if event_type == EventType.NOTE_ON:
                    # Send to SuperCollider
                    logger.debug(f"Playing note: pitch={pitch}, vel={velocity}")
                    try:
                        # Create synth in SuperCollider
                        self.osc_client.send_message("/s_new", [
                            "sine", -1, 1, 0,
                            "freq", pitch * 8.175799,
                            "amp", velocity
                        ])
                    except:
                        pass
                
            # Sleep briefly to avoid busy waiting
            time.sleep(0.001)  # 1ms polling rate
    
    def cleanup(self):
        """Clean up audio resources"""
        if hasattr(self, 'sc_process'):
            self.sc_process.terminate()
            self.sc_process.wait()
        super().cleanup()

class ControlProcess(PerformiaProcess):
    """Agent control and AI process - normal priority"""
    
    def __init__(self):
        super().__init__("ControlProcess", ProcessPriority.NORMAL)
        self.agents = []
        
    def main_loop(self):
        """Control process main loop"""
        # Pin to CPU cores 4-5
        self.setup_cpu_affinity([4, 5])
        
        # Initialize agents
        from src.main_simple import SimpleMusicalAgent
        
        roles = ['drums', 'bass', 'melody', 'harmony']
        for i in range(4):
            agent = SimpleMusicalAgent(f"Agent_{i}", roles[i])
            self.agents.append(agent)
        
        logger.info(f"Initialized {len(self.agents)} agents")
        
        # Agent decision loop
        decision_rate = 20  # Hz
        interval = 1.0 / decision_rate
        
        while self.running.is_set():
            start_time = time.perf_counter()
            
            # Each agent makes decisions
            for i, agent in enumerate(self.agents):
                # Simple pattern generation
                if time.time() % 0.5 < 0.1:  # Trigger events periodically
                    self.shared_buffer.write_event(
                        agent_id=i,
                        event_type=EventType.NOTE_ON,
                        pitch=60 + (i * 7),  # Different pitch per agent
                        velocity=0.7,
                        duration=200
                    )
            
            # Maintain decision rate
            elapsed = time.perf_counter() - start_time
            if elapsed < interval:
                time.sleep(interval - elapsed)

class GUIProcess(PerformiaProcess):
    """Web GUI process - low priority, read-only access"""
    
    def __init__(self):
        super().__init__("GUIProcess", ProcessPriority.LOW)
        
    def main_loop(self):
        """GUI process main loop"""
        # Pin to CPU cores 6-7
        self.setup_cpu_affinity([6, 7])
        
        # Import Flask app
        os.environ['FLASK_ENV'] = 'production'
        
        # Change to GUI directory and start Flask
        gui_path = Path(__file__).parent.parent.parent / "gui"
        
        # Add paths for imports
        import sys
        sys.path.insert(0, str(gui_path.parent))
        sys.path.insert(0, str(gui_path))
        
        os.chdir(gui_path)
        
        # Start Flask app on port 5001
        try:
            from app import app, socketio
            logger.info("Starting GUI on http://localhost:5001")
            socketio.run(app, host='0.0.0.0', port=5001, debug=False)
        except ImportError as e:
            logger.error(f"Could not import GUI: {e}")
            # Run simple GUI as fallback
            from app_simple import app
            logger.info("Starting simple GUI on http://localhost:5001")
            app.run(host='0.0.0.0', port=5001, debug=False, allow_unsafe_werkzeug=True)

class PerformiaProcessManager:
    """Manages all Performia system processes"""
    
    def __init__(self):
        self.shared_buffer = None
        self.audio_process = None
        self.control_process = None
        self.gui_process = None
        self.processes = []
        
    def start(self):
        """Start all system processes"""
        logger.info("="*50)
        logger.info("Starting Performia Process Manager")
        logger.info("="*50)
        
        # Create shared memory buffer
        logger.info("Creating shared memory buffer...")
        self.shared_buffer = AudioEventBuffer("PerformiaBuffer", create=True)
        logger.info(f"✓ Shared memory created (1MB)")
        
        # Start audio process (highest priority)
        logger.info("Starting audio process...")
        self.audio_process = AudioProcess()
        self.audio_process.start()
        self.processes.append(self.audio_process)
        time.sleep(1)  # Let audio initialize
        
        # Start control process (normal priority)
        logger.info("Starting control process...")
        self.control_process = ControlProcess()
        self.control_process.start()
        self.processes.append(self.control_process)
        
        # Start GUI process (low priority)
        logger.info("Starting GUI process...")
        self.gui_process = GUIProcess()
        self.gui_process.start()
        self.processes.append(self.gui_process)
        
        logger.info("-"*50)
        logger.info("✓ All processes started")
        logger.info(f"✓ Audio: PID {self.audio_process.pid} (RT priority)")
        logger.info(f"✓ Control: PID {self.control_process.pid} (Normal priority)")
        logger.info(f"✓ GUI: PID {self.gui_process.pid} (Low priority)")
        logger.info("-"*50)
        
        # Monitor processes
        self.monitor()
    
    def monitor(self):
        """Monitor process health and performance"""
        try:
            while True:
                time.sleep(1)
                
                # Check process health
                for process in self.processes:
                    if not process.is_alive():
                        logger.error(f"Process {process.name} died!")
                        self.restart_process(process)
                
                # Get buffer stats
                stats = self.shared_buffer.get_buffer_stats()
                if stats['buffer_usage'] > 0.8:
                    logger.warning(f"Buffer usage high: {stats['buffer_usage']*100:.1f}%")
                    
        except KeyboardInterrupt:
            logger.info("Shutdown requested...")
            self.stop()
    
    def restart_process(self, process):
        """Restart a failed process"""
        logger.info(f"Restarting {process.name}...")
        
        if isinstance(process, AudioProcess):
            self.audio_process = AudioProcess()
            self.audio_process.start()
        elif isinstance(process, ControlProcess):
            self.control_process = ControlProcess()
            self.control_process.start()
        elif isinstance(process, GUIProcess):
            self.gui_process = GUIProcess()
            self.gui_process.start()
    
    def stop(self):
        """Stop all processes gracefully"""
        logger.info("Stopping all processes...")
        
        # Signal processes to stop
        for process in self.processes:
            if process.is_alive():
                process.running.clear()
        
        # Wait for processes to finish
        for process in self.processes:
            process.join(timeout=5)
            if process.is_alive():
                logger.warning(f"Force terminating {process.name}")
                process.terminate()
        
        # Clean up shared memory
        if self.shared_buffer:
            self.shared_buffer.cleanup()
        
        logger.info("✓ All processes stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal")
    sys.exit(0)

def main():
    """Main entry point for process manager"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s'
    )
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the process manager
    manager = PerformiaProcessManager()
    manager.start()

if __name__ == "__main__":
    main()