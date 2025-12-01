import tkinter as tk
from tkinter import ttk

class StartMenu:
    def __init__(self, parent, start_button):
        self.parent = parent
        self.start_button = start_button
        
        # Create menu window
        self.menu = tk.Toplevel(parent)
        self.menu.overrideredirect(True)
        self.menu.configure(bg='#1e1e1e', relief='raised', border=1)
        
        # Position above start button
        x = start_button.winfo_rootx()
        y = start_button.winfo_rooty() - 400
        self.menu.geometry(f"300x400+{x}+{y}")
        
        # Setup menu
        self._setup_menu()
        
        # Bind focus out
        self.menu.bind("<FocusOut>", self._on_focus_out)
        self.menu.focus_set()
    
    def _setup_menu(self):
        """Setup start menu content"""
        # Header
        header = tk.Frame(self.menu, bg='#007acc', height=60)
        header.pack(fill=tk.X)
        
        title = tk.Label(
            header,
            text="TurboX Desktop",
            fg='white',
            bg='#007acc',
            font=('Arial', 14, 'bold')
        )
        title.pack(pady=20)
        
        # App list
        app_frame = tk.Frame(self.menu, bg='#1e1e1e')
        app_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Application buttons
        apps = [
            ("📱 App Store", "app_store"),
            ("📁 File Manager", "file_manager"), 
            ("💻 Terminal", "terminal"),
            ("🔧 API Tools", "api_tools"),
            ("🤖 AI Console", "ai_console"),
            ("⚙️ Settings", "settings")
        ]
        
        for app_name, app_id in apps:
            btn = tk.Button(
                app_frame,
                text=app_name,
                bg='#2d2d30',
                fg='white',
                font=('Arial', 11),
                border=0,
                anchor='w',
                command=lambda aid=app_id: self._launch_app(aid),
                width=25
            )
            btn.pack(fill=tk.X, pady=2)
    
    def _launch_app(self, app_id):
        """Launch application and close menu"""
        from desktop.core.desktop_manager import DesktopManager
        
        # Get desktop manager instance
        for child in self.parent.winfo_children():
            if isinstance(child, tk.Canvas):
                desktop_manager = DesktopManager(self.parent)
                desktop_manager.launch_app(app_id)
                break
        
        self.menu.destroy()
    
    def _on_focus_out(self, event):
        """Close menu when focus lost"""
        self.menu.destroy()
