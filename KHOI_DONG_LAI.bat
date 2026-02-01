@echo off
chcp 65001 >nul
title KHỞI ĐỘNG LẠI VIETLOTT AI
color 0B

echo ═══════════════════════════════════════════════════════
echo    🔄 KHỞI ĐỘNG LẠI VIETLOTT AI
echo ═══════════════════════════════════════════════════════
echo.

echo [1/3] Đóng phần mềm cũ...
taskkill /F /IM pythonw.exe >nul 2>&1
ping 127.0.0.1 -n 2 >nul

echo [2/3] Xóa cache Python...
rd /s /q src\vietlott\predictor\__pycache__ 2>nul
rd /s /q src\__pycache__ 2>nul

echo [3/3] Khởi động phần mềm với code mới...
set PYTHONPATH=src;src/vietlott/predictor
start pythonw.exe src/vietlott/predictor/gui_app.py

ping 127.0.0.1 -n 3 >nul

echo.
echo ═══════════════════════════════════════════════════════
echo    ✅ ĐÃ KHỞI ĐỘNG!
echo ═══════════════════════════════════════════════════════
echo.
echo Kiểm tra cửa sổ phần mềm (Alt+Tab).
echo.
echo 💡 THAY ĐỔI MỚI (v11.1):
echo    ✅ Logic cho phép soi cầu khi đã kiểm tra (checked=true)
echo    ✅ Không bị chặn nữa khi Power/Mega đã audit xong
echo    ✅ Popup hướng dẫn rõ ràng nếu còn bị chặn
echo.
pause
