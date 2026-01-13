import socket
import threading
import random
import json
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 9999

# ===== GLOBAL STATE =====
lock = threading.Lock()
users = {}  # {username: {password, wins, losses, avatar, friends: [...]}}
rooms = {}  # {room_id: {id1: conn, id2: conn, status}}
matching_queue = []  # [(conn, username)]
user_sockets = {}  # {username: conn}

USER_FILE = "users.json"


def load_users_db():
    global users
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        except:
            users = {}
    else:
        users = {}


def save_users_db():
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def check_win_board(x, y, sym, pos_symbol):
    """Kiểm tra thắng tại vị trí (x,y)"""
    SIZE = 30
    WIN_COUNT = 5
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    
    for dx, dy in directions:
        cnt = 1
        for k in [1, -1]:
            i, j = x + dx*k, y + dy*k
            while 0 <= i < SIZE and 0 <= j < SIZE and (i, j) in pos_symbol and pos_symbol[(i, j)] == sym:
                cnt += 1
                i += dx*k
                j += dy*k
        if cnt >= WIN_COUNT:
            return True
    return False


def handle_game(c1, c2, u1, u2, room_id):
    """Xử lý trò chơi giữa 2 người"""
    players = [(c1, u1, "X"), (c2, u2, "O")]
    random.shuffle(players)
    
    current_symbol = "X"
    current_user = players[0][1]  # tên người chơi hiện tại
    pos_symbol = {}  # {(x,y): symbol}
    
    # Gửi START cho cả 2
    for conn, username, sym in players:
        try:
            conn.send(f"START {sym} {players[0][1]} {players[1][1]}".encode())
        except:
            pass
    
    def listen(conn, username, symbol):
        nonlocal current_symbol, current_user
        
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                
                parts = data.split(maxsplit=2)
                
                if parts[0] == "MOVE":
                    x, y = int(parts[1]), int(parts[2])
                    
                    with lock:
                        # Kiểm tra lượt chơi & vị trí hợp lệ
                        if symbol != current_symbol:
                            continue
                        if (x, y) in pos_symbol:
                            continue
                        
                        pos_symbol[(x, y)] = symbol
                        
                        # Broadcast nước đi
                        for c, u, s in players:
                            try:
                                c.send(f"MOVE {x} {y} {symbol}".encode())
                            except:
                                pass
                        
                        # Kiểm tra thắng
                        if check_win_board(x, y, symbol, pos_symbol):
                            for c, u, s in players:
                                try:
                                    c.send(f"END {symbol} {username}".encode())
                                except:
                                    pass
                            
                            # Cập nhật điểm
                            with lock:
                                if username in users:
                                    users[username]["wins"] += 1
                                for c, u, s in players:
                                    if u != username and u in users:
                                        users[u]["losses"] += 1
                                save_users_db()
                            
                            # Đóng kết nối
                            for c, u, s in players:
                                try:
                                    c.close()
                                except:
                                    pass
                            return
                        
                        # Đổi lượt
                        current_symbol = "O" if current_symbol == "X" else "X"
                        for c, u, s in players:
                            if s == current_symbol:
                                current_user = u
                                break
            except:
                break
        
        # Đối thủ mất kết nối
        for c, u, s in players:
            if c is not conn:
                try:
                    c.send("DISCONNECT".encode())
                    c.close()
                except:
                    pass
        conn.close()
    
    for conn, username, sym in players:
        threading.Thread(
            target=listen,
            args=(conn, username, sym),
            daemon=True
        ).start()


def handle_client(conn, addr):
    """Xử lý kết nối client"""
    username = None
    
    try:
        # Bước 1: Nhận tên user
        msg = conn.recv(1024).decode()
        if msg.startswith("USER "):
            username = msg.split(maxsplit=1)[1]
            with lock:
                user_sockets[username] = conn
            print(f"[+] {username} kết nối từ {addr}")
    except:
        conn.close()
        return
    
    # Bước 2: Chờ lệnh từ client
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            
            parts = data.split(maxsplit=3)
            cmd = parts[0]
            
            # ===== RANDOM MATCHING =====
            if cmd == "QUEUE_MATCH":
                with lock:
                    matching_queue.append((conn, username))
                    print(f"📊 {username} vào queue. Queue size: {len(matching_queue)}")
                    
                    if len(matching_queue) >= 2:
                        c1, u1 = matching_queue.pop(0)
                        c2, u2 = matching_queue.pop(0)
                        room_id = f"match_{datetime.now().timestamp()}"
                        rooms[room_id] = {"u1": u1, "u2": u2, "status": "playing"}
                        print(f"🎮 Ghép cặp: {u1} vs {u2}")
                        
                        threading.Thread(
                            target=handle_game,
                            args=(c1, c2, u1, u2, room_id),
                            daemon=True
                        ).start()
            
            # ===== INVITE BẠN =====
            elif cmd == "INVITE":
                friend = parts[1]
                with lock:
                    if friend in user_sockets:
                        try:
                            user_sockets[friend].send(f"INVITE {username}".encode())
                            conn.send("INVITE_SENT".encode())
                        except:
                            conn.send("ERROR Friend offline".encode())
                    else:
                        conn.send("ERROR Friend not found".encode())
            
            # ===== ACCEPT INVITE =====
            elif cmd == "ACCEPT_INVITE":
                inviter = parts[1]
                room_id = f"room_{datetime.now().timestamp()}"
                
                with lock:
                    if inviter in user_sockets:
                        c1 = user_sockets[inviter]
                        c2 = conn
                        rooms[room_id] = {"u1": inviter, "u2": username, "status": "playing"}
                        
                        # Thông báo cho cả 2
                        c1.send(f"ROOM_READY {room_id}".encode())
                        c2.send(f"ROOM_READY {room_id}".encode())
                        
                        print(f"🎮 Tạo phòng: {inviter} vs {username}")
                        threading.Thread(
                            target=handle_game,
                            args=(c1, c2, inviter, username, room_id),
                            daemon=True
                        ).start()
            
            # ===== CANCEL INVITE =====
            elif cmd == "CANCEL_INVITE":
                conn.send("INVITE_CANCELLED".encode())
            
            # ===== GET FRIENDS =====
            elif cmd == "GET_FRIENDS":
                with lock:
                    if username in users:
                        friends = users[username].get("friends", [])
                        friends_data = [f for f in friends if f in user_sockets]
                        conn.send(f"FRIENDS {' '.join(friends_data)}".encode())
            
            # ===== ADD FRIEND =====
            elif cmd == "ADD_FRIEND":
                friend = parts[1]
                with lock:
                    if username in users:
                        if "friends" not in users[username]:
                            users[username]["friends"] = []
                        if friend not in users[username]["friends"]:
                            users[username]["friends"].append(friend)
                            save_users_db()
                            conn.send("FRIEND_ADDED".encode())
                        else:
                            conn.send("ERROR Already friends".encode())
                    else:
                        conn.send("ERROR User not found".encode())
        
        except Exception as e:
            print(f"Error: {e}")
            break
    
    # Xóa user khỏi queue nếu có
    with lock:
        matching_queue[:] = [(c, u) for c, u in matching_queue if u != username]
        if username in user_sockets:
            del user_sockets[username]
    
    conn.close()
    print(f"[-] {username} ngắt kết nối")


def main():
    load_users_db()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    
    print(f"🚀 Server chạy tại {HOST}:{PORT}")
    
    while True:
        try:
            conn, addr = server.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            ).start()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Server error: {e}")
    
    server.close()


if __name__ == "__main__":
    main()
