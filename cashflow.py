from tkinter import *
import sqlite3
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import datetime
import threading
from datetime import timedelta

class cashflowClass:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1000x600+220+130")
        self.root.title("CashFlow Management System")
        self.root.config(bg="white")
        self.root.focus_force()
        self.all_entries = []  # store all transactions

        #====content====
        self.lbl_all_transactions = Label(self.root, text="All Transactions", font=("times new roman", 20, "bold"), bg="white", fg="#e50000")
        self.lbl_all_transactions.place(x=100,y=20, height=150,width=300)

if __name__ == "__main__":
    root = Tk()
    obj = cashflowClass(root)
    root.mainloop()

