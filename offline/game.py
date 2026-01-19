"""
Cờ Caro Offline - Hỗ trợ chế độ Người vs Người và Người vs AI
- Board: 30x30
- Thắng: 5 quân liên tiếp (ngang, dọc, chéo)
- AI: Dùng heuristic để lựa chọn nước đi tốt nhất
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import json
import os


# ========== CẤU HÌNH ==========
BOARD_SIZE = 30
WIN_COUNT = 5
TIME_LIMIT = 15
USER_FILE = "users.json"


def update_score(username, win):
    """Cập nhật điểm thắng/thua của người chơi"""
    if not os.path.exists(USER_FILE):
        return
    with open(USER_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)

    if username in users:
        if win:
            users[username]["wins"] += 1
        else:
            users[username]["losses"] += 1

    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def start_game(parent, username, avatar, mode, on_close=None):
    """
    Bắt đầu game offline
    - parent: cửa sổ cha
    - username: tên người chơi
    - avatar: đường dẫn ảnh avatar
    - mode: "human" (Người vs Người) hoặc "ai" (Người vs AI)
    - on_close: callback khi game kết thúc
    """
    win = tk.Toplevel(parent)
    win.title("Cờ Caro Offline")
    GamePage(win, parent, username, avatar, mode, on_close)


class GamePage:
    """Giao diện và logic game Caro Offline"""
    
    def __init__(self, root, home, username, avatar, mode, on_close):
        self.root = root
        self.home = home
        self.username = username
        self.avatar = avatar
        self.mode = mode  # "human" hoặc "ai"
        self.on_close = on_close

        self.current = "X"
        self.time = TIME_LIMIT
        self.paused = False
        self.running = True

        # ===== BOARD STATE =====
        self.board = [["" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.btns = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]

        self.setup_ui()
        self.update_timer()

    def setup_ui(self):
        """Tạo giao diện game"""
        # ===== TOP: Avatar & Info =====
        top = tk.Frame(self.root)
        top.pack(fill=tk.X, padx=10, pady=10)

        # Avatar người chơi
        img = Image.open(self.avatar).resize((50, 50))
        self.avatar_img = ImageTk.PhotoImage(img)
        tk.Label(top, image=self.avatar_img).pack(side=tk.LEFT)

        # Thông tin lượt chơi & timer
        self.info = tk.Label(top, text="", font=("Arial", 12, "bold"))
        self.info.pack(side=tk.LEFT, padx=15)

        # Buttons
        tk.Button(top, text="⏸ Pause", command=self.toggle_pause, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="🏠 Quay lại", command=self.go_back, font=("Arial", 10), bg="#FFA500", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="❌ Thoát", command=self.confirm_exit, font=("Arial", 10), bg="#F44336", fg="white").pack(side=tk.LEFT, padx=5)

        # ===== BOARD =====
        board_frame = tk.Frame(self.root, bg="white", relief=tk.SUNKEN, bd=2)
        board_frame.pack(padx=10, pady=10)

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                b = tk.Button(
                    board_frame,
                    width=2,
                    height=1,
                    command=lambda x=i, y=j: self.move(x, y),
                    font=("Arial", 7)
                )
                b.grid(row=i, column=j, padx=0, pady=0)
                self.btns[i][j] = b

    # ========== GAME LOGIC ==========

    def update_timer(self):
        """Cập nhật timer và chuyển lượt nếu hết giờ"""
        if not self.running:
            return
        
        self.info.config(text=f"Lượt {self.current} | {self.time}s")
        
        if not self.paused:
            self.time -= 1
            if self.time <= 0:
                self.switch_turn()
        
        self.root.after(1000, self.update_timer)

    def toggle_pause(self):
        """Tạm dừng/tiếp tục game"""
        self.paused = not self.paused

    def switch_turn(self):
        """Chuyển sang lượt khác"""
        self.current = "O" if self.current == "X" else "X"
        self.time = TIME_LIMIT

    def move(self, x, y):
        """
        Xử lý nước đi của người chơi
        - Nếu chế độ AI: chỉ cho phép người chơi đánh X
        """
        if self.paused or self.board[x][y] != "":
            return
        if self.mode == "ai" and self.current == "O":
            return
        
        self.place(x, y)
        
        # Nếu AI: tự động đánh sau một khoảng thời gian
        if self.mode == "ai" and self.current == "O":
            self.root.after(500, self.ai_move)

    def place(self, x, y):
        """
        Đặt quân cờ tại vị trí (x, y)
        - Kiểm tra thắng/thua
        - Chuyển lượt
        """
        sym = self.current
        self.board[x][y] = sym

        # Hiển thị quân cờ với màu khác nhau
        color = "red" if sym == "X" else "green"
        self.btns[x][y].config(text=sym, fg=color)

        # Kiểm tra thắng
        if self.check_win(x, y, sym):
            update_score(self.username, sym == "X")
            winner_name = "Bạn" if sym == "X" else "Đối thủ"
            messagebox.showinfo("🎉 Kết thúc", f"{winner_name} ({sym}) THẮNG!")
            self.close_game()
            return

        self.switch_turn()

    # ========== AI LOGIC ==========

    def ai_move(self):
        """
        AI tự động chọn nước đi tốt nhất
        1. Kiểm tra nước thắng ngay cho O
        2. Kiểm tra chặn nước thắng của X
        3. Dùng heuristic để chọn nước tốt nhất
        """
        # 1️⃣ Nếu AI có thể thắng ngay → đánh
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == "":
                    self.board[i][j] = "O"
                    if self.check_win(i, j, "O"):
                        self.board[i][j] = ""
                        self.place(i, j)
                        return
                    self.board[i][j] = ""

        # 2️⃣ Nếu đối thủ (X) có thể thắng ngay → chặn
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == "":
                    self.board[i][j] = "X"
                    if self.check_win(i, j, "X"):
                        self.board[i][j] = ""
                        self.place(i, j)
                        return
                    self.board[i][j] = ""

        # 3️⃣ Đánh giá nước đi bằng heuristic
        def max_line_length(x, y, sym):
            """Tính độ dài đường thẳng tối đa nếu đặt quân tại (x, y)"""
            best = 0
            for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                cnt = 1
                for k in [1, -1]:
                    i, j = x + dx * k, y + dy * k
                    while 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE and self.board[i][j] == sym:
                        cnt += 1
                        i += dx * k
                        j += dy * k
                if cnt > best:
                    best = cnt
            return best

        moves = [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if self.board[i][j] == ""]
        if not moves:
            return

        best_move = None
        best_score = -10**9
        center = BOARD_SIZE // 2

        for i, j in moves:
            # Tấn công: tạo hàng dài cho O
            offense = max_line_length(i, j, "O")
            # Phòng thủ: chặn hàng dài của X
            defense = max_line_length(i, j, "X")
            # Score: ưu tiên tấn công, rồi phòng thủ, ưu tiên ô gần tâm
            score = offense * 100 + defense * 90 - (abs(i - center) + abs(j - center))

            if score > best_score:
                best_score = score
                best_move = (i, j)

        if best_move:
            self.place(*best_move)
        else:
            self.place(*random.choice(moves))

    def check_win(self, x, y, sym):
        """
        Kiểm tra xem vị trí (x, y) có tạo thành 5 quân liên tiếp không
        - Kiểm tra 4 hướng: ngang, dọc, chéo /, chéo \\
        """
        for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            cnt = 1
            # Kiểm tra 2 phía
            for k in [1, -1]:
                i, j = x + dx * k, y + dy * k
                while 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE and self.board[i][j] == sym:
                    cnt += 1
                    i += dx * k
                    j += dy * k
            if cnt >= WIN_COUNT:
                return True
        return False

    # ========== UI ACTIONS ==========

    def go_back(self):
        """Quay lại trang chủ (không cộng điểm)"""
        if messagebox.askyesno("Quay lại", "Bạn chắc muốn quay lại?"):
            self.close_game()

    def confirm_exit(self):
        """Thoát game (cộng 1 lần thua)"""
        if messagebox.askyesno("Thoát", "Thoát = thua. Bạn chắc chứ?"):
            update_score(self.username, False)
            self.close_game()

    def close_game(self):
        """Đóng game window và quay lại home"""
        self.running = False
        self.root.destroy()
        self.home.deiconify()
        if self.on_close:
            self.on_close()
