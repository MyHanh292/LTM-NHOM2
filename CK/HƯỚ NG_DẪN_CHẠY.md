# 🚀 HỆ THỐNG UPLOAD TÀI LIỆU STUDOCU - HƯỚNG DẪN CHẠY

## 📋 Cấu Trúc Dự Án

```
project/
├── backend_api/          # Flask backend (port 5000)
├── socket_server/        # TCP socket server (port 6000)
├── socket_client/        # CLI client for testing
├── frontend/             # Web UI (port 8000)
├── database/             # MySQL schema
├── storage/              # File uploads storage
└── utils/                # Shared utilities
```

## ⚙️ YÊU CẦU HỆ THỐNG

- Python 3.7+
- MySQL 5.7+
- Node.js (optional, for npm packages)

## 🔧 BƯỚC 1: CÀI ĐẶT DEPENDENCIES

```bash
cd backend_api
pip install -r requirements.txt

cd ../socket_server
pip install -r requirements.txt

cd ../socket_client
pip install -r requirements.txt
```

## 🗄️ BƯỚC 2: TẠO DATABASE

```bash
mysql -u root -p < database/schema.sql
```

Hoặc dùng Python:
```bash
python -c "
import pymysql
conn = pymysql.connect(host='localhost', user='root', password='<password>')
cursor = conn.cursor()
with open('database/schema.sql', 'r') as f:
    for stmt in f.read().split(';'):
        if stmt.strip():
            cursor.execute(stmt)
conn.commit()
print('✅ Database created')
"
```

## 🚀 BƯỚC 3: CHẠY HỆ THỐNG (3 TERMINAL)

### Terminal 1: Socket Server (Port 6000)
```bash
cd socket_server
python server.py
# Output: Listening on port 6000...
```

### Terminal 2: Flask Backend (Port 5000)
```bash
cd backend_api
python app.py
# Output: Running on http://127.0.0.1:5000
```

### Terminal 3: Frontend (Port 8000)
```bash
cd frontend/web
python -m http.server 8000
# Output: Serving HTTP on port 8000
```

## 🌐 BƯỚC 4: TRUY CẬP GIAO DIỆN

```
http://localhost:8000
```

## 🧪 BƯỚC 5: KIỂM TRA CHỨC NĂNG

### Test 1: Đăng Ký
1. Vào `http://localhost:8000/register.html`
2. Nhập email, password
3. Click "Register"
4. Kỳ vọng: ✅ Đăng ký thành công

### Test 2: Đăng Nhập
1. Vào `http://localhost:8000/login.html`
2. Nhập email/password từ Test 1
3. Click "Login"
4. Kỳ vọng: ✅ Chuyển đến trang chính

### Test 3: Upload File
1. Click "Upload"
2. Chọn file từ máy
3. Click "Choose File" → chọn file
4. Click "Upload"
5. Kỳ vọng: ✅ File upload, progress bar chạy

### Test 4: Danh Sách Tài Liệu
1. Click "My Documents"
2. Kỳ vọng: ✅ Hiển thị file vừa upload

### Test 5: Tìm Kiếm
1. Nhập keyword trong search
2. Click "Search"
3. Kỳ vọng: ✅ Hiển thị kết quả

### Test 6: Download File
1. Vào "My Documents"
2. Click download icon
3. Kỳ vọng: ✅ File được download

### Test 7: Favorites
1. Click heart icon trên document
2. Click "Favorites" tab
3. Kỳ vọng: ✅ File xuất hiện trong Favorites

### Test 8: Trash
1. Click delete icon trên document
2. Click "Trash" tab
3. Kỳ vọng: ✅ File xuất hiện trong Trash

### Test 9: Upload via CLI
```bash
cd socket_client
python client.py
# Nhập: localhost, 6000, email, filename, filepath
```

### Test 10: Resume Upload
1. Bắt đầu upload file lớn
2. Ngắt kết nối (Ctrl+C)
3. Chạy lại upload → sẽ resume từ vị trí cũ

