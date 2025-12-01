#!/usr/bin/env python3
"""
TurboX Desktop Environment - Main Entry Point
"""
import tkinter as tk
from desktop.core.desktop_manager import DesktopManager
from desktop.ui.taskbar import Taskbar
from desktop.ui.start_menu import StartMenu
import sys
import os

class TurboXDesktop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TurboX Desktop")
        self.root.geometry("1024x768")
        self.root.configure(bg='#1e1e1e')
        
        # Make fullscreen
        self.root.attributes('-fullscreen', True)
        
        # Initialize desktop manager
        self.desktop_manager = DesktopManager(self.root)
        
        # Setup desktop
        self._setup_desktop()
        
    def _setup_desktop(self):
        """Setup the complete desktop environment"""
        # Create desktop background
        self.canvas = tk.Canvas(
            self.root, 
            bg='#1e1e1e',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create taskbar
        self.taskbar = Taskbar(self.root)
        
        # Create desktop icons
        self._create_desktop_icons()
        
        # Bind keyboard shortcuts
        self._bind_shortcuts()
        
    def _create_desktop_icons(self):
        """Create default desktop icons"""
        icons = [
            {"name": "App Store", "app_id": "app_store", "position": (50, 50)},
            {"name": "File Manager", "app_id": "file_manager", "position": (50, 120)},
            {"name": "Terminal", "app_id": "terminal", "position": (50, 190)},
            {"name": "API Tools", "app_id": "api_tools", "position": (50, 260)},
        ]
        
        for icon_config in icons:
            self.desktop_manager.create_desktop_icon(icon_config)
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Alt-F4>', lambda e: self.shutdown())
        self.root.bind('<Control-Alt-t>', lambda e: self.launch_terminal())
        self.root.bind('<Super>', lambda e: self.taskbar.toggle_start_menu())
        
    def launch_terminal(self):
        """Launch terminal application"""
        from apps.terminal.terminal_app import TerminalApp
        terminal = TerminalApp()
        terminal.launch()
        
    def shutdown(self):
        """Shutdown desktop environment"""
        self.desktop_manager.shutdown()
        self.root.quit()
        
    def run(self):
        """Start the desktop environment"""
        print("🚀 TurboX Desktop starting...")
        self.root.mainloop()

if __name__ == "__main__":
    desktop = TurboXDesktop()
    desktop.run()
