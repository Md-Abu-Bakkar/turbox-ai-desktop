import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
import time

class Taskbar:
    """Windows-style taskbar"""
    
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.app_buttons = {}
        self.start_menu = None
        
        # Colors based on theme
        self.colors = {
            'dark': {
                'bg': '#2d2d30',
                'fg': '#ffffff',
                'hover': '#3e3e42',
                'pressed': '#007acc'
            },
            'light': {
                'bg': '#f3f2f1',
                'fg': '#323130',
                'hover': '#e1dfdd',
                'pressed': '#0078d4'
            }
        }
        
        theme = config.get('theme', 'dark')
        self.colors = self.colors.get(theme, self.colors['dark'])
        
        self._setup_taskbar()
    
    def _setup_taskbar(self):
        """Setup taskbar UI"""
        # Main frame
        self.frame = tk.Frame(
            self.root,
            bg=self.colors['bg'],
            height=40,
            relief='raised',
            borderwidth=1
        )
        
        # Start button
        self._create_start_button()
        
        # App buttons area
        self.apps_frame = tk.Frame(self.frame, bg=self.colors['bg'])
        self.apps_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # System tray area
        self.tray_frame = tk.Frame(self.frame, bg=self.colors['bg'])
        self.tray_frame.pack(side=tk.RIGHT, padx=5)
        
        # Clock
        self._create_clock()
        
        # Network indicator
        self._create_network_indicator()
        
        # Battery indicator (if applicable)
        self._create_battery_indicator()
        
        # Volume indicator
        self._create_volume_indicator()
        
        # Pack taskbar at bottom
        self.frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Start menu (hidden initially)
        self._create_start_menu()
    
    def _create_start_button(self):
        """Create Windows-style start button"""
        self.start_button = tk.Button(
            self.frame,
            text=" 🚀 TurboX",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            activebackground=self.colors['hover'],
            activeforeground=self.colors['fg'],
            border=0,
            font=('Segoe UI', 10, 'bold'),
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.toggle_start_menu
        )
        self.start_button.pack(side=tk.LEFT)
        
        # Hover effects
        self.start_button.bind('<Enter>', lambda e: self.start_button.config(bg=self.colors['hover']))
        self.start_button.bind('<Leave>', lambda e: self.start_button.config(bg=self.colors['bg']))
    
    def _create_clock(self):
        """Create digital clock"""
        self.clock_label = tk.Label(
            self.tray_frame,
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=('Segoe UI', 9)
        )
        self.clock_label.pack(side=tk.RIGHT, padx=5)
        
        # Update clock every second
        self._update_clock()
    
    def _update_clock(self):
        """Update clock display"""
        now = datetime.now()
        
        # Format: HH:MM:SS
        time_str = now.strftime("%H:%M:%S")
        
        # Format: Day, Month DD
        date_str = now.strftime("%a, %b %d")
        
        self.clock_label.config(text=f"{time_str}\n{date_str}")
        
        # Schedule next update
        self.clock_label.after(1000, self._update_clock)
    
    def _create_network_indicator(self):
        """Create network status indicator"""
        self.network_label = tk.Label(
            self.tray_frame,
            text="🌐",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=('Segoe UI', 12)
        )
        self.network_label.pack(side=tk.RIGHT, padx=2)
        
        # Tooltip
        self._create_tooltip(self.network_label, "Network Status")
    
    def _create_battery_indicator(self):
        """Create battery indicator"""
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                percent = int(battery.percent)
                if battery.power_plugged:
                    icon = "🔌"
                elif percent > 80:
                    icon = "🔋"
                elif percent > 40:
                    icon = "🔋"
                else:
                    icon = "🪫"
                    
                self.battery_label = tk.Label(
                    self.tray_frame,
                    text=f"{icon} {percent}%",
                    bg=self.colors['bg'],
                    fg=self.colors['fg'],
                    font=('Segoe UI', 9)
                )
                self.battery_label.pack(side=tk.RIGHT, padx=2)
        except:
            pass
    
    def _create_volume_indicator(self):
        """Create volume indicator"""
        self.volume_label = tk.Label(
            self.tray_frame,
            text="🔊",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=('Segoe UI', 12)
        )
        self.volume_label.pack(side=tk.RIGHT, padx=2)
        
        # Click to mute/unmute
        self.volume_label.bind('<Button-1>', self._toggle_volume)
    
    def _toggle_volume(self, event):
        """Toggle volume mute"""
        current_text = self.volume_label.cget("text")
        if current_text == "🔊":
            self.volume_label.config(text="🔇")
            # Actually mute system volume here
        else:
            self.volume_label.config(text="🔊")
            # Actually unmute system volume here
    
    def _create_start_menu(self):
        """Create start menu (hidden initially)"""
        from desktop.ui.start_menu import StartMenu
        self.start_menu_instance = StartMenu(self.root, self.start_button)
    
    def toggle_start_menu(self):
        """Toggle start menu visibility"""
        if self.start_menu_instance and hasattr(self.start_menu_instance, 'window'):
            if self.start_menu_instance.window.winfo_exists():
                self.start_menu_instance.window.destroy()
            else:
                self.start_menu_instance.show()
        else:
            self._create_start_menu()
            self.start_menu_instance.show()
    
    def add_app_button(self, app_name, app_id, icon="📄"):
        """Add application button to taskbar"""
        btn = tk.Button(
            self.apps_frame,
            text=f" {icon} {app_name}",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            activebackground=self.colors['hover'],
            activeforeground=self.colors['fg'],
            border=0,
            font=('Segoe UI', 9),
            padx=10,
            pady=5,
            anchor='w',
            cursor='hand2'
        )
        btn.pack(side=tk.LEFT, padx=2)
        
        # Store reference
        self.app_buttons[app_id] = btn
        
        # Hover effects
        btn.bind('<Enter>', lambda e, b=btn: b.config(bg=self.colors['hover']))
        btn.bind('<Leave>', lambda e, b=btn: b.config(bg=self.colors['bg']))
        
        return btn
    
    def remove_app_button(self, app_id):
        """Remove application button from taskbar"""
        if app_id in self.app_buttons:
            self.app_buttons[app_id].destroy()
            del self.app_buttons[app_id]
    
    def update_app_button(self, app_id, state='normal'):
        """Update app button state"""
        if app_id in self.app_buttons:
            if state == 'active':
                self.app_buttons[app_id].config(bg=self.colors['pressed'])
            elif state == 'minimized':
                self.app_buttons[app_id].config(bg=self.colors['bg'], relief='sunken')
            else:
                self.app_buttons[app_id].config(bg=self.colors['bg'], relief='flat')
    
    def _create_tooltip(self, widget, text):
        """Create a tooltip for widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, bg="yellow", fg="black", padx=5, pady=2)
            label.pack()
            
            widget.tooltip = tooltip
            
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip') and widget.tooltip:
                widget.tooltip.destroy()
                widget.tooltip = None
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
