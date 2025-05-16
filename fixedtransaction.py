from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from create_db import DBConnection

class FixedTransaction:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1350x700+0+0")
        self.root.title("Fixed Transactions Management")
        self.root.config(bg="white")
        self.root.focus_force()
        
        self.db = DBConnection()
        self.cursor = self.db.cursor
        
        # Variables
        self.var_id = StringVar()
        self.var_description = StringVar()
        self.var_amount = StringVar()
        self.var_type = StringVar()
        self.var_category = StringVar()
        self.var_frequency = StringVar()
        self.var_due_day = IntVar(value=1)
        self.var_search_month = StringVar()
        self.var_search_year = StringVar()
        
        # UI Components
        self.create_input_fields()
        self.create_buttons()
        self.create_treeview()
        self.create_filter_section()
        self.load_data()

    def create_input_fields(self):
        input_frame = Frame(self.root, bd=3, relief=RIDGE, bg="white")
        input_frame.place(x=50, y=50, width=400, height=500)
        
        Label(input_frame, text="Fixed Transaction Details", font=("arial", 14, "bold"), bg="lightgray").pack(fill=X)
        
        fields = [
            ("Description", self.var_description, 50),
            ("Amount", self.var_amount, 90),
            ("Type", self.var_type, 130, ["Income", "Expense"]),
            ("Category", self.var_category, 170, ["EMI", "Rent", "Utilities", "Insurance", "Subscription", "Other"]),
            ("Frequency", self.var_frequency, 210, ["Monthly", "Bi-Monthly", "Quarterly", "Annual"]),
        ]
        
        y_pos = 50
        for field in fields:
            Label(input_frame, text=f"{field[0]}:", bg="white", font=("arial", 12)).place(x=10, y=y_pos)
            if len(field) > 3:
                ttk.Combobox(input_frame, textvariable=field[1], values=field[3], 
                            state="readonly", font=("arial", 12)).place(x=120, y=y_pos, width=250)
            else:
                Entry(input_frame, textvariable=field[1], font=("arial", 12), bg="lightyellow").place(x=120, y=y_pos, width=250)
            y_pos += 40
            
        Label(input_frame, text="Due Day:", bg="white", font=("arial", 12)).place(x=10, y=290)
        Spinbox(input_frame, from_=1, to=31, textvariable=self.var_due_day, 
               font=("arial", 12)).place(x=120, y=290, width=250)

    def create_buttons(self):
        buttons = [
            ("Save", "green", self.save, 50, 560),
            ("Update", "orange", self.update, 160, 560),
            ("Delete", "red", self.delete, 270, 560),
            ("Clear", "gray", self.clear, 380, 560),
            ("Mark Paid", "blue", self.mark_paid, 50, 600)
        ]
        
        for text, color, command, x, y in buttons:
            Button(self.root, text=text, bg=color, fg="white", font=("arial", 12, "bold"),
                  command=command).place(x=x, y=y, width=100 if text != "Mark Paid" else 150, height=30)

    def create_treeview(self):
        tree_frame = Frame(self.root, bd=3, relief=RIDGE)
        tree_frame.place(x=500, y=50, width=800, height=600)
        
        scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
        self.tree = ttk.Treeview(tree_frame, columns=("entry_date", "desc", "amount", "type", "category", 
                                                    "freq", "due", "next_due", "status"), 
                                yscrollcommand=scroll_y.set)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_y.config(command=self.tree.yview)
        
        columns = [
            ("#0", "ID", 50, 'center'),
            ("entry_date", "Entry Date", 120, 'center'),
            ("desc", "Description", 150, 'w'),
            ("amount", "Amount", 80, 'e'),
            ("type", "Type", 80, 'center'),
            ("category", "Category", 100, 'w'),
            ("freq", "Frequency", 100, 'w'),
            ("due", "Due Day", 70, 'center'),
            ("next_due", "Next Due", 120, 'center'),
            ("status", "Status", 150, 'center')
        ]
        
        for col in columns:
            self.tree.heading(col[0], text=col[1])
            self.tree.column(col[0], width=col[2], anchor=col[3])
        
        self.tree.pack(fill=BOTH, expand=1)
        self.tree.bind("<ButtonRelease-1>", self.get_data)

    def create_filter_section(self):
        filter_frame = Frame(self.root, bg="white")
        filter_frame.place(x=500, y=10, width=800, height=30)
        
        Label(filter_frame, text="Filter Month:", font=("arial", 12)).pack(side=LEFT, padx=5)
        ttk.Combobox(filter_frame, textvariable=self.var_search_month, 
                    values=["All"] + [date(2000, m, 1).strftime('%B') for m in range(1,13)], 
                    state="readonly", width=12).pack(side=LEFT, padx=5)
        
        Label(filter_frame, text="Year:", font=("arial", 12)).pack(side=LEFT, padx=5)
        ttk.Combobox(filter_frame, textvariable=self.var_search_year, 
                    state="readonly", width=8).pack(side=LEFT, padx=5)
        
        Button(filter_frame, text="Search", command=self.load_data, bg="lightblue").pack(side=LEFT, padx=5)
        
        # Populate years
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year-2, current_year+3)]
        self.var_search_year.set(str(current_year))
        ttk.Combobox(filter_frame, textvariable=self.var_search_year, 
                    values=years, state="readonly", width=8)

    def save(self):
        if not all([self.var_description.get(), self.var_amount.get(), self.var_type.get()]):
            messagebox.showerror("Error", "Please fill all mandatory fields!")
            return
            
        try:
            entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            next_due = self.calculate_next_due()
            
            self.cursor.execute('''INSERT INTO fixed_transactions 
                                (entry_date, description, amount, type, category, 
                                frequency, due_day, next_due_date)
                                VALUES (?,?,?,?,?,?,?,?)''',
                                (entry_date,
                                 self.var_description.get(),
                                 float(self.var_amount.get()),
                                 self.var_type.get(),
                                 self.var_category.get(),
                                 self.var_frequency.get(),
                                 self.var_due_day.get(),
                                 next_due))
            
            fixed_id = self.cursor.lastrowid
            self.generate_payment_records(fixed_id, datetime.now().date())
            
            self.db.conn.commit()
            self.load_data()
            self.clear()
            messagebox.showinfo("Success", "Transaction saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def generate_payment_records(self, fixed_id, start_date):
        start = start_dateload
        end = date(start.year + 2, 12, 31)  # Generate records for 2 years ahead
        current = start
        
        while current <= end:
            self.cursor.execute('''INSERT OR IGNORE INTO payment_status 
                                  (fixed_id, month, year)
                                  VALUES (?,?,?)''',
                                  (fixed_id, current.month, current.year))
            current += relativedelta(months=1)

    def calculate_next_due(self):
        today = date.today()
        due_day = self.var_due_day.get()
        freq = self.var_frequency.get()
        
        try:
            initial_due = date(today.year, today.month, due_day)
        except ValueError:
            initial_due = date(today.year, today.month, 28)
            
        freq_map = {
            "Monthly": 1,
            "Bi-Monthly": 2,
            "Quarterly": 3,
            "Annual": 12
        }
        
        months = freq_map.get(freq, 1)
        next_due = initial_due
        
        while next_due <= today:
            year = next_due.year + (next_due.month + months - 1) // 12
            month = (next_due.month + months - 1) % 12 + 1
            try:
                next_due = date(year, month, due_day)
            except ValueError:
                next_due = date(year, month, 28)
        
        return next_due.strftime("%Y-%m-%d")

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        query = '''SELECT 
                    ft.id, 
                    ft.entry_date,
                    ft.description,
                    ft.amount,
                    ft.type,
                    ft.category,
                    ft.frequency,
                    ft.due_day,
                    ps.month || '/' || ps.year as period,
                    ps.status,
                    ps.paid_date,
                    ps.month,
                    ps.year
                FROM fixed_transactions ft
                JOIN payment_status ps ON ft.id = ps.fixed_id'''
        
        params = []
        conditions = []
        
        # Handle month filter
        current_month = self.var_search_month.get()
        if current_month and current_month != "All":
            try:
                month_num = datetime.strptime(current_month, "%B").month
                conditions.append("ps.month = ?")
                params.append(month_num)
            except ValueError:
                messagebox.showerror("Error", "Invalid month selection")
        
        # Handle year filter
        current_year = self.var_search_year.get()
        if current_year:
            conditions.append("ps.year = ?")
            params.append(current_year)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY ps.year, ps.month"
        
        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            status_text = "Pending"
            paid_date = ""
            if row[9] == "Paid":
                paid_date = datetime.strptime(row[10], "%Y-%m-%d %H:%M:%S").strftime("%d-%b-%Y %H:%M")
                status_text = f"Paid on {paid_date}"
            
            due_date = date(int(row[12]), int(row[11]), row[7]).strftime("%d-%b-%Y")
            
            self.tree.insert("", "end", text=row[0], values=(
                datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S").strftime("%d-%b-%Y %H:%M"),
                row[2],  # description
                row[3],  # amount
                row[4],  # type
                row[5],  # category
                row[6],  # frequency
                row[7],  # due_day
                due_date,
                status_text
            ))

    def mark_paid(self):
        if not self.var_id.get():
            messagebox.showerror("Error", "Select a transaction to mark paid!")
            return
            
        try:
            paid_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Update payment status
            self.cursor.execute('''UPDATE payment_status SET
                                status=?, paid_date=?
                                WHERE fixed_id=? 
                                AND month=? 
                                AND year=?''',
                                ("Paid", paid_datetime, self.var_id.get(), 
                                 current_month, current_year))
            
            # Add to main transactions
            self.cursor.execute('''INSERT INTO transactions 
                                (datetime, description, amount, type, category,
                                month, year, fixed_id)
                                SELECT ?, description, amount, type, category,
                                ?, ?, id
                                FROM fixed_transactions WHERE id=?''',
                                (paid_datetime, current_month, current_year, self.var_id.get()))
            
            # Update next due date and generate new payment record
            self.update_next_due_date()
            
            self.db.conn.commit()
            self.load_data()
            messagebox.showinfo("Success", "Transaction marked as paid!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def generate_payment_records(self, fixed_id, start_date):
        # Corrected variable name from start_dateload to start_date
        start = start_date  # <-- Fix this line
        end = date(start.year + 2, 12, 31)  # Generate records for 2 years ahead
        current = start
        
        while current <= end:
            self.cursor.execute('''INSERT OR IGNORE INTO payment_status 
                                (fixed_id, month, year)
                                VALUES (?,?,?)''',
                                (fixed_id, current.month, current.year))
            current += relativedelta(months=1)

    

    def update_next_due_date(self):
        self.cursor.execute('''SELECT next_due_date, frequency 
                            FROM fixed_transactions WHERE id=?''',
                            (self.var_id.get(),))
        result = self.cursor.fetchone()
        current_due = datetime.strptime(result[0], "%Y-%m-%d").date()
        frequency = result[1]
        
        new_due = self.add_months(current_due, {
            "Monthly": 1,
            "Bi-Monthly": 2,
            "Quarterly": 3,
            "Annual": 12
        }[frequency])
        
        self.cursor.execute('''UPDATE fixed_transactions 
                            SET next_due_date=?
                            WHERE id=?''',
                            (new_due.strftime("%Y-%m-%d"), self.var_id.get()))
        
        # Create new payment record if not exists
        self.cursor.execute('''INSERT OR IGNORE INTO payment_status 
                            (fixed_id, month, year)
                            VALUES (?,?,?)''',
                            (self.var_id.get(), new_due.month, new_due.year))

    def add_months(self, source_date, months):
        month = source_date.month - 1 + months
        year = source_date.year + (month // 12)
        month = (month % 12) + 1
        day = source_date.day
        try:
            return date(year, month, day)
        except ValueError:
            return date(year, month, 28)

    def get_data(self, event):
        selected = self.tree.focus()
        if selected:
            data = self.tree.item(selected)
            self.var_id.set(data['text'])
            values = data['values']
            self.var_description.set(values[1])
            self.var_amount.set(values[2])
            self.var_type.set(values[3])
            self.var_category.set(values[4])
            self.var_frequency.set(values[5])
            self.var_due_day.set(values[6])

    def update(self):
        if not self.var_id.get():
            messagebox.showerror("Error", "Select a record to update!")
            return
            
        try:
            next_due = self.calculate_next_due()
            self.cursor.execute('''UPDATE fixed_transactions SET
                                description=?, amount=?, type=?, category=?,
                                frequency=?, due_day=?, next_due_date=?
                                WHERE id=?''',
                                (self.var_description.get(),
                                 float(self.var_amount.get()),
                                 self.var_type.get(),
                                 self.var_category.get(),
                                 self.var_frequency.get(),
                                 self.var_due_day.get(),
                                 next_due,
                                 self.var_id.get()))
            self.db.conn.commit()
            self.load_data()
            self.clear()
            messagebox.showinfo("Success", "Transaction updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def delete(self):
        if not self.var_id.get():
            messagebox.showerror("Error", "Select a record to delete!")
            return
            
        if messagebox.askyesno("Confirm", "Delete this transaction?"):
            self.cursor.execute("DELETE FROM fixed_transactions WHERE id=?", (self.var_id.get(),))
            self.db.conn.commit()
            self.load_data()
            self.clear()

    def clear(self):
        for var in [self.var_id, self.var_description, self.var_amount, 
                   self.var_type, self.var_category, self.var_frequency]:
            var.set("")
        self.var_due_day.set(1)

if __name__ == "__main__":
    root = Tk()
    obj = FixedTransaction(root)
    root.mainloop()