# alltransaction.py
from tkinter import *
from tkinter import ttk, messagebox
import datetime
import calendar
import sqlite3
from datetime import datetime, timedelta


class AllTransaction:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1350x700+0+0")
        self.root.title("All Transactions")
        self.root.config(bg="white")
        self.root.focus_force()

        

if __name__ == "__main__":
    root = Tk()
    obj = AllTransaction(root)
    root.mainloop()