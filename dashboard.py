# cashflow_main_ui.py (fully updated with month/year and transaction type filters, and ORDER BY fix)

from tkinter import *
import sqlite3
import datetime
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
from alltransaction import AllTransaction
from advanceamount import AdvanceAmount
from delay import DelayAmount
from payout import PayoutAmount
from fixedtransaction import FixedTransaction
from onetime import OneTime
from loan import LoanAmount

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
        self.lbl_clock = Label(self.root, font=("times new roman", 15, "bold"),
                               bg="#e50000", fg="white")
        self.update_clock()

        # Variables for display
        self.balance_var = StringVar()
        self.pending_var = StringVar()
        self.shortage_var = StringVar()

        # Filter variables
        self.filter_source = StringVar(value="All")
        self.filter_status = StringVar(value="Pending")
        self.filter_month = StringVar(value="All")
        self.filter_year = StringVar(value="All")
        self.filter_type = StringVar(value="All")

        # Dashboard Info Labels
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
            ("Pendings", self.delay_amount),
            ("Payouts", self.payout_amount),
            ("One Time", self.one_time),
            ("Fixed Transactions", self.fixed_transaction),
            ("Loan Amounts", self.loan)
        ]

        for label, cmd in menu_buttons:
            Button(self.LeftMenu, text=label, command=cmd, font=("times new roman", 15, "bold"),
                   bg="white", bd=3, fg="black", cursor="hand2").pack(side=TOP, fill=X)

        # Pending Transactions Treeview and Filters
        self.create_pending_treeview()

        # Footer
        Label(self.root, text="CFMS - CashFlow Management System | Developed by Loanitol \n"
                              "For any technical issue Contact: 94466*****",
              font=("times new roman", 15, "bold"), bg="#e50000", fg="white").pack(side=BOTTOM, fill=X)

        # Initial Updates
        self.update_all()

    def update_clock(self):
        now = datetime.datetime.now()
        clock_text = now.strftime("Welcome to CashFlow Management System\t\t Date: %d-%m-%Y\t\t Time: %H:%M:%S")
        self.lbl_clock.config(text=clock_text)
        self.lbl_clock.place(x=0, y=70, relwidth=1, height=30)
        self.root.after(1000, self.update_clock)

    def create_pending_treeview(self):
        # Filter Frame
        filter_frame = Frame(self.root, bg="white")
        filter_frame.place(x=200, y=130, width=1150, height=60)

        # Source Filter
        Label(filter_frame, text="Filter by Source:", font=("arial", 12), bg="white").place(x=10, y=5)
        source_combo = ttk.Combobox(filter_frame, textvariable=self.filter_source, 
                                  values=["All", "Fixed", "Loan", "Advance"],
                                  state="readonly", width=12)
        source_combo.place(x=120, y=5)
        source_combo.bind("<<ComboboxSelected>>", lambda e: self.load_pending_transactions())

        # Status Filter
        Label(filter_frame, text="Status:", font=("arial", 12), bg="white").place(x=260, y=5)
        status_combo = ttk.Combobox(filter_frame, textvariable=self.filter_status,
                                  values=["All", "Pending", "Paid"],
                                  state="readonly", width=12)
        status_combo.place(x=310, y=5)
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.load_pending_transactions())

        # Month Filter
        Label(filter_frame, text="Month:", font=("arial", 12), bg="white").place(x=450, y=5)
        month_values = ["All"] + [f"{m:02d}" for m in range(1, 13)]
        month_combo = ttk.Combobox(filter_frame, textvariable=self.filter_month,
                                   values=month_values, state="readonly", width=8)
        month_combo.place(x=510, y=5)
        month_combo.bind("<<ComboboxSelected>>", lambda e: self.load_pending_transactions())

        # Year Filter
        Label(filter_frame, text="Year:", font=("arial", 12), bg="white").place(x=610, y=5)
        year_values = ["All"] + [str(y) for y in range(2020, 2031)]
        year_combo = ttk.Combobox(filter_frame, textvariable=self.filter_year,
                                  values=year_values, state="readonly", width=8)
        year_combo.place(x=650, y=5)
        year_combo.bind("<<ComboboxSelected>>", lambda e: self.load_pending_transactions())

        # Transaction Type Filter
        Label(filter_frame, text="Trans Type:", font=("arial", 12), bg="white").place(x=750, y=5)
        type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type,
                                  values=["All", "Incoming", "Expense"],
                                  state="readonly", width=10)
        type_combo.place(x=840, y=5)
        type_combo.bind("<<ComboboxSelected>>", lambda e: self.load_pending_transactions())

        # Treeview Frame
        tree_frame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        tree_frame.place(x=200, y=190, width=1150, height=510)

        scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
        self.pending_tree = ttk.Treeview(
            tree_frame,
            columns=("source", "description", "amount", "date", "status"),
            show="headings",
            yscrollcommand=scroll_y.set
        )
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_y.config(command=self.pending_tree.yview)

        columns = [
            ("source", "Source", 100),
            ("description", "Description", 400),
            ("amount", "Amount", 150),
            ("date", "Due Date", 150),
            ("status", "Status", 100),
        ]

        for col_id, heading, width in columns:
            self.pending_tree.heading(col_id, text=heading)
            self.pending_tree.column(col_id, width=width, 
                                    anchor='center' if col_id == 'source' else 'w')

        self.pending_tree.pack(fill=BOTH, expand=1)

    def update_balance_and_pending_info(self):
        try:
            # Current Balance Calculation
            self.cursor.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END), 0)
                FROM transactions
            """)
            income_sum, expense_sum = self.cursor.fetchone()
            balance = income_sum - expense_sum
            self.balance_var.set(f"Current Balance: ₹{balance:.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"Balance calculation failed: {str(e)}")
            self.balance_var.set("Current Balance: Error")
            balance = 0

        try:
            # Pending Amounts Calculation
            self.cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM loans WHERE status = 'Pending'")
            pending_loans = self.cursor.fetchone()[0] or 0

            self.cursor.execute("""
                SELECT COALESCE(SUM(ft.amount), 0)
                FROM payment_status ps
                JOIN fixed_transactions ft ON ps.fixed_id = ft.id
                WHERE ps.status = 'Pending'
                  AND date(printf('%04d-%02d-%02d', ps.year, ps.month, ft.due_day))
                  BETWEEN date('now') AND date('now','+7 days')
            """)
            pending_fixed_due = self.cursor.fetchone()[0] or 0

            self.cursor.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM advances
                WHERE status = 'Pending'
                  AND date(advance_date) BETWEEN date('now') AND date('now','+7 days')
            """)
            pending_advances_due = self.cursor.fetchone()[0] or 0

            total_pending = pending_loans + pending_fixed_due + pending_advances_due
            self.pending_var.set(
                f"Pending Loans: ₹{pending_loans:.2f} | Fixed Due: ₹{pending_fixed_due:.2f} | "
                f"Advances Due: ₹{pending_advances_due:.2f} | Total: ₹{total_pending:.2f}"
            )

            shortage = total_pending - balance
            self.shortage_var.set(f"Shortage: ₹{shortage:.2f}" if shortage > 0 else "Shortage: ₹0.00")

        except Exception as e:
            messagebox.showerror("Error", f"Pending calculation failed: {str(e)}")
            self.pending_var.set("Pending information unavailable")

    def load_pending_transactions(self):
        self.pending_tree.delete(*self.pending_tree.get_children())
        try:
            # Retrieve filter values
            source_filter = self.filter_source.get()
            status_filter = self.filter_status.get()
            month_filter = self.filter_month.get()
            year_filter = self.filter_year.get()
            type_filter = self.filter_type.get()

            queries = []

            # Fixed Transactions (Expense)
            if source_filter in ["All", "Fixed"] and type_filter in ["All", "Expense"]:
                fixed_query = """
                    SELECT 'Fixed' AS source,
                           ft.description,
                           ft.amount,
                           printf('%04d-%02d-%02d', ps.year, ps.month, ft.due_day) AS due_date,
                           ps.status
                    FROM fixed_transactions ft
                    JOIN payment_status ps ON ft.id = ps.fixed_id
                    WHERE 1=1
                """
                if status_filter != "All":
                    fixed_query += f" AND ps.status = '{status_filter}'"
                if month_filter != "All":
                    # Filter by month from due_date
                    fixed_query += f" AND strftime('%m', printf('%04d-%02d-%02d', ps.year, ps.month, ft.due_day)) = '{month_filter}'"
                if year_filter != "All":
                    fixed_query += f" AND strftime('%Y', printf('%04d-%02d-%02d', ps.year, ps.month, ft.due_day)) = '{year_filter}'"
                queries.append(fixed_query)

            # Loans (Expense)
            if source_filter in ["All", "Loan"] and type_filter in ["All", "Expense"]:
                loan_query = """
                    SELECT 'Loan' AS source,
                           description,
                           amount,
                           due_date,
                           status
                    FROM loans
                    WHERE 1=1
                """
                if status_filter != "All":
                    loan_query += f" AND status = '{status_filter}'"
                if month_filter != "All":
                    loan_query += f" AND strftime('%m', due_date) = '{month_filter}'"
                if year_filter != "All":
                    loan_query += f" AND strftime('%Y', due_date) = '{year_filter}'"
                queries.append(loan_query)

            # Advances (Incoming)
            if source_filter in ["All", "Advance"] and type_filter in ["All", "Incoming"]:
                advance_query = """
                    SELECT 'Advance' AS source,
                           description,
                           amount,
                           advance_date AS due_date,
                           status
                    FROM advances
                    WHERE 1=1
                """
                if status_filter != "All":
                    advance_query += f" AND status = '{status_filter}'"
                if month_filter != "All":
                    advance_query += f" AND strftime('%m', advance_date) = '{month_filter}'"
                if year_filter != "All":
                    advance_query += f" AND strftime('%Y', advance_date) = '{year_filter}'"
                queries.append(advance_query)

            if not queries:
                return

            # Combine queries with UNION ALL and order by due_date (YYYY-MM-DD format works lexically)
            final_query = " UNION ALL ".join(queries) + " ORDER BY due_date ASC"

            self.cursor.execute(final_query)
            transactions = self.cursor.fetchall()

            for tran in transactions:
                source, desc, amount, due_date, status = tran
                try:
                    formatted_date = datetime.datetime.strptime(due_date, "%Y-%m-%d").strftime("%d-%b-%Y")
                except:
                    formatted_date = due_date
                self.pending_tree.insert("", "end", values=(
                    source,
                    desc,
                    f"₹{float(amount):.2f}",
                    formatted_date,
                    status
                ))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions: {str(e)}")

    def update_all(self):
        self.update_balance_and_pending_info()
        self.load_pending_transactions()

    def create_child_window(self, window_class):
        top = Toplevel(self.root)
        window_class(top)
        top.bind("<Destroy>", lambda e: self.update_all())

    # Menu Actions
    def all_transaction(self):
        self.create_child_window(AllTransaction)

    def advance_amount(self):
        self.create_child_window(AdvanceAmount)

    def delay_amount(self):
        self.create_child_window(DelayAmount)

    def payout_amount(self):
        self.create_child_window(PayoutAmount)

    def one_time(self):
        self.create_child_window(OneTime)

    def fixed_transaction(self):
        self.create_child_window(FixedTransaction)

    def loan(self):
        self.create_child_window(LoanAmount)

if __name__ == "__main__":
    root = Tk()
    obj = IMS(root)
    root.mainloop()