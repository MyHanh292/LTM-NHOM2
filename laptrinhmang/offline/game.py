import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random

SIZE = 30
WIN_COUNT = 5
TIME_LIMIT = 15


def start_game(player_name, avatar_path, mode):
    root = tk.Tk()
    root.title("Cờ Caro")
    GamePage(root, player_name, avatar_path, mode)
    root.mainloop()


class GamePage:
    def __init__(self, root, name, avatar, mode):
        self.root = root
        self.name = name
        self.mode = mode

        self.current = "X"
        self.time = TIME_LIMIT
        self.paused = False
        self.running = True

        # ===== TOP BAR =====
        top = tk.Frame(root)
        top.pack(pady=5)

        img = Image.open(avatar).resize((50, 50))
        self.avatar_img = ImageTk.PhotoImage(img)
        tk.Label(top, image=self.avatar_img).pack(side="left")

        self.info = tk.Label(top, font=("Arial", 12))
        self.info.pack(side="left", padx=10)

        tk.Button(top, text="⏸ Pause", command=self.toggle_pause).pack(side="left", padx=5)
        tk.Button(top, text="❌ Thoát", command=self.confirm_exit).pack(side="left")

        # ===== BOARD =====
        self.board = [["" for _ in range(SIZE)] for _ in range(SIZE)]
        self.btns = [[None]*SIZE for _ in range(SIZE)]

        frame = tk.Frame(root)
        frame.pack()

        for i in range(SIZE):
            for j in range(SIZE):
                b = tk.Button(
                    frame,
                    width=2,
                    height=1,
                    font=("Arial", 8, "bold"),
                    command=lambda x=i, y=j: self.move(x, y)
                )
                b.grid(row=i, column=j)
                self.btns[i][j] = b

        self.update_timer()

    # ================= TIMER =================
    def update_timer(self):
        if not self.running:
            return

        self.info.config(text=f"Lượt {self.current} | ⏳ {self.time}s")

        if not self.paused:
            self.time -= 1
            if self.time <= 0:
                self.switch_turn()

        self.root.after(1000, self.update_timer)

    def toggle_pause(self):
        self.paused = not self.paused

    # ================= EXIT =================
    def confirm_exit(self):
        if messagebox.askyesno(
            "Xác nhận",
            "Bạn chắc chắn muốn thoát?\nBên còn lại sẽ thắng."
        ):
            winner = "O" if self.current == "X" else "X"
            messagebox.showinfo("Kết quả", f"{winner} THẮNG!")
            self.running = False
            self.root.destroy()

    # ================= GAME =================
    def switch_turn(self):
        self.current = "O" if self.current == "X" else "X"
        self.time = TIME_LIMIT

    def move(self, x, y):
        if not self.running or self.paused:
            return
        if self.board[x][y] != "":
            return
        if self.mode == "ai" and self.current == "O":
            return

        self.place(x, y)

        if self.mode == "ai" and self.current == "O":
            self.root.after(150, self.ai_move)

    def place(self, x, y):
        symbol = self.current
        self.board[x][y] = symbol
        self.btns[x][y].config(
            text=symbol,
            fg="red" if symbol == "X" else "green"
        )

        # ✅ CHECK WIN TRƯỚC KHI ĐỔI LƯỢT
        if self.check_win(x, y, symbol):
            messagebox.showinfo("Kết quả", f"{symbol} THẮNG!")
            self.running = False
            return

        self.switch_turn()

    # ================= AI =================
    def ai_move(self):
        if not self.running:
            return

        # 1️⃣ AI thắng
        for i in range(SIZE):
            for j in range(SIZE):
                if self.board[i][j] == "":
                    self.board[i][j] = "O"
                    if self.check_win(i, j, "O"):
                        self.board[i][j] = ""
                        self.place(i, j)
                        return
                    self.board[i][j] = ""

        # 2️⃣ Chặn người
        for i in range(SIZE):
            for j in range(SIZE):
                if self.board[i][j] == "":
                    self.board[i][j] = "X"
                    if self.check_win(i, j, "X"):
                        self.board[i][j] = ""
                        self.place(i, j)
                        return
                    self.board[i][j] = ""

        # 3️⃣ Đánh gần quân đã có
        candidates = []
        for i in range(SIZE):
            for j in range(SIZE):
                if self.board[i][j] != "":
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            x, y = i + dx, j + dy
                            if 0 <= x < SIZE and 0 <= y < SIZE and self.board[x][y] == "":
                                candidates.append((x, y))

        if candidates:
            self.place(*random.choice(candidates))

    # ================= CHECK WIN =================
    def check_win(self, x, y, symbol):
        directions = [(1,0),(0,1),(1,1),(1,-1)]
        for dx, dy in directions:
            count = 1

            i, j = x + dx, y + dy
            while 0 <= i < SIZE and 0 <= j < SIZE and self.board[i][j] == symbol:
                count += 1
                i += dx
                j += dy

            i, j = x - dx, y - dy
            while 0 <= i < SIZE and 0 <= j < SIZE and self.board[i][j] == symbol:
                count += 1
                i -= dx
                j -= dy

            if count >= WIN_COUNT:
                return True
        return False
