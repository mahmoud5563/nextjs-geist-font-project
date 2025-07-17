from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
                             QMessageBox, QGroupBox, QFormLayout, QHeaderView,
                             QTextEdit, QSplitter, QFileDialog, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from database import ClientDB, BarcodeDB
from utils.barcode_utils import BarcodeGenerator, BarcodeManager
import os

class BarcodeGenerationThread(QThread):
    """Thread for generating barcodes without blocking UI"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str)  # barcode_data, image_path
    error = pyqtSignal(str)
    
    def __init__(self, client_id, client_name):
        super().__init__()
        self.client_id = client_id
        self.client_name = client_name
    
    def run(self):
        try:
            self.progress.emit(25)
            generator = BarcodeGenerator()
            
            self.progress.emit(50)
            barcode_data = generator.generate_barcode_data(self.client_id)
            
            self.progress.emit(75)
            image_path = generator.create_barcode_image(barcode_data, self.client_name)
            
            self.progress.emit(100)
            
            if image_path:
                # Save to database
                success = BarcodeDB.create_barcode(self.client_id, barcode_data)
                if success:
                    self.finished.emit(barcode_data, image_path)
                else:
                    self.error.emit("فشل في حفظ الباركود في قاعدة البيانات")
            else:
                self.error.emit("فشل في إنشاء صورة الباركود")
                
        except Exception as e:
            self.error.emit(f"خطأ في إنشاء الباركود: {str(e)}")

class BarcodeManagementWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Setup barcode management UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Page title
        title = QLabel("إدارة الباركود")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Create splitter for layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Barcode generation and management
        self.create_barcode_section(splitter)
        
        # Right side - Barcode table and preview
        self.create_table_section(splitter)
        
        layout.addWidget(splitter)
    
    def create_barcode_section(self, parent):
        """Create barcode generation section"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Barcode generation form
        generation_group = QGroupBox("إنشاء باركود جديد")
        generation_layout = QFormLayout(generation_group)
        generation_layout.setSpacing(15)
        
        # Client selection
        self.client_combo = QComboBox()
        self.load_clients()
        self.client_combo.currentTextChanged.connect(self.on_client_selected)
        generation_layout.addRow("اختر العميل:", self.client_combo)
        
        # Generate button
        self.generate_btn = QPushButton("إنشاء باركود")
        self.generate_btn.setObjectName("success_button")
        self.generate_btn.clicked.connect(self.generate_barcode)
        generation_layout.addRow(self.generate_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        generation_layout.addRow(self.progress_bar)
        
        left_layout.addWidget(generation_group)
        
        # Barcode management form
        management_group = QGroupBox("إدارة الباركود")
        management_layout = QFormLayout(management_group)
        management_layout.setSpacing(15)
        
        # Barcode search
        self.barcode_search = QLineEdit()
        self.barcode_search.setPlaceholderText("أدخل رقم الباركود للبحث...")
        self.barcode_search.textChanged.connect(self.search_barcode)
        management_layout.addRow("البحث عن باركود:", self.barcode_search)
        
        # Management buttons
        button_layout = QHBoxLayout()
        
        self.activate_btn = QPushButton("تفعيل")
        self.activate_btn.setObjectName("success_button")
        self.activate_btn.clicked.connect(self.activate_barcode)
        self.activate_btn.setEnabled(False)
        button_layout.addWidget(self.activate_btn)
        
        self.deactivate_btn = QPushButton("إلغاء تفعيل")
        self.deactivate_btn.setObjectName("danger_button")
        self.deactivate_btn.clicked.connect(self.deactivate_barcode)
        self.deactivate_btn.setEnabled(False)
        button_layout.addWidget(self.deactivate_btn)
        
        self.renew_btn = QPushButton("تجديد")
        self.renew_btn.setObjectName("warning_button")
        self.renew_btn.clicked.connect(self.renew_barcode)
        self.renew_btn.setEnabled(False)
        button_layout.addWidget(self.renew_btn)
        
        management_layout.addRow(button_layout)
        
        left_layout.addWidget(management_group)
        
        # Barcode info display
        self.create_barcode_info_section(left_layout)
        
        # Barcode scanner simulation
        self.create_scanner_section(left_layout)
        
        left_layout.addStretch()
        parent.addWidget(left_widget)
    
    def create_barcode_info_section(self, parent_layout):
        """Create barcode information display"""
        info_group = QGroupBox("معلومات الباركود")
        info_layout = QVBoxLayout(info_group)
        
        self.barcode_info_text = QTextEdit()
        self.barcode_info_text.setReadOnly(True)
        self.barcode_info_text.setMaximumHeight(200)
        self.barcode_info_text.setPlainText("اختر باركود لعرض معلوماته...")
        
        info_layout.addWidget(self.barcode_info_text)
        
        # Export button
        self.export_btn = QPushButton("تصدير صورة الباركود")
        self.export_btn.clicked.connect(self.export_barcode_image)
        self.export_btn.setEnabled(False)
        info_layout.addWidget(self.export_btn)
        
        parent_layout.addWidget(info_group)
    
    def create_scanner_section(self, parent_layout):
        """Create barcode scanner simulation section"""
        scanner_group = QGroupBox("ماسح الباركود")
        scanner_layout = QFormLayout(scanner_group)
        
        # Barcode input (simulating scanner)
        self.scanner_input = QLineEdit()
        self.scanner_input.setPlaceholderText("امسح الباركود أو أدخله يدوياً...")
        self.scanner_input.returnPressed.connect(self.process_scanned_barcode)
        scanner_layout.addRow("الباركود الممسوح:", self.scanner_input)
        
        # Process button
        self.process_btn = QPushButton("معالجة الباركود")
        self.process_btn.clicked.connect(self.process_scanned_barcode)
        scanner_layout.addRow(self.process_btn)
        
        # Scanner result
        self.scanner_result = QLabel("في انتظار مسح الباركود...")
        self.scanner_result.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        scanner_layout.addRow("النتيجة:", self.scanner_result)
        
        parent_layout.addWidget(scanner_group)
    
    def create_table_section(self, parent):
        """Create barcode table section"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Filter options
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("تصفية حسب الحالة:"))
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["الكل", "active", "inactive", "expired", "renewed"])
        self.status_filter.currentTextChanged.connect(self.filter_barcodes)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("تحديث")
        refresh_btn.clicked.connect(self.refresh_data)
        filter_layout.addWidget(refresh_btn)
        
        right_layout.addLayout(filter_layout)
        
        # Barcode table
        self.barcode_table = QTableWidget()
        self.barcode_table.setColumnCount(6)
        self.barcode_table.setHorizontalHeaderLabels([
            "ID", "اسم العميل", "رقم الباركود", "الحالة", "تاريخ الإنشاء", "آخر تحديث"
        ])
        
        # Set table properties
        header = self.barcode_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.barcode_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.barcode_table.setAlternatingRowColors(True)
        self.barcode_table.itemSelectionChanged.connect(self.on_barcode_selected)
        
        right_layout.addWidget(self.barcode_table)
        
        # Barcode preview
        preview_group = QGroupBox("معاينة الباركود")
        preview_layout = QVBoxLayout(preview_group)
        
        self.barcode_preview = QLabel("اختر باركود لمعاينته")
        self.barcode_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.barcode_preview.setMinimumHeight(100)
        self.barcode_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)
        preview_layout.addWidget(self.barcode_preview)
        
        right_layout.addWidget(preview_group)
        
        parent.addWidget(right_widget)
    
    def load_clients(self):
        """Load clients into combo box"""
        self.client_combo.clear()
        self.client_combo.addItem("اختر عميل...", None)
        
        clients = ClientDB.get_all_clients()
        for client in clients:
            client_id, name, phone, email, sub_type, start_date, end_date, status, created_at = client
            if status == 'active':  # Only show active clients
                display_text = f"{name} - {phone}"
                self.client_combo.addItem(display_text, client_id)
    
    def on_client_selected(self):
        """Handle client selection"""
        client_id = self.client_combo.currentData()
        if client_id:
            # Check if client already has a barcode
            existing_barcode = BarcodeDB.get_client_barcode(client_id)
            if existing_barcode:
                reply = QMessageBox.question(
                    self, "باركود موجود", 
                    "هذا العميل لديه باركود بالفعل.\nهل تريد إنشاء باركود جديد؟",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            self.generate_btn.setEnabled(True)
        else:
            self.generate_btn.setEnabled(False)
    
    def generate_barcode(self):
        """Generate barcode for selected client"""
        client_id = self.client_combo.currentData()
        if not client_id:
            return
        
        client_name = self.client_combo.currentText().split(" - ")[0]
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.generate_btn.setEnabled(False)
        
        # Start barcode generation thread
        self.generation_thread = BarcodeGenerationThread(client_id, client_name)
        self.generation_thread.progress.connect(self.progress_bar.setValue)
        self.generation_thread.finished.connect(self.on_barcode_generated)
        self.generation_thread.error.connect(self.on_generation_error)
        self.generation_thread.start()
    
    def on_barcode_generated(self, barcode_data, image_path):
        """Handle successful barcode generation"""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        
        QMessageBox.information(
            self, "نجح", 
            f"تم إنشاء الباركود بنجاح!\nرقم الباركود: {barcode_data}"
        )
        
        self.refresh_data()
        
        # Reset client selection
        self.client_combo.setCurrentIndex(0)
    
    def on_generation_error(self, error_message):
        """Handle barcode generation error"""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        
        QMessageBox.critical(self, "خطأ", error_message)
    
    def search_barcode(self):
        """Search for barcode"""
        search_text = self.barcode_search.text().strip()
        
        if len(search_text) < 3:
            self.reset_management_buttons()
            return
        
        # Search in table
        found = False
        for row in range(self.barcode_table.rowCount()):
            barcode_item = self.barcode_table.item(row, 2)  # Barcode data column
            if barcode_item and search_text.upper() in barcode_item.text().upper():
                self.barcode_table.selectRow(row)
                found = True
                break
        
        if not found:
            self.reset_management_buttons()
            QMessageBox.information(self, "البحث", "لم يتم العثور على الباركود")
    
    def on_barcode_selected(self):
        """Handle barcode selection from table"""
        current_row = self.barcode_table.currentRow()
        if current_row >= 0:
            # Get barcode data
            barcode_id = int(self.barcode_table.item(current_row, 0).text())
            client_name = self.barcode_table.item(current_row, 1).text()
            barcode_data = self.barcode_table.item(current_row, 2).text()
            status = self.barcode_table.item(current_row, 3).text()
            created_at = self.barcode_table.item(current_row, 4).text()
            updated_at = self.barcode_table.item(current_row, 5).text()
            
            # Store selected barcode info
            self.selected_barcode_id = barcode_id
            self.selected_barcode_data = barcode_data
            
            # Display barcode info
            info_text = f"""
معلومات الباركود:
العميل: {client_name}
رقم الباركود: {barcode_data}
الحالة: {status}
تاريخ الإنشاء: {created_at}
آخر تحديث: {updated_at}
            """
            self.barcode_info_text.setPlainText(info_text.strip())
            
            # Enable management buttons based on status
            self.activate_btn.setEnabled(status != 'active')
            self.deactivate_btn.setEnabled(status == 'active')
            self.renew_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
            
            # Load barcode image preview
            self.load_barcode_preview(barcode_data)
    
    def load_barcode_preview(self, barcode_data):
        """Load barcode image preview"""
        image_path = f"barcodes/barcode_{barcode_data}.png"
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale image to fit preview
                scaled_pixmap = pixmap.scaled(
                    300, 100, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                self.barcode_preview.setPixmap(scaled_pixmap)
            else:
                self.barcode_preview.setText("فشل في تحميل صورة الباركود")
        else:
            self.barcode_preview.setText("صورة الباركود غير موجودة")
    
    def activate_barcode(self):
        """Activate selected barcode"""
        if hasattr(self, 'selected_barcode_id'):
            success = BarcodeManager.activate_barcode(self.selected_barcode_id)
            if success:
                QMessageBox.information(self, "نجح", "تم تفعيل الباركود بنجاح!")
                self.refresh_data()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في تفعيل الباركود!")
    
    def deactivate_barcode(self):
        """Deactivate selected barcode"""
        if hasattr(self, 'selected_barcode_id'):
            reply = QMessageBox.question(
                self, "تأكيد", 
                "هل أنت متأكد من إلغاء تفعيل هذا الباركود؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success = BarcodeManager.deactivate_barcode(self.selected_barcode_id)
                if success:
                    QMessageBox.information(self, "نجح", "تم إلغاء تفعيل الباركود بنجاح!")
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في إلغاء تفعيل الباركود!")
    
    def renew_barcode(self):
        """Renew selected barcode"""
        if hasattr(self, 'selected_barcode_id'):
            # Get client ID from current selection
            current_row = self.barcode_table.currentRow()
            if current_row >= 0:
                # Find client ID from barcode data
                from utils.barcode_utils import BarcodeGenerator
                generator = BarcodeGenerator()
                client_id = generator.get_client_id_from_barcode(self.selected_barcode_data)
                
                if client_id:
                    new_barcode_data, image_path = BarcodeManager.renew_barcode(client_id)
                    if new_barcode_data:
                        QMessageBox.information(
                            self, "نجح", 
                            f"تم تجديد الباركود بنجاح!\nالباركود الجديد: {new_barcode_data}"
                        )
                        self.refresh_data()
                    else:
                        QMessageBox.critical(self, "خطأ", "فشل في تجديد الباركود!")
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في استخراج معرف العميل من الباركود!")
    
    def export_barcode_image(self):
        """Export barcode image"""
        if hasattr(self, 'selected_barcode_data'):
            image_path = f"barcodes/barcode_{self.selected_barcode_data}.png"
            if os.path.exists(image_path):
                save_path, _ = QFileDialog.getSaveFileName(
                    self, "حفظ صورة الباركود", 
                    f"barcode_{self.selected_barcode_data}.png",
                    "PNG Files (*.png);;All Files (*)"
                )
                
                if save_path:
                    try:
                        import shutil
                        shutil.copy2(image_path, save_path)
                        QMessageBox.information(self, "نجح", "تم حفظ صورة الباركود بنجاح!")
                    except Exception as e:
                        QMessageBox.critical(self, "خطأ", f"فشل في حفظ الصورة: {str(e)}")
            else:
                QMessageBox.warning(self, "تحذير", "صورة الباركود غير موجودة!")
    
    def process_scanned_barcode(self):
        """Process scanned barcode"""
        barcode_data = self.scanner_input.text().strip()
        
        if not barcode_data:
            return
        
        # Validate barcode
        from utils.barcode_utils import BarcodeGenerator
        generator = BarcodeGenerator()
        
        if not generator.validate_barcode(barcode_data):
            self.scanner_result.setText("باركود غير صالح!")
            self.scanner_result.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 4px;
                    color: #721c24;
                    font-weight: bold;
                }
            """)
            return
        
        # Get client ID from barcode
        client_id = generator.get_client_id_from_barcode(barcode_data)
        if not client_id:
            self.scanner_result.setText("فشل في استخراج معرف العميل!")
            return
        
        # Get barcode info from database
        barcode_info = BarcodeDB.get_client_barcode(client_id)
        if barcode_info:
            barcode_id, client_id, stored_barcode_data, status, created_at, updated_at, client_name = barcode_info
            
            if stored_barcode_data == barcode_data:
                if status == 'active':
                    self.scanner_result.setText(f"✓ باركود صالح - العميل: {client_name}")
                    self.scanner_result.setStyleSheet("""
                        QLabel {
                            padding: 10px;
                            background-color: #d4edda;
                            border: 1px solid #c3e6cb;
                            border-radius: 4px;
                            color: #155724;
                            font-weight: bold;
                        }
                    """)
                    
                    # Auto mark attendance
                    from database import AttendanceDB
                    AttendanceDB.mark_attendance(client_id)
                    
                else:
                    self.scanner_result.setText(f"⚠ باركود غير مفعل - العميل: {client_name}")
                    self.scanner_result.setStyleSheet("""
                        QLabel {
                            padding: 10px;
                            background-color: #fff3cd;
                            border: 1px solid #ffeaa7;
                            border-radius: 4px;
                            color: #856404;
                            font-weight: bold;
                        }
                    """)
            else:
                self.scanner_result.setText("باركود غير مطابق في قاعدة البيانات!")
        else:
            self.scanner_result.setText("باركود غير موجود في النظام!")
        
        # Clear scanner input
        self.scanner_input.clear()
    
    def filter_barcodes(self):
        """Filter barcodes by status"""
        status_filter = self.status_filter.currentText()
        
        for row in range(self.barcode_table.rowCount()):
            if status_filter == "الكل":
                self.barcode_table.setRowHidden(row, False)
            else:
                status_item = self.barcode_table.item(row, 3)  # Status column
                if status_item:
                    self.barcode_table.setRowHidden(row, status_item.text() != status_filter)
    
    def reset_management_buttons(self):
        """Reset management buttons"""
        self.activate_btn.setEnabled(False)
        self.deactivate_btn.setEnabled(False)
        self.renew_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.barcode_info_text.setPlainText("اختر باركود لعرض معلوماته...")
        self.barcode_preview.clear()
        self.barcode_preview.setText("اختر باركود لمعاينته")
    
    def refresh_data(self):
        """Refresh barcode data"""
        # Load clients
        self.load_clients()
        
        # Load barcodes table
        from database import get_connection
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT b.id, c.name, b.barcode_data, b.status, b.created_at, b.updated_at
                FROM barcodes b
                JOIN clients c ON b.client_id = c.id
                ORDER BY b.created_at DESC
                """)
                
                barcodes = cursor.fetchall()
                
                self.barcode_table.setRowCount(len(barcodes))
                
                for row, barcode in enumerate(barcodes):
                    for col, value in enumerate(barcode):
                        item = QTableWidgetItem(str(value))
                        
                        # Color code status
                        if col == 3:  # Status column
                            if value == 'active':
                                item.setBackground(Qt.GlobalColor.green)
                            elif value == 'inactive':
                                item.setBackground(Qt.GlobalColor.red)
                            elif value == 'expired':
                                item.setBackground(Qt.GlobalColor.yellow)
                            else:
                                item.setBackground(Qt.GlobalColor.cyan)
                        
                        self.barcode_table.setItem(row, col, item)
                
            except Exception as e:
                print(f"Error loading barcode data: {e}")
            finally:
                conn.close()
        
        # Reset selection
        self.reset_management_buttons()
