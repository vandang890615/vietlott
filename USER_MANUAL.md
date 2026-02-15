# HƯỚNG DẪN SỬ DỤNG & QUY TRÌNH KIỂM THỬ (TEST PROCESS)

Dưới đây là quy trình chuẩn để sử dụng và kiểm tra các chức năng của VIETLOTT AI PRO v5.0.

## 1. Quy trình Kiểm thử & Soi cầu (Standard Workflow)

### Bước 1: Kiểm tra dữ liệu & Kết quả mới nhất (Crawl Data)
- **Mục đích:** Đảm bảo hệ thống có kết quả quay thưởng mới nhất từ Vietlott.
- **Thao tác:**
    1. Tại giao diện chính, bấm nút **"CẬP NHẬT KẾT QUẢ MỚI"** (hoặc "TẢI/LÀM MỚI DỮ LIỆU").
    2. Quan sát thanh trạng thái hoặc terminal: Hệ thống sẽ tải dữ liệu cho Mega, Power, Max 3D, Keno, và Lotto.
    3. **Lưu ý:** Với Lotto (dữ liệu giả lập), hệ thống sẽ tự sinh dữ liệu nếu chưa có.

### Bước 2: Thực hiện Soi cầu (Prediction)
- **Mục đích:** Dùng AI để dự đoán bộ số cho kỳ quay kế tiếp.
- **Thao tác:**
    1. Chọn Tab sản phẩm mong muốn (ví dụ: **MEGA 6/45**, **POWER 6/55**, **LOTTO**, **MAX 3D PRO**).
    2. Quan sát khung "Lịch sử": Nếu hiện **"SẴN SÀNG SOI CẦU MỚI"**, bấm nút **"SOI CẦU..."**.
    3. Chờ đợi: AI sẽ chạy mô hình (khoảng 5-30 giây tùy game).
    4. **Kết quả:** Bộ số dự đoán sẽ hiện ở khung bên phải (kèm ngày giờ).
    5. **Tự động lưu:** Nếu ô "Tự động lưu" được chọn, kết quả sẽ được ghi vào Nhật ký (Audit Log) với trạng thái ⏳ (Đang chờ).

### Bước 3: Kiểm tra & Đối soát kết quả (Audit)
- **Mục đích:** Kiểm tra xem các dự đoán cũ đã trúng thưởng chưa khi có kết quả mới.
- **Thao tác:**
    1. Sau khi có kết quả quay thưởng mới (đã làm Bước 1), vào Tab **"AUDIT"** hoặc bấm nút **"KIỂM TRA DỰ ĐOÁN CŨ"**.
    2. Hệ thống sẽ so sánh các dự đoán có trạng thái ⏳ với kết quả thực tế.
    3. **Hiển thị:**
        - Nếu trúng: Trạng thái chuyển sang ✅, các số trúng sẽ được tô màu.
        - Nếu trượt: Trạng thái vẫn là ✅ (đã kiểm tra) nhưng ít số trùng.
    4. Xem chi tiết tại khung "Lịch sử dự báo" của từng Tab.

### Bước 4: Xem Thống kê hiệu suất (Statistics)
- **Mục đích:** Đánh giá độ chính xác của AI theo thời gian.
- **Thao tác:**
    1. Chọn Tab **"THỐNG KÊ (STATS)"**.
    2. Bấm **"TRÍCH XUẤT BÁO CÁO CHI TIẾT"**.
    3. Xem tỷ lệ thắng, tần suất xuất hiện của các số.

---

## 2. Tính năng Mới (New Features)

- **Lotto 5/35:**
    - Sử dụng dữ liệu giả lập (do chưa có API chính thức).
    - Có thể soi cầu và xem kết quả như các game khác.
- **Max 3D Pro:**
    - Soi cặp số (ví dụ: 123 - 456).
    - Kết quả hiển thị dạng cặp.
- **Bingo 18:**
    - Soi Tài/Xỉu và khoảng tổng (ví dụ: Tài (11-13)).
- **Tự động (Auto-Scheduler):**
    - Check vào "Tự động soi cầu" ở Tab Keno.
    - Hệ thống sẽ tự chạy mỗi 5 phút (Keno) hoặc 30 phút (các game khác) để tìm kết quả mới và soi cầu.

## 3. Lưu ý
- Dữ liệu **Lotto** hiện tại là **giả lập (Mock Data)** để kiểm thử tính năng. Khi có nguồn dữ liệu thật, hệ thống sẽ tự động cập nhật.
- Để kiểm tra chức năng **Đối soát (Audit)** ngay lập tức, bạn có thể sửa thủ công file `data/audit_log.json` (đổi ngày dự đoán về quá khứ) để hệ thống so sánh với dữ liệu giả lập.

---
**Chúc bạn may mắn với VIETLOTT AI ULTRA PRO!**
