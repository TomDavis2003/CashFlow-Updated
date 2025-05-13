from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import datetime
import sqlite3
from datetime import datetime, timedelta
from tkinter import messagebox

class AdvanceAmount:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1110x500+220+130")
        self.root.title("Advance Amounts")
        self.root.config(bg="white")
        self.root.focus_force()

        
    def convert_to_payout(self, advance_id):
        con = sqlite3.connect(database=r'imsc.db')
        cur = con.cursor()
        
        # Update advance status
        cur.execute("UPDATE advances SET status='converted' WHERE id=?", (advance_id,))
        
        # Create payout entry
        cur.execute("INSERT INTO payouts (advance_id, amount, date_paid) VALUES (?, ?, ?)",
                   (advance_id, self.amount, datetime.now().date()))
        
        con.commit()
        con.close()
        self.load_advances()



if __name__ == "__main__":
    root = Tk()
    obj = AdvanceAmount(root)
    root.mainloop()