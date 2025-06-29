# Windows Build Instructions

## Prerequisites

Building the Windows portable executable requires a **native Windows environment**. The build cannot be performed in WSL (Windows Subsystem for Linux).

### Required Software on Windows:
- Python 3.12 or later
- Git
- UV package manager (or pip)

## Build Process

### 1. Clone and Setup (on Windows)
```cmd
git clone <repository-url>
cd iso-pulse-gen
```

### 2. Install Dependencies
```cmd
# If using UV (recommended)
uv sync

# Or with pip
pip install -e .
pip install briefcase
```

### 3. Create Build Environment
```cmd
uv run briefcase create windows
```
This will:
- Set up a Python environment for Windows packaging
- Download and configure build tools
- Prepare the application structure

### 4. Build the Application
```cmd
uv run briefcase build windows
```
This creates the portable executable with all dependencies bundled.

### 5. Package for Distribution
```cmd
uv run briefcase package windows
```
This creates a ZIP file containing the portable application.

## Build Output

The build process will create:
- **Executable**: `dist/Isochronic Pulse Generator.exe`
- **Portable Package**: `dist/Isochronic_Pulse_Generator-0.1.0-windows.zip`

## Distribution

The ZIP file contains:
- The main executable
- All required Python libraries
- PySide6 Qt libraries
- Audio libraries (sounddevice, PortAudio)
- All dependencies bundled

Users can:
1. Extract the ZIP to any folder
2. Run `Isochronic Pulse Generator.exe` directly
3. No installation or admin rights required

## Troubleshooting

### Build Fails
- Ensure you're running on native Windows (not WSL)
- Check Python version is 3.12+
- Verify all dependencies are installed

### Audio Issues
- On Windows, PortAudio is included with sounddevice
- The app will automatically use real audio (not mock)
- Test with different audio devices if needed

### Performance
- The portable executable is larger due to bundled libraries
- First startup may be slower as libraries load
- Subsequent runs will be faster

## Development Workflow

For development on Windows:
```cmd
# Test in development mode
uv run briefcase dev

# Quick build and test
uv run briefcase build windows
uv run briefcase run windows

# Full package creation
uv run briefcase package windows
```

## File Structure

After successful build:
```
dist/
├── Isochronic_Pulse_Generator-0.1.0-windows.zip  # Portable package
└── windows/
    └── app/
        └── Isochronic Pulse Generator/
            ├── Isochronic Pulse Generator.exe    # Main executable
            ├── lib/                               # Python libraries
            ├── Qt6/                               # PySide6 libraries
            └── audio/                             # Audio libraries
```