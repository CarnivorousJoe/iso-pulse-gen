import threading
import time
from typing import Optional, Callable
import numpy as np


class MockOutputStream:
    """Mock audio stream that simulates sounddevice.OutputStream API"""

    def __init__(
        self,
        samplerate: int,
        blocksize: int,
        channels: int,
        callback: Callable,
        dtype: str,
        device=None,
        **kwargs,
    ):
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.channels = channels
        self.callback = callback
        self.dtype = dtype
        self.device = device
        self.is_active = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self):
        """Start the mock audio stream"""
        if self.is_active:
            return

        self.is_active = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_callback_loop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        """Stop the mock audio stream"""
        if not self.is_active:
            return

        self.is_active = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def close(self):
        """Close the mock audio stream"""
        self.stop()

    def _run_callback_loop(self):
        """Simulate audio callbacks at regular intervals"""
        callback_interval = self.blocksize / self.samplerate

        while not self._stop_event.is_set():
            start_time = time.time()

            # Create output buffer
            outdata = np.zeros((self.blocksize, self.channels), dtype=np.float32)

            # Call the audio callback
            try:
                self.callback(outdata, self.blocksize, None, None)
            except Exception as e:
                print(f"Error in mock audio callback: {e}")

            # Sleep to maintain timing
            elapsed = time.time() - start_time
            sleep_time = max(0, callback_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)


def query_devices():
    """Mock implementation of sounddevice.query_devices()"""
    return [
        {
            "name": "Mock Default Audio Device (WSL)",
            "channels": 2,
            "default_samplerate": 44100.0,
            "max_input_channels": 0,
            "max_output_channels": 2,
        },
        {
            "name": "Mock Secondary Audio Device (WSL)",
            "channels": 2,
            "default_samplerate": 48000.0,
            "max_input_channels": 0,
            "max_output_channels": 2,
        },
        {
            "name": "Mock Headphones Device (WSL)",
            "channels": 2,
            "default_samplerate": 44100.0,
            "max_input_channels": 0,
            "max_output_channels": 2,
        },
    ]


# Mock the sounddevice module interface
OutputStream = MockOutputStream
