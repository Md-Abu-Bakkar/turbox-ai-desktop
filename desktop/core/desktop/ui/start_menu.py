import tkinter as tk
from tkinter import ttk
import os
import json

class StartMenu:
    """Windows-style start menu"""
    
    def __init__(self, root, start_button):
        self.root = root
        self.start_button = start_button
        self.window = None
        
        # Load menu items
        self.menu_items = self._load_menu_items()
    
    def _load_menu_items(self):
        """Load start menu items from configuration"""
        items_path = os.path.expanduser("~/.turbox/config/start_menu.json")
        
        default_items = {
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
        
        if os.path.exists(items_path):
            try:
                with open(items_path, 'r') as f:
                    return json.load(f)
            except:
                return default_items
        
        return default_items
    
    def show(self):
        """Show the start menu"""
        if self.window and self.window.winfo_exists():
            self.window.destroy()
        
        # Create menu window
        self.window = tk.Toplevel(self.root)
        self.window.overrideredirect(True)
        self.window.configure(bg='#1e1e1e', relief='raised', borderwidth=1)
        
        # Position above start button
        x = self.start_button.winfo_rootx()
        y = self.start_button.winfo_rooty() - 450
        self.window.geometry(f"300x450+{x}+{y}")
        
        # Make sure it's on top
        self.window.attributes('-topmost', True)
        
        # Setup menu UI
        self._setup_ui()
        
        # Bind focus out
        self.window.bind('<FocusOut>', self._on_focus_out)
        
        # Give focus
        self.window.focus_set()
    
    def _setup_ui(self):
        """Setup start menu UI"""
        # Header
        header = tk.Frame(self.window, bg='#007acc', height=80)
        header.pack(fill=tk.X)
        
        # User info
        user_frame = tk.Frame(header, bg='#007acc')
        user_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        user_icon = tk.Label(
            user_frame,
            text="👤",
            bg='#007acc',
            fg='white',
            font=('Segoe UI', 20)
        )
        user_icon.pack(side=tk.LEFT)
        
        user_info = tk.Frame(user_frame, bg='#007acc')
        user_info.pack(side=tk.LEFT, padx=10)
        
        username = os.getlogin()
        tk.Label(
            user_info,
            text=username,
            bg='#007acc',
            fg='white',
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor='w')
        
        tk.Label(
            user_info,
            text="TurboX Desktop",
            bg='#007acc',
            fg='#e0e0e0',
            font=('Segoe UI', 9)
        ).pack(anchor='w')
        
        # Search box
        search_frame = tk.Frame(self.window, bg='#2d2d30', height=40)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        search_entry = tk.Entry(
            search_frame,
            bg='#3e3e42',
            fg='white',
            insertbackground='white',
            relief='flat',
            font=('Segoe UI', 10)
        )
        search_entry.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)
        search_entry.insert(0, "Type here to search...")
        
        # Bind search functionality
        search_entry.bind('<FocusIn>', lambda e: self._on_search_focus(e, search_entry))
        search_entry.bind('<FocusOut>', lambda e: self._on_search_blur(e, search_entry))
        search_entry.bind('<KeyRelease>', lambda e: self._on_search_key(e, search_entry))
        
        # App list
        app_list_frame = tk.Frame(self.window, bg='#1e1e1e')
        app_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create scrollable canvas
        canvas = tk.Canvas(app_list_frame, bg='#1e1e1e', highlightthickness=0)
        scrollbar = tk.Scrollbar(app_list_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1e1e1e')
        
        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add app buttons
        for i, app in enumerate(self.menu_items['apps']):
            self._create_app_button(scrollable_frame, app, i)
        
        # Pack scrollable area
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # System actions
        system_frame = tk.Frame(self.window, bg='#252526', height=40)
        system_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        for action in self.menu_items['system']:
            self._create_system_button(system_frame, action)
    
    def _create_app_button(self, parent, app_config, index):
        """Create application button"""
        btn_frame = tk.Frame(
            parent,
            bg='#1e1e1e',
            height=40
        )
        btn_frame.pack(fill=tk.X, pady=1)
        
        # Button
        btn = tk.Button(
            btn_frame,
            text=f"  {app_config['icon']}  {app_config['name']}",
            bg='#1e1e1e',
            fg='white',
            activebackground='#2d2d30',
            activeforeground='white',
            border=0,
            font=('Segoe UI', 10),
            anchor='w',
            cursor='hand2',
            command=lambda a=app_config: self._launch_app(a)
        )
        btn.pack(fill=tk.BOTH, expand=True)
        
        # Hover effects
        btn.bind('<Enter>', lambda e, f=btn_frame: f.config(bg='#2d2d30'))
        btn.bind('<Leave>', lambda e, f=btn_frame: f.config(bg='#1e1e1e'))
    
    def _create_system_button(self, parent, action_config):
        """Create system action button"""
        btn = tk.Button(
            parent,
            text=f"  {action_config['icon']}  {action_config['name']}",
            bg='#252526',
            fg='white',
            activebackground='#2d2d30',
            activeforeground='white',
            border=0,
            font=('Segoe UI', 9),
            anchor='w',
            cursor='hand2',
            command=lambda a=action_config: self._execute_system_action(a)
        )
        btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    def _launch_app(self, app_config):
        """Launch application from start menu"""
        # Import desktop manager
        from desktop.core.desktop_manager import DesktopManager
        
        # Find desktop manager instance
        for child in self.root.winfo_children():
            if hasattr(child, 'desktop_manager'):
                child.desktop_manager.launch_app(app_config['app_id'])
                break
        
        # Close start menu
        self.window.destroy()
    
    def _execute_system_action(self, action_config):
        """Execute system action"""
        action = action_config['action']
        
        if action == 'shutdown':
            # Find desktop instance and shutdown
            for child in self.root.winfo_children():
                if hasattr(child, 'shutdown'):
                    child.shutdown()
                    break
        
        elif action == 'restart':
            print("Restart functionality would be implemented here")
            # Would restart the desktop environment
        
        elif action == 'logout':
            print("Logout functionality would be implemented here")
            # Would logout current session
        
        # Close start menu
        self.window.destroy()
    
    def _on_search_focus(self, event, entry):
        """Handle search focus"""
        if entry.get() == "Type here to search...":
            entry.delete(0, tk.END)
            entry.config(fg='white')
    
    def _on_search_blur(self, event, entry):
        """Handle search blur"""
        if not entry.get():
            entry.insert(0, "Type here to search...")
            entry.config(fg='gray')
    
    def _on_search_key(self, event, entry):
        """Handle search typing"""
        # Search functionality would filter apps
        pass
    
    def _on_focus_out(self, event):
        """Close menu when focus lost"""
        # Only close if focus goes to another window
        if event.widget != self.window:
            self.window.destroy()
