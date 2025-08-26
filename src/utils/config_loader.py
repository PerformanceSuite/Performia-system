"""
Configuration loader utility
"""

import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_config(config_path: str = None) -> dict:
    """Load configuration from YAML file"""
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / 'config' / 'config.yaml'
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"✓ Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        # Return default config
        return {
            'audio': {
                'sample_rate': 48000,
                'block_size': 128,
            },
            'agents': {
                'count': 4
            },
            'performance': {
                'tempo': 120
            }
        }
