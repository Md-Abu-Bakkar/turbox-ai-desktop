import os
import json
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sqlite3
from datetime import datetime

@dataclass
class AppConfig:
    app_id: str
    name: str
    version: str
    category: str
    executable: str
    icon: str
    dependencies: List[str]

class DesktopManager:
    """Manages desktop applications and windows"""
    
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.apps: Dict[str, AppConfig] = {}
        self.running_apps: Dict[str, object] = {}
        self.windows: List[object] = []
        
        # Initialize database
        self.db_path = os.path.expanduser("~/.turbox/data/desktop.db")
        self._init_database()
        
        # Load installed apps
        self._load_installed_apps()
        
    def _init_database(self):
        """Initialize desktop database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create apps table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS apps (
            id TEXT PRIMARY KEY,
            name TEXT,
            version TEXT,
            category TEXT,
            executable TEXT,
            icon TEXT,
            dependencies TEXT,
            install_date TIMESTAMP,
            last_used TIMESTAMP
        )
        """)
        
        # Create windows table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS windows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id TEXT,
            position_x INTEGER,
            position_y INTEGER,
            width INTEGER,
            height INTEGER,
            state TEXT,
            FOREIGN KEY (app_id) REFERENCES apps (id)
        )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_installed_apps(self):
        """Load installed applications from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM apps")
        rows = cursor.fetchall()
        
        for row in rows:
            app_config = AppConfig(
                app_id=row[0],
                name=row[1],
                version=row[2],
                category=row[3],
                executable=row[4],
                icon=row[5],
                dependencies=json.loads(row[6]) if row[6] else []
            )
            self.apps[app_config.app_id] = app_config
        
        conn.close()
        
        # Add default apps if none installed
        if not self.apps:
            self._create_default_apps()
    
    def _create_default_apps(self):
        """Create default application configurations"""
        default_apps = [
            AppConfig(
                app_id="app_store",
                name="App Store",
                version="1.0.0",
                category="system",
                executable="apps.app_store.app_store:AppStore",
                icon="📦",
                dependencies=[]
            ),
            AppConfig(
                app_id="file_manager",
                name="File Manager",
                version="1.0.0",
                category="system",
                executable="apps.file_manager.file_manager:FileManager",
                icon="📁",
                dependencies=[]
            ),
            AppConfig(
                app_id="terminal",
                name="Terminal",
                version="1.0.0",
                category="system",
                executable="apps.terminal.terminal_app:TerminalApp",
                icon="💻",
                dependencies=[]
            ),
            AppConfig(
                app_id="api_tools",
                name="API Tools",
                version="1.0.0",
                category="development",
                executable="tools.api.api_tester:APITesterApp",
                icon="🔧",
                dependencies=["requests", "beautifulsoup4"]
            ),
            AppConfig(
                app_id="ai_console",
                name="AI Console",
                version="1.0.0",
                category="development",
                executable="tools.ai.ai_console:AIConsole",
                icon="🤖",
                dependencies=[]
            )
        ]
        
        for app in default_apps:
            self.register_app(app)
    
    def register_app(self, app_config: AppConfig):
        """Register an application"""
        self.apps[app_config.app_id] = app_config
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT OR REPLACE INTO apps 
        (id, name, version, category, executable, icon, dependencies, install_date, last_used)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            app_config.app_id,
            app_config.name,
            app_config.version,
            app_config.category,
            app_config.executable,
            app_config.icon,
            json.dumps(app_config.dependencies),
            datetime.now(),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def launch_app(self, app_id: str, **kwargs):
        """Launch an application"""
        if app_id not in self.apps:
            print(f"Application {app_id} not found")
            return None
        
        app_config = self.apps[app_id]
        
        try:
            # Dynamically import and create app
            module_path, class_name = app_config.executable.split(":")
            module = __import__(module_path, fromlist=[class_name])
            app_class = getattr(module, class_name)
            
            # Create app instance
            app = app_class(**kwargs)
            
            # Launch app
            if hasattr(app, 'launch'):
                window = app.launch()
            else:
                window = app()
            
            # Track running app
            self.running_apps[app_id] = {
                'app': app,
                'window': window,
                'config': app_config
            }
            
            # Update last used
            self._update_app_usage(app_id)
            
            print(f"Launched {app_config.name}")
            return app
            
        except Exception as e:
            print(f"Failed to launch {app_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _update_app_usage(self, app_id: str):
        """Update app last used timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE apps SET last_used = ? WHERE id = ?",
            (datetime.now(), app_id)
        )
        
        conn.commit()
        conn.close()
    
    def close_app(self, app_id: str):
        """Close an application"""
        if app_id in self.running_apps:
            app_data = self.running_apps[app_id]
            
            # Close window if exists
            if hasattr(app_data['app'], 'close'):
                app_data['app'].close()
            
            # Remove from running apps
            del self.running_apps[app_id]
    
    def close_all_apps(self):
        """Close all running applications"""
        for app_id in list(self.running_apps.keys()):
            self.close_app(app_id)
    
    def get_running_apps(self):
        """Get all running applications"""
        return list(self.running_apps.values())
    
    def cycle_windows(self):
        """Cycle through open windows"""
        if not self.running_apps:
            return
        
        # Get list of windows
        windows = []
        for app_id, app_data in self.running_apps.items():
            if 'window' in app_data and app_data['window']:
                windows.append(app_data['window'])
        
        if not windows:
            return
        
        # Find currently focused window
        try:
            focused = self.root.focus_get()
            if focused in windows:
                current_index = windows.index(focused)
                next_index = (current_index + 1) % len(windows)
            else:
                next_index = 0
        except:
            next_index = 0
        
        # Focus next window
        if windows[next_index]:
            try:
                windows[next_index].focus_set()
                windows[next_index].lift()
            except:
                pass
    
    def save_all_states(self):
        """Save all application states"""
        for app_id, app_data in self.running_apps.items():
            if hasattr(app_data['app'], 'save_state'):
                try:
                    app_data['app'].save_state()
                except:
                    pass
    
    def check_for_updates(self):
        """Check for application updates"""
        print("Checking for updates...")
        # Implementation would check app store for updates
    
    def install_app(self, app_package):
        """Install an application package"""
        # Implementation for app installation
        pass
    
    def uninstall_app(self, app_id: str):
        """Uninstall an application"""
        if app_id in self.apps:
            # Close if running
            if app_id in self.running_apps:
                self.close_app(app_id)
            
            # Remove from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM apps WHERE id = ?", (app_id,))
            cursor.execute("DELETE FROM windows WHERE app_id = ?", (app_id,))
            
            conn.commit()
            conn.close()
            
            # Remove from apps dict
            del self.apps[app_id]
            
            print(f"Uninstalled {app_id}")
