import tkinter as tk
from tkinter import messagebox, simpledialog
import json, os
import hashlib

from offline.home import start_home

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_FILE = os.path.join(BASE_DIR, "users.json")


def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def hash_password(password: str, username: str) -> str:
    # simple salted hash using username as salt
    return hashlib.sha256((username + password).encode("utf-8")).hexdigest()


class LoginPage:
    def __init__(self, root):
        self.root = root
        root.title("Đăng nhập")
        root.geometry("350x300")

        tk.Label(root, text="ĐĂNG NHẬP", font=("Arial", 18, "bold")).pack(pady=10)

        tk.Label(root, text="Tên đăng nhập").pack()
        self.username = tk.Entry(root)
        self.username.pack()

        tk.Label(root, text="Mật khẩu").pack()
        self.password = tk.Entry(root, show="*")
        self.password.pack()

        tk.Button(root, text="Đăng nhập", command=self.login).pack(pady=5)
        tk.Button(root, text="Đăng ký", command=self.register).pack()
        tk.Button(root, text="Quên mật khẩu?", command=self.forgot_password).pack(pady=5)

    def register(self):
        users = load_users()
        u, p = self.username.get().strip(), self.password.get().strip()

        if not u or not p:
            messagebox.showerror("Lỗi", "Không được để trống")
            return
        if u in users:
            messagebox.showerror("Lỗi", "Tài khoản đã tồn tại")
            return

        users[u] = {"password": hash_password(p, u), "wins": 0, "losses": 0}
        save_users(users)
        messagebox.showinfo("OK", "Đăng ký thành công")

    def login(self):
        users = load_users()
        u, p = self.username.get().strip(), self.password.get().strip()

        if u not in users:
            messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu")
            return

        stored = users[u]["password"]
        hashed = hash_password(p, u)

        # support existing plaintext passwords: accept if stored equals plain or hashed
        if stored != p and stored != hashed:
            messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu")
            return

        # migrate to hashed password if stored was plaintext
        if stored != hashed:
            users[u]["password"] = hashed
            save_users(users)

        self.root.destroy()
        start_home(u)

    def forgot_password(self):
        users = load_users()
        username = self.username.get().strip()

        if not username:
            messagebox.showerror("Lỗi", "Nhập tên đăng nhập trước")
            return

        if username not in users:
            messagebox.showerror("Lỗi", "Tài khoản không tồn tại")
            return

        new_pass = simpledialog.askstring(
            "Đặt lại mật khẩu",
            "Nhập mật khẩu mới:",
            show="*"
        )

        if not new_pass:
            return

        users[username]["password"] = hash_password(new_pass, username)
        save_users(users)

        messagebox.showinfo("Thành công", "Mật khẩu đã được đặt lại")


if __name__ == "__main__":
    root = tk.Tk()
    LoginPage(root)
    root.mainloop()
