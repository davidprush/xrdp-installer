# xRDP-CUDA Installer Script

This script automates the installation of xRDP (Remote Desktop Protocol) with optional CUDA toolkit support on Ubuntu (20.04-24.04) and Debian systems. It provides both standard and custom installation modes for xRDP, sound redirection capabilities, and CUDA integration for GPU-accelerated computing.

## Features

- **xRDP Installation**: Supports both standard (package-based) and custom (source-compiled) installations
- **CUDA Support**: Optional installation of NVIDIA CUDA toolkit
- **Sound Redirection**: Enables audio support via PipeWire or PulseAudio
- **Flexible Options**: Multiple command-line flags for customization
- **Verbose Output**: Detailed logging for troubleshooting
- **Desktop Environment Detection**: Automatically configures for various desktop environments
- **Error Handling**: Robust exception management with clear feedback

## Version

- **Current Version**: 1.0.0-cuda
- **Release Date**: February 2025

## Prerequisites

- Ubuntu 24.04, or Debian (10/11/12)
- Standard user account (script must not run with sudo initially)
- Internet connection for package downloads
- For CUDA: NVIDIA GPU and compatible drivers

## Installation

1. **Download the Script**:

   ```bash
   wget https://github.com/davidprush/xrdp-installer/raw/refs/heads/main/xrdp-installer.py
   ```

2. **Make it Executable**:

   ```bash
    chmod +x xrdp-installer.py

3. **Run the Script**:
    See usage examples below.

## Usage

Run the script with Python 3 and optional arguments:

```bash
python3 xrdp-installer.py [OPTIONS]
```

### Command-Line Options

Flag | Long Form | Description
-c | --custom | Perform custom xRDP installation (compiled from source)
-r | --remove | Remove xRDP packages and configuration
-d | --dev | Use development branch for xRDP (with --custom)
-s | --sound | Enable sound redirection (PipeWire or PulseAudio)
-v | --verbose | Enable detailed output for debugging
 | --cuda | Install NVIDIA CUDA toolkit
 | --nexarian | Use Nexarian's xRDP fork instead of neutrinolabs

### Examples

1. Basic xRDP Installation:
bash
python3 xrdp-installer.py
2. Custom xRDP with Sound and CUDA:
bash
python3 xrdp-installer.py -c -s --cuda -v
3. Remove xRDP:
bash
python3 xrdp-installer.py -r
4. Development Build with Nexarian Fork:
bash
python3 xrdp-installer.py -c -d --nexarian

### Notes

- Sudo: The script will prompt for sudo password when needed. Do not run with sudo initially.
- Sound: After enabling sound, a full system reboot is recommended.
- CUDA: Ensure NVIDIA drivers are installed prior to CUDA installation.
- Previous Installs: The script detects prior installations and prevents mixing standard/custom modes.

### Troubleshooting

- Verbose Mode: Use -v to see detailed output.
- Logs: Check /etc/xrdp/xrdp-installer-check.log for installation mode history.
- Errors: Common issues include missing dependencies or unsupported OS versions.

### Disclaimer

This script is provided AS IS. Use at your own risk. The authors are not responsible for any damage or data loss resulting from its use.

### License

This project is licensed under the MIT License - see the LICENSE file for details.

#### Customization Notes

- Replace `https://github.com/davidprush/xrdp-installer/raw/refs/heads/main/xrdp-installer.py` with the actual download URL if available.
- Add a `LICENSE` file if you choose to include one (e.g., MIT License text).
- Expand the "Troubleshooting" section with specific known issues as they arise.
- Update the "Website" link if you have a specific page for this script.

This README provides clear instructions, usage examples, and essential information for users of the `xrdp-installer.py` script.
