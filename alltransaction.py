# alltransaction.py
from tkinter import *
from tkinter import ttk, messagebox
import datetime
import calendar
import sqlite3
from datetime import datetime, timedelta


class AllTransaction:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1350x700+0+0")
        self.root.title("All Transactions")
        self.root.config(bg="white")
        self.root.focus_force()

        self.load_transactions()

    def load_transactions(self):
        con = sqlite3.connect(database=r'imsc.db')
        cur = con.cursor()
        
        cur.execute("""SELECT t.*, ft.description 
                     FROM transactions t
                     LEFT JOIN fixed_transactions ft ON t.fixed_transaction_id = ft.id""")
        rows = cur.fetchall()
        
        # Populate transactions in GUI table
        for row in rows:
            self.treeview.insert('', 'end', values=row)
        
        con.close()
        

if __name__ == "__main__":
    root = Tk()
    obj = AllTransaction(root)
    root.mainloop()