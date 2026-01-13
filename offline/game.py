import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random, json, os

SIZE = 30
WIN_COUNT = 5
TIME_LIMIT = 15
USER_FILE = "users.json"


def update_score(username, win):
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
    win = tk.Toplevel(parent)
    win.title("Cờ Caro")
    GamePage(win, parent, username, avatar, mode, on_close)


class GamePage:
    def __init__(self, root, home, username, avatar, mode, on_close):
        self.root = root
        self.home = home
        self.username = username
        self.mode = mode
        self.on_close = on_close

        self.current = "X"
        self.time = TIME_LIMIT
        self.paused = False
        self.running = True

        # ===== TOP =====
        top = tk.Frame(root)
        top.pack()

        img = Image.open(avatar).resize((50, 50))
        self.avatar_img = ImageTk.PhotoImage(img)
        tk.Label(top, image=self.avatar_img).pack(side="left")

        self.info = tk.Label(top)
        self.info.pack(side="left", padx=10)

        tk.Button(top, text="⏸ Pause", command=self.toggle_pause).pack(side="left")
        tk.Button(top, text="❌ Thoát", command=self.confirm_exit).pack(side="left")

        # ===== BOARD =====
        self.board = [["" for _ in range(SIZE)] for _ in range(SIZE)]
        self.btns = [[None]*SIZE for _ in range(SIZE)]

        frame = tk.Frame(root)
        frame.pack()

        for i in range(SIZE):
            for j in range(SIZE):
                b = tk.Button(
                    frame, width=2, height=1,
                    command=lambda x=i, y=j: self.move(x, y)
                )
                b.grid(row=i, column=j)
                self.btns[i][j] = b

        self.update_timer()

    # ===== TIMER =====
    def update_timer(self):
        if not self.running:
            return
        self.info.config(text=f"Lượt {self.current} | {self.time}s")
        if not self.paused:
            self.time -= 1
            if self.time <= 0:
                self.switch()
        self.root.after(1000, self.update_timer)

    def toggle_pause(self):
        self.paused = not self.paused

    def switch(self):
        self.current = "O" if self.current == "X" else "X"
        self.time = TIME_LIMIT

    # ===== GAME =====
    def move(self, x, y):
        if self.paused or self.board[x][y] != "":
            return
        if self.mode == "ai" and self.current == "O":
            return
        self.place(x, y)
        if self.mode == "ai" and self.current == "O":
            self.root.after(150, self.ai_move)

    def place(self, x, y):
        s = self.current
        self.board[x][y] = s

        # ✅ MÀU QUÂN CỜ
        self.btns[x][y].config(
            text=s,
            fg="red" if s == "X" else "green"
        )

        if self.check_win(x, y, s):
            update_score(self.username, s == "X")
            messagebox.showinfo("Kết quả", f"{s} THẮNG!")
            self.close_game()
            return

        self.switch()

    # ===== AI =====
    def ai_move(self):
        # 1) Nếu có nước thắng ngay cho O -> đi
        for i in range(SIZE):
            for j in range(SIZE):
                if self.board[i][j] == "":
                    self.board[i][j] = "O"
                    if self.check_win(i, j, "O"):
                        self.board[i][j] = ""
                        self.place(i, j)
                        return
                    self.board[i][j] = ""

        # 2) Nếu đối thủ có thể thắng ngay (X) -> chặn
        for i in range(SIZE):
            for j in range(SIZE):
                if self.board[i][j] == "":
                    self.board[i][j] = "X"
                    if self.check_win(i, j, "X"):
                        self.board[i][j] = ""
                        self.place(i, j)
                        return
                    self.board[i][j] = ""

        # 3) Đánh giá các nước đi còn lại bằng heuristic đơn giản
        def max_line_length(x, y, sym):
            best = 0
            for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                cnt = 1
                for k in [1, -1]:
                    i, j = x + dx * k, y + dy * k
                    while 0 <= i < SIZE and 0 <= j < SIZE and self.board[i][j] == sym:
                        cnt += 1
                        i += dx * k
                        j += dy * k
                if cnt > best:
                    best = cnt
            return best

        moves = [(i, j) for i in range(SIZE) for j in range(SIZE) if self.board[i][j] == ""]
        if not moves:
            return

        best_move = None
        best_score = -10**9
        center = SIZE // 2

        for i, j in moves:
            # trọng số: ưu tiên nước giúp O mạnh, rồi chặn X
            off = max_line_length(i, j, "O")
            deff = max_line_length(i, j, "X")
            # score: tấn công + phòng thủ, ưu tiên ô gần tâm
            score = off * 100 + deff * 90 - (abs(i - center) + abs(j - center))

            if score > best_score:
                best_score = score
                best_move = (i, j)

        if best_move:
            self.place(*best_move)
        else:
            self.place(*random.choice(moves))

    def check_win(self, x, y, s):
        for dx, dy in [(1,0),(0,1),(1,1),(1,-1)]:
            cnt = 1
            for k in [1, -1]:
                i, j = x+dx*k, y+dy*k
                while 0 <= i < SIZE and 0 <= j < SIZE and self.board[i][j] == s:
                    cnt += 1
                    i += dx*k
                    j += dy*k
            if cnt >= WIN_COUNT:
                return True
        return False

    def confirm_exit(self):
        if messagebox.askyesno("Thoát", "Thoát = thua. Bạn chắc chứ?"):
            update_score(self.username, False)
            self.close_game()

    def close_game(self):
        self.root.destroy()
        self.home.deiconify()
        if self.on_close:
            self.on_close()
