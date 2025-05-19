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
        
        # Year combobox with 2010-2040 range
        years = [str(y) for y in range(2010, 2041)]
        self.var_search_year.set(str(datetime.now().year))
        ttk.Combobox(filter_frame, textvariable=self.var_search_year, 
                    values=years, state="readonly", width=8).pack(side=LEFT, padx=5)
        
        Button(filter_frame, text="Search", command=self.load_data, bg="lightblue").pack(side=LEFT, padx=5)

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
            next_due_date = datetime.strptime(next_due, "%Y-%m-%d").date()
            self.generate_payment_records(fixed_id, next_due_date, self.cursor)
            
            self.db.conn.commit()
            self.load_data()
            self.clear()
            messagebox.showinfo("Success", "Transaction saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def calculate_next_due(self):
        today = date.today()
        due_day = self.var_due_day.get()
        freq = self.var_frequency.get()
        
        # Always start from current month
        try:
            initial_due = date(today.year, today.month, due_day)
        except ValueError:
            initial_due = date(today.year, today.month, 28)
            
        # If due date already passed this month, keep it current month
        if initial_due < today:
            initial_due = initial_due  # Still use current month's due date
        
        return initial_due.strftime("%Y-%m-%d")

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        query = '''SELECT 
                    ft.id, 
                    ft.entry_date,
                    ft.description,
                    COALESCE(ps.amount, ft.amount) AS amount,  -- Use stored amount for paid transactions
                    ft.type,
                    ft.category,
                    ft.frequency,
                    ft.due_day,
                    ps.month,
                    ps.year,
                    ps.status,
                    ps.paid_date
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
            if row[10] == "Paid":
                paid_date = datetime.strptime(row[11], "%Y-%m-%d %H:%M:%S").strftime("%d-%b-%Y %H:%M")
                status_text = f"Paid on {paid_date}"
            
            try:
                due_date = date(int(row[9]), int(row[8]), row[7]).strftime("%d-%b-%Y")
            except ValueError:
                due_date = "Invalid Date"
            
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
            with self.db.conn:
                cursor = self.db.conn.cursor()
                paid_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                current_month = datetime.now().month
                current_year = datetime.now().year
                
                # Get and store current amount
                cursor.execute('SELECT amount FROM fixed_transactions WHERE id=?', 
                            (self.var_id.get(),))
                current_amount = cursor.fetchone()[0]

                # Update payment status with amount
                cursor.execute('''UPDATE payment_status SET
                                status=?, paid_date=?, amount=?
                                WHERE fixed_id=? AND month=? AND year=?''',
                                ("Paid", paid_datetime, current_amount,
                                self.var_id.get(), current_month, current_year))
                
                # Add to transactions
                cursor.execute('''INSERT INTO transactions 
                                (datetime, description, amount, type, category,
                                month, year, fixed_id)
                                VALUES (?,?,?,?,?,?,?,?)''',
                                (paid_datetime, 
                                self.var_description.get(),
                                current_amount,
                                self.var_type.get(),
                                self.var_category.get(),
                                current_month, 
                                current_year,
                                self.var_id.get()))
                
                self.load_data()
                messagebox.showinfo("Success", "Transaction marked as paid!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def generate_payment_records(self, fixed_id, start_date, cursor=None):
        try:
            if cursor is None:
                cursor = self.cursor
            cursor.execute('SELECT frequency FROM fixed_transactions WHERE id=?', 
                        (fixed_id,))
            frequency = cursor.fetchone()[0]
            
            freq_map = {
                "Monthly": 1,
                "Bi-Monthly": 2,
                "Quarterly": 3,
                "Annual": 12
            }
            step = freq_map.get(frequency, 1)

            # Start from the first day of the current month
            current_date = date(start_date.year, start_date.month, 1)
            end_date = current_date + relativedelta(years=2)  # Generate for 2 years
            
            months_added = 0
            while months_added < 24:  # Limit to 24 months (2 years)
                cursor.execute('''INSERT OR IGNORE INTO payment_status 
                                (fixed_id, month, year)
                                VALUES (?, ?, ?)''',
                                (fixed_id, current_date.month, current_date.year))
                
                # Move to next period
                current_date = self.add_months(current_date, step)
                months_added += step
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generating payment records: {str(e)}")

    def update_next_due_date(self, cursor):
        cursor.execute('''SELECT next_due_date, frequency 
                        FROM fixed_transactions WHERE id=?''',
                        (self.var_id.get(),))
        result = cursor.fetchone()
        current_due = datetime.strptime(result[0], "%Y-%m-%d").date()
        frequency = result[1]
        
        new_due = self.add_months(current_due, {
            "Monthly": 1,
            "Bi-Monthly": 2,
            "Quarterly": 3,
            "Annual": 12
        }[frequency])
        
        cursor.execute('''UPDATE fixed_transactions 
                        SET next_due_date=?
                        WHERE id=?''',
                        (new_due.strftime("%Y-%m-%d"), self.var_id.get()))
        
        self.generate_payment_records(self.var_id.get(), new_due, cursor)

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
            try:
                # Delete related payment status first
                self.cursor.execute("DELETE FROM payment_status WHERE fixed_id=?", 
                                  (self.var_id.get(),))
                # Delete related transactions
                self.cursor.execute("DELETE FROM transactions WHERE fixed_id=?", 
                                  (self.var_id.get(),))
                # Finally delete the fixed transaction
                self.cursor.execute("DELETE FROM fixed_transactions WHERE id=?", 
                                  (self.var_id.get(),))
                self.db.conn.commit()
                self.load_data()
                self.clear()
            except Exception as e:
                self.db.conn.rollback()
                messagebox.showerror("Error", f"Database error: {str(e)}")

    def clear(self):
        for var in [self.var_id, self.var_description, self.var_amount, 
                   self.var_type, self.var_category, self.var_frequency]:
            var.set("")
        self.var_due_day.set(1)

if __name__ == "__main__":
    root = Tk()
    obj = FixedTransaction(root)
    root.mainloop()