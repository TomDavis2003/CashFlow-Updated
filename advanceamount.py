from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import datetime
import sqlite3
from datetime import datetime, timedelta
from tkinter import messagebox

class AdvanceAmount:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1110x500+220+130")
        self.root.title("Advance Amounts")
        self.root.config(bg="white")
        self.root.focus_force()

        



if __name__ == "__main__":
    root = Tk()
    obj = AdvanceAmount(root)
    root.mainloop()