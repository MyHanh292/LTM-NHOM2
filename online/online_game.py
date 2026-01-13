import socket
import threading
from tkinter import messagebox, simpledialog
import tkinter as tk
from offline.game import GamePage, update_score

PORT = 9999


class OnlineGamePage(GamePage):
    def __init__(self, root, home, username, avatar, server_ip=None, mode="random"):
        # ===== TRẠNG THÁI ONLINE =====
        self.my_symbol = None
        self.my_turn = False
        self.started = False
        self.sock = None
        self.mode = mode
        self.opponent_name = None

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
        self.info.config(text="⏳ Đang kết nối server...")

        # ===== KẾT NỐI SERVER =====
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            addr = server_ip if server_ip else "127.0.0.1"
            self.sock.connect((addr, PORT))
            
            # Gửi tên user
            self.sock.send(f"USER {username}".encode())
            
            # Vào queue matching nếu chế độ random
            if self.mode == "random":
                self.sock.send("QUEUE_MATCH".encode())
                self.info.config(text="⏳ Đang tìm người chơi...")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không kết nối được server: {e}")
            root.destroy()
            if home:
                home.deiconify()
            return

        # ===== LUỒNG NHẬN DỮ LIỆU =====
        threading.Thread(target=self.receive, daemon=True).start()

    # ==================================================
    # ĐÁNH NƯỚC
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

                parts = msg.split(maxsplit=3)

                # ===== SERVER BÁO BẮT ĐẦU =====
                if parts[0] == "START":
                    self.my_symbol = parts[1]
                    self.opponent_name = parts[3] if len(parts) > 3 else "Opponent"
                    self.current = "X"
                    self.started = True
                    self.my_turn = (self.my_symbol == "X")

                    self.info.config(
                        text=f"vs {self.opponent_name} | Bạn: {self.my_symbol} | "
                             f"{'Đến lượt bạn' if self.my_turn else 'Chờ đối thủ'}"
                    )

                # ===== SERVER GỬI NƯỚC ĐI =====
                elif parts[0] == "MOVE":
                    x, y = int(parts[1]), int(parts[2])
                    sym = parts[3]

                    # CẬP NHẬT BÀN CỜ
                    self.board[x][y] = sym
                    self.btns[x][y].config(
                        text=sym,
                        fg="red" if sym == "X" else "green"
                    )

                    # ĐỔI LƯỢT
                    self.current = "O" if sym == "X" else "X"
                    self.my_turn = (self.current == self.my_symbol)

                    self.info.config(
                        text=f"vs {self.opponent_name} | Bạn: {self.my_symbol} | "
                             f"{'Đến lượt bạn' if self.my_turn else 'Chờ đối thủ'}"
                    )

                # ===== SERVER BÁO KẾT THÚC =====
                elif parts[0] == "END":
                    winner = parts[1]
                    winner_name = parts[2] if len(parts) > 2 else winner
                    win = (winner == self.my_symbol)
                    try:
                        update_score(self.username, win)
                    except:
                        pass
                    messagebox.showinfo("Kết quả", f"{winner_name} ({winner}) THẮNG!")
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


class OnlineFriendsPage(tk.Frame):
    """Trang chơi với bạn bè"""
    def __init__(self, root, home, username, avatar, server_ip=None):
        super().__init__(root)
        self.root = root
        self.home = home
        self.username = username
        self.avatar = avatar
        self.server_ip = server_ip if server_ip else "127.0.0.1"
        
        root.title("Chơi với bạn bè")
        root.geometry("400x500")
        
        self.sock = None
        self.friends_online = []
        
        # ===== UI =====
        tk.Label(root, text="Chơi với bạn bè", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Nút: Mời bạn
        tk.Button(root, text="📤 Mời bạn", command=self.invite_friend, width=20).pack(pady=5)
        
        # Danh sách bạn online
        tk.Label(root, text="Bạn bè đang online:").pack()
        self.friends_listbox = tk.Listbox(root, height=8, width=40)
        self.friends_listbox.pack(pady=5)
        
        # Nút: Yêu cầu chơi với bạn
        tk.Button(root, text="🎮 Yêu cầu chơi", command=self.request_play, width=20).pack(pady=5)
        
        # Nút: Tạo mã phòng
        tk.Button(root, text="🔑 Tạo mã phòng để bạn tham gia", command=self.create_room_code, width=20).pack(pady=5)
        
        # Nút: Nhập mã phòng
        tk.Button(root, text="🔐 Nhập mã phòng", command=self.join_room_code, width=20).pack(pady=5)
        
        # Nút: Quay lại
        tk.Button(root, text="⬅️ Quay lại", command=self.go_back, width=20).pack(pady=5)
        
        # ===== KẾT NỐI SERVER =====
        self.connect_to_server()
    
    def connect_to_server(self):
        """Kết nối tới server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_ip, PORT))
            
            # Gửi tên user
            self.sock.send(f"USER {self.username}".encode())
            
            # Lấy danh sách bạn online
            self.sock.send("GET_FRIENDS".encode())
            
            # Nhận dữ liệu
            threading.Thread(target=self.receive_friends, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không kết nối được server: {e}")
            self.go_back()
    
    def receive_friends(self):
        """Nhận danh sách bạn"""
        while True:
            try:
                msg = self.sock.recv(1024).decode()
                if not msg:
                    break
                
                parts = msg.split(maxsplit=1)
                if parts[0] == "FRIENDS":
                    friends = parts[1].split() if len(parts) > 1 else []
                    self.friends_online = friends
                    self.update_friends_list()
            except:
                break
    
    def update_friends_list(self):
        """Cập nhật danh sách bạn"""
        self.friends_listbox.delete(0, tk.END)
        for friend in self.friends_online:
            self.friends_listbox.insert(tk.END, f"✅ {friend}")
    
    def invite_friend(self):
        """Mời bạn"""
        if not self.friends_online:
            messagebox.showwarning("Thông báo", "Không có bạn nào online")
            return
        
        friend = simpledialog.askstring("Mời bạn", "Nhập tên bạn:")
        if not friend:
            return
        
        if friend not in self.friends_online:
            messagebox.showerror("Lỗi", "Bạn này không online")
            return
        
        try:
            self.sock.send(f"INVITE {friend}".encode())
            messagebox.showinfo("Thành công", f"Đã gửi lời mời tới {friend}")
        except:
            messagebox.showerror("Lỗi", "Không thể gửi lời mời")
    
    def request_play(self):
        """Yêu cầu chơi với bạn đã chọn"""
        selection = self.friends_listbox.curselection()
        if not selection:
            messagebox.showwarning("Thông báo", "Chọn bạn trước")
            return
        
        friend = self.friends_online[selection[0]]
        try:
            self.sock.send(f"INVITE {friend}".encode())
            messagebox.showinfo("Thành công", f"Đã gửi lời mời tới {friend}")
        except:
            messagebox.showerror("Lỗi", "Không thể gửi lời mời")
    
    def create_room_code(self):
        """Tạo mã phòng"""
        import random
        import string
        room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        messagebox.showinfo("Mã phòng", f"Chia sẻ mã này với bạn:\n\n{room_code}")
    
    def join_room_code(self):
        """Tham gia phòng qua mã"""
        room_code = simpledialog.askstring("Tham gia phòng", "Nhập mã phòng:")
        if not room_code:
            return
        messagebox.showinfo("Thông báo", f"Tham gia phòng {room_code}\n(Tính năng sẽ sớm hoạt động)")
    
    def go_back(self):
        """Quay lại trang chủ"""
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
        self.root.destroy()
        if self.home:
            self.home.deiconify()
