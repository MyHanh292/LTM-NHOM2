# 🎬 CloudVault - DEMO SCRIPT TRỰC TIẾP

## ⚙️ Chuẩn bị trước demo
1. **Đảm bảo đã start 3 server:**
   ```
   Terminal 1: cd g:\LTM\CK\backend_api && python app.py
   Terminal 2: cd g:\LTM\CK\socket_server && python server.py  
   Terminal 3: cd g:\LTM\CK\frontend && python -m http.server 8000
   ```

2. **Đảm bảo database sạch hoặc có dữ liệu test**
3. **Chuẩn bị 2 tài khoản test:**
   - hanh@gmail.com / hanh123
   - khanh@gmail.com / khanh123

4. **Chuẩn bị một file PDF/DOCX để upload**

---

## 📋 DEMO FLOW (Từng bước cụ thể)

### **PHẦN 1: ĐĂNG KÝ & ĐĂNG NHẬP (2 phút)**

#### Bước 1.1: Truy cập trang chủ
- Mở browser → `http://localhost:8000`
- Màn hình hiển thị: CloudVault Dashboard
- Click nút "Đăng ký" (hoặc Register)

#### Bước 1.2: Tạo tài khoản đầu tiên
- **Email:** hanh@gmail.com
- **Mật khẩu:** hanh123
- **Họ tên:** Mỹ Hạnh
- Click "Đăng ký"
- ✅ Thông báo thành công → Redirect về trang chủ

#### Bước 1.3: Tạo tài khoản thứ hai
- Click "Đăng xuất"
- Click "Đăng ký"
- **Email:** khanh@gmail.com
- **Mật khẩu:** khanh123
- **Họ tên:** Phạm Khánh
- Click "Đăng ký"
- ✅ Thông báo thành công → Redirect về trang chủ

#### Bước 1.4: Đăng nhập lại với tài khoản đầu tiên
- Click "Đăng xuất"
- Click "Đăng nhập"
- **Email:** hanh@gmail.com
- **Mật khẩu:** hanh123
- Click "Đăng nhập"
- ✅ Hiển thị tên "Mỹ Hạnh" ở top-right

---

### **PHẦN 2: UPLOAD FILE (3 phút)**

#### Bước 2.1: Truy cập trang Upload
- Click menu "📤 Tải lên"
- Hiển thị giao diện: Drag & Drop zone, Metadata form, Control buttons

#### Bước 2.2: Chọn file để upload
- **Cách 1 (Drag & Drop):** Kéo file PDF/DOCX vào Drop zone
- **Cách 2 (Browse):** Click "🖱️ Chọn tệp từ máy"
- ✅ Hiển thị: "📄 [filename] (X.XX MB)"
- ✅ Nút "▶️ Bắt đầu" được enable

#### Bước 2.3: Điền thông tin file
- **Chế độ chia sẻ:** Chọn "🌐 Công khai"
- **Tags:** Nhập "Toán, Lớp 12"
- **Mô tả:** Nhập "Tài liệu ôn tập môn Toán lớp 12"
- Click "▶️ Bắt đầu"

#### Bước 2.4: Xem quá trình upload (MỚI - có thời gian)
- ✅ **Hiển thị:**
  - Progress bar chạy từ 0% → 100%
  - Trạng thái: "Đang tải... 25% | 14:35:42"
  - Thời gian real-time cập nhật mỗi chunk
- ⏸️ Có thể **Tạm dừng** bằng nút "⏸️ Tạm dừng"
- ▶️ Tiếp tục bằng nút "▶️ Tiếp tục"

#### Bước 2.5: Upload hoàn tất (MỚI - auto-redirect)
- ✅ **Hiển thị:**
  - "✅ Upload hoàn tất! Tải lên lúc: 26/01/2026 14:36:15"
  - ⏰ Timestamp đầy đủ
  - Progress bar 100%
- ✅ **Auto-redirect** sau 2 giây → Trang "📂 Tài liệu của tôi"

#### Bước 2.6: Xem file vừa upload (MỚI - trang myfiles)
- ✅ File hiển thị ở trang "Tài liệu của tôi"
- Thông tin hiển thị:
  - Tên file: [filename]
  - Tác giả: Mỹ Hạnh
  - Tags: Toán, Lớp 12
  - Ngày tải: 26/01/2026
  - Mô tả: "Tài liệu ôn tập môn Toán lớp 12"

---

### **PHẦN 3: TEST CANCEL UPLOAD (2 phút) - MỚI**

#### Bước 3.1: Chọn file mới
- Click "📤 Tải lên"
- Drag & drop hoặc chọn file khác
- ✅ "▶️ Bắt đầu" được enable

#### Bước 3.2: Click "⏹️ Hủy" ngay khi upload bắt đầu
- Điền metadata như bước 2.3
- Click "▶️ Bắt đầu"
- Khi progress hiển thị 10-20%, click "⏹️ Hủy"

#### Bước 3.3: Verify cancel state (MỚI)
- ✅ Hiển thị: "⛔ Đã hủy upload. Vui lòng chọn file khác để tiếp tục."
- ✅ Drop zone reset lại trạng thái ban đầu
- ✅ **NỤT "▶️ BẮT ĐẦU" BƯỚC DISABLE**
- ❌ Không thể click "Bắt đầu" cho đến khi chọn file mới
- ✅ Phải chọn file mới để upload tiếp

---

### **PHẦN 4: EXPLORE & FAVORITE (3 phút)**

#### Bước 4.1: Xem file công khai
- Click "📂 Tài liệu" → Explore
- ✅ Hiển thị file "Tài liệu ôn tập môn Toán lớp 12" từ Mỹ Hạnh
- **Nút yêu thích:** 🤍 Yêu thích

