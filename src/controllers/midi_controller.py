"""MIDI controller for pedal input and control changes"""

import mido
import asyncio
from typing import Callable, Dict, Optional, List
import logging
from enum import Enum


class ListeningMode(Enum):
    """Different listening/response modes for the system"""
    CHORD_FOLLOW = "chord"      # Agents follow chord progressions
    CALL_RESPONSE = "response"   # Agents respond to phrases
    RHYTHMIC_SYNC = "rhythm"     # Agents sync to strumming pattern
    AMBIENT_LAYER = "ambient"    # Agents provide texture
    OFF = "off"                  # Not listening


class MidiPedalController:
    """
    MIDI pedal controller for triggering analysis and mode changes
    Optimized for Presonus Quantum 2626
    """
    
    def __init__(self, device_name: Optional[str] = None):
        """
        Initialize MIDI controller
        
        Args:
            device_name: MIDI input device name (auto-detect if None)
        """
        self.logger = logging.getLogger(__name__)
        self.device_name = device_name
        self.input_port = None
        self.listening = False
        self.mode = ListeningMode.OFF
        
        # Callbacks for different events
        self.callbacks: Dict[str, List[Callable]] = {
            'listen_start': [],
            'listen_stop': [],
            'mode_change': [],
            'expression': [],
            'tap_tempo': []
        }
        
        # Default CC mappings (configurable)
        self.cc_mappings = {
            64: 'sustain',      # Sustain pedal - main listen trigger
            65: 'portamento',   # Portamento - mode switching
            66: 'sostenuto',    # Sostenuto - dynamics control
            67: 'soft',         # Soft pedal - sensitivity
            11: 'expression',   # Expression pedal - continuous control
            80: 'tap_tempo',    # General purpose - tap tempo
        }
        
        # Mode cycle order
        self.mode_cycle = [
            ListeningMode.CHORD_FOLLOW,
            ListeningMode.CALL_RESPONSE,
            ListeningMode.RHYTHMIC_SYNC,
            ListeningMode.AMBIENT_LAYER
        ]
        self.mode_index = 0
        
        # Tap tempo detection
        self.tap_times = []
        self.tap_timeout = 2.0  # Reset taps after 2 seconds
        
        # Connect to MIDI device
        self._connect()
    
    def _connect(self):
        """Connect to MIDI input device"""
        try:
            # List available MIDI inputs
            available_inputs = mido.get_input_names()
            self.logger.info(f"Available MIDI inputs: {available_inputs}")
            
            if self.device_name:
                # Use specified device
                if self.device_name in available_inputs:
                    self.input_port = mido.open_input(self.device_name)
                    self.logger.info(f"Connected to MIDI device: {self.device_name}")
                else:
                    self.logger.error(f"MIDI device not found: {self.device_name}")
                    # Try to find Quantum 2626
                    for name in available_inputs:
                        if 'Quantum' in name or '2626' in name:
                            self.input_port = mido.open_input(name)
                            self.logger.info(f"Connected to Quantum 2626: {name}")
                            break
            else:
                # Auto-detect: prefer Quantum 2626, otherwise use first available
                for name in available_inputs:
                    if 'Quantum' in name or '2626' in name:
                        self.input_port = mido.open_input(name)
                        self.logger.info(f"Auto-detected Quantum 2626: {name}")
                        break
                
                if not self.input_port and available_inputs:
                    self.input_port = mido.open_input(available_inputs[0])
                    self.logger.info(f"Using first available MIDI input: {available_inputs[0]}")
            
            if not self.input_port:
                self.logger.warning("No MIDI input device found - pedal control disabled")
                
        except Exception as e:
            self.logger.error(f"Failed to connect to MIDI device: {e}")
            self.input_port = None
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback for MIDI events
        
        Args:
            event_type: Type of event ('listen_start', 'listen_stop', 'mode_change', etc.)
            callback: Function to call when event occurs
        """
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
            self.logger.debug(f"Registered callback for {event_type}")
    
    async def listen(self):
        """Main async loop for processing MIDI messages"""
        if not self.input_port:
            self.logger.warning("No MIDI input available")
            return
        
        self.logger.info("Starting MIDI pedal listener")
        
        while True:
            try:
                # Non-blocking check for MIDI messages
                msg = self.input_port.poll()
                
                if msg:
                    await self._process_message(msg)
                
                # Small sleep to prevent CPU spinning
                await asyncio.sleep(0.001)  # 1ms
                
            except Exception as e:
                self.logger.error(f"Error processing MIDI message: {e}")
                await asyncio.sleep(0.01)
    
    async def _process_message(self, msg: mido.Message):
        """Process incoming MIDI message"""
        if msg.type == 'control_change':
            cc_num = msg.control
            value = msg.value
            
            if cc_num in self.cc_mappings:
                mapping = self.cc_mappings[cc_num]
                
                if mapping == 'sustain':
                    await self._handle_sustain(value)
                elif mapping == 'portamento':
                    await self._handle_mode_change(value)
                elif mapping == 'expression':
                    await self._handle_expression(value)
                elif mapping == 'tap_tempo':
                    await self._handle_tap_tempo(value)
                elif mapping in ['sostenuto', 'soft']:
                    # These can be used for additional controls
                    self.logger.debug(f"{mapping} pedal: {value}")
    
    async def _handle_sustain(self, value: int):
        """
        Handle sustain pedal (main listen trigger)
        
        Args:
            value: MIDI value (0-127, >63 is pressed)
        """
        pressed = value > 63
        
        if pressed and not self.listening:
            # Start listening
            self.listening = True
            self.logger.info("Started listening to guitar input")
            
            # Trigger callbacks
            for callback in self.callbacks['listen_start']:
                await self._call_async(callback, True)
                
        elif not pressed and self.listening:
            # Stop listening
            self.listening = False
            self.logger.info("Stopped listening to guitar input")
            
            # Trigger callbacks
            for callback in self.callbacks['listen_stop']:
                await self._call_async(callback, False)
    
    async def _handle_mode_change(self, value: int):
        """
        Handle mode change pedal
        
        Args:
            value: MIDI value (>63 triggers mode change)
        """
        if value > 63:  # Pedal pressed
            # Cycle to next mode
            self.mode_index = (self.mode_index + 1) % len(self.mode_cycle)
            self.mode = self.mode_cycle[self.mode_index]
            
            self.logger.info(f"Changed listening mode to: {self.mode.value}")
            
            # Trigger callbacks
            for callback in self.callbacks['mode_change']:
                await self._call_async(callback, self.mode)
    
    async def _handle_expression(self, value: int):
        """
        Handle expression pedal (continuous control)
        
        Args:
            value: MIDI value (0-127)
        """
        # Convert to 0-1 range
        normalized_value = value / 127.0
        
        # Trigger callbacks
        for callback in self.callbacks['expression']:
            await self._call_async(callback, normalized_value)
    
    async def _handle_tap_tempo(self, value: int):
        """
        Handle tap tempo pedal
        
        Args:
            value: MIDI value (>63 is a tap)
        """
        if value > 63:  # Pedal pressed
            import time
            current_time = time.time()
            
            # Add tap time
            self.tap_times.append(current_time)
            
            # Remove old taps
            self.tap_times = [
                t for t in self.tap_times 
                if current_time - t < self.tap_timeout
            ]
            
            # Calculate tempo if we have enough taps
            if len(self.tap_times) >= 2:
                intervals = [
                    self.tap_times[i] - self.tap_times[i-1] 
                    for i in range(1, len(self.tap_times))
                ]
                avg_interval = sum(intervals) / len(intervals)
                bpm = 60.0 / avg_interval
                
                self.logger.info(f"Tap tempo detected: {bpm:.1f} BPM")
                
                # Trigger callbacks
                for callback in self.callbacks['tap_tempo']:
                    await self._call_async(callback, bpm)
    
    async def _call_async(self, callback: Callable, *args):
        """Helper to call either sync or async callbacks"""
        if asyncio.iscoroutinefunction(callback):
            await callback(*args)
        else:
            callback(*args)
    
    def get_status(self) -> Dict:
        """Get current controller status"""
        return {
            'connected': self.input_port is not None,
            'device': self.device_name,
            'listening': self.listening,
            'mode': self.mode.value,
            'tap_count': len(self.tap_times)
        }
    
    def close(self):
        """Clean up MIDI connections"""
        if self.input_port:
            self.input_port.close()
            self.logger.info("MIDI controller closed")


class MidiLearnMode:
    """Helper class for MIDI learn functionality"""
    
    def __init__(self, controller: MidiPedalController):
        self.controller = controller
        self.learning = False
        self.learn_target = None
        self.learn_callback = None
    
    async def start_learn(self, target: str, callback: Callable):
        """
        Start MIDI learn mode
        
        Args:
            target: What to map ('listen', 'mode', 'expression', etc.)
            callback: Function to call when learned
        """
        self.learning = True
        self.learn_target = target
        self.learn_callback = callback
        
        # Temporarily capture all CCs
        self.original_mappings = self.controller.cc_mappings.copy()
        
    async def process_learn(self, cc_num: int):
        """Process CC during learn mode"""
        if self.learning and self.learn_target:
            # Map this CC to the target
            self.controller.cc_mappings[cc_num] = self.learn_target
            
            if self.learn_callback:
                self.learn_callback(cc_num, self.learn_target)
            
            self.learning = False
            self.learn_target = None
