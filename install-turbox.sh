#!/bin/bash
# TurboX Desktop Environment Installer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
INSTALL_DIR="$HOME/.turbox"
REPO_URL="https://github.com/turbox-project/turbox-desktop.git"

log() {
    echo -e "${GREEN}[TurboX]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[Warning]${NC} $1"
}

error() {
    echo -e "${RED}[Error]${NC} $1"
}

check_dependencies() {
    log "Checking dependencies..."
    
    # Check for Termux
    if [ -d "/data/data/com.termux" ]; then
        log "Termux environment detected"
        IS_TERMUX=true
    else
        IS_TERMUX=false
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python3 is required but not installed"
        exit 1
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        error "Git is required but not installed"
        exit 1
    fi
    
    log "Dependencies check passed"
}

install_termux_deps() {
    log "Installing Termux dependencies..."
    
    pkg update -y
    pkg install -y python git tk x11-repo tur-repo
    pkg install -y xfce4-terminal
    
    log "Termux dependencies installed"
}

install_system_deps() {
    log "Installing system dependencies..."
    
    if command -v apt &> /dev/null; then
        # Debian/Ubuntu
        sudo apt update
        sudo apt install -y python3 python3-tk git python3-pip
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        sudo pacman -S python tk git
    elif command -v dnf &> /dev/null; then
        # Fedora
        sudo dnf install -y python3 python3-tkinter git
    else
        warn "Unknown package manager - please install python3-tk manually"
    fi
    
    log "System dependencies installed"
}

clone_repository() {
    log "Downloading TurboX Desktop..."
    
    if [ -d "$INSTALL_DIR" ]; then
        warn "Installation directory exists - updating..."
        cd "$INSTALL_DIR"
        git pull
    else
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi
    
    cd "$INSTALL_DIR"
}

setup_environment() {
    log "Setting up environment..."
    
    # Create necessary directories
    mkdir -p "$HOME/.turbox/config"
    mkdir -p "$HOME/.turbox/apps"
    mkdir -p "$HOME/.turbox/data"
    
    # Create desktop configuration
    cat > "$HOME/.turbox/config/desktop.json" << EOF
{
    "theme": "dark",
    "wallpaper": "default",
    "icons": true,
    "animations": true,
    "install_dir": "$INSTALL_DIR"
}
EOF

    # Make main script executable
    chmod +x "$INSTALL_DIR/desktop/main.py"
    
    log "Environment setup complete"
}

create_launch_script() {
    log "Creating launch scripts..."
    
    # Create start-desktop command
    cat > "$INSTALL_DIR/start-desktop" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 desktop/main.py
EOF

    chmod +x "$INSTALL_DIR/start-desktop"
    
    # Create desktop entry (for Linux systems)
    if [ "$IS_TERMUX" = false ]; then
        mkdir -p "$HOME/.local/share/applications"
        cat > "$HOME/.local/share/applications/turbox-desktop.desktop" << EOF
[Desktop Entry]
Name=TurboX Desktop
Comment=TurboX Desktop Environment
Exec=$INSTALL_DIR/start-desktop
Icon=terminal
Type=Application
Categories=System;
EOF
    fi
    
    log "Launch scripts created"
}

main() {
    log "🚀 Starting TurboX Desktop Installation"
    
    check_dependencies
    
    if [ "$IS_TERMUX" = true ]; then
        install_termux_deps
    else
        install_system_deps
    fi
    
    clone_repository
    setup_environment
    create_launch_script
    
    log "🎉 Installation completed successfully!"
    log ""
    log "To start TurboX Desktop:"
    log "  $INSTALL_DIR/start-desktop"
    log ""
    log "Features available:"
    log "  • Desktop with icons and taskbar"
    log "  • Start menu with app launcher" 
    log "  • Terminal application"
    log "  • File manager"
    log "  • App store"
    log ""
    log "Press Alt+F4 to exit the desktop environment"
}

# Run installation
main "$@"
