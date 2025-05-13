from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import datetime

class FixedTransaction:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1110x500+220+130")
        self.root.title("Fixed Transactions")
        self.root.config(bg="white")
        self.root.focus_force()
        
        self.check_delays()  # Check for pending delays when window opens

    def check_delays(self):
            """Check for unpaid fixed transactions that are past due"""
            current_date = datetime.now()
            current_month = current_date.month
            current_year = current_date.year
            
            con = sqlite3.connect(database=r'imsc.db')
            cur = con.cursor()
            
            # Get all active fixed transactions
            cur.execute("SELECT * FROM fixed_transactions WHERE is_active=1")
            fixed_transactions = cur.fetchall()
            
            for ft in fixed_transactions:
                ft_id, desc, amount, due_day, category, is_active = ft
                
                # Calculate due date for current month
                try:
                    due_date = datetime(current_year, current_month, due_day)
                except ValueError:
                    # Handle invalid day for month (e.g., February 30)
                    due_date = datetime(current_year, current_month + 1, 1) - timedelta(days=1)
                    due_day = due_date.day
                    due_date = datetime(current_year, current_month, due_day)
                
                # Check if payment is late
                if current_date > due_date:
                    # Check if payment exists for this month/year
                    cur.execute("""SELECT * FROM transactions 
                                WHERE fixed_transaction_id=? 
                                AND month=? 
                                AND year=?""", (ft_id, current_month, current_year))
                    if not cur.fetchone():
                        # Add to delays if not already exists
                        cur.execute("""INSERT INTO delays (fixed_transaction_id, month, year, due_date)
                                    SELECT ?, ?, ?, ?
                                    WHERE NOT EXISTS (
                                        SELECT 1 FROM delays 
                                        WHERE fixed_transaction_id=? 
                                        AND month=? 
                                        AND year=?
                                    )""", (ft_id, current_month, current_year, due_date, ft_id, current_month, current_year))
            con.commit()
            con.close()


if __name__ == "__main__":
    root = Tk()
    obj = FixedTransaction(root)
    root.mainloop()