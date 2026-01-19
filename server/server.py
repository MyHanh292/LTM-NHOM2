"""
Cờ Caro Online Server - Socket TCP Multi-Client-Server Architecture
- Nhận kết nối từ các client (localhost hoặc LAN IP)
- Ghép cặp 2 client để chơi
- Quản lý game logic (kiểm tra thắng/thua)
- Gửi tín hiệu nhân vật (X hoặc O) cho client
"""

import datetime
import socket
import threading
import json
import os
import random

# ========== CẤU HÌNH SERVER ==========
HOST = "0.0.0.0"  # Lắng nghe trên tất cả IP (localhost + LAN)
PORT = 9999
BOARD_SIZE = 20
WIN_COUNT = 5

# ========== GLOBAL STATE ==========
clients_queue = []
lock = threading.Lock()

def log(msg):
    """In log với timestamp"""
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


# ========== GAME LOGIC ==========

def check_win(x, y, sym, board):
    """
    Kiểm tra xem vị trí (x, y) có tạo thành 5 quân liên tiếp không
    - Kiểm tra 4 hướng: ngang, dọc, chéo xuôi, chéo ngược
    """
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx, dy in directions:
        count = 1
        # Kiểm tra 2 phía (trước và sau)
        for k in [1, -1]:
            i, j = x + dx * k, y + dy * k
            while (i, j) in board and board[(i, j)] == sym:
                count += 1
                i += dx * k
                j += dy * k
        if count >= WIN_COUNT:
            return True
    return False


def handle_game(p1, p2, p1_name, p2_name, p1_avatar, p2_avatar):
    """
    Xử lý game giữa 2 player
    - p1, p2: socket connection
    - Gửi thông tin opponent cho mỗi player
    - Quản lý turn, move, kiểm tra thắng/thua
    """
    board = {}
    players = [(p1, "X", p1_name, p1_avatar), (p2, "O", p2_name, p2_avatar)]
    random.shuffle(players)
    
    turn = "X"

    # Gửi thông tin START cho cả 2 player
    for i, (conn, sym, name, avatar) in enumerate(players):
        opponent_idx = 1 - i
        opponent_name = players[opponent_idx][2]
        opponent_avatar = players[opponent_idx][3]
        # Format: START symbol opponent_name opponent_avatar
        start_msg = f"START {sym} {opponent_name} {opponent_avatar}\n"
        try:
            conn.send(start_msg.encode('utf-8'))
        except:
            log(f"Lỗi gửi START tới {name}")

    def listen(conn, sym, player_name):
        """Lắng nghe move từ client"""
        nonlocal turn
        while True:
            try:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break
                
                for line in data.split("\n"):
                    if not line.startswith("MOVE"):
                        continue
                    
                    try:
                        parts = line.split()
                        x, y = int(parts[1]), int(parts[2])
                    except:
                        continue

                    with lock:
                        # Kiểm tra lượt chơi và vị trí hợp lệ
                        if sym != turn or (x, y) in board:
                            continue
                        
                        board[(x, y)] = sym
                        log(f"{player_name} ({sym}) đánh: ({x}, {y})")

                        # Gửi move tới cả 2 player
                        move_msg = f"MOVE {x} {y} {sym}\n"
                        for player_conn, _, _, _ in players:
                            try:
                                player_conn.send(move_msg.encode('utf-8'))
                            except:
                                pass

                        # Kiểm tra thắng
                        if check_win(x, y, sym, board):
                            end_msg = f"END {sym}\n"
                            for player_conn, _, _, _ in players:
                                try:
                                    player_conn.send(end_msg.encode('utf-8'))
                                except:
                                    pass
                            log(f"{player_name} ({sym}) THẮNG!")
                            return

                        # Chuyển lượt
                        turn = "O" if turn == "X" else "X"
            except Exception as e:
                log(f"Lỗi listener {player_name}: {e}")
                break

    # Tạo thread lắng nghe cho từng player
    for conn, sym, player_name, _ in players:
        threading.Thread(
            target=listen,
            args=(conn, sym, player_name),
            daemon=True
        ).start()


def handle_client(conn, addr):
    """
    Xử lý khi có client kết nối
    - Nhận thông tin username/avatar
    - Đưa vào hàng chờ
    - Khi có 2 client: ghép cặp chơi game
    """
    try:
        conn.send("WAIT\n".encode('utf-8'))
        
        # Nhận thông tin từ client
        client_info = conn.recv(1024).decode('utf-8').strip()
        try:
            parts = client_info.split("|")
            username = parts[0] if len(parts) > 0 else "Player"
            avatar_path = parts[1] if len(parts) > 1 else ""
        except:
            username = "Player"
            avatar_path = ""
        
        log(f"Client {addr} kết nối: {username}")
        
        with lock:
            clients_queue.append((conn, username, avatar_path))
            
            # Khi có 2 client: bắt đầu game
            if len(clients_queue) >= 2:
                p1_conn, p1_name, p1_avatar = clients_queue.pop(0)
                p2_conn, p2_name, p2_avatar = clients_queue.pop(0)
                
                log(f"Ghép cặp: {p1_name} vs {p2_name}")
                
                threading.Thread(
                    target=handle_game,
                    args=(p1_conn, p2_conn, p1_name, p2_name, p1_avatar, p2_avatar),
                    daemon=True
                ).start()
    except Exception as e:
        log(f"Lỗi handle_client {addr}: {e}")
        try:
            conn.close()
        except:
            pass


# ========== MAIN SERVER ==========

def get_lan_ip():
    """Lấy IP LAN của server (để client biết kết nối)"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(('8.8.8.8', 80))
            lan_ip = s.getsockname()[0]
        except:
            lan_ip = '127.0.0.1'
        finally:
            s.close()
        return lan_ip
    except:
        return '127.0.0.1'


def main():
    """Main server loop"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    
    lan_ip = get_lan_ip()
    
    print("\n" + "="*60)
    print("🎮 CỜ CARO ONLINE SERVER")
    print("="*60)
    log(f"Server chạy tại: 0.0.0.0:{PORT}")
    log(f"Máy cùng LAN kết nối: {lan_ip}:{PORT}")
    log(f"Máy local kết nối: 127.0.0.1:{PORT}")
    print("="*60 + "\n")

    try:
        while True:
            conn, addr = server.accept()
            log(f"✓ Client mới từ {addr}")
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            ).start()
    except KeyboardInterrupt:
        log("Server dừng")
        server.close()




if __name__ == "__main__":
    main()
