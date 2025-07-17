import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.main_window import MainWindow

def setup_application():
    """Setup application configuration"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("نظام إدارة الجيم")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Gym Management System")
    
    # Set application font
    font = QFont("Arial", 10)
    app.setFont(font)
    
    # Enable high DPI scaling
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    return app

def load_stylesheet(app):
    """Load and apply stylesheet"""
    try:
        style_path = os.path.join(os.path.dirname(__file__), "utils", "style.qss")
        with open(style_path, "r", encoding="utf-8") as f:
            stylesheet = f.read()
            app.setStyleSheet(stylesheet)
        print("Stylesheet loaded successfully!")
    except FileNotFoundError:
        print("Warning: Stylesheet file not found. Using default styling.")
    except Exception as e:
        print(f"Error loading stylesheet: {e}")

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import barcode
    except ImportError:
        missing_deps.append("python-barcode")
    
    try:
        from barcode.writer import ImageWriter
    except ImportError:
        missing_deps.append("Pillow (for barcode image generation)")
    
    if missing_deps:
        error_msg = "المكتبات التالية مطلوبة لتشغيل التطبيق:\n\n"
        for dep in missing_deps:
            error_msg += f"• {dep}\n"
        error_msg += "\nيرجى تثبيتها باستخدام:\n"
        error_msg += "pip install python-barcode[images] pillow"
        
        return False, error_msg
    
    return True, ""

def create_directories():
    """Create necessary directories"""
    directories = [
        "barcodes",
        "exports",
        "backups"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"Created directory: {directory}")
            except Exception as e:
                print(f"Warning: Could not create directory {directory}: {e}")

def main():
    """Main application entry point"""
    try:
        # Check dependencies
        deps_ok, error_msg = check_dependencies()
        if not deps_ok:
            print("Dependency Error:")
            print(error_msg)
            
            # Try to show GUI error if PyQt6 is available
            try:
                app = QApplication(sys.argv)
                QMessageBox.critical(None, "خطأ في المتطلبات", error_msg)
                return 1
            except:
                return 1
        
        # Setup application
        app = setup_application()
        
        # Load stylesheet
        load_stylesheet(app)
        
        # Create necessary directories
        create_directories()
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        print("Gym Management System started successfully!")
        print("نظام إدارة الجيم - تم تشغيل التطبيق بنجاح!")
        
        # Start event loop
        return app.exec()
        
    except ImportError as e:
        error_msg = f"خطأ في استيراد المكتبات:\n{str(e)}\n\nيرجى التأكد من تثبيت PyQt6:\npip install PyQt6"
        print(error_msg)
        
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "خطأ في الاستيراد", error_msg)
        except:
            pass
        
        return 1
        
    except Exception as e:
        error_msg = f"خطأ غير متوقع:\n{str(e)}"
        print(error_msg)
        
        try:
            QMessageBox.critical(None, "خطأ", error_msg)
        except:
            pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
