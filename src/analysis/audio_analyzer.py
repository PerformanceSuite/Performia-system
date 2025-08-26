"""Real-time audio analyzer for guitar input processing"""

import numpy as np
from scipy import signal
import librosa
import asyncio
from typing import Dict, Optional, Tuple
import time


class RealtimeAudioAnalyzer:
    """Ultra-low latency audio analysis for live input"""
    
    def __init__(self, sample_rate: int = 48000, hop_length: int = 256):
        """
        Initialize the analyzer with optimized parameters for low latency
        
        Args:
            sample_rate: Audio sample rate (48000 for Quantum 2626)
            hop_length: Hop size for analysis (256 = ~5.3ms @ 48kHz)
        """
        self.sr = sample_rate
        self.hop_length = hop_length  # ~5.3ms at 48kHz for ultra-low latency
        self.buffer_size = 1024  # ~21ms window - minimum for reliable pitch
        self.ring_buffer = np.zeros(self.buffer_size)
        self.write_pos = 0
        
        # Pre-compute chromagram basis for speed
        self.chroma_basis = librosa.filters.chroma(sr=sample_rate, n_fft=1024)
        
        # Onset detection parameters
        self.onset_threshold = 0.3
        self.prev_onset_strength = 0.0
        
        # Pre-allocate arrays for performance
        self.fft_window = np.hanning(self.buffer_size)
        self.magnitude_spectrum = np.zeros(self.buffer_size // 2 + 1)
        
    async def analyze_frame(self, audio_frame: np.ndarray) -> Dict:
        """
        Analyze a frame of audio with minimal latency
        
        Args:
            audio_frame: Audio samples to analyze
            
        Returns:
            Dictionary with analysis results
        """
        start_time = time.perf_counter()
        
        # Update ring buffer
        frame_len = len(audio_frame)
        if self.write_pos + frame_len <= self.buffer_size:
            self.ring_buffer[self.write_pos:self.write_pos + frame_len] = audio_frame
        else:
            split = self.buffer_size - self.write_pos
            self.ring_buffer[self.write_pos:] = audio_frame[:split]
            self.ring_buffer[:frame_len - split] = audio_frame[split:]
        self.write_pos = (self.write_pos + frame_len) % self.buffer_size
        
        # Get analysis window
        if self.write_pos >= self.buffer_size:
            window = self.ring_buffer[self.write_pos - self.buffer_size:self.write_pos]
        else:
            window = np.concatenate([
                self.ring_buffer[self.write_pos - self.buffer_size:],
                self.ring_buffer[:self.write_pos]
            ])
        
        # Fast pitch detection using autocorrelation
        pitch, confidence = self._fast_pitch_detect(window)
        
        # Compute chromagram for chord detection (only if confident pitch)
        chord = None
        if confidence > 0.8:
            chroma = self._fast_chroma(window)
            chord = self._detect_chord_from_chroma(chroma)
        
        # Onset detection
        onset = self._detect_onset(audio_frame)
        
        # Calculate dynamics (RMS)
        dynamics = np.sqrt(np.mean(audio_frame ** 2))
        
        analysis_time = (time.perf_counter() - start_time) * 1000  # ms
        
        return {
            'pitch': pitch,
            'confidence': confidence,
            'chord': chord,
            'dynamics': dynamics,
            'onset': onset,
            'latency_ms': analysis_time
        }
    
    def _fast_pitch_detect(self, window: np.ndarray) -> Tuple[Optional[float], float]:
        """
        Fast pitch detection using autocorrelation method
        
        Returns:
            Tuple of (pitch in Hz, confidence 0-1)
        """
        # Apply window to reduce spectral leakage
        windowed = window * self.fft_window
        
        # Autocorrelation using FFT for speed
        fft = np.fft.rfft(windowed, n=2048)
        autocorr = np.fft.irfft(np.abs(fft) ** 2)
        
        # Find peaks in autocorrelation
        min_period = int(self.sr / 1000)  # 1000 Hz max
        max_period = int(self.sr / 60)    # 60 Hz min
        
        autocorr_slice = autocorr[min_period:max_period]
        if len(autocorr_slice) == 0:
            return None, 0.0
            
        # Find maximum
        max_idx = np.argmax(autocorr_slice)
        lag = max_idx + min_period
        
        # Calculate confidence (ratio of peak to mean)
        confidence = autocorr[lag] / np.mean(np.abs(autocorr))
        confidence = np.clip(confidence, 0, 1)
        
        if confidence > 0.5:
            pitch = self.sr / lag
            return pitch, confidence
        
        return None, 0.0
    
    def _fast_chroma(self, window: np.ndarray) -> np.ndarray:
        """
        Fast chromagram computation using pre-computed basis
        """
        # FFT
        spectrum = np.abs(np.fft.rfft(window * self.fft_window, n=1024))
        
        # Apply chroma basis
        chroma = np.dot(self.chroma_basis, spectrum[:self.chroma_basis.shape[1]])
        
        # Normalize
        chroma_norm = np.linalg.norm(chroma)
        if chroma_norm > 0:
            chroma /= chroma_norm
            
        return chroma
    
    def _detect_chord_from_chroma(self, chroma: np.ndarray) -> Optional[str]:
        """
        Simple chord detection using template matching
        """
        # Basic chord templates (can be expanded)
        chord_templates = {
            'C': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
            'Dm': [0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
            'Em': [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
            'F': [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
            'G': [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            'Am': [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
            'Bdim': [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        }
        
        best_match = None
        best_score = -1
        
        for chord_name, template in chord_templates.items():
            # Rotate chroma for all possible roots
            for shift in range(12):
                rotated_chroma = np.roll(chroma, shift)
                score = np.dot(rotated_chroma, template)
                
                if score > best_score:
                    best_score = score
                    if shift == 0:
                        best_match = chord_name
                    else:
                        # Transpose chord name
                        root_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 
                                     'F#', 'G', 'G#', 'A', 'A#', 'B']
                        root_idx = root_names.index(chord_name[0])
                        new_root = root_names[(root_idx + shift) % 12]
                        if 'm' in chord_name:
                            best_match = new_root + 'm'
                        elif 'dim' in chord_name:
                            best_match = new_root + 'dim'
                        else:
                            best_match = new_root
        
        return best_match if best_score > 0.7 else None
    
    def _detect_onset(self, frame: np.ndarray) -> bool:
        """
        Detect note onsets using spectral flux
        """
        # Compute spectral flux
        spectrum = np.abs(np.fft.rfft(frame * np.hanning(len(frame))))
        flux = np.sum(np.maximum(0, spectrum - self.magnitude_spectrum))
        self.magnitude_spectrum = spectrum
        
        # Apply threshold
        onset = flux > self.onset_threshold and flux > self.prev_onset_strength * 1.5
        self.prev_onset_strength = flux
        
        return onset
