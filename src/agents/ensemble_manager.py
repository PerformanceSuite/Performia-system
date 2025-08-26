"""
Ensemble Manager for coordinating multiple musical agents
"""

import asyncio
import logging
from typing import List
from dataclasses import dataclass

from src.agents.base_agent import BaseMusicalAgent
from src.memory.shared_memory import SharedMusicalContext, LockFreeRingBuffer
from src.engine.supercollider import SuperColliderEngine
from src.personality.personality import MusicalPersonality

logger = logging.getLogger(__name__)

class MusicalEnsembleManager:
    """Manages the multi-agent musical ensemble"""
    
    def __init__(self, num_agents: int = 4, config: dict = None):
        self.config = config or {}
        
        # Shared infrastructure
        self.shared_context = SharedMusicalContext()
        self.event_buffer = LockFreeRingBuffer(
            size=config.get('memory', {}).get('buffer_size', 1024)
        )
        self.sc_engine = SuperColliderEngine(
            server_options=config.get('audio', {})
        )
        
        # Create agents with different personalities
        self.agents = self.create_ensemble(num_agents)
        
        # Set initial musical context from config
        perf_config = config.get('performance', {})
        self.shared_context.tempo.value = perf_config.get('tempo', 120.0)
        self.shared_context.key_signature.value = perf_config.get('key', 0)
        self.shared_context.mode.value = perf_config.get('mode', 0)
        
        logger.info(f"✓ Ensemble Manager initialized with {num_agents} agents")
    
    def create_ensemble(self, num_agents: int) -> List[BaseMusicalAgent]:
        """Create ensemble with varied personalities"""
        agents = []
        roles = self.config.get('agents', {}).get('roles', 
                                ['drums', 'bass', 'melody', 'harmony'])
        
        # Load personality presets
        from src.personality.personality import load_personalities
        personalities = load_personalities()
        
        # Default personality mapping
        role_personalities = {
            'drums': personalities.get('jazz_drummer'),
            'bass': personalities.get('rock_bassist'),
            'melody': personalities.get('ambient_melodist'),
            'harmony': personalities.get('classical_harmonist')
        }
        
        for i in range(num_agents):
            role = roles[i % len(roles)]
            personality = role_personalities.get(role)
            
            if not personality:
                personality = MusicalPersonality()
            
            agent = BaseMusicalAgent(
                name=f"{role}_agent_{i}",
                role=role,
                personality=personality,
                shared_context=self.shared_context,
                event_buffer=self.event_buffer,
                sc_engine=self.sc_engine
            )
            agents.append(agent)
        
        return agents
    
    async def start_performance(self):
        """Start the musical performance"""
        logger.info("🎵 Starting Musical Performance")
        
        # Start tempo keeper
        asyncio.create_task(self.keep_tempo())
        
        # Start all agents
        tasks = []
        for agent in self.agents:
            task = asyncio.create_task(agent.listen_and_respond())
            tasks.append(task)
        
        # Run forever
        await asyncio.gather(*tasks)
    
    async def keep_tempo(self):
        """Maintain global tempo and beat counter"""
        beat_duration = 60.0 / self.shared_context.tempo.value
        
        while True:
            current_beat = self.shared_context.current_beat.value
            self.shared_context.current_beat.value = (current_beat + 0.25) % 4
            
            if current_beat == 0:
                self.shared_context.bar_number.value += 1
            
            await asyncio.sleep(beat_duration / 4)
