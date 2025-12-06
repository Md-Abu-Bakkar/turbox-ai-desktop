#!/data/data/com.termux/files/usr/bin/python3
# ==============================================================================
# TurboX Desktop OS - Window Manager
# Phase 1: Basic Window Controls
# ==============================================================================

import os
import sys
import subprocess
import time
from datetime import datetime

class TurboXWindowManager:
    """Manage desktop windows and UI interactions"""
    
    def __init__(self):
        self.home_dir = os.path.expanduser("~")
        self.config_dir = os.path.join(self.home_dir, '.turboX')
        self.windows_file = os.path.join(self.config_dir, 'config', 'windows.json')
        
        # Window tracking
        self.windows = {}
        self.window_counter = 0
        
        # Load saved window positions
        self.load_window_positions()
    
    def load_window_positions(self):
        """Load saved window positions from file"""
        try:
            if os.path.exists(self.windows_file):
                with open(self.windows_file, 'r') as f:
                    import json
                    self.window_positions = json.load(f)
            else:
                self.window_positions = {}
        except Exception as e:
            print(f"⚠️  Window positions load error: {e}")
            self.window_positions = {}
    
    def save_window_positions(self):
        """Save current window positions to file"""
        try:
            with open(self.windows_file, 'w') as f:
                import json
                json.dump(self.window_positions, f, indent=2)
        except Exception as e:
            print(f"❌ Window positions save error: {e}")
    
    def create_window(self, title, width=800, height=600, x=None, y=None):
        """Create a new desktop window (placeholder for Phase 2)"""
        window_id = f"window_{self.window_counter}"
        self.window_counter += 1
        
        # Default position (staggered)
        if x is None:
            x = 50 + (self.window_counter % 5) * 30
        if y is None:
            y = 50 + (self.window_counter % 5) * 30
        
        # Save window info
        self.windows[window_id] = {
            "id": window_id,
            "title": title,
            "width": width,
            "height": height,
            "x": x,
            "y": y,
            "created": datetime.now().isoformat(),
            "visible": True,
            "minimized": False,
            "maximized": False
        }
        
        # Save position
        self.window_positions[window_id] = {"x": x, "y": y}
        self.save_window_positions()
        
        print(f"📁 Created window: {title} ({window_id}) at {x},{y}")
        return window_id
    
    def close_window(self, window_id):
        """Close a window"""
        if window_id in self.windows:
            print(f"📁 Closing window: {self.windows[window_id]['title']}")
            del self.windows[window_id]
            
            # Also remove from positions
            if window_id in self.window_positions:
                del self.window_positions[window_id]
                self.save_window_positions()
            
            return True
        return False
    
    def minimize_window(self, window_id):
        """Minimize a window"""
        if window_id in self.windows:
            self.windows[window_id]["minimized"] = True
            self.windows[window_id]["visible"] = False
            print(f"📁 Minimized: {self.windows[window_id]['title']}")
            return True
        return False
    
    def maximize_window(self, window_id):
        """Maximize a window"""
        if window_id in self.windows:
            was_maximized = self.windows[window_id]["maximized"]
            self.windows[window_id]["maximized"] = not was_maximized
            
            if was_maximized:
                print(f"📁 Restored: {self.windows[window_id]['title']}")
            else:
                print(f"📁 Maximized: {self.windows[window_id]['title']}")
            
            return True
        return False
    
    def move_window(self, window_id, x, y):
        """Move a window to new position"""
        if window_id in self.windows:
            old_pos = (self.windows[window_id]["x"], self.windows[window_id]["y"])
            self.windows[window_id]["x"] = x
            self.windows[window_id]["y"] = y
            
            # Update saved position
            self.window_positions[window_id] = {"x": x, "y": y}
            self.save_window_positions()
            
            print(f"📁 Moved {self.windows[window_id]['title']}: {old_pos} → ({x},{y})")
            return True
        return False
    
    def resize_window(self, window_id, width, height):
        """Resize a window"""
        if window_id in self.windows:
            old_size = (self.windows[window_id]["width"], self.windows[window_id]["height"])
            self.windows[window_id]["width"] = width
            self.windows[window_id]["height"] = height
            
            print(f"📁 Resized {self.windows[window_id]['title']}: {old_size} → ({width},{height})")
            return True
        return False
    
    def list_windows(self):
        """List all managed windows"""
        return list(self.windows.keys())
    
    def get_window_info(self, window_id):
        """Get information about a specific window"""
        return self.windows.get(window_id, {})
    
    def get_active_windows(self):
        """Get all currently visible (not minimized) windows"""
        active = []
        for window_id, info in self.windows.items():
            if info.get("visible", True) and not info.get("minimized", False):
                active.append(window_id)
        return active
    
    def bring_to_front(self, window_id):
        """Bring a window to the front (z-order)"""
        # In Phase 1, just mark as recently accessed
        if window_id in self.windows:
            self.windows[window_id]["last_access"] = datetime.now().isoformat()
            print(f"📁 Brought to front: {self.windows[window_id]['title']}")
            return True
        return False
    
    def tile_windows(self, arrangement="horizontal"):
        """Arrange windows in a tiled pattern"""
        active_windows = self.get_active_windows()
        if not active_windows:
            return
        
        screen_width = 1366  # Default, will be detected in Phase 2
        screen_height = 768
        
        if arrangement == "horizontal":
            # Horizontal split
            window_width = screen_width // len(active_windows)
            for i, window_id in enumerate(active_windows):
                x = i * window_width
                self.move_window(window_id, x, 0)
                self.resize_window(window_id, window_width, screen_height)
        
        elif arrangement == "vertical":
            # Vertical split
            window_height = screen_height // len(active_windows)
            for i, window_id in enumerate(active_windows):
                y = i * window_height
                self.move_window(window_id, 0, y)
                self.resize_window(window_id, screen_width, window_height)
        
        print(f"📁 Tiled {len(active_windows)} windows ({arrangement})")
    
    def cascade_windows(self):
        """Arrange windows in a cascading pattern"""
        active_windows = self.get_active_windows()
        if not active_windows:
            return
        
        start_x, start_y = 30, 30
        step_x, step_y = 30, 30
        
        for i, window_id in enumerate(active_windows):
            x = start_x + (i * step_x)
            y = start_y + (i * step_y)
            self.move_window(window_id, x, y)
            # Default size for cascaded windows
            self.resize_window(window_id, 600, 400)
        
        print(f"📁 Cascaded {len(active_windows)} windows")
    
    def run_window_command(self, command, window_id=None):
        """Execute a window management command"""
        if command == "tile_horizontal":
            self.tile_windows("horizontal")
        elif command == "tile_vertical":
            self.tile_windows("vertical")
        elif command == "cascade":
            self.cascade_windows()
        elif command == "minimize_all":
            for win_id in self.get_active_windows():
                self.minimize_window(win_id)
        elif command == "close_all":
            for win_id in list(self.windows.keys()):
                self.close_window(win_id)
        elif command == "list":
            print("📋 Managed Windows:")
            for win_id, info in self.windows.items():
                state = "MIN" if info.get("minimized") else "VIS" if info.get("visible") else "HID"
                print(f"  {win_id}: {info['title']} [{state}] {info['width']}x{info['height']}")
        else:
            print(f"❌ Unknown command: {command}")
    
    def monitor_x11_windows(self):
        """Monitor actual X11 windows (Phase 2 placeholder)"""
        print("⚠️  X11 window monitoring available in Phase 2")
        return []
    
    def get_desktop_info(self):
        """Get desktop environment information"""
        info = {
            "window_manager": "TurboX Window Manager (Phase 1)",
            "total_windows": len(self.windows),
            "active_windows": len(self.get_active_windows()),
            "screen_resolution": "1366x768 (default)",
            "theme": "Windows Dark",
            "supports": ["move", "resize", "minimize", "maximize", "close"],
            "phase": 1
        }
        return info

