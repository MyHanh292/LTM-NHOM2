import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from offline.login import LoginPage

def start_online():
    root = tk.Tk()
    LoginPage(root)   # dùng lại login offline
    root.mainloop()

if __name__ == "__main__":
    start_online()
