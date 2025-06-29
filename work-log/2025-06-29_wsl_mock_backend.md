# Work Log: WSL Mock Audio Backend Implementation
**Date**: 2025-06-29
**Task**: Implement workaround for PortAudio limitations in WSL environments

## Problem Statement

The Isochronic Pulse Generator uses the `sounddevice` library for real-time audio playback, which depends on PortAudio. In WSL (Windows Subsystem for Linux) and other headless environments, PortAudio is not available, preventing the application from running and making GUI development/testing impossible.

## Solution Implemented

### 1. Mock Audio Backend (`src/iso_pulse_gen/audio/mock_backend.py`)
Created a complete mock implementation that simulates the `sounddevice` API:

- **MockOutputStream**: Simulates audio streaming with threaded callback execution
- **Timing Simulation**: Maintains proper callback intervals (blocksize/samplerate)
- **API Compatibility**: Implements the same interface as `sounddevice.OutputStream`
- **Thread Safety**: Proper start/stop handling with threading events

### 2. Automatic Backend Detection (`src/iso_pulse_gen/audio/stream_manager.py`)
Implemented graceful fallback mechanism:

```python
try:
    import sounddevice as sd
    AUDIO_BACKEND = "sounddevice"
except (OSError, ImportError):
    from . import mock_backend as sd
    AUDIO_BACKEND = "mock"
```

### 3. User Feedback
- Window title shows "(Mock Audio - No Sound)" when using mock backend
- Console message: "Note: Running with mock audio backend (no actual audio output)"
- Backend type accessible via `audio_manager.backend` property

## Testing Results

### GUI Functionality (WSL Environment)
✅ Application launches successfully  
✅ All input fields work correctly  
✅ Channel linking functions properly  
✅ Play/Pause button state changes  
✅ Parameter validation works  
✅ Mock audio callbacks execute without errors  

### Manual Audio Test
```bash
$ uv run python test_audio_manual.py
Audio backend: mock
Test 1: Default settings (440Hz carrier, 10Hz pulse)
Test 2: Different frequencies per channel  
Test 3: Low frequency pulse (2Hz)
Audio tests completed successfully!
```

## Technical Implementation Details

### Mock Stream Behavior
- Runs audio callbacks in separate daemon thread
- Maintains timing accuracy using sleep intervals
- Properly handles start/stop/close operations
- No actual audio output (silent operation)

### Backward Compatibility
- Zero changes required to existing audio generation code
- Same API surface as real sounddevice
- Automatic detection with no configuration needed
- Real audio works unchanged on systems with PortAudio

## Benefits

1. **Development**: GUI can be developed/tested in any environment
2. **CI/CD**: Automated testing possible in headless environments  
3. **Debugging**: Audio logic can be tested without hardware
4. **Cross-platform**: Works regardless of audio system availability

## Limitations

- No actual audio output in mock mode
- Cannot test real audio performance/latency
- Mock timing may not perfectly match real audio hardware

## Usage Notes

The application automatically detects the environment and chooses the appropriate backend. No user intervention required. For actual audio testing, run on a system with proper audio support (Windows, macOS, or Linux with PortAudio installed).

## Next Steps

The WSL workaround is complete and functional. The application can now be developed and tested in any environment while maintaining full compatibility with real audio systems.