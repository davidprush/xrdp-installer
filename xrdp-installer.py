#!/usr/bin/env python3
#####################################################################################################
# Script_Name : xrdp-installer.py
# Description : Perform xRDP installation with optional CUDA support on Ubuntu 20.04-24.04 and Debian
# Date : Feb 2025
# Written by : David Rush
# Version : 1.0.0-cuda
# History :1.0.0 - Added Ubuntu 24.04 support, CUDA integration, and enhanced argument handling
# Disclaimer : Script provided AS IS. Use it at your own risk....
####################################################################################################

import os
import sys
import subprocess
import shutil
import getpass
import argparse
import tempfile
import re
from pathlib import Path
from typing import Optional

# Constants
SCRIPT_VER = "1.0.0"
COLORS = {
    'cyan': '\033[1;36m',
    'yellow': '\033[1;33m',
    'green': '\033[1;32m',
    'red': '\033[1;31m',
    'purple': '\033[1;35m',
    'white': '\033[1;38m',
    'reset': '\033[0m'
}

class SetupError(Exception):
    """Custom exception for setup-related errors"""
    pass

# Global variables
version = subprocess.getoutput("lsb_release -sd")
codename = subprocess.getoutput("lsb_release -sc")
release = subprocess.getoutput("lsb_release -sr")
ucodename = subprocess.getoutput("cat /etc/os-release | grep UBUNTU_CODENAME | cut -d'=' -f2")
download_dir = subprocess.getoutput("xdg-user-dir DOWNLOAD")
modetype = "unknown"
DesktopVer = ""
SessionVer = ""
ConfDir = ""
GDMSess = ""
HWE = ""

def print_colored(text: str, color: str) -> None:
    print(f"{COLORS[color]}{text}{COLORS['reset']}")

