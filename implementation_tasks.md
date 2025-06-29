# Isochronic Pulse Generator - Implementation Tasks

## High Priority Tasks (Core Functionality)

1. **Set up project structure and development environment** ✅ READY FOR REVIEW
   - Install Python, numpy, sounddevice, and PySide6
   - Configure project directory structure
   - Set up virtual environment

2. **Implement audio generation engine** ✅ READY FOR REVIEW
   - Create sine wave carrier tone generator with numpy
   - Support configurable frequency input

3. **Implement square wave modulation** ✅ READY FOR REVIEW
   - Create on/off gating mechanism for isochronic pulses
   - Ensure clean square wave transitions

4. **Implement stereo channel support** ✅ READY FOR REVIEW
   - Enable independent L/R channel audio generation
   - Support different frequencies/carriers per channel

5. **Implement sample-accurate synchronization** ✅ READY FOR REVIEW
   - Ensure left and right channels start simultaneously
   - Maintain phase alignment throughout playback

6. **Create audio playback system** ✅ READY FOR REVIEW
   - Use sounddevice for real-time streaming
   - Implement continuous audio buffer generation

7. **Connect GUI to audio engine** ✅ READY FOR REVIEW
   - Wire up inputs and controls to audio generation
   - Ensure responsive parameter updates

8. **Implement proper audio stream management** ✅ READY FOR REVIEW
   - Handle start/stop/cleanup operations
   - Prevent audio glitches and buffer underruns

## Medium Priority Tasks (User Interface)

9. **Design and implement GUI layout** ✅ READY FOR REVIEW
   - Create main window with PySide6
   - Design intuitive input panel layout

10. **Create input configuration panel** ✅ READY FOR REVIEW
    - Frequency input fields for L/R channels
    - Carrier tone input fields for L/R channels

11. **Implement channel linking feature** ✅ READY FOR REVIEW
    - Add checkbox/toggle to mirror L/R values
    - Synchronize inputs when linked

12. **Add input validation** ✅ READY FOR REVIEW
    - Ensure positive Hz values
    - Set reasonable frequency ranges

13. **Implement playback controls** ✅ READY FOR REVIEW
    - Create play/pause buttons
    - Update UI to reflect playback state

14. **Add error handling**
    - Handle audio device issues gracefully
    - Provide user feedback for invalid inputs

## URGENT: Audio Debug & Fix Tasks

**Issue**: Application connects to audio device but produces no sound output.

### Phase 1: Immediate Diagnosis (High Priority)

1. **Add audio callback logging to verify callback is being called** ✅ READY FOR REVIEW
   - Add debug prints in _audio_callback to confirm execution
   - Log callback frequency and timing

2. **Implement RMS level monitoring in callback to detect if signal contains audio** ✅ READY FOR REVIEW
   - Calculate RMS level of generated audio data
   - Log signal levels to verify non-zero audio generation

3. **Add volume/gain parameter to AudioGenerator (default 0.3-0.5)** ✅ READY FOR REVIEW
   - Add master volume control to scale output amplitude
   - Ensure signal is audible without clipping

4. **Add comprehensive stream error handling with specific PortAudio error messages** ✅ READY FOR REVIEW
   - Wrap stream operations with detailed exception handling
   - Log specific PortAudio error codes and messages

### Phase 2: Stream Validation (Medium Priority)

5. **Verify selected device supports stream parameters (sample rate, channels, format)**
   - Query device capabilities before stream creation
   - Validate compatibility with 44.1kHz, stereo, float32

6. **Add callback status monitoring and logging for underflow/overflow detection**
   - Monitor and log all callback status flags
   - Detect and report buffer underruns/overruns

7. **Add debug GUI controls for volume and signal monitoring**
   - Add volume slider to main window
   - Display real-time signal level meters

### Phase 3: Testing & Validation (Low Priority)

8. **Test with different volume levels and frequencies to isolate the issue**
   - Systematic testing across parameter ranges
   - Document working vs non-working configurations

9. **Add audio buffer validation to ensure proper data format**
   - Verify output buffer contains expected float32 values
   - Check for NaN, infinity, or out-of-range values

15. **Implement audio output device selection** ✅ READY FOR REVIEW
    - Add device enumeration and selection to AudioStreamManager
    - Create device selection UI in main window
    - Support default device and specific device selection
    - Handle device switching during playback

## Low Priority Tasks (Polish & Documentation)

16. **Test cross-platform compatibility**
    - Test on Windows
    - Test on macOS
    - Test on Linux

17. **Create basic documentation**
    - Write usage instructions
    - Document technical requirements
    - Add troubleshooting guide

## Implementation Notes

- Follow the PRD specifications closely
- Prioritize audio accuracy and synchronization
- Keep the UI simple and focused on core functionality
- Test audio generation thoroughly before GUI integration