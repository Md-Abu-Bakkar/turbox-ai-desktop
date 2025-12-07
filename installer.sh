#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# TurboX Desktop OS v2.0 - Complete One-Command Installer
# Full Automation System with Windows-Style Desktop
# ==============================================================================

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         TurboX Desktop OS v2.0 - Complete Automation     ║"
echo "║           Full Windows-Style Desktop on Android          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📱 Platform: Android (Termux + X11)"
echo "🚀 Features: Full automation • CAPTCHA solving • Multi-tool coordination"
echo ""

# Check Termux
if [ ! -d "/data/data/com.termux/files/usr" ]; then
    echo "❌ ERROR: Must run in Termux"
    echo "   Install Termux from Google Play/F-Droid first"
    exit 1
fi

# Update system
echo "🔄 Updating Termux packages..."
pkg update -y && pkg upgrade -y

# Install repositories
echo "📦 Installing X11 repositories..."
pkg install x11-repo tur-repo -y

# Install desktop environment
echo "🏗️  Installing desktop components..."
pkg install termux-x11 pulseaudio -y
pkg install openbox obconf tint2 pcmanfm xfce4-terminal mousepad -y
pkg install firefox chromium -y

# Install development tools
echo "🔧 Installing development tools..."
pkg install python nodejs git wget curl unzip -y
pkg install wine box64 -y

# Install Python packages for automation
echo "🐍 Installing Python automation packages..."
pip install pyqt5 psutil requests pillow selenium pyautogui beautifulsoup4 lxml cryptography

# Create TurboX directories
echo "📁 Creating system directories..."
mkdir -p ~/.turboX/{config,scripts,tools,data,logs,exports,sessions,captchas}
mkdir -p ~/Desktop ~/Documents ~/Downloads ~/Pictures ~/Music ~/Videos

# Download TurboX system files
echo "⬇️  Downloading TurboX system files..."
cd ~/.turboX

# Download core files
echo "  Downloading core system..."
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/desktop_core.py -O scripts/desktop_core.py
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/file_manager.py -O scripts/file_manager.py
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/window_manager.py -O scripts/window_manager.py

# Download automated tools
echo "  Downloading automated tools..."
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/api_tester_auto.py -O tools/api_tester_auto.py
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/sms_panel_auto.py -O tools/sms_panel_auto.py
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/captcha_solver.py -O scripts/captcha_solver.py
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/session_manager.py -O scripts/session_manager.py
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/automation_controller.py -O scripts/automation_controller.py
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/socket_bridge.py -O scripts/socket_bridge.py
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/auto_launcher.py -O scripts/auto_launcher.py

# Download browser extension
echo "  Downloading browser extension..."
mkdir -p browser_extension
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/browser_extension/manifest.json -O browser_extension/manifest.json
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/browser_extension/background.js -O browser_extension/background.js
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/browser_extension/content.js -O browser_extension/content.js
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/browser_extension/popup.html -O browser_extension/popup.html
wget -q https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/browser_extension/popup.js -O browser_extension/popup.js

# Create configuration files
echo "⚙️  Creating configuration files..."

# System configuration
cat > config/system.json << EOF
{
  "system": {
    "version": "2.0",
    "platform": "android",
    "install_date": "$(date +"%Y-%m-%d %H:%M:%S")",
    "auto_start": true
  },
  "desktop": {
    "theme": "windows-dark",
    "taskbar": true,
    "start_menu": true,
    "multi_window": true,
    "file_manager": "pcmanfm"
  },
  "automation": {
    "auto_login": true,
    "auto_captcha": true,
    "auto_tools": true,
    "auto_session": true,
    "auto_data_fetch": true
  },
  "tools": {
    "api_tester": {
      "auto_launch": true,
      "auto_fetch": true,
      "resizable": true
    },
    "sms_panel": {
      "auto_launch": true,
      "auto_fetch": true,
      "resizable": true,
      "fetch_all_months": true
    },
    "dev_tools": {
      "auto_capture": true,
      "share_data": true
    }
  },
  "browser": {
    "extension_port": 8765,
    "auto_connect": true,
    "supported": ["chrome", "firefox", "chromium"]
  }
}
EOF

