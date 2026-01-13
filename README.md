Hướng dẫn dự án Cờ Caro

Mô tả:
- Trò Cờ Caro 30x30 với chế độ **Offline** (Người vs Người, Người vs AI)
- **Online Mode** được hoàn thiện với 2 chế độ:
  - Tìm người chơi ngẫu nhiên (Random Matching)
  - Chơi với bạn bè (danh sách bạn, mã phòng)

Yêu cầu:
- Python 3.8+
- Pillow (thư viện ảnh)
- Tkinter (đã tích hợp sẵn trong Python trên Windows)

Cài đặt phụ thuộc:

```bash
pip install -r requirements.txt
```

Chạy Server (BẮT BUỘC cho chế độ Online):

```bash
python server\server.py
```

Chạy Client GUI (Đăng nhập):

```bash
python offline\login.py
```

---

## 🎮 Các Chế Độ Chơi

### Offline:
1. **Người vs Người**: Cả hai chơi trên cùng máy
2. **Người vs AI**: Chơi với máy tính

### Online (New!):
1. **Tìm Người Chơi Ngẫu Nhiên**: 
   - Hệ thống tự ghép cặp với người lạ
   - Có xếp hạng (Win/Loss)
   
2. **Chơi Với Bạn Bè**:
   - Mời bạn bè trực tiếp
   - Tạo mã phòng chia sẻ
   - Danh sách bạn bè online

---

## 📖 Hướng Dẫn Chi Tiết

👉 **Xem file: `ONLINE_GUIDE.md`** để hiểu rõ cách chơi Online

---

## ⚠️ Lưu Ý

- **Khi chơi online**: Server PHẢI chạy trước (`python server\server.py`)
- **Địa chỉ server**: Mặc định `localhost` (cùng máy)
  - Nếu server trên máy khác → nhập IP của máy đó
- **Mật khẩu**: Lưu dưới dạng băm SHA256 (username làm salt)
  - Dự án tự động di cư các mật khẩu cũ dạng plaintext khi đăng nhập lần đầu
- **Điểm thắng/thua**: Được lưu vào `users.json` và hiển thị trên xếp hạng

---

## 🔧 Cấu Trúc Dự Án

```
📁 laptrinhmang/
├── 📄 README.md                 # Hướng dẫn chính
├── 📄 ONLINE_GUIDE.md          # Hướng dẫn chế độ Online chi tiết
├── 📄 requirements.txt
├── 📄 users.json               # Dữ liệu người dùng (wins/losses/friends)
│
├── 📁 offline/                 # Chế độ Offline
│   ├── login.py               # Đăng nhập
│   ├── home.py                # Trang chủ (chọn chế độ chơi)
│   ├── game.py                # Logic trò chơi
│   └── avatars/               # Hình đại diện người chơi
│
├── 📁 online/                  # Chế độ Online
│   └── online_game.py         # Logic chơi online
│
└── 📁 server/                  # Server (TCP Socket)
    └── server.py              # Server quản lý matching, phòng, điểm
```

---

## 📊 Hệ Thống Điểm (Online)

- **Thắng**: +1 win
- **Thua**: +1 loss
- **Xếp hạng**: Sắp xếp theo số trận thắng (cao nhất trên cùng)
- **Lưu trữ**: Lưu vào `users.json` trên server

---

## 🚀 Những Cải Tiến Thực Hiện

✅ **Hoàn thiện chế độ Online:**
- Tìm kiếm người chơi ngẫu nhiên (matching queue)
- Danh sách bạn bè
- Mời bạn bè chơi
- Tạo mã phòng chia sẻ
- Quản lý phòng chơi trên server
- Cập nhật điểm (wins/losses)

✅ **Nâng cấp Server:**
- Quản lý trạng thái người dùng (online/offline)
- Xử lý matching logic (FIFO queue)
- Xử lý lời mời bạn bè
- Lưu dữ liệu người dùng liên tục

---

## 📋 Các Đề Xuất Cải Tiến Tiếp Theo

- [ ] Lưu mật khẩu an toàn hơn: bcrypt/scrypt thay vì SHA256
- [ ] Chat với đối thủ trong game
- [ ] Lịch sử trận đấu (match history)
- [ ] Xếp hạng toàn cầu
- [ ] Phòng chơi công khai (public rooms)
- [ ] AI nâng cấp: Minimax/Alpha-Beta
- [ ] Badge/thành tích

---

**Chúc bạn chơi vui! 🎮**


