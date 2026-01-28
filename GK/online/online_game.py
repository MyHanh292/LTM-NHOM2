"""
Cờ Caro Online Client - Socket TCP Multi-Player
- Kết nối tới Server
- Nhận/gửi move realtime
- Hiển thị board đã update
"""

import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import os
import json
import subprocess
import re


class CaroClient:
    """Client chơi Caro Online"""
    
    BOARD_SIZE = 20
    
    def __init__(self, root, username="Player", avatar_path=""):
        self.root = root
        self.username = username
        self.avatar_path = avatar_path
        self.root.title("Cờ Caro Online")
        self.root.geometry("600x700")
        
        # ===== GAME STATE =====
        self.sock = None
        self.my_symbol = None
        self.opponent_name = "..."
        self.opponent_avatar = ""
        self.my_turn = False
        self.board = {}
        self.game_active = True
        self.buttons = {}
        self.game_started = False
        
        # ===== SETUP UI =====
        self.setup_ui()
        
        # ===== CONNECT =====
        self.connect_to_server()
    
    def setup_ui(self):
        """Tạo giao diện"""
        # ===== INFO PANEL =====
        info_frame = tk.Frame(self.root, bg="lightgray", height=100)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Left: Bạn
        left_frame = tk.Frame(info_frame, bg="lightgray")
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.p1_avatar_label = tk.Label(left_frame, bg="white", width=8, height=4, relief=tk.RIDGE)
        self.p1_avatar_label.pack()
        
        self.p1_name_label = tk.Label(left_frame, text=f"Bạn: {self.username}", font=("Arial", 10, "bold"), bg="lightgray")
        self.p1_name_label.pack()
        
        # Center: Status
        center_frame = tk.Frame(info_frame, bg="lightgray")
        center_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.status_label = tk.Label(
            center_frame,
            text="⏳ Kết nối...",
            font=("Arial", 12, "bold"),
            bg="lightgray",
            fg="blue",
            wraplength=150
        )
        self.status_label.pack(pady=10)
        
        # Right: Đối thủ
        right_frame = tk.Frame(info_frame, bg="lightgray")
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.p2_avatar_label = tk.Label(right_frame, bg="white", width=8, height=4, relief=tk.RIDGE)
        self.p2_avatar_label.pack()
        
        self.p2_name_label = tk.Label(right_frame, text="Đối thủ: ...", font=("Arial", 10, "bold"), bg="lightgray")
        self.p2_name_label.pack()
        
        # ===== BOARD =====
        board_frame = tk.Frame(self.root, bg="white", relief=tk.SUNKEN, bd=2)
        board_frame.pack(padx=10, pady=5)
        
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                btn = tk.Button(
                    board_frame,
                    text="",
                    width=2,
                    height=1,
                    font=("Arial", 7),
                    command=lambda x=i, y=j: self.on_click(x, y),
                    state="disabled"
                )
                btn.grid(row=i, column=j, padx=1, pady=1)
                self.buttons[(i, j)] = btn
        
        # ===== BUTTONS =====
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.play_again_btn = tk.Button(
            btn_frame,
            text="🔄 Ván tiếp theo",
            command=self.play_again,
            font=("Arial", 10, "bold"),
            bg="#00BCD4",
            fg="white",
            padx=12, pady=6,
            state="disabled"
        )
        self.play_again_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🏠 Quay lại",
            command=self.go_back,
            font=("Arial", 10, "bold"),
            bg="#FFA500",
            fg="white",
            padx=12, pady=6
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="⏸ Dừng",
            command=self.pause_game,
            font=("Arial", 10, "bold"),
            bg="#9C27B0",
            fg="white",
            padx=12, pady=6
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Thoát",
            command=self.quit_game,
            font=("Arial", 10, "bold"),
            bg="#F44336",
            fg="white",
            padx=12, pady=6
        ).pack(side=tk.LEFT, padx=5)
    
    def connect_to_server(self):
        """Kết nối server - Tự động detect IP LAN hoặc cho phép nhập"""
        try:
            # Tự động detect IP LAN
            server_ip = self.get_lan_ip()
            
            # Hỏi người dùng về IP server
            dialog_ip = simpledialog.askstring(
                "Kết nối Server",
                f"Nhập IP server (IP LAN của bạn: {server_ip})\n\nNếu trên cùng máy: 127.0.0.1\nNếu trên LAN: Nhập IP máy server",
                initialvalue=server_ip
            )
            
            if dialog_ip is None:  # User cancelled
                self.game_active = False
                self.root.quit()
                return
            
            server_ip = dialog_ip.strip()
            
            # Xóa port nếu user nhập 192.168.1.5:9999
            if ':' in server_ip:
                server_ip = server_ip.split(':')[0]
            
            # Validate IP format
            if not self.is_valid_ip(server_ip):
                messagebox.showerror("Lỗi", f"IP không hợp lệ: {server_ip}")
                self.connect_to_server()
                return
            
            print(f"[{self.username}] Kết nối tới {server_ip}:9999...")
            self.status_label.config(text=f"⏳ Kết nối {server_ip}:9999...", fg="blue")
            self.root.update()
            
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)  # 5 giây timeout
            self.sock.connect((server_ip, 9999))
            self.sock.settimeout(None)  # Bỏ timeout sau khi kết nối thành công
            
            # Gửi info
            msg = f"{self.username}|{self.avatar_path}\n"
            self.sock.send(msg.encode('utf-8'))
            print(f"[{self.username}] Gửi: {msg.strip()}")
            
            # Load avatar
            self.load_my_avatar()
            
            # Listen
            self.status_label.config(text="⏳ Chờ đối thủ...", fg="blue")
            threading.Thread(target=self.listen_loop, daemon=True).start()
            
        except socket.timeout:
            messagebox.showerror("Lỗi Kết Nối", f"Timeout: Server {server_ip}:9999 không phản hồi\n\nHãy kiểm tra:\n1. Server đã chạy?\n2. IP đúng không?\n3. Firewall có chặn port 9999 không?")
            self.connect_to_server()
        except ConnectionRefusedError:
            messagebox.showerror("Lỗi Kết Nối", f"Bị từ chối: Server {server_ip}:9999 không mở\n\nHãy chạy server trước!")
            self.connect_to_server()
        except Exception as e:
            print(f"[{self.username}] Connection error: {e}")
            messagebox.showerror("Lỗi", f"Không kết nối được:\n{e}")
            self.root.destroy()
    
    def get_lan_ip(self):
        """Lấy IP LAN của máy hiện tại"""
        try:
            # Phương pháp: Kết nối tới 1 IP bên ngoài để lấy IP LAN
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            lan_ip = s.getsockname()[0]
            s.close()
            return lan_ip
        except:
            return "127.0.0.1"
    
    def is_valid_ip(self, ip):
        """Kiểm tra IP hợp lệ"""
        # Regex để validate IPv4
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        
        parts = ip.split('.')
        for part in parts:
            if int(part) > 255:
                return False
        return True
    
    def listen_loop(self):
        """Lắng nghe server"""
        print(f"[{self.username}] Listening...")
        buffer = ""
        
        while self.game_active:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if not data:
                    print(f"[{self.username}] Server disconnected")
                    break
                
                buffer += data
                
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line:
                        print(f"[{self.username}] Got: {line}")
                        self.handle_message(line)
                    
            except Exception as e:
                print(f"[{self.username}] Listen error: {e}")
                if self.game_active:
                    self.status_label.config(text="❌ Mất kết nối!", fg="red")
                break
    
    def handle_message(self, msg):
        """Xử lý tin nhắn"""
        parts = msg.split()
        if not parts:
            return
        
        cmd = parts[0]
        
        if cmd == "WAIT":
            self.root.after(0, lambda: self.status_label.config(text="⏳ Chờ đối thủ...", fg="blue"))
        
        elif cmd == "START":
            self.my_symbol = parts[1] if len(parts) > 1 else "X"
            opp_name = parts[2] if len(parts) > 2 else "Đối thủ"
            opp_avatar = parts[3] if len(parts) > 3 else ""
            
            self.game_started = True
            self.opponent_name = opp_name
            self.opponent_avatar = opp_avatar
            self.my_turn = (self.my_symbol == "X")
            
            def update():
                opp_sym = "O" if self.my_symbol == "X" else "X"
                self.p1_name_label.config(text=f"Bạn ({self.my_symbol}): {self.username}")
                self.p2_name_label.config(text=f"Đối thủ ({opp_sym}): {opp_name}")
                
                # Load avatar đối thủ
                if opp_avatar and os.path.exists(opp_avatar):
                    try:
                        img = Image.open(opp_avatar).resize((80, 50))
                        photo = ImageTk.PhotoImage(img)
                        self.p2_avatar_label.config(image=photo)
                        self.p2_avatar_label.image = photo
                    except:
                        pass
                
                # Enable buttons
                for btn in self.buttons.values():
                    btn.config(state="normal")
                
                self.update_status()
            
            self.root.after(0, update)
        
        elif cmd == "MOVE":
            x, y, sym = int(parts[1]), int(parts[2]), parts[3]
            
            def update():
                color = "red" if sym == "X" else "blue"
                self.buttons[(x, y)].config(text=sym, fg=color, state="disabled")
                self.board[(x, y)] = sym
                
                # Cập nhật lượt
                if sym == "X":
                    self.my_turn = (self.my_symbol == "O")
                else:
                    self.my_turn = (self.my_symbol == "X")
                
                self.update_status()
            
            self.root.after(0, update)
        
        elif cmd == "END":
            winner = parts[1] if len(parts) > 1 else ""
            
            def update():
                # Disable all buttons
                for btn in self.buttons.values():
                    btn.config(state="disabled")
                
                # Enable play again button
                self.play_again_btn.config(state="normal")
                
                if winner == self.my_symbol:
                    self.status_label.config(text="🎉 BẠN THẮNG!", fg="green", font=("Arial", 14, "bold"))
                    messagebox.showinfo("Thắng!", f"Chúc mừng! Bạn đã thắng!")
                else:
                    self.status_label.config(text="😢 Bạn Thua", fg="red", font=("Arial", 14, "bold"))
                    messagebox.showinfo("Thua", "Chúc lần sau may mắn hơn!")
                
                self.game_active = False
            
            self.root.after(0, update)
    
    def on_click(self, x, y):
        """Click ô trên board"""
        if not self.game_active:
            messagebox.showwarning("Lỗi", "Game đã kết thúc!")
            return
        
        if not self.game_started:
            messagebox.showwarning("Lỗi", "Chờ game bắt đầu...")
            return
        
        if not self.my_turn:
            messagebox.showwarning("Lỗi", f"Chờ {self.opponent_name} đánh!")
            return
        
        if (x, y) in self.board:
            messagebox.showwarning("Lỗi", "Ô này đã có quân rồi!")
            return
        
        try:
            msg = f"MOVE {x} {y}\n"
            self.sock.send(msg.encode('utf-8'))
            print(f"[{self.username}] Sent move: {x} {y}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Gửi move thất bại: {e}")
    
    def update_status(self):
        """Cập nhật status"""
        if not self.game_started:
            self.status_label.config(text="⏳ Chờ...", fg="blue")
            return
        
        if self.my_turn:
            self.status_label.config(
                text=f"✋ TỚI LƯỢT BẠN\n({self.my_symbol})",
                fg="green",
                font=("Arial", 11, "bold")
            )
        else:
            self.status_label.config(
                text=f"⏳ Chờ {self.opponent_name[:8]}\n({chr(88 if self.my_symbol == 79 else 79)})",
                fg="orange",
                font=("Arial", 10)
            )
    
    def play_again(self):
        """Chơi ván tiếp theo"""
        # Reset board và state
        self.board.clear()
        self.game_active = True
        self.game_started = False
        
        # Clear buttons
        for btn in self.buttons.values():
            btn.config(text="", state="disabled", fg="black")
        
        # Disable play again button
        self.play_again_btn.config(state="disabled")
        
        # Update status
        self.status_label.config(text="⏳ Chờ ván tiếp theo...", fg="blue")
        
        # Gửi READY signal tới server (nếu server support)
        try:
            msg = "READY\n"
            self.sock.send(msg.encode('utf-8'))
        except:
            pass
    
    def load_my_avatar(self):
        """Load avatar bạn"""
        if self.avatar_path and os.path.exists(self.avatar_path):
            try:
                img = Image.open(self.avatar_path).resize((80, 50))
                photo = ImageTk.PhotoImage(img)
                self.p1_avatar_label.config(image=photo)
                self.p1_avatar_label.image = photo
            except:
                pass
    
    def go_back(self):
        """Quay lại home"""
        if messagebox.askyesno("Quay lại", "Quay lại trang chủ? (Sẽ thua)"):
            self.game_active = False
            try:
                self.sock.close()
            except:
                pass
            self.root.destroy()
    
    def pause_game(self):
        """Dừng game"""
        messagebox.showinfo("Dừng", "Tính năng này sẽ được thêm sớm.")
    
    def quit_game(self):
        """Thoát"""
        if messagebox.askyesno("Thoát", "Thoát ứng dụng?"):
            self.game_active = False
            try:
                self.sock.close()
            except:
                pass
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    CaroClient(root, "Test", "")
    root.mainloop()


