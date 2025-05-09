from tkinter import *
from PIL import Image, ImageTk
from cashflow import cashflowClass

class IMS:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1350x700+0+0")
        self.root.title("CashFlow Management System")
        self.root.config(bg="white")

        # Title
        self.icon_title = PhotoImage(file=r"images\logo.png")
        title = Label(self.root, text="CashFlow Management System", image=self.icon_title, compound=LEFT, 
                    font=("times new roman", 40, "bold"), bg="white", fg="#e50000", anchor="w", padx=20)
        title.place(x=0, y=0, relwidth=1, height=70)

        # btn_logout
        btn_logout = Button(self.root, text="Logout", font=("times new roman", 15, "bold"), 
                      bg="white", fg="black", cursor="hand2")
        btn_logout.place(x=1200, y=10, height=30, width=100)

        # clock
        self.lbl_clock = Label(self.root, 
                             text="Welcome to CashFlow Management System\t\t Date: DD-MM-YYYY\t\t Time: HH:MM:SS", 
                             font=("times new roman", 15, "bold"), bg="#e50000", fg="white")
        self.lbl_clock.place(x=0, y=70, relwidth=1, height=30)

        # left menu
        self.MenuLogo = Image.open(r"images\menu.png")
        self.MenuLogo = self.MenuLogo.resize((100, 100), Image.Resampling.LANCZOS)
        self.MenuLogo = ImageTk.PhotoImage(self.MenuLogo)
        
        self.LeftMenu = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        self.LeftMenu.place(x=0, y=100, width=200, height=600)
        
        lbl_menu_img = Label(self.LeftMenu, image=self.MenuLogo)
        lbl_menu_img.pack(side=TOP, fill=X)
        
        lbl_menu = Label(self.LeftMenu, text="Menu", font=("times new roman", 15), bg="black", fg="white")
        lbl_menu.pack(side=TOP, fill=X)

        btn_cashflow = Button(self.LeftMenu, text="Cash Flow", command=self.cashflow, 
                            font=("times new roman", 15, "bold"), bg="white", bd=3, fg="black", cursor="hand2")
        btn_cashflow.pack(side=TOP, fill=X)
        
        btn_employee = Button(self.LeftMenu, text="Employee", 
                            font=("times new roman", 15, "bold"), bg="white", bd=3, fg="black", cursor="hand2")
        btn_employee.pack(side=TOP, fill=X)
        
        # Add test button
        btn_test = Button(self.LeftMenu, text="Test Entry", command=self.test_entry,
                         font=("times new roman", 15, "bold"), bg="white", bd=3, 
                         fg="black", cursor="hand2")
        btn_test.pack(side=TOP, fill=X)
        
        btn_exit = Button(self.LeftMenu, text="Exit", 
                         font=("times new roman", 15, "bold"), bg="white", bd=3, fg="black", cursor="hand2")
        btn_exit.pack(side=TOP, fill=X)

        # footer
        lbl_footer = Label(self.root, 
                         text="CFMS - CashFlow Management System | Developed by Loanitol \n For any technical issue Contact: 94466*****", 
                         font=("times new roman", 15, "bold"), bg="#e50000", fg="white")
        lbl_footer.pack(side=BOTTOM, fill=X)

    def cashflow(self):
        self.new_window = Toplevel(self.root)
        self.app = cashflowClass(self.new_window)

    def test_entry(self):
        test_window = Toplevel(self.root)
        test_window.title("Test Entry")
        
        # Create a simple Entry widget
        test_entry = Entry(test_window, font=("times new roman", 15))
        test_entry.pack(padx=20, pady=20)
        
        # Add a button to print the entry's content
        Button(test_window, text="Print Entry", 
               command=lambda: print(test_entry.get())).pack()

if __name__ == "__main__":
    root = Tk()
    obj = IMS(root)
    root.mainloop()