## 📊 ĐỌC LOGS

### Socket Server Logs
```bash
tail -f socket_server/logs/server.log
```

Output mẫu:
```
[2026-01-20 20:30:45] INFO     Server listening on port 6000
[2026-01-20 20:30:50] INFO     Client connected: 127.0.0.1:52345
[2026-01-20 20:31:00] INFO     Upload: test.pdf (1048576 bytes)
[2026-01-20 20:31:05] DEBUG    Chunk 1: 65536 bytes received
[2026-01-20 20:31:10] INFO     Upload completed
```

### Flask Logs
Console output hiển thị:
```
127.0.0.1 - - [20/Jan/2026 20:30:50] "POST /api/auth/register HTTP/1.1" 201
127.0.0.1 - - [20/Jan/2026 20:30:55] "POST /api/auth/login HTTP/1.1" 200
127.0.0.1 - - [20/Jan/2026 20:31:00] "GET /api/documents HTTP/1.1" 200
```

### Database Queries
```bash
mysql -u root -p upload_file

# Kiểm tra users
SELECT id, name, email FROM users;

# Kiểm tra documents
SELECT id, filename, user_id, created_at FROM documents;

# Kiểm tra favorites
SELECT COUNT(*) FROM user_favorites;
```

## ⚠️ TROUBLESHOOTING

### Lỗi: "Port 5000 already in use"
```bash
# Tìm process chiếm port
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Lỗi: "MySQL connection failed"
- Kiểm tra MySQL đang chạy: `mysql -u root -p`
- Kiểm tra database tạo được: `SHOW DATABASES;`
- Kiểm tra user tạo được: `USE upload_file; SHOW TABLES;`

### Lỗi: "No module named 'flask'"
```bash
pip install -r backend_api/requirements.txt
```

### Lỗi: Upload không hoạt động
1. Kiểm tra socket server đang chạy: `ps aux | grep server.py`
2. Kiểm tra kết nối: `nc -zv localhost 6000`
3. Xem logs: `tail socket_server/logs/server.log`

## 📈 KIỂM TRA HIỆU SUẤT

### Test upload file 100MB
```bash
cd socket_client
python client.py
# Chọn file 100MB, kiểm tra tốc độ upload
```

### Test concurrent users (3 clients)
Terminal 1-3: Chạy `python socket_client/client.py`

Kỳ vọng: Server xử lý 3 clients cùng lúc mà không crash

## 🔒 BẢO MẬT

- JWT tokens: 24 giờ hết hạn
- Passwords: Mã hóa bcrypt
- Input: Validate tất cả requests
- SQL Injection: Dùng parameterized queries
- CORS: Enabled cho frontend

## 📚 API ENDPOINTS

### Authentication
- `POST /api/auth/register` - Đăng ký
- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/logout` - Đăng xuất

### Documents
- `GET /api/documents` - Lấy danh sách
- `POST /api/documents` - Tạo document
- `GET /api/documents/<id>` - Chi tiết
- `DELETE /api/documents/<id>` - Xóa
- `PUT /api/documents/<id>` - Cập nhật

### Search & Filter
- `GET /api/search?q=keyword` - Tìm kiếm
- `GET /api/documents?visibility=public` - Lọc

### Favorites
- `POST /api/documents/<id>/favorite` - Thêm yêu thích
- `DELETE /api/documents/<id>/favorite` - Bỏ yêu thích

## 🔗 LIÊN HỆ & HỖ TRỢ

Nếu gặp vấn đề:
1. Xem logs: `tail socket_server/logs/server.log`
2. Kiểm tra database: `mysql -u root -p`
3. Test endpoints: `curl http://localhost:5000/api/health`
4. Restart servers: `Ctrl+C` rồi chạy lại

---

**Tài Liệu Cho: Lập Trình Mạng (Network Programming)**
**Trường: [Tên Trường]**
**Năm:** 2026
