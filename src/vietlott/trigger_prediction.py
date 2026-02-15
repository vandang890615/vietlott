import os
import sys
import pandas as pd
import json
from datetime import datetime

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), "src"))

from vietlott.predictor.lstm_predictor import LSTMPredictor, log_predictions
from vietlott.config.products import get_config

def run_super_prediction(prod):
    print(f"🚀 KÍCH HOẠT HỆ THỐNG SOI CẦU SIÊU CẤP (SUPER PREDICTOR V5.2) CHO {prod.upper()}...")
    
    json_path = os.path.join("data", prod.replace("_","")+".jsonl")
    if not os.path.exists(json_path):
        print(f"❌ Lỗi: Không tìm thấy file dữ liệu {json_path}")
        return

    # 1. Load Data
    df = pd.read_json(json_path, lines=True).sort_values(by=["date", "id"])
    conf = get_config(prod)
    max_n = conf.max_value
    output_n = conf.size_output
    
    # 2. Setup AI Brain (Bidirectional LSTM + Attention)
    print("🧠 Đang khởi tạo bộ não AI (Ensemble + Attention)...")
    p = LSTMPredictor(window_size=15, max_num=max_n)
    d = p.prepare_data(df)
    X, y = p.create_sequences(d)
    p.build_model(input_shape=(X.shape[1], X.shape[2]))
    
    # 3. Deep Training
    print("⚙️ Đang huấn luyện AI trên bộ dữ liệu khổng lồ (3000+ kỳ)...")
    p.train(X, y, epochs=30)
    
    # 4. Super Prediction (Signal Fusion: AI + Biased Stats)
    print("📡 Đang thực hiện Hợp nhất Tín hiệu (Signal Fusion)...")
    tickets = []
    for i in range(10):
        # We pass df as context for the Signal Scorer
        ticket = p.predict_next(d[-p.window_size:], df_context=df, count=output_n)
        tickets.append(ticket)
        print(f"   Vé {i+1:02d}: {' '.join([f'{n:02d}' for n in ticket])}")
    
    # 5. Persistent Logging
    log_predictions(prod, tickets)
    print(f"\n✅ Đã chốt 10 bộ số Siêu Cấp và lưu vào Audit Log.")
    
    # Output result string for the UI/User
    result_str = "\n".join([f"Vé {i+1:02d}: {' '.join([f'{n:02d}' for n in t])}" for i, t in enumerate(tickets)])
    return result_str

if __name__ == "__main__":
    run_super_prediction("power_655")