# Openbox configuration (Windows-style)
cat > config/openbox.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <theme>
    <name>Clearlooks</name>
    <titleLayout>LIMC</titleLayout>
    <keepBorder>yes</keepBorder>
    <animateIconify>yes</animateIconify>
    <font place="ActiveWindow">
      <name>Segoe UI</name>
      <size>10</size>
      <weight>normal</weight>
      <slant>normal</slant>
    </font>
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
        <command>python ~/.turboX/scripts/desktop_core.py</command>
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
    <context name="Titlebar">
      <mousebind button="Left" action="Press">
        <action name="Focus"/>
        <action name="Raise"/>
      </mousebind>
      <mousebind button="Left" action="Drag">
        <action name="Move"/>
      </mousebind>
      <mousebind button="Left" action="DoubleClick">
        <action name="ToggleMaximize"/>
      </mousebind>
      <mousebind button="Right" action="Press">
        <action name="Focus"/>
        <action name="Raise"/>
        <action name="ShowMenu">
          <menu>client-menu</menu>
        </action>
      </mousebind>
    </context>
    <context name="Frame">
      <mousebind button="Left" action="Press">
        <action name="Focus"/>
        <action name="Raise"/>
      </mousebind>
      <mousebind button="Left" action="Drag">
        <action name="Resize"/>
      </mousebind>
    </context>
  </mouse>
  
  <applications>
    <application class="*">
      <decor>yes</decor>
      <position force="no">
        <x>center</x>
        <y>center</y>
      </position>
      <size>
        <width>800</width>
        <height>600</height>
      </size>
      <focus>yes</focus>
      <desktop>1</desktop>
      <layer>normal</layer>
      <iconic>no</iconic>
      <maximized>no</maximized>
    </application>
  </applications>
</openbox_config>
EOF

# Tint2 taskbar configuration
cat > config/tint2rc << EOF
# TurboX Windows-Style Taskbar
panel_monitor = all
panel_position = bottom center horizontal
panel_size = 100% 48
panel_margin = 0 0
panel_padding = 5 0 5
panel_dock = 0
wm_menu = 1
panel_background_id = 1
panel_items = LTSBC

# Launcher (Start Menu)
launcher_icon_theme = Adwaita
launcher_padding = 5 0 5
launcher_background_id = 2
launcher_icon_size = 32
launcher_item_app = ~/.turboX/scripts/desktop_core.py

# Taskbar (Windows-style)
taskbar_mode = multi_desktop
taskbar_padding = 5 0 5
task_background_id = 3
task_icon = 1
task_text = 1
task_centered = 1
task_maximum_size = 200 40
task_active_background_id = 4

# System tray
systray = 1
systray_padding = 5 0 5
systray_sort = right2left
systray_background_id = 5

# Clock (Windows-style)
time1_format = %I:%M %p
time1_font = Segoe UI 10
time2_format = %A, %d %B
time2_font = Segoe UI 9
clock_font_color = #ffffff 100
clock_padding = 10 0
clock_background_id = 6

# Battery (for mobile)
battery = 1
battery_hide = 100
battery_low_status = 20
battery_low_cmd = notify-send "Battery Low"
battery_font = Segoe UI 9
battery_font_color = #ffffff 100
battery_padding = 10 0

# Backgrounds
background 1 = rounded 0 border 0 color #2d2d2d 100
background 2 = rounded 5 border 1 border_color #555555 100 color #3d3d3d 100
background 3 = rounded 3 border 0 color #3d3d3d 80
background 4 = rounded 3 border 1 border_color #0078d7 100 color #1e3a5f 100
background 5 = rounded 5 border 0 color #3d3d3d 100
background 6 = rounded 5 border 0 color #0078d7 100
EOF

# Create desktop startup script
cat > scripts/start_desktop.sh << 'EOF'
#!/bin/bash
# TurboX Desktop v2.0 - Startup Script

export DISPLAY=:0
export PULSE_SERVER=127.0.0.1

echo "🚀 Starting TurboX Desktop v2.0..."

# Start X server if not running
if ! pgrep -x "termux-x11" > /dev/null; then
    echo "  Starting X11 server..."
    termux-x11 :0 &
    sleep 3
fi

# Start window manager
echo "  Starting Windows-style desktop..."
openbox --config-file ~/.turboX/config/openbox.xml &

# Start taskbar
echo "  Starting taskbar..."
tint2 -c ~/.turboX/config/tint2rc &

# Start file manager as desktop
echo "  Starting file manager..."
pcmanfm --desktop &

# Start automation controller
echo "  Starting automation system..."
python ~/.turboX/scripts/automation_controller.py &

# Start socket bridge for browser communication
echo "  Starting browser communication..."
python ~/.turboX/scripts/socket_bridge.py &

echo ""
echo "✅ TurboX Desktop is running!"
echo ""
echo "📱 Quick Start:"
echo "   1. Open browser (Firefox/Chrome)"
echo "   2. Load extension from: ~/.turboX/browser_extension/"
echo "   3. Visit any website"
echo "   4. Tools auto-launch and fetch data automatically!"
echo ""
echo "🖱️  Controls:"
echo "   • Left-click: Select/Open"
echo "   • Right-click: Context menu"
echo "   • Double-click: Open files"
echo "   • Drag & Drop: Move files/windows"
echo ""
EOF

