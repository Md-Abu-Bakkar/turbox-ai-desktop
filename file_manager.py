#!/usr/bin/env python3
# ==============================================================================
# TurboX Desktop OS - File Manager with Phone Storage Integration
# Files synced with native Android file manager
# ==============================================================================

import os
import sys
import shutil
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class TurboXFileManager(QMainWindow):
    """Windows-style file manager with phone storage integration"""
    
    def __init__(self):
        super().__init__()
        self.home_dir = os.path.expanduser("~")
        self.phone_storage = "/storage/emulated/0"
        
        # Check if phone storage is accessible
        self.phone_accessible = os.path.exists(self.phone_storage)
        
        # Current directory
        self.current_dir = self.home_dir
        
        # Initialize UI
        self.init_ui()
        
        # Load current directory
        self.load_directory(self.current_dir)
        
        print("✅ File Manager initialized")
        if self.phone_accessible:
            print(f"📱 Phone storage mounted: {self.phone_storage}")
    
    def init_ui(self):
        """Initialize Windows-style file manager UI"""
        self.setWindowTitle("TurboX File Manager")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet(self.get_stylesheet())
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Navigation buttons
        back_btn = QAction("← Back", self)
        back_btn.triggered.connect(self.go_back)
        toolbar.addAction(back_btn)
        
        forward_btn = QAction("→ Forward", self)
        forward_btn.triggered.connect(self.go_forward)
        toolbar.addAction(forward_btn)
        
        up_btn = QAction("↑ Up", self)
        up_btn.triggered.connect(self.go_up)
        toolbar.addAction(up_btn)
        
        toolbar.addSeparator()
        
        # Home button
        home_btn = QAction("🏠 Home", self)
        home_btn.triggered.connect(self.go_home)
        toolbar.addAction(home_btn)
        
        # Phone storage button
        if self.phone_accessible:
            phone_btn = QAction("📱 Phone", self)
            phone_btn.triggered.connect(self.go_phone_storage)
            toolbar.addAction(phone_btn)
        
        # Desktop button
        desktop_btn = QAction("🖥️ Desktop", self)
        desktop_btn.triggered.connect(self.go_desktop)
        toolbar.addAction(desktop_btn)
        
        toolbar.addSeparator()
        
        # View buttons
        list_view_btn = QAction("📋 List", self)
        list_view_btn.triggered.connect(self.set_list_view)
        toolbar.addAction(list_view_btn)
        
        icon_view_btn = QAction("🖼️ Icons", self)
        icon_view_btn.triggered.connect(self.set_icon_view)
        toolbar.addAction(icon_view_btn)
        
        toolbar.addSeparator()
        
        # Refresh button
        refresh_btn = QAction("🔄 Refresh", self)
        refresh_btn.triggered.connect(self.refresh)
        toolbar.addAction(refresh_btn)
        
        # Address bar
        address_layout = QHBoxLayout()
        address_layout.addWidget(QLabel("Address:"))
        
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.navigate_to_address)
        address_layout.addWidget(self.address_bar, 1)
        
        main_layout.addLayout(address_layout)
        
        # Splitter for two-pane view
        splitter = QSplitter(Qt.Horizontal)
        
        # Left pane: Quick access
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        
        quick_access_label = QLabel("Quick Access")
        quick_access_label.setStyleSheet("font-weight: bold; padding: 5px;")
        left_layout.addWidget(quick_access_label)
        
        # Quick access items
        quick_items = [
            ("🏠 Home", self.home_dir),
            ("🖥️ Desktop", os.path.join(self.home_dir, "Desktop")),
            ("📂 Documents", os.path.join(self.home_dir, "Documents")),
            ("⬇️ Downloads", os.path.join(self.home_dir, "Downloads")),
            ("🖼️ Pictures", os.path.join(self.home_dir, "Pictures")),
            ("🎵 Music", os.path.join(self.home_dir, "Music")),
            ("🎬 Videos", os.path.join(self.home_dir, "Videos"))
        ]
        
        if self.phone_accessible:
            quick_items.append(("📱 Phone Storage", self.phone_storage))
        
        for name, path in quick_items:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
            btn.clicked.connect(lambda checked, p=path: self.load_directory(p))
            left_layout.addWidget(btn)
        
        left_layout.addStretch()
        splitter.addWidget(left_pane)
        
        # Right pane: File browser
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setViewMode(QListWidget.IconMode)
        self.file_list.setIconSize(QSize(64, 64))
        self.file_list.setResizeMode(QListWidget.Adjust)
        self.file_list.setMovement(QListWidget.Static)
        self.file_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        
        right_layout.addWidget(self.file_list)
        
        # Status bar
        status_bar = QStatusBar()
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)
        right_layout.addWidget(status_bar)
        
        splitter.addWidget(right_pane)
        splitter.setSizes([200, 800])
        
        main_layout.addWidget(splitter, 1)
        
        # Navigation history
        self.history = [self.home_dir]
        self.history_index = 0
        
        # Update address bar
        self.update_address_bar()
    
    def get_stylesheet(self):
        """Get file manager stylesheet"""
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
            background-color: #3d3d3d;
            border: none;
            padding: 5px;
        }
        QToolButton {
            color: white;
            padding: 5px 10px;
            border-radius: 3px;
        }
        QToolButton:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        QLineEdit {
            background-color: #3e3e3e;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 5px;
        }
        QListWidget {
            background-color: #3e3e3e;
            border: 1px solid #555;
            border-radius: 3px;
        }
        QListWidget::item {
            padding: 5px;
            border-radius: 3px;
        }
        QListWidget::item:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        QListWidget::item:selected {
            background-color: #0078d7;
        }
        QStatusBar {
            background-color: #3d3d3d;
            color: white;
        }
        """
    
    def load_directory(self, directory):
        """Load directory contents"""
        try:
            if not os.path.exists(directory):
                QMessageBox.warning(self, "Error", f"Directory not found:\n{directory}")
                return
            
            self.current_dir = directory
            
            # Update history
            if self.history_index == len(self.history) - 1:
                self.history.append(directory)
                self.history_index += 1
            else:
                self.history = self.history[:self.history_index + 1]
                self.history.append(directory)
                self.history_index = len(self.history) - 1
            
            # Clear file list
            self.file_list.clear()
            
            # Add ".." for parent directory
            if directory != "/":
                parent_item = QListWidgetItem()
                parent_item.setText("..")
                parent_item.setIcon(self.get_icon("folder-up"))
                parent_item.setData(Qt.UserRole, os.path.dirname(directory))
                self.file_list.addItem(parent_item)
            
            # List directory contents
            items = []
            
            # Add directories first
            for item in sorted(os.listdir(directory)):
                item_path = os.path.join(directory, item)
                
                if os.path.isdir(item_path):
                    list_item = QListWidgetItem()
                    list_item.setText(item)
                    list_item.setIcon(self.get_icon("folder"))
                    list_item.setData(Qt.UserRole, item_path)
                    items.append(list_item)
            
            # Add files
            for item in sorted(os.listdir(directory)):
                item_path = os.path.join(directory, item)
                
                if os.path.isfile(item_path):
                    list_item = QListWidgetItem()
                    list_item.setText(item)
                    
                    # Get file icon based on extension
                    icon = self.get_file_icon(item_path)
                    list_item.setIcon(icon)
                    
                    list_item.setData(Qt.UserRole, item_path)
                    items.append(list_item)
            
            # Add to list widget
            for item in items:
                self.file_list.addItem(item)
            
            # Update UI
            self.update_address_bar()
            self.update_status(f"{len(items)} items")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot access directory:\n{str(e)}")
    
    def get_icon(self, icon_name):
        """Get icon by name"""
        icon = QIcon()
        
        if icon_name == "folder":
            icon = QIcon.fromTheme("folder")
        elif icon_name == "folder-up":
            icon = QIcon.fromTheme("go-up")
        elif icon_name == "file":
            icon = QIcon.fromTheme("text-x-generic")
        
        if icon.isNull():
            # Create simple icon
            pixmap = QPixmap(32, 32)
            if icon_name == "folder":
                pixmap.fill(QColor(66, 133, 244))
            else:
                pixmap.fill(QColor(52, 168, 83))
            icon = QIcon(pixmap)
        
        return icon
    
    def get_file_icon(self, file_path):
        """Get icon for file based on extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        icon_map = {
            '.txt': 'text-x-generic',
            '.pdf': 'application-pdf',
            '.jpg': 'image-jpeg',
            '.jpeg': 'image-jpeg',
            '.png': 'image-png',
            '.mp3': 'audio-x-generic',
            '.mp4': 'video-x-generic',
            '.zip': 'application-zip',
            '.py': 'text-x-python',
            '.js': 'text-x-javascript',
            '.html': 'text-html',
            '.css': 'text-css',
            '.json': 'application-json'
        }
        
        icon_name = icon_map.get(ext, 'text-x-generic')
        icon = QIcon.fromTheme(icon_name)
        
        if icon.isNull():
            # Create colored icon based on file type
            pixmap = QPixmap(32, 32)
            
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                pixmap.fill(QColor(219, 68, 55))  # Red for images
            elif ext in ['.mp3', '.wav', '.flac']:
                pixmap.fill(QColor(244, 180, 0))  # Yellow for audio
            elif ext in ['.mp4', '.avi', '.mkv']:
                pixmap.fill(QColor(15, 157, 88))  # Green for video
            elif ext in ['.zip', '.rar', '.7z']:
                pixmap.fill(QColor(121, 85, 72))  # Brown for archives
            else:
                pixmap.fill(QColor(66, 133, 244))  # Blue for documents
            
            icon = QIcon(pixmap)
        
        return icon
    
    def on_item_double_clicked(self, item):
        """Handle double click on file/folder"""
        item_path = item.data(Qt.UserRole)
        
        if os.path.isdir(item_path):
            self.load_directory(item_path)
        else:
            self.open_file(item_path)
    
    def open_file(self, file_path):
        """Open file with default application"""
        try:
            # Get MIME type and open
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            
            if mime_type:
                if mime_type.startswith('text/'):
                    # Open text files with mousepad
                    subprocess.Popen(['mousepad', file_path])
                elif mime_type.startswith('image/'):
                    # Open images with default viewer
                    subprocess.Popen(['xdg-open', file_path])
                elif mime_type == 'application/pdf':
                    # Open PDFs
                    subprocess.Popen(['xdg-open', file_path])
                else:
                    # Try to open with default application
                    subprocess.Popen(['xdg-open', file_path])
            else:
                # Try to open anyway
                subprocess.Popen(['xdg-open', file_path])
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot open file:\n{str(e)}")
    
    def show_context_menu(self, position):
        """Show right-click context menu"""
        item = self.file_list.itemAt(position)
        
        menu = QMenu()
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
            QMenu::separator {
                height: 1px;
                background-color: #555;
                margin: 5px 0;
            }
        """)
        
        if item:
            item_path = item.data(Qt.UserRole)
            
            # Item-specific actions
            if os.path.isdir(item_path):
                menu.addAction("📂 Open", lambda: self.load_directory(item_path))
                menu.addAction("📂 Open in Terminal", 
                             lambda: self.open_in_terminal(item_path))
            else:
                menu.addAction("📄 Open", lambda: self.open_file(item_path))
                menu.addAction("📄 Open With...", 
                             lambda: self.open_with_dialog(item_path))
            
            menu.addSeparator()
            
            # Common actions
            menu.addAction("📋 Copy", lambda: self.copy_item(item_path))
            menu.addAction("✂️ Cut", lambda: self.cut_item(item_path))
            menu.addAction("📝 Rename", lambda: self.rename_item(item))
            menu.addAction("🗑️ Delete", lambda: self.delete_item(item_path))
            
            menu.addSeparator()
            
            # Properties
            menu.addAction("⚙️ Properties", 
                         lambda: self.show_properties(item_path))
        
        else:
            # Empty space actions
            menu.addAction("📁 New Folder", self.create_new_folder)
            menu.addAction("📄 New File", self.create_new_file)
            menu.addAction("📋 Paste", self.paste_items)
            menu.addAction("🔄 Refresh", self.refresh)
        
        menu.exec_(self.file_list.mapToGlobal(position))
    
    def create_new_folder(self):
        """Create new folder in current directory"""
        folder_name, ok = QInputDialog.getText(self, "New Folder", 
                                             "Enter folder name:")
        if ok and folder_name:
            folder_path = os.path.join(self.current_dir, folder_name)
            
            try:
                os.makedirs(folder_path, exist_ok=True)
                self.refresh()
                self.status_label.setText(f"Created folder: {folder_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Cannot create folder:\n{str(e)}")
    
    def create_new_file(self):
        """Create new file in current directory"""
        file_name, ok = QInputDialog.getText(self, "New File", 
                                           "Enter file name:")
        if ok and file_name:
            file_path = os.path.join(self.current_dir, file_name)
            
            try:
                with open(file_path, 'w') as f:
                    f.write("")
                self.refresh()
                self.status_label.setText(f"Created file: {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Cannot create file:\n{str(e)}")
    
    def copy_item(self, item_path):
        """Copy item to clipboard"""
        self.clipboard_action = 'copy'
        self.clipboard_item = item_path
        self.status_label.setText(f"Copied: {os.path.basename(item_path)}")
    
    def cut_item(self, item_path):
        """Cut item to clipboard"""
        self.clipboard_action = 'cut'
        self.clipboard_item = item_path
        self.status_label.setText(f"Cut: {os.path.basename(item_path)}")
    
    def paste_items(self):
        """Paste items from clipboard"""
        if hasattr(self, 'clipboard_item') and self.clipboard_item:
            try:
                dest_path = os.path.join(self.current_dir, 
                                       os.path.basename(self.clipboard_item))
                
                if self.clipboard_action == 'copy':
                    if os.path.isdir(self.clipboard_item):
                        shutil.copytree(self.clipboard_item, dest_path)
                    else:
                        shutil.copy2(self.clipboard_item, dest_path)
                    
                    self.status_label.setText(f"Copied to current directory")
                
                elif self.clipboard_action == 'cut':
                    shutil.move(self.clipboard_item, dest_path)
                    self.status_label.setText(f"Moved to current directory")
                
                self.refresh()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Cannot paste item:\n{str(e)}")
    
    def rename_item(self, item):
        """Rename selected item"""
        old_path = item.data(Qt.UserRole)
        old_name = os.path.basename(old_path)
        
        new_name, ok = QInputDialog.getText(self, "Rename", 
                                          "Enter new name:", 
                                          text=old_name)
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            
            try:
                os.rename(old_path, new_path)
                item.setData(Qt.UserRole, new_path)
                item.setText(new_name)
                self.status_label.setText(f"Renamed to: {new_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Cannot rename:\n{str(e)}")
    
    def delete_item(self, item_path):
        """Delete selected item"""
        reply = QMessageBox.question(self, "Delete", 
                                   f"Delete '{os.path.basename(item_path)}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                
                self.refresh()
                self.status_label.setText(f"Deleted: {os.path.basename(item_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Cannot delete:\n{str(e)}")
    
    def show_properties(self, item_path):
        """Show file/folder properties"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Properties")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Item info
        name = os.path.basename(item_path)
        is_dir = os.path.isdir(item_path)
        
        info_text = f"""
        <b>Name:</b> {name}<br>
        <b>Type:</b> {"Folder" if is_dir else "File"}<br>
        <b>Location:</b> {os.path.dirname(item_path)}<br>
        <b>Size:</b> {self.get_size(item_path)}<br>
        <b>Modified:</b> {datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M:%S')}<br>
        <b>Permissions:</b> {oct(os.stat(item_path).st_mode)[-3:]}<br>
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def get_size(self, path):
        """Get human-readable size of file/folder"""
        if os.path.isfile(path):
            size = os.path.getsize(path)
        elif os.path.isdir(path):
            size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        size += os.path.getsize(fp)
        else:
            return "0 B"
        
        # Convert to human readable
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        
        return f"{size:.1f} TB"
    
    def open_in_terminal(self, directory):
        """Open directory in terminal"""
        try:
            subprocess.Popen(['xfce4-terminal', '--working-directory', directory])
        except:
            QMessageBox.warning(self, "Error", "Cannot open terminal")
    
    def open_with_dialog(self, file_path):
        """Open 'Open With' dialog"""
        # Simple implementation - just open with default
        self.open_file(file_path)
    
    def go_back(self):
        """Go back in history"""
        if self.history_index > 0:
            self.history_index -= 1
            self.load_directory(self.history[self.history_index])
    
    def go_forward(self):
        """Go forward in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.load_directory(self.history[self.history_index])
    
    def go_up(self):
        """Go to parent directory"""
        parent = os.path.dirname(self.current_dir)
        if parent != self.current_dir:
            self.load_directory(parent)
    
    def go_home(self):
        """Go to home directory"""
        self.load_directory(self.home_dir)
    
    def go_phone_storage(self):
        """Go to phone storage"""
        if self.phone_accessible:
            self.load_directory(self.phone_storage)
        else:
            QMessageBox.warning(self, "Error", "Phone storage not accessible")
    
    def go_desktop(self):
        """Go to desktop directory"""
        desktop_path = os.path.join(self.home_dir, "Desktop")
        self.load_directory(desktop_path)
    
    def set_list_view(self):
        """Set list view mode"""
        self.file_list.setViewMode(QListWidget.ListMode)
        self.file_list.setIconSize(QSize(32, 32))
    
    def set_icon_view(self):
        """Set icon view mode"""
        self.file_list.setViewMode(QListWidget.IconMode)
        self.file_list.setIconSize(QSize(64, 64))
    
    def refresh(self):
        """Refresh current directory"""
        self.load_directory(self.current_dir)
    
    def navigate_to_address(self):
        """Navigate to address in address bar"""
        address = self.address_bar.text()
        
        if os.path.exists(address):
            self.load_directory(address)
        else:
            QMessageBox.warning(self, "Error", "Path does not exist")
    
    def update_address_bar(self):
        """Update address bar with current directory"""
        self.address_bar.setText(self.current_dir)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.setText(message)

def main():
    """Start file manager"""
    app = QApplication(sys.argv)
    fm = TurboXFileManager()
    fm.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