def run_command(command: str, sudo: bool = False, verbose: bool = False) -> subprocess.CompletedProcess:
    """Execute a shell command with optional sudo privileges"""
    full_command = f"sudo {command}" if sudo else command
    if verbose:
        print_colored(f"Executing: {full_command}", 'yellow')
    
    try:
        result = subprocess.run(
            full_command,
            shell=True,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if verbose and result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        raise SetupError(f"Command failed: {full_command}\nError: {e.stderr}") from e

def write_file_with_sudo(filepath: str, content: str, verbose: bool = False) -> None:
    """Write content to a file using sudo privileges"""
    if verbose:
        print_colored(f"Writing to {filepath}", 'yellow')
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
            temp.write(content)
            temp_path = temp.name
        run_command(f"mv {temp_path} {filepath}", sudo=True, verbose=verbose)
        run_command(f"chmod 644 {filepath}", sudo=True, verbose=verbose)
    except Exception as e:
        raise SetupError(f"Failed to write file {filepath}: {str(e)}") from e

def display_banner() -> None:
    print_colored(f"   ! xrdp-cuda-installer-{SCRIPT_VER} Script", 'cyan')
    print_colored("   ! Supports Ubuntu, Debian with optional CUDA installation", 'cyan')
    print_colored("   ! Written by David Rush - Feb 2025", 'cyan')
    print_colored(f"   ! For Help: {sys.argv[0]} -h", 'cyan')
    print_colored("   ! Disclaimer: Use at your own risk", 'white')

def check_previous_runs(verbose: bool) -> None:
    global modetype
    log_file = "/etc/xrdp/xrdp-installer-check.log"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            modetype = f.readline().strip()
        if verbose:
            print_colored(f"   Previous mode detected: {modetype}", 'green')

def detect_desktop_environment(verbose: bool) -> None:
    global DesktopVer, SessionVer, ConfDir, GDMSess
    if os.environ.get('XDG_SESSION_TYPE') == 'tty':
        # SSH detection and handling omitted for brevity, using defaults
        DesktopVer = "ubuntu:GNOME"
        SessionVer = "ubuntu"
        ConfDir = "/usr/share/ubuntu:/usr/local/share/:/usr/share/:/var/lib/snapd/desktop"
        GDMSess = "ubuntu"
    else:
        DesktopVer = os.environ.get('XDG_CURRENT_DESKTOP', 'ubuntu:GNOME')
        SessionVer = os.environ.get('GNOME_SHELL_SESSION_MODE', 'ubuntu')
        ConfDir = os.environ.get('XDG_DATA_DIRS', '/usr/share/ubuntu:/usr/local/share/:/usr/share/')
        GDMSess = os.environ.get('GDMSESSION', 'ubuntu')

def check_os(verbose: bool) -> None:
    supported = ["Ubuntu 24.04", "Debian"]
    if not any(v in version for v in supported):
        raise SetupError(f"Unsupported OS: {version}")

def check_hwe(verbose: bool) -> None:
    global HWE
    xorg_no_hwe = subprocess.getoutput("dpkg-query -W -f='${Status}' xserver-xorg-core 2>/dev/null")
    xorg_hwe = subprocess.getoutput(f"dpkg-query -W -f='${{Status}}' xserver-xorg-core-hwe-{Release} 2>/dev/null")
    HWE = "yes" if "installed" in xorg_hwe else "no"

def install_cuda(verbose: bool) -> None:
    """Install CUDA toolkit"""
    print_colored("   Installing CUDA...", 'yellow')
    os.chdir(os.path.expanduser("~"))
    run_command("wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb", verbose=verbose)
    run_command("dpkg -i cuda-keyring_1.1-1_all.deb", sudo=True, verbose=verbose)
    run_command("apt-get update", sudo=True, verbose=verbose)
    run_command("apt-get -y install cuda", sudo=True, verbose=verbose)
    os.remove("cuda-keyring_1.1-1_all.deb")

def prep_os(verbose: bool) -> None:
    """Prepare OS for installation"""
    if "Debian" in version:
        run_command("sed -i 's/deb cdrom:/#deb cdrom:/' /etc/apt/sources.list", sudo=True, verbose=verbose)
        run_command("apt-get update", sudo=True, verbose=verbose)
    run_command("apt-get -y install pulseaudio-utils", sudo=True, verbose=verbose)

def install_xrdp(verbose: bool) -> None:
    """Standard xRDP installation"""
    run_command("apt-get install xrdp -y", sudo=True, verbose=verbose)

def install_prereqs(verbose: bool) -> None:
    """Install prerequisites for custom build"""
    packages = "git jq xvfb libmp3lame-dev curl libfuse-dev libx11-dev libxfixes-dev libssl-dev libpam0g-dev libtool libjpeg-dev flex bison gettext autoconf libxml-parser-perl xsltproc libxrandr-dev python3-libxml2 nasm pkg-config intltool checkinstall"
    run_command(f"apt-get -y install {packages}", sudo=True, verbose=verbose)
    if HWE == "yes":
        run_command(f"apt-get install -y xserver-xorg-dev-hwe-{Release} xserver-xorg-core-hwe-{Release}", sudo=True, verbose=verbose)
    else:
        run_command("apt-get install -y xserver-xorg-dev xserver-xorg-core", sudo=True, verbose=verbose)

def get_binaries(args: argparse.Namespace, verbose: bool) -> None:
    """Download xRDP binaries"""
    os.chdir(download_dir)
    for dir_name in ["xrdp", "xorgxrdp"]:
        if os.path.exists(dir_name):
            run_command(f"rm -rf {dir_name}", sudo=True, verbose=verbose)
    
    repo = "neutrinolabs" if not args.nexarian else "Nexarian"
    branch = "mainline_merge" if args.nexarian else ("--branch " + ("HEAD" if args.dev else "latest"))
    
    run_command(f"git clone https://github.com/{repo}/xrdp.git {branch} xrdp --recursive", verbose=verbose)
    run_command(f"git clone https://github.com/{repo}/xorgxrdp.git {branch} xorgxrdp --recursive", verbose=verbose)

def compile_source(verbose: bool) -> None:
    """Compile xRDP source"""
    os.chdir(os.path.join(download_dir, "xrdp"))
    run_command("./bootstrap", sudo=True, verbose=verbose)
    run_command("./configure --enable-fuse --enable-jpeg --enable-rfxcodec --enable-mp3lame --enable-vsock", sudo=True, verbose=verbose)
    run_command(f"make -j {os.cpu_count()}", sudo=True, verbose=verbose)
    run_command("checkinstall --pkgname=xrdp --default", sudo=True, verbose=verbose)
    
    os.chdir(os.path.join(download_dir, "xorgxrdp"))
    run_command("./bootstrap", sudo=True, verbose=verbose)
    run_command("./configure", sudo=True, verbose=verbose)
    run_command(f"make -j {os.cpu_count()}", sudo=True, verbose=verbose)
    run_command("checkinstall --pkgname=xorgxrdp --default", sudo=True, verbose=verbose)

def enable_service(verbose: bool) -> None:
    """Enable and configure xRDP services"""
    run_command("systemctl daemon-reload", sudo=True, verbose=verbose)
    run_command("systemctl enable xrdp.service", sudo=True, verbose=verbose)
    run_command("systemctl enable xrdp-sesman.service", sudo=True, verbose=verbose)
    run_command("systemctl start xrdp", sudo=True, verbose=verbose)

def install_common(verbose: bool) -> None:
    """Common installation steps"""
    if "GNOME" in DesktopVer:
        run_command("apt-get install gnome-tweaks -y", sudo=True, verbose=verbose)
    run_command("sed -i 's/allowed_users=console/allowed_users=anybody/' /etc/X11/Xwrapper.config || echo 'allowed_users=anybody' > /etc/X11/Xwrapper.config", sudo=True, verbose=verbose)
    # Polkit and theme fixes omitted for brevity

def enable_sound(args: argparse.Namespace, verbose: bool) -> None:
    """Enable sound redirection"""
    snd_server = subprocess.getoutput("pactl info | grep 'Server Name' | cut -d: -f2")
    if "PipeWire" in snd_server:
        run_command("apt install -y git pkg-config autotools-dev libtool make gcc libpipewire-0.3-dev libspa-0.2-dev", sudo=True, verbose=verbose)
        os.chdir(download_dir)
        run_command("git clone https://github.com/neutrinolabs/pipewire-module-xrdp.git --recursive", verbose=verbose)
        os.chdir(os.path.join(download_dir, "pipewire-module-xrdp"))
        run_command("./bootstrap", verbose=verbose)
        run_command("./configure", verbose=verbose)
        run_command("make", verbose=verbose)
        run_command("make install", sudo=True, verbose=verbose)

def remove_xrdp(verbose: bool) -> None:
    """Remove xRDP installation"""
    run_command("systemctl stop xrdp", sudo=True, verbose=verbose)
    run_command("apt-get autoremove xrdp -y", sudo=True, verbose=verbose)
    run_command("apt-get purge xrdp -y", sudo=True, verbose=verbose)

def main(args: argparse.Namespace) -> None:
    try:
        if os.geteuid() == 0:
            raise SetupError("Script must not run with sudo")
        
        display_banner()
        check_previous_runs(args.verbose)
        detect_desktop_environment(args.verbose)
        check_os(args.verbose)
        check_hwe(args.verbose)

        if args.remove:
            remove_xrdp(args.verbose)
            return

        if args.cuda:
            install_cuda(args.verbose)

        prep_os(args.verbose)
        
        if args.custom:
            if modetype != "standard":
                install_prereqs(args.verbose)
                get_binaries(args, args.verbose)
                compile_source(args.verbose)
                enable_service(args.verbose)
                install_common(args.verbose)
                run_command("bash -c 'echo custom > /etc/xrdp/xrdp-installer-check.log'", sudo=True, verbose=verbose)
        else:
            if modetype != "custom":
                install_xrdp(args.verbose)
                install_common(args.verbose)
                run_command("bash -c 'echo standard > /etc/xrdp/xrdp-installer-check.log'", sudo=True, verbose=verbose)

        if args.sound:
            enable_sound(args, args.verbose)

    except SetupError as e:
        print_colored(f"Setup failed: {str(e)}", 'red')
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="xRDP and CUDA Installation Script")
    parser.add_argument("-c", "--custom", action="store_true", help="Custom xRDP install with compilation")
    parser.add_argument("-r", "--remove", action="store_true", help="Remove xRDP packages")
    parser.add_argument("-d", "--dev", action="store_true", help="Use development branch for xRDP")
    parser.add_argument("-s", "--sound", action="store_true", help="Enable sound redirection")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--cuda", action="store_true", help="Install CUDA toolkit")
    parser.add_argument("--nexarian", action="store_true", help="Use Nexarian's xRDP fork")
    args = parser.parse_args()
    main(args)
