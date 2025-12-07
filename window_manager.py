#!/usr/bin/env python3
# ==============================================================================
# TurboX Desktop OS - Multi-Window Manager
# Resizable, draggable, overlapping windows with full mouse control
# ==============================================================================

import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class WindowManager:
    """Manage multiple resizable, draggable windows"""
    
    def __init__(self):
        self.windows = []
        self.active_window = None
        self.z_order = []  # Window stacking order
        
        # Window management state
        self.window_state = {
            'resizing': False,
            'moving': False,
            'resize_edge': None,
            'move_start': None
        }
        
        print("✅ Window Manager initialized")
    
    def create_window(self, title, content_widget, parent=None, 
                     width=800, height=600, x=None, y=None):
        """Create a new resizable window"""
        window = ResizableWindow(title, content_widget, parent, width, height, x, y)
        self.windows.append(window)
        self.z_order.append(window)
        self.active_window = window
        
        # Connect signals
        window.activated.connect(lambda: self.bring_to_front(window))
        window.closed.connect(lambda: self.remove_window(window))
        
        return window
    
    def bring_to_front(self, window):
        """Bring window to front"""
        if window in self.z_order:
            self.z_order.remove(window)
            self.z_order.append(window)
            self.active_window = window
            
            # Update window stacking
            for i, win in enumerate(self.z_order):
                win.raise_() if i == len(self.z_order) - 1 else win.lower()
    
    def remove_window(self, window):
        """Remove window from management"""
        if window in self.windows:
            self.windows.remove(window)
        if window in self.z_order:
            self.z_order.remove(window)
        
        if self.windows:
            self.active_window = self.windows[-1]
        else:
            self.active_window = None
    
    def cascade_windows(self, start_x=30, start_y=30, offset=30):
        """Arrange windows in cascade pattern"""
        for i, window in enumerate(self.windows):
            window.move(start_x + (i * offset), start_y + (i * offset))
            window.resize(800, 600)
    
    def tile_windows(self, arrangement="horizontal"):
        """Tile windows horizontally or vertically"""
        if not self.windows:
            return
        
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        if arrangement == "horizontal":
            # Horizontal tiling
            window_width = screen_width // len(self.windows)
            for i, window in enumerate(self.windows):
                window.move(i * window_width, 0)
                window.resize(window_width, screen_height)
        
        elif arrangement == "vertical":
            # Vertical tiling
            window_height = screen_height // len(self.windows)
            for i, window in enumerate(self.windows):
                window.move(0, i * window_height)
                window.resize(screen_width, window_height)
    
    def minimize_all(self):
        """Minimize all windows"""
        for window in self.windows:
            window.showMinimized()
    
    def maximize_all(self):
        """Maximize all windows"""
        for window in self.windows:
            window.showMaximized()
    
    def restore_all(self):
        """Restore all windows"""
        for window in self.windows:
            window.showNormal()
    
    def close_all(self):
        """Close all windows"""
        for window in self.windows[:]:  # Copy list
            window.close()
    
    def get_window_info(self):
        """Get information about all windows"""
        info = []
        for window in self.windows:
            info.append({
                'title': window.windowTitle(),
                'geometry': window.geometry().getRect(),
                'is_active': window == self.active_window,
                'is_minimized': window.isMinimized(),
                'is_maximized': window.isMaximized()
            })
        return info

