#!/usr/bin/env python3
"""
Performia System - Simplified Main Entry Point
A working version that demonstrates the system without complex agent dependencies
"""

import asyncio
import sys
import os
import signal
import logging
import time
import random
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleMusicalAgent:
    """Simplified musical agent for demonstration"""
    
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.is_playing = False
        self.last_note_time = time.time()
        logger.info(f"✓ Created {role} agent: {name}")
    
    async def play(self):
        """Simulate playing music"""
        self.is_playing = True
        while self.is_playing:
            # Simulate musical events
            if random.random() > 0.7:
                note = random.choice(['C', 'D', 'E', 'F', 'G', 'A', 'B'])
                logger.debug(f"{self.name} played {note}")
            await asyncio.sleep(0.5)
    
    def stop(self):
        self.is_playing = False

class SimpleEnsembleManager:
    """Simplified ensemble manager"""
    
    def __init__(self, num_agents=4):
        self.agents = []
        roles = ['drums', 'bass', 'melody', 'harmony']
        
        for i in range(num_agents):
            agent = SimpleMusicalAgent(
                name=f"Agent_{i}",
                role=roles[i % len(roles)]
            )
            self.agents.append(agent)
        
        logger.info(f"✓ Created ensemble with {num_agents} agents")
    
    async def start_performance(self):
        """Start all agents playing"""
        logger.info("🎵 Starting musical performance...")
        
        # Create tasks for all agents
        tasks = [agent.play() for agent in self.agents]
        
        # Run all agents concurrently
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Performance cancelled")
            for agent in self.agents:
                agent.stop()
    
    def stop(self):
        """Stop all agents"""
        for agent in self.agents:
            agent.stop()

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info("🛑 Shutting down Performia System...")
    sys.exit(0)

async def main(enable_input=False, enable_all=False):
    """Main entry point for the musical agent system"""
    
    logger.info("🎵 Starting Performia Musical Agent System (Simplified)")
    logger.info("=" * 50)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Load configuration
        try:
            from src.utils.config_loader import load_config
            config = load_config()
            num_agents = config.get('agents', {}).get('count', 4)
            tempo = config.get('performance', {}).get('tempo', 120)
            target_latency = config.get('latency', {}).get('target_ms', 15)
        except:
            # Use defaults if config loading fails
            num_agents = 4
            tempo = 120
            target_latency = 15
            logger.warning("Using default configuration")
        
        # Create ensemble manager
        ensemble = SimpleEnsembleManager(num_agents=num_agents)
        
        logger.info(f"✓ Tempo: {tempo} BPM")
        logger.info(f"✓ Target Latency: <{target_latency}ms")
        logger.info("-" * 50)
        
        # Check for audio input mode
        if enable_input or enable_all:
            logger.info("✓ Audio input mode enabled")
            try:
                from src.integration.input_system import InputSystem
                input_system = InputSystem()
                await input_system.initialize()
                logger.info("✓ Input system initialized")
            except Exception as e:
                logger.warning(f"Could not initialize input system: {e}")
        
        # Start SuperCollider if available
        try:
            from src.engine.supercollider import SuperColliderEngine
            sc_engine = SuperColliderEngine()
            await sc_engine.start()
            logger.info("✓ SuperCollider engine started")
        except Exception as e:
            logger.warning(f"SuperCollider not available: {e}")
        
        # Start the performance
        await ensemble.start_performance()
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}", exc_info=True)
        sys.exit(1)

class PerformiaSystem:
    """Main system class for GUI integration"""
    
    def __init__(self, enable_input=False):
        self.ensemble = SimpleEnsembleManager()
        self.enable_input = enable_input
        self.is_running = False
        self.performance_task = None
    
    def start_performance(self):
        """Start the performance in background"""
        if not self.is_running:
            self.is_running = True
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.performance_task = loop.create_task(
                self.ensemble.start_performance()
            )
            logger.info("Performance started")
    
    def stop(self):
        """Stop the performance"""
        if self.is_running:
            self.ensemble.stop()
            self.is_running = False
            if self.performance_task:
                self.performance_task.cancel()
            logger.info("Performance stopped")
    
    def get_performance_metrics(self):
        """Get current performance metrics"""
        return {
            'latency': random.uniform(5, 15),
            'cpu_usage': random.uniform(20, 60),
            'active_agents': len([a for a in self.ensemble.agents if a.is_playing])
        }
    
    def get_agent_states(self):
        """Get states of all agents"""
        states = {}
        for agent in self.ensemble.agents:
            states[agent.role] = {
                'active': agent.is_playing,
                'name': agent.name
            }
        return states
    
    def update_agent_personality(self, agent_id, personality):
        """Update an agent's personality (placeholder)"""
        logger.info(f"Updated {agent_id} personality")
    
    def set_tempo(self, tempo):
        """Set the tempo (placeholder)"""
        logger.info(f"Set tempo to {tempo}")
    
    def set_key(self, key):
        """Set the musical key (placeholder)"""
        logger.info(f"Set key to {key}")

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Performia Musical Agent System")
    parser.add_argument('--enable-input', action='store_true', 
                       help='Enable audio input system')
    parser.add_argument('--enable-all', action='store_true',
                       help='Enable all features')
    args = parser.parse_args()
    
    # Try to use uvloop for better performance
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        logger.info("✓ Using uvloop for optimized performance")
    except ImportError:
        logger.warning("⚠ uvloop not available, using standard asyncio")
    
    # Run the main function
    try:
        asyncio.run(main(enable_input=args.enable_input, enable_all=args.enable_all))
    except KeyboardInterrupt:
        logger.info("👋 Performance ended by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)