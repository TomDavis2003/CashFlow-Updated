from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import datetime

class DelayAmount:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1110x500+220+130")
        self.root.title("Delayed Amounts")  
        self.root.config(bg="white")
        self.root.focus_force()

        self.load_delays()


    def mark_as_paid(self, delay_id):
        con = sqlite3.connect(database=r'imsc.db')
        cur = con.cursor()
        
        # Update delay status
        cur.execute("UPDATE delays SET status='paid' WHERE id=?", (delay_id,))
        
        # Get delay details
        cur.execute("SELECT * FROM delays WHERE id=?", (delay_id,))
        delay = cur.fetchone()
        
        # Record transaction
        cur.execute("""INSERT INTO transactions 
                    (fixed_transaction_id, amount_paid, date_paid, month, year, type)
                    VALUES (?, ?, ?, ?, ?, 'fixed')""",
                   (delay[1], delay[4], datetime.now().date(), delay[2], delay[3]))
        
        con.commit()
        con.close()
        self.load_delays()


if __name__ == "__main__":
    root = Tk()
    obj = DelayAmount(root)
    root.mainloop()