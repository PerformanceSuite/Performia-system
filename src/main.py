#!/usr/bin/env python3
"""
Performia System - Ultra-Low Latency Musical Agent System
Main entry point for the multi-agent musical performance system.
"""

import asyncio
import sys
import os
import signal
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.ensemble_manager import MusicalEnsembleManager
from src.engine.supercollider import SuperColliderEngine
from src.memory.shared_memory import SharedMusicalContext, LockFreeRingBuffer
from src.personality.personality import load_personalities

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info("🛑 Shutting down Performia System...")
    sys.exit(0)

async def main():
    """Main entry point for the musical agent system"""
    
    logger.info("🎵 Starting Performia Musical Agent System")
    logger.info("=" * 50)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Load configuration
        from src.utils.config_loader import load_config
        config = load_config()
        
        # Create ensemble manager with configuration
        ensemble = MusicalEnsembleManager(
            num_agents=config.get('agents', {}).get('count', 4),
            config=config
        )
        
        logger.info(f"✓ Created ensemble with {len(ensemble.agents)} agents")
        logger.info(f"✓ Tempo: {config.get('performance', {}).get('tempo', 120)} BPM")
        logger.info(f"✓ Target Latency: <{config.get('latency', {}).get('target_ms', 15)}ms")
        logger.info("-" * 50)
        
        # Optional: Start latency monitoring
        if config.get('latency', {}).get('measurement', False):
            from src.utils.latency_monitor import LatencyMonitor
            monitor = LatencyMonitor()
            asyncio.create_task(monitor.start_monitoring())
            logger.info("✓ Latency monitoring enabled")
        
        # Start the performance
        await ensemble.start_performance()
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # Try to use uvloop for better performance
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        logger.info("✓ Using uvloop for optimized performance")
    except ImportError:
        logger.warning("⚠ uvloop not available, using standard asyncio")
    
    # Run the main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Performance ended by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
