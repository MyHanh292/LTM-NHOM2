import tkinter as tk
from offline.login import LoginPage

def start_online():
    root = tk.Tk()
    LoginPage(root)   # dùng lại login offline
    root.mainloop()

if __name__ == "__main__":
    start_online()
