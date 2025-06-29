# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Isochronic Pulse Generator is a desktop application that generates configurable audio pulses using square wave modulation. It supports independent left/right channel configuration with sample-accurate synchronization.

## Technical Stack

- **Language**: Python
- **Core Dependencies**:
  - `uv` - Package and Dependency management
  - `numpy` - Audio signal generation
  - `sounddevice` - Real-time audio playback
  - `PySide6` - Qt-based GUI framework
- **Target Platforms**: Windows, macOS, Linux

## Development Commands

This project uses UV for package management. Use these commands:

```bash
# Install dependencies with UV
uv sync

# Run the application (once implemented)
uv run python main.py
```

## Architecture Guidelines

### Audio Engine
- Use numpy to generate sine wave carrier tones
- Implement square wave modulation as on/off gating (not smooth transitions)
- Ensure sample-accurate synchronization between L/R channels
- Use sounddevice for real-time audio streaming with proper buffer management

### GUI Structure
- PySide6-based interface with:
  - Input fields for frequency (Hz) and carrier tone (Hz) per channel
  - Channel linking toggle to mirror L/R settings
  - Play/Pause controls with state management
- Validate all inputs for positive Hz values

### Key Technical Requirements
1. **Square Wave Modulation**: Must use sharp on/off transitions, not sine wave amplitude modulation
2. **Sample Accuracy**: Left and right channels must start and remain perfectly synchronized
3. **Real-time Playback**: Audio generation must be continuous without glitches or underruns
4. **Input Validation**: Frequency inputs must be positive numbers within reasonable audio ranges

## Project Status

Currently in initial development phase. Refer to `implementation_tasks.md` for the prioritized task list and `Isochronic_Pulse_Generator_PRD.md` for detailed requirements.