"""Advanced chord detection with jazz chord support"""

import numpy as np
from typing import List, Dict, Optional, Tuple


class ChordDetector:
    """Enhanced chord detection including extended and jazz chords"""
    
    def __init__(self):
        # Extended chord templates including 7ths, 9ths, etc.
        self.templates = self._build_chord_templates()
        self.chord_history = []
        self.history_size = 4  # Keep last 4 detected chords for smoothing
        
    def _build_chord_templates(self) -> Dict[str, np.ndarray]:
        """Build comprehensive chord templates"""
        templates = {}
        
        # Major chords
        templates['maj'] = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])
        templates['maj7'] = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1])
        templates['maj9'] = np.array([1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1])
        templates['6'] = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0])
        templates['add9'] = np.array([1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0])
        
        # Minor chords
        templates['m'] = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])
        templates['m7'] = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0])
        templates['m9'] = np.array([1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0])
        templates['m6'] = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0])
        
        # Dominant chords
        templates['7'] = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0])
        templates['9'] = np.array([1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0])
        templates['13'] = np.array([1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0])
        
        # Suspended chords
        templates['sus2'] = np.array([1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0])
        templates['sus4'] = np.array([1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0])
        templates['7sus4'] = np.array([1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0])
        
        # Diminished and augmented
        templates['dim'] = np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0])
        templates['dim7'] = np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0])
        templates['aug'] = np.array([1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0])
        
        # Half-diminished
        templates['m7b5'] = np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0])
        
        # Normalize all templates
        for key in templates:
            templates[key] = templates[key] / np.linalg.norm(templates[key])
            
        return templates
    
    def detect(self, chroma: np.ndarray, use_history: bool = True) -> Tuple[str, float]:
        """
        Detect chord from chromagram
        
        Args:
            chroma: 12-element chromagram vector
            use_history: Whether to use temporal smoothing
            
        Returns:
            Tuple of (chord name, confidence)
        """
        if len(chroma) != 12:
            raise ValueError("Chroma vector must have 12 elements")
        
        # Normalize input
        chroma_norm = np.linalg.norm(chroma)
        if chroma_norm > 0:
            chroma = chroma / chroma_norm
        
        best_chord = None
        best_score = -1
        best_root = 0
        
        root_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 
                     'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Test all chord types and all possible roots
        for chord_type, template in self.templates.items():
            for root in range(12):
                # Rotate template to match root
                rotated_template = np.roll(template, root)
                
                # Calculate correlation
                score = np.dot(chroma, rotated_template)
                
                if score > best_score:
                    best_score = score
                    best_root = root
                    best_chord = root_names[root] + chord_type
        
        # Apply temporal smoothing if enabled
        if use_history and len(self.chord_history) > 0:
            self.chord_history.append((best_chord, best_score))
            if len(self.chord_history) > self.history_size:
                self.chord_history.pop(0)
            
            # Weight recent detections
            weighted_scores = {}
            for i, (chord, score) in enumerate(self.chord_history):
                weight = (i + 1) / len(self.chord_history)  # More recent = higher weight
                if chord not in weighted_scores:
                    weighted_scores[chord] = 0
                weighted_scores[chord] += score * weight
            
            # Find best weighted chord
            best_chord = max(weighted_scores, key=weighted_scores.get)
            best_score = weighted_scores[best_chord] / sum((i + 1) / len(self.chord_history) 
                                                           for i in range(len(self.chord_history)))
        
        return best_chord, best_score
    
    def get_chord_tones(self, chord_name: str) -> List[int]:
        """
        Get MIDI note numbers for a chord
        
        Args:
            chord_name: Chord name (e.g., 'Cmaj7', 'F#m')
            
        Returns:
            List of MIDI note numbers
        """
        # Parse root note
        root_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
        
        root_note = chord_name[0]
        offset = 1
        
        # Handle sharps and flats
        if len(chord_name) > 1 and chord_name[1] in ['#', 'b']:
            if chord_name[1] == '#':
                root_note = (root_map[root_note[0]] + 1) % 12
            else:  # flat
                root_note = (root_map[root_note[0]] - 1) % 12
            offset = 2
        else:
            root_note = root_map[root_note]
        
        # Get chord type
        chord_type = chord_name[offset:] if offset < len(chord_name) else ''
        if not chord_type:
            chord_type = 'maj'
        
        # Find matching template
        for template_name, template in self.templates.items():
            if template_name in chord_type:
                # Get notes from template
                notes = []
                for i, val in enumerate(template):
                    if val > 0.5:  # Note is present in chord
                        notes.append(60 + root_note + i)  # Middle C octave
                return notes
        
        # Default to major triad if not found
        return [60 + root_note, 60 + root_note + 4, 60 + root_note + 7]
    
    def suggest_next_chord(self, current_chord: str, key: str = 'C') -> List[Tuple[str, float]]:
        """
        Suggest likely next chords based on music theory
        
        Args:
            current_chord: Current chord name
            key: Key signature
            
        Returns:
            List of (chord, probability) tuples
        """
        # Simple chord progression probabilities (can be enhanced)
        progressions = {
            'I': [('IV', 0.3), ('V', 0.3), ('vi', 0.2), ('ii', 0.1), ('iii', 0.1)],
            'ii': [('V', 0.5), ('vii°', 0.2), ('IV', 0.2), ('I', 0.1)],
            'iii': [('vi', 0.4), ('IV', 0.3), ('I', 0.2), ('ii', 0.1)],
            'IV': [('V', 0.4), ('I', 0.3), ('ii', 0.2), ('vi', 0.1)],
            'V': [('I', 0.6), ('vi', 0.2), ('IV', 0.1), ('ii', 0.1)],
            'vi': [('ii', 0.3), ('IV', 0.3), ('V', 0.2), ('I', 0.2)],
            'vii°': [('I', 0.7), ('vi', 0.2), ('iii', 0.1)]
        }
        
        # Simplified - just return common progressions
        # In production, would analyze the actual chord function
        return [
            (current_chord, 0.2),  # Stay on same chord
            ('G7', 0.3),  # Dominant
            ('Cmaj', 0.2),  # Tonic
            ('Am', 0.15),  # Relative minor
            ('Fmaj', 0.15)  # Subdominant
        ]
