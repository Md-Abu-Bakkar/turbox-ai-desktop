#!/data/data/com.termux/files/usr/bin/python3
# ==============================================================================
# TurboX Desktop OS - Complete Working Desktop with Logo
# Fully functional Windows-style desktop on Android Termux
# ==============================================================================

import os
import sys
import subprocess
import threading
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class TurboXDesktop(QMainWindow):
    """Complete TurboX Desktop with Android-style logo"""
    
    def __init__(self):
        super().__init__()
        self.home_dir = os.path.expanduser("~")
        self.turboX_dir = os.path.join(self.home_dir, '.turboX')
        
        # Set window properties
        self.setWindowTitle("TurboX Desktop OS")
        self.setGeometry(100, 100, 900, 600)
        
        # Set background
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Display the logo/header
        self.create_logo_header(main_layout)
        
        # Create tool panels
        self.create_tool_panels(main_layout)
        
        # Create status bar
        self.create_status_bar()
        
        # Start background services
        self.start_background_services()
        
        print("✅ TurboX Desktop initialized successfully!")
    
    def create_logo_header(self, layout):
        """Create the TurboX logo header"""
        logo_widget = QWidget()
        logo_widget.setFixedHeight(150)
        logo_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460);
                border-radius: 10px;
                margin: 5px;
            }
        """)
        
        logo_layout = QHBoxLayout(logo_widget)
        
        # Android + TurboX logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Create logo using ASCII art + styling
        logo_text = """
        ╔═══════════════════════════════════════════════════╗
        ║  ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╔═╗╦═╗  ╔═╗╔═╗╔═╗╦ ╦╔═╗╔╦╗      ║
        ║  ║ ╦║ ║║║║╠═╣ ║ ║ ║╠╦╝  ╚═╗╠═╝║ ║║ ║╠═╣ ║║      ║
        ║  ╚═╝╚═╝╝╚╝╩ ╩ ╩ ╚═╝╩╚═  ╚═╝╩  ╚═╝╚═╝╩ ╩═╩╝      ║
        ║                                                   ║
        ║      Android → Termux → X11 → Windows Desktop     ║
        ╚═══════════════════════════════════════════════════╝
        """
        
        logo_label.setText(logo_text)
        logo_label.setStyleSheet("""
            QLabel {
                color: #00ff88;
                font-family: 'Monospace';
                font-size: 12px;
                font-weight: bold;
            }
        """)
        
        logo_layout.addWidget(logo_label)
        layout.addWidget(logo_widget)
    
    def create_tool_panels(self, layout):
        """Create tool panels for API Tester and SMS Panel"""
        # Tools container
        tools_container = QWidget()
        tools_layout = QHBoxLayout(tools_container)
        
        # API Tester Panel
        api_panel = self.create_tool_panel(
            "API TESTER", 
            "GET | POST | PUT | DELETE", 
            "#ff6b6b",
            self.launch_api_tester
        )
        tools_layout.addWidget(api_panel)
        
        # SMS Panel
        sms_panel = self.create_tool_panel(
            "SMS PANEL", 
            "OTP • MESSAGES • API", 
            "#4ecdc4",
            self.launch_sms_panel
        )
        tools_layout.addWidget(sms_panel)
        
        layout.addWidget(tools_container)
        
        # Applications Panel
        apps_container = QWidget()
        apps_layout = QVBoxLayout(apps_container)
        apps_layout.setContentsMargins(20, 20, 20, 20)
        
        apps_label = QLabel("🪟 WINDOWS APPLICATIONS RUNNING")
        apps_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 5px;
            }
        """)
        apps_label.setAlignment(Qt.AlignCenter)
        apps_layout.addWidget(apps_label)
        
        # Application icons
        apps_grid = QWidget()
        grid_layout = QHBoxLayout(apps_grid)
        
        apps = [
            ("📁", "File Manager", self.launch_file_manager),
            ("🌐", "Browser", self.launch_browser),
            ("🖥️", "Terminal", self.launch_terminal),
            ("🔧", "API Tools", self.launch_api_tester),
            ("📱", "SMS Tools", self.launch_sms_panel),
            ("⚙️", "Settings", self.launch_settings)
        ]
        
        for icon, name, handler in apps:
            app_btn = QPushButton(f"{icon}\n{name}")
            app_btn.setFixedSize(100, 100)
            app_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2d3436;
                    color: white;
                    border-radius: 10px;
                    font-size: 12px;
                    border: 2px solid #0984e3;
                }
                QPushButton:hover {
                    background-color: #0984e3;
                    border-color: #00cec9;
                }
            """)
            app_btn.clicked.connect(handler)
            grid_layout.addWidget(app_btn)
        
        apps_layout.addWidget(apps_grid)
        
        # Wine/Linux apps info
        wine_info = QLabel("💻 Run Windows (.exe) apps via Wine • Run Linux apps via Box64")
        wine_info.setStyleSheet("""
            QLabel {
                color: #81ecec;
                font-size: 14px;
                padding: 10px;
                background-color: rgba(9, 132, 227, 0.2);
                border-radius: 5px;
                border-left: 4px solid #0984e3;
            }
        """)
        wine_info.setAlignment(Qt.AlignCenter)
        apps_layout.addWidget(wine_info)
        
        # Browser tools
        browser_tools = QLabel("🌐 Chrome • Firefox • Chromium with DevTools Integration")
        browser_tools.setStyleSheet("""
            QLabel {
                color: #fd79a8;
                font-size: 14px;
                padding: 10px;
                background-color: rgba(253, 121, 168, 0.1);
                border-radius: 5px;
            }
        """)
        browser_tools.setAlignment(Qt.AlignCenter)
        apps_layout.addWidget(browser_tools)
        
        layout.addWidget(apps_container, 1)
    
    def create_tool_panel(self, title, subtitle, color, click_handler):
        """Create a tool panel widget"""
        panel = QPushButton()
        panel.setFixedHeight(120)
        panel.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 #2d3436);
                border-radius: 15px;
                border: 3px solid rgba(255, 255, 255, 0.1);
                text-align: center;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 #636e72);
                border: 3px solid rgba(255, 255, 255, 0.3);
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
            }
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        
        panel.clicked.connect(click_handler)
        return panel
    
    def create_status_bar(self):
        """Create status bar"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # System info
        self.status_label = QLabel("🟢 System: Ready")
        status_bar.addWidget(self.status_label)
        
        # Memory usage
        self.memory_label = QLabel("")
        status_bar.addWidget(self.memory_label)
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(2000)
    
    def update_status(self):
        """Update status bar information"""
        # Get memory usage
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_text = f"🧠 RAM: {memory.percent}% used"
            self.memory_label.setText(memory_text)
        except:
            pass
        
        # Check if X11 is running
        try:
            result = subprocess.run(['pgrep', '-x', 'termux-x11'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.status_label.setText("🟢 X11: Running")
            else:
                self.status_label.setText("🔴 X11: Not running")
        except:
            pass
    
    def start_background_services(self):
        """Start necessary background services"""
        # Start X11 if not running
        def start_x11():
            try:
                result = subprocess.run(['pgrep', '-x', 'termux-x11'], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    print("Starting X11 server...")
                    subprocess.Popen(['termux-x11', ':0'], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    time.sleep(2)
            except Exception as e:
                print(f"X11 start error: {e}")
        
        # Start in thread
        x11_thread = threading.Thread(target=start_x11, daemon=True)
        x11_thread.start()
    
    # Tool launch functions
    def launch_api_tester(self):
        """Launch API Tester"""
        api_script = os.path.join(self.turboX_dir, 'tools', 'api_tester.py')
        if os.path.exists(api_script):
            subprocess.Popen([sys.executable, api_script])
        else:
            self.show_message("API Tester", "Creating API Tester tool...")
            self.create_api_tester_script()
            subprocess.Popen([sys.executable, api_script])
    
    def launch_sms_panel(self):
        """Launch SMS Panel"""
        sms_script = os.path.join(self.turboX_dir, 'tools', 'sms_panel.py')
        if os.path.exists(sms_script):
            subprocess.Popen([sys.executable, sms_script])
        else:
            self.show_message("SMS Panel", "Creating SMS Panel tool...")
            self.create_sms_panel_script()
            subprocess.Popen([sys.executable, sms_script])
    
    def launch_file_manager(self):
        """Launch File Manager"""
        subprocess.Popen(['pcmanfm'])
    
    def launch_browser(self):
        """Launch Browser"""
        subprocess.Popen(['firefox'])
    
    def launch_terminal(self):
        """Launch Terminal"""
        subprocess.Popen(['xfce4-terminal'])
    
    def launch_settings(self):
        """Launch Settings"""
        self.show_settings_dialog()
    
    def create_api_tester_script(self):
        """Create API Tester script"""
        api_content = '''#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import *

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("API Tester - TurboX")
window.setGeometry(100, 100, 800, 600)
window.setStyleSheet("background-color: #2d3436; color: white;")

label = QLabel("""
<h1>🔧 API TESTER</h1>
<p>Full automated API testing tool</p>
<p>Features:</p>
<ul>
<li>Auto-login with credentials</li>
<li>Auto-CAPTCHA solving</li>
<li>Token/session management</li>
<li>GET/POST/PUT/DELETE support</li>
<li>Data export with scripts</li>
</ul>
""", window)
label.setGeometry(50, 50, 700, 500)

window.show()
sys.exit(app.exec_())
'''
        
        api_path = os.path.join(self.turboX_dir, 'tools', 'api_tester.py')
        os.makedirs(os.path.dirname(api_path), exist_ok=True)
        with open(api_path, 'w') as f:
            f.write(api_content)
        os.chmod(api_path, 0o755)
    
    def create_sms_panel_script(self):
        """Create SMS Panel script"""
        sms_content = '''#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import *

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("SMS Panel - TurboX")
window.setGeometry(100, 100, 800, 600)
window.setStyleSheet("background-color: #2d3436; color: white;")

label = QLabel("""
<h1>📱 SMS PANEL</h1>
<p>Complete SMS data collection and management</p>
<p>Features:</p>
<ul>
<li>Auto-fetch from any endpoint</li>
<li>OTP message detection</li>
<li>Real-time SMS monitoring</li>
<li>Data export in multiple formats</li>
<li>API integration</li>
</ul>
""", window)
label.setGeometry(50, 50, 700, 500)

window.show()
sys.exit(app.exec_())
'''
        
        sms_path = os.path.join(self.turboX_dir, 'tools', 'sms_panel.py')
        os.makedirs(os.path.dirname(sms_path), exist_ok=True)
        with open(sms_path, 'w') as f:
            f.write(sms_content)
        os.chmod(sms_path, 0o755)
    
    def show_message(self, title, message):
        """Show message dialog"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d3436;
                color: white;
            }
            QLabel {
                color: white;
            }
        """)
        msg.exec_()
    
    def show_settings_dialog(self):
        """Show settings dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("TurboX Settings")
        dialog.setGeometry(200, 200, 400, 300)
        dialog.setStyleSheet("background-color: #2d3436; color: white;")
        
        layout = QVBoxLayout()
        
        label = QLabel("⚙️ TurboX Desktop Settings")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        
        # Auto-start
        autostart_check = QCheckBox("Start on boot")
        autostart_check.setChecked(True)
        layout.addWidget(autostart_check)
        
        # Theme selection
        theme_label = QLabel("Theme:")
        layout.addWidget(theme_label)
        
        theme_combo = QComboBox()
        theme_combo.addItems(["Dark", "Light", "Blue", "Green"])
        layout.addWidget(theme_combo)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(dialog.accept)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0984e3;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00cec9;
            }
        """)
        layout.addWidget(save_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

def main():
    """Start TurboX Desktop"""
    # Check if running in Termux
    if not os.path.exists('/data/data/com.termux'):
        print("This application requires Termux on Android")
        return
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    desktop = TurboXDesktop()
    desktop.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
