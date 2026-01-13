import socket
import threading
from tkinter import messagebox
from offline.game import GamePage, update_score

PORT = 9999


class OnlineGamePage(GamePage):
    def __init__(self, root, home, username, avatar, server_ip=None):
        # ===== TRẠNG THÁI ONLINE =====
        self.my_symbol = None
        self.my_turn = False
        self.started = False
        self.sock = None

        # ===== TẠO UI GAME (NHƯ OFFLINE) =====
        super().__init__(
            root,
            home,
            username,
            avatar,
            mode="online",
            on_close=self.on_close_online
        )

        # ⚠️ CHƯA CHO ĐÁNH – CHỜ SERVER
        self.info.config(text="⏳ Đang chờ người chơi khác...")

        # ===== KẾT NỐI SERVER =====
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            addr = server_ip if server_ip else "127.0.0.1"
            self.sock.connect((addr, PORT))
        except:
            messagebox.showerror("Lỗi", "Không kết nối được server")
            root.destroy()
            if home:
                home.deiconify()
            return

        # ===== LUỒNG NHẬN DỮ LIỆU =====
        threading.Thread(target=self.receive, daemon=True).start()

    # ==================================================
    # ❌ KHÔNG cho đánh khi:
    #   - chưa START
    #   - không tới lượt mình
    # ==================================================
    def move(self, x, y):
        if not self.started:
            return
        if not self.my_turn:
            return

        try:
            self.sock.send(f"MOVE {x} {y}".encode())
        except:
            pass

    # ==================================================
    # NHẬN DỮ LIỆU TỪ SERVER
    # ==================================================
    def receive(self):
        while True:
            try:
                msg = self.sock.recv(1024).decode()
                if not msg:
                    break

                parts = msg.split()

                # ===== SERVER BÁO BẮT ĐẦU =====
                if parts[0] == "START":
                    self.my_symbol = parts[1]
                    self.current = "X"
                    self.started = True
                    self.my_turn = (self.my_symbol == "X")

                    self.info.config(
                        text=f"Bạn là {self.my_symbol} | "
                             f"{'Đến lượt bạn' if self.my_turn else 'Chờ đối thủ'}"
                    )

                # ===== SERVER GỬI NƯỚC ĐI =====
                elif parts[0] == "MOVE":
                    _, x, y, s = parts
                    x, y = int(x), int(y)

                    # CẬP NHẬT BÀN CỜ
                    self.board[x][y] = s
                    self.btns[x][y].config(
                        text=s,
                        fg="red" if s == "X" else "green"
                    )

                    # ĐỔI LƯỢT
                    self.current = "O" if s == "X" else "X"
                    self.my_turn = (self.current == self.my_symbol)

                    self.info.config(
                        text=f"Bạn là {self.my_symbol} | "
                             f"{'Đến lượt bạn' if self.my_turn else 'Chờ đối thủ'}"
                    )

                # ===== SERVER BÁO KẾT THÚC =====
                elif parts[0] == "END":
                    winner = parts[1]
                    win = (winner == self.my_symbol)
                    try:
                        update_score(self.username, win)
                    except:
                        pass
                    messagebox.showinfo("Kết quả", f"{winner} THẮNG!")
                    self.close_game()

                # ===== ĐỐI THỦ NGẮT KẾT NỐI =====
                elif parts[0] == "DISCONNECT":
                    messagebox.showinfo("Kết nối", "Đối thủ đã ngắt kết nối")
                    self.close_game()

            except:
                break

    # ==================================================
    # THOÁT GAME ONLINE
    # ==================================================
    def on_close_online(self):
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
