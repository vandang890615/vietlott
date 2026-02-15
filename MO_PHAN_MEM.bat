@echo off
chcp 65001 >nul
title Khởi chạy Vietlott AI Predictor Pro
color 0B

echo ═══════════════════════════════════════════════════════
echo    🏆 VIETLOTT ULTRA PREDICTOR v4.0 (Hybrid + RE Bias)
echo    Ensemble AI + Hot Zone + Coverage + Machine Bias Correction
echo ═══════════════════════════════════════════════════════
echo.

REM Kiểm tra dữ liệu mới nhất trước khi mở app
echo [BƯỚC 1] Kiểm tra cập nhật dữ liệu...
python -c "import json, os; from datetime import datetime; df_path='data/power645.jsonl'; lines=open(df_path).readlines(); last=json.loads(lines[-1]); print(f'  └─ Mega 6/45: Kỳ #{last[\"id\"]} ({last[\"date\"]})'); df_path='data/power655.jsonl'; lines=open(df_path).readlines(); last=json.loads(lines[-1]); print(f'  └─ Power 6/55: Kỳ #{last[\"id\"]} ({last[\"date\"]})')"
echo.

echo [BƯỚC 2] Khởi động giao diện...
set PYTHONPATH=src;src/vietlott/predictor
start pythonw.exe src/vietlott/predictor/gui_app.py

timeout /t 3 /nobreak >nul
echo.
echo ═══════════════════════════════════════════════════════
echo    ✅ Ứng dụng đã khởi động! Kiểm tra cửa sổ GUI.
echo ═══════════════════════════════════════════════════════
echo.
echo 💡 LƯU Ý QUAN TRỌNG:
echo    - Nếu chưa thấy kết quả mới: Chạy "CAP_NHAT_DU_LIEU.bat"
echo    - Nếu không soi cầu được: Phải cập nhật dữ liệu trước
echo    - Mỗi kỳ CHỈ SOI 1 LẦN (đợi có kết quả mới soi tiếp)
echo.
pause
