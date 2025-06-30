import threading
from typing import Optional
import numpy as np
import sys
import logging
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
    def __init__(self, sample_rate: int = 44100, block_size: int = 512, volume: float = 0.4):
        self.logger = logging.getLogger(__name__)
        
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.generator = AudioGenerator(sample_rate, volume)
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
        
        self.logger.info(f"AudioStreamManager initialized - SR: {sample_rate}Hz, Block: {block_size}, Backend: {AUDIO_BACKEND}")
        self.logger.info(f"Default parameters - Carrier: {self.left_carrier_freq}Hz, Pulse: {self.left_pulse_freq}Hz, Volume: {volume}")

    def get_available_devices(self):
        """Get list of available audio output devices"""
        try:
            self.logger.debug("Querying available audio devices...")
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
            self.logger.info(f"Found {len(output_devices)} available audio output devices")
            return output_devices
        except Exception as e:
            self.logger.error(f"Error querying audio devices: {e}")
            return []

    def set_output_device(self, device_index: Optional[int]):
        """Set the output device by index. None means use default device."""
        with self._lock:
            if self.is_playing:
                self.logger.info("Stopping playback to change audio device")
                self.stop()
            self.selected_device = device_index
            self.logger.info(f"Audio output device set to: {device_index if device_index is not None else 'Default'}")

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
            self.logger.debug(f"Left channel parameters set - Carrier: {self.left_carrier_freq}Hz, Pulse: {self.left_pulse_freq}Hz")

            if self.channels_linked:
                self.right_carrier_freq = self.left_carrier_freq
                self.right_pulse_freq = self.left_pulse_freq
                self.logger.debug("Right channel synced to left channel parameters")

    def set_right_parameters(self, carrier_freq: float, pulse_freq: float):
        with self._lock:
            self.right_carrier_freq = max(0.0, carrier_freq)
            self.right_pulse_freq = max(0.0, pulse_freq)
            self.logger.debug(f"Right channel parameters set - Carrier: {self.right_carrier_freq}Hz, Pulse: {self.right_pulse_freq}Hz")

            if self.channels_linked:
                self.left_carrier_freq = self.right_carrier_freq
                self.left_pulse_freq = self.right_pulse_freq
                self.logger.debug("Left channel synced to right channel parameters")

    def set_channels_linked(self, linked: bool):
        with self._lock:
            self.channels_linked = linked
            if linked:
                self.right_carrier_freq = self.left_carrier_freq
                self.right_pulse_freq = self.left_pulse_freq
    
    def set_volume(self, volume: float):
        """Set the master volume (0.0 to 1.0)"""
        with self._lock:
            self.generator.set_volume(volume)

    def _audio_callback(self, outdata: np.ndarray, frames: int, time_info, status):
        if status:
            self.logger.warning(f"Audio stream status: {status}")

        # Only log callback details at debug level to avoid spam
        self.logger.debug(f"Audio callback - frames: {frames}, timestamp: {time_info}")

        with self._lock:
            audio_data = self.generator.generate_stereo_frames(
                frames,
                self.left_carrier_freq,
                self.left_pulse_freq,
                self.right_carrier_freq,
                self.right_pulse_freq,
            )

        # Calculate RMS levels to detect if signal contains audio
        rms_left = np.sqrt(np.mean(audio_data[:, 0] ** 2))
        rms_right = np.sqrt(np.mean(audio_data[:, 1] ** 2))
        rms_total = np.sqrt(np.mean(audio_data ** 2))
        
        # Log audio levels (but not too frequently)
        if hasattr(self, '_callback_count'):
            self._callback_count += 1
        else:
            self._callback_count = 0
            
        # Log audio levels every 100 callbacks (roughly every 2-3 seconds at typical rates)
        if self._callback_count % 100 == 0:
            self.logger.info(f"Audio levels - Left RMS: {rms_left:.6f}, Right RMS: {rms_right:.6f}, Total RMS: {rms_total:.6f}")
        
        # Check for silent output and warn immediately
        if rms_total < 1e-10:
            self.logger.warning("Audio output is essentially silent! Check audio generation parameters.")

        outdata[:] = audio_data

    def start(self):
        if self.is_playing:
            self.logger.debug("Start() called but audio is already playing")
            return

        try:
            self.logger.info("Starting audio stream...")
            self.generator.reset_phases()
            self._callback_count = 0  # Reset callback counter
            
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
                self.logger.info(f"Using audio device index: {self.selected_device}")
            else:
                self.logger.info("Using default audio device")

            self.logger.info(f"Stream parameters: SR={self.sample_rate}Hz, Block={self.block_size}, Channels=2, Device={self.selected_device}")
            self.logger.info(f"Audio parameters: L[{self.left_carrier_freq}Hz carrier, {self.left_pulse_freq}Hz pulse] R[{self.right_carrier_freq}Hz carrier, {self.right_pulse_freq}Hz pulse]")
            
            self.stream = sd.OutputStream(**stream_params)
            self.stream.start()
            self.is_playing = True
            self.logger.info("Audio stream started successfully")
            
        except sd.PortAudioError as e:
            error_msg = f"PortAudio Error: {e}"
            if hasattr(e, 'args') and len(e.args) > 0:
                error_code = e.args[0] if isinstance(e.args[0], int) else "Unknown"
                error_msg += f" (Error code: {error_code})"
            
            # Add specific PortAudio error handling
            if "Invalid device" in str(e):
                error_msg += " - The selected audio device is invalid or not available"
            elif "Invalid sample rate" in str(e):
                error_msg += f" - Sample rate {self.sample_rate} is not supported by the device"
            elif "Device unavailable" in str(e):
                error_msg += " - The audio device is currently unavailable"
            elif "Insufficient memory" in str(e):
                error_msg += " - Insufficient memory to start audio stream"
            
            self.logger.error(error_msg)
            self.is_playing = False
            raise RuntimeError(error_msg) from e
            
        except ImportError as e:
            error_msg = f"Audio backend import error: {e} - PortAudio may not be installed"
            self.logger.error(error_msg)
            self.is_playing = False
            raise RuntimeError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Unexpected error starting audio stream: {type(e).__name__}: {e}"
            self.logger.error(error_msg)
            self.is_playing = False
            raise RuntimeError(error_msg) from e

    def stop(self):
        if not self.is_playing:
            self.logger.debug("Stop() called but audio is not playing")
            return

        self.logger.info("Stopping audio stream...")
        self.is_playing = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
                self.stream = None
                self.logger.info("Audio stream stopped successfully")
            except Exception as e:
                self.logger.error(f"Error stopping audio stream: {type(e).__name__}: {e}")
                self.stream = None  # Ensure stream is cleared even if stop/close fails

    def toggle_playback(self) -> bool:
        if self.is_playing:
            self.stop()
        else:
            self.start()
        return self.is_playing

    def __del__(self):
        self.stop()
