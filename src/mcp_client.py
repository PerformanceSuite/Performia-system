"""
MCP Client for Performia System
Connects to the external Performia_MCP server for pattern recognition
"""

import asyncio
import aiohttp
import numpy as np
from typing import Dict, List, Optional, Any
import yaml
import os
from pathlib import Path

class PerformiaMCPClient:
    """Client for connecting to the Performia MCP server"""
    
    def __init__(self, config_path: str = "config/mcp_config.yaml"):
        """Initialize MCP client with configuration"""
        self.config = self._load_config(config_path)
        self.base_url = f"http://{self.config['mcp']['host']}:{self.config['mcp']['port']}"
        self.session = None
        self.cache = {} if self.config['mcp']['cache']['enabled'] else None
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"MCP config not found: {config_path}")
        
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
        if self.session:
            await self.session.close()
    
    async def connect(self):
        """Establish connection to MCP server"""
        try:
            async with self.session.get(f"{self.base_url}/health") as resp:
                if resp.status == 200:
                    print("Connected to Performia MCP")
                    return True
        except aiohttp.ClientError as e:
            print(f"Failed to connect to MCP: {e}")
            return False
    
    async def disconnect(self):
        """Close connection to MCP server"""
        # Cleanup if needed
        pass
    
    async def recognize_pattern(self, audio_vector: np.ndarray) -> Optional[Dict]:
        """
        Recognize a musical pattern from audio features
        
        Args:
            audio_vector: 128-dimensional feature vector
            
        Returns:
            Pattern match with metadata or None
        """
        # Check cache first if enabled
        if self.cache is not None:
            cache_key = audio_vector.tobytes()
            if cache_key in self.cache:
                return self.cache[cache_key]
        
        # Query MCP server
        endpoint = self.config['mcp']['endpoints']['recognition']
        async with self.session.post(
            f"{self.base_url}{endpoint}",
            json={"vector": audio_vector.tolist()}
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                
                # Cache result if enabled
                if self.cache is not None:
                    self.cache[audio_vector.tobytes()] = result
                
                return result
        
        return None
    
    async def learn_pattern(self, pattern_data: Dict) -> bool:
        """
        Send a new pattern to MCP for learning (Studio mode only)
        
        Args:
            pattern_data: Pattern information including audio features and metadata
            
        Returns:
            Success status
        """
        if not self.config['mcp']['studio']['enable_learning']:
            print("Learning disabled in current mode")
            return False
        
        endpoint = self.config['mcp']['endpoints']['learning']
        async with self.session.post(
            f"{self.base_url}{endpoint}",
            json=pattern_data
        ) as resp:
            return resp.status == 200
    
    async def get_song_info(self, song_id: str) -> Optional[Dict]:
        """
        Retrieve song structure and metadata
        
        Args:
            song_id: Unique song identifier
            
        Returns:
            Song information or None
        """
        endpoint = self.config['mcp']['endpoints']['songs']
        async with self.session.get(f"{self.base_url}{endpoint}/{song_id}") as resp:
            if resp.status == 200:
                return await resp.json()
        return None
    
    async def search_patterns(self, query: Dict) -> List[Dict]:
        """
        Search for patterns matching criteria
        
        Args:
            query: Search parameters (style, tempo_range, complexity, etc.)
            
        Returns:
            List of matching patterns
        """
        endpoint = self.config['mcp']['endpoints']['patterns']
        async with self.session.post(
            f"{self.base_url}{endpoint}/search",
            json=query
        ) as resp:
            if resp.status == 200:
                return await resp.json()
        return []
    
    def get_cached_patterns(self) -> Dict:
        """Return all cached patterns for live mode"""
        return self.cache if self.cache else {}
    
    def clear_cache(self):
        """Clear the pattern cache"""
        if self.cache is not None:
            self.cache.clear()


# Singleton instance for global access
_mcp_client = None

async def get_mcp_client() -> PerformiaMCPClient:
    """Get or create the global MCP client instance"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = PerformiaMCPClient()
        await _mcp_client.connect()
    return _mcp_client

# Example usage
async def example_usage():
    """Example of using the MCP client"""
    async with PerformiaMCPClient() as mcp:
        # Recognize a pattern
        test_vector = np.random.randn(128)
        pattern = await mcp.recognize_pattern(test_vector)
        
        if pattern:
            print(f"Recognized pattern: {pattern['name']}")
        
        # Learn a new pattern (Studio mode)
        new_pattern = {
            "vector": test_vector.tolist(),
            "name": "Jazz Lick #42",
            "style": "bebop",
            "tempo": 140
        }
        success = await mcp.learn_pattern(new_pattern)
        
        if success:
            print("Pattern learned successfully")

if __name__ == "__main__":
    asyncio.run(example_usage())
