#!/data/data/com.termux/files/usr/bin/python3
# ==============================================================================
# TurboX Desktop OS - SMS Panel
# Phase 2: SMS Data Display
# ==============================================================================

import os
import sys
import json
import csv
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class SMSPanel(QMainWindow):
    """SMS Data Collection and Display Panel"""
    
    def __init__(self):
        super().__init__()
        self.home_dir = os.path.expanduser("~")
        self.config_dir = os.path.join(self.home_dir, '.turboX')
        self.data_file = os.path.join(self.config_dir, 'tools', 'sms_data.json')
        
        # Load SMS data
        self.sms_data = self._load_sms_data()
        
        # Filters
        self.current_filter = "all"
        self.search_text = ""
        
        # Initialize UI
        self.init_ui()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(5000)  # 5 seconds
    
    def _load_sms_data(self):
        """Load SMS data from file"""
        default_data = {
            "messages": [],
            "stats": {
                "total": 0,
                "today": 0,
                "by_source": {},
                "by_status": {}
            },
            "last_updated": None
        }
        
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                # Ensure structure
                if "messages" not in data:
                    data["messages"] = []
                if "stats" not in data:
                    data["stats"] = default_data["stats"]
                
                return data
        except Exception as e:
            print(f"⚠️  SMS data load error: {e}")
        
        return default_data
    
    def _save_sms_data(self):
        """Save SMS data to file"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(self.sms_data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ SMS data save error: {e}")
            return False
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("TurboX SMS Panel")
        self.setGeometry(150, 150, 1000, 600)
        self.setStyleSheet(self._get_stylesheet())
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Top toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        # Refresh button
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.triggered.connect(self.refresh_data)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # Filter buttons
        filter_group = QButtonGroup(self)
        
        all_filter = QPushButton("All")
        all_filter.setCheckable(True)
        all_filter.setChecked(True)
        all_filter.clicked.connect(lambda: self.set_filter("all"))
        toolbar.addWidget(all_filter)
        filter_group.addButton(all_filter)
        
        unread_filter = QPushButton("Unread")
        unread_filter.setCheckable(True)
        unread_filter.clicked.connect(lambda: self.set_filter("unread"))
        toolbar.addWidget(unread_filter)
        filter_group.addButton(unread_filter)
        
        today_filter = QPushButton("Today")
        today_filter.setCheckable(True)
        today_filter.clicked.connect(lambda: self.set_filter("today"))
        toolbar.addWidget(today_filter)
        filter_group.addButton(today_filter)
        
        toolbar.addSeparator()
        
        # Search box
        toolbar.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search messages...")
        self.search_box.setMaximumWidth(200)
        self.search_box.textChanged.connect(self.on_search)
        toolbar.addWidget(self.search_box)
        
        toolbar.addSeparator()
        
        # Export button
        export_action = QAction("💾 Export", self)
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)
        
        # Clear button
        clear_action = QAction("🗑️ Clear", self)
        clear_action.triggered.connect(self.clear_data)
        toolbar.addAction(clear_action)
        
        main_layout.addWidget(toolbar)
        
        # Stats bar
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        
        self.total_label = QLabel("Total: 0")
        stats_layout.addWidget(self.total_label)
        
        self.today_label = QLabel("Today: 0")
        stats_layout.addWidget(self.today_label)
        
        self.source_label = QLabel("Sources: 0")
        stats_layout.addWidget(self.source_label)
        
        self.last_update_label = QLabel("Last update: Never")
        stats_layout.addWidget(self.last_update_label)
        
        stats_layout.addStretch()
        
        # Auto-refresh toggle
        self.auto_refresh_check = QCheckBox("Auto-refresh")
        self.auto_refresh_check.setChecked(True)
        self.auto_refresh_check.toggled.connect(self.toggle_auto_refresh)
        stats_layout.addWidget(self.auto_refresh_check)
        
        main_layout.addWidget(stats_widget)
        
        # Messages table
        self.messages_table = QTableWidget(0, 6)
        self.messages_table.setHorizontalHeaderLabels([
            "Time", "From", "To", "Message", "Status", "Source"
        ])
        self.messages_table.horizontalHeader().setStretchLastSection(True)
        self.messages_table.setAlternatingRowColors(True)
        self.messages_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.messages_table.doubleClicked.connect(self.view_message_details)
        
        main_layout.addWidget(self.messages_table, 1)
        
        # Bottom panel for message details
        bottom_panel = QWidget()
        bottom_layout = QVBoxLayout(bottom_panel)
        
        details_label = QLabel("Message Details:")
        details_label.setStyleSheet("font-weight: bold;")
        bottom_layout.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(100)
        bottom_layout.addWidget(self.details_text)
        
        main_layout.addWidget(bottom_panel)
        
        # Initial data load
        self.refresh_data()
    
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
        QToolBar {
            background-color: #3e3e3e;
            border: none;
            padding: 5px;
        }
        QPushButton {
            background-color: #4e4e4e;
            color: white;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 5px 10px;
        }
        QPushButton:hover {
            background-color: #5e5e5e;
        }
        QPushButton:checked {
            background-color: #0078d7;
        }
        QLineEdit {
            background-color: #3e3e3e;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 5px;
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
            padding: 5px;
        }
        QCheckBox {
            spacing: 5px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        """
    
    def refresh_data(self):
        """Refresh SMS data from storage"""
        # Load from browser extension storage (Phase 3 will use socket)
        # For now, use file-based storage
        
        old_data = self.sms_data.copy()
        self.sms_data = self._load_sms_data()
        
        # Update stats
        self.update_stats()
        
        # Update table if data changed
        if old_data != self.sms_data:
            self.update_table()
    
    def update_stats(self):
        """Update statistics display"""
        messages = self.sms_data.get("messages", [])
        stats = self.sms_data.get("stats", {})
        
        # Count today's messages
        today = datetime.now().date().isoformat()
        today_count = 0
        for msg in messages:
            msg_date = msg.get("timestamp", "").split("T")[0]
            if msg_date == today:
                today_count += 1
        
        # Count by source
        sources = set()
        for msg in messages:
            sources.add(msg.get("source", "Unknown"))
        
        self.total_label.setText(f"Total: {len(messages)}")
        self.today_label.setText(f"Today: {today_count}")
        self.source_label.setText(f"Sources: {len(sources)}")
        
        last_update = self.sms_data.get("last_updated")
        if last_update:
            self.last_update_label.setText(f"Last update: {last_update[:19]}")
        else:
            self.last_update_label.setText("Last update: Never")
    
    def update_table(self):
        """Update messages table with filtered data"""
        messages = self.sms_data.get("messages", [])
        
        # Apply filters
        filtered_messages = []
        for msg in messages:
            # Apply status filter
            if self.current_filter == "unread":
                if msg.get("status", "read") != "unread":
                    continue
            elif self.current_filter == "today":
                msg_date = msg.get("timestamp", "").split("T")[0]
                today = datetime.now().date().isoformat()
                if msg_date != today:
                    continue
            
            # Apply search filter
            if self.search_text:
                search_lower = self.search_text.lower()
                msg_text = msg.get("body", "").lower()
                msg_from = msg.get("from", "").lower()
                msg_to = msg.get("to", "").lower()
                
                if (search_lower not in msg_text and 
                    search_lower not in msg_from and 
                    search_lower not in msg_to):
                    continue
            
            filtered_messages.append(msg)
        
        # Sort by timestamp (newest first)
        filtered_messages.sort(
            key=lambda x: x.get("timestamp", ""), 
            reverse=True
        )
        
        # Update table
        self.messages_table.setRowCount(len(filtered_messages))
        
        for row, msg in enumerate(filtered_messages):
            # Time
            timestamp = msg.get("timestamp", "")
            if timestamp:
                time_str = timestamp[11:19] if len(timestamp) > 19 else timestamp
                date_str = timestamp[5:10] if len(timestamp) > 10 else timestamp[:10]
                display_time = f"{date_str} {time_str}"
            else:
                display_time = "Unknown"
            
            self.messages_table.setItem(row, 0, QTableWidgetItem(display_time))
            
            # From
            from_val = msg.get("from", "Unknown")
            from_item = QTableWidgetItem(str(from_val))
            if len(str(from_val)) > 20:
                from_item.setToolTip(str(from_val))
            self.messages_table.setItem(row, 1, from_item)
            
            # To
            to_val = msg.get("to", "Unknown")
            to_item = QTableWidgetItem(str(to_val))
            if len(str(to_val)) > 20:
                to_item.setToolTip(str(to_val))
            self.messages_table.setItem(row, 2, to_item)
            
            # Message (truncated)
            body = msg.get("body", "")
            display_body = str(body)[:50] + ("..." if len(str(body)) > 50 else "")
            body_item = QTableWidgetItem(display_body)
            body_item.setToolTip(str(body))
            self.messages_table.setItem(row, 3, body_item)
            
            # Status
            status = msg.get("status", "unknown")
            status_item = QTableWidgetItem(status)
            
            # Color code status
            if status == "unread":
                status_item.setForeground(QColor("#ff6b6b"))
            elif status == "sent":
                status_item.setForeground(QColor("#4ecdc4"))
            elif status == "delivered":
                status_item.setForeground(QColor("#1dd1a1"))
            elif status == "failed":
                status_item.setForeground(QColor("#ff9f43"))
            
            self.messages_table.setItem(row, 4, status_item)
            
            # Source
            source = msg.get("source", "Unknown")
            self.messages_table.setItem(row, 5, QTableWidgetItem(source))
        
        # Resize columns
        self.messages_table.resizeColumnsToContents()
    
    def set_filter(self, filter_type):
        """Set the current filter"""
        self.current_filter = filter_type
        self.update_table()
    
    def on_search(self, text):
        """Handle search text change"""
        self.search_text = text.lower()
        self.update_table()
    
    def view_message_details(self, index):
        """View details of selected message"""
        row = index.row()
        
        if 0 <= row < self.messages_table.rowCount():
            # Get message from filtered list
            messages = self.sms_data.get("messages", [])
            filtered_indices = []
            
            for msg in messages:
                # Apply same filters as table
                if self.current_filter == "unread":
                    if msg.get("status", "read") != "unread":
                        continue
                elif self.current_filter == "today":
                    msg_date = msg.get("timestamp", "").split("T")[0]
                    today = datetime.now().date().isoformat()
                    if msg_date != today:
                        continue
                
                if self.search_text:
                    search_lower = self.search_text.lower()
                    msg_text = msg.get("body", "").lower()
                    msg_from = msg.get("from", "").lower()
                    msg_to = msg.get("to", "").lower()
                    
                    if (search_lower not in msg_text and 
                        search_lower not in msg_from and 
                        search_lower not in msg_to):
                        continue
                
                filtered_indices.append(msg)
            
            if row < len(filtered_indices):
                msg = filtered_indices[row]
                
                # Format details
                details = f"""
                Time: {msg.get('timestamp', 'Unknown')}
                From: {msg.get('from', 'Unknown')}
                To: {msg.get('to', 'Unknown')}
                Status: {msg.get('status', 'unknown')}
                Source: {msg.get('source', 'Unknown')}
                Message ID: {msg.get('id', 'N/A')}
                
                Message:
                {msg.get('body', 'No content')}
                """
                
                self.details_text.setText(details.strip())
    
    def export_data(self):
        """Export SMS data to file"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export SMS Data", "", 
            "JSON Files (*.json);;CSV Files (*.csv);;Text Files (*.txt)",
            options=options
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'w') as f:
                        json.dump(self.sms_data, f, indent=2)
                
                elif file_path.endswith('.csv'):
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Timestamp', 'From', 'To', 'Message', 'Status', 'Source', 'ID'])
                        
                        for msg in self.sms_data.get("messages", []):
                            writer.writerow([
                                msg.get('timestamp', ''),
                                msg.get('from', ''),
                                msg.get('to', ''),
                                msg.get('body', ''),
                                msg.get('status', ''),
                                msg.get('source', ''),
                                msg.get('id', '')
                            ])
                
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        for msg in self.sms_data.get("messages", []):
                            f.write(f"Time: {msg.get('timestamp', '')}\n")
                            f.write(f"From: {msg.get('from', '')}\n")
                            f.write(f"To: {msg.get('to', '')}\n")
                            f.write(f"Message: {msg.get('body', '')}\n")
                            f.write(f"Status: {msg.get('status', '')}\n")
                            f.write(f"Source: {msg.get('source', '')}\n")
                            f.write("-" * 40 + "\n")
                
                QMessageBox.information(self, "Export Successful", 
                                      f"SMS data exported to:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))
    
    def clear_data(self):
        """Clear all SMS data"""
        reply = QMessageBox.question(
            self, 'Confirm Clear',
            "Are you sure you want to clear all SMS data?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.sms_data = {
                "messages": [],
                "stats": {
                    "total": 0,
                    "today": 0,
                    "by_source": {},
                    "by_status": {}
                },
                "last_updated": datetime.now().isoformat()
            }
            
            self._save_sms_data()
            self.refresh_data()
            
            QMessageBox.information(self, "Data Cleared", "All SMS data has been cleared.")
    
    def toggle_auto_refresh(self, enabled):
        """Toggle auto-refresh timer"""
        if enabled:
            self.refresh_timer.start(5000)
            self.statusBar().showMessage("Auto-refresh enabled")
        else:
            self.refresh_timer.stop()
            self.statusBar().showMessage("Auto-refresh disabled")
    
    def add_test_data(self):
        """Add test data for demonstration"""
        test_messages = [
            {
                "id": "msg_001",
                "from": "+1234567890",
                "to": "+0987654321",
                "body": "Hello, this is a test SMS message for TurboX Desktop.",
                "timestamp": datetime.now().isoformat(),
                "status": "delivered",
                "source": "Test API"
            },
            {
                "id": "msg_002",
                "from": "+1234567890",
                "to": "+5555555555",
                "body": "Meeting scheduled for tomorrow at 2 PM.",
                "timestamp": datetime.now().isoformat(),
                "status": "unread",
                "source": "Twilio API"
            },
            {
                "id": "msg_003",
                "from": "SYSTEM",
                "to": "ALL",
                "body": "System maintenance scheduled for midnight.",
                "timestamp": datetime.now().isoformat(),
                "status": "sent",
                "source": "Nexmo API"
            }
        ]
        
        self.sms_data["messages"].extend(test_messages)
        self.sms_data["last_updated"] = datetime.now().isoformat()
        self._save_sms_data()
        self.refresh_data()
    
    def closeEvent(self, event):
        """Handle window close"""
        self.refresh_timer.stop()
        event.accept()

def main():
    """Entry point"""
    # Check for X11
    if "DISPLAY" not in os.environ:
        print("⚠️  Please start TurboX Desktop first")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    panel = SMSPanel()
    panel.show()
    
    # Add test data on first run (optional)
    if not panel.sms_data.get("messages"):
        reply = QMessageBox.question(
            panel, "Demo Data",
            "Add demo SMS data for testing?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            panel.add_test_data()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
