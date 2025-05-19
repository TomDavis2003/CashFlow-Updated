from tkinter import *
from tkinter import ttk
from tkcalendar import Calendar
import sqlite3
from datetime import datetime
from tkinter import messagebox

class AdvanceAmount:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1350x700+0+0")
        self.root.title("Advance Amounts Management")
        self.root.config(bg="white")
        self.root.focus_force()
        
        # Connect to the same database
        self.db = sqlite3.connect('cashflow.db')
        self.cursor = self.db.cursor()
        self.create_table()
        
        # Variables (no more var_type or var_due_date)
        self.var_id = StringVar()
        self.var_entry_date = StringVar()
        self.var_description = StringVar()
        self.var_amount = StringVar()
        self.var_party = StringVar()
        self.var_advance_date = StringVar()
        self.var_status = StringVar(value="Pending")
        
        # Filter vars
        self.var_search_party = StringVar()
        self.var_search_status = StringVar(value="All")
        self.var_search_month = StringVar()
        self.var_search_year = StringVar(value=str(datetime.now().year))
        
        # Build the UI
        self.create_input_fields()
        self.create_buttons()
        self.create_treeview()
        self.create_filter_section()
        self.load_data()

    def create_table(self):
        """
        Ensures the advances table exists with the same schema.
        Note: 'type' and 'due_date' columns must still exist in the table definition,
        but the form will no longer set them manually.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS advances (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date    TEXT    NOT NULL,
                description   TEXT    NOT NULL,
                amount        REAL    NOT NULL,
                type          TEXT    NOT NULL,
                party         TEXT    NOT NULL,
                advance_date  TEXT    NOT NULL,
                due_date      TEXT    NOT NULL,
                status        TEXT    DEFAULT 'Pending',
                repaid_date   TEXT
            )
        ''')
        self.db.commit()

    def create_input_fields(self):
        """
        Build the left-side input form— WITHOUT "Type" or "Due Date" rows.
        """
        input_frame = Frame(self.root, bd=3, relief=RIDGE, bg="white")
        input_frame.place(x=50, y=50, width=400, height=550)
        
        Label(
            input_frame,
            text="Advance Details",
            font=("arial", 14, "bold"),
            bg="lightgray"
        ).pack(fill=X)
        
        fields = [
            ("Entry Date",   self.var_entry_date,   50),
            ("Description",  self.var_description, 100),
            ("Amount",       self.var_amount,      150),
            # ("Type", removed)
            ("Party Name",   self.var_party,       200),
            ("Advance Date", self.var_advance_date,300, lambda: self.date_picker("advance")),
            # ("Due Date", removed)
            ("Status",       self.var_status,     350, ["Pending", "Paid"])
        ]
        
        y_pos = 50
        for field in fields:
            Label(
                input_frame,
                text=f"{field[0]}:",
                bg="white",
                font=("arial", 12)
            ).place(x=10, y=y_pos)
            
            # If there's a callback (date picker), show a “Select Date” button
            if len(field) > 3 and callable(field[3]):
                Button(
                    input_frame,
                    text="Select Date",
                    command=field[3],
                    bg="lightblue",
                    font=("arial", 11)
                ).place(x=150, y=y_pos, width=120)
            
            # If it’s a dropdown (e.g., Status)
            elif len(field) > 3 and isinstance(field[3], list):
                ttk.Combobox(
                    input_frame,
                    textvariable=field[1],
                    values=field[3],
                    state="readonly",
                    font=("arial", 12)
                ).place(x=150, y=y_pos, width=200)
            
            # Otherwise, it’s a simple Entry
            else:
                # "Entry Date" is read-only
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
        Opens a small Calendar. Since we only have 'advance' or (originally) 'due',
        we only set var_advance_date here.
        """
        top = Toplevel(self.root)
        top.title("Select Date")
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10)
        
        def set_date():
            if field_type == "advance":
                self.var_advance_date.set(cal.get_date())
            top.destroy()
        
        Button(top, text="Select", command=set_date).pack(pady=5)

    def create_buttons(self):
        """
        Save / Update / Delete / Clear / Mark Paid
        (same positions as before)
        """
        buttons = [
            ("Save",      "green",  self.save,      50, 610),
            ("Update",    "orange", self.update,   160, 610),
            ("Delete",    "red",    self.delete,   270, 610),
            ("Clear",     "gray",   self.clear,    380, 610),
            ("Mark Paid", "blue",   self.mark_paid, 50, 650)
        ]
        
        for text, color, command, x, y in buttons:
            Button(
                self.root,
                text=text,
                bg=color,
                fg="white",
                font=("arial", 12, "bold"),
                command=command
            ).place(
                x=x,
                y=y,
                width=100 if text != "Mark Paid" else 150,
                height=30
            )

    def create_treeview(self):
        """
        Build the right‐side Treeview WITHOUT 'Type' or 'Due Date' columns.
        Remaining columns:
          ID | Entry Date | Description | Amount | Party | Advance Date | Status
        """
        tree_frame = Frame(self.root, bd=3, relief=RIDGE)
        tree_frame.place(x=500, y=50, width=800, height=600)
        
        scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=(
                "entry_date", "desc", "amount", "party",
                "advance_date", "status"
            ),
            yscrollcommand=scroll_y.set
        )
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_y.config(command=self.tree.yview)
        
        columns = [
            ("#0",          "ID",            50,    'center'),
            ("entry_date",  "Entry Date",   150,    'center'),
            ("desc",        "Description",  200,    'w'),
            ("amount",      "Amount",       100,    'e'),
            ("party",       "Party",        150,    'w'),
            ("advance_date","Advance Date", 120,    'center'),
            ("status",      "Status",       100,    'center')
        ]
        
        for col in columns:
            self.tree.heading(col[0], text=col[1])
            self.tree.column(col[0], width=col[2], anchor=col[3])
        
        self.tree.pack(fill=BOTH, expand=1)
        self.tree.bind("<ButtonRelease-1>", self.get_data)

    def create_filter_section(self):
        """
        The filter bar: Party | Month | Year | Status | [Search]
        (unchanged from your existing version)
        """
        filter_frame = Frame(self.root, bg="white")
        filter_frame.place(x=500, y=10, width=800, height=30)
        
        # Party Filter
        Label(filter_frame, text="Party:", font=("arial", 12)).pack(side=LEFT, padx=5)
        Entry(filter_frame, textvariable=self.var_search_party, width=15).pack(side=LEFT, padx=5)
        
        # Month Filter
        Label(filter_frame, text="Month:", font=("arial", 12)).pack(side=LEFT, padx=5)
        ttk.Combobox(
            filter_frame,
            textvariable=self.var_search_month,
            values=["All"] + [datetime(2000, m, 1).strftime('%B') for m in range(1,13)],
            state="readonly",
            width=12
        ).pack(side=LEFT, padx=5)
        
        # Year Filter
        Label(filter_frame, text="Year:", font=("arial", 12)).pack(side=LEFT, padx=5)
        years = [str(y) for y in range(2010, 2041)]
        ttk.Combobox(
            filter_frame,
            textvariable=self.var_search_year,
            values=years,
            state="readonly",
            width=8
        ).pack(side=LEFT, padx=5)
        
        # Status Filter
        Label(filter_frame, text="Status:", font=("arial", 12)).pack(side=LEFT, padx=5)
        ttk.Combobox(
            filter_frame,
            textvariable=self.var_search_status,
            values=["All", "Pending", "Paid"],
            width=8
        ).pack(side=LEFT, padx=5)
        
        Button(
            filter_frame,
            text="Search",
            command=self.load_data,
            bg="lightblue"
        ).pack(side=LEFT, padx=5)

    def save(self):
        """
        Inserts a new advance record.  
        Because we removed the “Type” and “Due Date” inputs, 
        we hardcode them here as follows:
          type = "Given"
          due_date = ""
        """
        if not all([self.var_description.get(), self.var_amount.get()]):
            messagebox.showerror("Error", "Please fill all mandatory fields!")
            return
            
        try:
            entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Hardcode type="Given", due_date="" (empty)
            self.cursor.execute('''
                INSERT INTO advances 
                  (entry_date, description, amount, type, party, 
                   advance_date, due_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry_date,
                self.var_description.get(),
                float(self.var_amount.get()),
                "Given",                          # fixed type
                self.var_party.get(),
                self.var_advance_date.get(),
                "",                               # fixed empty due_date
                self.var_status.get()
            ))
            self.db.commit()
            self.load_data()
            self.clear()
            messagebox.showinfo("Success", "Advance saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def load_data(self):
        """
        Populate the Treeview using the same filters you already had,
        but now only SELECT the columns we kept:
         (id, entry_date, description, amount, party, advance_date, status)
        """
        self.tree.delete(*self.tree.get_children())
        
        query = '''
            SELECT 
                id, 
                entry_date, 
                description, 
                amount, 
                party,
                advance_date, 
                status
            FROM advances
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
        
        # Month filter (on advance_date)
        if self.var_search_month.get() and self.var_search_month.get() != "All":
            month_num = datetime.strptime(self.var_search_month.get(), "%B").month
            conditions.append("strftime('%m', advance_date) = ?")
            params.append(f"{month_num:02d}")
        
        # Year filter (on advance_date)
        if self.var_search_year.get():
            conditions.append("strftime('%Y', advance_date) = ?")
            params.append(self.var_search_year.get())
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY advance_date DESC"
        
        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            # row = (id, entry_date, description, amount, party, advance_date, status)
            rec_id, ent_dt, desc, amt, party, adv_dt, stat = row

            # Try to parse as "%Y-%m-%d %H:%M:%S";
            # if that fails, assume it's already in "%d-%b-%Y %H:%M"
            try:
                ent_dt_obj = datetime.strptime(ent_dt, "%Y-%m-%d %H:%M:%S")
                ent_dt_str = ent_dt_obj.strftime("%d-%b-%Y %H:%M")
            except ValueError:
                ent_dt_str = ent_dt

            self.tree.insert(
                "",
                "end",
                text=rec_id,
                values=(
                    ent_dt_str,
                    desc,
                    amt,
                    party,
                    adv_dt,
                    stat
                )
            )

    def mark_paid(self):
        """
        Mark a selected record as Paid.  (No changes here.)
        """
        if not self.var_id.get():
            messagebox.showerror("Error", "Select an advance to mark as paid!")
            return
            
        try:
            self.cursor.execute('''
                UPDATE advances 
                SET status = ?, repaid_date = ?
                WHERE id = ?
            ''', (
                "Paid", 
                datetime.now().strftime("%Y-%m-%d"), 
                self.var_id.get()
            ))
            self.db.commit()
            self.load_data()
            messagebox.showinfo("Success", "Advance marked as paid!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def get_data(self, event):
        """
        When a row is clicked, populate the left‐side fields.
        (No “Type” or “Due Date” anymore.)
        """
        selected = self.tree.focus()
        if selected:
            data = self.tree.item(selected)
            self.var_id.set(data['text'])
            values = data['values']
            # values = [entry_date, description, amount, party, advance_date, status]
            self.var_entry_date.set(values[0])
            self.var_description.set(values[1])
            self.var_amount.set(values[2])
            self.var_party.set(values[3])
            self.var_advance_date.set(values[4])
            self.var_status.set(values[5])

    def update(self):
        """
        Update an existing record. 
        We STILL have to set “type”=“Given” and “due_date”="" under the hood.
        """
        if not self.var_id.get():
            messagebox.showerror("Error", "Select a record to update!")
            return
            
        try:
            self.cursor.execute('''
                UPDATE advances 
                SET 
                    entry_date   = ?, 
                    description  = ?, 
                    amount       = ?, 
                    type         = ?, 
                    party        = ?, 
                    advance_date = ?, 
                    due_date     = ?, 
                    status       = ?
                WHERE id = ?
            ''', (
                self.var_entry_date.get(),
                self.var_description.get(),
                float(self.var_amount.get()),
                "Given",                          # still “Given”
                self.var_party.get(),
                self.var_advance_date.get(),
                "",                               # still empty string
                self.var_status.get(),
                self.var_id.get()
            ))
            self.db.commit()
            self.load_data()
            self.clear()
            messagebox.showinfo("Success", "Advance updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def delete(self):
        """
        Delete the selected record.
        """
        if not self.var_id.get():
            messagebox.showerror("Error", "Select a record to delete!")
            return
            
        if messagebox.askyesno("Confirm", "Delete this advance record?"):
            try:
                self.cursor.execute("DELETE FROM advances WHERE id = ?", (self.var_id.get(),))
                self.db.commit()
                self.load_data()
                self.clear()
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {str(e)}")

    def clear(self):
        """
        Reset all entry fields to blank (and default status).
        """
        for var in [
            self.var_id,
            self.var_entry_date,
            self.var_description,
            self.var_amount,
            self.var_party,
            self.var_advance_date
        ]:
            var.set("")
        self.var_status.set("Pending")

if __name__ == "__main__":
    root = Tk()
    obj = AdvanceAmount(root)
    root.mainloop()
