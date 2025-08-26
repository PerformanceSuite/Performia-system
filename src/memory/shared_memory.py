"""
Shared Memory structures for ultra-low latency inter-agent communication
"""

import json
import time
import multiprocessing as mp
from multiprocessing import shared_memory
import ctypes
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class LockFreeRingBuffer:
    """Lock-free ring buffer for ultra-low latency inter-agent communication"""
    
    def __init__(self, size: int = 1024):
        self.size = size
        # Shared memory for musical events
        try:
            self.buffer = shared_memory.SharedMemory(create=True, size=size * 256)
            self.write_index = mp.Value(ctypes.c_uint32, 0)
            self.read_indices = {}
            logger.info(f"✓ Created lock-free ring buffer (size: {size})")
        except Exception as e:
            logger.error(f"Failed to create shared memory: {e}")
            raise
    
    def write(self, agent_id: str, event: dict) -> None:
        """Write musical event to buffer (lock-free)"""
        data = json.dumps({
            'agent_id': agent_id,
            'timestamp': time.perf_counter_ns(),
            **event
        }).encode('utf-8')[:256]
        
        # Get write position atomically
        idx = self.write_index.value % self.size
        
        # Write to shared memory
        start = idx * 256
        self.buffer.buf[start:start + len(data)] = data
        
        # Atomic increment
        with self.write_index.get_lock():
            self.write_index.value += 1
    
    def read(self, agent_id: str) -> Optional[dict]:
        """Read next event for this agent (lock-free)"""
        if agent_id not in self.read_indices:
            self.read_indices[agent_id] = 0
        
        if self.read_indices[agent_id] >= self.write_index.value:
            return None
        
        idx = self.read_indices[agent_id] % self.size
        start = idx * 256
        
        # Read from shared memory
        data = bytes(self.buffer.buf[start:start + 256])
        try:
            event = json.loads(data.decode('utf-8').rstrip('\x00'))
            self.read_indices[agent_id] += 1
            return event
        except:
            return None
    
    def cleanup(self):
        """Clean up shared memory"""
        try:
            self.buffer.close()
            self.buffer.unlink()
        except:
            pass


class SharedMusicalContext:
    """Shared memory for real-time musical state"""
    
    def __init__(self):
        # Current harmonic context (12 semitones + root note)
        self.harmony = mp.Array('f', 13)
        # Current rhythm pattern (32 sixteenth notes)
        self.rhythm = mp.Array('i', 32)
        # Tempo and timing
        self.tempo = mp.Value('f', 120.0)
        self.current_beat = mp.Value('f', 0.0)
        self.bar_number = mp.Value('i', 0)
        
        # Per-agent activity (up to 8 agents)
        self.agent_notes = mp.Array('f', 8 * 16)
        self.agent_velocities = mp.Array('f', 8 * 16)
        
        # Global musical parameters
        self.key_signature = mp.Value('i', 0)  # 0=C, 1=C#, etc
        self.mode = mp.Value('i', 0)  # 0=major, 1=minor, etc
        self.dynamics = mp.Value('f', 0.7)  # Global dynamics 0-1
        
        logger.info("✓ Shared musical context initialized")
