import socket
import threading
import random

HOST = "0.0.0.0"
PORT = 9999

waiting = []
lock = threading.Lock()


def handle_game(c1, c2):
    players = [(c1, "X"), (c2, "O")]
    random.shuffle(players)

    current = "X"
    board = set()

    def check_win_board(x, y, sym):
        # board is set of (x,y)
        SIZE = 30
        WIN_COUNT = 5
        directions = [(1,0),(0,1),(1,1),(1,-1)]
        for dx, dy in directions:
            cnt = 1
            for k in [1, -1]:
                i, j = x + dx*k, y + dy*k
                while 0 <= i < SIZE and 0 <= j < SIZE and (i, j) in board and symbol_at(i, j) == sym:
                    cnt += 1
                    i += dx*k
                    j += dy*k
            if cnt >= WIN_COUNT:
                return True
        return False

    # Helper to get symbol at position from board set by tracking a small map
    pos_symbol = {}

    def symbol_at(x, y):
        return pos_symbol.get((x, y))

    for conn, sym in players:
        conn.send(f"START {sym}".encode())

    def listen(conn, symbol):
        nonlocal current
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break

                parts = data.split()
                if parts[0] != "MOVE":
                    continue

                x, y = int(parts[1]), int(parts[2])

                with lock:
                    if symbol != current:
                        continue
                    if (x, y) in board:
                        continue

                    board.add((x, y))
                    pos_symbol[(x, y)] = symbol

                    # broadcast move
                    for c, _ in players:
                        try:
                            c.send(f"MOVE {x} {y} {symbol}".encode())
                        except:
                            pass

                    # check for win
                    if check_win_board(x, y, symbol):
                        # notify both clients
                        for c, _ in players:
                            try:
                                c.send(f"END {symbol}".encode())
                            except:
                                pass
                        # close connections and end
                        for c, _ in players:
                            try:
                                c.close()
                            except:
                                pass
                        return

                    current = "O" if current == "X" else "X"

            except:
                break
        conn.close()
        # thông báo cho đối thủ nếu còn kết nối
        try:
            for c, s in players:
                if c is not conn:
                    try:
                        c.send("DISCONNECT".encode())
                    except:
                        pass
                    try:
                        c.close()
                    except:
                        pass
        except:
            pass

    for conn, sym in players:
        threading.Thread(
            target=listen,
            args=(conn, sym),
            daemon=True
        ).start()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print("🚀 Server chạy cổng", PORT)

    while True:
        conn, addr = server.accept()
        print("[+] Client:", addr)

        with lock:
            waiting.append(conn)

            if len(waiting) >= 2:
                c1 = waiting.pop(0)
                c2 = waiting.pop(0)
                print("🎮 Ghép cặp 2 client")

                threading.Thread(
                    target=handle_game,
                    args=(c1, c2),
                    daemon=True
                ).start()


if __name__ == "__main__":
    main()
