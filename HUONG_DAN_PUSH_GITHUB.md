# HƯỚNG DẪN PUSH PROJECT LÊN GITHUB

Để cập nhật code mới nhất lên kho lưu trữ GitHub của bạn, vui lòng làm theo các bước đơn giản sau.

## 🟢 CÁCH PUSH NHANH (KHUYẾN NGHỊ)

Bạn chỉ cần chạy file script tự động đã được chuẩn bị sẵn:

1.  Tìm file **`COMMIT_VA_PUSH.bat`** trong thư mục dự án.
2.  Nhấn đúp chuột (Double click) để chạy.
3.  Nhập thông điệp commit khi được hỏi (ví dụ: "Cap nhat data moi").
4.  Chờ script chạy xong là Code đã lên GitHub!

---

## 🟡 CÁCH PUSH THỦ CÔNG (COMMAND LINE)

Nếu bạn muốn dùng dòng lệnh (CMD/Terminal), hãy làm theo 3 bước chuẩn của Git:

### Bước 1: Thêm file vào danh sách chờ (Stage)
```bash
git add .
```
*(Dấu chấm `.` nghĩa là thêm tất cả thay đổi)*

### Bước 2: Lưu thay đổi (Commit)
```bash
git commit -m "Noi dung thay doi cua ban o day"
```

### Bước 3: Đẩy lên GitHub (Push)
```bash
git push origin main
```
*(Nếu kho của bạn dùng nhánh `master` thì đổi `main` thành `master`)*

---

## 🔴 GIẢI QUYẾT SỰ CỐ THƯỜNG GẶP

### 1. Lỗi "Updates were rejected because the remote contains work..."
**Nguyên nhân**: Trên GitHub có file mới mà máy bạn chưa tải về.
**Cách sửa**: Kéo code về trước khi đẩy lên.
```bash
git pull origin main
# Sau đó chạy lại lệnh push
git push origin main
```

### 2. Lỗi "Authentication failed"
**Nguyên nhân**: Sai mật khẩu hoặc chưa cài đặt quyền truy cập.
**Cách sửa**: Đăng nhập lại Git trên máy tính hoặc kiểm tra lại Personal Access Token.

---

## 💡 MẸO
- Nên **Pull** (kéo code về) trước khi bắt đầu chỉnh sửa code mỗi ngày để đảm bảo đồng bộ.
- Nên viết nội dung commit rõ ràng (ví dụ: "Fix lỗi nút bấm", "Thêm tính năng AI") dễ theo dõi sau này.