#### Bước 4.2: Test nút yêu thích (MỚI - đã fix)
- Click "🤍 Yêu thích"
- ✅ **KHÔNG hiển thị alert "Vui lòng đăng nhập"**
- ✅ Nút chuyển thành: "❤️ Đã yêu thích" (màu đỏ)
- Nếu click lại → Quay lại "🤍 Yêu thích"

#### Bước 4.3: Xem file (MỚI - track recently viewed)
- Click vào file để xem
- ✅ File được tracked, lưu vào "Recently Viewed"

---

### **PHẦN 5: RECENTLY VIEWED (2 phút) - MỚI**

#### Bước 5.1: Truy cập trang Gần đây
- Click "⏱️ Gần đây"
- ✅ **Hiển thị ALL các file đã xem** (không giới hạn 2 file)
- Nếu xem 5 file → Hiển thị 5 file

#### Bước 5.2: Xem file từ trang Explore
- Quay lại "📂 Tài liệu"
- Click vào 2-3 file khác để xem
- Quay lại "⏱️ Gần đây"
- ✅ **ALL các file đã xem được hiển thị ngay**
- ✅ **Không cần refresh - auto-update trong real-time**

---

### **PHẦN 6: FAVORITES (2 phút)**

#### Bước 6.1: Xem danh sách yêu thích
- Click "❤️ Yêu thích"
- ✅ Hiển thị file "Tài liệu ôn tập môn Toán" từ Mỹ Hạnh
- Thông tin đầy đủ:
  - Ngày tải: 26/01/2026
  - Tags hiển thị đúng
  - Mô tả

#### Bước 6.2: Bỏ yêu thích
- Click "❤️ Đã yêu thích" → Quay lại "🤍 Yêu thích"
- ✅ File biến mất khỏi danh sách yêu thích

---

### **PHẦN 7: TRASH & RESTORE (2 phút) - MỚI**

#### Bước 7.1: Xóa file
- Click "📂 Tài liệu của tôi"
- Tìm file vừa upload → Click "Xóa" (delete button)
- ✅ File biến mất khỏi "Tài liệu của tôi"

#### Bước 7.2: Xem thùng rác (MỚI - fix date & tags)
- Click "🗑️ Rác"
- ✅ **File hiển thị ở Rác**
- ✅ **Ngày xóa hiển thị đúng:** 26/01/2026 (không phải N/A)
- ✅ **Tags hiển thị:** Toán, Lớp 12
- ✅ **Mô tả hiển thị:** "Tài liệu ôn tập môn Toán lớp 12"

#### Bước 7.3: Khôi phục file
- Click "🔄 Khôi phục"
- ✅ File biến mất khỏi Rác
- ✅ File quay lại "📂 Tài liệu của tôi"

---

### **PHẦN 8: TEST BỎ TỐI ƯU (1 phút)**

#### Bước 8.1: Verify cây thư mục sạch
- Kiểm tra: KHÔNG có file `test-*.html`, `server_improved.py`, `Nhom2-SourceCode`, `utils`
- ✅ Cây thư mục professional, clean

#### Bước 8.2: Verify date format consistency
- Mở DevTools (F12) → Network tab
- Upload file → Xem response API
- ✅ Date format: ISO format (2026-01-26T14:36:15.123456)
- ✅ Frontend hiển thị: 26/01/2026

---

## 🎯 KIỂM TRA CUỐI CÙNG

| Tính năng | Trạng thái | Ghi chú |
|-----------|-----------|--------|
| ✅ Đăng ký/Đăng nhập | ✅ OK | Tài khoản 2 người |
| ✅ Upload với progress | ✅ OK | Hiển thị time HH:MM:SS |
| ✅ Cancel upload | ✅ OK | Không thể restart cùng file |
| ✅ Auto-redirect myfiles | ✅ OK | Sau 2 giây upload xong |
| ✅ Recently Viewed ALL | ✅ OK | Không limit 2 file |
| ✅ Real-time tracking | ✅ OK | Tự động update sau xem |
| ✅ Favorite button | ✅ OK | Không alert khi logged-in |
| ✅ Trash date | ✅ OK | Hiển thị updated_at đúng |
| ✅ Trash tags | ✅ OK | Hiển thị tag danh sách |
| ✅ Code clean | ✅ OK | Xóa test files, gọn nhẹ |

---

## 💡 ĐIỂM NỔI BẬT DEMO

1. **Upload Progress Time** - Hiển thị giờ upload real-time
2. **Auto Redirect** - Tự động về My Documents sau upload
3. **Recently Viewed ALL** - Không giới hạn, hiển thị tất cả
4. **Cancel State Lock** - Không upload lại sau cancel
5. **Date Accuracy** - Trash page hiển thị delete date đúng
6. **Tags Display** - Tags show ở trash page, favorites, myfiles
7. **Professional Structure** - Cây thư mục sạch, không test files

---

## 🔧 TROUBLESHOOT NHANH

**Nếu Recently Viewed không update:**
- Hard refresh: Ctrl+Shift+R
- Kiểm tra DevTools → Network tab xem API `/api/documents/recently-viewed` có chạy không

**Nếu Trash không hiển thị date:**
- Kiểm tra browser console (F12) xem có error không
- Reload trang rác

**Nếu Upload không redirect:**
- Kiểm tra Flask server log xem có error không
- Kiểm าว Socket.IO connection status

**Nếu Cancel button không disable Start:**
- Clear cache browser (Ctrl+Shift+Delete)
- Reload trang

---

**✅ READY TO DEMO! LET'S GO! 🚀**
