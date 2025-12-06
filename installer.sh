#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# TurboX Desktop OS - Foundation Installer
# Phase 1: Base System Setup
# ==============================================================================

set -e  # Exit on any error

echo "╔══════════════════════════════════════════════════════════╗"
echo "║               TurboX Desktop OS Installer                ║"
echo "║                    Phase 1: Foundation                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if running in Termux
if [ ! -d "/data/data/com.termux/files/usr" ]; then
    echo "❌ ERROR: This script must run inside Termux"
    echo "   Please install Termux from Google Play/F-Droid first"
    exit 1
fi

# Update and upgrade base system
echo "📦 Updating Termux packages..."
pkg update -y && pkg upgrade -y

# Install essential repositories
echo "📦 Installing X11 and Turing repositories..."
pkg install x11-repo tur-repo -y

# Install core desktop packages
echo "📦 Installing desktop environment..."
pkg install termux-x11 pulseaudio -y

# Install window manager and utilities
echo "📦 Installing window manager and tools..."
pkg install openbox obconf tint2 pcmanfm xfce4-terminal mousepad -y

# Install development tools
echo "📦 Installing development tools..."
pkg install python nodejs git wget curl unzip -y

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install pyqt5 psutil requests pillow

# Create necessary directories
echo "📁 Creating system directories..."
mkdir -p ~/.turboX/{config,scripts,tools,logs}
mkdir -p ~/Desktop ~/Documents ~/Downloads ~/Pictures

# Copy configuration files
echo "⚙️  Setting up configuration..."
cp -r config/* ~/.turboX/config/ 2>/dev/null || true

# Set up startup script
echo "📝 Creating startup scripts..."
cat > ~/.termux/boot << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# Auto-start TurboX on Termux boot
if [ -f ~/.turboX/autostart ] && [ "$(cat ~/.turboX/autostart)" = "1" ]; then
    termux-x11 :0 &
    sleep 2
    ~/.turboX/scripts/start-desktop.sh
fi
EOF

chmod +x ~/.termux/boot

# Create desktop start script
cat > ~/.turboX/scripts/start-desktop.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# Start TurboX Desktop Environment

export DISPLAY=:0
export PULSE_SERVER=127.0.0.1

# Start X server if not running
if ! pgrep -x "termux-x11" > /dev/null; then
    termux-x11 :0 &
    sleep 3
fi

# Start Openbox window manager
openbox --config-file ~/.turboX/config/openbox.xml &

# Start taskbar
tint2 -c ~/.turboX/config/tint2rc &

# Start file manager
pcmanfm --desktop &

# Start TurboX core services
python ~/.turboX/scripts/core_manager.py &

echo "TurboX Desktop started successfully!"
EOF

chmod +x ~/.turboX/scripts/start-desktop.sh

# Create basic openbox configuration
cat > ~/.turboX/config/openbox.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
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
  </keyboard>
  <mouse>
    <dragThreshold>8</dragThreshold>
    <doubleClickTime>500</doubleClickTime>
  </mouse>
</openbox_config>
EOF

# Create tint2 taskbar config
cat > ~/.turboX/config/tint2rc << 'EOF'
# TurboX Taskbar Configuration
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
EOF

# Enable autostart
echo "1" > ~/.turboX/autostart

# Set permissions
chmod 755 ~/.turboX
chmod 755 ~/.turboX/scripts/*

echo ""
echo "✅ Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "To start TurboX Desktop:"
echo "1. Restart Termux"
echo "2. OR Run: termux-x11 :0 &"
echo "3. Then run: ~/.turboX/scripts/start-desktop.sh"
echo ""
echo "Next phase: Core window manager and UI framework"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
