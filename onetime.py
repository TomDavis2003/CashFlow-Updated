from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
from create_db import DBConnection

class OneTime:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1350x700+0+0")
        self.root.title("One Time Transactions")
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
        
        Label(input_frame, text="Transaction Details", font=("arial", 14, "bold"), bg="lightgray").pack(fill=X)
        
        fields = [
            ("Description", self.var_description, 50),
            ("Amount", self.var_amount, 100),
            ("Type", self.var_type, 150, ["Income", "Expense"]),
            ("Category", self.var_category, 200, ["Shopping", "Food", "Transport", "Entertainment", "Other"]),
        ]
        
        y_pos = 50
        for field in fields:
            Label(input_frame, text=f"{field[0]}:", bg="white", font=("arial", 12)).place(x=10, y=y_pos)
            if len(field) > 3:
                ttk.Combobox(input_frame, textvariable=field[1], values=field[3], 
                            state="readonly", font=("arial", 12)).place(x=120, y=y_pos, width=250)
            else:
                Entry(input_frame, textvariable=field[1], font=("arial", 12), bg="lightyellow").place(x=120, y=y_pos, width=250)
            y_pos += 50

    def create_buttons(self):
        buttons = [
            ("Save", "green", self.save, 50, 560),
            ("Update", "orange", self.update, 160, 560),
            ("Clear", "gray", self.clear, 270, 560)
        ]
        
        for text, color, command, x, y in buttons:
            Button(self.root, text=text, bg=color, fg="white", font=("arial", 12, "bold"),
                  command=command).place(x=x, y=y, width=100, height=30)

    def create_treeview(self):
        tree_frame = Frame(self.root, bd=3, relief=RIDGE)
        tree_frame.place(x=500, y=50, width=800, height=600)
        
        scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
        self.tree = ttk.Treeview(tree_frame, columns=("datetime", "desc", "amount", "type", "category"), 
                                yscrollcommand=scroll_y.set)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_y.config(command=self.tree.yview)
        
        columns = [
            ("#0", "ID", 50, 'center'),
            ("datetime", "Date/Time", 150, 'center'),
            ("desc", "Description", 250, 'w'),
            ("amount", "Amount", 100, 'e'),
            ("type", "Type", 100, 'center'),
            ("category", "Category", 150, 'w')
        ]
        
        for col in columns:
            self.tree.heading(col[0], text=col[1])
            self.tree.column(col[0], width=col[2], anchor=col[3])
        
        self.tree.pack(fill=BOTH, expand=1)
        self.tree.bind("<ButtonRelease-1>", self.get_data)

    def create_filter_section(self):
        filter_frame = Frame(self.root, bg="white")
        filter_frame.place(x=500, y=10, width=800, height=30)
        
        Label(filter_frame, text="Month:", font=("arial", 12)).pack(side=LEFT, padx=5)
        ttk.Combobox(filter_frame, textvariable=self.var_search_month, 
                    values=["All"] + [datetime(2000, m, 1).strftime('%B') for m in range(1,13)], 
                    state="readonly", width=12).pack(side=LEFT, padx=5)
        
        Label(filter_frame, text="Year:", font=("arial", 12)).pack(side=LEFT, padx=5)
        ttk.Combobox(filter_frame, textvariable=self.var_search_year, 
                    values=[str(y) for y in range(2010, 2041)], width=8).pack(side=LEFT, padx=5)
        
        Button(filter_frame, text="Search", command=self.load_data, bg="lightblue").pack(side=LEFT, padx=5)

    def save(self):
        if not all([self.var_description.get(), self.var_amount.get(), self.var_type.get()]):
            messagebox.showerror("Error", "Please fill all mandatory fields!")
            return
            
        try:
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''INSERT INTO transactions 
                                (datetime, description, amount, type, category, month, year)
                                VALUES (?,?,?,?,?,?,?)''',
                                (current_datetime,
                                 self.var_description.get(),
                                 float(self.var_amount.get()),
                                 self.var_type.get(),
                                 self.var_category.get(),
                                 datetime.now().month,
                                 datetime.now().year))
            
            self.db.conn.commit()
            self.load_data()
            self.clear()
            messagebox.showinfo("Success", "Transaction saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        # Only include true one‐time entries, NOT advance‐payouts (or other excluded categories)
        query = '''
            SELECT id, datetime, description, amount, type, category
              FROM transactions
             WHERE fixed_id IS NULL
               AND category != "Advance Payout"
               AND category != "Loan Repaid"
        '''
        params = []

        # Month filter
        if self.var_search_month.get() and self.var_search_month.get() != "All":
            month_num = datetime.strptime(self.var_search_month.get(), "%B").month
            query += " AND strftime('%m', datetime) = ?"
            params.append(f"{month_num:02d}")

        # Year filter
        if self.var_search_year.get() and self.var_search_year.get() != "All":
            query += " AND strftime('%Y', datetime) = ?"
            params.append(self.var_search_year.get())

        query += " ORDER BY datetime DESC"

        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            rec_id, dt_str, desc, amt, typ, cat = row
            try:
                display_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").strftime("%d-%b-%Y %H:%M")
            except ValueError:
                display_dt = dt_str

            self.tree.insert(
                "",
                "end",
                text=rec_id,
                values=(display_dt, desc, amt, typ, cat)
            )

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

    def update(self):
        if not self.var_id.get():
            messagebox.showerror("Error", "Select a record to update!")
            return
            
        try:
            # Get existing datetime from database
            self.cursor.execute('SELECT datetime FROM transactions WHERE id=?', (self.var_id.get(),))
            existing_datetime = self.cursor.fetchone()[0]
            
            self.cursor.execute('''UPDATE transactions SET
                                description=?, amount=?, 
                                type=?, category=?, month=?, year=?
                                WHERE id=?''',
                                (self.var_description.get(),
                                 float(self.var_amount.get()),
                                 self.var_type.get(),
                                 self.var_category.get(),
                                 datetime.strptime(existing_datetime, "%Y-%m-%d %H:%M:%S").month,
                                 datetime.strptime(existing_datetime, "%Y-%m-%d %H:%M:%S").year,
                                 self.var_id.get()))
            self.db.conn.commit()
            self.load_data()
            self.clear()
            messagebox.showinfo("Success", "Transaction updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def clear(self):
        self.var_id.set("")
        self.var_description.set("")
        self.var_amount.set("")
        self.var_type.set("")
        self.var_category.set("")

if __name__ == "__main__":
    root = Tk()
    obj = OneTime(root)
    root.mainloop()