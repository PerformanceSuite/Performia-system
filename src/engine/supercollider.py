"""
SuperCollider integration for ultra-low latency audio synthesis
"""

import subprocess
import time
import platform
import logging
from typing import Dict, Optional
from pythonosc import udp_client

logger = logging.getLogger(__name__)

class SuperColliderEngine:
    """Manages SuperCollider server and synthesis"""
    
    def __init__(self, server_options: dict = None):
        self.server_options = server_options or {
            'blockSize': 64,
            'hardwareBufferSize': 128,
            'sampleRate': 48000,
            'numOutputBusChannels': 2,
            'memSize': 65536 * 4,
            'maxNodes': 2048,
            'verbosity': 0
        }
        
        # OSC client for sending to SuperCollider
        self.osc_client = udp_client.SimpleUDPClient("127.0.0.1", 57110)
        self.server_process = None
        
        logger.info("🎛️ Initializing SuperCollider Engine")
