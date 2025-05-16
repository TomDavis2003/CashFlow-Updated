# create_db.py
import sqlite3

class DBConnection:
    def __init__(self):
        self.conn = sqlite3.connect('cashflow.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        # Fixed Transactions Table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS fixed_transactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            entry_date TEXT NOT NULL,
                            description TEXT NOT NULL,
                            amount REAL NOT NULL,
                            type TEXT NOT NULL,
                            category TEXT,
                            frequency TEXT NOT NULL,
                            due_day INTEGER NOT NULL,
                            next_due_date TEXT NOT NULL
                            )''')

        # Payment Status Table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS payment_status (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            fixed_id INTEGER NOT NULL,
                            month INTEGER NOT NULL,
                            year INTEGER NOT NULL,
                            status TEXT DEFAULT 'Pending',
                            paid_date TEXT,
                            FOREIGN KEY(fixed_id) REFERENCES fixed_transactions(id)
                            )''')

        # Main Transactions Table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            datetime TEXT NOT NULL,
                            description TEXT NOT NULL,
                            amount REAL NOT NULL,
                            type TEXT NOT NULL,
                            category TEXT,
                            month INTEGER,
                            year INTEGER,
                            fixed_id INTEGER,
                            FOREIGN KEY(fixed_id) REFERENCES fixed_transactions(id)
                            )''')
        self.conn.commit()