from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import datetime

class FixedTransaction:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1110x500+220+130")
        self.root.title("Fixed Transactions")
        self.root.config(bg="white")
        self.root.focus_force()
    


if __name__ == "__main__":
    root = Tk()
    obj = FixedTransaction(root)
    root.mainloop()