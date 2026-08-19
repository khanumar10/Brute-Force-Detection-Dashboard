import sqlite3
from datetime import datetime

DB_NAME = "security_logs.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            username TEXT NOT NULL,
            status TEXT NOT NULL,          -- 'SUCCESS' or 'FAILED'
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            target_username TEXT,
            failed_count INTEGER NOT NULL,
            first_attempt DATETIME,
            last_attempt DATETIME,
            severity TEXT DEFAULT 'HIGH',
            detected_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("[+] Database and tables initialized successfully.")

if __name__ == "__main__":
    init_db()
