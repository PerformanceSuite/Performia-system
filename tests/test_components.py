#!/usr/bin/env python3
"""
Simple test to verify Performia system components
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.agents.base_agent import BaseMusicalAgent
        print("✓ BaseMusicalAgent imported")
    except ImportError as e:
        print(f"✗ Failed to import BaseMusicalAgent: {e}")
        return False
    
    try:
        from src.memory.shared_memory import SharedMusicalContext, LockFreeRingBuffer
        print("✓ SharedMusicalContext imported")
        print("✓ LockFreeRingBuffer imported")
    except ImportError as e:
        print(f"✗ Failed to import memory modules: {e}")
        return False
    
    try:
        from src.personality.personality import MusicalPersonality, load_personalities
        print("✓ MusicalPersonality imported")
    except ImportError as e:
        print(f"✗ Failed to import personality: {e}")
        return False
    
    try:
        from src.utils.config_loader import load_config
        print("✓ Config loader imported")
    except ImportError as e:
        print(f"✗ Failed to import config loader: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    from src.utils.config_loader import load_config
    config = load_config()
    
    assert 'audio' in config, "Missing audio config"
    assert 'agents' in config, "Missing agents config"
    assert 'performance' in config, "Missing performance config"
    
    print(f"✓ Config loaded successfully")
    print(f"  - Agents: {config['agents']['count']}")
    print(f"  - Tempo: {config['performance']['tempo']} BPM")
    print(f"  - Sample Rate: {config['audio']['sample_rate']} Hz")
    
    return True

def test_personalities():
    """Test personality loading"""
    print("\nTesting personalities...")
    
    from src.personality.personality import load_personalities
    personalities = load_personalities()
    
    assert len(personalities) > 0, "No personalities loaded"
    
    print(f"✓ Loaded {len(personalities)} personalities:")
    for name in personalities:
        print(f"  - {name}")
    
    return True

def test_shared_memory():
    """Test shared memory creation"""
    print("\nTesting shared memory...")
    
    from src.memory.shared_memory import SharedMusicalContext, LockFreeRingBuffer
    
    try:
        context = SharedMusicalContext()
        print("✓ SharedMusicalContext created")
        
        buffer = LockFreeRingBuffer(size=256)
        print("✓ LockFreeRingBuffer created")
        
        # Test write/read
        buffer.write("test_agent", {"note": 60, "velocity": 0.7})
        event = buffer.read("test_agent")
        assert event is not None, "Failed to read from buffer"
        assert event['note'] == 60, "Incorrect data read from buffer"
        
        print("✓ Shared memory read/write working")
        
        # Cleanup
        buffer.cleanup()
        
        return True
    except Exception as e:
        print(f"✗ Shared memory test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("PERFORMIA SYSTEM COMPONENT TEST")
    print("=" * 60)
    
    all_passed = True
    
    # Run tests
    if not test_imports():
        all_passed = False
    
    if not test_config():
        all_passed = False
    
    if not test_personalities():
        all_passed = False
    
    if not test_shared_memory():
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - System ready!")
        print("\nNext step: Run latency test with:")
        print("  python scripts/measure_latency.py")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
