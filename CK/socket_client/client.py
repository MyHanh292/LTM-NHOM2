import socket
import json
import os
import time
import threading

# =============================
# ⚙️ CẤU HÌNH
# =============================
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6000
CHUNK_SIZE = 65536  # 64KB
STATE_FILE = "client_upload_state.json"
PING_INTERVAL = 10  # giây

lock = threading.Lock()


# =============================
# 🧩 HÀM TIỆN ÍCH
# =============================
def send_json(sock, data: dict):
    sock.sendall((json.dumps(data) + "\n").encode("utf-8"))


def read_json(sock):
    buffer = b""
    while not buffer.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            return None
        buffer += chunk
    return json.loads(buffer.decode("utf-8").strip())


def save_state(upload_id, offset):
    with lock:
        state = {}
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except Exception:
                pass
        state[upload_id] = offset
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)


def load_state(upload_id):
    if not os.path.exists(STATE_FILE):
        return 0
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get(upload_id, 0)
    except Exception:
        return 0


# =============================
# 🚀 UPLOAD CLIENT
# =============================
class UploadClient:
    def __init__(
        self,
        file_path,
        token,
        description="",
        visibility="private",
        tags=None,
        on_progress=None
    ):
        self.file_path = file_path
        self.token = token
        self.description = description
        self.visibility = visibility
        self.tags = tags or []

        self.filename = os.path.basename(file_path)
        self.filesize = os.path.getsize(file_path)
        self.upload_id = f"{int(time.time())}_{self.filename}"

        self.sock = None
        self.offset = load_state(self.upload_id)

        self.state = "INIT"
        self.stop_flag = False
        self.pause_flag = False

        self.on_progress = on_progress

    # =============================
    # 🔌 KẾT NỐI
    # =============================
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(20)
        self.sock.connect((SERVER_HOST, SERVER_PORT))
        print("🔗 Đã kết nối tới Socket Server")

    def close(self):
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass

    # =============================
    # ❤️ HEARTBEAT
    # =============================
    def heartbeat(self):
        while self.state == "UPLOADING":
            try:
                send_json(self.sock, {"action": "ping"})
            except Exception:
                print("⚠️ Mất kết nối (heartbeat)")
                self.state = "ERROR"
                break
            time.sleep(PING_INTERVAL)

    # =============================
    # ▶️ UPLOAD
    # =============================
    def start(self):
        self.stop_flag = False
        self.pause_flag = False
        self.state = "UPLOADING"
        threading.Thread(target=self._upload_loop, daemon=True).start()
        threading.Thread(target=self.heartbeat, daemon=True).start()

    def _upload_loop(self):
        try:
            self.connect()

            send_json(self.sock, {
                "action": "start" if self.offset == 0 else "resume",
                "upload_id": self.upload_id,
                "filename": self.filename,
                "filesize": self.filesize,
                "chunk_size": CHUNK_SIZE,
                "metadata": {
                    "token": self.token,
                    "description": self.description,
                    "visibility": self.visibility,
                    "tags": self.tags
                }
            })

            resp = read_json(self.sock)
            if not resp or resp.get("status") != "ok":
                raise Exception("Không thể khởi tạo upload")

            self.offset = resp.get("offset", self.offset)
            print(f"🚀 Upload từ byte {self.offset}/{self.filesize}")

            with open(self.file_path, "rb") as f:
                while self.offset < self.filesize:
                    if self.stop_flag:
                        self.state = "STOPPED"
                        save_state(self.upload_id, self.offset)
                        send_json(self.sock, {"action": "stop", "upload_id": self.upload_id})
                        print("⛔ Upload đã dừng")
                        return

                    if self.pause_flag:
                        self.state = "PAUSED"
                        save_state(self.upload_id, self.offset)
                        send_json(self.sock, {"action": "pause", "upload_id": self.upload_id})
                        print("⏸ Upload tạm dừng")
                        while self.pause_flag and not self.stop_flag:
                            time.sleep(0.3)
                        send_json(self.sock, {"action": "resume", "upload_id": self.upload_id})
                        self.state = "UPLOADING"

                    f.seek(self.offset)
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    send_json(self.sock, {
                        "action": "chunk",
                        "upload_id": self.upload_id,
                        "offset": self.offset,
                        "length": len(chunk)
                    })
                    self.sock.sendall(chunk)

                    ack = read_json(self.sock)
                    if not ack or ack.get("status") != "ok":
                        raise Exception("Lỗi gửi chunk")

                    self.offset = ack.get("offset", self.offset)
                    save_state(self.upload_id, self.offset)

                    percent = (self.offset / self.filesize) * 100
                    print(f"⬆️ Tiến độ: {percent:.2f}%")

                    if self.on_progress:
                        self.on_progress(percent)

            self.state = "DONE"
            print("✅ Upload hoàn tất 100%")
            self._clear_state()

        except Exception as e:
            self.state = "ERROR"
            print(f"❌ Lỗi upload: {e}")

        finally:
            self.close()

    def _clear_state(self):
        if not os.path.exists(STATE_FILE):
            return
        with lock:
            try:
                with open(STATE_FILE, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                    data.pop(self.upload_id, None)
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=2)
            except Exception:
                pass

    # =============================
    # 🎮 ĐIỀU KHIỂN
    # =============================
    def pause(self):
        self.pause_flag = True

    def resume(self):
        self.pause_flag = False

    def stop(self):
        self.stop_flag = True
        self.pause_flag = False


# =============================
# 💡 TEST CLI
# =============================
if __name__ == "__main__":
    token = input("Nhập JWT token: ").strip()
    file_path = input("Nhập đường dẫn file: ").strip()

    client = UploadClient(
        file_path=file_path,
        token=token,
        description="Test upload socket nâng cao",
        visibility="public",
        tags=["socket", "resume", "heartbeat"],
        on_progress=lambda p: print(f"[UI] {p:.1f}%")
    )

    client.start()

    print("\nLệnh: p = pause | r = resume | s = stop | q = quit\n")
    while True:
        cmd = input(">> ").strip().lower()
        if cmd == "p":
            client.pause()
        elif cmd == "r":
            client.resume()
        elif cmd == "s":
            client.stop()
        elif cmd == "q":
            client.stop()
            break
