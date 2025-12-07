#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# TurboX Desktop OS v2.0 - Complete One-Command Installer (FIXED)
# Updated for current Termux repositories
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

# Install desktop environment (FIXED PACKAGES)
echo "🏗️  Installing desktop components..."
pkg install termux-x11-nightly pulseaudio -y
pkg install openbox openbox-menu tint2 pcmanfm xfce4-terminal geany -y
pkg install firefox chromium -y

# Install development tools
echo "🔧 Installing development tools..."
pkg install python nodejs-lts git wget curl unzip -y
pkg install wine box64 -y

# Install Python packages for automation
echo "🐍 Installing Python automation packages..."
pip install pyqt5 psutil requests pillow selenium beautifulsoup4 lxml

# Create TurboX directories
echo "📁 Creating system directories..."
mkdir -p ~/.turboX/{config,scripts,tools,data,logs,exports,sessions,captchas}
mkdir -p ~/Desktop ~/Documents ~/Downloads ~/Pictures ~/Music ~/Videos

# Download TurboX system files
echo "⬇️  Downloading TurboX system files..."
cd ~/.turboX

# Create a simple download function
download_file() {
    local url=$1
    local dest=$2
    echo "  Downloading: $(basename $dest)"
    wget -q --timeout=30 --tries=3 "$url" -O "$dest" || echo "  ⚠️ Failed to download: $(basename $dest)"
}

# Download core files
echo "  Downloading core system..."
download_file "https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/desktop_core.py" "scripts/desktop_core.py"
download_file "https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/file_manager.py" "scripts/file_manager.py"
download_file "https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/window_manager.py" "scripts/window_manager.py"

# Download automated tools
echo "  Downloading automated tools..."
download_file "https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/api_tester_auto.py" "tools/api_tester_auto.py"
download_file "https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/sms_panel_auto.py" "tools/sms_panel_auto.py"
download_file "https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/captcha_solver.py" "scripts/captcha_solver.py"
download_file "https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/session_manager.py" "scripts/session_manager.py"
download_file "https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/automation_controller.py" "scripts/automation_controller.py"
download_file "https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/socket_bridge.py" "scripts/socket_bridge.py"
download_file "https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/auto_launcher.py" "scripts/auto_launcher.py"

# Create browser extension files
echo "  Creating browser extension..."
mkdir -p browser_extension

# Create manifest.json
cat > browser_extension/manifest.json << 'EOF'
{
  "manifest_version": 3,
  "name": "TurboX DevTools Pro",
  "version": "2.0",
  "description": "TurboX Desktop OS - Complete Automation Suite",
  "permissions": [
    "webRequest",
    "webRequestBlocking",
    "tabs",
    "storage",
    "debugger",
    "scripting",
    "activeTab",
    "<all_urls>"
  ],
  "host_permissions": [
    "<all_urls>"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"],
      "run_at": "document_start"
    }
  ],
  "action": {
    "default_popup": "popup.html",
    "default_title": "TurboX DevTools Pro"
  }
}
EOF

# Create simple background.js
cat > browser_extension/background.js << 'EOF'
// TurboX Browser Extension - Background Service
console.log('TurboX DevTools Pro loaded');

// Listen for installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('TurboX extension installed');
  chrome.storage.local.set({ turboXEnabled: true });
});

// Listen for messages
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Message received:', message.type);
  
  if (message.type === 'GET_STATUS') {
    sendResponse({ status: 'active', version: '2.0' });
  }
  
  if (message.type === 'TOGGLE_CAPTURE') {
    chrome.storage.local.set({ captureEnabled: message.enabled });
    sendResponse({ success: true });
  }
  
  return true;
});
EOF

# Create simple content.js
cat > browser_extension/content.js << 'EOF'
// TurboX Content Script
console.log('TurboX content script loaded');

// Connect to background
chrome.runtime.sendMessage({ type: 'CONTENT_SCRIPT_READY' });

// Listen for messages
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'SCAN_PAGE') {
    const pageInfo = {
      url: window.location.href,
      title: document.title,
      forms: document.forms.length,
      hasLogin: document.querySelector('input[type="password"]') !== null
    };
    sendResponse(pageInfo);
  }
  return true;
});
EOF

