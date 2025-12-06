#!/usr/bin/env python3
# ==============================================================================
# TurboX Desktop OS - Automation Controller
# Phase 3: Automatic Tool Launch & Coordination
# ==============================================================================

import os
import sys
import json
import time
import threading
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class AutomationController:
    """Central controller for automatic tool management"""
    
    def __init__(self):
        self.home_dir = os.path.expanduser("~")
        self.config_dir = os.path.join(self.home_dir, '.turboX')
        self.config_file = os.path.join(self.config_dir, 'config', 'automation.json')
        
        # Load configuration
        self.config = self._load_config()
        
        # Running tools
        self.running_tools = {
            'api_tester': None,
            'sms_panel': None,
            'socket_bridge': None,
            'session_manager': None
        }
        
        # Browser connection state
        self.browser_connected = False
        self.last_browser_activity = None
        
        # Automation rules
        self.automation_rules = self.config.get('automation_rules', {})
        
        # Start monitoring
        self.monitor_thread = threading.Thread(target=self._monitor_tools, daemon=True)
        self.monitor_thread.start()
        
        print("🤖 Automation Controller initialized")
    
    def _load_config(self):
        """Load automation configuration"""
        default_config = {
            'auto_launch': {
                'api_tester': True,
                'sms_panel': True,
                'on_browser_connect': True
            },
            'automation_rules': {
                'auto_captcha': True,
                'auto_session': True,
                'auto_data_export': False,
                'auto_refresh': 300  # seconds
            },
            'browser_integration': {
                'port': 8765,
                'auto_connect': True
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                
                return config
            else:
                return default_config
        
        except Exception as e:
            print(f"⚠️ Config load error: {e}")
            return default_config
    
    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Config save error: {e}")
            return False
    
    def launch_tool(self, tool_name, auto_restart=True):
        """Launch a tool automatically"""
        try:
            if self.running_tools.get(tool_name):
                print(f"⚠️ {tool_name} is already running")
                return True
            
            script_path = None
            
            if tool_name == 'api_tester':
                script_path = os.path.join(os.path.dirname(__file__), 'api_tester.py')
            elif tool_name == 'sms_panel':
                script_path = os.path.join(os.path.dirname(__file__), 'sms_panel.py')
            elif tool_name == 'socket_bridge':
                script_path = os.path.join(os.path.dirname(__file__), 'socket_bridge.py')
            elif tool_name == 'session_manager':
                # Session manager runs as service, not GUI
                return True
            
            if script_path and os.path.exists(script_path):
                # Launch tool
                if tool_name in ['api_tester', 'sms_panel']:
                    # GUI tools - run in separate process
                    process = subprocess.Popen([sys.executable, script_path])
                    self.running_tools[tool_name] = {
                        'process': process,
                        'pid': process.pid,
                        'started': datetime.now().isoformat(),
                        'auto_restart': auto_restart
                    }
                else:
                    # Service tools - run in thread
                    thread = threading.Thread(
                        target=self._run_tool_script,
                        args=(tool_name, script_path),
                        daemon=True
                    )
                    thread.start()
                
                print(f"🚀 Launched {tool_name}")
                return True
            else:
                print(f"❌ Tool script not found: {tool_name}")
                return False
        
        except Exception as e:
            print(f"❌ Launch error for {tool_name}: {e}")
            return False
    
    def _run_tool_script(self, tool_name, script_path):
        """Run a tool script in thread"""
        try:
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.running_tools[tool_name] = {
                'process': process,
                'pid': process.pid,
                'started': datetime.now().isoformat(),
                'auto_restart': True
            }
            
            # Monitor output
            for line in process.stdout:
                print(f"[{tool_name}] {line.strip()}")
            
            # Check exit
            process.wait()
            print(f"📤 {tool_name} exited with code {process.returncode}")
            
        except Exception as e:
            print(f"❌ {tool_name} thread error: {e}")
        finally:
            self.running_tools[tool_name] = None
    
    def stop_tool(self, tool_name):
        """Stop a running tool"""
        try:
            if tool_name in self.running_tools and self.running_tools[tool_name]:
                tool_info = self.running_tools[tool_name]
                
                if 'process' in tool_info and tool_info['process']:
                    tool_info['process'].terminate()
                    time.sleep(1)
                    
                    if tool_info['process'].poll() is None:
                        tool_info['process'].kill()
                
                self.running_tools[tool_name] = None
                print(f"🛑 Stopped {tool_name}")
                return True
            else:
                print(f"⚠️ {tool_name} is not running")
                return False
        
        except Exception as e:
            print(f"❌ Stop error for {tool_name}: {e}")
            return False
    
    def launch_all_tools(self):
        """Launch all configured tools"""
        print("🚀 Launching all tools...")
        
        # Start socket bridge first (for communication)
        if self.config['auto_launch'].get('socket_bridge', True):
            self.launch_tool('socket_bridge')
            time.sleep(2)  # Wait for socket bridge to start
        
        # Start API Tester
        if self.config['auto_launch'].get('api_tester', True):
            self.launch_tool('api_tester')
        
        # Start SMS Panel
        if self.config['auto_launch'].get('sms_panel', True):
            self.launch_tool('sms_panel')
        
        print("✅ All tools launched")
    
    def stop_all_tools(self):
        """Stop all running tools"""
        print("🛑 Stopping all tools...")
        
        for tool_name in list(self.running_tools.keys()):
            self.stop_tool(tool_name)
        
        print("✅ All tools stopped")
    
    def on_browser_connected(self):
        """Handle browser extension connection"""
        print("🌐 Browser extension connected")
        self.browser_connected = True
        self.last_browser_activity = datetime.now()
        
        # Auto-launch tools if configured
        if self.config['auto_launch'].get('on_browser_connect', True):
            self.launch_all_tools()
        
        # Notify tools about browser connection
        self._notify_tools('browser_connected', {})
    
    def on_browser_disconnected(self):
        """Handle browser extension disconnection"""
        print("🌐 Browser extension disconnected")
        self.browser_connected = False
        
        # Notify tools
        self._notify_tools('browser_disconnected', {})
    
    def on_browser_data(self, data):
        """Handle data from browser extension"""
        self.last_browser_activity = datetime.now()
        
        # Process captured requests
        requests = data.get('requests', [])
        if requests:
            print(f"📥 Received {len(requests)} requests from browser")
            
            # Forward to tools
            self._notify_tools('new_requests', {'requests': requests})
            
            # Auto-process if configured
            if self.automation_rules.get('auto_session', True):
                self._auto_process_requests(requests)
        
        # Process CAPTCHA if present
        captcha_data = data.get('captcha')
        if captcha_data and self.automation_rules.get('auto_captcha', True):
            solution = self._solve_captcha(captcha_data)
            if solution:
                self._notify_tools('captcha_solution', {
                    'captcha': captcha_data,
                    'solution': solution
                })
    
    def _auto_process_requests(self, requests):
        """Automatically process captured requests"""
        from session_manager import SessionManager
        
        session_mgr = SessionManager()
        
        for req in requests:
            # Extract domain
            url = req.get('url', '')
            if not url:
                continue
            
            domain = url.split('/')[2] if '//' in url else url.split('/')[0]
            
            # Get or create session
            session = session_mgr.get_session_for_domain(domain)
            if session:
                session_id = session['id']
                
                # Add request to session
                session_mgr.add_captured_request(session_id, req)
                
                # Extract tokens
                session_mgr.extract_tokens_from_request(session_id, req)
                
                # Check for login
                if 'login' in url.lower() or 'auth' in url.lower():
                    print(f"🔐 Detected login request for {domain}")
                    # Could trigger auto-login here
    
    def _solve_captcha(self, captcha_data):
        """Solve CAPTCHA automatically"""
        from session_manager import SessionManager
        
        session_mgr = SessionManager()
        solution = session_mgr.solve_captcha(captcha_data)
        
        if solution:
            if solution.startswith('MANUAL:'):
                print(f"⚠️ CAPTCHA requires manual solving: {solution}")
                # Could show notification to user
            else:
                print(f"✅ CAPTCHA solved: {solution}")
            
            return solution
        
        return None
    
    def _notify_tools(self, event_type, data):
        """Notify all tools about an event"""
        # This would use socket bridge to send messages
        # Placeholder for Phase 3
        
        print(f"📢 Event: {event_type}, Data: {len(str(data))} chars")
    
    def _monitor_tools(self):
        """Monitor running tools and auto-restart if needed"""
        while True:
            time.sleep(10)  # Check every 10 seconds
            
            try:
                for tool_name, tool_info in list(self.running_tools.items()):
                    if tool_info and 'process' in tool_info:
                        process = tool_info['process']
                        
                        # Check if process is still alive
                        if process.poll() is not None:
                            print(f"⚠️ {tool_name} has stopped (exit code: {process.returncode})")
                            
                            # Auto-restart if configured
                            if tool_info.get('auto_restart', False):
                                print(f"🔄 Auto-restarting {tool_name}...")
                                self.launch_tool(tool_name)
                            
                            self.running_tools[tool_name] = None
                
                # Check browser connection timeout
                if (self.browser_connected and self.last_browser_activity and 
                    (datetime.now() - self.last_browser_activity).seconds > 60):
                    print("⚠️ No browser activity for 60 seconds")
                    self.on_browser_disconnected()
            
            except Exception as e:
                print(f"⚠️ Monitor error: {e}")
    
    def get_status(self):
        """Get current automation status"""
        status = {
            'browser_connected': self.browser_connected,
            'last_activity': self.last_browser_activity.isoformat() if self.last_browser_activity else None,
            'running_tools': {},
            'automation_rules': self.automation_rules
        }
        
        for tool_name, tool_info in self.running_tools.items():
            if tool_info:
                status['running_tools'][tool_name] = {
                    'running': True,
                    'pid': tool_info.get('pid'),
                    'started': tool_info.get('started')
                }
            else:
                status['running_tools'][tool_name] = {'running': False}
        
        return status

class AutomationGUI(QMainWindow):
    """GUI for automation controller"""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        self.init_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(2000)  # Update every 2 seconds
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("TurboX Automation Controller")
        self.setGeometry(200, 200, 800, 500)
        self.setStyleSheet(self._get_stylesheet())
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("🤖 TurboX Automation Controller")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Status panel
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout()
        
        # Browser status
        browser_status = QHBoxLayout()
        browser_status.addWidget(QLabel("Browser Connection:"))
        self.browser_status_label = QLabel("Disconnected")
        self.browser_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        browser_status.addWidget(self.browser_status_label)
        browser_status.addStretch()
        status_layout.addLayout(browser_status)
        
        # Last activity
        self.activity_label = QLabel("Last activity: Never")
        status_layout.addWidget(self.activity_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Tools panel
        tools_group = QGroupBox("Tool Management")
        tools_layout = QVBoxLayout()
        
        # Tool status table
        self.tools_table = QTableWidget(4, 3)
        self.tools_table.setHorizontalHeaderLabels(["Tool", "Status", "Action"])
        self.tools_table.horizontalHeader().setStretchLastSection(True)
        self.tools_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        tools_layout.addWidget(self.tools_table)
        
        # Control buttons
        control_buttons = QHBoxLayout()
        
        self.launch_all_btn = QPushButton("🚀 Launch All")
        self.launch_all_btn.clicked.connect(self.launch_all_tools)
        control_buttons.addWidget(self.launch_all_btn)
        
        self.stop_all_btn = QPushButton("🛑 Stop All")
        self.stop_all_btn.clicked.connect(self.stop_all_tools)
        control_buttons.addWidget(self.stop_all_btn)
        
        tools_layout.addLayout(control_buttons)
        
        tools_group.setLayout(tools_layout)
        layout.addWidget(tools_group)
        
        # Automation rules
        rules_group = QGroupBox("Automation Rules")
        rules_layout = QVBoxLayout()
        
        self.auto_captcha_check = QCheckBox("Auto-solve CAPTCHA")
        self.auto_captcha_check.setChecked(self.controller.automation_rules.get('auto_captcha', True))
        self.auto_captcha_check.toggled.connect(self.toggle_auto_captcha)
        rules_layout.addWidget(self.auto_captcha_check)
        
        self.auto_session_check = QCheckBox("Auto-manage sessions")
        self.auto_session_check.setChecked(self.controller.automation_rules.get('auto_session', True))
        self.auto_session_check.toggled.connect(self.toggle_auto_session)
        rules_layout.addWidget(self.auto_session_check)
        
        self.auto_launch_check = QCheckBox("Auto-launch tools on browser connect")
        self.auto_launch_check.setChecked(self.controller.config['auto_launch'].get('on_browser_connect', True))
        self.auto_launch_check.toggled.connect(self.toggle_auto_launch)
        rules_layout.addWidget(self.auto_launch_check)
        
        rules_group.setLayout(rules_layout)
        layout.addWidget(rules_group)
        
        # Log panel
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Initial update
        self.update_tools_table()
    
    def _get_stylesheet(self):
        """Get application stylesheet"""
        return """
        QMainWindow {
            background-color: #1e1e1e;
        }
        QWidget {
            background-color: #2d2d2d;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #444;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QPushButton {
            background-color: #4e4e4e;
            color: white;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 8px 15px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #5e5e5e;
        }
        QPushButton:pressed {
            background-color: #3e3e3e;
        }
        QTableWidget {
            background-color: #3e3e3e;
            border: 1px solid #555;
            alternate-background-color: #4e4e4e;
        }
        QHeaderView::section {
            background-color: #3e3e3e;
            padding: 5px;
            border: 1px solid #555;
        }
        QTextEdit {
            background-color: #3e3e3e;
            border: 1px solid #555;
            border-radius: 3px;
        }
        QCheckBox {
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        """
    
    def update_status(self):
        """Update status display"""
        status = self.controller.get_status()
        
        # Browser status
        if status['browser_connected']:
            self.browser_status_label.setText("Connected")
            self.browser_status_label.setStyleSheet("color: #1dd1a1; font-weight: bold;")
        else:
            self.browser_status_label.setText("Disconnected")
            self.browser_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        
        # Last activity
        last_activity = status['last_activity']
        if last_activity:
            from datetime import datetime
            last_time = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
            now = datetime.now()
            seconds_ago = int((now - last_time).total_seconds())
            
            if seconds_ago < 60:
                self.activity_label.setText(f"Last activity: {seconds_ago} seconds ago")
            else:
                minutes = seconds_ago // 60
                self.activity_label.setText(f"Last activity: {minutes} minutes ago")
        else:
            self.activity_label.setText("Last activity: Never")
        
        # Update tools table
        self.update_tools_table()
    
    def update_tools_table(self):
        """Update tools table with current status"""
        tools = [
            ('API Tester', 'api_tester'),
            ('SMS Panel', 'sms_panel'),
            ('Socket Bridge', 'socket_bridge'),
            ('Session Manager', 'session_manager')
        ]
        
        self.tools_table.setRowCount(len(tools))
        
        for i, (display_name, tool_name) in enumerate(tools):
            # Tool name
            name_item = QTableWidgetItem(display_name)
            self.tools_table.setItem(i, 0, name_item)
            
            # Status
            status = self.controller.running_tools.get(tool_name)
            if status:
                status_text = "Running"
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(QColor("#1dd1a1"))
            else:
                status_text = "Stopped"
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(QColor("#ff6b6b"))
            
            self.tools_table.setItem(i, 1, status_item)
            
            # Action button
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            if status:
                stop_btn = QPushButton("Stop")
                stop_btn.setStyleSheet("background-color: #ff6b6b;")
                stop_btn.clicked.connect(lambda checked, tn=tool_name: self.stop_tool(tn))
                action_layout.addWidget(stop_btn)
            else:
                start_btn = QPushButton("Start")
                start_btn.setStyleSheet("background-color: #1dd1a1;")
                start_btn.clicked.connect(lambda checked, tn=tool_name: self.start_tool(tn))
                action_layout.addWidget(start_btn)
            
            action_layout.addStretch()
            self.tools_table.setCellWidget(i, 2, action_widget)
        
        self.tools_table.resizeColumnsToContents()
    
    def start_tool(self, tool_name):
        """Start a specific tool"""
        self.controller.launch_tool(tool_name)
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Started {tool_name}")
    
    def stop_tool(self, tool_name):
        """Stop a specific tool"""
        self.controller.stop_tool(tool_name)
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Stopped {tool_name}")
    
    def launch_all_tools(self):
        """Launch all tools"""
        self.controller.launch_all_tools()
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Launched all tools")
    
    def stop_all_tools(self):
        """Stop all tools"""
        self.controller.stop_all_tools()
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Stopped all tools")
    
    def toggle_auto_captcha(self, enabled):
        """Toggle auto-CAPTCHA solving"""
        self.controller.automation_rules['auto_captcha'] = enabled
        self.controller.save_config()
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Auto-CAPTCHA: {'ON' if enabled else 'OFF'}")
    
    def toggle_auto_session(self, enabled):
        """Toggle auto-session management"""
        self.controller.automation_rules['auto_session'] = enabled
        self.controller.save_config()
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Auto-session: {'ON' if enabled else 'OFF'}")
    
    def toggle_auto_launch(self, enabled):
        """Toggle auto-launch on browser connect"""
        self.controller.config['auto_launch']['on_browser_connect'] = enabled
        self.controller.save_config()
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Auto-launch: {'ON' if enabled else 'OFF'}")

def main():
    """Entry point"""
    # Check for X11
    if "DISPLAY" not in os.environ:
        print("⚠️ Please start TurboX Desktop first")
        sys.exit(1)
    
    # Create controller
    controller = AutomationController()
    
    # Start GUI
    app = QApplication(sys.argv)
    gui = AutomationGUI(controller)
    gui.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
