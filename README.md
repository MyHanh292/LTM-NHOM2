Hướng dẫn dự án Cờ Caro

Mô tả:
- Trò Cờ Caro 30x30 với chế độ Offline (Người vs Người, Người vs AI) và Online (ghép cặp qua server TCP).

Yêu cầu:
- Python 3.8+
- Pillow (thư viện ảnh)
- Tkinter (đã tích hợp sẵn trong Python trên Windows)

Cài đặt phụ thuộc:

```bash
pip install -r requirements.txt
```

Chạy server (nếu muốn chơi Online trên cùng máy hoặc mạng nội bộ):

```bash
python server\server.py
```

Chạy client GUI (đăng nhập):

```bash
python offline\login.py
```

Lưu ý:
- Khi chơi online, trong `Trang Chủ` sẽ hỏi địa chỉ server (mặc định `localhost`).
- Mật khẩu hiện được lưu dưới dạng băm SHA256 (username làm salt). Dự án tự động di cư các mật khẩu cũ dạng plaintext khi người dùng đăng nhập lần đầu.
- Server hiện kiểm tra thắng/thua và sẽ gửi `END <X|O>` khi có người thắng; nếu một client ngắt kết nối, server gửi `DISCONNECT` cho đối thủ.

Các đề xuất cải tiến:
- Lưu mật khẩu an toàn hơn với salt độc lập và thuật toán băm mạnh hơn (bcrypt/scrypt).
- Server nên quản lý người dùng, phiên, và xác thực.
- AI có thể nâng cấp bằng Minimax/Alpha-Beta để chơi mạnh hơn.

