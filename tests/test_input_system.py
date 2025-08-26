#!/usr/bin/env python3
"""
Test script for Performia audio input system
Tests latency and functionality of guitar input processing
"""

import asyncio
import time
import numpy as np
import logging
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from controllers import AudioInputController, MidiPedalController
from analysis import RealtimeAudioAnalyzer, ChordDetector
from controllers.midi_controller import ListeningMode


async def test_audio_latency():
    """Test audio input latency"""
    print("\n" + "="*50)
    print("AUDIO INPUT LATENCY TEST")
    print("="*50)
    
    controller = AudioInputController(
        device_name="Quantum 2626",
        sample_rate=48000,
        block_size=64
    )
    
    # Measure analysis latency
    latencies = []
    
    def latency_callback(analysis):
        if 'latency_ms' in analysis:
            latencies.append(analysis['latency_ms'])
    
    controller.register_analysis_callback(latency_callback)
    
    print("Starting audio input...")
    await controller.start_listening()
    
    print("Measuring latency for 5 seconds (play some notes)...")
    await asyncio.sleep(5)
    
    await controller.stop_listening()
    
    if latencies:
        print(f"\nLatency Statistics:")
        print(f"  Mean: {np.mean(latencies):.2f}ms")
        print(f"  Min:  {np.min(latencies):.2f}ms")
        print(f"  Max:  {np.max(latencies):.2f}ms")
        print(f"  Std:  {np.std(latencies):.2f}ms")
        
        if np.mean(latencies) < 8:
            print("✓ PASS: Mean latency under 8ms target")
        else:
            print("✗ FAIL: Mean latency exceeds 8ms target")
    else:
        print("No audio detected - make sure to play your guitar!")


async def test_chord_detection():
    """Test chord detection accuracy"""
    print("\n" + "="*50)
    print("CHORD DETECTION TEST")
    print("="*50)
    
    controller = AudioInputController(
        device_name="Quantum 2626",
        sample_rate=48000,
        block_size=64
    )
    
    detected_chords = []
    
    def chord_callback(analysis):
        if analysis.get('chord'):
            chord = analysis['chord']
            confidence = analysis.get('chord_confidence', 0)
            detected_chords.append((chord, confidence))
            print(f"  Detected: {chord} (confidence: {confidence:.2f})")
    
    controller.register_analysis_callback(chord_callback)
    
    print("\nPlay the following chords:")
    test_chords = ['C', 'G', 'Am', 'F', 'Dm', 'Em']
    for chord in test_chords:
        print(f"  - {chord}")
    
    print("\nStarting detection...")
    await controller.start_listening()
    
    # Listen for 20 seconds
    await asyncio.sleep(20)
    
    await controller.stop_listening()
    
    if detected_chords:
        print(f"\nDetected {len(detected_chords)} chord events")
        avg_confidence = np.mean([c[1] for c in detected_chords])
        print(f"Average confidence: {avg_confidence:.2f}")
        
        # Show unique chords detected
        unique_chords = list(set(c[0] for c in detected_chords))
        print(f"Unique chords detected: {', '.join(unique_chords)}")
    else:
        print("No chords detected")


async def test_midi_pedal():
    """Test MIDI pedal responsiveness"""
    print("\n" + "="*50)
    print("MIDI PEDAL TEST")
    print("="*50)
    
    controller = MidiPedalController(device_name="Quantum 2626")
    
    events = []
    
    def pedal_callback(state):
        events.append(('sustain', state, time.time()))
        print(f"  Sustain pedal: {'ON' if state else 'OFF'}")
    
    def mode_callback(mode):
        events.append(('mode', mode.value, time.time()))
        print(f"  Mode changed to: {mode.value}")
    
    controller.register_callback('listen_start', pedal_callback)
    controller.register_callback('listen_stop', pedal_callback)
    controller.register_callback('mode_change', mode_callback)
    
    print("Test the following pedals:")
    print("  1. Press and release SUSTAIN pedal (CC64)")
    print("  2. Press MODE CHANGE pedal (CC65) multiple times")
    print("  3. Press Ctrl+C when done")
    
    try:
        await controller.listen()
    except KeyboardInterrupt:
        pass
    
    controller.close()
    
    if events:
        print(f"\nRecorded {len(events)} events")
        
        # Check response time
        if len(events) >= 2:
            response_times = []
            for i in range(1, len(events)):
                dt = (events[i][2] - events[i-1][2]) * 1000  # ms
                if dt < 1000:  # Ignore long pauses
                    response_times.append(dt)
            
            if response_times:
                print(f"Average response time: {np.mean(response_times):.1f}ms")


async def test_integrated_system():
    """Test the complete integrated system"""
    print("\n" + "="*50)
    print("INTEGRATED SYSTEM TEST")
    print("="*50)
    
    from integration import InputSystem
    
    system = InputSystem()
    await system.initialize()
    
    print("Running calibration...")
    calibration = await system.calibrate()
    if calibration:
        print(f"  Noise floor: {calibration.get('noise_floor', 0):.4f}")
        print(f"  Recommended threshold: {calibration.get('recommended_threshold', 0):.4f}")
    
    print("\nSystem ready. Test workflow:")
    print("  1. Press SUSTAIN pedal to start listening")
    print("  2. Play some chords or notes")
    print("  3. Release SUSTAIN pedal to stop")
    print("  4. Press MODE pedal to change modes")
    print("  5. Press Ctrl+C to exit")
    
    # Monitor status
    async def status_monitor():
        while True:
            status = system.get_status()
            if status['audio_input'] and status['audio_input']['listening']:
                chord = status['audio_input'].get('chord', '--')
                level = status['audio_input'].get('level', 0)
                mode = status['listener'].get('mode', '--')
                print(f"\r[{mode}] Chord: {chord:6s} Level: {level:.2f}", end='', flush=True)
            await asyncio.sleep(0.1)
    
    try:
        await asyncio.gather(
            system.start(),
            status_monitor()
        )
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        await system.stop()


async def main():
    """Run all tests"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*60)
    print("   PERFORMIA AUDIO INPUT SYSTEM - COMPREHENSIVE TEST")
    print("="*60)
    
    tests = [
        ("Audio Latency", test_audio_latency),
        ("Chord Detection", test_chord_detection),
        ("MIDI Pedal", test_midi_pedal),
        ("Integrated System", test_integrated_system)
    ]
    
    print("\nAvailable tests:")
    for i, (name, _) in enumerate(tests, 1):
        print(f"  {i}. {name}")
    print(f"  {len(tests)+1}. Run all tests")
    print("  0. Exit")
    
    choice = input("\nSelect test to run: ")
    
    try:
        choice = int(choice)
        if choice == 0:
            return
        elif choice == len(tests) + 1:
            # Run all tests
            for name, test_func in tests:
                print(f"\nRunning {name}...")
                try:
                    await test_func()
                except Exception as e:
                    print(f"Error in {name}: {e}")
        elif 1 <= choice <= len(tests):
            await tests[choice-1][1]()
        else:
            print("Invalid choice")
    except ValueError:
        print("Invalid input")
    except KeyboardInterrupt:
        print("\nTest interrupted")


if __name__ == "__main__":
    asyncio.run(main())