chmod +x scripts/start_desktop.sh

# Create desktop launcher script
cat > Desktop/TurboX\ Launcher.desktop << EOF
[Desktop Entry]
Name=TurboX Launcher
Comment=Launch TurboX Applications
Exec=python ~/.turboX/scripts/desktop_core.py
Icon=applications-system
Terminal=false
Type=Application
Categories=System;Utility;
EOF

chmod +x Desktop/TurboX\ Launcher.desktop

# Create auto-start for Termux
cat > ~/.termux/boot << EOF
#!/bin/bash
# Auto-start TurboX on Termux boot
sleep 5
~/.turboX/scripts/start_desktop.sh &
EOF

chmod +x ~/.termux/boot

# Create turbox command
cat > /data/data/com.termux/files/usr/bin/turbox << 'EOF'
#!/bin/bash
# TurboX Command Line Interface

case "$1" in
    start)
        ~/.turboX/scripts/start_desktop.sh
        ;;
    stop)
        pkill -f "termux-x11"
        pkill -f "openbox"
        pkill -f "tint2"
        pkill -f "pcmanfm"
        pkill -f "automation_controller"
        pkill -f "socket_bridge"
        echo "✅ TurboX stopped"
        ;;
    launcher)
        python ~/.turboX/scripts/desktop_core.py
        ;;
    api)
        python ~/.turboX/tools/api_tester_auto.py
        ;;
    sms)
        python ~/.turboX/tools/sms_panel_auto.py
        ;;
    automation)
        python ~/.turboX/scripts/automation_controller.py
        ;;
    browser)
        echo "📱 Load browser extension from: ~/.turboX/browser_extension/"
        echo "🌐 Chrome: chrome://extensions → Load unpacked"
        echo "🔥 Firefox: about:debugging → Load Temporary Add-on"
        ;;
    install-ext)
        # Auto-install browser extension for Chrome
        if [ -d "/data/data/com.android.chrome" ]; then
            echo "Installing Chrome extension..."
            # Copy extension files to Chrome extension directory
            cp -r ~/.turboX/browser_extension /data/data/com.android.chrome/files/
            echo "Extension installed. Restart Chrome."
        else
            echo "Chrome not found. Install manually from ~/.turboX/browser_extension/"
        fi
        ;;
    status)
        echo "TurboX Desktop v2.0 Status:"
        echo "  X11: $(pgrep -x "termux-x11" && echo "Running" || echo "Stopped")"
        echo "  Desktop: $(pgrep -f "openbox" && echo "Running" || echo "Stopped")"
        echo "  Automation: $(pgrep -f "automation_controller" && echo "Running" || echo "Stopped")"
        echo "  Bridge: $(pgrep -f "socket_bridge" && echo "Running" || echo "Stopped")"
        ;;
    help|*)
        echo "TurboX Desktop OS v2.0 - Complete Automation System"
        echo ""
        echo "Commands:"
        echo "  turbox start        - Start desktop"
        echo "  turbox stop         - Stop desktop"
        echo "  turbox launcher     - Open application launcher"
        echo "  turbox api          - Open API Tester"
        echo "  turbox sms          - Open SMS Panel"
        echo "  turbox automation   - Open Automation Controller"
        echo "  turbox browser      - Show browser extension instructions"
        echo "  turbox install-ext  - Auto-install browser extension"
        echo "  turbox status       - Check system status"
        echo "  turbox help         - Show this help"
        echo ""
        echo "📖 Automation Flow:"
        echo "  1. turbox start"
        echo "  2. Open browser with extension"
        echo "  3. Visit any website"
        echo "  4. Tools auto-launch and fetch data!"
        echo ""
        ;;
esac
EOF

chmod +x /data/data/com.termux/files/usr/bin/turbox

# Enable autostart
echo "1" > ~/.turboX/config/autostart

# Set permissions
chmod -R 755 ~/.turboX/scripts/*

echo ""
echo "✅ INSTALLATION COMPLETE!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 TURBOX DESKTOP OS v2.0 READY!"
echo ""
echo "🚀 To start:"
echo "   1. Run: turbox start"
echo "   2. Or reboot Termux (auto-starts on boot)"
echo ""
echo "🌐 Browser Extension:"
echo "   • Chrome: chrome://extensions → Load unpacked"
echo "   • Select: ~/.turboX/browser_extension/"
echo ""
echo "🤖 Automation Features:"
echo "   • Auto-login with credentials"
echo "   • Auto-CAPTCHA solving"
echo "   • Auto-token/session management"
echo "   • Auto-data fetching"
echo "   • Tools auto-launch when browsing"
echo ""
echo "📱 One Command to Start Everything: turbox start"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
