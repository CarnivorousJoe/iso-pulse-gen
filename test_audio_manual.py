#!/usr/bin/env python3
"""
Manual test script for the Isochronic Pulse Generator audio output.
This script tests the audio generation without the GUI.
"""

import time
import sys
from src.iso_pulse_gen.audio.stream_manager import AudioStreamManager


def test_audio_output():
    print("Isochronic Pulse Generator - Manual Audio Test")
    print("=" * 50)

    try:
        audio_manager = AudioStreamManager()
        print(f"Audio backend: {audio_manager.backend}")

        print("\nTest 1: Default settings (440Hz carrier, 10Hz pulse)")
        audio_manager.start()
        time.sleep(3)
        audio_manager.stop()

        print("\nTest 2: Different frequencies per channel")
        audio_manager.set_channels_linked(False)
        audio_manager.set_left_parameters(440.0, 8.0)
        audio_manager.set_right_parameters(528.0, 12.0)
        audio_manager.start()
        time.sleep(3)
        audio_manager.stop()

        print("\nTest 3: Low frequency pulse (2Hz)")
        audio_manager.set_channels_linked(True)
        audio_manager.set_left_parameters(300.0, 2.0)
        audio_manager.start()
        time.sleep(4)
        audio_manager.stop()

        print("\nAudio tests completed successfully!")

    except Exception as e:
        print(f"\nError during audio test: {e}")
        print("\nNote: This test requires PortAudio to be installed on your system.")
        print("On Ubuntu/Debian: sudo apt-get install portaudio19-dev")
        print("On macOS: brew install portaudio")
        print("On Windows: PortAudio should be included with sounddevice")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(test_audio_output())
