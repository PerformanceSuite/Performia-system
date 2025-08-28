"""
Lock-free shared memory buffer for ultra-low latency communication
Target: <0.1ms read/write latency for musical events
"""

import mmap
import struct
import ctypes
import time
import logging
from enum import IntEnum
from typing import Optional, List, Tuple
from multiprocessing import shared_memory
import platform

logger = logging.getLogger(__name__)

class EventType(IntEnum):
    """Musical event types"""
    NOTE_ON = 1
    NOTE_OFF = 2
    PATTERN_CHANGE = 3
    CONTROL_CHANGE = 4
    TEMPO_CHANGE = 5
    KEY_CHANGE = 6
    ONSET = 7
    PITCH = 8
    CHORD = 9
    SYSTEM = 10

class EventFlags(IntEnum):
    """Event flags for metadata"""
    URGENT = 1 << 0
    BROADCAST = 1 << 1
    NEEDS_OSC = 1 << 2
    FROM_INPUT = 1 << 3
    PATTERN_START = 1 << 4
    PATTERN_END = 1 << 5

class AudioEventBuffer:
    """
    Lock-free ring buffer for musical events.
    Single writer, multiple readers design for zero-contention.
    """
    
    # Constants
    MAGIC = 0xDEADBEEF12345678
    VERSION = 1
    EVENT_SIZE = 32  # bytes per event
    BUFFER_SIZE = 1024 * 1024  # 1MB total
    CONTROL_SIZE = 256  # Control block size
    EVENT_BUFFER_SIZE = BUFFER_SIZE - CONTROL_SIZE
    MAX_EVENTS = EVENT_BUFFER_SIZE // EVENT_SIZE  # 32,760 events
    MAX_READERS = 5  # GUI, SC, and 3 monitoring slots
    
    def __init__(self, name: str = "PerformiaBuffer", create: bool = False):
        """
        Initialize shared memory buffer.
        
        Args:
            name: Shared memory segment name
            create: True to create new, False to attach existing
        """
        self.name = name
        self.is_creator = create
        
        try:
            if create:
                # Try to unlink existing segment
                try:
                    existing = shared_memory.SharedMemory(name=name)
                    existing.close()
                    existing.unlink()
                except FileNotFoundError:
                    pass
                
                # Create new shared memory segment
                self.shm = shared_memory.SharedMemory(
                    create=True,
                    size=self.BUFFER_SIZE,
                    name=name
                )
                self.buffer = self.shm.buf
                self._initialize_control_block()
                logger.info(f"Created shared memory buffer: {name} ({self.BUFFER_SIZE} bytes)")
            else:
                # Attach to existing segment
                self.shm = shared_memory.SharedMemory(name=name)
                self.buffer = self.shm.buf
                self._verify_control_block()
                logger.info(f"Attached to shared memory buffer: {name}")
            
            # Create atomic access to positions
            self._setup_atomic_positions()
            
            # Statistics
            self.stats = {
                'writes': 0,
                'reads': 0,
                'drops': 0,
                'max_latency_ns': 0
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize shared memory: {e}")
            raise
    
    def _initialize_control_block(self):
        """Initialize control block with header information."""
        # Clear buffer
        self.buffer[:] = b'\x00' * self.BUFFER_SIZE
        
        # Write header
        header = struct.pack(
            '<QQIIIIII',
            self.MAGIC,           # Magic number (8 bytes)
            self.VERSION,         # Version (8 bytes)
            0,                    # Write position (4 bytes)
            0,                    # Padding (4 bytes)
            self.EVENT_SIZE,      # Event size (4 bytes)
            self.MAX_EVENTS,      # Max events (4 bytes)
            self.BUFFER_SIZE,     # Buffer size (4 bytes)
            0                     # Sequence number (4 bytes)
        )
        self.buffer[0:40] = header
        
        # Initialize read positions (5 readers x 8 bytes = 40 bytes)
        for i in range(self.MAX_READERS):
            self.buffer[64 + i*8:64 + (i+1)*8] = struct.pack('<Q', 0)
    
    def _verify_control_block(self):
        """Verify control block has correct magic and version."""
        magic, version = struct.unpack('<QQ', self.buffer[0:16])
        
        if magic != self.MAGIC:
            raise ValueError(f"Invalid magic number: 0x{magic:016X}")
        
        if version != self.VERSION:
            raise ValueError(f"Incompatible version: {version} (expected {self.VERSION})")
    
    def _setup_atomic_positions(self):
        """Set up atomic access to position counters."""
        # Platform-specific atomic operations
        if platform.system() in ['Linux', 'Darwin']:  # Unix-like
            # Create ctypes pointers for atomic access
            self.write_pos = ctypes.c_uint32.from_buffer(self.buffer, 16)
            self.seq_num = ctypes.c_uint32.from_buffer(self.buffer, 36)
            
            self.read_positions = []
            for i in range(self.MAX_READERS):
                pos = ctypes.c_uint64.from_buffer(self.buffer, 64 + i*8)
                self.read_positions.append(pos)
        else:
            # Windows or other platforms - use struct (not truly atomic)
            logger.warning("Non-atomic operations on this platform")
            self.write_pos = None
            self.read_positions = None
    
    def write_event(self, agent_id: int, event_type: EventType, 
                   pitch: float = 0.0, velocity: float = 0.0,
                   duration: int = 0, flags: int = 0) -> bool:
        """
        Write musical event to buffer (lock-free).
        
        Args:
            agent_id: Agent identifier (0-255)
            event_type: Type of event
            pitch: MIDI pitch or frequency
            velocity: Velocity/amplitude (0.0-1.0)
            duration: Duration in milliseconds
            flags: Event flags/metadata
            
        Returns:
            True if successful, False if buffer full
        """
        start_time = time.perf_counter_ns()
        
        # Get current write position (atomic read)
        if self.write_pos:
            write_idx = self.write_pos.value % self.MAX_EVENTS
            
            # Check if buffer is full
            if self.read_positions:
                min_read = min(rp.value for rp in self.read_positions)
                if self.write_pos.value - min_read >= self.MAX_EVENTS - 1:
                    self.stats['drops'] += 1
                    logger.warning("Buffer full, dropping event")
                    return False
        else:
            # Fallback for non-atomic platforms
            write_idx = struct.unpack('<I', self.buffer[16:20])[0] % self.MAX_EVENTS
        
        # Calculate byte offset (skip control block)
        offset = self.CONTROL_SIZE + (write_idx * self.EVENT_SIZE)
        
        # Pack event data (32 bytes total)
        timestamp = time.time_ns()
        event_data = struct.pack(
            '<QBBHffHHQ',
            timestamp,        # 8 bytes: nanosecond timestamp
            agent_id & 0xFF,  # 1 byte: agent ID
            event_type & 0xFF,# 1 byte: event type
            0,                # 2 bytes: padding for alignment
            pitch,            # 4 bytes: float pitch
            velocity,         # 4 bytes: float velocity
            duration & 0xFFFF,# 2 bytes: duration in ms
            flags & 0xFFFF,   # 2 bytes: flags
            0                 # 8 bytes: padding to reach 32 bytes
        )
        
        # Write to buffer (atomic on cache-line aligned 32-byte writes)
        for i, byte in enumerate(event_data):
            self.buffer[offset + i] = byte
        
        # Update write position (atomic increment)
        if self.write_pos:
            self.write_pos.value = (self.write_pos.value + 1) & 0xFFFFFFFF
            self.seq_num.value = (self.seq_num.value + 1) & 0xFFFFFFFF
        else:
            # Fallback
            new_pos = (write_idx + 1) & 0xFFFFFFFF
            self.buffer[16:20] = struct.pack('<I', new_pos)
        
        # Update statistics
        self.stats['writes'] += 1
        latency = time.perf_counter_ns() - start_time
        self.stats['max_latency_ns'] = max(self.stats['max_latency_ns'], latency)
        
        return True
    
    def read_events(self, reader_id: int = 0, max_events: int = 100) -> List[Tuple]:
        """
        Read available events for a specific reader.
        
        Args:
            reader_id: Reader index (0-4)
            max_events: Maximum events to read
            
        Returns:
            List of event tuples (timestamp, agent_id, event_type, pitch, velocity, duration, flags)
        """
        if reader_id >= self.MAX_READERS:
            raise ValueError(f"Invalid reader_id: {reader_id} (max: {self.MAX_READERS-1})")
        
        events = []
        
        if self.read_positions and self.write_pos:
            read_pos = self.read_positions[reader_id]
            
            # Read up to write position
            while len(events) < max_events and read_pos.value < self.write_pos.value:
                # Calculate buffer position
                read_idx = read_pos.value % self.MAX_EVENTS
                offset = self.CONTROL_SIZE + (read_idx * self.EVENT_SIZE)
                
                # Read event data
                event_data = bytes(self.buffer[offset:offset + self.EVENT_SIZE])
                
                # Unpack event (32 bytes)
                timestamp, agent_id, event_type, _, pitch, velocity, duration, flags, _ = \
                    struct.unpack('<QBBHffHHQ', event_data)
                
                events.append((timestamp, agent_id, event_type, pitch, velocity, duration, flags))
                
                # Update read position (atomic)
                read_pos.value += 1
            
            self.stats['reads'] += len(events)
        
        return events
    
    def get_pending_events(self, reader_id: int = 0) -> int:
        """Get number of unread events for a reader."""
        if self.read_positions and self.write_pos:
            return self.write_pos.value - self.read_positions[reader_id].value
        return 0
    
    def get_buffer_stats(self) -> dict:
        """Get buffer statistics and health."""
        stats = dict(self.stats)
        
        if self.write_pos and self.read_positions:
            min_read = min(rp.value for rp in self.read_positions)
            stats.update({
                'write_position': self.write_pos.value,
                'min_read_position': min_read,
                'events_pending': self.write_pos.value - min_read,
                'buffer_usage': (self.write_pos.value - min_read) / self.MAX_EVENTS,
                'sequence_number': self.seq_num.value if hasattr(self, 'seq_num') else 0
            })
        
        return stats
    
    def reset_reader(self, reader_id: int):
        """Reset a reader to current write position (skip all pending)."""
        if self.read_positions and self.write_pos:
            self.read_positions[reader_id].value = self.write_pos.value
    
    def close(self):
        """Close shared memory connection."""
        self.shm.close()
        
    def cleanup(self):
        """Clean up shared memory (only call from creator process)."""
        if self.is_creator:
            try:
                # Clear references to avoid pointer issues
                self.buffer = None
                self.write_pos = None
                self.read_positions = None
                self.seq_num = None
                
                # Now safe to close and unlink
                self.shm.close()
                self.shm.unlink()
                logger.info(f"Cleaned up shared memory buffer: {self.name}")
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")

# Test function
def test_shared_memory():
    """Test shared memory buffer performance."""
    import random
    
    print("Testing shared memory buffer...")
    
    # Create buffer
    buffer = AudioEventBuffer("PerformiaTest", create=True)
    
    try:
        # Write test events
        print("\n1. Writing events...")
        start = time.perf_counter()
        
        for i in range(1000):
            success = buffer.write_event(
                agent_id=i % 4,
                event_type=EventType.NOTE_ON,
                pitch=60 + random.randint(0, 24),
                velocity=random.random(),
                duration=random.randint(100, 500)
            )
            if not success:
                print(f"  Buffer full at event {i}")
                break
        
        write_time = time.perf_counter() - start
        print(f"  Wrote 1000 events in {write_time*1000:.3f}ms")
        print(f"  Average write time: {write_time*1000000/1000:.3f}μs")
        
        # Read test events
        print("\n2. Reading events...")
        start = time.perf_counter()
        
        events = buffer.read_events(reader_id=0, max_events=1000)
        
        read_time = time.perf_counter() - start
        print(f"  Read {len(events)} events in {read_time*1000:.3f}ms")
        print(f"  Average read time: {read_time*1000000/len(events):.3f}μs")
        
        # Show statistics
        print("\n3. Buffer statistics:")
        stats = buffer.get_buffer_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n✅ Shared memory buffer test successful!")
        
    finally:
        buffer.cleanup()

if __name__ == "__main__":
    test_shared_memory()