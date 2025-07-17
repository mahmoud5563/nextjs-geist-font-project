import barcode
from barcode.writer import ImageWriter
import os
import uuid
from datetime import datetime

class BarcodeGenerator:
    def __init__(self):
        self.barcode_dir = "barcodes"
        if not os.path.exists(self.barcode_dir):
            os.makedirs(self.barcode_dir)
    
    def generate_barcode_data(self, client_id):
        """Generate unique barcode data for client"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        barcode_data = f"GYM{client_id:04d}{timestamp}{unique_id}"
        return barcode_data
    
    def create_barcode_image(self, barcode_data, client_name=""):
        """Create barcode image file"""
        try:
            # Use Code128 barcode format
            code128 = barcode.get_barcode_class('code128')
            barcode_instance = code128(barcode_data, writer=ImageWriter())
            
            # Generate filename
            filename = f"barcode_{barcode_data}"
            filepath = os.path.join(self.barcode_dir, filename)
            
            # Save barcode image
            barcode_instance.save(filepath)
            
            return f"{filepath}.png"
        except Exception as e:
            print(f"Error creating barcode image: {e}")
            return None
    
    def validate_barcode(self, barcode_data):
        """Validate barcode format"""
        if not barcode_data:
            return False
        
        # Check if barcode starts with GYM and has proper length
        if barcode_data.startswith('GYM') and len(barcode_data) >= 20:
            return True
        return False
    
    def get_client_id_from_barcode(self, barcode_data):
        """Extract client ID from barcode data"""
        try:
            if self.validate_barcode(barcode_data):
                # Extract client ID from barcode (positions 3-7)
                client_id = int(barcode_data[3:7])
                return client_id
        except Exception as e:
            print(f"Error extracting client ID from barcode: {e}")
        return None

# Barcode status management
class BarcodeManager:
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    RENEWED = "renewed"
    
    @staticmethod
    def activate_barcode(barcode_id):
        """Activate barcode"""
        from database import BarcodeDB
        return BarcodeDB.update_barcode_status(barcode_id, BarcodeManager.ACTIVE)
    
    @staticmethod
    def deactivate_barcode(barcode_id):
        """Deactivate barcode"""
        from database import BarcodeDB
        return BarcodeDB.update_barcode_status(barcode_id, BarcodeManager.INACTIVE)
    
    @staticmethod
    def renew_barcode(client_id):
        """Renew barcode for client"""
        from database import BarcodeDB
        
        # Get existing barcode
        existing_barcode = BarcodeDB.get_client_barcode(client_id)
        if existing_barcode:
            # Mark old barcode as expired
            BarcodeDB.update_barcode_status(existing_barcode[0], BarcodeManager.EXPIRED)
        
        # Generate new barcode
        generator = BarcodeGenerator()
        new_barcode_data = generator.generate_barcode_data(client_id)
        
        # Create new barcode record
        success = BarcodeDB.create_barcode(client_id, new_barcode_data)
        if success:
            # Generate barcode image
            image_path = generator.create_barcode_image(new_barcode_data)
            return new_barcode_data, image_path
        
        return None, None
