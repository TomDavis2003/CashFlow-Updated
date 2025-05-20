# alltransaction.py
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import calendar

class AllTransaction:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1350x700+0+0")
        self.root.title("All Transactions")
        self.root.config(bg="white")
        self.root.focus_force()

        # Database connection
        self.conn = sqlite3.connect('cashflow.db')
        self.cursor = self.conn.cursor()

        # Filter variables
        self.var_search_month = StringVar(value="All")
        self.var_search_year  = StringVar(value=str(datetime.now().year))

        # Balance variable
        self.balance_var = StringVar()

        self.create_filter_section()
        self.create_balance_label()
        self.create_treeview()
        self.create_refresh_button()
        self.load_data()

    def create_filter_section(self):
        filter_frame = Frame(self.root, bg="white")
        filter_frame.place(x=20, y=10, width=1310, height=40)

        Label(filter_frame, text="Month:", font=("arial", 12), bg="white")\
            .pack(side=LEFT, padx=(10, 5))
        month_values = ["All"] + [calendar.month_name[m] for m in range(1, 13)]
        ttk.Combobox(
            filter_frame, textvariable=self.var_search_month,
            values=month_values, state="readonly", width=12
        ).pack(side=LEFT, padx=(0, 15))

        Label(filter_frame, text="Year:", font=("arial", 12), bg="white")\
            .pack(side=LEFT, padx=(0, 5))
        years = [str(y) for y in range(2010, 2041)]
        ttk.Combobox(
            filter_frame, textvariable=self.var_search_year,
            values=years, state="readonly", width=8
        ).pack(side=LEFT, padx=(0, 15))

        Button(
            filter_frame, text="Search", command=self.load_data,
            bg="lightblue", font=("arial", 12, "bold")
        ).pack(side=LEFT)

    def create_balance_label(self):
        # Display current balance just below the filter bar
        lbl_frame = Frame(self.root, bg="white")
        lbl_frame.place(x=20, y=50, width=1310, height=30)
        Label(
            lbl_frame,
            textvariable=self.balance_var,
            font=("arial", 12, "bold"),
            bg="white",
            fg="darkgreen"
        ).pack(anchor="w", padx=10)

    def create_treeview(self):
        tree_frame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        tree_frame.place(x=20, y=80, width=1310, height=580)

        scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("datetime", "description", "amount", "tran_type", "category", "source"),
            show="headings",
            yscrollcommand=scroll_y.set
        )
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_y.config(command=self.tree.yview)

        columns = [
            ("datetime",    "Date/Time",    200,  'center'),
            ("description", "Description",  400,  'w'),
            ("amount",      "Amount",       100,  'e'),
            ("tran_type",   "Type",         100,  'center'),
            ("category",    "Category",     150,  'w'),
            ("source",      "Source",       100,  'center'),
        ]

        for col_id, heading, width, anchor in columns:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor=anchor)

        self.tree.pack(fill=BOTH, expand=1)

    def create_refresh_button(self):
        Button(
            self.root, text="Refresh", bg="lightblue", fg="black",
            font=("arial", 12, "bold"), command=self.load_data
        ).place(x=620, y=670, width=150, height=30)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())

        base_transactions_sql = """
            SELECT
                t.datetime,
                t.description,
                t.amount,
                t.type,
                t.category,
                CASE WHEN t.fixed_id IS NOT NULL THEN 'Fixed' ELSE 'One-Time' END AS source,
                strftime('%m', t.datetime) AS mon,
                strftime('%Y', t.datetime) AS yr
            FROM transactions t
            WHERE 1 = 1
        """

        advances_sql = """
            SELECT
                a.repaid_date,
                a.description,
                a.amount,
                'Advance' AS type,
                ''       AS category,
                'Advance' AS source,
                strftime('%m', a.repaid_date) AS mon,
                strftime('%Y', a.repaid_date) AS yr
            FROM advances a
            WHERE a.status = 'Paid'
        """

        loans_sql = """
            SELECT
                l.repaid_date,
                l.description,
                l.amount,
                'Loan'   AS type,
                ''       AS category,
                'Loan'   AS source,
                strftime('%m', l.repaid_date) AS mon,
                strftime('%Y', l.repaid_date) AS yr
            FROM loans l
            WHERE l.status = 'Repaid'
        """

        # Filters
        conds = []
        params = []

        month_val = self.var_search_month.get()
        if month_val and month_val != "All":
            try:
                month_num = datetime.strptime(month_val, "%B").month
                conds.append("mon = ?")
                params.append(f"{month_num:02d}")
            except ValueError:
                messagebox.showerror("Error", "Invalid month selected")
                return

        year_val = self.var_search_year.get()
        if year_val:
            conds.append("yr = ?")
            params.append(year_val)

        if conds:
            where_clause = " AND " + " AND ".join(conds)
            base_transactions_sql += where_clause.replace(
                "mon", "strftime('%m', t.datetime)"
            ).replace(
                "yr", "strftime('%Y', t.datetime)"
            )
            advances_sql += where_clause.replace(
                "mon", "strftime('%m', a.repaid_date)"
            ).replace(
                "yr", "strftime('%Y', a.repaid_date)"
            )
            loans_sql += where_clause.replace(
                "mon", "strftime('%m', l.repaid_date)"
            ).replace(
                "yr", "strftime('%Y', l.repaid_date)"
            )

        final_sql = f"""
            {base_transactions_sql}
            UNION ALL
            {advances_sql}
            UNION ALL
            {loans_sql}
            ORDER BY datetime DESC
        """

        try:
            # Execute with the same params for each sub-query
            self.cursor.execute(final_sql, params * 3)
            rows = self.cursor.fetchall()

            for row in rows:
                datetime_str, desc, amt, tran_type, category, source, *_ = row
                try:
                    dt_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                    display_dt = dt_obj.strftime("%d-%b-%Y %H:%M")
                except ValueError:
                    display_dt = datetime_str

                self.tree.insert("", "end", values=(
                    display_dt,
                    desc,
                    f"{amt:.2f}",
                    tran_type,
                    category,
                    source
                ))

            # After loading all rows, update balance label
            self.update_balance()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions:\n{e}")

    def update_balance(self):
        """
        Calculate the current balance (Income - Expense) and set the label.
        """
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
        except Exception as e:
            self.balance_var.set("Current Balance: Error")

if __name__ == "__main__":
    root = Tk()
    AllTransaction(root)
    root.mainloop()