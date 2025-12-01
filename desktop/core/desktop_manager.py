import tkinter as tk
from tkinter import ttk
import os
import json
from typing import Dict, List

class DesktopManager:
    def __init__(self, root):
        self.root = root
        self.windows = []
        self.apps = {}
        self.desktop_icons = []
        
        # Load configuration
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load desktop configuration"""
        config_path = os.path.expanduser('~/.turbox/config/desktop.json')
        default_config = {
            "theme": "dark",
            "wallpaper": "default",
            "icons": True,
            "animations": True
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return {**default_config, **json.load(f)}
            except:
                return default_config
        return default_config
    
    def create_desktop_icon(self, icon_config: Dict):
        """Create a desktop icon"""
        from desktop.ui.desktop_icons import DesktopIcon
        
        icon = DesktopIcon(self.root, icon_config)
        self.desktop_icons.append(icon)
        return icon
    
    def launch_app(self, app_id: str):
        """Launch an application by ID"""
        try:
            if app_id == "app_store":
                from apps.app_store.app_store import AppStore
                app = AppStore()
            elif app_id == "file_manager":
                from apps.file_manager.file_manager import FileManager
                app = FileManager()
            elif app_id == "terminal":
                from apps.terminal.terminal_app import TerminalApp
                app = TerminalApp()
            elif app_id == "api_tools":
                from apps.api_tools.api_launcher import APITools
                app = APITools()
            else:
                print(f"Unknown app: {app_id}")
                return
                
            app.launch()
            self.apps[app_id] = app
            
        except Exception as e:
            print(f"Failed to launch {app_id}: {e}")
    
    def shutdown(self):
        """Shutdown all applications"""
        for app_id, app in self.apps.items():
            try:
                app.close()
            except:
                pass
        print("🔄 TurboX Desktop shutdown complete")
