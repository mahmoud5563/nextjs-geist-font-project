from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
                             QDateEdit, QMessageBox, QGroupBox, QFormLayout, QHeaderView)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from database import ClientDB

class ClientManagementWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Setup client management UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Page title
        title = QLabel("إدارة العملاء")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Create form and table layout
        content_layout = QHBoxLayout()
        
        # Client form
        self.create_client_form(content_layout)
        
        # Client table
        self.create_client_table(content_layout)
        
        layout.addLayout(content_layout)
    
    def create_client_form(self, parent_layout):
        """Create client input form"""
        form_group = QGroupBox("بيانات العميل")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(15)
        
        # Name field
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("أدخل اسم العميل")
        form_layout.addRow("الاسم:", self.name_input)
        
        # Phone field
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("رقم الهاتف")
        form_layout.addRow("الهاتف:", self.phone_input)
        
        # Email field
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("البريد الإلكتروني")
        form_layout.addRow("الإيميل:", self.email_input)
        
        # Subscription type
        self.subscription_combo = QComboBox()
        self.subscription_combo.addItems([
            "شهري", "ربع سنوي", "نصف سنوي", "سنوي", "يومي"
        ])
        form_layout.addRow("نوع الاشتراك:", self.subscription_combo)
        
        # Subscription start date
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        form_layout.addRow("تاريخ البداية:", self.start_date)
        
        # Subscription end date
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addMonths(1))
        self.end_date.setCalendarPopup(True)
        form_layout.addRow("تاريخ الانتهاء:", self.end_date)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["active", "inactive", "suspended"])
        form_layout.addRow("الحالة:", self.status_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("إضافة عميل")
        self.add_btn.setObjectName("success_button")
        self.add_btn.clicked.connect(self.add_client)
        button_layout.addWidget(self.add_btn)
        
        self.update_btn = QPushButton("تحديث")
        self.update_btn.setObjectName("warning_button")
        self.update_btn.clicked.connect(self.update_client)
        self.update_btn.setEnabled(False)
        button_layout.addWidget(self.update_btn)
        
        self.clear_btn = QPushButton("مسح")
        self.clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_btn)
        
        form_layout.addRow(button_layout)
        
        form_group.setMaximumWidth(400)
        parent_layout.addWidget(form_group)
    
    def create_client_table(self, parent_layout):
        """Create client data table"""
        table_group = QGroupBox("قائمة العملاء")
        table_layout = QVBoxLayout(table_group)
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("البحث:")
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_box")
        self.search_input.setPlaceholderText("ابحث عن عميل...")
        self.search_input.textChanged.connect(self.filter_clients)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        
        table_layout.addLayout(search_layout)
        
        # Table
        self.client_table = QTableWidget()
        self.client_table.setColumnCount(8)
        self.client_table.setHorizontalHeaderLabels([
            "ID", "الاسم", "الهاتف", "الإيميل", "نوع الاشتراك", 
            "تاريخ البداية", "تاريخ الانتهاء", "الحالة"
        ])
        
        # Set table properties
        header = self.client_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.client_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.client_table.setAlternatingRowColors(True)
        
        # Connect table selection
        self.client_table.itemSelectionChanged.connect(self.on_client_selected)
        
        table_layout.addWidget(self.client_table)
        
        # Table buttons
        table_button_layout = QHBoxLayout()
        
        self.delete_btn = QPushButton("حذف العميل")
        self.delete_btn.setObjectName("danger_button")
        self.delete_btn.clicked.connect(self.delete_client)
        self.delete_btn.setEnabled(False)
        table_button_layout.addWidget(self.delete_btn)
        
        table_button_layout.addStretch()
        
        refresh_btn = QPushButton("تحديث القائمة")
        refresh_btn.clicked.connect(self.refresh_data)
        table_button_layout.addWidget(refresh_btn)
        
        table_layout.addLayout(table_button_layout)
        
        parent_layout.addWidget(table_group)
    
    def add_client(self):
        """Add new client"""
        if not self.validate_form():
            return
        
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        subscription_type = self.subscription_combo.currentText()
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        client_id = ClientDB.add_client(name, phone, email, subscription_type, start_date, end_date)
        
        if client_id:
            QMessageBox.information(self, "نجح", f"تم إضافة العميل بنجاح!\nرقم العميل: {client_id}")
            self.clear_form()
            self.refresh_data()
        else:
            QMessageBox.critical(self, "خطأ", "فشل في إضافة العميل!")
    
    def update_client(self):
        """Update selected client"""
        if not hasattr(self, 'selected_client_id'):
            return
        
        if not self.validate_form():
            return
        
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        subscription_type = self.subscription_combo.currentText()
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        status = self.status_combo.currentText()
        
        success = ClientDB.update_client(
            self.selected_client_id, name, phone, email, 
            subscription_type, start_date, end_date, status
        )
        
        if success:
            QMessageBox.information(self, "نجح", "تم تحديث بيانات العميل بنجاح!")
            self.clear_form()
            self.refresh_data()
        else:
            QMessageBox.critical(self, "خطأ", "فشل في تحديث بيانات العميل!")
    
    def delete_client(self):
        """Delete selected client"""
        if not hasattr(self, 'selected_client_id'):
            return
        
        reply = QMessageBox.question(
            self, "تأكيد الحذف", 
            "هل أنت متأكد من حذف هذا العميل؟\nسيتم حذف جميع البيانات المرتبطة به.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = ClientDB.delete_client(self.selected_client_id)
            if success:
                QMessageBox.information(self, "نجح", "تم حذف العميل بنجاح!")
                self.clear_form()
                self.refresh_data()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في حذف العميل!")
    
    def on_client_selected(self):
        """Handle client selection from table"""
        current_row = self.client_table.currentRow()
        if current_row >= 0:
            # Get client data from table
            client_id = int(self.client_table.item(current_row, 0).text())
            name = self.client_table.item(current_row, 1).text()
            phone = self.client_table.item(current_row, 2).text()
            email = self.client_table.item(current_row, 3).text()
            subscription_type = self.client_table.item(current_row, 4).text()
            start_date = self.client_table.item(current_row, 5).text()
            end_date = self.client_table.item(current_row, 6).text()
            status = self.client_table.item(current_row, 7).text()
            
            # Fill form with selected client data
            self.selected_client_id = client_id
            self.name_input.setText(name)
            self.phone_input.setText(phone)
            self.email_input.setText(email)
            
            # Set combo box values
            subscription_index = self.subscription_combo.findText(subscription_type)
            if subscription_index >= 0:
                self.subscription_combo.setCurrentIndex(subscription_index)
            
            status_index = self.status_combo.findText(status)
            if status_index >= 0:
                self.status_combo.setCurrentIndex(status_index)
            
            # Set dates
            self.start_date.setDate(QDate.fromString(start_date, "yyyy-MM-dd"))
            self.end_date.setDate(QDate.fromString(end_date, "yyyy-MM-dd"))
            
            # Enable update and delete buttons
            self.update_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            
            # Change add button to update mode
            self.add_btn.setText("إضافة عميل جديد")
    
    def clear_form(self):
        """Clear form fields"""
        self.name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.subscription_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.start_date.setDate(QDate.currentDate())
        self.end_date.setDate(QDate.currentDate().addMonths(1))
        
        # Reset buttons
        self.add_btn.setText("إضافة عميل")
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        
        # Clear selection
        if hasattr(self, 'selected_client_id'):
            delattr(self, 'selected_client_id')
        
        self.client_table.clearSelection()
    
    def validate_form(self):
        """Validate form input"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم العميل!")
            return False
        
        if not self.phone_input.text().strip():
            QMessageBox.warning(self, "تحذير", "يرجى إدخال رقم الهاتف!")
            return False
        
        return True
    
    def filter_clients(self):
        """Filter clients based on search input"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.client_table.rowCount()):
            match = False
            for col in range(self.client_table.columnCount()):
                item = self.client_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            
            self.client_table.setRowHidden(row, not match)
    
    def refresh_data(self):
        """Refresh client data in table"""
        clients = ClientDB.get_all_clients()
        
        self.client_table.setRowCount(len(clients))
        
        for row, client in enumerate(clients):
            for col, value in enumerate(client):
                item = QTableWidgetItem(str(value))
                if col == 7:  # Status column
                    if value == 'active':
                        item.setBackground(Qt.GlobalColor.green)
                    elif value == 'inactive':
                        item.setBackground(Qt.GlobalColor.red)
                    else:
                        item.setBackground(Qt.GlobalColor.yellow)
                
                self.client_table.setItem(row, col, item)
