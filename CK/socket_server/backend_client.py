"""
BackendClient
-------------
Thông báo cho Flask API khi upload file hoàn tất qua socket.
Gửi request bất đồng bộ để không block socket server.
"""

import os
import threading

try:
    import requests
except ImportError:
    raise ImportError("⚠️ Thiếu thư viện 'requests'. Cài bằng: pip install requests")


# ==================================================
# ⚙️ CẤU HÌNH
# ==================================================
DEFAULT_BACKEND_URL = "http://127.0.0.1:5000/api/documents"
BACKEND_URL = os.getenv("BACKEND_URL", DEFAULT_BACKEND_URL)
REQUEST_TIMEOUT = 5  # giây


# ==================================================
# 🧩 HÀM POST AN TOÀN
# ==================================================
def safe_post(url: str, payload: dict, headers: dict) -> None:
    """
    Gửi POST request tới Backend, có xử lý lỗi phổ biến.
    """
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 201:
            print(f"[BackendClient] ✅ Upload hoàn tất: {payload.get('filename')}")
        else:
            print(
                f"[BackendClient] ⚠️ Backend trả về {response.status_code} | "
                f"{response.text[:200]}"
            )

    except requests.exceptions.Timeout:
        print("[BackendClient] ⏱️ Timeout khi gọi Backend API.")
    except requests.exceptions.ConnectionError:
        print("[BackendClient] 🚫 Không kết nối được Backend API.")
    except Exception as exc:
        print(f"[BackendClient] ❌ Lỗi không xác định: {exc}")


# ==================================================
# 🚀 BACKEND CLIENT
# ==================================================
class BackendClient:
    """
    Client dùng để gửi thông báo upload hoàn tất cho Flask Backend.
    """

    def __init__(self, url: str | None = None):
        self.url = url or BACKEND_URL

    def notify_completion(
        self,
        upload_id: str,
        file_path: str,
        metadata: dict,
    ) -> None:
        """
        Thông báo Backend rằng file đã upload xong.

        metadata bắt buộc:
        - token
        - filename
        """

        if not isinstance(metadata, dict):
            print(f"[BackendClient] ⚠️ [{upload_id}] Metadata không hợp lệ.")
            return

        token = metadata.get("token")
        filename = metadata.get("filename")

        if not token or not filename:
            print(f"[BackendClient] ⚠️ [{upload_id}] Thiếu token hoặc filename.")
            return

        payload = {
            "filename": filename,
            "file_path": file_path,
            "description": metadata.get("description"),
            "visibility": metadata.get("visibility", "private"),
            "tags": metadata.get("tags", []),
        }

        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Gửi request bằng thread riêng
        threading.Thread(
            target=safe_post,
            args=(self.url, payload, headers),
            daemon=True,
        ).start()

        print(
            f"[BackendClient] 📤 Đã gửi yêu cầu thông báo upload: {filename}"
        )
