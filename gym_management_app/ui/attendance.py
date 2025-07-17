from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
                             QDateEdit, QMessageBox, QGroupBox, QFormLayout, QHeaderView,
                             QCalendarWidget, QTextEdit, QSplitter)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QFont
from database import ClientDB, AttendanceDB
from datetime import datetime, date

class AttendanceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_timer()
        self.refresh_data()
    
    def setup_ui(self):
        """Setup attendance tracking UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Page title
        title = QLabel("متابعة الحضور")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Create splitter for layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Check-in form and client info
        self.create_checkin_section(splitter)
        
        # Right side - Attendance table and calendar
        self.create_attendance_section(splitter)
        
        layout.addWidget(splitter)
    
    def create_checkin_section(self, parent):
        """Create check-in form section"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Quick check-in form
        checkin_group = QGroupBox("تسجيل الحضور")
        checkin_layout = QFormLayout(checkin_group)
        checkin_layout.setSpacing(15)
        
        # Client search/selection
        self.client_search = QLineEdit()
        self.client_search.setPlaceholderText("ابحث عن العميل بالاسم أو الهاتف...")
        self.client_search.textChanged.connect(self.search_clients)
        checkin_layout.addRow("البحث عن العميل:", self.client_search)
        
        # Client dropdown
        self.client_combo = QComboBox()
        self.client_combo.currentTextChanged.connect(self.on_client_selected)
        checkin_layout.addRow("اختر العميل:", self.client_combo)
        
        # Check-in button
        self.checkin_btn = QPushButton("تسجيل الحضور")
        self.checkin_btn.setObjectName("success_button")
        self.checkin_btn.clicked.connect(self.mark_attendance)
        self.checkin_btn.setEnabled(False)
        checkin_layout.addRow(self.checkin_btn)
        
        left_layout.addWidget(checkin_group)
        
        # Client info display
        self.create_client_info_section(left_layout)
        
        # Today's stats
        self.create_stats_section(left_layout)
        
        left_layout.addStretch()
        parent.addWidget(left_widget)
    
    def create_client_info_section(self, parent_layout):
        """Create client information display"""
        info_group = QGroupBox("معلومات العميل")
        info_layout = QVBoxLayout(info_group)
        
        self.client_info_text = QTextEdit()
        self.client_info_text.setReadOnly(True)
        self.client_info_text.setMaximumHeight(200)
        self.client_info_text.setPlainText("اختر عميل لعرض معلوماته...")
        
        info_layout.addWidget(self.client_info_text)
        parent_layout.addWidget(info_group)
    
    def create_stats_section(self, parent_layout):
        """Create today's statistics section"""
        stats_group = QGroupBox("إحصائيات اليوم")
        stats_layout = QVBoxLayout(stats_group)
        
        # Current time display
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 6px;
            }
        """)
        stats_layout.addWidget(self.time_label)
        
        # Today's attendance count
        self.attendance_count_label = QLabel("عدد الحاضرين اليوم: 0")
        self.attendance_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.attendance_count_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #27ae60;
                padding: 8px;
                background-color: #d5f4e6;
                border-radius: 4px;
                margin: 5px;
            }
        """)
        stats_layout.addWidget(self.attendance_count_label)
        
        parent_layout.addWidget(stats_group)
    
    def create_attendance_section(self, parent):
        """Create attendance table and calendar section"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Date filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("تاريخ المراجعة:"))
        
        self.date_filter = QDateEdit()
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setCalendarPopup(True)
        self.date_filter.dateChanged.connect(self.filter_by_date)
        filter_layout.addWidget(self.date_filter)
        
        filter_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("تحديث")
        refresh_btn.clicked.connect(self.refresh_data)
        filter_layout.addWidget(refresh_btn)
        
        right_layout.addLayout(filter_layout)
        
        # Attendance table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(6)
        self.attendance_table.setHorizontalHeaderLabels([
            "ID", "اسم العميل", "وقت الدخول", "وقت الخروج", "التاريخ", "الحالة"
        ])
        
        # Set table properties
        header = self.attendance_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.attendance_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.attendance_table.setAlternatingRowColors(True)
        
        right_layout.addWidget(self.attendance_table)
        
        # Calendar widget
        calendar_group = QGroupBox("التقويم")
        calendar_layout = QVBoxLayout(calendar_group)
        
        self.calendar = QCalendarWidget()
        self.calendar.setMaximumHeight(200)
        self.calendar.clicked.connect(self.on_calendar_date_selected)
        calendar_layout.addWidget(self.calendar)
        
        right_layout.addWidget(calendar_group)
        
        parent.addWidget(right_widget)
    
    def setup_timer(self):
        """Setup timer for real-time updates"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        self.update_time()
    
    def update_time(self):
        """Update current time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"الوقت الحالي: {current_time}")
    
    def search_clients(self):
        """Search and populate client dropdown"""
        search_text = self.client_search.text().strip().lower()
        
        if len(search_text) < 2:
            self.client_combo.clear()
            self.checkin_btn.setEnabled(False)
            return
        
        clients = ClientDB.get_all_clients()
        matching_clients = []
        
        for client in clients:
            client_id, name, phone, email, sub_type, start_date, end_date, status, created_at = client
            
            if (search_text in name.lower() or 
                search_text in phone.lower() or 
                search_text in email.lower()):
                matching_clients.append((client_id, f"{name} - {phone}"))
        
        self.client_combo.clear()
        if matching_clients:
            for client_id, display_text in matching_clients:
                self.client_combo.addItem(display_text, client_id)
            self.checkin_btn.setEnabled(True)
        else:
            self.client_combo.addItem("لا توجد نتائج")
            self.checkin_btn.setEnabled(False)
    
    def on_client_selected(self):
        """Handle client selection"""
        if self.client_combo.currentData():
            client_id = self.client_combo.currentData()
            self.display_client_info(client_id)
            self.checkin_btn.setEnabled(True)
        else:
            self.checkin_btn.setEnabled(False)
    
    def display_client_info(self, client_id):
        """Display selected client information"""
        clients = ClientDB.get_all_clients()
        client_info = None
        
        for client in clients:
            if client[0] == client_id:
                client_info = client
                break
        
        if client_info:
            client_id, name, phone, email, sub_type, start_date, end_date, status, created_at = client_info
            
            # Check subscription status
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            today = date.today()
            days_remaining = (end_date_obj - today).days
            
            subscription_status = "منتهي الصلاحية"
            if days_remaining > 0:
                subscription_status = f"صالح ({days_remaining} يوم متبقي)"
            elif days_remaining == 0:
                subscription_status = "ينتهي اليوم"
            
            info_text = f"""
