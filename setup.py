#!/usr/bin/env python3
"""
TurboX Desktop Setup Script
"""
import os
import sys
import json
import subprocess
from pathlib import Path

def setup_turbox():
    """Setup TurboX Desktop Environment"""
    
    print("🚀 Setting up TurboX Desktop...")
    
    # Get installation directory
    install_dir = Path.home() / ".turbox"
    config_dir = install_dir / "config"
    apps_dir = install_dir / "apps"
    data_dir = install_dir / "data"
    
    # Create directories
    for directory in [install_dir, config_dir, apps_dir, data_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Create default configuration
    config = {
        "theme": "dark",
        "wallpaper": "default",
        "icons": True,
        "animations": True,
        "install_dir": str(install_dir)
    }
    
    config_file = config_dir / "desktop.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ TurboX setup complete!")
    print(f"📁 Installation directory: {install_dir}")
    print("🎮 Start with: python3 desktop/main.py")

if __name__ == "__main__":
    setup_turbox()
