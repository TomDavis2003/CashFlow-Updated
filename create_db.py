def create_db():
    con = sqlite3.connect(database=r'imsc.db')
    cur = con.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        date TEXT,
        type TEXT,
        income REAL,
        expense REAL,
        loan REAL,
        month TEXT,
        year TEXT
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value REAL
    )
    """)
    
    # Set initial balance if not exists
    cur.execute("""
    INSERT OR IGNORE INTO settings (key, value) 
    VALUES ('initial_balance', 0)
    """)
    
    con.commit()
    con.close()