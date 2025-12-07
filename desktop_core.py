#!/data/data/com.termux/files/usr/bin/python3
# ==============================================================================
# TurboX Desktop OS v2.0 - Windows-Style Desktop Core
# Full mouse control, taskbar, start menu, system tray
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

class WindowsDesktop(QMainWindow):
    """Windows-style desktop environment with full mouse control"""
    
    def __init__(self):
        super().__init__()
        self.home_dir = os.path.expanduser("~")
        self.config_dir = os.path.join(self.home_dir, '.turboX')
        
        # Load configuration
        self.config = self.load_config()
        
        # Window tracking
        self.windows = []
        self.active_window = None
        
        # Mouse control state
        self.mouse_state = {
            'left_pressed': False,
            'right_pressed': False,
            'drag_start': None,
            'drag_window': None
        }
        
        # Initialize Windows-style UI
        self.init_windows_ui()
        
        # Start desktop services
        self.start_desktop_services()
        
        print("✅ Windows-style desktop initialized")
    
    def load_config(self):
        """Load desktop configuration"""
        config_file = os.path.join(self.config_dir, 'config', 'system.json')
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            return {
                'desktop': {
                    'theme': 'windows-dark',
                    'taskbar': True,
                    'start_menu': True
                }
            }
    
    def init_windows_ui(self):
        """Initialize Windows-style user interface"""
        # Set window properties
        self.setWindowTitle("TurboX Desktop")
        
        # Get screen geometry
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        
        # Set to full screen
        self.setGeometry(geometry)
        
        # Set window flags for desktop
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint)
        
        # Set background (wallpaper)
        self.setStyleSheet(self.get_windows_stylesheet())
        
        # Create desktop widgets
        self.create_desktop_widgets()
        
        # Create taskbar
        if self.config.get('desktop', {}).get('taskbar', True):
            self.create_taskbar()
        
        # Setup mouse tracking
        self.setMouseTracking(True)
        self.installEventFilter(self)
    
    def get_windows_stylesheet(self):
        """Get Windows-style stylesheet"""
        return """
        QMainWindow {
            background-color: #1e1e1e;
            background-image: url('');
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
        }
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        """
    
    def create_desktop_widgets(self):
        """Create desktop icons and widgets"""
        # Desktop icons container
        self.desktop_widget = QWidget(self)
        self.desktop_widget.setGeometry(20, 20, 800, 600)
        
        # Desktop icons layout
        icons_layout = QVBoxLayout(self.desktop_widget)
        
        # Computer icon
        computer_btn = self.create_desktop_icon("This PC", "computer", 
                                               lambda: self.open_file_manager())
        icons_layout.addWidget(computer_btn)
        
        # Recycle Bin
        recycle_btn = self.create_desktop_icon("Recycle Bin", "trash",
                                              lambda: self.open_recycle_bin())
        icons_layout.addWidget(recycle_btn)
        
        # User Documents
        docs_btn = self.create_desktop_icon("Documents", "folder-documents",
                                           lambda: self.open_folder("Documents"))
        icons_layout.addWidget(docs_btn)
        
        # Downloads
        downloads_btn = self.create_desktop_icon("Downloads", "folder-download",
                                                lambda: self.open_folder("Downloads"))
        icons_layout.addWidget(downloads_btn)
        
        # TurboX Launcher
        turbox_btn = self.create_desktop_icon("TurboX Launcher", "applications-system",
                                             self.open_turbox_launcher)
        icons_layout.addWidget(turbox_btn)
        
        icons_layout.addStretch()
    
    def create_desktop_icon(self, name, icon_type, click_handler):
        """Create a desktop icon"""
        icon_btn = QPushButton(name)
        icon_btn.setIcon(self.get_icon(icon_type))
        icon_btn.setIconSize(QSize(48, 48))
        icon_btn.setFixedSize(100, 100)
        icon_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: white;
                font-size: 12px;
                padding: 5px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
            }
        """)
        icon_btn.clicked.connect(click_handler)
        return icon_btn
    
    def get_icon(self, icon_type):
        """Get icon based on type"""
        # Use system icons or fallback
        icon = QIcon()
        
        if icon_type == "computer":
            icon = QIcon.fromTheme("computer")
        elif icon_type == "trash":
            icon = QIcon.fromTheme("user-trash")
        elif "folder" in icon_type:
            icon = QIcon.fromTheme("folder")
        elif icon_type == "applications-system":
            icon = QIcon.fromTheme("applications-system")
        
        if icon.isNull():
            # Create simple colored icon
            pixmap = QPixmap(48, 48)
            pixmap.fill(QColor(66, 133, 244))
            icon = QIcon(pixmap)
        
        return icon
    
    def create_taskbar(self):
        """Create Windows-style taskbar"""
        self.taskbar = QFrame(self)
        screen_rect = QApplication.primaryScreen().geometry()
        taskbar_height = 48
        
        self.taskbar.setGeometry(
            0, 
            screen_rect.height() - taskbar_height,
            screen_rect.width(),
            taskbar_height
        )
        
        self.taskbar.setStyleSheet("""
            QFrame {
                background-color: rgba(45, 45, 45, 0.95);
                border-top: 1px solid #555;
            }
        """)
        
        # Taskbar layout
        taskbar_layout = QHBoxLayout(self.taskbar)
        taskbar_layout.setContentsMargins(5, 5, 5, 5)
        
        # Start button
        start_btn = QPushButton()
        start_btn.setIcon(QIcon.fromTheme("start-here"))
        start_btn.setIconSize(QSize(32, 32))
        start_btn.setFixedSize(40, 40)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        start_btn.clicked.connect(self.show_start_menu)
        taskbar_layout.addWidget(start_btn)
        
        # Taskbar applications
        self.taskbar_apps = QWidget()
        apps_layout = QHBoxLayout(self.taskbar_apps)
        apps_layout.setContentsMargins(10, 0, 10, 0)
        
        # Add common apps
        apps = [
            ("File Manager", "system-file-manager", self.open_file_manager),
            ("Terminal", "utilities-terminal", self.open_terminal),
            ("Browser", "web-browser", self.open_browser),
            ("API Tester", "network-server", self.open_api_tester),
            ("SMS Panel", "phone", self.open_sms_panel)
        ]
        
        for app_name, app_icon, app_handler in apps:
            app_btn = QPushButton()
            app_btn.setIcon(QIcon.fromTheme(app_icon))
            app_btn.setIconSize(QSize(24, 24))
            app_btn.setFixedSize(36, 36)
            app_btn.setToolTip(app_name)
            app_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)
            app_btn.clicked.connect(app_handler)
            apps_layout.addWidget(app_btn)
        
        taskbar_layout.addWidget(self.taskbar_apps, 1)
        
        # System tray area
        system_tray = QWidget()
        tray_layout = QHBoxLayout(system_tray)
        
        # Clock
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("color: white; font-size: 11px;")
        tray_layout.addWidget(self.clock_label)
        
        # Update clock
        self.update_clock()
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every second
        
        taskbar_layout.addWidget(system_tray)
    
    def update_clock(self):
        """Update taskbar clock"""
        current_time = datetime.now().strftime("%I:%M %p")
        current_date = datetime.now().strftime("%d/%m")
        self.clock_label.setText(f"{current_time} | {current_date}")
    
    def show_start_menu(self):
        """Show Windows-style start menu"""
        self.start_menu = QMenu(self)
        self.start_menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QMenu::item {
                color: white;
                padding: 8px 25px 8px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #0078d7;
            }
            QMenu::separator {
                height: 1px;
                background-color: #555;
                margin: 5px 0;
            }
        """)
        
        # Add menu items
        apps_menu = self.start_menu.addMenu("📁 Applications")
        
        # System apps
        apps_menu.addAction("📂 File Manager", self.open_file_manager)
        apps_menu.addAction("💻 Terminal", self.open_terminal)
        apps_menu.addAction("🌐 Web Browser", self.open_browser)
        
        apps_menu.addSeparator()
        
        # TurboX apps
        apps_menu.addAction("🔧 API Tester", self.open_api_tester)
        apps_menu.addAction("📱 SMS Panel", self.open_sms_panel)
        apps_menu.addAction("🤖 Automation", self.open_automation)
        
        self.start_menu.addSeparator()
        
        # System
        self.start_menu.addAction("⚙️ Settings", self.open_settings)
        self.start_menu.addAction("🔄 Restart Desktop", self.restart_desktop)
        self.start_menu.addAction("⏹️ Shutdown", self.shutdown)
        
        # Show menu at start button position
        start_btn = self.taskbar.findChild(QPushButton)
        if start_btn:
            pos = start_btn.mapToGlobal(QPoint(0, start_btn.height()))
            self.start_menu.exec_(pos)
    
    def open_file_manager(self):
        """Open file manager"""
        subprocess.Popen(['pcmanfm'])
    
    def open_terminal(self):
        """Open terminal"""
        subprocess.Popen(['xfce4-terminal'])
    
    def open_browser(self):
        """Open web browser"""
        subprocess.Popen(['firefox'])
    
    def open_api_tester(self):
        """Open API Tester"""
        api_path = os.path.join(self.config_dir, 'tools', 'api_tester_auto.py')
        subprocess.Popen([sys.executable, api_path])
    
    def open_sms_panel(self):
        """Open SMS Panel"""
        sms_path = os.path.join(self.config_dir, 'tools', 'sms_panel_auto.py')
        subprocess.Popen([sys.executable, sms_path])
    
    def open_automation(self):
        """Open Automation Controller"""
        auto_path = os.path.join(self.config_dir, 'scripts', 'automation_controller.py')
        subprocess.Popen([sys.executable, auto_path])
    
    def open_turbox_launcher(self):
        """Open TurboX application launcher"""
        self.show()
    
    def open_folder(self, folder_name):
        """Open specific folder"""
        folder_path = os.path.join(self.home_dir, folder_name)
        subprocess.Popen(['pcmanfm', folder_path])
    
    def open_recycle_bin(self):
        """Open recycle bin"""
        # Not implemented in Termux, open downloads as alternative
        self.open_folder("Downloads")
    
    def open_settings(self):
        """Open settings dialog"""
        settings_dialog = QDialog(self)
        settings_dialog.setWindowTitle("TurboX Settings")
        settings_dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Theme selection
        theme_label = QLabel("Theme:")
        theme_combo = QComboBox()
        theme_combo.addItems(["Windows Dark", "Windows Light", "Classic"])
        theme_combo.setCurrentText(self.config.get('desktop', {}).get('theme', 'Windows Dark').replace('-', ' ').title())
        
        # Taskbar toggle
        taskbar_check = QCheckBox("Show taskbar")
        taskbar_check.setChecked(self.config.get('desktop', {}).get('taskbar', True))
        
        # Auto-start toggle
        autostart_check = QCheckBox("Start on boot")
        autostart_check.setChecked(self.config.get('system', {}).get('auto_start', True))
        
        # Apply button
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(lambda: self.apply_settings(
            theme_combo.currentText(),
            taskbar_check.isChecked(),
            autostart_check.isChecked(),
            settings_dialog
        ))
        
        layout.addWidget(theme_label)
        layout.addWidget(theme_combo)
        layout.addWidget(taskbar_check)
        layout.addWidget(autostart_check)
        layout.addWidget(apply_btn)
        
        settings_dialog.setLayout(layout)
        settings_dialog.exec_()
    
    def apply_settings(self, theme, taskbar, autostart, dialog):
        """Apply desktop settings"""
        # Update config
        self.config['desktop']['theme'] = theme.lower().replace(' ', '-')
        self.config['desktop']['taskbar'] = taskbar
        self.config['system']['auto_start'] = autostart
        
        # Save config
        config_file = os.path.join(self.config_dir, 'config', 'system.json')
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # Update autostart
        autostart_file = os.path.join(self.config_dir, 'config', 'autostart')
        with open(autostart_file, 'w') as f:
            f.write('1' if autostart else '0')
        
        QMessageBox.information(self, "Settings Applied", 
                              "Restart desktop for changes to take effect.")
        dialog.accept()
    
    def restart_desktop(self):
        """Restart desktop environment"""
        reply = QMessageBox.question(self, "Restart Desktop",
                                   "Restart TurboX Desktop?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            subprocess.Popen(['turbox', 'stop'])
            import time
            time.sleep(2)
            subprocess.Popen(['turbox', 'start'])
    
    def shutdown(self):
        """Shutdown desktop"""
        reply = QMessageBox.question(self, "Shutdown",
                                   "Shutdown TurboX Desktop?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            subprocess.Popen(['turbox', 'stop'])
            self.close()
    
    def start_desktop_services(self):
        """Start desktop background services"""
        # Start automation controller if not running
        if not self.is_process_running("automation_controller"):
            auto_thread = threading.Thread(
                target=self.start_service,
                args=("automation_controller.py",),
                daemon=True
            )
            auto_thread.start()
        
        # Start socket bridge if not running
        if not self.is_process_running("socket_bridge"):
            bridge_thread = threading.Thread(
                target=self.start_service,
                args=("socket_bridge.py",),
                daemon=True
            )
            bridge_thread.start()
    
    def is_process_running(self, process_name):
        """Check if a process is running"""
        try:
            result = subprocess.run(['pgrep', '-f', process_name],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def start_service(self, script_name):
        """Start a background service"""
        script_path = os.path.join(self.config_dir, 'scripts', script_name)
        subprocess.Popen([sys.executable, script_path])
    
    # Mouse event handling for full mouse control
    def eventFilter(self, obj, event):
        """Handle mouse events for desktop interaction"""
        if event.type() == QEvent.MouseButtonPress:
            self.handle_mouse_press(event)
        elif event.type() == QEvent.MouseButtonRelease:
            self.handle_mouse_release(event)
        elif event.type() == QEvent.MouseMove:
            self.handle_mouse_move(event)
        elif event.type() == QEvent.MouseButtonDblClick:
            self.handle_double_click(event)
        
        return super().eventFilter(obj, event)
    
    def handle_mouse_press(self, event):
        """Handle mouse button press"""
        if event.button() == Qt.LeftButton:
            self.mouse_state['left_pressed'] = True
            self.mouse_state['drag_start'] = event.pos()
            
            # Check if clicking on a window
            for window in self.windows:
                if window.geometry().contains(event.pos()):
                    self.mouse_state['drag_window'] = window
                    self.active_window = window
                    break
        
        elif event.button() == Qt.RightButton:
            self.mouse_state['right_pressed'] = True
            self.show_context_menu(event.pos())
    
    def handle_mouse_release(self, event):
        """Handle mouse button release"""
        if event.button() == Qt.LeftButton:
            self.mouse_state['left_pressed'] = False
            self.mouse_state['drag_start'] = None
            self.mouse_state['drag_window'] = None
        
        elif event.button() == Qt.RightButton:
            self.mouse_state['right_pressed'] = False
    
    def handle_mouse_move(self, event):
        """Handle mouse movement"""
        if (self.mouse_state['left_pressed'] and 
            self.mouse_state['drag_window'] and
            self.mouse_state['drag_start']):
            
            # Calculate drag distance
            delta = event.pos() - self.mouse_state['drag_start']
            
            # Move the window
            window = self.mouse_state['drag_window']
            new_pos = window.pos() + delta
            window.move(new_pos)
            
            # Update drag start position
            self.mouse_state['drag_start'] = event.pos()
        
        # Update cursor based on position
        self.update_cursor(event.pos())
    
    def handle_double_click(self, event):
        """Handle double click"""
        if event.button() == Qt.LeftButton:
            # Check what was double-clicked
            for widget in self.desktop_widget.findChildren(QPushButton):
                if widget.geometry().contains(event.pos()):
                    widget.click()
                    break
    
    def show_context_menu(self, position):
        """Show right-click context menu"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QMenu::item {
                color: white;
                padding: 8px 25px 8px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #0078d7;
            }
        """)
        
        # Add context menu items
        menu.addAction("🔄 Refresh Desktop", self.refresh_desktop)
        menu.addAction("📁 New Folder", self.create_new_folder)
        menu.addAction("📄 New File", self.create_new_file)
        menu.addSeparator()
        menu.addAction("⚙️ Display Settings", self.open_display_settings)
        menu.addAction("🎨 Change Wallpaper", self.change_wallpaper)
        
        menu.exec_(self.mapToGlobal(position))
    
    def refresh_desktop(self):
        """Refresh desktop"""
        pass  # Could reload desktop icons
    
    def create_new_folder(self):
        """Create new folder on desktop"""
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and folder_name:
            folder_path = os.path.join(self.home_dir, 'Desktop', folder_name)
            os.makedirs(folder_path, exist_ok=True)
    
    def create_new_file(self):
        """Create new file on desktop"""
        file_name, ok = QInputDialog.getText(self, "New File", "File name:")
        if ok and file_name:
            file_path = os.path.join(self.home_dir, 'Desktop', file_name)
            with open(file_path, 'w') as f:
                f.write("")
    
    def open_display_settings(self):
        """Open display settings"""
        self.open_settings()
    
    def change_wallpaper(self):
        """Change desktop wallpaper"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Wallpaper", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            # Copy to wallpaper directory
            import shutil
            wallpaper_dir = os.path.join(self.config_dir, 'wallpapers')
            os.makedirs(wallpaper_dir, exist_ok=True)
            
            wallpaper_path = os.path.join(wallpaper_dir, 'current_wallpaper')
            shutil.copy2(file_path, wallpaper_path)
            
            # Update stylesheet
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: #1e1e1e;
                    background-image: url('{wallpaper_path}');
                    background-repeat: no-repeat;
                    background-position: center;
                    background-size: cover;
                }}
            """)
    
    def update_cursor(self, position):
        """Update cursor based on position"""
        # Check if near window edge for resizing
        for window in self.windows:
            if window.geometry().contains(position):
                # Check edges
                geom = window.geometry()
                if (abs(position.x() - geom.left()) < 5 or
                    abs(position.x() - geom.right()) < 5):
                    self.setCursor(Qt.SizeHorCursor)
                elif (abs(position.y() - geom.top()) < 5 or
                      abs(position.y() - geom.bottom()) < 5):
                    self.setCursor(Qt.SizeVerCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)
                return
        
        self.setCursor(Qt.ArrowCursor)
    
    def create_window(self, title, content_widget, width=800, height=600):
        """Create a new resizable window"""
        window = QWidget(self)
        window.setWindowTitle(title)
        window.setGeometry(100, 100, width, height)
        
        # Window frame
        frame = QFrame(window)
        frame.setGeometry(0, 0, width, height)
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 5px;
            }
        """)
        
        # Title bar
        title_bar = QFrame(frame)
        title_bar.setGeometry(0, 0, width, 30)
        title_bar.setStyleSheet("""
            QFrame {
                background-color: #3d3d3d;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                border-bottom: 1px solid #555;
            }
        """)
        
        # Title label
        title_label = QLabel(title, title_bar)
        title_label.setGeometry(10, 5, width - 100, 20)
        title_label.setStyleSheet("color: white; font-weight: bold;")
        
        # Window controls
        controls = QWidget(title_bar)
        controls.setGeometry(width - 90, 0, 90, 30)
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 5, 0)
        
        # Minimize button
        min_btn = QPushButton("─")
        min_btn.setFixedSize(20, 20)
        min_btn.clicked.connect(window.showMinimized)
        
        # Maximize button
        max_btn = QPushButton("□")
        max_btn.setFixedSize(20, 20)
        max_btn.clicked.connect(lambda: self.toggle_maximize(window))
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(window.close)
        
        for btn in [min_btn, max_btn, close_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4d4d4d;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5d5d5d;
                }
                QPushButton:pressed {
                    background-color: #3d3d3d;
                }
            """)
        
        controls_layout.addWidget(min_btn)
        controls_layout.addWidget(max_btn)
        controls_layout.addWidget(close_btn)
        
        # Content area
        content_area = QWidget(frame)
        content_area.setGeometry(0, 30, width, height - 30)
        content_layout = QVBoxLayout(content_area)
        content_layout.addWidget(content_widget)
        
        # Make window draggable
        window.setWindowFlags(Qt.FramelessWindowHint)
        
        # Add to windows list
        self.windows.append(window)
        self.active_window = window
        
        window.show()
        return window
    
    def toggle_maximize(self, window):
        """Toggle window maximize/restore"""
        if window.isMaximized():
            window.showNormal()
        else:
            window.showMaximized()

def main():
    """Start Windows-style desktop"""
    # Check for X11
    if "DISPLAY" not in os.environ:
        print("⚠️ Start TurboX Desktop first: turbox start")
        return
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    desktop = WindowsDesktop()
    desktop.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
