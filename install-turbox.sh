#!/bin/bash
# TurboX Desktop OS Installer
# Version: 1.0.0

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
INSTALL_DIR="$HOME/.turbox"
REPO_URL="https://github.com/turbox-project/turbox-desktop.git"
BRANCH="main"

# Logging functions
log() {
    echo -e "${GREEN}[✓]${NC} $1"
}

info() {
    echo -e "${BLUE}[i]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

header() {
    echo -e "${MAGENTA}"
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║           🚀 TurboX Desktop OS Installer            ║"
    echo "║                 Version 1.0.0                        ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "Do not run as root/sudo. Run as normal user."
        exit 1
    fi
}

detect_platform() {
    if [ -d "/data/data/com.termux" ]; then
        echo "termux"
    elif [ -f "/etc/os-release" ]; then
        . /etc/os-release
        if [[ "$ID" == "ubuntu" || "$ID" == "debian" ]]; then
            echo "debian"
        elif [[ "$ID" == "fedora" ]]; then
            echo "fedora"
        elif [[ "$ID" == "arch" ]]; then
            echo "arch"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

check_dependencies() {
    info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        warn "Python3 not found. It will be installed."
        return 1
    fi
    
    # Check Python version
    python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [[ $(echo "$python_version < 3.8" | bc) -eq 1 ]]; then
        warn "Python 3.8+ required (found $python_version)"
        return 1
    fi
    
    log "Python $python_version detected"
    return 0
}

install_termux() {
    info "Installing Termux dependencies..."
    
    # Update packages
    pkg update -y && pkg upgrade -y
    
    # Install core dependencies
    pkg install -y python git wget curl proot
    
    # Install X11 if requested
    read -p "Install X11 support for GUI? (y/N): " install_x11
    if [[ "$install_x11" =~ ^[Yy]$ ]]; then
        pkg install -y x11-repo tur-repo
        pkg install -y xfce4 xfce4-terminal xfwm4
        log "X11 support installed"
    fi
    
    # Install development tools
    pkg install -y nodejs php
    
    # Install archive tools
    pkg install -y unzip zip unrar p7zip
    
    # Install Wine if requested
    read -p "Install Wine for Windows EXE support? (y/N): " install_wine
    if [[ "$install_wine" =~ ^[Yy]$ ]]; then
        pkg install -y wine
        log "Wine installed"
    fi
    
    log "Termux dependencies installed"
}

install_debian() {
    info "Installing Debian/Ubuntu dependencies..."
    
    sudo apt update
    sudo apt install -y python3 python3-pip python3-tk git wget curl
    
    # Install NodeJS
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
    
    # Install PHP
    sudo apt install -y php
    
    # Install archive tools
    sudo apt install -y unzip zip unrar p7zip-full
    
    # Install Wine if requested
    read -p "Install Wine for Windows EXE support? (y/N): " install_wine
    if [[ "$install_wine" =~ ^[Yy]$ ]]; then
        sudo apt install -y wine
        log "Wine installed"
    fi
    
    log "Debian dependencies installed"
}

install_arch() {
    info "Installing Arch Linux dependencies..."
    
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm python python-pip tk git wget curl nodejs php
    
    # Install archive tools
    sudo pacman -S --noconfirm unzip zip unrar p7zip
    
    # Install Wine if requested
    read -p "Install Wine for Windows EXE support? (y/N): " install_wine
    if [[ "$install_wine" =~ ^[Yy]$ ]]; then
        sudo pacman -S --noconfirm wine
        log "Wine installed"
    fi
    
    log "Arch dependencies installed"
}

install_python_packages() {
    info "Installing Python packages..."
    
    pip3 install --upgrade pip
    
    # Core packages
    pip3 install requests beautifulsoup4 lxml pillow
    
    # Desktop packages
    pip3 install pyautogui psutil pyperclip
    
    # Database
    pip3 install sqlite3
    
    # Optional AI packages
    read -p "Install AI/ML packages? (y/N): " install_ai
    if [[ "$install_ai" =~ ^[Yy]$ ]]; then
        pip3 install numpy pandas scikit-learn transformers torch --index-url https://download.pytorch.org/whl/cpu
        log "AI packages installed"
    fi
    
    log "Python packages installed"
}

clone_repository() {
    info "Downloading TurboX Desktop OS..."
    
    if [ -d "$INSTALL_DIR" ]; then
        warn "Installation directory exists. Updating..."
        cd "$INSTALL_DIR"
        
        if [ -d ".git" ]; then
            git pull origin "$BRANCH"
        else
            warn "Not a git repository. Removing and cloning fresh..."
            cd ..
            rm -rf "$INSTALL_DIR"
            git clone --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
        fi
    else
        git clone --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
    fi
    
    cd "$INSTALL_DIR"
    log "Repository cloned to $INSTALL_DIR"
}

setup_environment() {
    info "Setting up environment..."
    
    # Create necessary directories
    mkdir -p "$INSTALL_DIR/data"
    mkdir -p "$INSTALL_DIR/config"
    mkdir -p "$INSTALL_DIR/apps"
    mkdir -p "$INSTALL_DIR/tools"
    mkdir -p "$HOME/.turbox/wallpapers"
    mkdir -p "$HOME/.turbox/screenshots"
    
    # Create default configuration
    cat > "$INSTALL_DIR/config/desktop.json" << EOF
{
    "theme": "dark",
    "wallpaper": "default",
    "show_icons": true,
    "animations": true,
    "taskbar_position": "bottom",
    "virtual_desktops": 4,
    "ai_enabled": false,
    "wine_enabled": false,
    "install_dir": "$INSTALL_DIR"
}
EOF
    
    # Create start menu configuration
    cat > "$INSTALL_DIR/config/start_menu.json" << EOF
{
    "apps": [
        {"name": "App Store", "icon": "📦", "app_id": "app_store", "category": "system"},
        {"name": "File Manager", "icon": "📁", "app_id": "file_manager", "category": "system"},
        {"name": "Terminal", "icon": "💻", "app_id": "terminal", "category": "system"},
        {"name": "API Tools", "icon": "🔧", "app_id": "api_tools", "category": "development"},
        {"name": "AI Console", "icon": "🤖", "app_id": "ai_console", "category": "development"},
        {"name": "Code Runner", "icon": "🚀", "app_id": "code_runner", "category": "development"},
        {"name": "Settings", "icon": "⚙️", "app_id": "settings", "category": "system"}
    ],
    "system": [
        {"name": "Shutdown", "icon": "⏻", "action": "shutdown"},
        {"name": "Restart", "icon": "↻", "action": "restart"},
        {"name": "Logout", "icon": "👤", "action": "logout"}
    ]
}
EOF
    
    # Download default wallpaper
    if ! [ -f "$HOME/.turbox/wallpapers/default.jpg" ]; then
        curl -s -o "$HOME/.turbox/wallpapers/default.jpg" \
            "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1920&h=1080&fit=crop"
    fi
    
    log "Environment setup complete"
}

create_launcher() {
    info "Creating launcher scripts..."
    
    # Create start-desktop script
    cat > "$INSTALL_DIR/start-desktop" << 'EOF'
#!/bin/bash
# TurboX Desktop Launcher

INSTALL_DIR="$HOME/.turbox"
cd "$INSTALL_DIR"

# Check if running in Termux
if [ -d "/data/data/com.termux" ]; then
    # Start X11 server if not running
    if ! pgrep -x "Xvfb" > /dev/null; then
        echo "Starting X11 server..."
        Xvfb :1 -screen 0 1024x768x24 &
        export DISPLAY=:1
    fi
fi

# Start TurboX Desktop
python3 desktop/main.py
EOF
    
    chmod +x "$INSTALL_DIR/start-desktop"
    
    # Create desktop entry for Linux
    if [ "$PLATFORM" != "termux" ] && [ "$PLATFORM" != "windows" ] && [ "$PLATFORM" != "macos" ]; then
        mkdir -p "$HOME/.local/share/applications"
        cat > "$HOME/.local/share/applications/turbox-desktop.desktop" << EOF
[Desktop Entry]
Name=TurboX Desktop
Comment=TurboX Desktop Environment
Exec=$INSTALL_DIR/start-desktop
Icon=applications-system
Type=Application
Categories=System;Utility;
StartupNotify=true
Terminal=false
EOF
        log "Desktop entry created"
    fi
    
    # Create bash alias
    if [ -f "$HOME/.bashrc" ]; then
        if ! grep -q "alias turbox=" "$HOME/.bashrc"; then
            echo "alias turbox='$INSTALL_DIR/start-desktop'" >> "$HOME/.bashrc"
        fi
    fi
    
    if [ -f "$HOME/.zshrc" ]; then
        if ! grep -q "alias turbox=" "$HOME/.zshrc"; then
            echo "alias turbox='$INSTALL_DIR/start-desktop'" >> "$HOME/.zshrc"
        fi
    fi
    
    log "Launcher scripts created"
}

post_install() {
    info "Running post-installation setup..."
    
    # Initialize database
    cd "$INSTALL_DIR"
    python3 -c "
from desktop.core.db_manager import DatabaseManager
db = DatabaseManager()
db.initialize()
print('Database initialized')
"
    
    # Set executable permissions
    find "$INSTALL_DIR" -name "*.py" -exec chmod +x {} \;
    
    log "Post-installation complete"
}

show_summary() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║               Installation Complete!                 ║"
    echo "╠══════════════════════════════════════════════════════╣"
    echo "║                                                    ║"
    echo "║  🎉 TurboX Desktop OS has been installed!           ║"
    echo "║                                                    ║"
    echo "║  To start TurboX:                                   ║"
    echo "║    $INSTALL_DIR/start-desktop                       ║"
    echo "║    or just type: turbox                             ║"
    echo "║                                                    ║"
    echo "║  📁 Installation directory:                         ║"
    echo "║    $INSTALL_DIR                                     ║"
    echo "║                                                    ║"
    echo "║  🚀 Features ready:                                 ║"
    echo "║    • Windows-style desktop                          ║"
    echo "║    • Start menu & taskbar                           ║"
    echo "║    • App launcher                                   ║"
    echo "║    • Terminal                                       ║"
    echo "║    • File manager                                   ║"
    echo "║    • API tools framework                            ║"
    echo "║                                                    ║"
    echo "║  Press Alt+F4 to exit the desktop environment       ║"
    echo "║                                                    ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

main() {
    header
    check_root
    
    PLATFORM=$(detect_platform)
    info "Detected platform: $PLATFORM"
    
    # Check dependencies
    if ! check_dependencies; then
        warn "Some dependencies are missing. They will be installed."
    fi
    
    # Platform-specific installation
    case "$PLATFORM" in
        "termux")
            install_termux
            ;;
        "debian"|"ubuntu")
            install_debian
            ;;
        "arch")
            install_arch
            ;;
        *)
            warn "Unsupported platform: $PLATFORM"
            warn "Manual dependency installation may be required"
            ;;
    esac
    
    # Install Python packages
    install_python_packages
    
    # Clone repository
    clone_repository
    
    # Setup environment
    setup_environment
    
    # Create launcher
    create_launcher
    
    # Post-installation
    post_install
    
    # Show summary
    show_summary
}

# Run installation
main "$@"
