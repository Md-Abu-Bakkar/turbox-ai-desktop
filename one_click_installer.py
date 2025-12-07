#!/usr/bin/env python3
# ==============================================================================
# TurboX Desktop OS - Ultimate One-Click Installer
# Complete System Installation from GitHub Repository
# ==============================================================================

import os
import sys
import subprocess
import requests
import zipfile
import tarfile
import shutil
import json
import time
from pathlib import Path

class TurboXInstaller:
    """Complete one-command installer for TurboX Desktop OS"""
    
    def __init__(self):
        self.home_dir = str(Path.home())
        self.turboX_dir = os.path.join(self.home_dir, '.turboX')
        self.install_dir = os.path.join(self.home_dir, 'turboX-ai-desktop')
        
        # GitHub repository
        self.github_repo = "https://github.com/Md-Abu-Bakkar/turbox-ai-desktop.git"
        self.github_raw = "https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main"
        
        # Colors for output
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.BLUE = '\033[94m'
        self.BOLD = '\033[1m'
        self.END = '\033[0m'
        
        # System info
        self.is_termux = 'com.termux' in self.home_dir
        self.is_android = self.is_termux
        self.is_linux = sys.platform.startswith('linux') and not self.is_android
        self.is_windows = sys.platform.startswith('win')
        self.is_mac = sys.platform.startswith('darwin')
    
    def print_banner(self):
        """Display installation banner"""
        banner = f"""
{self.BOLD}{self.BLUE}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  ████████╗██╗   ██╗██████╗ ██████╗  ██████╗ ██╗  ██╗        ║
║  ╚══██╔══╝██║   ██║██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝        ║
║     ██║   ██║   ██║██████╔╝██████╔╝██║   ██║ ╚███╔╝         ║
║     ██║   ██║   ██║██╔══██╗██╔══██╗██║   ██║ ██╔██╗         ║
║     ██║   ╚██████╔╝██║  ██║██████╔╝╚██████╔╝██╔╝ ██╗        ║
║     ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝        ║
║                                                              ║
║                Desktop OS + AI Automation Suite              ║
║                  Complete One-Click Installer                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{self.END}
        """
        print(banner)
        
        print(f"{self.BOLD}📋 System Detection:{self.END}")
        if self.is_termux:
            print(f"  • Platform: {self.GREEN}Android (Termux){self.END}")
        elif self.is_linux:
            print(f"  • Platform: {self.GREEN}Linux Desktop{self.END}")
        elif self.is_windows:
            print(f"  • Platform: {self.GREEN}Windows{self.END}")
        elif self.is_mac:
            print(f"  • Platform: {self.GREEN}macOS{self.END}")
        
        print(f"  • Home Directory: {self.turboX_dir}")
        print()
    
    def check_requirements(self):
        """Check system requirements"""
        print(f"{self.BOLD}🔍 Checking system requirements...{self.END}")
        
        requirements_met = True
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
            print(f"{self.RED}❌ Python 3.7+ required (found {python_version.major}.{python_version.minor}){self.END}")
            requirements_met = False
        else:
            print(f"{self.GREEN}✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}{self.END}")
        
        # Check for git
        try:
            subprocess.run(['git', '--version'], check=True, capture_output=True)
            print(f"{self.GREEN}✅ Git installed{self.END}")
        except:
            print(f"{self.YELLOW}⚠️ Git not found (will try alternative download){self.END}")
        
        # Check disk space (approximate)
        try:
            stat = os.statvfs(self.home_dir)
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            if free_gb < 2:
                print(f"{self.YELLOW}⚠️ Low disk space: {free_gb:.1f}GB free (2GB recommended){self.END}")
            else:
                print(f"{self.GREEN}✅ Disk space: {free_gb:.1f}GB free{self.END}")
        except:
            pass
        
        return requirements_met
    
    def install_termux_packages(self):
        """Install required packages for Termux"""
        print(f"\n{self.BOLD}📦 Installing Termux packages...{self.END}")
        
        packages = [
            'git', 'python', 'nodejs', 'wget', 'curl', 'unzip',
            'x11-repo', 'tur-repo', 'termux-x11', 'pulseaudio',
            'openbox', 'obconf', 'tint2', 'pcmanfm', 'xfce4-terminal',
            'mousepad', 'firefox', 'chromium'
        ]
        
        try:
            # Update package lists
            print("Updating package lists...")
            subprocess.run(['pkg', 'update', '-y'], check=True)
            subprocess.run(['pkg', 'upgrade', '-y'], check=True)
            
            # Install packages
            print("Installing core packages...")
            for pkg in packages:
                print(f"  Installing {pkg}...")
                try:
                    subprocess.run(['pkg', 'install', '-y', pkg], check=True)
                except subprocess.CalledProcessError:
                    print(f"{self.YELLOW}  Warning: Failed to install {pkg}{self.END}")
            
            # Install Python packages
            print("Installing Python packages...")
            python_packages = ['requests', 'pyqt5', 'psutil', 'pillow']
            for pkg in python_packages:
                subprocess.run([sys.executable, '-m', 'pip', 'install', pkg], check=True)
            
            return True
            
        except Exception as e:
            print(f"{self.RED}❌ Package installation failed: {e}{self.END}")
            return False
    
    def install_linux_packages(self):
        """Install required packages for Linux"""
        print(f"\n{self.BOLD}📦 Installing Linux packages...{self.END}")
        
        # Detect package manager
        try:
            if shutil.which('apt'):
                # Debian/Ubuntu
                packages = [
                    'git', 'python3', 'python3-pip', 'python3-pyqt5',
                    'python3-requests', 'python3-psutil', 'python3-pil',
                    'nodejs', 'npm', 'wget', 'curl', 'unzip',
                    'openbox', 'obconf', 'tint2', 'pcmanfm', 'xfce4-terminal',
                    'mousepad', 'firefox', 'chromium-browser'
                ]
                
                subprocess.run(['sudo', 'apt', 'update'], check=True)
                subprocess.run(['sudo', 'apt', 'install', '-y'] + packages, check=True)
                
            elif shutil.which('dnf'):
                # Fedora/RHEL
                packages = [
                    'git', 'python3', 'python3-pip', 'python3-qt5',
                    'python3-requests', 'python3-psutil', 'python3-pillow',
                    'nodejs', 'npm', 'wget', 'curl', 'unzip',
                    'openbox', 'obconf', 'tint2', 'pcmanfm', 'xfce4-terminal',
                    'mousepad', 'firefox', 'chromium'
                ]
                
                subprocess.run(['sudo', 'dnf', 'install', '-y'] + packages, check=True)
                
            elif shutil.which('pacman'):
                # Arch Linux
                packages = [
                    'git', 'python', 'python-pip', 'python-pyqt5',
                    'python-requests', 'python-psutil', 'python-pillow',
                    'nodejs', 'npm', 'wget', 'curl', 'unzip',
                    'openbox', 'obconf', 'tint2', 'pcmanfm', 'xfce4-terminal',
                    'mousepad', 'firefox', 'chromium'
                ]
                
                subprocess.run(['sudo', 'pacman', '-S', '--noconfirm'] + packages, check=True)
            
            return True
            
        except Exception as e:
            print(f"{self.YELLOW}⚠️ Package installation warning: {e}{self.END}")
            print("Continuing with basic installation...")
            return True
    
    def download_from_github(self):
        """Download TurboX from GitHub repository"""
        print(f"\n{self.BOLD}📥 Downloading TurboX Desktop OS...{self.END}")
        
        # Create installation directory
        os.makedirs(self.install_dir, exist_ok=True)
        
        try:
            # Try git clone first
            print("Cloning repository from GitHub...")
            subprocess.run(['git', 'clone', self.github_repo, self.install_dir], 
                         check=True, capture_output=True)
            print(f"{self.GREEN}✅ Repository cloned successfully{self.END}")
            return True
            
        except:
            # Fallback: Download ZIP
            print("Git clone failed, downloading ZIP...")
            try:
                zip_url = "https://github.com/Md-Abu-Bakkar/turbox-ai-desktop/archive/refs/heads/main.zip"
                zip_path = os.path.join(self.home_dir, 'turboX.zip')
                
                # Download ZIP
                response = requests.get(zip_url, stream=True)
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract ZIP
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.home_dir)
                
                # Move files
                extracted_dir = os.path.join(self.home_dir, 'turbox-ai-desktop-main')
                if os.path.exists(self.install_dir):
                    shutil.rmtree(self.install_dir)
                shutil.move(extracted_dir, self.install_dir)
                
                # Cleanup
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                
                print(f"{self.GREEN}✅ Downloaded and extracted successfully{self.END}")
                return True
                
            except Exception as e:
                print(f"{self.RED}❌ Download failed: {e}{self.END}")
                return False
    
    def setup_directories(self):
        """Setup necessary directories"""
        print(f"\n{self.BOLD}📁 Setting up directories...{self.END}")
        
        directories = [
            self.turboX_dir,
            os.path.join(self.turboX_dir, 'config'),
            os.path.join(self.turboX_dir, 'scripts'),
            os.path.join(self.turboX_dir, 'tools'),
            os.path.join(self.turboX_dir, 'data'),
            os.path.join(self.turboX_dir, 'logs'),
            os.path.join(self.turboX_dir, 'exports'),
            os.path.join(self.home_dir, 'Desktop'),
            os.path.join(self.home_dir, 'Documents'),
            os.path.join(self.home_dir, 'Downloads'),
            os.path.join(self.home_dir, 'Pictures')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"  Created: {directory}")
        
        return True
    
    def copy_files(self):
        """Copy files from installation directory to system"""
        print(f"\n{self.BOLD}📄 Copying system files...{self.END}")
        
        try:
            # Copy core files
            files_to_copy = [
                ('installer.sh', 'scripts/installer.sh'),
                ('core_manager.py', 'scripts/core_manager.py'),
                ('desktop_launcher.py', 'scripts/desktop_launcher.py'),
                ('window_manager.py', 'scripts/window_manager.py'),
                ('api_tester.py', 'tools/api_tester.py'),
                ('sms_panel.py', 'tools/sms_panel.py'),
                ('socket_bridge.py', 'scripts/socket_bridge.py'),
                ('session_manager.py', 'scripts/session_manager.py'),
                ('automation_controller.py', 'scripts/automation_controller.py'),
                ('one_click_installer.py', 'scripts/one_click_installer.py')
            ]
            
            for src_name, dest_name in files_to_copy:
                src = os.path.join(self.install_dir, src_name)
                dest = os.path.join(self.turboX_dir, dest_name)
                
                if os.path.exists(src):
                    shutil.copy2(src, dest)
                    print(f"  Copied: {src_name} → {dest_name}")
                else:
                    print(f"{self.YELLOW}  Warning: {src_name} not found{self.END}")
            
            # Copy browser extension
            extension_src = os.path.join(self.install_dir, 'browser_extension')
            extension_dest = os.path.join(self.turboX_dir, 'browser_extension')
            
            if os.path.exists(extension_src):
                if os.path.exists(extension_dest):
                    shutil.rmtree(extension_dest)
                shutil.copytree(extension_src, extension_dest)
                print(f"  Copied: browser_extension/")
            
            return True
            
        except Exception as e:
            print(f"{self.RED}❌ File copy failed: {e}{self.END}")
            return False
    
    def create_configuration(self):
        """Create system configuration files"""
        print(f"\n{self.BOLD}⚙️ Creating configuration...{self.END}")
        
        try:
            # Create system.json
            system_config = {
                "system": {
                    "version": "1.0.0",
                    "install_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "platform": "termux" if self.is_termux else sys.platform,
                    "home_dir": self.home_dir
                },
                "desktop": {
                    "theme": "windows-dark",
                    "taskbar_visible": True,
                    "auto_start": True,
                    "window_manager": "openbox"
                },
                "automation": {
                    "auto_launch_tools": True,
                    "auto_solve_captcha": True,
                    "auto_manage_sessions": True,
                    "auto_export": False
                },
                "browser": {
                    "extension_installed": False,
                    "socket_port": 8765,
                    "auto_connect": True
                }
            }
            
            config_file = os.path.join(self.turboX_dir, 'config', 'system.json')
            with open(config_file, 'w') as f:
                json.dump(system_config, f, indent=2)
            print(f"  Created: system.json")
            
            # Create start-desktop.sh
            start_script = f'''#!/bin/bash
# TurboX Desktop Startup Script
# Generated on {time.strftime("%Y-%m-%d %H:%M:%S")}

export HOME="{self.home_dir}"
export DISPLAY=:0
export PULSE_SERVER=127.0.0.1

echo "Starting TurboX Desktop OS..."

# Start X server if not running
if ! pgrep -x "termux-x11" > /dev/null; then
    echo "Starting X11 server..."
    termux-x11 :0 &
    sleep 3
fi

# Start window manager
echo "Starting Openbox..."
openbox --config-file {self.turboX_dir}/config/openbox.xml &

# Start taskbar
echo "Starting taskbar..."
tint2 -c {self.turboX_dir}/config/tint2rc &

# Start file manager
echo "Starting file manager..."
pcmanfm --desktop &

# Start TurboX core services
echo "Starting core manager..."
python {self.turboX_dir}/scripts/core_manager.py &

echo "TurboX Desktop started successfully!"
echo "Run 'python {self.turboX_dir}/scripts/desktop_launcher.py' to open application launcher"
'''
            
            start_file = os.path.join(self.turboX_dir, 'scripts', 'start-desktop.sh')
            with open(start_file, 'w') as f:
                f.write(start_script)
            
            # Make executable
            os.chmod(start_file, 0o755)
            print(f"  Created: start-desktop.sh")
            
            # Create autostart
            autostart_file = os.path.join(self.turboX_dir, 'autostart')
            with open(autostart_file, 'w') as f:
                f.write('1')
            print(f"  Created: autostart")
            
            return True
            
        except Exception as e:
            print(f"{self.RED}❌ Configuration failed: {e}{self.END}")
            return False
    
    def create_openbox_config(self):
        """Create Openbox window manager configuration"""
        print(f"\n{self.BOLD}🪟 Creating window manager config...{self.END}")
        
        try:
            # Openbox configuration
            openbox_config = '''<?xml version="1.0" encoding="UTF-8"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <resistance>
    <strength>10</strength>
    <screen_edge_strength>20</screen_edge_strength>
  </resistance>
  <focus>
    <focusNew>yes</focusNew>
    <followMouse>no</followMouse>
    <focusLast>yes</focusLast>
  </focus>
  <placement>
    <policy>Smart</policy>
    <center>yes</center>
    <monitor>Primary</monitor>
  </placement>
  <theme>
    <name>Clearlooks</name>
    <titleLayout>LIMC</titleLayout>
  </theme>
  <keyboard>
    <keybind key="W-t">
      <action name="Execute">
        <command>xfce4-terminal</command>
      </action>
    </keybind>
    <keybind key="W-f">
      <action name="Execute">
        <command>pcmanfm</command>
      </action>
    </keybind>
    <keybind key="W-a">
      <action name="Execute">
        <command>python ''' + os.path.join(self.turboX_dir, 'scripts', 'desktop_launcher.py') + '''</command>
      </action>
    </keybind>
    <keybind key="W-s">
      <action name="Execute">
        <command>python ''' + os.path.join(self.turboX_dir, 'scripts', 'socket_bridge.py') + '''</command>
      </action>
    </keybind>
    <keybind key="W-q">
      <action name="Exit">
        <prompt>no</prompt>
      </action>
    </keybind>
  </keyboard>
  <mouse>
    <dragThreshold>8</dragThreshold>
    <doubleClickTime>500</doubleClickTime>
    <context name="Frame">
      <mousebind button="A-Left" action="Press">
        <action name="Focus"/>
        <action name="Raise"/>
      </mousebind>
      <mousebind button="A-Left" action="Click">
        <action name="Unshade"/>
      </mousebind>
      <mousebind button="A-Left" action="Drag">
        <action name="Move"/>
      </mousebind>
    </context>
  </mouse>
</openbox_config>'''
            
            openbox_file = os.path.join(self.turboX_dir, 'config', 'openbox.xml')
            with open(openbox_file, 'w') as f:
                f.write(openbox_config)
            print(f"  Created: openbox.xml")
            
            # Tint2 taskbar configuration
            tint2_config = '''# TurboX Taskbar Configuration
panel_monitor = all
panel_position = bottom center horizontal
panel_size = 100% 40
panel_margin = 0 0
panel_padding = 5 0
panel_dock = 0
wm_menu = 1
panel_background_id = 1
panel_items = TSC

# Taskbar
task_icon = 1
task_text = 1
task_centered = 1
task_maximum_size = 150 35

# System tray
systray = 1
systray_padding = 5 0 5
systray_sort = right2left

# Clock
time1_format = %H:%M
time2_format = %d %b
clock_font_color = #ffffff 100
clock_padding = 5 0

# Battery (for mobile)
battery = 0
battery_low_status = 20
battery_low_cmd = notify-send "Battery low"

# Custom launchers
launcher_item_app = xfce4-terminal
launcher_icon_theme = Adwaita
launcher_tooltip = 1'''
            
            tint2_file = os.path.join(self.turboX_dir, 'config', 'tint2rc')
            with open(tint2_file, 'w') as f:
                f.write(tint2_config)
            print(f"  Created: tint2rc")
            
            return True
            
        except Exception as e:
            print(f"{self.RED}❌ WM config failed: {e}{self.END}")
            return False
    
    def create_desktop_shortcuts(self):
        """Create desktop shortcuts for applications"""
        print(f"\n{self.BOLD}🚀 Creating desktop shortcuts...{self.END}")
        
        try:
            desktop_dir = os.path.join(self.home_dir, 'Desktop')
            
            # TurboX Launcher shortcut
            launcher_shortcut = f'''[Desktop Entry]
Name=TurboX Launcher
Comment=Launch TurboX Applications
Exec=python {os.path.join(self.turboX_dir, 'scripts', 'desktop_launcher.py')}
Icon=applications-system
Terminal=false
Type=Application
Categories=System;Utility;'''
            
            with open(os.path.join(desktop_dir, 'TurboX Launcher.desktop'), 'w') as f:
                f.write(launcher_shortcut)
            print(f"  Created: TurboX Launcher.desktop")
            
            # API Tester shortcut
            api_tester_shortcut = f'''[Desktop Entry]
Name=API Tester
Comment=Test API endpoints
Exec=python {os.path.join(self.turboX_dir, 'tools', 'api_tester.py')}
Icon=network-server
Terminal=false
Type=Application
Categories=Development;Network;'''
            
            with open(os.path.join(desktop_dir, 'API Tester.desktop'), 'w') as f:
                f.write(api_tester_shortcut)
            print(f"  Created: API Tester.desktop")
            
            # SMS Panel shortcut
            sms_panel_shortcut = f'''[Desktop Entry]
Name=SMS Panel
Comment=SMS Data Collection
Exec=python {os.path.join(self.turboX_dir, 'tools', 'sms_panel.py')}
Icon=phone
Terminal=false
Type=Application
Categories=Network;Utility;'''
            
            with open(os.path.join(desktop_dir, 'SMS Panel.desktop'), 'w') as f:
                f.write(sms_panel_shortcut)
            print(f"  Created: SMS Panel.desktop")
            
            # Make executable
            for file in os.listdir(desktop_dir):
                if file.endswith('.desktop'):
                    os.chmod(os.path.join(desktop_dir, file), 0o755)
            
            return True
            
        except Exception as e:
            print(f"{self.YELLOW}⚠️ Desktop shortcuts failed: {e}{self.END}")
            return True  # Not critical
    
    def setup_browser_extension(self):
        """Setup instructions for browser extension"""
        print(f"\n{self.BOLD}🌐 Browser Extension Setup{self.END}")
        
        extension_dir = os.path.join(self.turboX_dir, 'browser_extension')
        
        if os.path.exists(extension_dir):
            print(f"""
{self.GREEN}✅ Browser extension files are ready!{self.END}

To install the browser extension:

{self.BOLD}For Chrome/Chromium:{self.END}
1. Open Chrome and go to: chrome://extensions/
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Select this directory: {extension_dir}
5. The TurboX DevTools Pro extension will appear

{self.BOLD}For Firefox:{self.END}
1. Open Firefox and go to: about:debugging#/runtime/this-firefox
2. Click "Load Temporary Add-on"
3. Select the manifest.json file from: {extension_dir}
4. The extension will load temporarily

{self.BOLD}After installation:{self.END}
• Click the TurboX icon in your browser toolbar
• Enable "Network Capture" to start automation
• Desktop tools will launch automatically
""")
        else:
            print(f"{self.YELLOW}⚠️ Browser extension directory not found{self.END}")
        
        return True
    
    def create_launch_script(self):
        """Create a simple launch script"""
        print(f"\n{self.BOLD}🎯 Creating launch script...{self.END}")
        
        try:
            # Create turbox command
            launch_script = f'''#!/bin/bash
# TurboX Desktop OS - Quick Launcher
# Run with: turbox

echo "╔══════════════════════════════════════════╗"
echo "║         TurboX Desktop OS v1.0          ║"
echo "╚══════════════════════════════════════════╝"

case "$1" in
    start)
        echo "Starting TurboX Desktop..."
        {os.path.join(self.turboX_dir, 'scripts', 'start-desktop.sh')}
        ;;
    stop)
        echo "Stopping TurboX Desktop..."
        pkill -f "termux-x11"
        pkill -f "openbox"
        pkill -f "tint2"
        pkill -f "pcmanfm"
        pkill -f "core_manager.py"
        echo "Stopped all services"
        ;;
    launcher)
        echo "Starting application launcher..."
        python {os.path.join(self.turboX_dir, 'scripts', 'desktop_launcher.py')}
        ;;
    api)
        echo "Starting API Tester..."
        python {os.path.join(self.turboX_dir, 'tools', 'api_tester.py')}
        ;;
    sms)
        echo "Starting SMS Panel..."
        python {os.path.join(self.turboX_dir, 'tools', 'sms_panel.py')}
        ;;
    bridge)
        echo "Starting Socket Bridge..."
        python {os.path.join(self.turboX_dir, 'scripts', 'socket_bridge.py')}
        ;;
    automation)
        echo "Starting Automation Controller..."
        python {os.path.join(self.turboX_dir, 'scripts', 'automation_controller.py')}
        ;;
    install)
        echo "Running installer..."
        python {os.path.join(self.turboX_dir, 'scripts', 'one_click_installer.py')}
        ;;
    help|*)
        echo "Usage: turbox [command]"
        echo ""
        echo "Commands:"
        echo "  start       - Start desktop environment"
        echo "  stop        - Stop desktop environment"
        echo "  launcher    - Open application launcher"
        echo "  api         - Start API Tester"
        echo "  sms         - Start SMS Panel"
        echo "  bridge      - Start Socket Bridge"
        echo "  automation  - Start Automation Controller"
        echo "  install     - Run installer"
        echo "  help        - Show this help"
        echo ""
        echo "Quick start:"
        echo "  1. turbox start      # Start desktop"
        echo "  2. turbox launcher   # Open apps"
        echo ""
        ;;
esac
'''
            
            # Write to multiple locations for easy access
            locations = [
                '/data/data/com.termux/files/usr/bin/turbox',  # Termux
                '/usr/local/bin/turbox',  # Linux
                os.path.join(self.home_dir, 'turbox')  # Home directory
            ]
            
            for location in locations:
                try:
                    with open(location, 'w') as f:
                        f.write(launch_script)
                    os.chmod(location, 0o755)
                    print(f"  Created: {location}")
                except:
                    pass  # Some locations might not be writable
            
            return True
            
        except Exception as e:
            print(f"{self.YELLOW}⚠️ Launch script failed: {e}{self.END}")
            return True  # Not critical
    
    def setup_termux_boot(self):
        """Setup Termux boot script for auto-start"""
        if not self.is_termux:
            return True
        
        print(f"\n{self.BOLD}🔧 Setting up Termux boot...{self.END}")
        
        try:
            termux_boot_dir = os.path.join(self.home_dir, '.termux')
            os.makedirs(termux_boot_dir, exist_ok=True)
            
            boot_script = f'''#!/data/data/com.termux/files/usr/bin/bash
# Auto-start TurboX on Termux boot

# Wait for system to settle
sleep 3

# Start TurboX if autostart is enabled
if [ -f "{self.turboX_dir}/autostart" ] && [ "$(cat "{self.turboX_dir}/autostart")" = "1" ]; then
    echo "Starting TurboX Desktop..."
    {os.path.join(self.turboX_dir, 'scripts', 'start-desktop.sh')} &
fi
'''
            
            boot_file = os.path.join(termux_boot_dir, 'boot')
            with open(boot_file, 'w') as f:
                f.write(boot_script)
            os.chmod(boot_file, 0o755)
            
            print(f"  Created: ~/.termux/boot")
            print(f"  TurboX will auto-start on Termux boot")
            
            return True
            
        except Exception as e:
            print(f"{self.YELLOW}⚠️ Termux boot setup failed: {e}{self.END}")
            return True
    
    def finalize_installation(self):
        """Final installation steps"""
        print(f"\n{self.BOLD}🎉 Finalizing installation...{self.END}")
        
        try:
            # Create README file
            readme_content = f'''# TurboX Desktop OS - Installation Complete!

## What's Installed
✅ Complete Windows-style desktop environment
✅ API Tester with automation capabilities
✅ SMS Panel for data collection
✅ Browser extension for DevTools integration
✅ Socket Bridge for desktop-browser communication
✅ Session Manager for automatic token handling
✅ Automation Controller for tool coordination

## Quick Start Guide

### 1. Start the Desktop
```bash
turbox start
