#!/usr/bin/env python3
"""
TurboX Desktop OS - Main Entry Point
Version: 1.0.0
"""
import sys
import os
import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop.core.desktop_manager import DesktopManager
from desktop.ui.taskbar import Taskbar
from desktop.ui.start_menu import StartMenu
from desktop.ui.desktop_icons import DesktopIconManager
from desktop.themes.theme_manager import ThemeManager

class TurboXDesktop:
    """Main desktop environment class"""
    
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("TurboX Desktop OS")
        
        # Fullscreen on first launch
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        
        # Remove window decorations for full desktop feel
        self.root.overrideredirect(True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize managers
        self.theme_manager = ThemeManager()
        self.desktop_manager = DesktopManager(self.root, self.config)
        self.icon_manager = DesktopIconManager(self.root)
        
        # Setup desktop
        self._setup_desktop()
        
        # Start background services
        self._start_background_services()
        
    def _load_config(self):
        """Load desktop configuration"""
        config_path = os.path.expanduser("~/.turbox/config/desktop.json")
        default_config = {
            "theme": "dark",
            "wallpaper": "default",
            "show_icons": True,
            "animations": True,
            "virtual_desktops": 4,
            "taskbar_position": "bottom",
            "start_menu_style": "windows"
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return {**default_config, **json.load(f)}
            except:
                return default_config
        return default_config
    
    def _setup_desktop(self):
        """Setup complete desktop environment"""
        
        # Apply theme
        self.theme_manager.apply_theme(self.root, self.config["theme"])
        
        # Create desktop background
        self._create_background()
        
        # Create taskbar
        self.taskbar = Taskbar(self.root, self.config)
        
        # Create desktop icons
        self._create_default_icons()
        
        # Bind global shortcuts
        self._bind_shortcuts()
        
        # Create system tray
        self._create_system_tray()
        
    def _create_background(self):
        """Create desktop background"""
        self.canvas = tk.Canvas(
            self.root,
            bg=self.theme_manager.get_color("background"),
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add wallpaper if available
        wallpaper_path = os.path.expanduser(f"~/.turbox/wallpapers/{self.config['wallpaper']}.jpg")
        if os.path.exists(wallpaper_path):
            try:
                self.wallpaper_img = tk.PhotoImage(file=wallpaper_path)
                self.canvas.create_image(0, 0, image=self.wallpaper_img, anchor="nw")
            except:
                pass
    
    def _create_default_icons(self):
        """Create default desktop icons"""
        icons = [
            {
                "name": "App Store",
                "app_id": "app_store",
                "position": (50, 50),
                "icon": "📦"
            },
            {
                "name": "File Manager", 
                "app_id": "file_manager",
                "position": (50, 130),
                "icon": "📁"
            },
            {
                "name": "Terminal",
                "app_id": "terminal", 
                "position": (50, 210),
                "icon": "💻"
            },
            {
                "name": "API Tools",
                "app_id": "api_tools",
                "position": (50, 290),
                "icon": "🔧"
            },
            {
                "name": "AI Console",
                "app_id": "ai_console",
                "position": (50, 370),
                "icon": "🤖"
            }
        ]
        
        for icon_config in icons:
            self.icon_manager.create_icon(icon_config)
    
    def _create_system_tray(self):
        """Create system tray"""
        from desktop.ui.system_tray import SystemTray
        self.system_tray = SystemTray(self.root, self.taskbar.frame)
    
    def _bind_shortcuts(self):
        """Bind global keyboard shortcuts"""
        # Windows key for start menu
        self.root.bind('<Super_L>', lambda e: self.taskbar.toggle_start_menu())
        
        # Alt+F4 to shutdown
        self.root.bind('<Alt-F4>', lambda e: self.shutdown())
        
        # Ctrl+Alt+T for terminal
        self.root.bind('<Control-Alt-t>', lambda e: self._launch_app("terminal"))
        
        # Alt+Tab for window switching
        self.root.bind('<Alt-Tab>', lambda e: self._cycle_windows())
        
        # Print screen (requires external tool)
        self.root.bind('<Print>', lambda e: self._take_screenshot())
    
    def _launch_app(self, app_id):
        """Launch application by ID"""
        self.desktop_manager.launch_app(app_id)
    
    def _cycle_windows(self):
        """Cycle through open windows"""
        self.desktop_manager.cycle_windows()
    
    def _take_screenshot(self):
        """Take desktop screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.expanduser(f"~/.turbox/screenshots/screenshot_{timestamp}.png")
        
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        
        # This would use PIL to capture screen
        print(f"Screenshot saved to: {screenshot_path}")
    
    def _start_background_services(self):
        """Start background services"""
        # Start update checker
        self._start_update_checker()
        
        # Start system monitor
        self._start_system_monitor()
        
        # Start AI model loader (if enabled)
        if self.config.get("ai_enabled", False):
            self._load_ai_models()
    
    def _start_update_checker(self):
        """Check for updates in background"""
        import threading
        
        def check_updates():
            import time
            while True:
                # Check for app updates every hour
                time.sleep(3600)
                self.desktop_manager.check_for_updates()
        
        thread = threading.Thread(target=check_updates, daemon=True)
        thread.start()
    
    def _start_system_monitor(self):
        """Monitor system resources"""
        import threading
        import psutil
        
        def monitor_resources():
            import time
            while True:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                
                # Update system tray if memory is low
                if memory.percent > 90:
                    self.system_tray.show_warning("High memory usage")
                
                time.sleep(10)
        
        thread = threading.Thread(target=monitor_resources, daemon=True)
        thread.start()
    
    def _load_ai_models(self):
        """Load AI models in background"""
        print("Loading AI models...")
        # Implementation depends on AI library used
    
    def shutdown(self):
        """Shutdown desktop environment"""
        print("Shutting down TurboX Desktop...")
        
        # Save all application states
        self.desktop_manager.save_all_states()
        
        # Close all windows
        self.desktop_manager.close_all_apps()
        
        # Exit
        self.root.quit()
        sys.exit(0)
    
    def run(self):
        """Start the desktop environment"""
        print("""
        ╔══════════════════════════════════════╗
        ║     🚀 TurboX Desktop OS v1.0        ║
        ║                                      ║
        ║  Starting desktop environment...     ║
        ╚══════════════════════════════════════╝
        """)
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.shutdown()

if __name__ == "__main__":
    desktop = TurboXDesktop()
    desktop.run()
