import threading
from typing import Optional
import numpy as np
import os
import sys
from .generator import AudioGenerator

# Try to import sounddevice, fall back to mock if not available
try:
    import sounddevice as sd

    AUDIO_BACKEND = "sounddevice"
except (OSError, ImportError):
    # Use mock backend for WSL or when PortAudio is not available
    from . import mock_backend as sd

    AUDIO_BACKEND = "mock"
    print(
        f"Note: Running with mock audio backend (no actual audio output)",
        file=sys.stderr,
    )


class AudioStreamManager:
    def __init__(self, sample_rate: int = 44100, block_size: int = 512):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.generator = AudioGenerator(sample_rate)
        self.stream: Optional[sd.OutputStream] = None
        self.is_playing = False
        self._lock = threading.Lock()

        self.left_carrier_freq = 440.0
        self.left_pulse_freq = 10.0
        self.right_carrier_freq = 440.0
        self.right_pulse_freq = 10.0

        self.channels_linked = True
        self.backend = AUDIO_BACKEND

    def set_left_parameters(self, carrier_freq: float, pulse_freq: float):
        with self._lock:
            self.left_carrier_freq = max(0.0, carrier_freq)
            self.left_pulse_freq = max(0.0, pulse_freq)

            if self.channels_linked:
                self.right_carrier_freq = self.left_carrier_freq
                self.right_pulse_freq = self.left_pulse_freq

    def set_right_parameters(self, carrier_freq: float, pulse_freq: float):
        with self._lock:
            self.right_carrier_freq = max(0.0, carrier_freq)
            self.right_pulse_freq = max(0.0, pulse_freq)

            if self.channels_linked:
                self.left_carrier_freq = self.right_carrier_freq
                self.left_pulse_freq = self.right_pulse_freq

    def set_channels_linked(self, linked: bool):
        with self._lock:
            self.channels_linked = linked
            if linked:
                self.right_carrier_freq = self.left_carrier_freq
                self.right_pulse_freq = self.left_pulse_freq

    def _audio_callback(self, outdata: np.ndarray, frames: int, time_info, status):
        if status:
            print(f"Audio stream status: {status}")

        with self._lock:
            audio_data = self.generator.generate_stereo_frames(
                frames,
                self.left_carrier_freq,
                self.left_pulse_freq,
                self.right_carrier_freq,
                self.right_pulse_freq,
            )

        outdata[:] = audio_data

    def start(self):
        if self.is_playing:
            return

        try:
            self.generator.reset_phases()
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                channels=2,
                callback=self._audio_callback,
                dtype="float32",
            )
            self.stream.start()
            self.is_playing = True
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            self.is_playing = False
            raise

    def stop(self):
        if not self.is_playing:
            return

        self.is_playing = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def toggle_playback(self) -> bool:
        if self.is_playing:
            self.stop()
        else:
            self.start()
        return self.is_playing

    def __del__(self):
        self.stop()
