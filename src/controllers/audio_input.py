"""Audio input controller for Presonus Quantum 2626"""

import sounddevice as sd
import numpy as np
import asyncio
from typing import Callable, Optional, List, Dict
import logging
from ..analysis import RealtimeAudioAnalyzer, ChordDetector, OptimizedRingBuffer


class AudioInputController:
    """
    Manages audio input from Presonus Quantum 2626
    Handles real-time analysis and routing to agents
    """
    
    def __init__(self, device_name: str = "Quantum 2626", 
                 sample_rate: int = 48000,
                 block_size: int = 64,
                 channels: int = 2):
        """
        Initialize audio input controller
        
        Args:
            device_name: Audio device name
            sample_rate: Sample rate (48000 for Quantum)
            block_size: Buffer size (64 for low latency)
            channels: Number of input channels
        """
        self.logger = logging.getLogger(__name__)
        self.device_name = device_name
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.channels = channels
        
        # Analysis components
        self.analyzer = RealtimeAudioAnalyzer(sample_rate=sample_rate, hop_length=256)
        self.chord_detector = ChordDetector()
        self.input_buffer = OptimizedRingBuffer(size=4096, channels=channels)
        
        # State
        self.is_listening = False
        self.stream = None
        
        # Callbacks
        self.analysis_callbacks: List[Callable] = []
        
        # Analysis results cache
        self.latest_analysis = {
            'pitch': None,
            'chord': None,
            'dynamics': 0.0,
            'onset': False,
            'timestamp': 0
        }
        
        # Performance metrics
        self.latency_buffer = []
        self.latency_window = 100  # Keep last 100 measurements
        
        # Find and configure device
        self._configure_device()
    
    def _configure_device(self):
        """Find and configure the Quantum 2626"""
        try:
            # List all audio devices
            devices = sd.query_devices()
            
            # Find Quantum 2626
            quantum_idx = None
            for idx, device in enumerate(devices):
                if self.device_name in device['name'] or 'Quantum' in device['name']:
                    if device['max_input_channels'] > 0:
                        quantum_idx = idx
                        self.logger.info(f"Found Quantum 2626 at index {idx}: {device['name']}")
                        break
            
            if quantum_idx is not None:
                # Set as default input
                sd.default.device[0] = quantum_idx
                sd.default.samplerate = self.sample_rate
                sd.default.blocksize = self.block_size
                sd.default.channels = self.channels
                
                # Get device info
                device_info = sd.query_devices(quantum_idx)
                self.logger.info(f"Configured Quantum 2626: {device_info}")
                
                # Check latency
                latency = sd.default.latency[0]
                self.logger.info(f"Input latency: {latency * 1000:.2f}ms")
            else:
                self.logger.warning("Quantum 2626 not found, using default input device")
                
        except Exception as e:
            self.logger.error(f"Error configuring audio device: {e}")
    
    def register_analysis_callback(self, callback: Callable):
        """Register callback for analysis results"""
        self.analysis_callbacks.append(callback)
    
    async def start_listening(self):
        """Start listening to audio input"""
        if self.is_listening:
            return
        
        try:
            # Audio callback function
            def audio_callback(indata, frames, time, status):
                if status:
                    self.logger.warning(f"Audio input status: {status}")
                
                # Write to ring buffer (non-blocking)
                if not self.input_buffer.write(indata.T):  # Transpose for channels x samples
                    self.logger.warning("Input buffer overflow")
                
                # Trigger async analysis
                asyncio.create_task(self._analyze_audio(indata))
            
            # Start audio stream
            self.stream = sd.InputStream(
                callback=audio_callback,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                dtype='float32'
            )
            
            self.stream.start()
            self.is_listening = True
            self.logger.info("Started audio input listening")
            
        except Exception as e:
            self.logger.error(f"Failed to start audio input: {e}")
            self.is_listening = False
    
    async def stop_listening(self):
        """Stop listening to audio input"""
        if not self.is_listening:
            return
        
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            self.is_listening = False
            self.input_buffer.clear()
            self.logger.info("Stopped audio input listening")
            
        except Exception as e:
            self.logger.error(f"Error stopping audio input: {e}")
    
    async def _analyze_audio(self, audio_data: np.ndarray):
        """
        Analyze audio frame asynchronously
        
        Args:
            audio_data: Input audio frame
        """
        try:
            # Use first channel for analysis if stereo
            if audio_data.shape[1] > 1:
                mono_data = np.mean(audio_data, axis=1)
            else:
                mono_data = audio_data[:, 0]
            
            # Run analysis
            analysis = await self.analyzer.analyze_frame(mono_data)
            
            # Enhanced chord detection if we have pitch
            if analysis['pitch'] and analysis['confidence'] > 0.7:
                # Get chromagram for chord detection
                chroma = self.analyzer._fast_chroma(mono_data)
                chord, confidence = self.chord_detector.detect(chroma)
                
                if confidence > 0.6:
                    analysis['chord'] = chord
                    analysis['chord_confidence'] = confidence
                    
                    # Get chord tones for agents
                    analysis['chord_tones'] = self.chord_detector.get_chord_tones(chord)
            
            # Update latest analysis
            import time
            analysis['timestamp'] = time.time()
            self.latest_analysis = analysis
            
            # Track latency
            if 'latency_ms' in analysis:
                self.latency_buffer.append(analysis['latency_ms'])
                if len(self.latency_buffer) > self.latency_window:
                    self.latency_buffer.pop(0)
            
            # Trigger callbacks
            for callback in self.analysis_callbacks:
                if asyncio.iscoroutinefunction(callback):
                    await callback(analysis)
                else:
                    # Run sync callbacks in executor to not block
                    await asyncio.get_event_loop().run_in_executor(
                        None, callback, analysis
                    )
            
        except Exception as e:
            self.logger.error(f"Error in audio analysis: {e}")
    
    def get_input_level(self) -> float:
        """Get current input level (0-1)"""
        return self.latest_analysis.get('dynamics', 0.0)
    
    def get_detected_chord(self) -> Optional[str]:
        """Get currently detected chord"""
        return self.latest_analysis.get('chord')
    
    def get_detected_pitch(self) -> Optional[float]:
        """Get currently detected pitch in Hz"""
        return self.latest_analysis.get('pitch')
    
    def get_latency_stats(self) -> Dict:
        """Get latency statistics"""
        if not self.latency_buffer:
            return {'mean': 0, 'min': 0, 'max': 0, 'current': 0}
        
        return {
            'mean': np.mean(self.latency_buffer),
            'min': np.min(self.latency_buffer),
            'max': np.max(self.latency_buffer),
            'current': self.latency_buffer[-1] if self.latency_buffer else 0
        }
    
    def get_buffer_samples(self, n_samples: int) -> Optional[np.ndarray]:
        """
        Get samples from input buffer for processing
        
        Args:
            n_samples: Number of samples to retrieve
            
        Returns:
            Audio samples or None if not available
        """
        return self.input_buffer.read(n_samples)
    
    def get_analysis_window(self) -> np.ndarray:
        """Get current analysis window for visualization"""
        return self.input_buffer.get_window(1024)
    
    async def calibrate_input(self, duration: float = 2.0) -> Dict:
        """
        Calibrate input levels and noise floor
        
        Args:
            duration: Calibration duration in seconds
            
        Returns:
            Calibration results
        """
        self.logger.info(f"Starting input calibration for {duration} seconds...")
        
        levels = []
        start_time = asyncio.get_event_loop().time()
        
        # Temporary listening
        await self.start_listening()
        
        while asyncio.get_event_loop().time() - start_time < duration:
            levels.append(self.get_input_level())
            await asyncio.sleep(0.1)
        
        await self.stop_listening()
        
        if levels:
            noise_floor = np.percentile(levels, 10)
            peak_level = np.max(levels)
            avg_level = np.mean(levels)
            
            results = {
                'noise_floor': noise_floor,
                'peak_level': peak_level,
                'average_level': avg_level,
                'recommended_threshold': noise_floor * 2
            }
            
            self.logger.info(f"Calibration complete: {results}")
            return results
        
        return {'error': 'No input detected during calibration'}
