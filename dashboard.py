# cashflow_main_ui.py

from tkinter import *
import sqlite3
import datetime
from PIL import Image, ImageTk
from alltransaction import AllTransaction
from advanceamount import AdvanceAmount
from delay import DelayAmount
from payout import PayoutAmount
from fixedtransaction import FixedTransaction
from onetime import OneTime
from loan import LoanAmount
from tkinter import messagebox

class IMS:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1350x700+0+0")
        self.root.title("CashFlow Management System")
        self.root.config(bg="white")

        # Database connection
        self.conn = sqlite3.connect('cashflow.db')
        self.cursor = self.conn.cursor()

        # Title
        self.icon_title = PhotoImage(file=r"images\\logo.png")
        title = Label(self.root, text="CashFlow Management System", image=self.icon_title, compound=LEFT,
                      font=("times new roman", 40, "bold"), bg="white", fg="#e50000", anchor="w", padx=20)
        title.place(x=0, y=0, relwidth=1, height=70)

        # Logout Button
        btn_logout = Button(self.root, text="Logout", font=("times new roman", 15, "bold"),
                            bg="white", fg="black", cursor="hand2")
        btn_logout.place(x=1200, y=10, height=30, width=100)

        # Clock
        now = datetime.datetime.now()
        clock_text = now.strftime("Welcome to CashFlow Management System\t\t Date: %d-%m-%Y\t\t Time: %H:%M:%S")
        self.lbl_clock = Label(self.root, text=clock_text, font=("times new roman", 15, "bold"),
                               bg="#e50000", fg="white")
        self.lbl_clock.place(x=0, y=70, relwidth=1, height=30)

        # Variables for display
        self.balance_var = StringVar()
        self.pending_var = StringVar()
        self.shortage_var = StringVar()

        self.update_balance_and_pending_info()

        lbl_balance = Label(self.root, textvariable=self.balance_var, font=("times new roman", 15, "bold"),
                            bg="white", fg="green")
        lbl_balance.place(x=20, y=100)

        lbl_pending = Label(self.root, textvariable=self.pending_var, font=("times new roman", 15, "bold"),
                            bg="white", fg="orange")
        lbl_pending.place(x=400, y=100)

        lbl_shortage = Label(self.root, textvariable=self.shortage_var, font=("times new roman", 15, "bold"),
                             bg="white", fg="red")
        lbl_shortage.place(x=1150, y=130)


        # Left Menu
        self.MenuLogo = Image.open(r"images\\menu.png")
        self.MenuLogo = self.MenuLogo.resize((100, 100), Image.Resampling.LANCZOS)
        self.MenuLogo = ImageTk.PhotoImage(self.MenuLogo)

        self.LeftMenu = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        self.LeftMenu.place(x=0, y=130, width=200, height=570)

        Label(self.LeftMenu, image=self.MenuLogo).pack(side=TOP, fill=X)
        Label(self.LeftMenu, text="Menu", font=("times new roman", 15), bg="black", fg="white").pack(side=TOP, fill=X)

        menu_buttons = [
            ("All Transactions", self.all_transaction),
            ("Advance Amounts", self.advance_amount),
            ("Delay", self.delay_amount),
            ("Payouts", self.payout_amount),
            ("One Time", self.one_time),
            ("Fixed Transactions", self.fixed_transaction),
            ("Loan Amounts", self.loan)
        ]

        for label, cmd in menu_buttons:
            Button(self.LeftMenu, text=label, command=cmd, font=("times new roman", 15, "bold"),
                   bg="white", bd=3, fg="black", cursor="hand2").pack(side=TOP, fill=X)

        # Footer
        Label(self.root, text="CFMS - CashFlow Management System | Developed by Loanitol \n"
                              "For any technical issue Contact: 94466*****",
              font=("times new roman", 15, "bold"), bg="#e50000", fg="white").pack(side=BOTTOM, fill=X)

    def update_balance_and_pending_info(self):
        try:
            self.cursor.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END), 0)
                FROM transactions
            """)
            income_sum, expense_sum = self.cursor.fetchone()
            balance = income_sum - expense_sum
            self.balance_var.set(f"Current Balance: ₹{balance:.2f}")
        except Exception:
            self.balance_var.set("Current Balance: Error")
            balance = 0

        try:
            self.cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM loans WHERE status = 'Pending'")
            pending_loans = self.cursor.fetchone()[0] or 0
        except Exception:
            pending_loans = 0

        try:
            self.cursor.execute("""
                SELECT COALESCE(SUM(ft.amount), 0)
                FROM payment_status ps
                JOIN fixed_transactions ft ON ps.fixed_id = ft.id
                WHERE ps.status = 'Pending'
                  AND date(printf('%04d-%02d-%02d', ps.year, ps.month, ft.due_day))
                  BETWEEN date('now') AND date('now','+7 days')
            """)
            pending_fixed_due = self.cursor.fetchone()[0] or 0
        except Exception:
            pending_fixed_due = 0

        try:
            self.cursor.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM advances
                WHERE status = 'Pending'
                  AND date(advance_date) BETWEEN date('now') AND date('now','+7 days')
            """)
            pending_advances_due = self.cursor.fetchone()[0] or 0
        except Exception:
            pending_advances_due = 0

        total_pending = pending_loans + pending_fixed_due + pending_advances_due
        self.pending_var.set(
            f"Pending Loans: ₹{pending_loans:.2f}   Fixed Due (7d): ₹{pending_fixed_due:.2f}   "
            f"Advances Due (7d): ₹{pending_advances_due:.2f}   → Total: ₹{total_pending:.2f}"
        )

        shortage = total_pending - balance
        self.shortage_var.set(f"Shortage: ₹{shortage:.2f}" if shortage > 0 else "Shortage: ₹0.00")

    def all_transaction(self):
        Toplevel(self.root).title("All Transactions")
        AllTransaction(Toplevel(self.root))

    def advance_amount(self):
        AdvanceAmount(Toplevel(self.root))

    def delay_amount(self):
        try:
            self.cursor.execute("""
                SELECT COUNT(*) FROM payment_status ps
                JOIN fixed_transactions ft ON ps.fixed_id = ft.id
                WHERE ps.status = 'Pending'
                  AND date(printf('%04d-%02d-%02d', ps.year, ps.month, ft.due_day))
                  BETWEEN date('now') AND date('now','+7 days')
            """)
            pending_fixed_count = self.cursor.fetchone()[0]

            self.cursor.execute("""
                SELECT COUNT(*) FROM loans
                WHERE status = 'Pending'
                  AND date(due_date) BETWEEN date('now') AND date('now','+7 days')
            """)
            pending_loans_count = self.cursor.fetchone()[0]

            self.cursor.execute("""
                SELECT COUNT(*) FROM advances
                WHERE status = 'Pending'
                  AND date(advance_date) BETWEEN date('now') AND date('now','+7 days')
            """)
            pending_advances_count = self.cursor.fetchone()[0]

            total_due = pending_fixed_count + pending_loans_count + pending_advances_count

            msg = (f"Fixed Installments Due ≤ 7 days: {pending_fixed_count}\n"
                   f"Loans Due ≤ 7 days: {pending_loans_count}\n"
                   f"Advances Due ≤ 7 days: {pending_advances_count}\n\n"
                   f"Total Due Soon: {total_due}")
            messagebox.showinfo("Pending Due Soon", msg if total_due > 0 else "No pending transactions due soon.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch pending due counts:\n{e}")

        DelayAmount(Toplevel(self.root))

    def payout_amount(self):
        PayoutAmount(Toplevel(self.root))

    def one_time(self):
        OneTime(Toplevel(self.root))

    def fixed_transaction(self):
        FixedTransaction(Toplevel(self.root))

    def loan(self):
        LoanAmount(Toplevel(self.root))



if __name__ == "__main__":
    root = Tk()
    obj = IMS(root)
    root.mainloop()
