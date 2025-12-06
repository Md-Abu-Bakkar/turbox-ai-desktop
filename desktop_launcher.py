#!/data/data/com.termux/files/usr/bin/python3
# ==============================================================================
# TurboX Desktop OS - Desktop Launcher
# Phase 1: Basic Application Management
# ==============================================================================

import os
import sys
import json
import subprocess
import threading
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class TurboXLauncher(QWidget):
    """Main desktop launcher and application manager"""
    
    def __init__(self):
        super().__init__()
        self.home_dir = os.path.expanduser("~")
        self.config_dir = os.path.join(self.home_dir, '.turboX')
        self.apps_file = os.path.join(self.config_dir, 'config', 'applications.json')
        
        # Load applications
        self.applications = self._load_applications()
        
        # Track running apps
        self.running_apps = {}
        
        # Initialize UI
        self.init_ui()
        
        # Setup auto-save
        self.setup_auto_save()
    
    def _load_applications(self):
        """Load application definitions"""
        default_apps = {
            "system": {
                "file_manager": {
                    "name": "File Manager",
                    "command": "pcmanfm",
                    "icon": "folder",
                    "category": "system",
                    "description": "Browse and manage files"
                },
                "terminal": {
                    "name": "Terminal",
                    "command": "xfce4-terminal",
                    "icon": "terminal",
                    "category": "system",
                    "description": "Command line terminal"
                },
                "text_editor": {
                    "name": "Text Editor",
                    "command": "mousepad",
                    "icon": "text-editor",
                    "category": "system",
                    "description": "Edit text files"
                }
            },
            "tools": {
                "api_tester": {
                    "name": "API Tester",
                    "command": "echo 'API Tester (Phase 2)'",
                    "icon": "network-server",
                    "category": "tools",
                    "description": "Test API endpoints (Coming Phase 2)",
                    "enabled": False
                },
                "browser": {
                    "name": "Web Browser",
                    "command": "am start -a android.intent.action.VIEW -d about:blank",
                    "icon": "web-browser",
                    "category": "tools",
                    "description": "Open web browser (External)"
                }
            }
        }
        
        try:
            if os.path.exists(self.apps_file):
                with open(self.apps_file, 'r') as f:
                    apps = json.load(f)
                return apps
            else:
                return default_apps
        except Exception as e:
            print(f"⚠️  Apps load error: {e}")
            return default_apps
    
    def save_applications(self):
        """Save application definitions"""
        try:
            with open(self.apps_file, 'w') as f:
                json.dump(self.applications, f, indent=2)
            print("✅ Applications saved")
        except Exception as e:
            print(f"❌ Apps save error: {e}")
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("TurboX Launcher")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet(self._get_stylesheet())
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Header
        header = QLabel("TurboX Application Launcher")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Category tabs
        self.tabs = QTabWidget()
        
        # System tab
        system_tab = QWidget()
        system_layout = QVBoxLayout()
        system_tab.setLayout(system_layout)
        
        # Add system apps
        for app_id, app_info in self.applications.get("system", {}).items():
            if app_info.get("enabled", True):
                btn = self._create_app_button(app_id, app_info)
                system_layout.addWidget(btn)
        
        system_layout.addStretch()
        self.tabs.addTab(system_tab, "System")
        
        # Tools tab
        tools_tab = QWidget()
        tools_layout = QVBoxLayout()
        tools_tab.setLayout(tools_layout)
        
        # Add tools
        for app_id, app_info in self.applications.get("tools", {}).items():
            if app_info.get("enabled", True):
                btn = self._create_app_button(app_id, app_info)
                tools_layout.addWidget(btn)
        
        tools_layout.addStretch()
        self.tabs.addTab(tools_tab, "Tools")
        
        # Settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        settings_tab.setLayout(settings_layout)
        
        # Add settings options
        settings_label = QLabel("System Settings (Phase 2)")
        settings_label.setAlignment(Qt.AlignCenter)
        settings_layout.addWidget(settings_label)
        
        # Theme selector placeholder
        theme_label = QLabel("Theme:")
        theme_combo = QComboBox()
        theme_combo.addItems(["Windows Dark", "Windows Light", "Classic"])
        theme_combo.setEnabled(False)  # Phase 2
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(theme_combo)
        settings_layout.addLayout(theme_layout)
        
        # Auto-start toggle
        autostart_check = QCheckBox("Start TurboX on Termux boot")
        autostart_check.setChecked(True)
        autostart_check.setEnabled(False)  # Phase 2
        settings_layout.addWidget(autostart_check)
        
        settings_layout.addStretch()
        self.tabs.addTab(settings_tab, "Settings")
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        status_bar = QStatusBar()
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)
        main_layout.addWidget(status_bar)
        
        self.setLayout(main_layout)
    
    def _create_app_button(self, app_id, app_info):
        """Create an application launch button"""
        btn = QPushButton(app_info["name"])
        btn.setToolTip(app_info["description"])
        btn.setMinimumHeight(50)
        
        # Style based on category
        if app_info["category"] == "system":
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2b579a;
                    color: white;
                    border-radius: 5px;
                    font-size: 14px;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: #3a6bc5;
                }
                QPushButton:disabled {
                    background-color: #666;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #107c10;
                    color: white;
                    border-radius: 5px;
                    font-size: 14px;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: #1a9e1a;
                }
                QPushButton:disabled {
                    background-color: #666;
                }
            """)
        
        # Connect click event
        btn.clicked.connect(lambda checked, aid=app_id: self.launch_application(aid))
        
        # Disable if not enabled
        if not app_info.get("enabled", True):
            btn.setEnabled(False)
            btn.setText(f"{app_info['name']} (Phase 2)")
        
        return btn
    
    def launch_application(self, app_id):
        """Launch an application"""
        # Find the app in categories
        app_info = None
        for category in self.applications.values():
            if app_id in category:
                app_info = category[app_id]
                break
        
        if not app_info:
            self.status_label.setText(f"❌ Application '{app_id}' not found")
            return
        
        if not app_info.get("enabled", True):
            self.status_label.setText(f"⏳ {app_info['name']} available in Phase 2")
            return
        
        try:
            # Run command in background
            process = subprocess.Popen(
                app_info["command"],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Track running app
            self.running_apps[app_id] = {
                "process": process,
                "started": datetime.now().isoformat(),
                "name": app_info["name"]
            }
            
            # Start monitor thread
            thread = threading.Thread(
                target=self._monitor_app,
                args=(app_id, process),
                daemon=True
            )
            thread.start()
            
            self.status_label.setText(f"✅ Launched: {app_info['name']}")
            print(f"🚀 Launched: {app_info['name']} (PID: {process.pid})")
            
        except Exception as e:
            self.status_label.setText(f"❌ Failed to launch: {app_info['name']}")
            print(f"❌ Launch error: {e}")
    
    def _monitor_app(self, app_id, process):
        """Monitor a running application"""
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"⚠️  App '{app_id}' exited with code {process.returncode}")
            if stderr:
                print(f"   Error: {stderr[:200]}")
        
        # Remove from running apps
        if app_id in self.running_apps:
            del self.running_apps[app_id]
            
            # Update status on UI thread
            def update_status():
                self.status_label.setText(f"📤 Closed: {self.running_apps.get(app_id, {}).get('name', app_id)}")
            
            QTimer.singleShot(0, update_status)
    
    def get_running_apps(self):
        """Get list of currently running applications"""
        return list(self.running_apps.keys())
    
    def setup_auto_save(self):
        """Setup periodic auto-save"""
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_applications)
        self.save_timer.start(30000)  # Save every 30 seconds
    
    def _get_stylesheet(self):
        """Get the application stylesheet"""
        return """
        QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QTabWidget::pane {
            border: 1px solid #444;
            background-color: #2d2d2d;
        }
        QTabBar::tab {
            background-color: #3e3e3e;
            color: #ccc;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #2d2d2d;
            color: #fff;
            border-bottom: 2px solid #0078d7;
        }
        QTabBar::tab:hover {
            background-color: #4e4e4e;
        }
        QStatusBar {
            background-color: #0078d7;
            color: white;
            font-size: 12px;
        }
        """
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop any running monitoring threads
        self.save_applications()
        
        # Confirm if apps are running
        if self.running_apps:
            reply = QMessageBox.question(
                self, 'Confirm Exit',
                f"You have {len(self.running_apps)} app(s) running. Close anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        # Terminate all running apps
        for app_id in list(self.running_apps.keys()):
            try:
                self.running_apps[app_id]["process"].terminate()
            except:
                pass
        
        event.accept()

def main():
    """Entry point"""
    # Check if running in X11
    if "DISPLAY" not in os.environ:
        print("⚠️  Not running in X11 environment")
        print("   Please start TurboX Desktop first")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    launcher = TurboXLauncher()
    launcher.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
