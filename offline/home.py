"""
Cờ Caro - Trang Chủ
- Chọn chế độ chơi (Offline hoặc Online)
- Chọn avatar
- Xem bảng xếp hạng
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import os, json

from offline.game import start_game   # OFFLINE GAME

AVATAR_DIR = "offline/avatars"
USER_FILE = "users.json"


def start_home(username):
    root = tk.Tk()
    HomePage(root, username)
    root.mainloop()


class HomePage:
    def __init__(self, root, username):
        self.root = root
        self.username = username

        root.title("Trang Chủ - Cờ Caro 30x30")
        root.geometry("850x700")

        tk.Label(root, text=f"👋 Xin chào {username}", font=("Arial", 14)).pack(pady=5)
        tk.Label(root, text="🎮 CỜ CARO 30×30", font=("Arial", 24, "bold")).pack(pady=10)

        # ===== AVATAR =====
        tk.Label(root, text="Chọn Avatar", font=("Arial", 11, "bold")).pack(pady=5)
        self.avatar_path = tk.StringVar()

        frame = tk.Frame(root)
        frame.pack(pady=5)

        self.img_refs = []
        avatar_files = [f for f in os.listdir(AVATAR_DIR) if f.lower().endswith((".jpg", ".png"))]
        
        if avatar_files:
            for f in avatar_files:
                path = os.path.join(AVATAR_DIR, f)
                img = Image.open(path).resize((70, 70))
                photo = ImageTk.PhotoImage(img)
                self.img_refs.append(photo)

                tk.Radiobutton(
                    frame,
                    image=photo,
                    variable=self.avatar_path,
                    value=path
                ).pack(side="left", padx=10)
        else:
            tk.Label(frame, text="❌ Không tìm thấy avatar").pack()

        # ===== MODE =====
        tk.Label(root, text="Chế độ chơi", font=("Arial", 11, "bold")).pack(pady=10)
        self.mode = tk.StringVar(value="ai")

        tk.Radiobutton(
            root, text="👥 Offline – Người vs Người",
            variable=self.mode, value="human", font=("Arial", 10)
        ).pack(anchor="w", padx=50)

        tk.Radiobutton(
            root, text="🤖 Offline – Người vs AI",
            variable=self.mode, value="ai", font=("Arial", 10)
        ).pack(anchor="w", padx=50)

        tk.Radiobutton(
            root, text="⚡ Online – Tìm người chơi ngẫu nhiên",
            variable=self.mode, value="online_random", font=("Arial", 10)
        ).pack(anchor="w", padx=50)

        tk.Radiobutton(
            root, text="👨‍👩‍👧 Online – Chơi với bạn bè (Room Code)",
            variable=self.mode, value="online_friends", font=("Arial", 10)
        ).pack(anchor="w", padx=50)

        tk.Button(
            root,
            text="🚀 BẮT ĐẦU CHƠI",
            font=("Arial", 13, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20, pady=10,
            command=self.start_game_click
        ).pack(pady=15)

        # ===== RANKING =====
        tk.Label(
            root,
            text="🏆 BẢNG XẾP HẠNG (Offline)",
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        self.rank_box = tk.Text(root, height=7, width=100)
        self.rank_box.pack(padx=10, pady=5)
        self.show_ranking()

    # ===== BẢNG XẾP HẠNG =====
    def show_ranking(self):
        self.rank_box.delete("1.0", tk.END)
        if not os.path.exists(USER_FILE):
            self.rank_box.insert(tk.END, "Chưa có dữ liệu")
            return

        try:
            with open(USER_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)

            ranking = sorted(
                users.items(),
                key=lambda x: (x[1].get("wins", 0), -x[1].get("losses", 0)),
                reverse=True
            )

            for i, (u, d) in enumerate(ranking[:20], 1):
                wins = d.get("wins", 0)
                losses = d.get("losses", 0)
                self.rank_box.insert(
                    tk.END,
                    f"{i:2d}. {u:20s} | Thắng: {wins:3d} | Thua: {losses:3d}\n"
                )
        except Exception as e:
            self.rank_box.insert(tk.END, f"Lỗi: {e}")

    # ===== CLICK BẮT ĐẦU =====
    def start_game_click(self):
        if not self.avatar_path.get():
            messagebox.showerror("Lỗi", "❌ Chưa chọn avatar!")
            return

        mode = self.mode.get()
        self.root.withdraw()

        # ===== OFFLINE =====
        if mode in ["human", "ai"]:
            start_game(
                self.root,
                self.username,
                self.avatar_path.get(),
                mode,
                on_close=self.show_ranking
            )

        # ===== ONLINE RANDOM =====
        elif mode == "online_random":
            self.start_online("random")

        # ===== ONLINE FRIENDS =====
        elif mode == "online_friends":
            self.start_online("friends")

    def start_online(self, online_mode):
        """Bắt đầu chế độ online"""
        try:
            from online.online_game import CaroClient
        except ImportError as e:
            messagebox.showerror(
                "Lỗi",
                f"❌ Không tìm thấy module Online.\nLỗi: {e}"
            )
            self.root.deiconify()
            return

        # Load config
        config_file = "config.json"
        default_ip = "127.0.0.1"
        
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    default_ip = cfg.get("server_ip", "127.0.0.1").split(":")[0]
            except:
                pass
        
        # Hỏi địa chỉ server
        server_ip = simpledialog.askstring(
            "🔗 Kết nối Server",
            f"Nhập IP server:\n(để trống = {default_ip})\n\nVí dụ: 127.0.0.1 hoặc 192.168.1.100",
        )
        
        if server_ip is None:  # Cancel
            self.root.deiconify()
            return
        
        if not server_ip:
            server_ip = default_ip
        
        # Xóa :9999 nếu user nhập
        if ':' in server_ip:
            server_ip = server_ip.split(':')[0]
        
        # Validate IP
        import re
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, server_ip):
            messagebox.showerror("Lỗi", f"IP không hợp lệ: {server_ip}")
            self.root.deiconify()
            return
        
        parts = server_ip.split('.')
        for part in parts:
            if int(part) > 255:
                messagebox.showerror("Lỗi", f"IP không hợp lệ: {server_ip}\n(Mỗi phần phải ≤ 255)")
                self.root.deiconify()
                return
        
        # Save config
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump({"server_ip": server_ip, "server_port": 9999}, f, indent=4)
        except:
            pass

        win = tk.Toplevel(self.root)
        win.title("Cờ Caro Online")
        win.geometry("500x650")
        
        # Truyền username và avatar cho client
        CaroClient(win, username=self.username, avatar_path=self.avatar_path.get())

