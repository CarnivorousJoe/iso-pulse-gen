import threading
from typing import Optional
import numpy as np
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
        "Note: Running with mock audio backend (no actual audio output)",
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
        self.selected_device = None  # None means use default device

    def get_available_devices(self):
        """Get list of available audio output devices"""
        try:
            devices = sd.query_devices()
            # Filter for devices that support output
            output_devices = []
            for i, device in enumerate(devices):
                if isinstance(device, dict):
                    # Check if device supports output (has output channels)
                    max_outputs = device.get("max_output_channels", 0)
                    if max_outputs > 0:
                        output_devices.append(
                            {
                                "index": i,
                                "name": device["name"],
                                "channels": max_outputs,
                                "default_samplerate": device.get(
                                    "default_samplerate", 44100
                                ),
                            }
                        )
                else:
                    # Handle case where devices is a single device dict
                    max_outputs = (
                        device.get("max_output_channels", 0)
                        if hasattr(device, "get")
                        else 2
                    )
                    output_devices.append(
                        {
                            "index": 0,
                            "name": str(device)
                            if not hasattr(device, "get")
                            else device.get("name", "Default Device"),
                            "channels": max_outputs,
                            "default_samplerate": 44100,
                        }
                    )
                    break
            return output_devices
        except Exception as e:
            print(f"Error querying audio devices: {e}")
            return []

    def set_output_device(self, device_index: Optional[int]):
        """Set the output device by index. None means use default device."""
        with self._lock:
            if self.is_playing:
                # Stop current playback before changing devices
                self.stop()
            self.selected_device = device_index

    def get_current_device_info(self):
        """Get information about the currently selected device"""
        try:
            if self.selected_device is None:
                return {"name": "Default Device", "index": None}

            devices = self.get_available_devices()
            for device in devices:
                if device["index"] == self.selected_device:
                    return device
            return {"name": "Unknown Device", "index": self.selected_device}
        except Exception:
            return {"name": "Error Getting Device Info", "index": self.selected_device}

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
            # Build stream parameters
            stream_params = {
                "samplerate": self.sample_rate,
                "blocksize": self.block_size,
                "channels": 2,
                "callback": self._audio_callback,
                "dtype": "float32",
            }

            # Add device parameter if a specific device is selected
            if self.selected_device is not None:
                stream_params["device"] = self.selected_device

            self.stream = sd.OutputStream(**stream_params)
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
