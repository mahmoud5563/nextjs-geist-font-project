from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QStackedWidget, QLabel, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.client_management import ClientManagementWidget
from ui.attendance import AttendanceWidget
from ui.barcode_management import BarcodeManagementWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة الجيم - Gym Management System")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Initialize database
        from database import init_db
        init_db()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.create_sidebar(main_layout)
        
        # Create content area
        self.create_content_area(main_layout)
        
        # Set default page
        self.show_clients_page()
    
    def create_sidebar(self, main_layout):
        """Create navigation sidebar"""
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # App title
        title_label = QLabel("إدارة الجيم")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background-color: #1a252f;
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                padding: 20px;
                border-bottom: 2px solid #34495e;
            }
        """)
        sidebar_layout.addWidget(title_label)
        
        # Navigation buttons
        self.nav_buttons = []
        
        # Clients button
        clients_btn = QPushButton("إدارة العملاء")
        clients_btn.setObjectName("nav_button")
        clients_btn.setCheckable(True)
        clients_btn.clicked.connect(self.show_clients_page)
        self.nav_buttons.append(clients_btn)
        sidebar_layout.addWidget(clients_btn)
        
        # Attendance button
        attendance_btn = QPushButton("متابعة الحضور")
        attendance_btn.setObjectName("nav_button")
        attendance_btn.setCheckable(True)
        attendance_btn.clicked.connect(self.show_attendance_page)
        self.nav_buttons.append(attendance_btn)
        sidebar_layout.addWidget(attendance_btn)
        
        # Barcode button
        barcode_btn = QPushButton("إدارة الباركود")
        barcode_btn.setObjectName("nav_button")
        barcode_btn.setCheckable(True)
        barcode_btn.clicked.connect(self.show_barcode_page)
        self.nav_buttons.append(barcode_btn)
        sidebar_layout.addWidget(barcode_btn)
        
        # Add stretch to push buttons to top
        sidebar_layout.addStretch()
        
        # Add info section
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #1a252f;
                border-top: 1px solid #34495e;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        version_label = QLabel("الإصدار 1.0")
        version_label.setStyleSheet("color: #bdc3c7; font-size: 12px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(version_label)
        
        sidebar_layout.addWidget(info_frame)
        
        main_layout.addWidget(sidebar)
    
    def create_content_area(self, main_layout):
        """Create main content area"""
        content_widget = QWidget()
        content_widget.setObjectName("content_area")
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create stacked widget for pages
        self.stacked_widget = QStackedWidget()
        
        # Create pages
        self.clients_page = ClientManagementWidget()
        self.attendance_page = AttendanceWidget()
        self.barcode_page = BarcodeManagementWidget()
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.clients_page)
        self.stacked_widget.addWidget(self.attendance_page)
        self.stacked_widget.addWidget(self.barcode_page)
        
        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(content_widget)
    
    def show_clients_page(self):
        """Show clients management page"""
        self.stacked_widget.setCurrentWidget(self.clients_page)
        self.update_nav_buttons(0)
        self.clients_page.refresh_data()
    
    def show_attendance_page(self):
        """Show attendance tracking page"""
        self.stacked_widget.setCurrentWidget(self.attendance_page)
        self.update_nav_buttons(1)
        self.attendance_page.refresh_data()
    
    def show_barcode_page(self):
        """Show barcode management page"""
        self.stacked_widget.setCurrentWidget(self.barcode_page)
        self.update_nav_buttons(2)
        self.barcode_page.refresh_data()
    
    def update_nav_buttons(self, active_index):
        """Update navigation button states"""
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == active_index)
