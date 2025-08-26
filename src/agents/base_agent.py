"""
Base Musical Agent class with personality and memory capabilities
"""

import asyncio
import numpy as np
import time
from collections import deque
from typing import Dict, List, Optional, Any
import logging

from autogen import ConversableAgent

logger = logging.getLogger(__name__)

class BaseMusicalAgent(ConversableAgent):
    """Base class for musical agents with personality and memory"""
    
    def __init__(
        self,
        name: str,
        role: str,
        personality,
        shared_context,
        event_buffer,
        sc_engine
    ):
        super().__init__(
            name=name,
            system_message=f"I am a {role} agent in a musical ensemble."
        )
        
        self.role = role
        self.personality = personality
        self.shared_context = shared_context
        self.event_buffer = event_buffer
        self.sc_engine = sc_engine
        
        # Agent-specific memory
        self.short_term_memory = deque(maxlen=32)
        self.current_pattern = []
        self.last_note_time = 0
        
        # Performance state
        self.active_notes = {}
        self.agent_id = f"{name}_{id(self)}"
        
        # Musical state
        self.current_scale = self.determine_scale()
        self.rhythm_pattern = self.generate_rhythm_pattern()
        
        logger.info(f"✓ Created {role} agent: {name}")
    
    def determine_scale(self) -> List[int]:
        """Determine scale based on current key and mode"""
        key = self.shared_context.key_signature.value
        mode = self.shared_context.mode.value
        
        # Scale patterns
        scales = {
            0: [0, 2, 4, 5, 7, 9, 11],  # Major
            1: [0, 2, 3, 5, 7, 8, 10],  # Natural Minor
            2: [0, 2, 3, 5, 7, 9, 10],  # Dorian
            3: [0, 1, 3, 5, 7, 8, 10],  # Phrygian
            4: [0, 2, 4, 6, 7, 9, 11],  # Lydian
            5: [0, 2, 4, 5, 7, 9, 10],  # Mixolydian
        }
        
        intervals = scales.get(mode, scales[0])
        return [(key + i) % 12 for i in intervals]
    
    def generate_rhythm_pattern(self) -> List[int]:
        """Generate rhythm pattern based on personality"""
        pattern = []
        density = self.personality.aggression * 0.5 + 0.3
        
        for i in range(16):
            if self.personality.preferred_rhythm == "syncopated":
                if i % 3 == 0 or (i + 1) % 4 == 0:
                    pattern.append(1 if np.random.random() < density else 0)
                else:
                    pattern.append(0)
            else:
                if i % 4 == 0:
                    pattern.append(1)
                elif i % 2 == 0 and np.random.random() < density:
                    pattern.append(1)
                else:
                    pattern.append(0)
        
        return pattern
    
    async def listen_and_respond(self):
        """Main loop: listen to other agents and respond musically"""
        while True:
            # Check for new events from other agents
            event = self.event_buffer.read(self.agent_id)
            
            if event and event['agent_id'] != self.agent_id:
                # Process musical event from another agent
                await self.process_musical_event(event)
            
            # Generate own musical contribution based on context
            current_time = time.perf_counter()
            if current_time - self.last_note_time > self.get_next_note_timing():
                await self.generate_and_play()
                self.last_note_time = current_time
            
            # Ultra-short sleep to prevent CPU spinning
            await asyncio.sleep(0.001)
    
    async def process_musical_event(self, event: dict):
        """Process and respond to another agent's musical event"""
        self.short_term_memory.append(event)
        
        # Analyze musical content
        if 'note' in event:
            note = event['note']
            
            # Check if we should respond
            if np.random.random() < self.personality.responsiveness:
                if self.personality.call_response and event.get('is_call'):
                    await self.generate_response(note)
    
    async def generate_and_play(self):
        """Generate and play musical content - to be implemented by subclasses"""
        pass
    
    async def generate_response(self, note):
        """Generate a response to another agent's note"""
        pass
    
    def get_next_note_timing(self) -> float:
        """Determine when to play next note"""
        tempo = self.shared_context.tempo.value
        beat_duration = 60.0 / tempo
        
        if self.personality.stability > 0.8:
            return beat_duration / 4
        else:
            base_time = beat_duration / 4
            variation = (1 - self.personality.stability) * 0.02
            return base_time + np.random.uniform(-variation, variation)
    
    def midi_to_freq(self, midi_note: int) -> float:
        """Convert MIDI note to frequency"""
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
