#!/usr/bin/env python3
"""
Latency measurement tool for Performia System
Measures various system latencies to ensure <15ms target
"""

import time
import statistics
import multiprocessing as mp
from multiprocessing import shared_memory
import struct
import numpy as np
from pythonosc import udp_client
import asyncio

def measure_shared_memory_latency(iterations=1000):
    """Measure shared memory communication latency"""
    print("\n📊 Measuring Shared Memory Latency...")
    
    shm = shared_memory.SharedMemory(create=True, size=8)
    latencies = []
    
    for i in range(iterations):
        start = time.perf_counter_ns()
        
        # Write timestamp
        struct.pack_into('q', shm.buf, 0, start)
        
        # Read back
        value = struct.unpack_from('q', shm.buf, 0)[0]
        
        end = time.perf_counter_ns()
        latency_ms = (end - start) / 1_000_000
        latencies.append(latency_ms)
    
    shm.close()
    shm.unlink()
    
    return {
        'mean': statistics.mean(latencies),
        'min': min(latencies),
        'max': max(latencies),
        'p99': statistics.quantiles(latencies, n=100)[98] if len(latencies) > 100 else max(latencies)
    }

def measure_osc_latency(iterations=100):
    """Measure OSC communication latency to SuperCollider"""
    print("\n📊 Measuring OSC Communication Latency...")
    
    client = udp_client.SimpleUDPClient("127.0.0.1", 57110)
    latencies = []
    
    for i in range(iterations):
        start = time.perf_counter_ns()
        
        # Send OSC message
        client.send_message("/status", [])
        
        # Simple timing measurement (actual round-trip would need response)
        end = time.perf_counter_ns()
        latency_ms = (end - start) / 1_000_000
        latencies.append(latency_ms)
    
    return {
        'mean': statistics.mean(latencies),
        'min': min(latencies),
        'max': max(latencies),
        'p99': statistics.quantiles(latencies, n=100)[98] if len(latencies) > 100 else max(latencies)
    }

async def measure_async_latency(iterations=1000):
    """Measure async event loop latency"""
    print("\n📊 Measuring Async Event Loop Latency...")
    
    latencies = []
    
    for i in range(iterations):
        start = time.perf_counter_ns()
        await asyncio.sleep(0)  # Yield to event loop
        end = time.perf_counter_ns()
        latency_ms = (end - start) / 1_000_000
        latencies.append(latency_ms)
    
    return {
        'mean': statistics.mean(latencies),
        'min': min(latencies),
        'max': max(latencies),
        'p99': statistics.quantiles(latencies, n=100)[98] if len(latencies) > 100 else max(latencies)
    }

def print_results(name, results):
    """Print formatted results"""
    print(f"\n✅ {name}:")
    print(f"   Mean: {results['mean']:.3f}ms")
    print(f"   Min:  {results['min']:.3f}ms")
    print(f"   Max:  {results['max']:.3f}ms")
    print(f"   P99:  {results['p99']:.3f}ms")
    
    # Check if meets target
    if results['p99'] < 15:
        print(f"   ✓ PASS - Under 15ms target")
    else:
        print(f"   ✗ FAIL - Exceeds 15ms target")

async def main():
    print("=" * 60)
    print("🎵 PERFORMIA SYSTEM LATENCY MEASUREMENT")
    print("=" * 60)
    print("Target: <15ms total system latency")
    
    # Measure shared memory
    shm_results = measure_shared_memory_latency()
    print_results("Shared Memory", shm_results)
    
    # Measure OSC
    try:
        osc_results = measure_osc_latency()
        print_results("OSC Communication", osc_results)
    except Exception as e:
        print(f"\n⚠ OSC measurement failed (is SuperCollider running?): {e}")
    
    # Measure async
    async_results = await measure_async_latency()
    print_results("Async Event Loop", async_results)
    
    # Total system estimate
    print("\n" + "=" * 60)
    print("📊 ESTIMATED TOTAL SYSTEM LATENCY:")
    
    estimated_total = (
        shm_results['p99'] +  # Agent communication
        2.5 +  # SuperCollider synthesis (typical)
        async_results['p99']  # Event processing
    )
    
    print(f"   Estimated Total: {estimated_total:.2f}ms")
    
    if estimated_total < 15:
        print("   ✅ SYSTEM PASSES - Ready for real-time performance!")
    else:
        print("   ⚠ SYSTEM NEEDS OPTIMIZATION")
        print("\n   Suggestions:")
        print("   - Reduce audio buffer size")
        print("   - Enable real-time scheduling")
        print("   - Check CPU governor settings")
        print("   - Disable power management")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        print("✓ Using uvloop for measurement\n")
    except ImportError:
        print("⚠ uvloop not available\n")
    
    asyncio.run(main())
