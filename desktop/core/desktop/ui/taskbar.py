import tkinter as tk
from tkinter import ttk
import time
from datetime import datetime

class Taskbar:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, height=40, style='Taskbar.TFrame')
        self.app_buttons = {}
        self.start_menu = None
        
        self._setup_taskbar()
    
    def _setup_taskbar(self):
        """Setup the taskbar UI"""
        # Configure style
        style = ttk.Style()
        style.configure('Taskbar.TFrame', background='#2d2d30')
        
        # Start button
        self.start_button = tk.Button(
            self.frame,
            text="🏠 TurboX",
            bg='#007acc',
            fg='white',
            border=0,
            font=('Arial', 10, 'bold'),
            command=self.toggle_start_menu,
            width=12,
            height=2
        )
        self.start_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        # App buttons container
        self.apps_frame = ttk.Frame(self.frame)
        self.apps_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # System tray
        self.system_tray = ttk.Frame(self.frame)
        self.system_tray.pack(side=tk.RIGHT, padx=10)
        
        # Clock
        self.clock_label = tk.Label(
            self.system_tray,
            text=self._get_time(),
            fg='white',
            bg='#2d2d30',
            font=('Arial', 10)
        )
        self.clock_label.pack(side=tk.RIGHT, padx=5)
        
        # Update clock
        self._update_clock()
        
        # Pack taskbar at bottom
        self.frame.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _get_time(self):
        """Get current time"""
        return datetime.now().strftime("%H:%M:%S")
    
    def _update_clock(self):
        """Update clock every second"""
        self.clock_label.config(text=self._get_time())
        self.clock_label.after(1000, self._update_clock)
    
    def toggle_start_menu(self):
        """Toggle start menu visibility"""
        from desktop.ui.start_menu import StartMenu
        
        if self.start_menu and self.start_menu.winfo_exists():
            self.start_menu.destroy()
            self.start_menu = None
        else:
            self.start_menu = StartMenu(self.parent, self.start_button)
    
    def add_app_button(self, app_name, app_id, command):
        """Add application button to taskbar"""
        btn = tk.Button(
            self.apps_frame,
            text=app_name,
            bg='#3e3e42',
            fg='white',
            border=0,
            font=('Arial', 9),
            command=command,
            width=15
        )
        btn.pack(side=tk.LEFT, padx=2)
        self.app_buttons[app_id] = btn
    
    def remove_app_button(self, app_id):
        """Remove application button"""
        if app_id in self.app_buttons:
            self.app_buttons[app_id].destroy()
            del self.app_buttons[app_id]
