from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
from create_db import DBConnection

class PayoutAmount:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1350x700+0+0")
        self.root.title("Payout Amounts")
        self.root.config(bg="white")
        self.root.focus_force()

        # Use the same DBConnection you use elsewhere
        self.db = DBConnection()
        self.cursor = self.db.cursor

        # Variables
        self.var_id          = StringVar()
        self.var_description = StringVar()
        self.var_amount      = StringVar()
        # We force "Type" to always be "Income" for a payout (money coming in)
        self.var_type        = StringVar(value="Income")
        # You can choose a default category or let the user pick from a short list
        self.var_category    = StringVar(value="Payout")

        # Filters for month/year
        self.var_search_month = StringVar()
        self.var_search_year  = StringVar(value=str(datetime.now().year))

        # Build UI
        self.create_input_fields()
        self.create_buttons()
        self.create_treeview()
        self.create_filter_section()
        self.load_data()

    def create_input_fields(self):
        """
        Input form on the left side: Description, Amount, (Type is fixed to "Income"), Category.
        """
        input_frame = Frame(self.root, bd=3, relief=RIDGE, bg="white")
        input_frame.place(x=50, y=50, width=400, height=500)

        Label(
            input_frame,
            text="Payout Details",
            font=("arial", 14, "bold"),
            bg="lightgray"
        ).pack(fill=X)

        fields = [
            ("Description", self.var_description, 50),
            ("Amount",      self.var_amount,      100),
            # Type is fixed, but we still show it in a disabled combobox so user sees "Income"
            ("Type",        self.var_type,        150, ["Income"]),
            ("Category",    self.var_category,    200, ["Payout", "Other"])
        ]

        y_pos = 50
        for field in fields:
            Label(input_frame, text=f"{field[0]}:", bg="white", font=("arial", 12)).place(x=10, y=y_pos)

            if len(field) > 3:
                # Show a read-only combobox containing exactly one (or a short list) of choices
                ttk.Combobox(
                    input_frame,
                    textvariable=field[1],
                    values=field[3],
                    state="readonly",
                    font=("arial", 12)
                ).place(x=120, y=y_pos, width=250)
            else:
                Entry(
                    input_frame,
                    textvariable=field[1],
                    font=("arial", 12),
                    bg="lightyellow"
                ).place(x=120, y=y_pos, width=250)

            y_pos += 50

    def create_buttons(self):
        """
        Save / Update / Clear.
        """
        buttons = [
            ("Save",   "green",  self.save,   50, 560),
            ("Update", "orange", self.update, 160, 560),
            ("Clear",  "gray",   self.clear,  270, 560)
        ]

        for (text, color, cmd, x, y) in buttons:
            Button(
                self.root,
                text=text,
                bg=color,
                fg="white",
                font=("arial", 12, "bold"),
                command=cmd
            ).place(x=x, y=y, width=100, height=30)

    def create_treeview(self):
        """
        Right‐side grid: shows all one‐time transactions where fixed_id IS NULL AND type="Income".
        Columns: ID | Date/Time | Description | Amount | Type | Category
        """
        tree_frame = Frame(self.root, bd=3, relief=RIDGE)
        tree_frame.place(x=500, y=50, width=800, height=600)

        scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("datetime", "desc", "amount", "type", "category"),
            yscrollcommand=scroll_y.set
        )
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_y.config(command=self.tree.yview)

        columns = [
            ("#0",       "ID",         50,  'center'),
            ("datetime", "Date/Time", 150,  'center'),
            ("desc",     "Description",250, 'w'),
            ("amount",   "Amount",    100,  'e'),
            ("type",     "Type",      100,  'center'),
            ("category", "Category",  150,  'w')
        ]

        for (col_id, heading, width, anchor) in columns:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor=anchor)

        self.tree.pack(fill=BOTH, expand=1)
        self.tree.bind("<ButtonRelease-1>", self.get_data)

    def create_filter_section(self):
        """
        Top filter bar: Month | Year | [Search]
        """
        filter_frame = Frame(self.root, bg="white")
        filter_frame.place(x=500, y=10, width=800, height=30)

        # Month filter
        Label(filter_frame, text="Month:", font=("arial", 12), bg="white").pack(side=LEFT, padx=(5,0))
        ttk.Combobox(
            filter_frame,
            textvariable=self.var_search_month,
            values=["All"] + [datetime(2000, m, 1).strftime("%B") for m in range(1,13)],
            state="readonly",
            width=12
        ).pack(side=LEFT, padx=(0,15))

        # Year filter
        Label(filter_frame, text="Year:", font=("arial", 12), bg="white").pack(side=LEFT, padx=(0,5))
        ttk.Combobox(
            filter_frame,
            textvariable=self.var_search_year,
            values=[str(y) for y in range(2010, 2041)],
            state="readonly",
            width=8
        ).pack(side=LEFT, padx=(0,15))

        # Search button
        Button(
            filter_frame,
            text="Search",
            command=self.load_data,
            bg="lightblue",
            font=("arial", 11, "bold")
        ).pack(side=LEFT)

    def save(self):
        """
        Insert a new payout.  
        We always set fixed_id = NULL (so it’s a one‐time),
        type = "Income", category = whatever was chosen,
        and store the current timestamp as datetime.
        """
        if not all([self.var_description.get(), self.var_amount.get(), self.var_category.get()]):
            messagebox.showerror("Error", "Please fill all mandatory fields!")
            return

        try:
            current_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                INSERT INTO transactions
                  (datetime, description, amount, type, category, month, year, fixed_id)
                VALUES (?,?,?,?,?,?,?,NULL)
            ''', (
                current_dt,
                self.var_description.get(),
                float(self.var_amount.get()),
                "Income",                      # now always Income for payouts
                self.var_category.get(),
                datetime.now().month,
                datetime.now().year
            ))
            self.db.conn.commit()
            self.load_data()
            self.clear()
            messagebox.showinfo("Success", "Payout saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def load_data(self):
        """
        Populate the Treeview with all "one‐time" income transactions (fixed_id IS NULL).
        Apply month/year filters if provided.
        """
        self.tree.delete(*self.tree.get_children())

        query = '''
            SELECT id, datetime, description, amount, type, category
              FROM transactions
             WHERE fixed_id IS NULL
               AND type = "Income"
        '''
        params = []

        # Month filter
        if self.var_search_month.get() and self.var_search_month.get() != "All":
            mnum = datetime.strptime(self.var_search_month.get(), "%B").month
            query += " AND strftime('%m', datetime) = ?"
            params.append(f"{mnum:02d}")

        # Year filter
        if self.var_search_year.get():
            query += " AND strftime('%Y', datetime) = ?"
            params.append(self.var_search_year.get())

        query += " ORDER BY datetime DESC"

        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            rec_id, dt_str, desc, amt, typ, cat = row
            # Convert from "YYYY-MM-DD HH:MM:SS" to "DD-Mon-YYYY HH:MM"
            try:
                dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                display_dt = dt_obj.strftime("%d-%b-%Y %H:%M")
            except ValueError:
                display_dt = dt_str

            self.tree.insert(
                "",
                "end",
                text=rec_id,
                values=(
                    display_dt,
                    desc,
                    amt,
                    typ,
                    cat
                )
            )

    def get_data(self, event):
        """
        When the user clicks a row, populate the left‐side form for editing.
        """
        selected = self.tree.focus()
        if not selected:
            return

        data = self.tree.item(selected)
        self.var_id.set(data["text"])
        values = data["values"]
        # values = [Date/Time, Description, Amount, Type, Category]
        self.var_description.set(values[1])
        self.var_amount.set(values[2])
        self.var_type.set(values[3])      # Should always be "Income"
        self.var_category.set(values[4])

    def update(self):
        """
        Update an existing payout record. We keep the original datetime/month/year,
        but allow editing description, amount, category.  Type stays "Income".
        """
        if not self.var_id.get():
            messagebox.showerror("Error", "Select a record to update!")
            return

        try:
            # Fetch the existing datetime for this record
            self.cursor.execute(
                "SELECT datetime FROM transactions WHERE id = ?",
                (self.var_id.get(),)
            )
            existing_dt = self.cursor.fetchone()[0]
            dt_obj = datetime.strptime(existing_dt, "%Y-%m-%d %H:%M:%S")
            orig_month = dt_obj.month
            orig_year  = dt_obj.year

            # Now update the record (type remains "Income", fixed_id remains NULL)
            self.cursor.execute('''
                UPDATE transactions
                   SET description = ?,
                       amount      = ?,
                       type        = ?,
                       category    = ?,
                       month       = ?,
                       year        = ?
                 WHERE id = ?
            ''', (
                self.var_description.get(),
                float(self.var_amount.get()),
                "Income",
                self.var_category.get(),
                orig_month,
                orig_year,
                self.var_id.get()
            ))
            self.db.conn.commit()
            self.load_data()
            self.clear()
            messagebox.showinfo("Success", "Payout updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def clear(self):
        """
        Clear all form fields (and reset type/category defaults).
        """
        self.var_id.set("")
        self.var_description.set("")
        self.var_amount.set("")
        self.var_type.set("Income")
        self.var_category.set("Payout")

if __name__ == "__main__":
    root = Tk()
    obj = PayoutAmount(root)
    root.mainloop()
