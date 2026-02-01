# 🚀 HƯỚNG DẪN PUSH PROJECT LÊN GITHUB

## 📋 CHECKLIST TRƯỚC KHI PUSH

### ✅ Đã hoàn thành:
- [x] Update `.gitignore` (ignore test files và data)
- [x] Tạo `README_GITHUB.md` (README chuyên nghiệp)
- [x] Code v11.2 hoạt động tốt
- [x] Tất cả features đã test

### ⏳ Cần làm:
- [ ] Xóa files test không cần thiết
- [ ] Rename README
- [ ] Commit all changes
- [ ] Tạo repository trên GitHub
- [ ] Push code lên

---

## 🗑️ BƯỚC 1: DỌN DẸP FILES

Em đề xuất XÓA các files sau (không cần thiết cho GitHub):

```bash
# Files test
test_app.py
test_import.py
test_logic.py
test_write.txt

# Files hướng dẫn cá nhân (có thể giữ hoặc xóa tùy anh)
HUONG_DAN_CAP_NHAT.bat      # → Có thể xóa, đã merge vào README
HUONG_DAN_PHIEN_BAN_MOI.md  # → Có thể xóa, đã merge vào README
KHAC_PHUC_LOI.md            # → Nên giữ (Troubleshooting guide)
SUA_LOI_v11.1.md            # → Nên giữ (Changelog)
SUA_LOI_IM_LIM_v11.2.md     # → Nên giữ (Changelog)
```

### Lệnh

xóa (Windows):
```cmd
del test_app.py test_import.py test_logic.py test_write.txt
del HUONG_DAN_CAP_NHAT.bat HUONG_DAN_PHIEN_BAN_MOI.md
```

---

## 📝 BƯỚC 2: RENAME README

```cmd
# Backup README cũ
copy readme.md readme_OLD.md

# Dùng README mới cho GitHub
copy README_GITHUB.md README.md
```

**HOẶC** chỉnh sửa `README.md` hiện tại để thêm:
- Badges (Python version, License, etc.)
- Disclaimer rõ ràng
- Screenshots (nếu có)
- Installation instructions
- Usage guide

---

## 💾 BƯỚC 3: COMMIT CHANGES

### 3.1. Add files mới
```bash
git add .gitignore
git add MO_PHAN_MEM.bat CAP_NHAT_DU_LIEU.bat KHOI_DONG_LAI.bat
git add src/vietlott/predictor/gui_app.py
git add src/vietlott/predictor/lstm_predictor.py
git add README.md
git add SUA_LOI_v11.1.md SUA_LOI_IM_LIM_v11.2.md KHAC_PHUC_LOI.md
```

### 3.2. Commit với message rõ ràng
```bash
git commit -m "feat: Upgrade to v11.2 - Complete GUI with AI prediction

- Add GUI with integrated update/audit buttons
- Fix prediction blocking logic (v11.1)
- Fix silent button click issue with popups (v11.2)
- Add batch scripts for easy launching
- Update README with comprehensive documentation
- Add troubleshooting guides"
```

---

## 🌐 BƯỚC 4: TẠO REPOSITORY TRÊN GITHUB

### Option A: Qua Web Interface (Dễ nhất)

1. **Đăng nhập GitHub:** https://github.com
2. **Click "New repository"** (nút xanh góc trên)
3. **Điền thông tin:**
   ```
   Repository name:     vietlott-ai-predictor
   Description:         🎰 AI-Powered Vietnamese Lottery Prediction using LSTM
   Public/Private:      Public (hoặc Private nếu muốn)
   Initialize:          ☐ KHÔNG tick gì cả (đã có code rồi)
   ```
4. **Click "Create repository"**

### Option B: Qua GitHub CLI (Nếu đã cài `gh`)
```bash
gh repo create vietlott-ai-predictor --public --description "🎰 AI-Powered Vietnamese Lottery Prediction using LSTM"
```

---

