# ⚠️ HƯỚNG DẪN KHẮC PHỤC SỰ CỐ (TROUBLESHOOTING)

Nếu bạn gặp vấn đề trong quá trình sử dụng phần mềm, vui lòng tham khảo các giải pháp dưới đây trước khi yêu cầu hỗ trợ.

---

## 🛑 SỰ CỐ PHỔ BIẾN

### 1. Nút "Soi cầu" bấm vào không thấy hiện tượng gì
**Nguyên nhân:** AI đang huấn luyện ngầm (Training) hoặc đang tải dữ liệu.
**Khắc phục:**
*   Nhìn xuống thanh trạng thái (dưới cùng cửa sổ), nếu thấy chữ "Đang huấn luyện AI..." thì hãy đợi khoảng 30-60 giây.
*   Nếu đợi quá 2 phút mà vẫn không có kết quả -> **Khởi động lại phần mềm**.

### 2. Cập nhật dữ liệu bị lỗi "Timeout" hoặc quay mãi không xong
**Nguyên nhân:** Mạng Internet chập chờn hoặc trang chủ Vietlott bị nghẽn.
**Khắc phục:**
*   Kiểm tra lại kết nối Wifi/Internet.
*   Thử lại sau 15-20 phút.
*   Chạy lệnh này thủ công để xem lỗi chi tiết:
    ```bash
    python src/vietlott/cli/crawl.py power_655 --index_to 2
    ```

### 3. Lỗi "ModuleNotFoundError: No module named..."
**Nguyên nhân:** Chưa cài đủ thư viện Python hoặc môi trường bị lỗi.
**Khắc phục:**
Chạy file cài đặt lại thư viện:
```bash
pip install -r requirements.txt
```

### 4. Phần mềm báo "Đã có dự đoán chưa kiểm tra!"
**Nguyên nhân:** Bạn đã soi cầu cho kỳ này rồi nhưng chưa cập nhật kết quả để đối chiếu (Audit). Hệ thống chặn soi tiếp để tránh loạn dữ liệu.
**Khắc phục:**
*   Bước 1: Bấm nút **"🌐 CẬP NHẬT KẾT QUẢ MỚI"**.
*   Bước 2: Bấm nút **"🔍 KIỂM TRA DỰ ĐOÁN"**.
*   Bước 3: Sau đó mới được soi cầu tiếp.

---

## 🛠 CÔNG CỤ SỬA LỖI NHANH

### Cách 1: Khởi động lại "sạch"
Chạy file **`MO_PHAN_MEM.bat`** lại từ đầu. Đôi khi chỉ cần tắt đi bật lại là hết lỗi.

### Cách 2: Xóa Cache (Dữ liệu tạm)
Nếu phần mềm chạy sai logic liên tục, bạn có thể xóa bộ nhớ đệm:
1.  Vào thư mục `src/vietlott/predictor/__pycache__`
2.  Xóa toàn bộ file trong đó.
3.  Chạy lại phần mềm.

---

## 📞 HỖ TRỢ KỸ THUẬT

Nếu đã thử hết các cách trên mà vẫn không được, hãy tạo **Issue** trên GitHub kèm theo ảnh chụp màn hình lỗi và file `audit_log.json` (trong thư mục `data/`).

**Chúc bạn thành công!** 🛠️
