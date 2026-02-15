import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
from collections import Counter
import sys
import io

# Force UTF-8 encoding for stdout/stderr to handle emojis on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class BiasAnalyzer:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.config = {
            "power655": {"max": 55, "size": 6},
            "power645": {"max": 45, "size": 6},
            "max3d": {"max": 999, "size": 20}, # Max 3D contains 20 sets of 3-digits in results
            "max3d_pro": {"max": 999, "size": 20},
            "keno": {"max": 80, "size": 20},
            "lotto": {"max": 35, "size": 6},
            "bingo18": {"max": 6, "size": 3}
        }

    def analyze(self, code):
        name = code.upper()
        path = os.path.join(self.data_dir, f"{code}.jsonl")
        if not os.path.exists(path):
            return f"❌ {name}: File not found."
        
        try:
            df = pd.read_json(path, lines=True)
            if df.empty: return f"⚠️ {name}: Data empty."
            
            total_draws = len(df)
            all_nums = [n for res in df['result'] for n in res]
            counts = Counter(all_nums)
            
            # 1. Hot/Cold
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            top_5 = sorted_counts[:5]
            bottom_5 = sorted_counts[-5:]
            
            # 2. Even/Odd
            even = sum(1 for n in all_nums if n % 2 == 0)
            odd = len(all_nums) - even
            even_pct = (even/len(all_nums))*100
            
            # 3. Gap Analysis (Only for Power/Mega/Lotto)
            # Find numbers that haven't appeared for a long time
            missing = []
            if code in ["power655", "power645", "lotto", "keno"]:
                max_val = self.config[code]["max"]
                latest_draws = df.sort_values(by="date", ascending=False).head(50)
                all_appearing = set([n for res in latest_draws['result'] for n in res])
                missing = [n for n in range(1, max_val + 1) if n not in all_appearing]

            # 4. Special Bias: Keno Time Slot
            time_bias = ""
            if code == "keno":
                df['hour'] = pd.to_datetime(df['date']).dt.hour # Assuming date field has time or using process_time
                # Note: 'date' in keno.jsonl is usually just YYYY-MM-DD. 
                # Need to use 'process_time' or check if browser timestamp is present.
                pass

            report = f"📊 {name} ({total_draws} kỳ quay):\n"
            report += f"   🔥 HOT (Hay về): {', '.join([f'{k}({v})' for k,v in top_5])}\n"
            report += f"   ❄️ COLD (Gan): {', '.join([f'{k}({v})' for k,v in bottom_5])}\n"
            report += f"   ⚖️ CHẴN/LẺ: {even_pct:.1f}% Chẵn | {100-even_pct:.1f}% Lẻ\n"
            if missing:
                report += f"   ⏳ SỐ LÂU CHƯA VỀ (Gan cực đại - 50 kỳ): {missing[:8]}...\n"
            
            # 5. Sample Size Warning
            confidence = "LOW"
            if total_draws > 1000: confidence = "HIGH (Siêu tin cậy)"
            elif total_draws > 300: confidence = "MEDIUM (Tạm ổn)"
            else: confidence = "LOW (Dữ liệu quá ít, kết quả chỉ mang tính tham khảo)"
            report += f"   📡 ĐỘ TIN CẬY: {confidence}\n"
            
            # Simple Bias Score
            observed = list(counts.values())
            if observed:
                std_dev = np.std(observed)
                bias_score = "BÌNH THƯỜNG"
                if std_dev > (total_draws * 0.1): bias_score = "NHIỄM BIAS NẶNG"
                elif std_dev > (total_draws * 0.05): bias_score = "BIAS NHẸ"
                report += f"   🛡️ ĐÁNH GIÁ: {bias_score}\n"
            
            return report + "\n"
        except Exception as e:
            return f"❌ {name} Error: {e}\n"

    def run(self):
        print("🔍 ĐANG KHỞI CHẠY HỆ THỐNG PHÂN TÍCH BIAS TOÀN DIỆN...\n")
        results = ""
        for code in self.config.keys():
            results += self.analyze(code)
        
        print(results)
        with open("data/bias_report.txt", "w", encoding="utf-8") as f:
            f.write(results)
        print("✅ Đã lưu báo cáo vào data/bias_report.txt")

if __name__ == "__main__":
    BiasAnalyzer().run()
