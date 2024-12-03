import sqlite3
import hashlib

class Database:
    def __init__(self, db_name="Grocerify_Database.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        # Users table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            last_login DATETIME
        )
        """)
        
        # Inventory table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            category TEXT NOT NULL,
            date_added TEXT NOT NULL
        )
        """)
        self.conn.commit()

    # Creates a default admin account if one does not exist
    def create_default_admin(self):
        self.cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not self.cursor.fetchone():
            hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
            self.cursor.execute("""
                INSERT INTO users (username, password, email, role)
                VALUES (?, ?, ?, ?)
            """, ('admin', hashed_password, 'admin@example.com', 'admin'))
            self.conn.commit()

    def insert_user(self, username, password, email, role='user'):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("""
            INSERT INTO users (username, password, email, role)
            VALUES (?, ?, ?, ?)
        """, (username, hashed_password, email, role))
        self.conn.commit()

    def check_user_credentials(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("""
            SELECT username, role FROM users 
            WHERE username = ? AND password = ?
        """, (username, hashed_password))
        return self.cursor.fetchone()

    def update_last_login(self, username):
        self.cursor.execute("""
            UPDATE users SET last_login = DATETIME('now')
            WHERE username = ?
        """, (username,))
        self.conn.commit()
    
    def close_connection(self):
        self.conn.close()

Database()

    