# 📖 HƯỚNG DẪN SỬ DỤNG VIETLOTT AI PREDICTOR PRO v10.8

## 🚀 CÁCH SỬ DỤNG NHANH

### Bước 1: Mở phần mềm
- **Chạy file:** `MO_PHAN_MEM.bat`
- Cửa sổ GUI sẽ hiện ra với giao diện 3 cột:
  - **Cột trái:** Dự đoán Mega 6/45
  - **Cột giữa:** Kết quả mới nhất
  - **Cột phải:** Dự đoán Power 6/55

### Bước 2: Cập nhật dữ liệu mới (Quan trọng!)
- **Chạy file:** `CAP_NHAT_DU_LIEU.bat`
- **Khi nào cần chạy:**
  - Ngay sau khi có kết quả quay số mới (18h30 các ngày trong tuần)
  - Trước khi "Soi cầu mới" cho kỳ tiếp theo
  - Khi phần mềm báo "đang chờ dự thưởng" mà đã có kết quả rồi

### Bước 3: Soi cầu
- Nhấn nút **"🔥 SOI CẦU MEGA MỚI"** hoặc **"🔥 SOI CẦU POWER MỚI"**
- AI sẽ phân tích và đưa ra 10 bộ số dự đoán
- **LƯU Ý:** Mỗi kỳ CHỈ SOI 1 LẦN, phải đợi có kết quả rồi mới soi tiếp

### Bước 4: Xem kết quả kiểm tra
- Sau khi cập nhật dữ liệu, click vào **"Lịch sử dự báo"**
- Các dự đoán có ✅ là đã kiểm tra, ⏳ là đang chờ quay số
- Số đỏ: Trúng | Số trắng: Không trúng

---

## ⚠️ CÁC LỖI THƯỜNG GẶP & CÁCH KHẮC PHỤC

### 1. Không nhấn được nút "Soi cầu mới"
**Nguyên nhân:** Đã có dự đoán cho kỳ này rồi, đang chờ có kết quả mới.

**Giải pháp:**
1. Chạy `CAP_NHAT_DU_LIEU.bat` để lấy kết quả mới
2. Đóng và mở lại phần mềm
3. Bây giờ có thể soi cầu cho kỳ tiếp theo

### 2. Không tự động cập nhật dữ liệu
**Nguyên nhân:** Phần mềm không có tính năng auto-update, phải cập nhật thủ công.

**Giải pháp:**
- Sau mỗi kỳ quay số, **BẮT BUỘC** phải chạy `CAP_NHAT_DU_LIEU.bat`

### 3. Lỗi kiểm tra kết quả (Audit không hoạt động)
**Nguyên nhân:** Thiếu dữ liệu hoặc dữ liệu cũ.

**Giải pháp:**
1. Chạy lại `CAP_NHAT_DU_LIEU.bat`
2. Kiểm tra kết nối Internet
3. Khởi động lại phần mềm

---

## 📅 LỊCH QUAY SỐ (Tham khảo)

| Loại xổ số | Ngày quay | Giờ quay |
|------------|-----------|----------|
| **Mega 6/45** | Thứ 3, 5, 7 | 18:30 |
| **Power 6/55** | Thứ 2, 4, 6 | 18:30 |

**Quy trình chuẩn:**
1. **18:00 - 18:25:** Soi cầu cho kỳ tối nay (nếu chưa soi)
2. **18:30:** Theo dõi quay số trực tiếp
3. **19:00:** Chạy `CAP_NHAT_DU_LIEU.bat` để lấy kết quả
4. **19:05:** Xem kết quả kiểm tra trong phần mềm

---

## 🧠 HIỂU VỀ HỆ THỐNG AI

### AI hoạt động như thế nào?
- Sử dụng mô hình **LSTM (Long Short-Term Memory)** - Deep Learning
- Phân tích **15 kỳ quay gần nhất** để học pattern
- Đưa ra **10 bộ số** với độ đa dạng cao (thêm noise để tránh trùng lặp)

### Độ chính xác?
- Xổ số là **ngẫu nhiên**, AI chỉ tìm pattern thống kê
- **KHÔNG CÓ AI nào dự đoán chính xác 100%**
- Dùng để tham khảo, không nên phụ thuộc hoàn toàn

### Tại sao phải audit (kiểm tra)?
- Giúp đánh giá hiệu suất của mô hình AI
- Lưu lại thống kê để cải thiện thuật toán
- Ngăn chặn việc soi cầu nhiều lần cho 1 kỳ (gian lận)

---

## 📁 CẤU TRÚC FILE QUAN TRỌNG

```
thanhnhu-vietlott/
├── MO_PHAN_MEM.bat          ← Khởi động phần mềm
├── CAP_NHAT_DU_LIEU.bat     ← Cập nhật dữ liệu mới
├── data/
│   ├── power655.jsonl       ← Dữ liệu Power 6/55
│   ├── power645.jsonl       ← Dữ liệu Mega 6/45
│   └── audit_log.json       ← Lịch sử dự đoán & kiểm tra
└── src/vietlott/predictor/
    └── gui_app.py           ← Giao diện chính
```

**Lưu ý:**
- **KHÔNG XÓA** thư mục `data/` - chứa toàn bộ dữ liệu
- **KHÔNG EDIT** file `audit_log.json` thủ công - sẽ bị lỗi

---

## 🛠️ HỖ TRỢ KỸ THUẬT

### Cần cài đặt lại môi trường?
```bash
pip install -r requirements.txt
```

### Kiểm tra phiên bản Python:
```bash
python --version
# Yêu cầu: Python 3.11 hoặc 3.12
```

### Xóa cache AI (nếu bị lỗi mô hình):
- Đóng phần mềm
- Xóa thư mục `src/vietlott/predictor/__pycache__/`
- Chạy lại `MO_PHAN_MEM.bat`

---

## 🎯 MẸO SỬ DỤNG HIỆU QUẢ

1. **Cập nhật đều đặn:** Chạy `CAP_NHAT_DU_LIEU.bat` ngay sau mỗi kỳ quay
2. **Soi cầu đúng lúc:** Trước 18h00 của ngày có kỳ quay
3. **Kiểm tra kết quả:** Luôn xem audit để hiểu AI đang hoạt động ra sao
4. **Không spam:** 1 kỳ = 1 lần soi, đừng soi nhiều lần (hệ thống sẽ chặn)
5. **Backup dữ liệu:** Thỉnh thoảng backup thư mục `data/` để giữ lịch sử

---

**📞 Liên hệ hỗ trợ:** Nếu gặp lỗi khác, mô tả chi tiết và gửi file `audit_log.json` để được hỗ trợ.
