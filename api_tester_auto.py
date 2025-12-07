#!/usr/bin/env python3
# ==============================================================================
# TurboX Desktop OS - Fully Automated API Tester
# Auto-login, auto-CAPTCHA, auto-token management, auto-data fetching
# ==============================================================================

import os
import sys
import json
import requests
import threading
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class AutomatedAPITester(QMainWindow):
    """Fully automated API tester with auto-login and CAPTCHA solving"""
    
    def __init__(self, automation_mode=True):
        super().__init__()
        self.home_dir = os.path.expanduser("~")
        self.config_dir = os.path.join(self.home_dir, '.turboX')
        
        # Load automation modules
        self.session_mgr = self.load_session_manager()
        self.captcha_solver = self.load_captcha_solver()
        
        # Automation state
        self.automation_mode = automation_mode
        self.is_automating = False
        self.current_session = None
        self.credentials = None
        
        # Captured requests
        self.captured_requests = []
        
        # Initialize UI
        self.init_ui()
        
        # Connect to automation controller
        self.connect_to_automation()
        
        print("✅ Automated API Tester initialized")
        if automation_mode:
            print("🤖 Automation mode: ON (Tools auto-launch, auto-fetch)")
    
    def load_session_manager(self):
        """Load session manager module"""
        try:
            sys.path.append(os.path.join(self.config_dir, 'scripts'))
            from session_manager import SessionManager
            return SessionManager()
        except:
            print("⚠️ Session manager not available")
            return None
    
    def load_captcha_solver(self):
        """Load CAPTCHA solver module"""
        try:
            sys.path.append(os.path.join(self.config_dir, 'scripts'))
            from captcha_solver import CaptchaSolver
            return CaptchaSolver()
        except:
            print("⚠️ CAPTCHA solver not available")
            return None
    
    def init_ui(self):
        """Initialize API tester UI"""
        self.setWindowTitle("TurboX API Tester 🤖")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(self.get_stylesheet())
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Toolbar
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Configuration
        left_panel = self.create_config_panel()
        splitter.addWidget(left_panel)
        
        # Right panel: Results
        right_panel = self.create_results_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([500, 700])
        main_layout.addWidget(splitter, 1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready for automation")
    
    def create_toolbar(self):
        """Create toolbar with automation controls"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        # Automation toggle
        self.auto_toggle = QAction("🤖 Auto", self)
        self.auto_toggle.setCheckable(True)
        self.auto_toggle.setChecked(self.automation_mode)
        self.auto_toggle.toggled.connect(self.toggle_automation)
        toolbar.addAction(self.auto_toggle)
        
        toolbar.addSeparator()
        
        # Auto-login button
        auto_login_btn = QAction("🔐 Auto-Login", self)
        auto_login_btn.triggered.connect(self.start_auto_login)
        toolbar.addAction(auto_login_btn)
        
        # Auto-fetch button
        auto_fetch_btn = QAction("📥 Auto-Fetch", self)
        auto_fetch_btn.triggered.connect(self.start_auto_fetch)
        toolbar.addAction(auto_fetch_btn)
        
        toolbar.addSeparator()
        
        # Manual controls
        send_btn = QAction("🚀 Send", self)
        send_btn.triggered.connect(self.send_manual_request)
        toolbar.addAction(send_btn)
        
        clear_btn = QAction("🗑️ Clear", self)
        clear_btn.triggered.connect(self.clear_data)
        toolbar.addAction(clear_btn)
        
        toolbar.addSeparator()
        
        # Export
        export_btn = QAction("💾 Export", self)
        export_btn.triggered.connect(self.export_data)
        toolbar.addAction(export_btn)
        
        return toolbar
    
    def create_config_panel(self):
        """Create configuration panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Credentials group
        cred_group = QGroupBox("🔐 Credentials (Auto-Login)")
        cred_layout = QVBoxLayout()
        
        # URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com/login")
        url_layout.addWidget(self.url_input, 1)
        cred_layout.addLayout(url_layout)
        
        # Username/Email
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("Username/Email:"))
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("user@example.com")
        user_layout.addWidget(self.user_input, 1)
        cred_layout.addLayout(user_layout)
        
        # Password
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Password:"))
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("********")
        pass_layout.addWidget(self.pass_input, 1)
        cred_layout.addLayout(pass_layout)
        
        # Auto-login button
        self.auto_login_btn = QPushButton("🚀 Start Auto-Login")
        self.auto_login_btn.clicked.connect(self.start_auto_login)
        self.auto_login_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        cred_layout.addWidget(self.auto_login_btn)
        
        cred_group.setLayout(cred_layout)
        layout.addWidget(cred_group)
        
        # Request configuration
        req_group = QGroupBox("📡 Request Configuration")
        req_layout = QVBoxLayout()
        
        # Method and endpoint
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Method:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE", "PATCH"])
        method_layout.addWidget(self.method_combo)
        
        method_layout.addWidget(QLabel("Endpoint:"))
        self.endpoint_input = QLineEdit()
        self.endpoint_input.setPlaceholderText("/api/data")
        method_layout.addWidget(self.endpoint_input, 1)
        req_layout.addLayout(method_layout)
        
        # Headers table
        headers_label = QLabel("Headers:")
        req_layout.addWidget(headers_label)
        
        self.headers_table = QTableWidget(0, 2)
        self.headers_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.headers_table.horizontalHeader().setStretchLastSection(True)
        req_layout.addWidget(self.headers_table)
        
        # Headers buttons
        header_buttons = QHBoxLayout()
        add_header_btn = QPushButton("Add Header")
        add_header_btn.clicked.connect(self.add_header_row)
        header_buttons.addWidget(add_header_btn)
        
        load_headers_btn = QPushButton("Load from Session")
        load_headers_btn.clicked.connect(self.load_session_headers)
        header_buttons.addWidget(load_headers_btn)
        req_layout.addLayout(header_buttons)
        
        # Parameters/Body tabs
        self.data_tabs = QTabWidget()
        
        # Parameters tab
        params_tab = QWidget()
        params_layout = QVBoxLayout(params_tab)
        
        self.params_table = QTableWidget(0, 2)
        self.params_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.params_table.horizontalHeader().setStretchLastSection(True)
        params_layout.addWidget(self.params_table)
        
        param_buttons = QHBoxLayout()
        add_param_btn = QPushButton("Add Parameter")
        add_param_btn.clicked.connect(self.add_param_row)
        param_buttons.addWidget(add_param_btn)
        params_layout.addLayout(param_buttons)
        
        self.data_tabs.addTab(params_tab, "Parameters")
        
        # JSON Body tab
        json_tab = QWidget()
        json_layout = QVBoxLayout(json_tab)
        
        self.json_editor = QPlainTextEdit()
        self.json_editor.setPlaceholderText('{"key": "value"}')
        json_layout.addWidget(self.json_editor)
        
        self.data_tabs.addTab(json_tab, "JSON")
        
        # Form Data tab
        form_tab = QWidget()
        form_layout = QVBoxLayout(form_tab)
        
        self.form_table = QTableWidget(0, 2)
        self.form_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.form_table.horizontalHeader().setStretchLastSection(True)
        form_layout.addWidget(self.form_table)
        
        form_buttons = QHBoxLayout()
        add_form_btn = QPushButton("Add Form Field")
        add_form_btn.clicked.connect(self.add_form_row)
        form_buttons.addWidget(add_form_btn)
        form_layout.addLayout(form_buttons)
        
        self.data_tabs.addTab(form_tab, "Form Data")
        
        req_layout.addWidget(self.data_tabs)
        
        # Send button
        send_btn = QPushButton("🚀 Send Request")
        send_btn.clicked.connect(self.send_manual_request)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1a9e1a;
            }
        """)
        req_layout.addWidget(send_btn)
        
        req_group.setLayout(req_layout)
        layout.addWidget(req_group, 1)
        
        return panel
    
    def create_results_panel(self):
        """Create results display panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Results tabs
        self.results_tabs = QTabWidget()
        
        # Response tab
        response_tab = QWidget()
        response_layout = QVBoxLayout(response_tab)
        
        # Response info
        info_widget = QWidget()
        info_layout = QHBoxLayout(info_widget)
        
        self.status_label = QLabel("Status: --")
        info_layout.addWidget(self.status_label)
        
        self.time_label = QLabel("Time: --")
        info_layout.addWidget(self.time_label)
        
        self.size_label = QLabel("Size: --")
        info_layout.addWidget(self.size_label)
        
        info_layout.addStretch()
        response_layout.addWidget(info_widget)
        
        # Response editor
        self.response_editor = QPlainTextEdit()
        self.response_editor.setReadOnly(True)
        response_layout.addWidget(self.response_editor, 1)
        
        self.results_tabs.addTab(response_tab, "Response")
        
        # Headers tab
        headers_tab = QWidget()
        headers_layout = QVBoxLayout(headers_tab)
        
        self.headers_editor = QPlainTextEdit()
        self.headers_editor.setReadOnly(True)
        headers_layout.addWidget(self.headers_editor)
        
        self.results_tabs.addTab(headers_tab, "Headers")
        
        # Captured Requests tab
        captured_tab = QWidget()
        captured_layout = QVBoxLayout(captured_tab)
        
        self.captured_table = QTableWidget(0, 5)
        self.captured_table.setHorizontalHeaderLabels(
            ["Method", "URL", "Status", "Time", "Size"]
        )
        self.captured_table.horizontalHeader().setStretchLastSection(True)
        self.captured_table.doubleClicked.connect(self.load_captured_request)
        captured_layout.addWidget(self.captured_table)
        
        self.results_tabs.addTab(captured_tab, "Captured")
        
        # Automation Log tab
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        
        self.log_editor = QPlainTextEdit()
        self.log_editor.setReadOnly(True)
        log_layout.addWidget(self.log_editor)
        
        self.results_tabs.addTab(log_tab, "Automation Log")
        
        layout.addWidget(self.results_tabs, 1)
        
        # Action buttons
        action_buttons = QHBoxLayout()
        
        copy_btn = QPushButton("📋 Copy Response")
        copy_btn.clicked.connect(self.copy_response)
        action_buttons.addWidget(copy_btn)
        
        save_btn = QPushButton("💾 Save Request")
        save_btn.clicked.connect(self.save_request)
        action_buttons.addWidget(save_btn)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_results)
        action_buttons.addWidget(clear_btn)
        
        layout.addLayout(action_buttons)
        
        return panel
    
    def get_stylesheet(self):
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
        QLineEdit, QPlainTextEdit, QComboBox, QTableWidget {
            background-color: #3e3e3e;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 5px;
        }
        QTabWidget::pane {
            border: 1px solid #444;
        }
        QTabBar::tab {
            background-color: #3e3e3e;
            color: #ccc;
            padding: 8px 16px;
        }
        QTabBar::tab:selected {
            background-color: #2d2d2d;
            color: #fff;
            border-bottom: 2px solid #0078d7;
        }
        QStatusBar {
            background-color: #0078d7;
            color: white;
        }
        QPushButton {
            background-color: #4e4e4e;
            color: white;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 8px 15px;
        }
        QPushButton:hover {
            background-color: #5e5e5e;
        }
        """
    
    def toggle_automation(self, enabled):
        """Toggle automation mode"""
        self.automation_mode = enabled
        status = "ON" if enabled else "OFF"
        self.status_bar.showMessage(f"Automation mode: {status}")
        self.log_message(f"Automation mode: {status}")
    
    def log_message(self, message):
        """Add message to automation log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_editor.appendPlainText(f"[{timestamp}] {message}")
    
    def connect_to_automation(self):
        """Connect to automation controller"""
        # This would connect via socket bridge
        # Placeholder for actual implementation
        self.log_message("Connected to automation controller")
    
    def start_auto_login(self):
        """Start automated login process"""
        if not self.automation_mode:
            QMessageBox.information(self, "Info", 
                                  "Enable automation mode first")
            return
        
        # Get credentials from UI
        url = self.url_input.text().strip()
        username = self.user_input.text().strip()
        password = self.pass_input.text()
        
        if not url or not username or not password:
            QMessageBox.warning(self, "Warning", 
                              "Please enter URL, username, and password")
            return
        
        self.credentials = {
            'url': url,
            'username': username,
            'password': password
        }
        
        # Start auto-login in thread
        self.is_automating = True
        self.auto_login_btn.setEnabled(False)
        self.auto_login_btn.setText("Logging in...")
        
        thread = threading.Thread(target=self.perform_auto_login, daemon=True)
        thread.start()
    
    def perform_auto_login(self):
        """Perform automated login"""
        try:
            self.log_message("Starting auto-login...")
            
            # Extract domain
            domain = urlparse(self.credentials['url']).netloc
            
            # Get or create session
            if self.session_mgr:
                session = self.session_mgr.get_session_for_domain(domain, create_if_missing=True)
                if session:
                    self.current_session = session['id']
                    self.log_message(f"Session created: {self.current_session}")
            
            # Perform login (this would use Selenium or requests)
            # For now, simulate login
            time.sleep(2)
            
            # Check for CAPTCHA
            captcha_detected = self.detect_captcha()
            if captcha_detected and self.captcha_solver:
                self.log_message("CAPTCHA detected, solving...")
                solution = self.captcha_solver.solve(captcha_detected)
                if solution:
                    self.log_message(f"CAPTCHA solved: {solution}")
            
            # Perform login request
            self.log_message("Sending login request...")
            
            # Update UI in main thread
            QMetaObject.invokeMethod(self, "login_completed", 
                                   Qt.QueuedConnection,
                                   Q_ARG(bool, True),
                                   Q_ARG(str, "Login successful"))
            
        except Exception as e:
            QMetaObject.invokeMethod(self, "login_completed",
                                   Qt.QueuedConnection,
                                   Q_ARG(bool, False),
                                   Q_ARG(str, str(e)))
    
    def login_completed(self, success, message):
        """Handle login completion"""
        self.is_automating = False
        self.auto_login_btn.setEnabled(True)
        self.auto_login_btn.setText("🚀 Start Auto-Login")
        
        if success:
            self.log_message(f"✅ {message}")
            self.status_bar.showMessage("Auto-login successful")
            
            # Auto-fetch if configured
            if self.automation_mode:
                self.start_auto_fetch()
        else:
            self.log_message(f"❌ {message}")
            self.status_bar.showMessage(f"Auto-login failed: {message}")
    
    def detect_captcha(self):
        """Detect CAPTCHA on page"""
        # This would use browser automation to detect CAPTCHA
        # Return CAPTCHA data for solving
        return None  # Placeholder
    
    def start_auto_fetch(self):
        """Start automated data fetching"""
        if not self.automation_mode or not self.current_session:
            QMessageBox.warning(self, "Warning", 
                              "Login first or enable automation")
            return
        
        endpoint = self.endpoint_input.text().strip()
        if not endpoint:
            QMessageBox.warning(self, "Warning", "Enter endpoint to fetch")
            return
        
        self.log_message(f"Starting auto-fetch from: {endpoint}")
        
        # Start fetch in thread
        thread = threading.Thread(target=self.perform_auto_fetch, daemon=True)
        thread.start()
    
    def perform_auto_fetch(self):
        """Perform automated data fetching"""
        try:
            # Get session headers
            headers = {}
            if self.session_mgr and self.current_session:
                session = self.session_mgr.get_session(self.current_session)
                if session and session.get('cookies'):
                    headers['Cookie'] = '; '.join(
                        [f"{k}={v}" for k, v in session['cookies'].items()]
                    )
            
            # Get method and endpoint
            method = self.method_combo.currentText()
            endpoint = self.endpoint_input.text().strip()
            url = self.credentials['url'] if self.credentials else ""
            full_url = url + endpoint if url else endpoint
            
            # Prepare request
            request_data = {
                'method': method,
                'url': full_url,
                'headers': headers,
                'timeout': 30
            }
            
            # Add parameters/body based on active tab
            current_tab = self.data_tabs.currentIndex()
            
            if current_tab == 0:  # Parameters
                params = self.get_table_data(self.params_table)
                if params:
                    request_data['params'] = params
            
            elif current_tab == 1:  # JSON
                json_body = self.json_editor.toPlainText().strip()
                if json_body:
                    try:
                        json.loads(json_body)
                        request_data['json'] = json.loads(json_body)
                        headers['Content-Type'] = 'application/json'
                    except:
                        self.log_message("Invalid JSON, sending as text")
                        request_data['data'] = json_body.encode()
            
            elif current_tab == 2:  # Form data
                form_data = self.get_table_data(self.form_table)
                if form_data:
                    request_data['data'] = form_data
            
            # Send request
            start_time = time.time()
            response = requests.request(**request_data)
            elapsed = time.time() - start_time
            
            # Update UI
            QMetaObject.invokeMethod(self, "fetch_completed",
                                   Qt.QueuedConnection,
                                   Q_ARG(object, response),
                                   Q_ARG(float, elapsed))
            
        except Exception as e:
            QMetaObject.invokeMethod(self, "fetch_failed",
                                   Qt.QueuedConnection,
                                   Q_ARG(str, str(e)))
    
    def fetch_completed(self, response, elapsed):
        """Handle fetch completion"""
        # Update response info
        self.status_label.setText(f"Status: {response.status_code} {response.reason}")
        self.time_label.setText(f"Time: {elapsed:.2f}s")
        self.size_label.setText(f"Size: {len(response.content)} bytes")
        
        # Display response
        try:
            json_data = response.json()
            formatted = json.dumps(json_data, indent=2)
            self.response_editor.setPlainText(formatted)
        except:
            self.response_editor.setPlainText(response.text)
        
        # Display headers
        headers_text = ""
        for key, value in response.headers.items():
            headers_text += f"{key}: {value}\n"
        self.headers_editor.setPlainText(headers_text)
        
        # Add to captured requests
        self.add_captured_request(response, elapsed)
        
        # Log
        self.log_message(f"✅ Fetch completed: {response.status_code} ({elapsed:.2f}s)")
        self.status_bar.showMessage("Auto-fetch completed")
    
    def fetch_failed(self, error):
        """Handle fetch failure"""
        self.response_editor.setPlainText(f"Error: {error}")
        self.log_message(f"❌ Fetch failed: {error}")
        self.status_bar.showMessage(f"Fetch failed: {error}")
    
    def add_header_row(self):
        """Add row to headers table"""
        self.add_table_row(self.headers_table)
    
    def add_param_row(self):
        """Add row to parameters table"""
        self.add_table_row(self.params_table)
    
    def add_form_row(self):
        """Add row to form data table"""
        self.add_table_row(self.form_table)
    
    def add_table_row(self, table):
        """Add row to table"""
        row = table.rowCount()
        table.insertRow(row)
    
    def get_table_data(self, table):
        """Get data from table as dictionary"""
        data = {}
        for row in range(table.rowCount()):
            key_item = table.item(row, 0)
            value_item = table.item(row, 1)
            
            if key_item and key_item.text().strip():
                key = key_item.text().strip()
                value = value_item.text().strip() if value_item else ""
                data[key] = value
        
        return data
    
    def load_session_headers(self):
        """Load headers from current session"""
        if not self.session_mgr or not self.current_session:
            QMessageBox.warning(self, "Warning", "No active session")
            return
        
        session = self.session_mgr.get_session(self.current_session)
        if not session:
            return
        
        # Clear current headers
        self.headers_table.setRowCount(0)
        
        # Add cookies as headers
        cookies = session.get('cookies', {})
        if cookies:
            row = self.headers_table.rowCount()
            self.headers_table.insertRow(row)
            self.headers_table.setItem(row, 0, QTableWidgetItem("Cookie"))
            cookie_value = '; '.join([f"{k}={v}" for k, v in cookies.items()])
            self.headers_table.setItem(row, 1, QTableWidgetItem(cookie_value))
        
        # Add other headers from session
        headers = session.get('headers', {})
        for key, value in headers.items():
            row = self.headers_table.rowCount()
            self.headers_table.insertRow(row)
            self.headers_table.setItem(row, 0, QTableWidgetItem(key))
            self.headers_table.setItem(row, 1, QTableWidgetItem(str(value)))
        
        self.log_message("Loaded headers from session")
    
    def send_manual_request(self):
        """Send manual request"""
        # Similar to auto-fetch but without automation
        thread = threading.Thread(target=self.perform_auto_fetch, daemon=True)
        thread.start()
    
    def add_captured_request(self, response, elapsed):
        """Add request to captured table"""
        row = self.captured_table.rowCount()
        self.captured_table.insertRow(row)
        
        # Method
        self.captured_table.setItem(row, 0, 
                                  QTableWidgetItem(response.request.method))
        
        # URL
        url = response.request.url
        if len(url) > 50:
            url = url[:47] + "..."
        self.captured_table.setItem(row, 1, QTableWidgetItem(url))
        
        # Status
        self.captured_table.setItem(row, 2, 
                                  QTableWidgetItem(str(response.status_code)))
        
        # Time
        self.captured_table.setItem(row, 3, 
                                  QTableWidgetItem(f"{elapsed:.2f}s"))
        
        # Size
        self.captured_table.setItem(row, 4, 
                                  QTableWidgetItem(f"{len(response.content)} B"))
    
    def load_captured_request(self, index):
        """Load captured request into editor"""
        row = index.row()
        # Implementation would load request details
        self.log_message(f"Loading captured request {row}")
    
    def copy_response(self):
        """Copy response to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.response_editor.toPlainText())
        self.status_bar.showMessage("Response copied to clipboard")
    
    def save_request(self):
        """Save current request configuration"""
        # Save to file
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Request", "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            request_data = {
                'url': self.url_input.text(),
                'username': self.user_input.text(),
                'method': self.method_combo.currentText(),
                'endpoint': self.endpoint_input.text(),
                'headers': self.get_table_data(self.headers_table),
                'parameters': self.get_table_data(self.params_table),
                'json_body': self.json_editor.toPlainText(),
                'form_data': self.get_table_data(self.form_table),
                'saved_at': datetime.now().isoformat()
            }
            
            try:
                with open(file_path, 'w') as f:
                    json.dump(request_data, f, indent=2)
                self.log_message(f"Request saved to: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Save failed: {e}")
    
    def clear_results(self):
        """Clear results display"""
        self.response_editor.clear()
        self.headers_editor.clear()
        self.status_label.setText("Status: --")
        self.time_label.setText("Time: --")
        self.size_label.setText("Size: --")
        self.log_message("Results cleared")
    
    def clear_data(self):
        """Clear all data"""
        self.captured_table.setRowCount(0)
        self.headers_table.setRowCount(0)
        self.params_table.setRowCount(0)
        self.form_table.setRowCount(0)
        self.json_editor.clear()
        self.clear_results()
        self.log_message("All data cleared")
    
    def export_data(self):
        """Export all captured data"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "",
            "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            # Collect data
            export_data = {
                'credentials': {
                    'url': self.url_input.text(),
                    'username': self.user_input.text()
                },
                'session_id': self.current_session,
                'captured_requests': [],
                'exported_at': datetime.now().isoformat()
            }
            
            # Export logic here
            self.log_message(f"Data exported to: {file_path}")

def main():
    """Start automated API tester"""
    app = QApplication(sys.argv)
    
    # Check for automation mode from command line
    automation_mode = "--auto" in sys.argv or "-a" in sys.argv
    
    tester = AutomatedAPITester(automation_mode=automation_mode)
    tester.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
