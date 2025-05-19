from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import sqlite3
from datetime import datetime

class LoanAmount:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1350x700+0+0")
        self.root.title("Loan Amounts")
        self.root.config(bg="white")
        self.root.focus_force()

        # Connect to the same database
        self.db = sqlite3.connect('cashflow.db')
        self.cursor = self.db.cursor()
        self.create_table()

        # Variables
        self.var_id          = StringVar()
        self.var_entry_date  = StringVar()
        self.var_description = StringVar()
        self.var_amount      = StringVar()
        self.var_party       = StringVar()
        self.var_due_date    = StringVar()
        self.var_status      = StringVar(value="Pending")

        # Filter variables
        self.var_search_party  = StringVar()
        self.var_search_status = StringVar(value="All")
        self.var_search_month  = StringVar()
        self.var_search_year   = StringVar(value=str(datetime.now().year))

        # Build UI
        self.create_input_fields()
        self.create_buttons()
        self.create_treeview()
        self.create_filter_section()
        self.load_data()

    def create_table(self):
        """
        Ensure the `loans` table exists with required columns:
          - id           : INTEGER PK
          - entry_date   : TEXT (YYYY-MM-DD HH:MM:SS)
          - description  : TEXT
          - amount       : REAL
          - party        : TEXT
          - due_date     : TEXT (YYYY-MM-DD)
          - status       : TEXT (Pending or Repaid)
          - repaid_date  : TEXT (YYYY-MM-DD) or NULL
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS loans (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date   TEXT    NOT NULL,
                description  TEXT    NOT NULL,
                amount       REAL    NOT NULL,
                party        TEXT    NOT NULL,
                due_date     TEXT    NOT NULL,
                status       TEXT    DEFAULT 'Pending',
                repaid_date  TEXT
            )
        ''')
        self.db.commit()

    def create_input_fields(self):
        """
        Left‐side input form (ID is hidden, entry_date is readonly):
          - Entry Date (auto)
          - Description
          - Amount
          - Party
          - Due Date (calendar)
          - Status (Pending / Repaid)
        """
        input_frame = Frame(self.root, bd=3, relief=RIDGE, bg="white")
        input_frame.place(x=50, y=50, width=400, height=500)

        Label(
            input_frame,
            text="Loan Details",
            font=("arial", 14, "bold"),
            bg="lightgray"
        ).pack(fill=X)

        fields = [
            ("Entry Date",   self.var_entry_date,   50),
            ("Description",  self.var_description, 100),
            ("Amount",       self.var_amount,      150),
            ("Party",        self.var_party,       200),
            ("Due Date",     self.var_due_date,    250, lambda: self.date_picker("due")),
            ("Status",       self.var_status,      300, ["Pending", "Repaid"])
        ]

        y_pos = 50
        for field in fields:
            Label(
                input_frame,
                text=f"{field[0]}:",
                bg="white",
                font=("arial", 12)
            ).place(x=10, y=y_pos)

            # If it has a date picker callback
            if len(field) > 3 and callable(field[3]):
                Button(
                    input_frame,
                    text="Select Date",
                    command=field[3],
                    bg="lightblue",
                    font=("arial", 11)
                ).place(x=150, y=y_pos, width=120)

            # If it’s a dropdown (Status)
            elif len(field) > 3 and isinstance(field[3], list):
                ttk.Combobox(
                    input_frame,
                    textvariable=field[1],
                    values=field[3],
                    state="readonly",
                    font=("arial", 12)
                ).place(x=150, y=y_pos, width=200)

            else:
                # Entry Date is readonly
                if field[0] == "Entry Date":
                    Entry(
                        input_frame,
                        textvariable=field[1],
                        font=("arial", 12),
                        state='readonly',
                        bg='lightgray'
                    ).place(x=150, y=y_pos, width=200)
                else:
                    Entry(
                        input_frame,
                        textvariable=field[1],
                        font=("arial", 12),
                        bg="lightyellow"
                    ).place(x=150, y=y_pos, width=200)

            y_pos += 50

    def date_picker(self, field_type):
        """
        Opens a child Toplevel with a Calendar; on “Select,” we set either
        var_due_date, then close the calendar.
        """
        top = Toplevel(self.root)
        top.title("Select Date")
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10)

        def set_date():
            if field_type == "due":
                self.var_due_date.set(cal.get_date())
            top.destroy()

        Button(top, text="Select", command=set_date).pack(pady=5)

    def create_buttons(self):
        """
        Bottom‐left buttons: Save, Update, Delete, Clear, Mark Repaid
        """
        buttons = [
            ("Save",       "green",  self.save,        50, 610),
            ("Update",     "orange", self.update,     160, 610),
            ("Delete",     "red",    self.delete,     270, 610),
            ("Clear",      "gray",   self.clear,      380, 610),
            ("Mark Repaid","blue",   self.mark_repaid, 50, 650)
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
        Right‐side Treeview with columns:
          ID | Entry Date | Description | Amount | Party | Due Date | Status
        """
        tree_frame = Frame(self.root, bd=3, relief=RIDGE)
        tree_frame.place(x=500, y=50, width=800, height=600)

        scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=(
                "entry_date", "desc", "amount", "party",
                "due_date", "status"
            ),
            yscrollcommand=scroll_y.set
        )
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_y.config(command=self.tree.yview)

        columns = [
            ("#0",         "ID",           50,  'center'),
            ("entry_date", "Entry Date",  120,  'center'),
            ("desc",       "Description", 200,  'w'),
            ("amount",     "Amount",       80,  'e'),
            ("party",      "Party",       120,  'w'),
            ("due_date",   "Due Date",    100,  'center'),
            ("status",     "Status",      100,  'center')
        ]

        for (col_id, heading, width, anchor) in columns:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor=anchor)

        self.tree.pack(fill=BOTH, expand=1)
        self.tree.bind("<ButtonRelease-1>", self.get_data)

    def create_filter_section(self):
        """
        Top‐right filter bar (party, status, month, year, [Search]).
        Filters are applied to the `due_date` column.
        """
        filter_frame = Frame(self.root, bg="white")
        filter_frame.place(x=500, y=10, width=800, height=30)

        # Party Filter
        Label(filter_frame, text="Party:", font=("arial", 12), bg="white").pack(side=LEFT, padx=5)
        Entry(filter_frame, textvariable=self.var_search_party, width=15).pack(side=LEFT, padx=5)

        # Status Filter
        Label(filter_frame, text="Status:", font=("arial", 12), bg="white").pack(side=LEFT, padx=5)
        ttk.Combobox(
            filter_frame,
            textvariable=self.var_search_status,
            values=["All", "Pending", "Repaid"],
            state="readonly",
            width=8
        ).pack(side=LEFT, padx=5)

        # Month Filter (on due_date)
        Label(filter_frame, text="Month:", font=("arial", 12), bg="white").pack(side=LEFT, padx=5)
        ttk.Combobox(
            filter_frame,
            textvariable=self.var_search_month,
            values=["All"] + [datetime(2000, m, 1).strftime('%B') for m in range(1,13)],
            state="readonly",
            width=12
        ).pack(side=LEFT, padx=5)

        # Year Filter (on due_date)
        Label(filter_frame, text="Year:", font=("arial", 12), bg="white").pack(side=LEFT, padx=5)
        ttk.Combobox(
            filter_frame,
            textvariable=self.var_search_year,
            values=[str(y) for y in range(2010, 2041)],
            state="readonly",
            width=8
        ).pack(side=LEFT, padx=5)

        # Search Button
        Button(
            filter_frame,
            text="Search",
            command=self.load_data,
            bg="lightblue",
            font=("arial", 12, "bold")
        ).pack(side=LEFT, padx=5)

    def save(self):
        """
        Insert a new loan record:
          - entry_date = current timestamp
          - description, amount, party, due_date, status  from form
          - repaid_date = NULL
        """
        if not all([
            self.var_description.get(),
            self.var_amount.get(),
            self.var_party.get(),
            self.var_due_date.get()
        ]):
            messagebox.showerror("Error", "Please fill all mandatory fields!")
            return

        try:
            entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                INSERT INTO loans
                  (entry_date, description, amount, party, due_date, status, repaid_date)
                VALUES (?, ?, ?, ?, ?, ?, NULL)
            ''', (
                entry_date,
                self.var_description.get(),
                float(self.var_amount.get()),
                self.var_party.get(),
                self.var_due_date.get(),
                self.var_status.get()
            ))
            self.db.commit()
            self.load_data()
            self.clear()
            messagebox.showinfo("Success", "Loan record saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def load_data(self):
        """
        Fetch loan records from `loans` with status='Pending' or 'Repaid',
        applying filters on party/status/month/year (month & year from due_date).
        Then populate the Treeview.
        """
        self.tree.delete(*self.tree.get_children())

        query = '''
            SELECT id, entry_date, description, amount, party,
                   due_date, status
              FROM loans
        '''
        params = []
        conditions = []

        # Party filter
        if self.var_search_party.get():
            conditions.append("party LIKE ?")
            params.append(f"%{self.var_search_party.get()}%")

        # Status filter
        if self.var_search_status.get() != "All":
            conditions.append("status = ?")
            params.append(self.var_search_status.get())

        # Month filter on due_date
        if self.var_search_month.get() and self.var_search_month.get() != "All":
            month_num = datetime.strptime(self.var_search_month.get(), "%B").month
            conditions.append("strftime('%m', due_date) = ?")
            params.append(f"{month_num:02d}")

        # Year filter on due_date
        if self.var_search_year.get():
            conditions.append("strftime('%Y', due_date) = ?")
            params.append(self.var_search_year.get())

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY due_date DESC"

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()

        for row in rows:
            (rid, ent_dt, desc, amt, party, ddate, status) = row

            # Format entry_date from "YYYY-MM-DD HH:MM:SS" to "DD-Mon-YYYY HH:MM"
            try:
                ent_dt_obj = datetime.strptime(ent_dt, "%Y-%m-%d %H:%M:%S")
                ent_display = ent_dt_obj.strftime("%d-%b-%Y %H:%M")
            except ValueError:
                ent_display = ent_dt

            self.tree.insert(
                "",
                "end",
                text=rid,
                values=(
                    ent_display,
                    desc,
                    f"{amt:.2f}",
                    party,
                    ddate,
                    status
                )
            )

    def get_data(self, event):
        """
        When a row is clicked, populate the left‐side inputs.
        """
        selected = self.tree.focus()
        if not selected:
            return

        data = self.tree.item(selected)
        self.var_id.set(data["text"])
        vals = data["values"]
        # values = [entry_date, description, amount, party, due_date, status]
        self.var_entry_date.set(vals[0])
        self.var_description.set(vals[1])
        self.var_amount.set(vals[2])
        self.var_party.set(vals[3])
        self.var_due_date.set(vals[4])
        self.var_status.set(vals[5])

    def update(self):
        """
        Update an existing loan record.
        We preserve the original `entry_date` in the DB.
        """
        if not self.var_id.get():
            messagebox.showerror("Error", "Select a record to update!")
            return

        try:
            # We only update description, amount, party, due_date, status
            self.cursor.execute('''
                UPDATE loans
                   SET description = ?,
                       amount      = ?,
                       party       = ?,
                       due_date    = ?,
                       status      = ?
                 WHERE id = ?
            ''', (
                self.var_description.get(),
                float(self.var_amount.get()),
                self.var_party.get(),
                self.var_due_date.get(),
                self.var_status.get(),
                self.var_id.get()
            ))
            self.db.commit()
            self.load_data()
            self.clear()
            messagebox.showinfo("Success", "Loan record updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def delete(self):
        """
        Delete the selected loan record (after confirmation).
        """
        if not self.var_id.get():
            messagebox.showerror("Error", "Select a record to delete!")
            return

        if messagebox.askyesno("Confirm", "Delete this loan record?"):
            try:
                self.cursor.execute("DELETE FROM loans WHERE id = ?", (self.var_id.get(),))
                self.db.commit()
                self.load_data()
                self.clear()
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {e}")

    def mark_repaid(self):
        """
        Mark the selected loan as "Repaid" and set repaid_date = today.
        """
        if not self.var_id.get():
            messagebox.showerror("Error", "Select a record to mark as repaid!")
            return

        try:
            repaid_dt = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute('''
                UPDATE loans
                   SET status = ?,
                       repaid_date = ?
                 WHERE id = ?
            ''', (
                "Repaid",
                repaid_dt,
                self.var_id.get()
            ))
            self.db.commit()
            self.load_data()
            messagebox.showinfo("Success", "Loan marked as repaid!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def clear(self):
        """
        Reset all entry fields to blank (and default status = "Pending").
        """
        for var in [
            self.var_id,
            self.var_entry_date,
            self.var_description,
            self.var_amount,
            self.var_party,
            self.var_due_date
        ]:
            var.set("")

        self.var_status.set("Pending")

if __name__ == "__main__":
    root = Tk()
    obj = LoanAmount(root)
    root.mainloop()
