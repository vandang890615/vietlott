# 🎰 Vietlott AI Predictor Pro

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)](https://www.tensorflow.org/)

> 🤖 **AI-Powered Vietnamese Lottery Prediction System** sử dụng LSTM Deep Learning để phân tích và dự đoán kết quả xổ số Vietlott.

![Version](https://img.shields.io/badge/version-11.2-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

---

## 📌 Tổng quan

**Vietlott AI Predictor Pro** là ứng dụng GUI desktop được xây dựng bằng Python, tích hợp:
- 🧠 **LSTM Neural Network** cho dự đoán thông minh
- 🌐 **Tự động crawl dữ liệu** từ vietlott.vn
- 🔍 **Audit system** để đánh giá độ chính xác
- 📊 **Giao diện trực quan** với Tkinter

### ⚠️ Disclaimer
> **LƯU Ý QUAN TRỌNG:** Đây là dự án **NGHIÊN CỨU VÀ HỌC TẬP**. Xổ số là trò chơi may rủi hoàn toàn ngẫu nhiên. Không có AI nào có thể dự đoán chính xác 100%. Chúng tôi không khuyến khích việc cờ bạc. Vui lòng chơi có trách nhiệm.

---

## ✨ Tính năng

### 🎯 Chức năng chính:
- ✅ **Dự đoán AI:** Sử dụng LSTM để tạo 10 bộ số dự đoán cho mỗi kỳ quay
- ✅ **Auto-crawl:** Tự động lấy kết quả mới nhất từ vietlott.vn
- ✅ **Audit System:** Tự động kiểm tra và đánh giá kết quả dự đoán
- ✅ **Lịch sử:** Lưu trữ và hiển thị toàn bộ lịch sử dự đoán
- ✅ **Countdown Timer:** Đếm ngược thời gian đến kỳ quay tiếp theo

### 🎮 Hỗ trợ:
- 🔴 **Mega 6/45** (Thứ 3, 5, 7)
- 🟠 **Power 6/55** (Thứ 2, 4, 6)

### 🆕 Phiên bản mới (v11.2):
- ✅ Giao diện tích hợp 2 nút: "Cập nhật kết quả" và "Kiểm tra dự đoán"
- ✅ Popup thông báo rõ ràng cho mọi hành động
- ✅ Xử lý lỗi chi tiết với messagebox
- ✅ Hiển thị tiến trình training AI real-time

---

## 🚀 Cài đặt

### Yêu cầu hệ thống:
- **Python:** 3.11 hoặc 3.12
- **OS:** Windows 10/11 (hỗ trợ tốt nhất)
- **RAM:** Tối thiểu 4GB
- **Internet:** Cần kết nối để crawl dữ liệu

### Bước 1: Clone repository
```bash
git clone https://github.com/YOUR_USERNAME/thanhnhu-vietlott.git
cd thanhnhu-vietlott
```

### Bước 2: Tạo virtual environment (khuyến nghị)
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### Bước 3: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

**Dependencies chính:**
- `tensorflow` - LSTM neural network
- `pandas` - Data processing
- `scikit-learn` - Machine learning utilities
- `beautifulsoup4` - Web crawling
- `requests` - HTTP requests
- `tkinter` - GUI (built-in với Python)

---

## 🎮 Sử dụng

### Cách 1: Sử dụng file batch (Windows - Đơn giản nhất)
```bash
# Mở phần mềm
double-click: MO_PHAN_MEM.bat

# Cập nhật dữ liệu (sau mỗi kỳ quay)
double-click: CAP_NHAT_DU_LIEU.bat

# Khởi động lại (nếu cần)
double-click: KHOI_DONG_LAI.bat
```

### Cách 2: Command line
```bash
# Set PYTHONPATH
set PYTHONPATH=src;src/vietlott/predictor  # Windows
export PYTHONPATH=src:src/vietlott/predictor  # Linux/Mac

# Chạy GUI
python src/vietlott/predictor/gui_app.py

# Hoặc crawl thủ công
python src/vietlott/cli/crawl.py power_655 --index_to 2
python src/vietlott/cli/crawl.py power_645 --index_to 2
```

---

## 📖 Hướng dẫn sử dụng

### 1️⃣ Giao diện chính

```
┌─────────────┬─────────────────┬─────────────┐
│  MEGA 6/45  │  KẾT QUẢ MỚI    │  POWER 6/55 │
│             │     NHẤT        │             │
│ [SOI CẦU]   │  [🌐] [🔍]     │ [SOI CẦU]   │
│             │                 │             │
│ Dự đoán     │  Hiển thị       │ Dự đoán     │
│ + Lịch sử   │  kết quả        │ + Lịch sử   │
└─────────────┴─────────────────┴─────────────┘
```

### 2️⃣ Quy trình sử dụng hàng ngày

**Sau mỗi kỳ quay (18h30):**
1. Nhấn **"🌐 CẬP NHẬT KẾT QUẢ MỚI"** (đợi 30-60s)
2. Nhấn **"🔍 KIỂM TRA DỰ ĐOÁN"** (đợi 5s)
3. Xem kết quả trong "Lịch sử dự báo"

**Trước khi quay số (trước 18h30):**
1. Nhấn **"🔥 SOI CẦU MỚI"** (đợi ~30s training AI)
2. Xem 10 bộ số dự đoán được tạo

### 3️⃣ Lịch quay số

| Loại xổ số | Ngày quay | Giờ quay |
|------------|-----------|----------|
| **Mega 6/45** | Thứ 3, 5, 7 | 18:30 |
| **Power 6/55** | Thứ 2, 4, 6 | 18:30 |

---

## 🏗️ Kiến trúc

### Cấu trúc dự án:
```
thanhnhu-vietlott/
├── src/
│   └── vietlott/
│       ├── cli/              # Command-line tools
│       │   ├── crawl.py      # Web crawler
│       │   └── missing.py    # Backfill missing data
│       ├── config/           # Configuration
│       ├── crawler/          # Crawler logic
│       └── predictor/
│           ├── gui_app.py    # 🔥 Main GUI application
│           ├── lstm_predictor.py  # LSTM model
│           └── web_app.py    # Flask web interface (experimental)
├── data/                     # Data storage (gitignored)
│   ├── power645.jsonl        # Mega 6/45 results
│   ├── power655.jsonl        # Power 6/55 results
│   └── audit_log.json        # Prediction audit log
├── *.bat                     # Windows batch scripts
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

### Luồng dữ liệu:
```
vietlott.vn
     ↓ (crawl.py)
  data/*.jsonl
     ↓ (lstm_predictor.py)
   LSTM Model
     ↓ (train 15 epochs)
 10 Predictions
     ↓ (log_predictions)
audit_log.json
     ↓ (check_audit_log)
  Win/Loss Analysis
```

---

## 🤖 Công nghệ

### Machine Learning:
- **Model:** LSTM (Long Short-Term Memory)
- **Framework:** TensorFlow 2.x
- **Input:** 15 kỳ quay gần nhất
- **Output:** 10 bộ số dự đoán (6 số mỗi bộ)
- **Training:** 15 epochs mỗi lần soi cầu

### Data Processing:
- **Pandas:** Data manipulation và analysis
- **NumPy:** Numerical computations
- **Scikit-learn:** Data preprocessing

### GUI:
- **Tkinter:** Cross-platform GUI toolkit
- **Threading:** Async operations để giữ UI responsive

---

## 📊 Dataset

Dữ liệu được crawl tự động từ [vietlott.vn](https://vietlott.vn):
- **Format:** JSONL (JSON Lines)
- **Fields:** `date`, `id`, `result`, `page`, `process_time`
- **Update frequency:** Manual (sau mỗi kỳ quay)

**Ví dụ:**
```json
{"date":"2026-02-01","id":"01466","result":[1,18,21,23,30,36],"page":0,"process_time":"2026-02-01 19:00:00"}
```

---

## 🐛 Troubleshooting

### Lỗi thường gặp:

#### 1. "ModuleNotFoundError: No module named 'tensorflow'"
```bash
pip install tensorflow
```

#### 2. Nút "Soi cầu" không phản hồi
- **Nguyên nhân:** Training AI mất ~30 giây
- **Giải pháp:** Đợi thêm, xem status bar

#### 3. "No results" khi crawl
- **Nguyên nhân:** Website chưa cập nhật kết quả mới
- **Giải pháp:** Đợi sau 19h00 rồi thử lại

#### 4. Crash khi training
- **Nguyên nhân:** Thiếu RAM hoặc data bị lỗi
- **Giải pháp:** 
  ```bash
  # Cập nhật lại data
  python src/vietlott/cli/crawl.py power_655 --index_to 5
  ```

**Xem thêm:** [KHAC_PHUC_LOI.md](KHAC_PHUC_LOI.md)

---

## 📝 Changelog

### v11.2 (2026-02-01)
- ✅ FIX: Sửa lỗi "im lìm" khi nhấn nút soi cầu
- ✅ ADD: Popup thông báo cho mọi hành động
- ✅ IMPROVE: Hiển thị tiến trình training chi tiết
- ✅ IMPROVE: Error handling với messagebox

### v11.1 (2026-02-01)
- ✅ FIX: Sửa logic kiểm tra audit (checked=true → cho phép soi mới)
- ✅ ADD: Timeout 30s cho crawler
- ✅ IMPROVE: Thông báo lỗi chi tiết

### v11.0 (2026-02-01)
- ✅ ADD: 2 nút mới trong GUI: "Cập nhật" và "Kiểm tra"
- ✅ REMOVE: Không cần chạy file .bat nữa

**Xem chi tiết:** [SUA_LOI_v11.1.md](SUA_LOI_v11.1.md), [SUA_LOI_IM_LIM_v11.2.md](SUA_LOI_IM_LIM_v11.2.md)

---

## 🤝 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng:

1. Fork repository này
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

### Coding style:
- **Python:** PEP 8
- **Docstrings:** Google style
- **Type hints:** Khuyến khích sử dụng

---

## 📄 License

Dự án này được phân phối dưới **MIT License**. Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

**TL;DR:**
- ✅ Sử dụng tự do cho mục đích cá nhân
- ✅ Sửa đổi và phân phối lại
- ✅ Sử dụng thương mại
- ⚠️ Phải giữ lại thông tin license gốc
- ❌ Không có bảo hành

---

## 👨‍💻 Tác giả

**ThanhNhu** 
- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- Email: your.email@example.com

---

## 🙏 Credits

### Dữ liệu:
- [Vietlott](https://vietlott.vn) - Nguồn dữ liệu kết quả xổ số

### Thư viện:
- [TensorFlow](https://www.tensorflow.org/) - Deep learning framework
- [Pandas](https://pandas.pydata.org/) - Data analysis
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - Web scraping

---

## ⭐ Support

Nếu bạn thấy dự án này hữu ích, hãy cho một ⭐️ trên GitHub!

---

## 📞 Liên hệ

Có câu hỏi hoặc đề xuất? Tạo [Issue](https://github.com/YOUR_USERNAME/thanhnhu-vietlott/issues) hoặc liên hệ qua email.

---

<div align="center">

**Made with ❤️ in Vietnam 🇻🇳**

*Chơi có trách nhiệm - Không quá liều lĩnh*

</div>
