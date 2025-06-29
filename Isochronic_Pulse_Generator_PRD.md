# Product Requirements Document: Isochronic Pulse Generator

## 1. Title
**Isochronic Pulse Generator**

---

## 2. Overview
The Isochronic Pulse Generator is a desktop application that allows users to configure and play isochronic audio pulses for personal use and enjoyment. Users can adjust pulse frequencies and carrier tones for both the left and right audio channels, either in sync or independently. The modulation uses a square wave for distinct, sharp pulse delivery.

---

## 3. Goals
- Allow users to input a pulse frequency (in Hz) and a carrier tone (in Hz).
- Allow users to configure the same settings for both audio channels or set values independently.
- Ensure sample-accurate synchronization between Left and Right channel playback.
- Use square wave modulation (fully on/off) to generate isochronic pulses.
- Provide the ability to play and pause the generated audio.

---

## 4. User Stories
- As a user, I want to input a frequency in Hz.
- As a user, I want to input a carrier tone in Hz.
- As a user, I want a separate set of inputs for the Left & Right Channels.
- As a user, I want to be able to set the same carrier tone and frequency for both channels, or input them separately.
- As a user, I want to be able to play and pause the generated audio.
- As a user, I expect the isochronic pulses to begin playing in each channel at the same time.

---

## 5. Scope

### In-Scope
- Generating audible isochronic pulses using square wave modulation at the configured tone and frequency.
- Generating separate pulses for Left and Right channels.
- Ensuring sample-accurate playback alignment between channels.
- Ability to play and pause the audio output.

### Out-of-Scope
- Audio export functionality.
- Sleep timers or any other feature enhancements.
- Visual waveform display (may be considered in future versions).

---

## 6. Features & Requirements (Bare Bones)

### 🔊 Feature: Pulse Generator Engine
- **Description:** Core engine responsible for generating isochronic pulses.
- **Requirements:**
  - Accepts input frequency (Hz) and carrier tone (Hz).
  - Uses square wave modulation (on/off gating).
  - Generates audio for both Left and Right channels.
  - Supports independent or shared configuration per channel.
  - Must ensure sample-accurate playback between both channels.

---

### 🎛️ Feature: Input Configuration Panel
- **Description:** UI interface for user input.
- **Requirements:**
  - Input fields for:
    - Left frequency (Hz)
    - Left carrier (Hz)
    - Right frequency (Hz)
    - Right carrier (Hz)
  - Checkbox or toggle to link channels (mirror values).
  - Basic validation (positive Hz values).

---

### ▶️ Feature: Playback Control
- **Description:** Simple interface for starting and stopping audio.
- **Requirements:**
  - Play and Pause buttons.
  - Playback starts both channels simultaneously (sample-accurate).
  - UI reflects playback state (e.g., button toggle or indicator).

---

## 7. Technical Requirements

### 7.1 Programming Language
- The application will be developed in **Python**.

### 7.2 Core Dependencies
The following libraries will be used:

| Dependency    | Purpose                                          |
|---------------|--------------------------------------------------|
| `uv`          | Package and dependency management                |
| `numpy`       | Generate carrier tones and pulse modulation data |
| `sounddevice` | Real-time stereo audio playback                  |
| `PySide6`     | GUI development using Qt framework for desktop   |

### 7.3 Audio Engine
- **Modulation Type:** Square wave (fully on/off)
- **Carrier Tone:** Pure tone generated using sine wave
- **Pulse Frequency:** Determines square wave gating interval
- **Channel Configuration:** Support for separate or mirrored L/R channel settings
- **Synchronization:** Left and Right audio channels must be sample-accurate

### 7.4 Platform
- Target platforms: **Windows**, **macOS**, and **Linux**
- Desktop-only; **no JavaScript** or browser-based runtime

### 7.5 Optional Tooling (Not Required for MVP)

| Tool         | Purpose                              |
|--------------|--------------------------------------|
| `matplotlib` | Waveform display                      |
| `pytest`     | Unit testing                          |
| `black`      | Code formatting                       |
| `pyinstaller` or `briefcase` | Application packaging |

