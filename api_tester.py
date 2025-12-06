#!/data/data/com.termux/files/usr/bin/python3
# ==============================================================================
# TurboX Desktop OS - API Tester Core
# Phase 2: API Testing with GUI
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

class APITester(QMainWindow):
    """Main API Tester application"""
    
    def __init__(self):
        super().__init__()
        self.home_dir = os.path.expanduser("~")
        self.config_dir = os.path.join(self.home_dir, '.turboX')
        self.requests_file = os.path.join(self.config_dir, 'tools', 'api_requests.json')
        self.history_file = os.path.join(self.config_dir, 'tools', 'api_history.json')
        
        # Load saved data
        self.saved_requests = self._load_json(self.requests_file, [])
        self.history = self._load_json(self.history_file, [])
        
        # Current request state
        self.current_request = {
            "name": "",
            "url": "",
            "method": "GET",
            "headers": {},
            "params": {},
            "body": "",
            "auth": {}
        }
        
        # Browser extension connection
        self.browser_data = []
        self.connected_to_browser = False
        
        # Initialize UI
        self.init_ui()
        
        # Try to connect to browser extension
        self.connect_to_browser()
    
    def _load_json(self, filepath, default):
        """Load JSON file or return default"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  Load error {filepath}: {e}")
        return default
    
    def _save_json(self, filepath, data):
        """Save data to JSON file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Save error {filepath}: {e}")
            return False
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("TurboX API Tester")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(self._get_stylesheet())
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Top toolbar
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Splitter for request/response
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Request configuration
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Request configuration
        config_group = QGroupBox("Request Configuration")
        config_layout = QVBoxLayout()
        
        # Method and URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Method:"))
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
        self.method_combo.setFixedWidth(100)
        url_layout.addWidget(self.method_combo)
        
        url_layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://api.example.com/endpoint")
        url_layout.addWidget(self.url_input, 1)
        
        config_layout.addLayout(url_layout)
        
        # Headers table
        headers_label = QLabel("Headers:")
        config_layout.addWidget(headers_label)
        
        self.headers_table = QTableWidget(0, 2)
        self.headers_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.headers_table.horizontalHeader().setStretchLastSection(True)
        config_layout.addWidget(self.headers_table)
        
        # Header buttons
        header_buttons = QHBoxLayout()
        add_header_btn = QPushButton("Add Header")
        add_header_btn.clicked.connect(self.add_header_row)
        header_buttons.addWidget(add_header_btn)
        
        remove_header_btn = QPushButton("Remove Selected")
        remove_header_btn.clicked.connect(self.remove_header_row)
        header_buttons.addWidget(remove_header_btn)
        
        config_layout.addLayout(header_buttons)
        
        # Parameters/Query string
        params_label = QLabel("Query Parameters:")
        config_layout.addWidget(params_label)
        
        self.params_table = QTableWidget(0, 2)
        self.params_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.params_table.horizontalHeader().setStretchLastSection(True)
        config_layout.addWidget(self.params_table)
        
        # Parameter buttons
        param_buttons = QHBoxLayout()
        add_param_btn = QPushButton("Add Parameter")
        add_param_btn.clicked.connect(self.add_param_row)
        param_buttons.addWidget(add_param_btn)
        
        remove_param_btn = QPushButton("Remove Selected")
        remove_param_btn.clicked.connect(self.remove_param_row)
        param_buttons.addWidget(remove_param_btn)
        
        config_layout.addLayout(param_buttons)
        
        # Request body
        body_label = QLabel("Request Body:")
        config_layout.addWidget(body_label)
        
        self.body_tabs = QTabWidget()
        
        # Raw JSON tab
        self.json_editor = QPlainTextEdit()
        self.json_editor.setPlaceholderText('{"key": "value"}')
        self.body_tabs.addTab(self.json_editor, "JSON")
        
        # Form data tab
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        self.form_table = QTableWidget(0, 2)
        self.form_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.form_table.horizontalHeader().setStretchLastSection(True)
        form_layout.addWidget(self.form_table)
        
        form_buttons = QHBoxLayout()
        add_form_btn = QPushButton("Add Form Field")
        add_form_btn.clicked.connect(self.add_form_row)
        form_buttons.addWidget(add_form_btn)
        
        remove_form_btn = QPushButton("Remove Selected")
        remove_form_btn.clicked.connect(self.remove_form_row)
        form_buttons.addWidget(remove_form_btn)
        
        form_layout.addLayout(form_buttons)
        self.body_tabs.addTab(form_widget, "Form Data")
        
        # Text tab
        self.text_editor = QPlainTextEdit()
        self.body_tabs.addTab(self.text_editor, "Text")
        
        config_layout.addWidget(self.body_tabs)
        
        config_group.setLayout(config_layout)
        left_layout.addWidget(config_group, 1)
        
        # Authentication section
        auth_group = QGroupBox("Authentication")
        auth_layout = QVBoxLayout()
        
        auth_type_combo = QComboBox()
        auth_type_combo.addItems(["None", "Basic Auth", "Bearer Token", "API Key"])
        auth_layout.addWidget(auth_type_combo)
        
        # Auth fields (initially hidden)
        self.auth_fields = QStackedWidget()
        
        # None
        none_widget = QWidget()
        self.auth_fields.addWidget(none_widget)
        
        # Basic Auth
        basic_widget = QWidget()
        basic_layout = QVBoxLayout(basic_widget)
        basic_layout.addWidget(QLabel("Username:"))
        self.basic_user = QLineEdit()
        basic_layout.addWidget(self.basic_user)
        basic_layout.addWidget(QLabel("Password:"))
        self.basic_pass = QLineEdit()
        self.basic_pass.setEchoMode(QLineEdit.Password)
        basic_layout.addWidget(self.basic_pass)
        self.auth_fields.addWidget(basic_widget)
        
        # Bearer Token
        bearer_widget = QWidget()
        bearer_layout = QVBoxLayout(bearer_widget)
        bearer_layout.addWidget(QLabel("Token:"))
        self.bearer_token = QLineEdit()
        bearer_layout.addWidget(self.bearer_token)
        self.auth_fields.addWidget(bearer_widget)
        
        # API Key
        apikey_widget = QWidget()
        apikey_layout = QVBoxLayout(apikey_widget)
        apikey_layout.addWidget(QLabel("Key:"))
        self.api_key = QLineEdit()
        apikey_layout.addWidget(self.api_key)
        apikey_layout.addWidget(QLabel("Value:"))
        self.api_value = QLineEdit()
        apikey_layout.addWidget(self.api_value)
        apikey_layout.addWidget(QLabel("In:"))
        self.api_location = QComboBox()
        self.api_location.addItems(["Header", "Query"])
        apikey_layout.addWidget(self.api_location)
        self.auth_fields.addWidget(apikey_widget)
        
        auth_layout.addWidget(self.auth_fields)
        auth_type_combo.currentIndexChanged.connect(self.auth_fields.setCurrentIndex)
        
        auth_group.setLayout(auth_layout)
        left_layout.addWidget(auth_group)
        
        # Send button
        send_btn = QPushButton("🚀 Send Request")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1a9e1a;
            }
        """)
        send_btn.clicked.connect(self.send_request)
        left_layout.addWidget(send_btn)
        
        # Right panel: Response viewer
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Response info
        info_group = QGroupBox("Response Information")
        info_layout = QVBoxLayout()
        
        self.status_label = QLabel("Status: Not sent")
        info_layout.addWidget(self.status_label)
        
        self.time_label = QLabel("Time: --")
        info_layout.addWidget(self.time_label)
        
        self.size_label = QLabel("Size: --")
        info_layout.addWidget(self.size_label)
        
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)
        
        # Response body tabs
        response_tabs = QTabWidget()
        
        # Pretty JSON viewer
        self.response_editor = QPlainTextEdit()
        self.response_editor.setReadOnly(True)
        response_tabs.addTab(self.response_editor, "Body")
        
        # Headers viewer
        self.headers_viewer = QPlainTextEdit()
        self.headers_viewer.setReadOnly(True)
        response_tabs.addTab(self.headers_viewer, "Headers")
        
        # Browser captured data
        self.browser_viewer = QTableWidget(0, 4)
        self.browser_viewer.setHorizontalHeaderLabels(["Method", "URL", "Status", "Time"])
        self.browser_viewer.horizontalHeader().setStretchLastSection(True)
        response_tabs.addTab(self.browser_viewer, "Browser Captures")
        
        right_layout.addWidget(response_tabs, 1)
        
        # Response action buttons
        action_buttons = QHBoxLayout()
        
        copy_btn = QPushButton("Copy Response")
        copy_btn.clicked.connect(self.copy_response)
        action_buttons.addWidget(copy_btn)
        
        save_btn = QPushButton("Save Request")
        save_btn.clicked.connect(self.save_request)
        action_buttons.addWidget(save_btn)
        
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_data)
        action_buttons.addWidget(export_btn)
        
        right_layout.addLayout(action_buttons)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 700])
        
        main_layout.addWidget(splitter, 1)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Load first saved request if exists
        if self.saved_requests:
            self.load_request(0)
    
    def _create_toolbar(self):
        """Create the main toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        # New request
        new_action = QAction("📄 New", self)
        new_action.triggered.connect(self.new_request)
        toolbar.addAction(new_action)
        
        toolbar.addSeparator()
        
        # Save request
        save_action = QAction("💾 Save", self)
        save_action.triggered.connect(self.save_request)
        toolbar.addAction(save_action)
        
        # Load request dropdown
        load_btn = QPushButton("📂 Load")
        load_menu = QMenu()
        
        for i, req in enumerate(self.saved_requests):
            action = QAction(req.get('name', f'Request {i+1}'), self)
            action.triggered.connect(lambda checked, idx=i: self.load_request(idx))
            load_menu.addAction(action)
        
        if not self.saved_requests:
            no_action = QAction("No saved requests", self)
            no_action.setEnabled(False)
            load_menu.addAction(no_action)
        
        load_btn.setMenu(load_menu)
        toolbar.addWidget(load_btn)
        
        toolbar.addSeparator()
        
        # Browser integration
        browser_btn = QPushButton("🌐 Browser Data")
        browser_btn.clicked.connect(self.show_browser_data)
        toolbar.addWidget(browser_btn)
        
        # SMS Panel toggle
        self.sms_toggle = QPushButton("📱 SMS Panel: OFF")
        self.sms_toggle.setCheckable(True)
        self.sms_toggle.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:checked {
                background-color: #107c10;
            }
        """)
        self.sms_toggle.toggled.connect(self.toggle_sms_panel)
        toolbar.addWidget(self.sms_toggle)
        
        toolbar.addSeparator()
        
        # Settings
        settings_action = QAction("⚙️ Settings", self)
        toolbar.addAction(settings_action)
        
        return toolbar
    
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
        QLineEdit, QPlainTextEdit, QComboBox, QTableWidget {
            background-color: #3e3e3e;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 5px;
        }
        QHeaderView::section {
            background-color: #3e3e3e;
            padding: 5px;
            border: 1px solid #555;
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
        """
    
    def add_header_row(self):
        """Add a new row to headers table"""
        row = self.headers_table.rowCount()
        self.headers_table.insertRow(row)
    
    def remove_header_row(self):
        """Remove selected rows from headers table"""
        selected = self.headers_table.selectionModel().selectedRows()
        for index in sorted(selected, key=lambda x: x.row(), reverse=True):
            self.headers_table.removeRow(index.row())
    
    def add_param_row(self):
        """Add a new row to parameters table"""
        row = self.params_table.rowCount()
        self.params_table.insertRow(row)
    
    def remove_param_row(self):
        """Remove selected rows from parameters table"""
        selected = self.params_table.selectionModel().selectedRows()
        for index in sorted(selected, key=lambda x: x.row(), reverse=True):
            self.params_table.removeRow(index.row())
    
    def add_form_row(self):
        """Add a new row to form data table"""
        row = self.form_table.rowCount()
        self.form_table.insertRow(row)
    
    def remove_form_row(self):
        """Remove selected rows from form data table"""
        selected = self.form_table.selectionModel().selectedRows()
        for index in sorted(selected, key=lambda x: x.row(), reverse=True):
            self.form_table.removeRow(index.row())
    
    def get_headers_from_table(self):
        """Extract headers from table"""
        headers = {}
        for row in range(self.headers_table.rowCount()):
            key_item = self.headers_table.item(row, 0)
            value_item = self.headers_table.item(row, 1)
            
            if key_item and key_item.text().strip():
                key = key_item.text().strip()
                value = value_item.text().strip() if value_item else ""
                headers[key] = value
        return headers
    
    def get_params_from_table(self):
        """Extract parameters from table"""
        params = {}
        for row in range(self.params_table.rowCount()):
            key_item = self.params_table.item(row, 0)
            value_item = self.params_table.item(row, 1)
            
            if key_item and key_item.text().strip():
                key = key_item.text().strip()
                value = value_item.text().strip() if value_item else ""
                params[key] = value
        return params
    
    def get_form_from_table(self):
        """Extract form data from table"""
        form_data = {}
        for row in range(self.form_table.rowCount()):
            key_item = self.form_table.item(row, 0)
            value_item = self.form_table.item(row, 1)
            
            if key_item and key_item.text().strip():
                key = key_item.text().strip()
                value = value_item.text().strip() if value_item else ""
                form_data[key] = value
        return form_data
    
    def send_request(self):
        """Send the API request"""
        # Get request data
        method = self.method_combo.currentText()
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return
        
        # Prepare request
        headers = self.get_headers_from_table()
        params = self.get_params_from_table()
        
        # Get body based on active tab
        body = None
        content_type = None
        
        current_tab = self.body_tabs.currentIndex()
        if current_tab == 0:  # JSON
            body = self.json_editor.toPlainText()
            if body.strip():
                try:
                    json.loads(body)  # Validate JSON
                    headers['Content-Type'] = 'application/json'
                except json.JSONDecodeError:
                    QMessageBox.warning(self, "Invalid JSON", "Please enter valid JSON")
                    return
        elif current_tab == 1:  # Form data
            form_data = self.get_form_from_table()
            if form_data:
                body = form_data
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
        elif current_tab == 2:  # Text
            body = self.text_editor.toPlainText()
            if body.strip():
                headers['Content-Type'] = 'text/plain'
        
        # Update UI
        self.statusBar().showMessage("Sending request...")
        start_time = time.time()
        
        # Send request in thread
        thread = threading.Thread(
            target=self._send_request_thread,
            args=(method, url, headers, params, body),
            daemon=True
        )
        thread.start()
    
    def _send_request_thread(self, method, url, headers, params, body):
        """Thread function to send request"""
        try:
            # Convert request
            req_args = {
                'method': method,
                'url': url,
                'headers': headers,
                'params': params,
                'timeout': 30
            }
            
            if body:
                if isinstance(body, dict):
                    req_args['data'] = body
                else:
                    req_args['data'] = body.encode('utf-8')
            
            # Send request
            response = requests.request(**req_args)
            elapsed = time.time() - start_time
            
            # Update UI in main thread
            QMetaObject.invokeMethod(self, "_update_response_ui", 
                                   Qt.QueuedConnection,
                                   Q_ARG(object, response),
                                   Q_ARG(float, elapsed))
            
        except Exception as e:
            QMetaObject.invokeMethod(self, "_show_error", 
                                   Qt.QueuedConnection,
                                   Q_ARG(str, str(e)))
    
    def _update_response_ui(self, response, elapsed):
        """Update UI with response (called from main thread)"""
        # Update status labels
        self.status_label.setText(f"Status: {response.status_code} {response.reason}")
        self.time_label.setText(f"Time: {elapsed:.2f}s")
        self.size_label.setText(f"Size: {len(response.content)} bytes")
        
        # Display response body
        try:
            # Try to format as JSON
            json_data = response.json()
            formatted = json.dumps(json_data, indent=2)
            self.response_editor.setPlainText(formatted)
        except:
            # Display as text
            self.response_editor.setPlainText(response.text)
        
        # Display headers
        headers_text = ""
        for key, value in response.headers.items():
            headers_text += f"{key}: {value}\n"
        self.headers_viewer.setPlainText(headers_text)
        
        # Add to history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "method": response.request.method,
            "url": response.request.url,
            "status": response.status_code,
            "time": elapsed,
            "size": len(response.content)
        }
        self.history.append(history_entry)
        self._save_json(self.history_file, self.history)
        
        self.statusBar().showMessage(f"Request completed in {elapsed:.2f}s")
    
    def _show_error(self, error_msg):
        """Show error message"""
        self.response_editor.setPlainText(f"Error: {error_msg}")
        self.status_label.setText("Status: Error")
        self.statusBar().showMessage(f"Error: {error_msg}")
    
    def new_request(self):
        """Create a new empty request"""
        self.url_input.clear()
        self.headers_table.setRowCount(0)
        self.params_table.setRowCount(0)
        self.form_table.setRowCount(0)
        self.json_editor.clear()
        self.text_editor.clear()
        self.response_editor.clear()
        self.headers_viewer.clear()
        
        self.status_label.setText("Status: Not sent")
        self.time_label.setText("Time: --")
        self.size_label.setText("Size: --")
        
        self.statusBar().showMessage("New request created")
    
    def save_request(self):
        """Save current request"""
        name, ok = QInputDialog.getText(self, "Save Request", "Enter request name:")
        if ok and name:
            request_data = {
                "name": name,
                "url": self.url_input.text(),
                "method": self.method_combo.currentText(),
                "headers": self.get_headers_from_table(),
                "params": self.get_params_from_table(),
                "body": self.json_editor.toPlainText(),
                "form_data": self.get_form_from_table(),
                "text_body": self.text_editor.toPlainText(),
                "saved_at": datetime.now().isoformat()
            }
            
            self.saved_requests.append(request_data)
            self._save_json(self.requests_file, self.saved_requests)
            
            self.statusBar().showMessage(f"Request '{name}' saved")
    
    def load_request(self, index):
        """Load a saved request"""
        if 0 <= index < len(self.saved_requests):
            req = self.saved_requests[index]
            
            self.url_input.setText(req.get("url", ""))
            
            method = req.get("method", "GET")
            method_index = self.method_combo.findText(method)
            if method_index >= 0:
                self.method_combo.setCurrentIndex(method_index)
            
            # Load headers
            self.headers_table.setRowCount(0)
            headers = req.get("headers", {})
            for key, value in headers.items():
                row = self.headers_table.rowCount()
                self.headers_table.insertRow(row)
                self.headers_table.setItem(row, 0, QTableWidgetItem(key))
                self.headers_table.setItem(row, 1, QTableWidgetItem(str(value)))
            
            # Load params
            self.params_table.setRowCount(0)
            params = req.get("params", {})
            for key, value in params.items():
                row = self.params_table.rowCount()
                self.params_table.insertRow(row)
                self.params_table.setItem(row, 0, QTableWidgetItem(key))
                self.params_table.setItem(row, 1, QTableWidgetItem(str(value)))
            
            # Load body
            self.json_editor.setPlainText(req.get("body", ""))
            
            # Load form data
            self.form_table.setRowCount(0)
            form_data = req.get("form_data", {})
            for key, value in form_data.items():
                row = self.form_table.rowCount()
                self.form_table.insertRow(row)
                self.form_table.setItem(row, 0, QTableWidgetItem(key))
                self.form_table.setItem(row, 1, QTableWidgetItem(str(value)))
            
            self.text_editor.setPlainText(req.get("text_body", ""))
            
            self.statusBar().showMessage(f"Loaded: {req.get('name', 'Unknown')}")
    
    def copy_response(self):
        """Copy response to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.response_editor.toPlainText())
        self.statusBar().showMessage("Response copied to clipboard")
    
    def export_data(self):
        """Export request/response data"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", 
            "JSON Files (*.json);;CSV Files (*.csv);;Text Files (*.txt)",
            options=options
        )
        
        if file_path:
            export_data = {
                "request": {
                    "url": self.url_input.text(),
                    "method": self.method_combo.currentText(),
                    "headers": self.get_headers_from_table(),
                    "params": self.get_params_from_table()
                },
                "response": {
                    "body": self.response_editor.toPlainText(),
                    "headers": self.headers_viewer.toPlainText(),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'w') as f:
                        json.dump(export_data, f, indent=2)
                elif file_path.endswith('.csv'):
                    # Simple CSV export
                    import csv
                    with open(file_path, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Type', 'Key', 'Value'])
                        for key, value in export_data['request']['headers'].items():
                            writer.writerow(['Header', key, value])
                        for key, value in export_data['request']['params'].items():
                            writer.writerow(['Param', key, value])
                else:
                    with open(file_path, 'w') as f:
                        f.write(str(export_data))
                
                self.statusBar().showMessage(f"Data exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))
    
    def connect_to_browser(self):
        """Attempt to connect to browser extension"""
        # This will be implemented in Phase 3 with socket connection
        self.statusBar().showMessage("Browser connection: Not implemented in Phase 2")
    
    def show_browser_data(self):
        """Show data captured from browser"""
        # Placeholder for Phase 3
        QMessageBox.information(self, "Browser Data", 
                              "Browser integration will be available in Phase 3")
    
    def toggle_sms_panel(self, enabled):
        """Toggle SMS panel integration"""
        if enabled:
            self.sms_toggle.setText("📱 SMS Panel: ON")
            self.statusBar().showMessage("SMS Panel enabled (Phase 3)")
        else:
            self.sms_toggle.setText("📱 SMS Panel: OFF")
            self.statusBar().showMessage("SMS Panel disabled")

def main():
    """Entry point"""
    # Check for X11
    if "DISPLAY" not in os.environ:
        print("⚠️  Please start TurboX Desktop first")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    tester = APITester()
    tester.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
