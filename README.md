# Engel CC300 Remote View (Windows Script)

A Windows batch script that automates remote VNC connections to Engel CC300 Control Panels on injection molding machines (IMM), with optional SSH tunneling support.

## Prerequisites

### Required Software

- **VNC Viewer** - Choose one (TigerVNC recommended):
  - **[TigerVNC](https://sourceforge.net/projects/tigervnc/)** ⭐ Recommended - Open source, GPL license
  - [UltraVNC](https://uvnc.com/downloads/ultravnc.html) - Open source, GPL license
  - [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/) - Free for personal use
  
- **PuTTY** - Only required for newer CC300 versions needing SSH tunnel
  - Download: [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) (Open source, MIT license)

### System Requirements

- Windows 7 or later (Windows 10/11 recommended)
- Network access to CC300 controllers

## Installation

1. Download the script:
   [`cc300remoteview.bat`](cc300remoteview.bat)

2. Install TigerVNC:
   - Download from [tigervnc.org](https://sourceforge.net/projects/tigervnc/)
   - For Windows 10/11 64-bit, download `vncviewer64-[version].exe`
   - Install to default location: `C:\Program Files\TigerVNC`

3. Install PuTTY (if using SSH tunnel):
   - Download from [putty.org](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)
   - Install to default location: `C:\Program Files\PuTTY`

4. Configure the script (see Configuration section below)

## Quick Start

1. Double-click `cc300remoteview.bat`
2. Enter the CC300 machine IP address
3. Choose whether to use SSH tunnel (Y/N)
   - **N** for older CC300 versions (direct VNC)
   - **Y** for newer CC300 versions (requires SSH)
4. VNC Viewer opens automatically

### Example Session

```
=========================================
  Engel CC300 Remote View
  Author: Jorge Santos (JorgeS15)
  Version: 1.9 (07/10/2025)

  github.com/JorgeS15/cc300remoteview
=========================================

Enter the complete machine IP address: 10.201.52.27
Is it necessary to establish an SSH tunnel? (Y/N): Y

Establishing SSH tunnel... (port: 10061)
Waiting for SSH tunnel establishment (3 seconds)...

Opening VNC Viewer through tunnel...
```

## Configuration

Edit the script settings section to match your environment:

```batch
REM =========================================
REM SETTINGS
REM =========================================
set "USE_IP_BASE=FALSE"      # Set to TRUE to enter only last octet
set "IP_BASE=10.201.52"      # Base IP (used when USE_IP_BASE=TRUE)

set "SSH_USER=changeme"      # Your SSH username
set "SSH_PASSWORD=changeme"  # Your SSH password

set "SSH_LOCAL_PORT=10061"   # Local port for SSH tunnel
set "SSH_REMOTE_PORT=5900"   # Remote VNC port
set "VNC_PORT=5900"          # VNC port for direct connection
set "SSH_TIMEOUT=3"          # Seconds to wait for tunnel
set "CLEANUP_TIMEOUT=2"      # Seconds before closing tunnel

set "PUTTY_PATH=C:\Program Files\PuTTY"
set "VNC_PATH=C:\Program Files\TigerVNC"
```

### Configuration Options

#### IP Address Mode

- **`USE_IP_BASE=FALSE`** (default): Enter complete IP address
  - Example: `192.168.1.100`
  
- **`USE_IP_BASE=TRUE`**: Enter only last octet
  - Set `IP_BASE` to your network prefix (e.g., `10.201.52`)
  - Enter only last number (e.g., `27` for `10.201.52.27`)

#### SSH Credentials

⚠️ **Important**: Replace `changeme` with your actual credentials before using SSH tunnel:

```batch
set "SSH_USER=your_username"
set "SSH_PASSWORD=your_password"
```

#### VNC Viewer Path

The script supports multiple VNC viewers. Update `VNC_PATH` if needed:

```batch
REM TigerVNC (default)
set "VNC_PATH=C:\Program Files\TigerVNC"

REM Alternative: UltraVNC
set "VNC_PATH=C:\Program Files\uvnc bvba\UltraVNC"

REM Alternative: RealVNC
set "VNC_PATH=C:\Program Files\RealVNC\VNC Viewer"
```

All viewers use `vncviewer.exe` as the executable name.

## CC300 Version Compatibility

The connection method depends on your CC300 control panel version:

### Older CC300 Versions
- **Connection**: Direct VNC (port 5900)
- **SSH tunnel**: Not required (select **N**)
- **Prerequisites**: VNC Viewer only

### Newer CC300 Versions  
- **Connection**: SSH tunnel required
- **SSH tunnel**: Required (select **Y**)
- **Prerequisites**: VNC Viewer + PuTTY

> **💡 Tip**: Not sure which version you have? Try direct connection first (select N). If it fails, try with SSH tunnel (select Y).


## Security Warning

- Restrict file permissions
- Keep the script secure

## Troubleshooting

- **Can't find VNC/PuTTY**: Update the paths in the script's `PUTTY_PATH` and `VNC_PATH` variables
- **SSH tunnel fails**: Check credentials and increase `SSH_TIMEOUT` in the script
- **Direct connection fails**: Your CC300 version likely requires SSH tunnel

## Author

**Jorge Santos** (JorgeS15)  
GitHub: [@JorgeS15](https://github.com/JorgeS15)

## Contributing

Issues and pull requests welcome!

## Disclaimer

This is an unofficial tool. Not affiliated with Engel Austria GmbH.
