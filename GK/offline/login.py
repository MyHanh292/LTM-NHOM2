"""
Cờ Caro - Trang Đăng nhập/Đăng ký
- Quản lý tài khoản người dùng
- Mã hóa mật khẩu bằng SHA256
- Tự động di cư từ plaintext sang mã hóa
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import hashlib
import sys

# Fix sys.path để có thể import từ parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from offline.home import start_home


def start_online_game(username, avatar=""):
    """Khởi động game online trực tiếp"""
    import tkinter as tk
    from online.online_game import CaroClient
    
    root = tk.Tk()
    client = CaroClient(root, username=username, avatar_path=avatar)
    root.mainloop()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_FILE = os.path.join(BASE_DIR, "users.json")


# ========== USER MANAGEMENT ==========

def load_users():
    """Tải dữ liệu người dùng từ users.json"""
    if not os.path.exists(USER_FILE):
        return {}
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_users(users):
    """Lưu dữ liệu người dùng vào users.json"""
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def hash_password(password: str, username: str) -> str:
    """
    Mã hóa mật khẩu bằng SHA256
    - Sử dụng username làm salt
    - Đảm bảo độ an toàn cơ bản
    """
    return hashlib.sha256((username + password).encode("utf-8")).hexdigest()


# ========== LOGIN UI ==========

class LoginPage:
    """Giao diện đăng nhập/đăng ký"""
    
    def __init__(self, root, mode="login", username="", avatar=""):
        self.root = root
        self.mode = mode
        self.auto_username = username
        self.auto_avatar = avatar
        
        root.title("Cờ Caro - Đăng nhập")
        root.geometry("350x300")
        root.resizable(False, False)

        # ===== HEADER =====
        tk.Label(root, text="🎮 CỜ CARO", font=("Arial", 24, "bold")).pack(pady=10)

        # ===== FORM =====
        tk.Label(root, text="Tên đăng nhập", font=("Arial", 10)).pack(anchor="w", padx=30)
        self.username = tk.Entry(root, font=("Arial", 10))
        self.username.pack(padx=30, pady=5, fill=tk.X)
        if username:
            self.username.insert(0, username)

        tk.Label(root, text="Mật khẩu", font=("Arial", 10)).pack(anchor="w", padx=30)
        self.password = tk.Entry(root, show="*", font=("Arial", 10))
        self.password.pack(padx=30, pady=5, fill=tk.X)

        # ===== BUTTONS =====
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame,
            text="Đăng nhập",
            command=self.login,
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=15, pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Đăng ký",
            command=self.register,
            font=("Arial", 11, "bold"),
            bg="#2196F3",
            fg="white",
            padx=15, pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            root,
            text="🔑 Quên mật khẩu?",
            command=self.forgot_password,
            font=("Arial", 9),
            bg="white",
            fg="#FF9800"
        ).pack(pady=5)

    def register(self):
        """Đăng ký tài khoản mới"""
        users = load_users()
        u = self.username.get().strip()
        p = self.password.get().strip()

        # Kiểm tra hợp lệ
        if not u or not p:
            messagebox.showerror("❌ Lỗi", "Không được để trống tên hoặc mật khẩu!")
            return
        
        if len(u) < 3:
            messagebox.showerror("❌ Lỗi", "Tên tài khoản phải ít nhất 3 ký tự!")
            return
        
        if len(p) < 4:
            messagebox.showerror("❌ Lỗi", "Mật khẩu phải ít nhất 4 ký tự!")
            return
        
        if u in users:
            messagebox.showerror("❌ Lỗi", "Tài khoản này đã tồn tại!")
            return

        # Tạo tài khoản mới
        users[u] = {
            "password": hash_password(p, u),
            "wins": 0,
            "losses": 0
        }
        save_users(users)
        messagebox.showinfo("✅ Thành công", "Đăng ký tài khoản thành công!\nBây giờ bạn có thể đăng nhập.")
        
        # Xóa form
        self.username.delete(0, tk.END)
        self.password.delete(0, tk.END)

    def login(self):
        """Đăng nhập tài khoản"""
        users = load_users()
        u = self.username.get().strip()
        p = self.password.get().strip()

        if not u or not p:
            messagebox.showerror("❌ Lỗi", "Nhập đầy đủ tên đăng nhập và mật khẩu!")
            return

        if u not in users:
            messagebox.showerror("❌ Lỗi", "Sai tên tài khoản hoặc mật khẩu!")
            return

        stored = users[u]["password"]
        hashed = hash_password(p, u)

        # Hỗ trợ cả mật khẩu plaintext (cũ) và mã hóa (mới)
        if stored != p and stored != hashed:
            messagebox.showerror("❌ Lỗi", "Sai tên tài khoản hoặc mật khẩu!")
            return

        # Di cư mật khẩu plaintext → mã hóa
        if stored != hashed:
            users[u]["password"] = hashed
            save_users(users)
            messagebox.showinfo("ℹ️ Thông báo", "Mật khẩu đã được cập nhật (bảo mật hơn)")

        # Đăng nhập thành công → vào trang chủ
        self.root.destroy()
        
        # Nếu mode = online thì nhảy trực tiếp vào game online
        if self.mode == "online":
            start_online_game(u, self.auto_avatar)
        else:
            start_home(u)

    def forgot_password(self):
        """Đặt lại mật khẩu"""
        users = load_users()
        username = self.username.get().strip()

        if not username:
            messagebox.showerror("❌ Lỗi", "Nhập tên tài khoản trước!")
            return

        if username not in users:
            messagebox.showerror("❌ Lỗi", "Tài khoản không tồn tại!")
            return

        new_pass = simpledialog.askstring(
            "Đặt lại mật khẩu",
            "Nhập mật khẩu mới (tối thiểu 4 ký tự):",
            show="*"
        )

        if not new_pass:
            return
        
        if len(new_pass) < 4:
            messagebox.showerror("❌ Lỗi", "Mật khẩu phải ít nhất 4 ký tự!")
            return

        users[username]["password"] = hash_password(new_pass, username)
        save_users(users)

        messagebox.showinfo("✅ Thành công", "Mật khẩu đã được đặt lại!\nBạn có thể đăng nhập ngay.")


# Alias cho test script
LoginWindow = LoginPage


if __name__ == "__main__":
    root = tk.Tk()
    LoginPage(root)
    root.mainloop()
