"""Optimized ring buffer for ultra-low latency audio buffering"""

import numpy as np
from typing import Optional
import threading


class OptimizedRingBuffer:
    """
    Lock-free ring buffer optimized for real-time audio
    Uses numpy for efficient memory operations
    """
    
    def __init__(self, size: int = 4096, channels: int = 2):
        """
        Initialize ring buffer
        
        Args:
            size: Buffer size in samples
            channels: Number of audio channels
        """
        self.size = size
        self.channels = channels
        
        # Pre-allocate buffer
        self.buffer = np.zeros((channels, size), dtype=np.float32)
        
        # Atomic indices (no locks needed for single producer/consumer)
        self.write_idx = 0
        self.read_idx = 0
        
        # For thread safety if needed
        self.lock = threading.RLock()
        
    def write(self, data: np.ndarray) -> bool:
        """
        Write data to buffer (non-blocking)
        
        Args:
            data: Audio data to write (channels x samples)
            
        Returns:
            True if successful, False if buffer full
        """
        if data.ndim == 1:
            data = data.reshape(1, -1)
            
        n_samples = data.shape[1]
        
        # Check available space (lock-free read)
        available = (self.read_idx - self.write_idx - 1) % self.size
        if available < n_samples:
            return False  # Buffer full
        
        # Write data (may wrap around)
        if self.write_idx + n_samples <= self.size:
            # Simple case: no wrap
            self.buffer[:, self.write_idx:self.write_idx + n_samples] = data
        else:
            # Wrap around
            split = self.size - self.write_idx
            self.buffer[:, self.write_idx:] = data[:, :split]
            self.buffer[:, :n_samples - split] = data[:, split:]
        
        # Update write index (atomic operation)
        self.write_idx = (self.write_idx + n_samples) % self.size
        
        return True
    
    def read(self, n_samples: int) -> Optional[np.ndarray]:
        """
        Read data from buffer (non-blocking)
        
        Args:
            n_samples: Number of samples to read
            
        Returns:
            Audio data or None if not enough samples available
        """
        # Check available samples (lock-free)
        available = (self.write_idx - self.read_idx) % self.size
        if available < n_samples:
            return None
        
        # Allocate output
        output = np.zeros((self.channels, n_samples), dtype=np.float32)
        
        # Read data (may wrap around)
        if self.read_idx + n_samples <= self.size:
            # Simple case: no wrap
            output[:] = self.buffer[:, self.read_idx:self.read_idx + n_samples]
        else:
            # Wrap around
            split = self.size - self.read_idx
            output[:, :split] = self.buffer[:, self.read_idx:]
            output[:, split:] = self.buffer[:, :n_samples - split]
        
        # Update read index (atomic operation)
        self.read_idx = (self.read_idx + n_samples) % self.size
        
        return output
    
    def peek(self, n_samples: int, offset: int = 0) -> Optional[np.ndarray]:
        """
        Read data without advancing read pointer
        
        Args:
            n_samples: Number of samples to peek
            offset: Offset from current read position
            
        Returns:
            Audio data or None if not enough samples available
        """
        # Check available samples
        available = (self.write_idx - self.read_idx) % self.size
        if available < n_samples + offset:
            return None
        
        # Calculate peek position
        peek_idx = (self.read_idx + offset) % self.size
        
        # Allocate output
        output = np.zeros((self.channels, n_samples), dtype=np.float32)
        
        # Read data without updating index
        if peek_idx + n_samples <= self.size:
            output[:] = self.buffer[:, peek_idx:peek_idx + n_samples]
        else:
            split = self.size - peek_idx
            output[:, :split] = self.buffer[:, peek_idx:]
            output[:, split:] = self.buffer[:, :n_samples - split]
        
        return output
    
    def get_window(self, size: int) -> np.ndarray:
        """
        Get the last 'size' samples for analysis
        
        Args:
            size: Window size in samples
            
        Returns:
            Audio window (channels x samples)
        """
        # Get write position snapshot
        write_pos = self.write_idx
        
        # Calculate start position for window
        if write_pos >= size:
            start_pos = write_pos - size
            return self.buffer[:, start_pos:write_pos].copy()
        else:
            # Wrap around case
            return np.concatenate([
                self.buffer[:, write_pos - size:],
                self.buffer[:, :write_pos]
            ], axis=1)
    
    def clear(self):
        """Clear the buffer"""
        self.buffer.fill(0)
        self.write_idx = 0
        self.read_idx = 0
    
    @property
    def available_samples(self) -> int:
        """Get number of samples available to read"""
        return (self.write_idx - self.read_idx) % self.size
    
    @property
    def free_samples(self) -> int:
        """Get number of samples available to write"""
        return (self.read_idx - self.write_idx - 1) % self.size
    
    @property
    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        return self.write_idx == self.read_idx
    
    @property
    def is_full(self) -> bool:
        """Check if buffer is full"""
        return self.free_samples == 0


class MultiChannelBuffer:
    """
    Manages multiple ring buffers for different audio streams
    (e.g., input, output, processed)
    """
    
    def __init__(self, n_buffers: int = 3, size: int = 4096, channels: int = 2):
        """
        Initialize multi-channel buffer system
        
        Args:
            n_buffers: Number of separate buffers
            size: Size of each buffer
            channels: Audio channels per buffer
        """
        self.buffers = [
            OptimizedRingBuffer(size, channels) 
            for _ in range(n_buffers)
        ]
        self.n_buffers = n_buffers
    
    def write_to(self, buffer_idx: int, data: np.ndarray) -> bool:
        """Write to specific buffer"""
        if 0 <= buffer_idx < self.n_buffers:
            return self.buffers[buffer_idx].write(data)
        return False
    
    def read_from(self, buffer_idx: int, n_samples: int) -> Optional[np.ndarray]:
        """Read from specific buffer"""
        if 0 <= buffer_idx < self.n_buffers:
            return self.buffers[buffer_idx].read(n_samples)
        return None
    
    def transfer(self, from_idx: int, to_idx: int, n_samples: int) -> bool:
        """
        Transfer data between buffers
        
        Args:
            from_idx: Source buffer index
            to_idx: Destination buffer index
            n_samples: Number of samples to transfer
            
        Returns:
            True if successful
        """
        data = self.read_from(from_idx, n_samples)
        if data is not None:
            return self.write_to(to_idx, data)
        return False
    
    def clear_all(self):
        """Clear all buffers"""
        for buffer in self.buffers:
            buffer.clear()
