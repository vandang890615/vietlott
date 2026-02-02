@echo off
chcp 65001 >nul
title Cập nhật dữ liệu Vietlott
color 0E

echo ═══════════════════════════════════════════════════════
echo    📥 CẬP NHẬT DỮ LIỆU VIETLOTT MỚI NHẤT
echo ═══════════════════════════════════════════════════════
echo.

echo [1/3] 🌐 Lấy kết quả Power 6/55 từ vietlott.vn...
python src/vietlott/cli/crawl.py power_655 --index_to 2
if %errorlevel% neq 0 (
    echo ❌ Lỗi kết nối! Kiểm tra mạng Internet.
    pause
    exit /b
)
echo     ✅ Hoàn thành!
echo.

echo [2/3] 🌐 Lấy kết quả Mega 6/45 từ vietlott.vn...
python src/vietlott/cli/crawl.py power_645 --index_to 2
if %errorlevel% neq 0 (
    echo ❌ Lỗi kết nối! Kiểm tra mạng Internet.
    pause
    exit /b
)
echo     ✅ Hoàn thành!
echo.

echo [3/3] 🔍 Kiểm tra kết quả dự đoán cũ (Audit)...
python -c "from src.vietlott.predictor.lstm_predictor import check_audit_log; check_audit_log()"
echo     ✅ Hoàn thành!
echo.

echo ═══════════════════════════════════════════════════════
echo    🎉 CẬP NHẬT THÀNH CÔNG!
echo ═══════════════════════════════════════════════════════
echo.
echo Bây giờ anh có thể:
echo   1. Đóng cửa sổ GUI cũ (nếu đang mở)
echo   2. Chạy lại "MO_PHAN_MEM.bat"
echo   3. Soi cầu mới hoặc xem kết quả đã kiểm tra
echo.
pause
