# 📋 Hướng dẫn Chơi Online - Cờ Caro 30x30

## 🎮 Các Chế Độ Chơi Online

### 1️⃣ **Tìm Người Chơi Ngẫu Nhiên** (Random Matching)
- ✅ Kết nối internet
- ✅ Hệ thống **tự động ghép cặp** với người lạ
- ✅ Có xếp hạng, tính điểm (Win/Loss)
- 👉 Phù hợp **muốn thi đấu, thử trình độ**

**Cách chơi:**
1. Chạy server: `python server\server.py`
2. Chạy client: `python offline\login.py`
3. Đăng nhập tài khoản
4. Chọn **"Online – Tìm người chơi ngẫu nhiên"**
5. Nhập địa chỉ server (mặc định: `localhost`)
6. **Chờ** hệ thống ghép cặp (⏳ Đang tìm người chơi...)
7. Khi tìm được đối thủ → bắt đầu chơi

---

### 2️⃣ **Chơi Với Bạn Bè** (Friends Mode)
- ✅ Kết nối internet
- ✅ Chơi với bạn **đã quen biết**
- ✅ **Danh sách bạn bè** được quản lý trên server
- 👉 Phù hợp **chơi nhóm, quen biết nhau**

**Cách chơi:**

#### **A. Mời Bạn Bè**
1. Chạy server: `python server\server.py`
2. Chạy client: `python offline\login.py`
3. Đăng nhập tài khoản
4. Chọn **"Online – Chơi với bạn bè"**
5. Nhập địa chỉ server
6. **Mục "Bạn bè đang online":**
   - Nhìn danh sách bạn bè đang online (✅ dấu)
   - Click **"📤 Mời bạn"** → nhập tên bạn
   - Click **"🎮 Yêu cầu chơi"** → chọn bạn từ danh sách
7. Bạn nhận được thông báo → **Yêu cầu xác nhận**
8. Khi bạn chấp nhận → **Bắt đầu chơi**

#### **B. Tạo Mã Phòng (Room Code)**
1. Làm theo bước 1-5 ở trên
2. Click **"🔑 Tạo mã phòng để bạn tham gia"**
3. **Sao chép mã** (ví dụ: `ABC123`)
4. **Chia sẻ** mã cho bạn bè
5. Bạn bè nhập mã → tham gia phòng

#### **C. Tham Gia Mã Phòng**
1. Làm theo bước 1-5 ở trên
2. Click **"🔐 Nhập mã phòng"**
3. **Nhập mã** mà bạn bè chia sẻ
4. **Tham gia phòng** → chơi

---

## ⚙️ Cài Đặt Server

### **Chạy Server Trước Tiên**
```bash
python server\server.py
```
**Output mong đợi:**
```
🚀 Server chạy tại 0.0.0.0:9999
```

### **Server Quản Lý:**
- ✅ Tìm kiếm người chơi (matching queue)
- ✅ Danh sách bạn bè
- ✅ Phòng chơi (room)
- ✅ Kiểm tra thắng/thua
- ✅ Lưu điểm (wins/losses)

---

## 📊 Hệ Thống Điểm

### **Điểm Thắng/Thua:**
- **Thắng**: `wins += 1`
- **Thua**: `losses += 1`
- 💾 **Lưu vào** `users.json`

### **Xem Bảng Xếp Hạng:**
- Ở trang chủ (Home) → danh sách xếp hạng người chơi
- Sắp xếp theo **số trận thắng** (cao nhất trên cùng)

---

## 🔧 Cấu Trúc Dữ Liệu

### **users.json - Dữ Liệu Người Dùng**
```json
{
    "username": {
        "password": "sha256_hash",
        "wins": 9,
        "losses": 3,
        "friends": ["friend1", "friend2"]
    }
}
```

### **Server State - Trạng Thái Chơi**
- `rooms`: Danh sách phòng chơi (room_id → user1, user2)
- `matching_queue`: Hàng đợi tìm người (FIFO)
- `user_sockets`: Kết nối client (username → socket)
- `users`: Dữ liệu người dùng từ `users.json`

---

## 📡 Giao Thức Client-Server

### **Kết Nối Đầu Tiên**
```
Client → Server: USER username
```

### **Tìm Người Chơi Ngẫu Nhiên**
```
Client → Server: QUEUE_MATCH
Server → Client: START X opponent_name  (nếu là X)
            hoặc START O opponent_name  (nếu là O)
```

### **Mời Bạn**
```
Client1 → Server: INVITE friend_name
Server → Client2: INVITE username
Client2 → Server: ACCEPT_INVITE username
Server → Client1: ROOM_READY room_id
       → Client2: ROOM_READY room_id
```

### **Đánh Nước**
```
Client → Server: MOVE x y
Server → Client1: MOVE x y symbol
       → Client2: MOVE x y symbol
```

### **Kết Thúc Trò Chơi**
```
Server → Client1: END symbol winner_name
       → Client2: END symbol winner_name
```

### **Mất Kết Nối**
```
Server → Client: DISCONNECT
```

---

## ❓ Thắc Mắc Thường Gặp

### **Q: Khi nhập IP server là gì?**
- **Localhost** (cùng máy): `localhost` hoặc `127.0.0.1`
- **Máy khác trong mạng**: Nhập IP của máy chạy server (ví dụ: `192.168.1.100`)

### **Q: Làm sao biết bạn bè có online không?**
- Chọn "Chơi với bạn bè" → xem danh sách bạn bè với dấu ✅

### **Q: Nếu bạn offline thì sao?**
- Không thể mời bạn offline → chuyển sang "Tìm người chơi ngẫu nhiên"

### **Q: Mã phòng có hết hạn không?**
- Hiện tại chưa có hết hạn → bạn bè phải nhập mã trong phiên chơi hiện tại

### **Q: Điểm có được lưu vĩnh viễn không?**
- ✅ Có! Lưu trong `users.json` → được tính vào xếp hạng

---

## 🐛 Xử Lý Lỗi

| Lỗi | Nguyên Nhân | Giải Pháp |
|-----|-----------|----------|
| "Không kết nối được server" | Server không chạy | Chạy `python server\server.py` |
| Bạn bè không hiển thị | Bạn bè offline | Chờ bạn bè online hoặc dùng matching random |
| Trò chơi bị hang | Client mất kết nối | Khởi động lại client |
| Điểm không được lưu | Server bị đóng | Chạy server trước khi chơi |

---

## 🎯 Đề Xuất Cải Tiến

- [ ] Thêm chat với đối thủ
- [ ] Lịch sử trận đấu (match history)
- [ ] Xếp hạng toàn cầu
- [ ] Phòng chơi công khai (public rooms)
- [ ] Đặt cược điểm (ranked matches)
- [ ] Avatar tùy chỉnh
- [ ] Badge/thành tích

---

**Chúc bạn chơi vui! 🎮**
