import numpy as np


class AudioGenerator:
    def __init__(self, sample_rate: int = 44100, volume: float = 0.4):
        self.sample_rate = sample_rate
        self.volume = max(0.0, min(1.0, volume))  # Clamp volume between 0.0 and 1.0
        self.phase_left = 0.0
        self.phase_right = 0.0
        self.pulse_phase_left = 0.0
        self.pulse_phase_right = 0.0

    def generate_stereo_frames(
        self,
        num_frames: int,
        left_carrier_freq: float,
        left_pulse_freq: float,
        right_carrier_freq: float,
        right_pulse_freq: float,
    ) -> np.ndarray:
        left_channel = self._generate_channel(
            num_frames, left_carrier_freq, left_pulse_freq, is_left=True
        )

        right_channel = self._generate_channel(
            num_frames, right_carrier_freq, right_pulse_freq, is_left=False
        )

        stereo_frames = np.column_stack((left_channel, right_channel))
        # Apply volume gain
        stereo_frames *= self.volume
        return stereo_frames.astype(np.float32)

    def _generate_channel(
        self, num_frames: int, carrier_freq: float, pulse_freq: float, is_left: bool
    ) -> np.ndarray:
        if carrier_freq <= 0 or pulse_freq <= 0:
            return np.zeros(num_frames)

        t = np.arange(num_frames) / self.sample_rate

        if is_left:
            carrier_phase = self.phase_left
            pulse_phase = self.pulse_phase_left
        else:
            carrier_phase = self.phase_right
            pulse_phase = self.pulse_phase_right

        carrier_phase_array = 2 * np.pi * carrier_freq * t + carrier_phase
        carrier_wave = np.sin(carrier_phase_array)

        pulse_phase_array = 2 * np.pi * pulse_freq * t + pulse_phase
        square_wave = (np.sin(pulse_phase_array) >= 0).astype(np.float32)

        modulated_wave = carrier_wave * square_wave

        new_carrier_phase = carrier_phase_array[-1] % (2 * np.pi)
        new_pulse_phase = pulse_phase_array[-1] % (2 * np.pi)

        if is_left:
            self.phase_left = new_carrier_phase
            self.pulse_phase_left = new_pulse_phase
        else:
            self.phase_right = new_carrier_phase
            self.pulse_phase_right = new_pulse_phase

        return modulated_wave

    def reset_phases(self):
        self.phase_left = 0.0
        self.phase_right = 0.0
        self.pulse_phase_left = 0.0
        self.pulse_phase_right = 0.0
    
    def set_volume(self, volume: float):
        """Set the master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
