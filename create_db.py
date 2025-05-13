# create_db.py
import sqlite3
import datetime

class DBConnection:
    def __init__(self):
        self.conn = sqlite3.connect('cashflow.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        # Transactions table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            datetime TEXT NOT NULL,
                            description TEXT NOT NULL,
                            amount REAL NOT NULL,
                            type TEXT NOT NULL,
                            category TEXT,
                            month INTEGER,
                            year INTEGER,
                            is_fixed BOOLEAN DEFAULT 0
                            )''')
        
        # Fixed Transactions table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS fixed_transactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            datetime TEXT NOT NULL,
                            description TEXT NOT NULL,
                            amount REAL NOT NULL,
                            type TEXT NOT NULL,
                            fixed_day INTEGER NOT NULL,
                            paid_date TEXT DEFAULT NULL
                            )''')
        self.conn.commit()