#!/data/data/com.termux/files/usr/bin/bash
# TurboX Desktop Startup Script

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    TurboX Desktop OS                     ║"
echo "║           Full Windows-Style Desktop on Android          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Starting system..."

# Export display
export DISPLAY=:0

# Kill any existing X11 servers
pkill -f "termux-x11"
sleep 1

# Start X11 server
echo "Starting X11 server..."
termux-x11 :0 &
X11_PID=$!
sleep 3

# Check if X11 started
if ! ps -p $X11_PID > /dev/null; then
    echo "❌ Failed to start X11 server"
    exit 1
fi

echo "✅ X11 server started (PID: $X11_PID)"

# Start Openbox window manager
echo "Starting window manager..."
openbox &
sleep 1

# Start taskbar
echo "Starting taskbar..."
tint2 &
sleep 1

# Start file manager as desktop
echo "Starting file manager..."
pcmanfm --desktop &
sleep 1

# Start TurboX Desktop
echo "Starting TurboX Desktop GUI..."
python ~/.turboX/scripts/turbox_desktop.py &

echo ""
echo "════════════════════════════════════════════════════════════"
echo "🎉 TurboX Desktop is now running!"
echo ""
echo "📱 Quick Access:"
echo "   • Desktop icons for applications"
echo "   • Taskbar for window management"
echo "   • Right-click for context menu"
echo ""
echo "🛠️  Available Tools:"
echo "   • API Tester (Auto-login, CAPTCHA solving)"
echo "   • SMS Panel (OTP, Message collection)"
echo "   • File Manager (Phone storage access)"
echo "   • Browser with DevTools integration"
echo ""
echo "💡 Tip: Run 'turbox help' for commands"
echo "════════════════════════════════════════════════════════════"

# Keep script running
wait $X11_PID
