from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime, date
from create_db import DBConnection  # assumes DBConnection gives you a .cursor and .conn as before

class DelayAmount:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1110x550+220+130")
        self.root.title("Delayed (Pending) Fixed Transactions")
        self.root.config(bg="white")
        self.root.focus_force()

        # Database connection (same as in FixedTransaction)
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
        """
        Builds the “Filter” frame at the very top with:
          • Month combobox: [All, January, ..., December]  
          • Year combobox: [2010..2040]  
          • A “Search” button that re-calls load_data()
        """
        filter_frame = Frame(self.root, bg="white")
        filter_frame.place(x=20, y=10, width=1070, height= 30)

        # Month Label + Combobox
        Label(filter_frame, text="Month:", font=("arial", 12), bg="white").pack(side=LEFT, padx=(0,5))
        month_values = ["All"] + [date(2000, m, 1).strftime("%B") for m in range(1, 13)]
        ttk.Combobox(
            filter_frame,
            textvariable=self.var_search_month,
            values=month_values,
            state="readonly",
            width=12
        ).pack(side=LEFT, padx=(0,15))

        # Year Label + Combobox
        Label(filter_frame, text="Year:", font=("arial", 12), bg="white").pack(side=LEFT, padx=(0,5))
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
        """
        Builds the Treeview to show:
            [ID, Fixed ID, Description, Amount, Type, Category, Frequency, Due Day, Due Date, Month, Year, Status]
        """
        tree_frame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        tree_frame.place(x=20, y=50, width=1070, height=430)

        scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=(
                "fixed_id", "description", "amount", "type", "category",
                "frequency", "due_day", "due_date", "month", "year", "status"
            ),
            yscrollcommand=scroll_y.set
        )
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_y.config(command=self.tree.yview)

        columns = [
            ("#0",        "ID",           50,  'center'),
            ("fixed_id",  "Fixed ID",     80,  'center'),
            ("description","Description", 200, 'w'),
            ("amount",    "Amount",       80,  'e'),
            ("type",      "Type",         80,  'center'),
            ("category",  "Category",    100,  'w'),
            ("frequency", "Frequency",   100,  'w'),
            ("due_day",   "Due Day",      70,  'center'),
            ("due_date",  "Due Date",    100,  'center'),
            ("month",     "Month",        70,  'center'),
            ("year",      "Year",         70,  'center'),
            ("status",    "Status",      100,  'center'),
        ]

        for col in columns:
            self.tree.heading(col[0], text=col[1])
            self.tree.column(col[0], width=col[2], anchor=col[3])

        self.tree.pack(fill=BOTH, expand=1)

    def create_refresh_button(self):
        """
        Adds a “Refresh” button below the Treeview to re-call load_data().
        """
        btn_refresh = Button(
            self.root,
            text="Refresh",
            bg="lightblue",
            fg="black",
            font=("arial", 12, "bold"),
            command=self.load_data
        )
        btn_refresh.place(x=490, y=500, width=130, height=30)

    def load_data(self):
        """
        Fetch all payment_status rows where status='Pending', join with fixed_transactions,
        apply month/year filters (if not “All”), and display them in the Treeview.
        """
        self.tree.delete(*self.tree.get_children())

        # Base query
        query = """
            SELECT 
                ps.rowid   AS psid,
                ft.id      AS fixed_id,
                ft.description,
                ft.amount,
                ft.type,
                ft.category,
                ft.frequency,
                ft.due_day,
                ps.month,
                ps.year,
                ps.status
            FROM fixed_transactions ft
            JOIN payment_status     ps ON ft.id = ps.fixed_id
            WHERE ps.status = 'Pending'
        """
        params = []

        # Apply Month filter if not “All”
        sel_month = self.var_search_month.get()
        if sel_month and sel_month != "All":
            try:
                month_num = datetime.strptime(sel_month, "%B").month
                query += " AND ps.month = ?"
                params.append(month_num)
            except ValueError:
                messagebox.showerror("Error", "Invalid month selection")
                return

        # Apply Year filter if any
        sel_year = self.var_search_year.get()
        if sel_year:
            query += " AND ps.year = ?"
            params.append(sel_year)

        # Final ordering
        query += " ORDER BY ps.year, ps.month, ft.id"

        try:
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()

            for row in rows:
                psid, fixed_id, desc, amount, typ, cat, freq, due_day, mon, yr, status = row

                # Construct a proper "Due Date" from (year, month, due_day)
                try:
                    due_date_obj = date(int(yr), int(mon), int(due_day))
                    due_date_str = due_date_obj.strftime("%d-%b-%Y")
                except ValueError:
                    due_date_str = "Invalid Date"

                # Insert into Treeview
                self.tree.insert(
                    "",
                    "end",
                    text=psid,
                    values=(
                        fixed_id,
                        desc,
                        f"{amount:.2f}",
                        typ,
                        cat,
                        freq,
                        due_day,
                        due_date_str,
                        mon,
                        yr,
                        status
                    )
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load pending transactions:\n{e}")


if __name__ == "__main__":
    root = Tk()
    obj = DelayAmount(root)
    root.mainloop()
