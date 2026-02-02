#!/usr/bin/env bash

# CONFIG
# Cấu hình user git để tự động commit khi chạy trên GitHub Actions
USER="vandang890615"
EMAIL="action@github.com" 

# SETUP ENV
# Thiết lập đường dẫn
echo "Current dir: $(pwd)"
export PYTHONPATH="src"
export LOGURU_LEVEL="INFO"

# RANDOM DELAY
# Tránh bị chặn IP bằng cách chờ ngẫu nhiên từ 1s đến 60s
RANDOM_DELAY=$(( RANDOM % 60 + 1 ))
echo "Delaying for $RANDOM_DELAY seconds..."
sleep $RANDOM_DELAY

# CRAWL DATA
# Chạy crawler để lấy dữ liệu mới nhất
echo "Starting crawler..."
python src/vietlott/cli/crawl.py power_655
python src/vietlott/cli/missing.py power_655
python src/vietlott/cli/crawl.py power_645
python src/vietlott/cli/missing.py power_645

# RENDER
# Cập nhật thông tin trong README (nếu có script)
# python src/render_readme.py

# GIT COMMIT & PUSH
# Tự động đẩy dữ liệu mới lên lại GitHub
git config user.name "$USER"
git config user.email "$EMAIL"
git status
git add data/*.jsonl
# git add readme.md
git commit -m "auto: update daily data @ $(date +%Y-%m-%d)"
git push
