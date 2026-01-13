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

        root.title("Trang Chủ")
        root.geometry("700x550")

        tk.Label(root, text=f"Xin chào {username}", font=("Arial", 14)).pack(pady=5)
        tk.Label(root, text="CỜ CARO 30x30", font=("Arial", 20, "bold")).pack(pady=5)

        # ===== AVATAR =====
        tk.Label(root, text="Chọn Avatar").pack()
        self.avatar_path = tk.StringVar()

        frame = tk.Frame(root)
        frame.pack(pady=5)

        self.img_refs = []
        for f in os.listdir(AVATAR_DIR):
            if f.lower().endswith((".jpg", ".png")):
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

        # ===== MODE =====
        tk.Label(root, text="Chế độ chơi").pack(pady=5)
        self.mode = tk.StringVar(value="ai")

        tk.Radiobutton(
            root, text="Offline – Người vs Người",
            variable=self.mode, value="human"
        ).pack()

        tk.Radiobutton(
            root, text="Offline – Người vs AI",
            variable=self.mode, value="ai"
        ).pack()

        tk.Radiobutton(
            root, text="Online – Client (qua Server)",
            variable=self.mode, value="online"
        ).pack()

        tk.Button(
            root,
            text="BẮT ĐẦU",
            font=("Arial", 14),
            bg="green",
            fg="white",
            command=self.start_game_click
        ).pack(pady=10)

        # ===== RANKING =====
        tk.Label(
            root,
            text="🏆 BẢNG XẾP HẠNG (Offline)",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        self.rank_box = tk.Text(root, height=8, width=50)
        self.rank_box.pack()
        self.show_ranking()

    # ===== BẢNG XẾP HẠNG =====
    def show_ranking(self):
        self.rank_box.delete("1.0", tk.END)
        if not os.path.exists(USER_FILE):
            return

        with open(USER_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)

        ranking = sorted(users.items(), key=lambda x: x[1]["wins"], reverse=True)

        for i, (u, d) in enumerate(ranking, 1):
            self.rank_box.insert(
                tk.END,
                f"{i}. {u} | Thắng: {d['wins']} | Thua: {d['losses']}\n"
            )

    # ===== CLICK BẮT ĐẦU =====
    def start_game_click(self):
        if not self.avatar_path.get():
            messagebox.showerror("Lỗi", "Chưa chọn avatar")
            return

        mode = self.mode.get()
        self.root.withdraw()

        # ===== ONLINE =====
        if mode == "online":
            try:
                from online.online_game import OnlineGamePage
            except ImportError:
                messagebox.showerror(
                    "Lỗi",
                    "Không tìm thấy module Online.\nHãy chạy server trước!"
                )
                self.root.deiconify()
                return

            # hỏi địa chỉ server (mặc định localhost)
            server_ip = simpledialog.askstring(
                "Địa chỉ Server",
                "Nhập địa chỉ IP server:\n(không nhập = localhost)",
            )
            if not server_ip:
                server_ip = "127.0.0.1"

            win = tk.Toplevel(self.root)
            OnlineGamePage(
                win,
                home=self.root,
                username=self.username,
                avatar=self.avatar_path.get(),
                server_ip=server_ip
            )

        # ===== OFFLINE =====
        else:
            start_game(
                self.root,
                self.username,
                self.avatar_path.get(),
                mode,
                on_close=self.show_ranking
            )
