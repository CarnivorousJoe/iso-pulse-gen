# Use Windows Server Core LTSC 2019 as base
FROM mcr.microsoft.com/windows/servercore:ltsc2019

# Set working directory
WORKDIR C:\\workspace

# Install PowerShell Core (optional, for better scripting support)
RUN powershell -Command \
    Set-ExecutionPolicy Bypass -Scope Process -Force; \
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; \
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install Python 3.12 via Chocolatey
RUN choco install python312 -y --no-progress

# Install Git (needed for UV and Briefcase)
RUN choco install git -y --no-progress

# Install Visual C++ Build Tools (needed for some Python packages)
RUN choco install visualstudio2022buildtools -y --no-progress

# Refresh environment variables
RUN refreshenv

# Install UV package manager
RUN python -m pip install --upgrade pip && \
    python -m pip install uv

# Set environment variables
ENV PYTHONPATH=C:\\workspace\\src
ENV UV_CACHE_DIR=C:\\temp\\uv-cache

# Create cache directory
RUN mkdir C:\\temp\\uv-cache

# Expose environment for development
EXPOSE 8080

# Default command
CMD ["powershell"]