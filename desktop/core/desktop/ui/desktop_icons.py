import tkinter as tk
from tkinter import ttk

class DesktopIcon:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.canvas = parent  # Assuming parent is the desktop canvas
        
        self._create_icon()
    
    def _create_icon(self):
        """Create desktop icon"""
        x, y = self.config.get('position', (50, 50))
        
        # Icon container
        self.frame = tk.Frame(
            self.canvas,
            bg='#1e1e1e',
            padx=5,
            pady=5
        )
        
        # Place on canvas (using place for absolute positioning)
        self.frame.place(x=x, y=y)
        
        # Icon "image" (using emoji for now)
        self.icon_label = tk.Label(
            self.frame,
            text="📁",  # Default icon
            font=('Arial', 24),
            bg='#1e1e1e',
            fg='white'
        )
        self.icon_label.pack()
        
        # App name
        self.name_label = tk.Label(
            self.frame,
            text=self.config['name'],
            font=('Arial', 9),
            bg='#1e1e1e', 
            fg='white',
            wraplength=80
        )
        self.name_label.pack()
        
        # Bind events
        self._bind_events()
    
    def _bind_events(self):
        """Bind mouse events to icon"""
        self.frame.bind("<Button-1>", self._on_click)
        self.frame.bind("<Double-Button-1>", self._on_double_click)
        self.icon_label.bind("<Button-1>", self._on_click)
        self.icon_label.bind("<Double-Button-1>", self._on_double_click)
        self.name_label.bind("<Button-1>", self._on_click)
        self.name_label.bind("<Double-Button-1>", self._on_double_click)
    
    def _on_click(self, event):
        """Select icon on click"""
        self._highlight_icon()
    
    def _on_double_click(self, event):
        """Launch app on double click"""
        self._launch_app()
    
    def _highlight_icon(self):
        """Highlight selected icon"""
        # Change background to show selection
        self.frame.configure(bg='#007acc')
        self.name_label.configure(bg='#007acc')
    
    def _launch_app(self):
        """Launch the associated application"""
        from desktop.core.desktop_manager import DesktopManager
        
        # Get desktop manager and launch app
        desktop_manager = DesktopManager(self.parent)
        desktop_manager.launch_app(self.config['app_id'])
