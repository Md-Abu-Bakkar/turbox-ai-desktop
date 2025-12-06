#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# TurboX Desktop OS - Clean Installer (2025 Stable)
# ==============================================================================

set -e

clear
echo "╔══════════════════════════════════════════════════════════╗"
echo "║            TurboX Desktop OS – Clean Installer           ║"
echo "║             Termux + Termux:X11 (Stable)                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ------------------------------------------------------------------
# Check Termux
# ------------------------------------------------------------------
if [ ! -d "/data/data/com.termux/files/usr" ]; then
  echo "❌ ERROR: Run this script ONLY inside Termux"
  exit 1
fi

# ------------------------------------------------------------------
# Clean previous partial installs (safe)
# ------------------------------------------------------------------
echo "🧹 Cleaning old TurboX files (if any)..."
rm -rf ~/.turboX 2>/dev/null || true

# ------------------------------------------------------------------
# Update system
# ------------------------------------------------------------------
echo "📦 Updating Termux base system..."
pkg update -y
pkg upgrade -y

# ------------------------------------------------------------------
# Enable repositories
# ------------------------------------------------------------------
echo "📦 Enabling repositories..."
pkg install -y x11-repo tur-repo

# ------------------------------------------------------------------
# Core X11 system
# ------------------------------------------------------------------
echo "🖥 Installing X11 system..."
pkg install -y termux-x11 pulseaudio

# ------------------------------------------------------------------
# Window manager & desktop tools (NO obconf)
# ------------------------------------------------------------------
echo "🪟 Installing window manager..."
pkg install -y \
  openbox \
  obconf-qt \
  tint2 \
  pcmanfm \
  xfce4-terminal \
  mousepad \
  xorg-xsetroot

# ------------------------------------------------------------------
# Developer utilities (safe only)
# ------------------------------------------------------------------
echo "🛠 Installing core tools..."
pkg install -y git curl wget unzip python nodejs

# ------------------------------------------------------------------
# Python libs (Termux-safe)
# ------------------------------------------------------------------
echo "🐍 Installing Python libraries..."
pip install --no-cache-dir psutil requests pillow

# ------------------------------------------------------------------
# Directory structure
# ------------------------------------------------------------------
echo "📁 Creating TurboX directories..."
mkdir -p ~/.turboX/{config,scripts,logs}
mkdir -p ~/Desktop ~/Documents ~/Downloads ~/Pictures

# ------------------------------------------------------------------
# Openbox config (SAFE MINIMAL)
# ------------------------------------------------------------------
echo "⚙️ Creating Openbox configuration..."
cat > ~/.turboX/config/rc.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <focus>
    <followMouse>no</followMouse>
    <focusNew>yes</focusNew>
  </focus>

  <placement>
    <policy>Smart</policy>
    <center>yes</center>
  </placement>

  <theme>
    <name>Clearlooks</name>
  </theme>

  <keyboard>
    <keybind key="W-Return">
      <action name="Execute">
        <command>xfce4-terminal</command>
      </action>
    </keybind>
    <keybind key="W-e">
      <action name="Execute">
        <command>pcmanfm</command>
      </action>
    </keybind>
  </keyboard>
</openbox_config>
EOF

# ------------------------------------------------------------------
# Tint2 panel
# ------------------------------------------------------------------
echo "📊 Creating taskbar..."
cat > ~/.turboX/config/tint2rc << 'EOF'
panel_monitor = all
panel_position = bottom center horizontal
panel_size = 100% 36
panel_margin = 0 0
panel_padding = 4 0
wm_menu = 1
panel_items = TSC

task_icon = 1
task_text = 1

systray = 1

time1_format = %H:%M
time2_format = %d %b
EOF

# ------------------------------------------------------------------
# Desktop start script
# ------------------------------------------------------------------
echo "▶️ Creating start script..."
cat > ~/.turboX/scripts/start-desktop.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

export DISPLAY=:0
export PULSE_SERVER=127.0.0.1

if ! pgrep -x termux-x11 >/dev/null; then
  termux-x11 :0 &
  sleep 3
fi

xsetroot -solid "#1e1e1e"

openbox --config-file ~/.turboX/config/rc.xml &
sleep 1
tint2 -c ~/.turboX/config/tint2rc &
pcmanfm --desktop &

echo "✅ TurboX Desktop started"
EOF

chmod +x ~/.turboX/scripts/start-desktop.sh

# ------------------------------------------------------------------
# Finish
# ------------------------------------------------------------------
echo ""
echo "✅ INSTALLATION COMPLETED SUCCESSFULLY"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 START DESKTOP:"
echo "termux-x11 :0 &"
echo "~/.turboX/scripts/start-desktop.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
