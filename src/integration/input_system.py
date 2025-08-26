"""Main integration module for audio input system"""

import asyncio
import logging
from typing import Dict, Optional
import yaml
from pathlib import Path

from ..controllers import MidiPedalController, AudioInputController
try:
    from ..agents.listener_agent_simple import ListenerAgent
except ImportError:
    from ..agents.listener_agent import ListenerAgent
from ..memory import SharedMemory


class InputSystem:
    """
    Integrates audio input, MIDI control, and agent communication
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the input system"""
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.audio_input = None
        self.midi_controller = None
        self.listener_agent = None
        self.shared_memory = None
        
        # System state
        self.is_running = False
        
    async def initialize(self):
        """Initialize all components"""
        self.logger.info("Initializing Performia Input System...")
        
        # Initialize shared memory
        self.shared_memory = SharedMemory(
            buffer_size=self.config['memory']['buffer_size']
        )
        
        # Initialize audio input if enabled
        if self.config['audio_input']['enabled']:
            self.audio_input = AudioInputController(
                device_name=self.config['audio_input']['device'],
                sample_rate=self.config['audio']['sample_rate'],
                block_size=self.config['audio']['block_size'],
                channels=self.config['audio_input']['channels']
            )
            self.logger.info("Audio input controller initialized")
        
        # Initialize MIDI controller if enabled
        if self.config['midi']['enabled']:
            self.midi_controller = MidiPedalController(
                device_name=self.config['midi']['device']
            )
            self.logger.info("MIDI controller initialized")
        
        # Create listener agent
        self.listener_agent = ListenerAgent(
            agent_id="listener",
            memory=self.shared_memory
        )
        self.logger.info("Listener agent created")
        
        # Connect components
        await self._connect_components()
        
        self.logger.info("Input system initialization complete")
    
    async def _connect_components(self):
        """Wire up callbacks between components"""
        
        if self.audio_input and self.listener_agent:
            # Connect audio analysis to listener agent
            self.audio_input.register_analysis_callback(
                self.listener_agent.process_guitar_input
            )
        
        if self.midi_controller and self.listener_agent:
            # Connect MIDI pedal events to listener agent
            self.midi_controller.register_callback(
                'listen_start',
                lambda _: asyncio.create_task(self._start_listening())
            )
            
            self.midi_controller.register_callback(
                'listen_stop',
                lambda _: asyncio.create_task(self._stop_listening())
            )
            
            self.midi_controller.register_callback(
                'mode_change',
                self.listener_agent.on_mode_change
            )
            
            self.midi_controller.register_callback(
                'expression',
                self.listener_agent.on_expression_pedal
            )
            
            self.midi_controller.register_callback(
                'tap_tempo',
                self.listener_agent.on_tap_tempo
            )
    
    async def _start_listening(self):
        """Start audio input listening"""
        if self.audio_input:
            await self.audio_input.start_listening()
        if self.listener_agent:
            await self.listener_agent.on_listening_start()
        self.logger.info("Started listening to guitar input")
    
    async def _stop_listening(self):
        """Stop audio input listening"""
        if self.audio_input:
            await self.audio_input.stop_listening()
        if self.listener_agent:
            await self.listener_agent.on_listening_stop()
        self.logger.info("Stopped listening to guitar input")
    
    async def start(self):
        """Start the input system"""
        if self.is_running:
            return
        
        self.logger.info("Starting input system...")
        self.is_running = True
        
        # Start components
        tasks = []
        
        if self.midi_controller:
            tasks.append(asyncio.create_task(self.midi_controller.listen()))
            
        if self.listener_agent:
            tasks.append(asyncio.create_task(self.listener_agent.run()))
        
        # Run all tasks
        if tasks:
            await asyncio.gather(*tasks)
    
    async def stop(self):
        """Stop the input system"""
        if not self.is_running:
            return
        
        self.logger.info("Stopping input system...")
        
        # Stop audio input
        if self.audio_input and self.audio_input.is_listening:
            await self.audio_input.stop_listening()
        
        # Close MIDI
        if self.midi_controller:
            self.midi_controller.close()
        
        self.is_running = False
        self.logger.info("Input system stopped")
    
    async def calibrate(self):
        """Run input calibration"""
        if self.audio_input:
            self.logger.info("Running input calibration...")
            results = await self.audio_input.calibrate_input(duration=3.0)
            self.logger.info(f"Calibration results: {results}")
            return results
        return None
    
    def get_status(self) -> Dict:
        """Get system status"""
        status = {
            'running': self.is_running,
            'audio_input': None,
            'midi': None,
            'listener': None
        }
        
        if self.audio_input:
            status['audio_input'] = {
                'listening': self.audio_input.is_listening,
                'level': self.audio_input.get_input_level(),
                'chord': self.audio_input.get_detected_chord(),
                'pitch': self.audio_input.get_detected_pitch(),
                'latency': self.audio_input.get_latency_stats()
            }
        
        if self.midi_controller:
            status['midi'] = self.midi_controller.get_status()
        
        if self.listener_agent:
            status['listener'] = self.listener_agent.get_status()
        
        return status


async def test_input_system():
    """Test the input system"""
    logging.basicConfig(level=logging.INFO)
    
    system = InputSystem()
    await system.initialize()
    
    print("\n" + "="*50)
    print("PERFORMIA INPUT SYSTEM TEST")
    print("="*50)
    print("\nControls:")
    print("- Press SUSTAIN pedal (CC64) to start/stop listening")
    print("- Press PORTAMENTO pedal (CC65) to change modes")
    print("- Use EXPRESSION pedal (CC11) for dynamics")
    print("- Tap TEMPO pedal (CC80) to set tempo")
    print("\nPress Ctrl+C to exit")
    print("="*50 + "\n")
    
    try:
        # Run calibration
        print("Running input calibration (play some notes)...")
        await system.calibrate()
        
        # Start system
        await system.start()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        await system.stop()


if __name__ == "__main__":
    asyncio.run(test_input_system())
