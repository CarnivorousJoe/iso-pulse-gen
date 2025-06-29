import numpy as np
from src.iso_pulse_gen.audio.generator import AudioGenerator


class TestAudioGenerator:
    def test_generator_initialization(self):
        generator = AudioGenerator(sample_rate=44100)
        assert generator.sample_rate == 44100
        assert generator.phase_left == 0.0
        assert generator.phase_right == 0.0
        assert generator.pulse_phase_left == 0.0
        assert generator.pulse_phase_right == 0.0

    def test_generate_stereo_frames_shape(self):
        generator = AudioGenerator(sample_rate=44100)
        frames = generator.generate_stereo_frames(
            num_frames=1024,
            left_carrier_freq=440.0,
            left_pulse_freq=10.0,
            right_carrier_freq=440.0,
            right_pulse_freq=10.0,
        )

        assert frames.shape == (1024, 2)
        assert frames.dtype == np.float32

    def test_zero_frequency_returns_silence(self):
        generator = AudioGenerator(sample_rate=44100)

        frames = generator.generate_stereo_frames(
            num_frames=100,
            left_carrier_freq=0.0,
            left_pulse_freq=10.0,
            right_carrier_freq=440.0,
            right_pulse_freq=0.0,
        )

        assert np.all(frames[:, 0] == 0)
        assert np.all(frames[:, 1] == 0)

    def test_phase_continuity(self):
        generator = AudioGenerator(sample_rate=44100)

        frames1 = generator.generate_stereo_frames(
            num_frames=100,
            left_carrier_freq=440.0,
            left_pulse_freq=10.0,
            right_carrier_freq=440.0,
            right_pulse_freq=10.0,
        )

        frames2 = generator.generate_stereo_frames(
            num_frames=100,
            left_carrier_freq=440.0,
            left_pulse_freq=10.0,
            right_carrier_freq=440.0,
            right_pulse_freq=10.0,
        )

        assert generator.phase_left != 0.0
        assert generator.phase_right != 0.0
        assert not np.array_equal(frames1[0], frames2[0])

    def test_square_wave_modulation(self):
        generator = AudioGenerator(sample_rate=1000)

        frames = generator.generate_stereo_frames(
            num_frames=100,
            left_carrier_freq=100.0,
            left_pulse_freq=10.0,
            right_carrier_freq=100.0,
            right_pulse_freq=10.0,
        )

        left_channel = frames[:, 0]
        non_zero_mask = left_channel != 0

        if np.any(non_zero_mask):
            zero_crossings = np.where(np.diff(np.sign(left_channel)))[0]
            assert len(zero_crossings) > 0

    def test_reset_phases(self):
        generator = AudioGenerator(sample_rate=44100)

        generator.generate_stereo_frames(
            num_frames=100,
            left_carrier_freq=440.0,
            left_pulse_freq=10.0,
            right_carrier_freq=440.0,
            right_pulse_freq=10.0,
        )

        assert generator.phase_left != 0.0
        assert generator.phase_right != 0.0

        generator.reset_phases()

        assert generator.phase_left == 0.0
        assert generator.phase_right == 0.0
        assert generator.pulse_phase_left == 0.0
        assert generator.pulse_phase_right == 0.0

    def test_independent_channels(self):
        generator = AudioGenerator(sample_rate=44100)

        frames = generator.generate_stereo_frames(
            num_frames=1000,
            left_carrier_freq=440.0,
            left_pulse_freq=10.0,
            right_carrier_freq=880.0,
            right_pulse_freq=20.0,
        )

        left_channel = frames[:, 0]
        right_channel = frames[:, 1]

        assert not np.array_equal(left_channel, right_channel)
