"""
Simple Listener Agent for audio input processing
"""

import asyncio
import logging
from enum import Enum
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ListeningMode(Enum):
    CHORD_FOLLOW = "chord_follow"
    CALL_RESPONSE = "call_response"
    RHYTHMIC_SYNC = "rhythmic_sync"
    AMBIENT_LAYER = "ambient_layer"

class ListenerAgent:
    """Simple listener agent that processes audio input"""
    
    def __init__(self, agent_id="listener", memory=None):
        self.agent_id = agent_id
        self.memory = memory
        self.listening = False
        self.listening_mode = ListeningMode.CHORD_FOLLOW
        self.response_threshold = 0.1
        self.input_context = {
            'current_chord': None,
            'tempo_estimate': 120,
            'dynamics_history': [],
        }
        logger.info(f"✓ Created listener agent: {agent_id}")
    
    async def process_audio_input(self, analysis: Dict):
        """Process incoming audio analysis"""
        if not self.listening:
            return
        
        # Store in context
        if 'chord' in analysis:
            self.input_context['current_chord'] = analysis['chord']
        
        # Process based on mode
        if self.listening_mode == ListeningMode.CHORD_FOLLOW:
            await self._chord_follow_strategy(analysis)
        elif self.listening_mode == ListeningMode.CALL_RESPONSE:
            await self._call_response_strategy(analysis)
    
    async def _chord_follow_strategy(self, analysis: Dict):
        """Simple chord following"""
        chord = analysis.get('chord')
        if chord:
            logger.debug(f"Following chord: {chord}")
    
    async def _call_response_strategy(self, analysis: Dict):
        """Simple call and response"""
        if analysis.get('onset'):
            logger.debug("Detected onset, preparing response")
    
    async def on_listening_start(self):
        """Start listening"""
        self.listening = True
        logger.info("Started listening")
    
    async def on_listening_stop(self):
        """Stop listening"""
        self.listening = False
        logger.info("Stopped listening")
    
    def get_status(self) -> Dict:
        """Get current status"""
        return {
            'listening': self.listening,
            'mode': self.listening_mode.value,
            'current_chord': self.input_context.get('current_chord'),
            'tempo': self.input_context.get('tempo_estimate', 120)
        }