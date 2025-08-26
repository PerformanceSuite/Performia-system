"""
Musical Personality system for agents
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

@dataclass
class MusicalPersonality:
    """Defines an agent's musical personality"""
    
    # Core personality traits (0-1 scale)
    aggression: float = 0.5
    creativity: float = 0.5
    responsiveness: float = 0.8
    stability: float = 0.7
    
    # Musical preferences
    melodic_range: Tuple[int, int] = (48, 72)
    preferred_rhythm: str = "straight"
    harmonic_complexity: float = 0.5
    
    # Interaction style
    leader_tendency: float = 0.5
    call_response: bool = True
    imitation_tendency: float = 0.3
    
    def to_synthesis_params(self) -> Dict:
        """Convert personality to synthesis parameters"""
        return {
            'attack': 0.001 + (1 - self.aggression) * 0.1,
            'decay': 0.05 + self.stability * 0.2,
            'sustain': 0.3 + self.stability * 0.5,
            'release': 0.1 + (1 - self.aggression) * 0.5,
            'filter_cutoff': 200 + self.harmonic_complexity * 5000,
            'resonance': 0.5 + self.creativity * 3.5,
            'amplitude': 0.3 + self.aggression * 0.6
        }

def load_personalities() -> Dict[str, MusicalPersonality]:
    """Load personality presets from configuration file"""
    config_path = Path(__file__).parent.parent.parent / 'config' / 'personalities.json'
    
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        personalities = {}
        for name, params in data.get('personalities', {}).items():
            # Convert melodic_range from list to tuple if present
            if 'melodic_range' in params:
                params['melodic_range'] = tuple(params['melodic_range'])
            
            personalities[name] = MusicalPersonality(**params)
            logger.debug(f"Loaded personality: {name}")
        
        logger.info(f"✓ Loaded {len(personalities)} personality presets")
        return personalities
    
    except Exception as e:
        logger.error(f"Failed to load personalities: {e}")
        # Return default personality if loading fails
        return {
            'default': MusicalPersonality()
        }
