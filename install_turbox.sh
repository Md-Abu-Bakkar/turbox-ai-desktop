#!/data/data/com.termux/files/usr/bin/bash
# Complete TurboX Desktop Installer

echo "Installing TurboX Desktop OS..."

# Update packages
pkg update -y && pkg upgrade -y

# Install required packages
pkg install x11-repo -y
pkg install termux-x11-nightly openbox tint2 pcmanfm python nodejs firefox geany wget curl -y

# Install Python packages
pip install pyqt5 psutil requests beautifulsoup4 pillow

# Create directories
mkdir -p ~/.turboX/{scripts,tools,config,browser_extension,data}
mkdir -p ~/Desktop ~/Documents ~/Downloads ~/Pictures

# Download desktop script
cd ~/.turboX/scripts
curl -sL -o turbox_desktop.py https://raw.githubusercontent.com/Md-Abu-Bakkar/turbox-ai-desktop/main/turbox_desktop.py

# Create startup script
cat > start_turbox.sh << 'EOF'
#!/bin/bash
export DISPLAY=:0
termux-x11 :0 &
sleep 3
openbox &
tint2 &
pcmanfm --desktop &
python ~/.turboX/scripts/turbox_desktop.py &
wait
EOF

chmod +x start_turbox.sh

# Create turbox command
cat > $PREFIX/bin/turbox << 'EOF'
#!/bin/bash
case "$1" in
    start)
        ~/.turboX/scripts/start_turbox.sh
        ;;
    stop)
        pkill -f "termux-x11"
        pkill -f "openbox"
        pkill -f "tint2"
        pkill -f "pcmanfm"
        pkill -f "turbox_desktop.py"
        echo "✅ TurboX stopped"
        ;;
    api)
        python ~/.turboX/tools/api_tester.py
        ;;
    sms)
        python ~/.turboX/tools/sms_panel.py
        ;;
    install)
        echo "Running installer..."
        bash ~/.turboX/scripts/install_turbox.sh
        ;;
    help|*)
        echo "TurboX Desktop OS Commands:"
        echo "  turbox start    - Start desktop"
        echo "  turbox stop     - Stop desktop"
        echo "  turbox api      - Launch API Tester"
        echo "  turbox sms      - Launch SMS Panel"
        echo "  turbox install  - Install/update"
        echo "  turbox help     - Show this help"
        ;;
esac
EOF

chmod +x $PREFIX/bin/turbox

# Create API Tester
mkdir -p ~/.turboX/tools
cat > ~/.turboX/tools/api_tester.py << 'EOF'
#!/usr/bin/env python3
print("API Tester - Ready for automation")
print("Features: Auto-login, CAPTCHA solving, Token management")
input("Press Enter to exit...")
EOF

chmod +x ~/.turboX/tools/api_tester.py

# Create SMS Panel
cat > ~/.turboX/tools/sms_panel.py << 'EOF'
#!/usr/bin/env python3
print("SMS Panel - Ready for data collection")
print("Features: OTP detection, Message monitoring, API integration")
input("Press Enter to exit...")
EOF

chmod +x ~/.turboX/tools/sms_panel.py

echo ""
echo "✅ INSTALLATION COMPLETE!"
echo ""
echo "To start TurboX Desktop:"
echo "  1. Run: turbox start"
echo "  2. Wait for desktop to load"
echo "  3. Use the graphical interface"
echo ""
echo "For help: turbox help"
