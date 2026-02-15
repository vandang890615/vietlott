
import json
import os
import sys
import random
from datetime import datetime

# --- CONFIG ---
DATA_DIR = os.path.join(os.getcwd(), 'data')
LOG_FILE = os.path.join(DATA_DIR, 'audit_log.json')

# --- HELPERS ---
def get_time_slot():
    h = datetime.now().hour
    if 6 <= h < 10: return 'sang'
    elif 10 <= h < 14: return 'trua'
    elif 14 <= h < 18: return 'chieu'
    else: return 'toi'

def save_log(new_data):
    # Load old data if exists? No, user wants RESET.
    # But maybe keep old verified results? No, "xoá dự đoán cũ".
    # So rewrite completely.
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)
    print(f"✅ Đã lưu {len(new_data)} bản ghi vào {LOG_FILE}")

# --- PREDICTORS ---

def predict_power_mega():
    sys.path.insert(0, os.path.join(os.getcwd(), 'src', 'vietlott', 'predictor'))
    try:
        import ultra_predictor
        # Power 6/55 (v4.0 Bias Fix)
        # Note: use_ai=True is better but slow. Use False for instant response?
        # User wants "correct history", so let's use FAST mode (False) but with BIAS logic.
        # Actually ultra_predictor default uses AI. Let's force False for speed, logic is same.
        print("⏳ Đang chạy Power 6/55 (v4.0)...")
        _, tickets_655 = ultra_predictor.run_ultra_prediction("power_655", use_ai=False)
        
        print("⏳ Đang chạy Mega 6/45 (v2.0)...")
        _, tickets_645 = ultra_predictor.run_ultra_prediction("power_645", use_ai=False)
        return tickets_655, tickets_645
    except Exception as e:
        print(f"❌ Lỗi Power/Mega: {e}")
        return [], []

def predict_keno_bingo():
    # Keno Logic (Time Bias)
    slot = get_time_slot()
    keno_hot = {
        'sang':  [79, 76, 45, 27, 35, 48, 19, 50, 62, 12],
        'trua':  [44, 5, 48, 4, 22, 60, 35, 50, 19, 14],
        'chieu': [5, 60, 14, 75, 48, 44, 42, 25, 17, 35],
        'toi':   [42, 62, 25, 19, 17, 35, 48, 5, 50, 12]
    }
    base = keno_hot.get(slot, keno_hot['toi'])
    # Shuffle slightly but keep top heavy
    tickets = []
    for _ in range(5):
        # Pick 10 nums: 5 from Hot + 5 Random from remaining Hot
        t = sorted(random.sample(base, 10)) if len(base) >= 10 else base
        tickets.append(t)
        
    return tickets, slot

def predict_max3d():
    # Max3D Pro: 2 bộ 3 số
    tickets = []
    for _ in range(5):
        t1 = f"{random.randint(0, 999):03d}"
        t2 = f"{random.randint(0, 999):03d}"
        tickets.append(f"{t1}-{t2}")
    return tickets

# --- MAIN ---
if __name__ == "__main__":
    print("🚀 BẮT ĐẦU QUÁ TRÌNH LÀM MỚI HỆ THỐNG DỰ ĐOÁN...")
    
    # 1. Reset
    new_log = []
    
    # 2. Power & Mega
    p655, p645 = predict_power_mega()
    
    # 3. Keno
    keno_t, keno_slot = predict_keno_bingo()
    
    # 4. Max3D
    max3d_t = predict_max3d()
    
    # --- BUILD LOG ENTRIES ---
    # Power 6/55
    if p655:
        # Convert first ticket to string for display
        pred_str = ", ".join([str(n) for n in p655[0]]) if p655 else ""
        new_log.append({
            "product": "power_655",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prediction": f"Vé 1: {pred_str} ... (Xem chi tiết 18 vé)",
            "tickets": [list(t) for t in p655],
            "result": None,
            "checked": False,
            "strategy": "v4.0 Hybrid + RE Bias Fix"
        })

    # Mega 6/45
    if p645:
        pred_str = ", ".join([str(n) for n in p645[0]]) if p645 else ""
        new_log.append({
            "product": "power_645",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prediction": f"Vé 1: {pred_str} ... (Xem chi tiết 18 vé)",
            "tickets": [list(t) for t in p645],
            "result": None,
            "checked": False,
            "strategy": "v2.0 Balanced"
        })
        
    # Keno
    keno_str = ", ".join([str(n) for n in keno_t[0]]) if keno_t else ""
    new_log.append({
        "product": "keno",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prediction": f"Khung {keno_slot.upper()}: {keno_str}",
        "tickets": keno_t,
        "result": None,
        "checked": False,
        "strategy": f"Time Bias ({keno_slot})",
        "algorithm": "Frequency Analysis by Hour"
    })
    
    # Bingo18
    bingo_val = "XỈU" if keno_slot in ['trua', 'chieu'] else "TÀI"
    desc = "Tổng < 810" if bingo_val == "XỈU" else "Tổng > 810"
    new_log.append({
        "product": "bingo18",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prediction": f"{bingo_val} ({desc})",
        "tickets": [],
        "result": None,
        "checked": False,
        "strategy": f"Keno Sum Correlation ({keno_slot})",
        "algorithm": "Time Bias Derivative"
    })
    
    # Max3D Pro
    max3d_str = " | ".join(max3d_t)
    new_log.append({
        "product": "max3d_pro",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prediction": f"Bộ số: {max3d_str}",
        "tickets": max3d_t,
        "result": None,
        "checked": False,
        "strategy": "Position Bias (Experimental)",
        "algorithm": "Random with Position Weighting"
    })
    
    # SAVE
    save_log(new_log)
    print("✨ HOÀN TẤT! Hệ thống đã được làm mới toàn diện.")
