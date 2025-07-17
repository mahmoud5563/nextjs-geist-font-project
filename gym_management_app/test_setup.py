#!/usr/bin/env python3
"""
Test script to verify the gym management system setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import PyQt6
        print("✓ PyQt6 imported successfully")
    except ImportError as e:
        print(f"✗ PyQt6 import failed: {e}")
        return False
    
    try:
        import barcode
        print("✓ python-barcode imported successfully")
    except ImportError as e:
        print(f"✗ python-barcode import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Pillow import failed: {e}")
        return False
    
    return True

def test_database():
    """Test database initialization"""
    print("\nTesting database setup...")
    
    try:
        from database import init_db, ClientDB
        
        # Initialize database
        init_db()
        print("✓ Database initialized successfully")
        
        # Test adding a sample client
        client_id = ClientDB.add_client(
            name="عميل تجريبي",
            phone="01234567890",
            email="test@example.com",
            subscription_type="شهري",
            subscription_start="2024-01-01",
            subscription_end="2024-02-01"
        )
        
        if client_id:
            print(f"✓ Sample client added successfully (ID: {client_id})")
            
            # Test retrieving clients
            clients = ClientDB.get_all_clients()
            if clients:
                print(f"✓ Retrieved {len(clients)} clients from database")
            else:
                print("✗ No clients found in database")
                return False
        else:
            print("✗ Failed to add sample client")
            return False
            
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False
    
    return True

def test_barcode():
    """Test barcode generation"""
    print("\nTesting barcode generation...")
    
    try:
        from utils.barcode_utils import BarcodeGenerator
        
        generator = BarcodeGenerator()
        
        # Test barcode data generation
        barcode_data = generator.generate_barcode_data(1)
        print(f"✓ Generated barcode data: {barcode_data}")
        
        # Test barcode validation
        is_valid = generator.validate_barcode(barcode_data)
        if is_valid:
            print("✓ Barcode validation passed")
        else:
            print("✗ Barcode validation failed")
            return False
        
        # Test barcode image creation
        image_path = generator.create_barcode_image(barcode_data, "Test Client")
        if image_path and os.path.exists(image_path):
            print(f"✓ Barcode image created: {image_path}")
        else:
            print("✗ Failed to create barcode image")
            return False
            
    except Exception as e:
        print(f"✗ Barcode test failed: {e}")
        return False
    
    return True

def test_ui_components():
    """Test UI component imports"""
    print("\nTesting UI components...")
    
    try:
        from ui.main_window import MainWindow
        print("✓ MainWindow imported successfully")
        
        from ui.client_management import ClientManagementWidget
        print("✓ ClientManagementWidget imported successfully")
        
        from ui.attendance import AttendanceWidget
        print("✓ AttendanceWidget imported successfully")
        
        from ui.barcode_management import BarcodeManagementWidget
        print("✓ BarcodeManagementWidget imported successfully")
        
    except Exception as e:
        print(f"✗ UI component test failed: {e}")
        return False
    
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    
    try:
        # Remove test database
        if os.path.exists("gym_management.db"):
            os.remove("gym_management.db")
            print("✓ Test database removed")
        
        # Remove test barcode images
        if os.path.exists("barcodes"):
            import shutil
            shutil.rmtree("barcodes")
            print("✓ Test barcode images removed")
            
    except Exception as e:
        print(f"Warning: Cleanup failed: {e}")

def main():
    """Main test function"""
    print("=== Gym Management System Setup Test ===\n")
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    # Test database
    if not test_database():
        all_tests_passed = False
    
    # Test barcode generation
    if not test_barcode():
        all_tests_passed = False
    
    # Test UI components
    if not test_ui_components():
        all_tests_passed = False
    
    # Cleanup
    cleanup_test_data()
    
    print("\n=== Test Results ===")
    if all_tests_passed:
        print("✓ All tests passed! The system is ready to use.")
        print("\nTo start the application, run:")
        print("python main.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
