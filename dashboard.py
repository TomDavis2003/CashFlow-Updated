from tkinter import *
import sqlite3
import datetime
from PIL import Image, ImageTk
from alltransaction import AllTransaction
from advanceamount import AdvanceAmount
from delay import DelayAmount
from payout import PayoutAmount
from fixedtransaction import FixedTransaction
from onetime import OneTime


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

        btn_cashflow = Button(self.LeftMenu, text="All Transactions",command=self.all_transaction, font=("times new roman", 15, "bold"), bg="white", bd=3, fg="black", cursor="hand2")
        btn_cashflow.pack(side=TOP, fill=X)
        
        btn_employee = Button(self.LeftMenu, text="Advance Amounts", command=self.advance_amount,
                            font=("times new roman", 15, "bold"), bg="white", bd=3, fg="black", cursor="hand2")
        btn_employee.pack(side=TOP, fill=X)
        
        # Add test button
        btn_test = Button(self.LeftMenu, text="Delay", command=self.delay_amount,
                         font=("times new roman", 15, "bold"), bg="white", bd=3, 
                         fg="black", cursor="hand2")
        btn_test.pack(side=TOP, fill=X)
        
        btn_exit = Button(self.LeftMenu, text="Payouts", command=self.payout_amount,
                         font=("times new roman", 15, "bold"), bg="white", bd=3, fg="black", cursor="hand2")
        
        btn_exit = Button(self.LeftMenu, text="Fixed Transactions", command=self.fixed_transaction,
                         font=("times new roman", 15, "bold"), bg="white", bd=3, fg="black", cursor="hand2")        

        btn_exit.pack(side=TOP, fill=X)

        # footer
        lbl_footer = Label(self.root, 
                         text="CFMS - CashFlow Management System | Developed by Loanitol \n For any technical issue Contact: 94466*****", 
                         font=("times new roman", 15, "bold"), bg="#e50000", fg="white")
        lbl_footer.pack(side=BOTTOM, fill=X)



#====================================================================================

    def all_transaction(self):
        self.new_window = Toplevel(self.root)
        self.new_obj = AllTransaction(self.new_window)

    def advance_amount(self):
        self.new_window = Toplevel(self.root)
        self.new_obj = AdvanceAmount(self.new_window)

    def delay_amount(self):
        self.new_window = Toplevel(self.root)
        self.new_obj = DelayAmount(self.new_window)

    def payout_amount(self):
        self.new_window = Toplevel(self.root)
        self.new_obj = PayoutAmount(self.new_window)

    def fixed_transaction(self):
        self.new_window = Toplevel(self.root)
        self.new_obj = FixedTransaction(self.new_window)

    def one_time(self):
        self.new_window = Toplevel(self.root)
        self.new_obj = OneTime(self.new_window)


if __name__ == "__main__":
    root = Tk()
    obj = IMS(root)
    root.mainloop()