# Command-line interface for testing
def main():
    """Command-line interface for window manager"""
    wm = TurboXWindowManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            title = sys.argv[2] if len(sys.argv) > 2 else "New Window"
            wm.create_window(title)
        
        elif command == "close":
            window_id = sys.argv[2] if len(sys.argv) > 2 else None
            if window_id and window_id in wm.windows:
                wm.close_window(window_id)
            else:
                print("❌ Please specify a valid window ID")
        
        elif command == "list":
            wm.run_window_command("list")
        
        elif command == "tile":
            arrangement = sys.argv[2] if len(sys.argv) > 2 else "horizontal"
            wm.tile_windows(arrangement)
        
        elif command == "cascade":
            wm.cascade_windows()
        
        elif command == "info":
            info = wm.get_desktop_info()
            import json
            print(json.dumps(info, indent=2))
        
        else:
            print("Available commands:")
            print("  create <title>    - Create new window")
            print("  close <window_id> - Close window")
            print("  list              - List all windows")
            print("  tile [horizontal|vertical] - Tile windows")
            print("  cascade           - Cascade windows")
            print("  info              - Show desktop info")
    else:
        print("TurboX Window Manager (Phase 1)")
        print("Run with a command, e.g.: python window_manager.py create 'My Window'")

if __name__ == "__main__":
    main()
