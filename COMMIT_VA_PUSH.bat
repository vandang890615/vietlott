@echo off
chcp 65001 >nul
title Chuẩn bị push lên GitHub
color 0E

echo ═══════════════════════════════════════════════════════
echo    📦 CHUẨN BỊ PUSH LÊN GITHUB
echo ═══════════════════════════════════════════════════════
echo.

echo [1/6] Kiểm tra git status...
git status --short
echo.

pause
echo.

echo [2/6] Add files mới...
git add .gitignore
git add MO_PHAN_MEM.bat CAP_NHAT_DU_LIEU.bat KHOI_DONG_LAI.bat
git add src/vietlott/predictor/gui_app.py
git add src/vietlott/predictor/lstm_predictor.py
git add src/vietlott/predictor/web_app.py
git add README_GITHUB.md HUONG_DAN_PUSH_GITHUB.md
git add SUA_LOI_v11.1.md SUA_LOI_IM_LIM_v11.2.md 
git add KHAC_PHUC_LOI.md HUONG_DAN_SU_DUNG.md
echo ✅ Đã add xong!
echo.

echo [3/6] Xem những gì sẽ commit...
git status
echo.

pause
echo.

echo [4/6] Commit với message...
git commit -m "feat: Upgrade to v11.2 - Complete GUI with AI prediction

Major improvements:
- Add GUI with integrated update/audit buttons (v11.0)
- Fix prediction blocking logic when checked=true (v11.1)
- Fix silent button click issue with error popups (v11.2)
- Add batch scripts for easy launching on Windows
- Add comprehensive documentation and troubleshooting guides

Features:
- LSTM-based prediction for Mega 6/45 and Power 6/55
- Auto-crawl results from vietlott.vn
- Audit system to track prediction accuracy
- Real-time training progress display
- User-friendly GUI with clear feedback
"
echo.

IF %ERRORLEVEL% EQU 0 (
    echo ✅ Commit thành công!
) ELSE (
    echo ❌ Có lỗi khi commit!
    pause
    exit /b 1
)
echo.

echo [5/6] Xem commit vừa tạo...
git log -1 --stat
echo.

pause
echo.

echo ═══════════════════════════════════════════════════════
echo    ✅ CHUẨN BỊ XONG!
echo ═══════════════════════════════════════════════════════
echo.
echo 🎯 BÂY GIỜ ANH CẦN:
echo.
echo 1. Tạo repository trên GitHub:
echo    - Vào: https://github.com/new
echo    - Tên: vietlott-ai-predictor
echo    - Description: 🎰 AI-Powered Vietnamese Lottery Prediction using LSTM
echo    - Public/Private: Tùy chọn
echo    - ☐ KHÔNG tick "Initialize this repository..."
echo    - Nhấn "Create repository"
echo.
echo 2. Copy lệnh từ GitHub (phần "...or push an existing repository"):
echo    Sẽ có dạng:
echo    git remote add origin https://github.com/USERNAME/vietlott-ai-predictor.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. Hoặc chạy lệnh này (THAY YOUR_USERNAME):
echo    git remote remove origin
echo    git remote add origin https://github.com/YOUR_USERNAME/vietlott-ai-predictor.git
echo    git push -u origin master
echo.
echo 📖 Xem hướng dẫn chi tiết: HUONG_DAN_PUSH_GITHUB.md
echo.
pause
