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

                    for c, _ in players:
                        c.send(f"MOVE {x} {y} {symbol}".encode())

                    current = "O" if current == "X" else "X"

            except:
                break
        conn.close()

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