معلومات العميل:
الاسم: {name}
الهاتف: {phone}
الإيميل: {email}
نوع الاشتراك: {sub_type}
تاريخ البداية: {start_date}
تاريخ الانتهاء: {end_date}
حالة الاشتراك: {subscription_status}
حالة العميل: {status}
            """
            
            self.client_info_text.setPlainText(info_text.strip())
            
            # Change button color based on subscription status
            if days_remaining <= 0:
                self.checkin_btn.setObjectName("danger_button")
                self.checkin_btn.setText("اشتراك منتهي - تسجيل الحضور")
            elif days_remaining <= 7:
                self.checkin_btn.setObjectName("warning_button")
                self.checkin_btn.setText("اشتراك ينتهي قريباً - تسجيل الحضور")
            else:
                self.checkin_btn.setObjectName("success_button")
                self.checkin_btn.setText("تسجيل الحضور")
            
            # Reapply stylesheet
            self.checkin_btn.style().unpolish(self.checkin_btn)
            self.checkin_btn.style().polish(self.checkin_btn)
    
    def mark_attendance(self):
        """Mark client attendance"""
        if not self.client_combo.currentData():
            return
        
        client_id = self.client_combo.currentData()
        
        # Check if already marked today
        today = date.today().strftime("%Y-%m-%d")
        attendance_records = AttendanceDB.get_attendance_by_client(client_id)
        
        already_marked_today = any(
            record[4] == today for record in attendance_records  # record[4] is date
        )
        
        if already_marked_today:
            reply = QMessageBox.question(
                self, "تأكيد", 
                "تم تسجيل حضور هذا العميل اليوم بالفعل.\nهل تريد تسجيل دخول إضافي؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        success = AttendanceDB.mark_attendance(client_id)
        
        if success:
            client_name = self.client_combo.currentText().split(" - ")[0]
            QMessageBox.information(self, "نجح", f"تم تسجيل حضور {client_name} بنجاح!")
            
            # Clear form
            self.client_search.clear()
            self.client_combo.clear()
            self.client_info_text.setPlainText("اختر عميل لعرض معلوماته...")
            self.checkin_btn.setEnabled(False)
            
            # Refresh data
            self.refresh_data()
        else:
            QMessageBox.critical(self, "خطأ", "فشل في تسجيل الحضور!")
    
    def filter_by_date(self):
        """Filter attendance by selected date"""
        selected_date = self.date_filter.date().toString("yyyy-MM-dd")
        self.load_attendance_data(selected_date)
    
    def on_calendar_date_selected(self, date):
        """Handle calendar date selection"""
        self.date_filter.setDate(date)
        self.filter_by_date()
    
    def load_attendance_data(self, date_filter=None):
        """Load attendance data for specific date"""
        if not date_filter:
            date_filter = date.today().strftime("%Y-%m-%d")
        
        # Get all attendance records
        from database import get_connection
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT a.id, c.name, a.check_in_time, a.check_out_time, a.date, a.status
                FROM attendance a
                JOIN clients c ON a.client_id = c.id
                WHERE a.date = ?
                ORDER BY a.check_in_time DESC
                """, (date_filter,))
                
                attendance_records = cursor.fetchall()
                
                self.attendance_table.setRowCount(len(attendance_records))
                
                for row, record in enumerate(attendance_records):
                    for col, value in enumerate(record):
                        if value is None:
                            value = "-"
                        item = QTableWidgetItem(str(value))
                        
                        # Color code status
                        if col == 5:  # Status column
                            if value == 'present':
                                item.setBackground(Qt.GlobalColor.green)
                            else:
                                item.setBackground(Qt.GlobalColor.yellow)
                        
                        self.attendance_table.setItem(row, col, item)
                
                # Update attendance count
                self.attendance_count_label.setText(f"عدد الحاضرين في {date_filter}: {len(attendance_records)}")
                
            except Exception as e:
                print(f"Error loading attendance data: {e}")
            finally:
                conn.close()
    
    def refresh_data(self):
        """Refresh all data"""
        # Load today's attendance
        today = date.today().strftime("%Y-%m-%d")
        self.load_attendance_data(today)
        
        # Update calendar to highlight dates with attendance
        self.highlight_attendance_dates()
    
    def highlight_attendance_dates(self):
        """Highlight dates with attendance records in calendar"""
        # This would require custom calendar implementation
        # For now, we'll keep it simple
        pass