# Create popup.html
cat > browser_extension/popup.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TurboX</title>
  <style>
    body { width: 300px; padding: 15px; background: #1e1e1e; color: white; }
    .status { color: #4CAF50; font-weight: bold; }
    button { background: #0078d7; color: white; border: none; padding: 10px; margin: 5px; border-radius: 5px; cursor: pointer; }
    button:hover { background: #106ebe; }
  </style>
</head>
<body>
  <h3>TurboX DevTools Pro v2.0</h3>
  <p>Status: <span class="status" id="status">Active</span></p>
  <button id="capture">Toggle Capture</button>
  <button id="launch">Launch Tools</button>
  <script src="popup.js"></script>
</body>
</html>
EOF

# Create popup.js
cat > browser_extension/popup.js << 'EOF'
document.getElementById('capture').addEventListener('click', () => {
  chrome.runtime.sendMessage({ type: 'TOGGLE_CAPTURE', enabled: true });
});

document.getElementById('launch').addEventListener('click', () => {
  // Launch desktop tools
  fetch('http://localhost:8765/launch/tools')
    .then(response => response.json())
    .then(data => {
      document.getElementById('status').textContent = 'Tools launching...';
    });
});
EOF

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
    "auto_session": true
  }
}
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
openbox &

# Start taskbar
echo "  Starting taskbar..."
tint2 &

# Start file manager as desktop
echo "  Starting file manager..."
pcmanfm --desktop &

echo ""
echo "✅ TurboX Desktop is running!"
echo ""
echo "📱 Quick Access:"
echo "   • Desktop icons for quick launch"
echo "   • Right-click for context menu"
echo "   • Taskbar for app switching"
echo ""
EOF

chmod +x scripts/start_desktop.sh

# Create desktop launcher
cat > Desktop/TurboX\ Launcher.desktop << EOF
[Desktop Entry]
Name=TurboX Launcher
Comment=Launch TurboX Applications
Exec=python ~/.turboX/scripts/desktop_core.py
Terminal=false
Type=Application
Categories=System;
EOF

chmod +x Desktop/TurboX\ Launcher.desktop

# Create turbox command
cat > $PREFIX/bin/turbox << 'EOF'
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
    install)
        echo "Re-running installer..."
        curl -sL https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/installer.sh | bash
        ;;
    status)
        echo "TurboX Desktop v2.0 Status:"
        echo "  X11: $(pgrep -x "termux-x11" && echo "✅ Running" || echo "❌ Stopped")"
        echo "  Desktop: $(pgrep -f "openbox" && echo "✅ Running" || echo "❌ Stopped")"
        echo "  Install dir: ~/.turboX"
        echo "  Tools: API Tester, SMS Panel, File Manager"
        ;;
    help|*)
        echo "TurboX Desktop OS v2.0"
        echo ""
        echo "Commands:"
        echo "  turbox start        - Start desktop"
        echo "  turbox stop         - Stop desktop"
        echo "  turbox launcher     - Open application launcher"
        echo "  turbox api          - Open API Tester"
        echo "  turbox sms          - Open SMS Panel"
        echo "  turbox install      - Re-install system"
        echo "  turbox status       - Check system status"
        echo "  turbox help         - Show this help"
        echo ""
        echo "Quick Start:"
        echo "  1. turbox start"
        echo "  2. Open browser"
        echo "  3. Load extension from ~/.turboX/browser_extension/"
        echo ""
        ;;
esac
EOF

chmod +x $PREFIX/bin/turbox

# Enable autostart
echo "1" > config/autostart

# Set permissions
chmod -R 755 scripts/*

echo ""
echo "✅ INSTALLATION COMPLETE!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 TURBOX DESKTOP OS v2.0 INSTALLED SUCCESSFULLY!"
echo ""
echo "🚀 To start the desktop:"
echo "   turbox start"
echo ""
echo "🌐 To install browser extension:"
echo "   1. Open Chrome/Chromium"
echo "   2. Go to: chrome://extensions/"
echo "   3. Enable 'Developer mode'"
echo "   4. Click 'Load unpacked'"
echo "   5. Select: ~/.turboX/browser_extension/"
echo ""
echo "🖱️  Features installed:"
echo "   ✅ Windows-style desktop"
echo "   ✅ File manager with phone storage"
echo "   ✅ Multi-window support"
echo "   ✅ API Tester with automation"
echo "   ✅ SMS Panel"
echo "   ✅ Browser extension"
echo ""
echo "📝 Need help? Run: turbox help"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
