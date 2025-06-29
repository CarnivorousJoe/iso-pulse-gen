# Windows DevContainer for Briefcase Builds

## ⚠️ Important Limitations

Based on research, there are significant limitations when using Windows containers for GUI application development:

### GUI Limitations in Windows Containers
- **No GUI Display**: Windows containers don't support interactive GUI sessions or RDP
- **No Desktop Environment**: LTSC2019 containers run in headless mode only
- **Build-Only Environment**: Suitable for building/packaging, not for running GUI apps

### Technical Challenges
- **Encoding Issues**: Known Python encoding problems in LTSC2019 containers
- **Visual Studio Requirements**: Briefcase may need full Visual Studio for some builds
- **Container Size**: Windows containers are significantly larger than Linux containers

## What This DevContainer Can Do

✅ **Build Environment**: Create Windows executables using Briefcase  
✅ **Package Creation**: Generate MSI installers and portable packages  
✅ **Dependency Management**: Install and manage Python packages  
✅ **Cross-Platform Development**: Build Windows apps from any host OS  

❌ **GUI Testing**: Cannot display or interact with GUI applications  
❌ **Audio Testing**: No audio device support in containers  
❌ **Interactive Development**: No visual debugging of GUI elements  

## Usage Instructions

### 1. Prerequisites
- Docker Desktop with Windows container support enabled
- VS Code with Dev Containers extension
- Windows 10/11 host or Windows Server

### 2. Build the Container
```bash
# Open project in VS Code
code .

# Command Palette -> "Dev Containers: Reopen in Container"
# This will build and start the Windows container
```

### 3. Build Windows Executable
```powershell
# Inside the container
uv sync
uv run briefcase create windows
uv run briefcase build windows  
uv run briefcase package windows
```

### 4. Access Build Artifacts
Built executables will be available in:
- `dist/windows/app/Isochronic Pulse Generator/`
- `dist/Isochronic_Pulse_Generator-0.1.0-windows.zip`

## Alternative Recommendation

For GUI development with testing capabilities, consider:

1. **Dual Approach**: 
   - Use Linux devcontainer for development (with mock audio)
   - Use Windows devcontainer only for final builds

2. **GitHub Actions**:
   - Automate Windows builds using GitHub's Windows runners
   - Build artifacts automatically on code changes

3. **Local Windows VM**:
   - Use Windows VM for development and testing
   - Full GUI and audio support available

## Container Build Process

The devcontainer will:
1. Install Python 3.12 via Chocolatey
2. Install Git and Visual Studio Build Tools
3. Set up UV package manager
4. Install project dependencies
5. Configure environment for Briefcase builds

## Troubleshooting

### If Build Fails
- Ensure Docker Desktop is running Windows containers (not Linux)
- Check Windows container compatibility with your host OS
- Verify Visual Studio Build Tools are properly installed

### Performance Notes
- Windows containers are resource-intensive
- Initial setup may take 15-30 minutes
- Consider using faster storage for better performance