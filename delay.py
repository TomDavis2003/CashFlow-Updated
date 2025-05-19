from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime, date
from create_db import DBConnection  # assumes DBConnection provides .cursor and .conn

class DelayAmount:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1110x600+220+130")
        self.root.title("Delayed (Pending) Fixed, Loan & Advance Transactions")
        self.root.config(bg="white")
        self.root.focus_force()

        # Database connection
        self.db = DBConnection()
        self.cursor = self.db.cursor

        # Variables for filtering
        self.var_search_month = StringVar(value="All")
        self.var_search_year  = StringVar(value=str(datetime.now().year))

        # Build UI
        self.create_filter_section()
        self.create_treeview()
        self.create_refresh_button()

        # Initial load
        self.load_data()

    def create_filter_section(self):
        filter_frame = Frame(self.root, bg="white")
        filter_frame.place(x=20, y=10, width=1070, height=30)

        # Month Label + Combobox
        Label(filter_frame, text="Month:", font=("arial", 12), bg="white")\
            .pack(side=LEFT, padx=(0,5))
        month_values = ["All"] + [date(2000, m, 1).strftime("%B") for m in range(1, 13)]
        ttk.Combobox(
            filter_frame,
            textvariable=self.var_search_month,
            values=month_values,
            state="readonly",
            width=12
        ).pack(side=LEFT, padx=(0,15))

        # Year Label + Combobox
        Label(filter_frame, text="Year:", font=("arial", 12), bg="white")\
            .pack(side=LEFT, padx=(0,5))
        years = [str(y) for y in range(2010, 2041)]
        ttk.Combobox(
            filter_frame,
            textvariable=self.var_search_year,
            values=years,
            state="readonly",
            width=8
        ).pack(side=LEFT, padx=(0,15))

        # Search Button
        Button(
            filter_frame,
            text="Search",
            command=self.load_data,
            bg="lightblue",
            fg="black",
            font=("arial", 12, "bold")
        ).pack(side=LEFT)

    def create_treeview(self):
        tree_frame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        tree_frame.place(x=20, y=50, width=1070, height=480)

        scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=(
                "source",      # "Fixed", "Loan" or "Advance"
                "assoc_id",    # payment_status.rowid, loans.id, or advances.id
                "description",
                "amount",
                "tran_type",   # "Income"/"Expense"/"Loan"/"Advance"
                "category",    # for fixed: its category; for others: blank
                "frequency",   # for fixed: its frequency; otherwise blank
                "due_day",     # for fixed: its day-of-month; blank for loans/advances
                "date_field",  # due_date or advance_date (formatted YYYY-MM-DD)
                "month",       # numeric month of that date_field
                "year",        # numeric year of that date_field
                "status"       # "Pending"/"Paid"/"Repaid"
            ),
            show="headings",
            yscrollcommand=scroll_y.set
        )
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_y.config(command=self.tree.yview)

        columns = [
            ("source",      "Source",        80,  'center'),
            ("assoc_id",    "ID",            80,  'center'),
            ("description", "Description",  200,  'w'),
            ("amount",      "Amount",        80,  'e'),
            ("tran_type",   "Type",          80,  'center'),
            ("category",    "Category",     100,  'w'),
            ("frequency",   "Frequency",    100,  'w'),
            ("due_day",     "Due Day",       70,  'center'),
            ("date_field",  "Date",         100,  'center'),
            ("month",       "Month",         70,  'center'),
            ("year",        "Year",          70,  'center'),
            ("status",      "Status",       100,  'center'),
        ]

        for col_id, heading, width, anchor in columns:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor=anchor)

        self.tree.pack(fill=BOTH, expand=1)

    def create_refresh_button(self):
        btn_refresh = Button(
            self.root,
            text="Refresh",
            bg="lightblue",
            fg="black",
            font=("arial", 12, "bold"),
            command=self.load_data
        )
        btn_refresh.place(x=490, y=540, width=130, height=30)

    def load_data(self):
        # Clear existing rows
        self.tree.delete(*self.tree.get_children())

        #
        # 1) Fixed installments that are pending & due within next 7 days
        #
        fixed_sql = """
            SELECT
                'Fixed'                                AS source,
                ps.rowid                              AS assoc_id,
                ft.description                        AS description,
                COALESCE(ps.amount, ft.amount)        AS amount,
                ft.type                                AS tran_type,
                ft.category                            AS category,
                ft.frequency                           AS frequency,
                ft.due_day                             AS due_day,
                printf('%04d-%02d-%02d', 
                       ps.year, ps.month, ft.due_day)   AS date_field,
                ps.month                               AS month,
                ps.year                                AS year,
                ps.status                              AS status
            FROM fixed_transactions ft
            JOIN payment_status       ps 
              ON ft.id = ps.fixed_id
            WHERE ps.status = 'Pending'
              AND date( printf('%04d-%02d-%02d', ps.year, ps.month, ft.due_day) )
                  BETWEEN date('now') AND date('now','+7 days')
        """

        #
        # 2) Loans that are pending & due within next 7 days
        #
        loan_sql = """
            SELECT
                'Loan'                                AS source,
                l.id                                  AS assoc_id,
                l.description                         AS description,
                l.amount                              AS amount,
                'Loan'                                AS tran_type,
                ''                                    AS category,
                ''                                    AS frequency,
                ''                                    AS due_day,
                l.due_date                            AS date_field,
                strftime('%m', l.due_date)           AS month,
                strftime('%Y', l.due_date)           AS year,
                l.status                              AS status
            FROM loans l
            WHERE l.status = 'Pending'
              AND date(l.due_date) 
                  BETWEEN date('now') AND date('now','+7 days')
        """

        #
        # 3) Advances that are pending & "advance_date" within next 7 days
        #
        advance_sql = """
            SELECT
                'Advance'                             AS source,
                a.id                                  AS assoc_id,
                a.description                         AS description,
                a.amount                              AS amount,
                'Advance'                             AS tran_type,
                ''                                    AS category,
                ''                                    AS frequency,
                ''                                    AS due_day,
                a.advance_date                        AS date_field,
                strftime('%m', a.advance_date)       AS month,
                strftime('%Y', a.advance_date)       AS year,
                a.status                              AS status
            FROM advances a
            WHERE a.status = 'Pending'
              AND date(a.advance_date)
                  BETWEEN date('now') AND date('now','+7 days')
        """

        #
        # Now build the month/year filters (if the user selected something other than "All")
        #
        conds  = []
        params = []

        # If the user picked a specific month (e.g. "May"):
        sel_month = self.var_search_month.get()
        if sel_month and sel_month != "All":
            try:
                month_num = datetime.strptime(sel_month, "%B").month
                conds.append("month = ?")
                params.append(f"{month_num:02d}")
            except ValueError:
                messagebox.showerror("Error", "Invalid month selection")
                return

        # If the user picked a specific year (e.g. "2025"):
        sel_year = self.var_search_year.get()
        if sel_year:
            conds.append("year = ?")
            params.append(sel_year)

        # If we have at least one filter condition, append it to each sub‐query
        if conds:
            filter_clause = " AND " + " AND ".join(conds)
            fixed_sql   += filter_clause
            loan_sql    += filter_clause
            advance_sql += filter_clause

        #
        # Finally, UNION ALL the three sub‐queries and order by date_field ascending
        #
        final_sql = f"""
            {fixed_sql}
            UNION ALL
            {loan_sql}
            UNION ALL
            {advance_sql}
            ORDER BY date_field ASC
        """

        try:
            # Execute with the same params for each sub‐query:
            # (because each SELECT uses "month = ?" and "year = ?" if present)
            self.cursor.execute(final_sql, params * 3)
            rows = self.cursor.fetchall()

            for row in rows:
                (
                    source,
                    assoc_id,
                    desc,
                    amt,
                    tran_type,
                    category,
                    frequency,
                    due_day,
                    date_str,
                    mon,
                    yr,
                    status
                ) = row

                # Convert date_str (always stored as "YYYY-MM-DD") to "DD-MMM-YYYY"
                try:
                    dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    display_date = dt_obj.strftime("%d-%b-%Y")
                except:
                    display_date = date_str

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        source,
                        assoc_id,
                        desc,
                        f"{amt:.2f}",
                        tran_type,
                        category,
                        frequency,
                        due_day,
                        display_date,
                        mon,
                        yr,
                        status
                    )
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load delayed transactions:\n{e}")


# To test as a standalone window:
if __name__ == "__main__":
    root = Tk()
    app = DelayAmount(root)
    root.mainloop()