## 🚀 BƯỚC 5: PUSH CODE LÊN GITHUB

### 5.1. Link repository (nếu chưa có remote)
```bash
# Xóa remote cũ (nếu có)
git remote remove origin

# Add remote mới
git remote add origin https://github.com/YOUR_USERNAME/vietlott-ai-predictor.git

# Hoặc dùng SSH (nếu đã setup SSH key)
git remote add origin git@github.com:YOUR_USERNAME/vietlott-ai-predictor.git
```

**THAY `YOUR_USERNAME` bằng username GitHub của anh!**

### 5.2. Push code
```bash
# Push lần đầu
git push -u origin master

# Hoặc nếu branch chính là 'main'
git push -u origin main
```

### 5.3. Nhập credentials (nếu dùng HTTPS)
- **Username:** GitHub username của anh
- **Password:** **KHÔNG PHẢI password GitHub!** Phải dùng **Personal Access Token**

#### Tạo Personal Access Token:
1. GitHub → Settings → Developer settings
2. Personal access tokens → Tokens (classic)
3. Generate new token (classic)
4. Chọn scope: `repo` (full control)
5. Copy token và dùng làm password

---

## ✅ BƯỚC 6: XÁC NHẬN

Sau khi push xong:

1. **Mở GitHub repository:** https://github.com/YOUR_USERNAME/vietlott-ai-predictor
2. **Kiểm tra:**
   - [ ] README.md hiển thị đẹp
   - [ ] Code đã lên đầy đủ
   - [ ] .gitignore hoạt động (không thấy `data/*.jsonl`, `test_*.py`)
   - [ ] Batch files đã có

3. **Tùy chỉnh (nếu muốn):**
   - Add topics: `python`, `machine-learning`, `lstm`, `vietnamese`, `lottery`, `prediction`
   - Add description
   - Add website (nếu có)

---

## 🎨 BƯỚC 7: CHỈNH SỬA THÊM (Optional)

### 7.1. Thêm License
```bash
# Tạo file LICENSE
echo "MIT License" > LICENSE
# ... hoặc copy từ: https://choosealicense.com/licenses/mit/
git add LICENSE
git commit -m "docs: Add MIT License"
git push
```

### 7.2. Thêm CONTRIBUTING.md
```md
# Contributing to Vietlott AI Predictor

We welcome contributions! ...
```

### 7.3. Thêm screenshots
```md
![Screenshot](docs/images/screenshot.png)
```

### 7.4. Setup GitHub Actions (CI/CD)
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
```

---

## 📌 SUMMARY - CÁC LỆNH CHÍNH

```bash
# 1. Dọn dẹp
del test_*.py test_*.txt

# 2. Add & Commit
git add .
git commit -m "feat: Upgrade to v11.2 with complete GUI"

# 3. Add remote
git remote add origin https://github.com/YOUR_USERNAME/vietlott-ai-predictor.git

# 4. Push
git push -u origin master
```

---

## 🆘 TROUBLESHOOTING

### Lỗi: "failed to push some refs"
```bash
# Pull về trước
git pull origin master --rebase
git push
```

### Lỗi: "authentication failed"
- Đảm bảo dùng **Personal Access Token**, KHÔNG phải password
- Hoặc setup SSH key: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### Lỗi: "large files"
```bash
# Nếu file quá lớn (>100MB), dùng Git LFS
git lfs install
git lfs track "*.h5"  # Model files
git add .gitattributes
```

---

## 🎯 NEXT STEPS SAU KHI PUSH

1. **Share project:**
   - Chia sẻ link repository
   - Post lên social media (nếu muốn)

2. **Maintain:**
   - Trả lời Issues
   - Review Pull Requests
   - Update README khi có thay đổi

3. **Promote:**
   - Add to Awesome lists
   - Write blog post
   - Create demo video

---

**Ready to push? Let's go! 🚀**

Nếu cần em hỗ trợ từng bước, anh cứ bảo em nhé!