class ResizableWindow(QWidget):
    """Resizable, draggable window with Windows-style controls"""
    
    # Signals
    activated = pyqtSignal()
    closed = pyqtSignal()
    
    def __init__(self, title, content_widget, parent=None, 
                 width=800, height=600, x=None, y=None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        
        # Set position
        if x is not None and y is not None:
            self.move(x, y)
        else:
            # Center on screen
            screen = QApplication.primaryScreen().geometry()
            center_x = (screen.width() - width) // 2
            center_y = (screen.height() - height) // 2
            self.move(center_x, center_y)
        
        # Set size
        self.resize(width, height)
        
        # Window properties
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        # Window state
        self.is_resizing = False
        self.is_moving = False
        self.resize_edge = None
        self.move_start_pos = None
        self.drag_start_pos = None
        
        # Create window frame
        self.create_window_frame()
        
        # Add content
        self.content_area = QWidget(self.frame)
        self.content_area.setGeometry(0, 30, width, height - 30)
        
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(content_widget)
        
        # Install event filter for mouse events
        self.installEventFilter(self)
        self.frame.installEventFilter(self)
        
        # Show window
        self.show()
        
        print(f"📁 Created window: {title}")
    
    def create_window_frame(self):
        """Create window frame with title bar and controls"""
        self.frame = QWidget(self)
        self.frame.setGeometry(0, 0, self.width(), self.height())
        self.frame.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 5px;
            }
        """)
        
        # Title bar
        self.title_bar = QWidget(self.frame)
        self.title_bar.setGeometry(0, 0, self.width(), 30)
        self.title_bar.setStyleSheet("""
            QWidget {
                background-color: #3d3d3d;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                border-bottom: 1px solid #555;
            }
        """)
        
        # Title label
        self.title_label = QLabel(self.windowTitle(), self.title_bar)
        self.title_label.setGeometry(10, 5, self.width() - 100, 20)
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        
        # Window controls
        self.create_window_controls()
    
    def create_window_controls(self):
        """Create window control buttons"""
        controls = QWidget(self.title_bar)
        controls.setGeometry(self.width() - 90, 0, 90, 30)
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 5, 0)
        controls_layout.setSpacing(2)
        
        # Minimize button
        self.min_btn = QPushButton("─")
        self.min_btn.setFixedSize(20, 20)
        self.min_btn.clicked.connect(self.showMinimized)
        
        # Maximize/Restore button
        self.max_btn = QPushButton("□")
        self.max_btn.setFixedSize(20, 20)
        self.max_btn.clicked.connect(self.toggle_maximize)
        
        # Close button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.clicked.connect(self.close)
        
        # Style buttons
        button_style = """
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
            QPushButton#close_btn:hover {
                background-color: #e81123;
            }
            QPushButton#close_btn:pressed {
                background-color: #f1707a;
            }
        """
        
        self.min_btn.setStyleSheet(button_style)
        self.max_btn.setStyleSheet(button_style)
        self.close_btn.setStyleSheet(button_style)
        self.close_btn.setObjectName("close_btn")
        
        controls_layout.addWidget(self.min_btn)
        controls_layout.addWidget(self.max_btn)
        controls_layout.addWidget(self.close_btn)
    
    def toggle_maximize(self):
        """Toggle between maximize and restore"""
        if self.isMaximized():
            self.showNormal()
            self.max_btn.setText("□")
        else:
            self.showMaximized()
            self.max_btn.setText("❐")
    
    def eventFilter(self, obj, event):
        """Handle mouse events for window management"""
        if event.type() == QEvent.MouseButtonPress:
            return self.handle_mouse_press(event)
        elif event.type() == QEvent.MouseButtonRelease:
            return self.handle_mouse_release(event)
        elif event.type() == QEvent.MouseMove:
            return self.handle_mouse_move(event)
        elif event.type() == QEvent.Enter:
            self.activated.emit()
            return True
        elif event.type() == QEvent.Close:
            self.closed.emit()
            return True
        
        return super().eventFilter(obj, event)
    
    def handle_mouse_press(self, event):
        """Handle mouse button press"""
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            
            # Check if clicked on title bar
            if self.title_bar.geometry().contains(pos):
                self.is_moving = True
                self.move_start_pos = event.globalPos()
                self.drag_start_pos = self.pos()
                return True
            
            # Check if clicked on window edge for resizing
            edge = self.get_resize_edge(pos)
            if edge:
                self.is_resizing = True
                self.resize_edge = edge
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self.geometry()
                return True
        
        return False
    
    def handle_mouse_release(self, event):
        """Handle mouse button release"""
        if event.button() == Qt.LeftButton:
            self.is_moving = False
            self.is_resizing = False
            self.resize_edge = None
            return True
        
        return False
    
    def handle_mouse_move(self, event):
        """Handle mouse movement"""
        # Update cursor based on position
        if not self.is_resizing and not self.is_moving:
            edge = self.get_resize_edge(event.pos())
            self.update_cursor(edge)
        
        # Handle window moving
        if self.is_moving and event.buttons() & Qt.LeftButton:
            delta = event.globalPos() - self.move_start_pos
            new_pos = self.drag_start_pos + delta
            self.move(new_pos)
            return True
        
        # Handle window resizing
        if self.is_resizing and event.buttons() & Qt.LeftButton:
            delta = event.globalPos() - self.resize_start_pos
            new_geom = QRect(self.resize_start_geometry)
            
            if 'left' in self.resize_edge:
                new_geom.setLeft(new_geom.left() + delta.x())
            if 'right' in self.resize_edge:
                new_geom.setRight(new_geom.right() + delta.x())
            if 'top' in self.resize_edge:
                new_geom.setTop(new_geom.top() + delta.y())
            if 'bottom' in self.resize_edge:
                new_geom.setBottom(new_geom.bottom() + delta.y())
            
            # Ensure minimum size
            if new_geom.width() < 200:
                if 'left' in self.resize_edge:
                    new_geom.setLeft(new_geom.right() - 200)
                else:
                    new_geom.setRight(new_geom.left() + 200)
            
            if new_geom.height() < 150:
                if 'top' in self.resize_edge:
                    new_geom.setTop(new_geom.bottom() - 150)
                else:
                    new_geom.setBottom(new_geom.top() + 150)
            
            self.setGeometry(new_geom)
            self.update_window_layout()
            return True
        
        return False
    
    def get_resize_edge(self, pos):
        """Determine which edge the cursor is near"""
        margin = 5
        rect = self.rect()
        
        edges = []
        
        if pos.x() <= margin:
            edges.append('left')
        elif pos.x() >= rect.width() - margin:
            edges.append('right')
        
        if pos.y() <= margin:
            edges.append('top')
        elif pos.y() >= rect.height() - margin:
            edges.append('bottom')
        
        return edges if edges else None
    
    def update_cursor(self, edges):
        """Update cursor based on resize edges"""
        if not edges:
            self.setCursor(Qt.ArrowCursor)
        elif edges == ['left'] or edges == ['right']:
            self.setCursor(Qt.SizeHorCursor)
        elif edges == ['top'] or edges == ['bottom']:
            self.setCursor(Qt.SizeVerCursor)
        elif edges == ['left', 'top'] or edges == ['right', 'bottom']:
            self.setCursor(Qt.SizeFDiagCursor)
        elif edges == ['right', 'top'] or edges == ['left', 'bottom']:
            self.setCursor(Qt.SizeBDiagCursor)
    
    def update_window_layout(self):
        """Update window layout after resize"""
        width = self.width()
        height = self.height()
        
        # Update frame
        self.frame.setGeometry(0, 0, width, height)
        
        # Update title bar
        self.title_bar.setGeometry(0, 0, width, 30)
        self.title_label.setGeometry(10, 5, width - 100, 20)
        
        # Update controls position
        controls = self.title_bar.findChild(QWidget)
        if controls:
            controls.setGeometry(width - 90, 0, 90, 30)
        
        # Update content area
        self.content_area.setGeometry(0, 30, width, height - 30)
    
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        self.update_window_layout()
    
    def closeEvent(self, event):
        """Handle window close"""
        self.closed.emit()
        event.accept()

# Example usage and testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create window manager
    wm = WindowManager()
    
    # Create some test windows
    def create_test_window(title):
        content = QTextEdit()
        content.setPlainText(f"This is {title}\n\nResize me, drag me, maximize me!")
        
        window = wm.create_window(
            title=title,
            content_widget=content,
            width=600,
            height=400
        )
        return window
    
    # Create windows
    window1 = create_test_window("API Tester")
    window2 = create_test_window("SMS Panel")
    window3 = create_test_window("File Manager")
    
    # Arrange windows
    wm.cascade_windows()
    
    sys.exit(app.exec_())
