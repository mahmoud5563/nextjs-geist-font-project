import sqlite3
from datetime import datetime

def get_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect("gym_management.db")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    """Initialize database tables"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Create clients table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                subscription_type TEXT NOT NULL,
                subscription_start DATE,
                subscription_end DATE,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create attendance table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                check_in_time TIMESTAMP,
                check_out_time TIMESTAMP,
                date TEXT,
                status TEXT DEFAULT 'present',
                FOREIGN KEY(client_id) REFERENCES clients(id)
            )
            """)
            
            # Create barcode table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS barcodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                barcode_data TEXT UNIQUE,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(client_id) REFERENCES clients(id)
            )
            """)
            
            conn.commit()
            print("Database initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            conn.close()

# Client CRUD operations
class ClientDB:
    @staticmethod
    def add_client(name, phone, email, subscription_type, subscription_start, subscription_end):
        """Add new client"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO clients (name, phone, email, subscription_type, subscription_start, subscription_end)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (name, phone, email, subscription_type, subscription_start, subscription_end))
                conn.commit()
                client_id = cursor.lastrowid
                return client_id
            except Exception as e:
                print(f"Error adding client: {e}")
                return None
            finally:
                conn.close()
    
    @staticmethod
    def get_all_clients():
        """Get all clients"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM clients ORDER BY name")
                clients = cursor.fetchall()
                return clients
            except Exception as e:
                print(f"Error fetching clients: {e}")
                return []
            finally:
                conn.close()
    
    @staticmethod
    def update_client(client_id, name, phone, email, subscription_type, subscription_start, subscription_end, status):
        """Update client information"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                UPDATE clients 
                SET name=?, phone=?, email=?, subscription_type=?, 
                    subscription_start=?, subscription_end=?, status=?
                WHERE id=?
                """, (name, phone, email, subscription_type, subscription_start, subscription_end, status, client_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error updating client: {e}")
                return False
            finally:
                conn.close()
    
    @staticmethod
    def delete_client(client_id):
        """Delete client"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error deleting client: {e}")
                return False
            finally:
                conn.close()

# Attendance operations
class AttendanceDB:
    @staticmethod
    def mark_attendance(client_id, status='present'):
        """Mark client attendance"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                today = datetime.now().strftime('%Y-%m-%d')
                check_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute("""
                INSERT INTO attendance (client_id, check_in_time, date, status)
                VALUES (?, ?, ?, ?)
                """, (client_id, check_in_time, today, status))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error marking attendance: {e}")
                return False
            finally:
                conn.close()
    
    @staticmethod
    def get_attendance_by_client(client_id):
        """Get attendance history for a client"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT a.*, c.name FROM attendance a
                JOIN clients c ON a.client_id = c.id
                WHERE a.client_id = ?
                ORDER BY a.check_in_time DESC
                """, (client_id,))
                attendance = cursor.fetchall()
                return attendance
            except Exception as e:
                print(f"Error fetching attendance: {e}")
                return []
            finally:
                conn.close()

# Barcode operations
class BarcodeDB:
    @staticmethod
    def create_barcode(client_id, barcode_data):
        """Create barcode for client"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO barcodes (client_id, barcode_data)
                VALUES (?, ?)
                """, (client_id, barcode_data))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error creating barcode: {e}")
                return False
            finally:
                conn.close()
    
    @staticmethod
    def update_barcode_status(barcode_id, status):
        """Update barcode status (active/inactive)"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                UPDATE barcodes SET status=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
                """, (status, barcode_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error updating barcode status: {e}")
                return False
            finally:
                conn.close()
    
    @staticmethod
    def get_client_barcode(client_id):
        """Get barcode for client"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT b.*, c.name FROM barcodes b
                JOIN clients c ON b.client_id = c.id
                WHERE b.client_id = ?
                """, (client_id,))
                barcode = cursor.fetchone()
                return barcode
            except Exception as e:
                print(f"Error fetching barcode: {e}")
                return None
            finally:
                conn.close()

if __name__ == "__main__":
    init_db()
