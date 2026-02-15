import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
from vietlott.predictor.lstm_predictor import LSTMPredictor

def run_backtest(product_code, window_size=15, test_draws=20):
    print(f"🧪 BACKTESTING {product_code.upper()} (Testing last {test_draws} draws)...")
    
    # Load data
    json_path = os.path.join("data", product_code.replace("_","")+".jsonl")
    if not os.path.exists(json_path):
        print(f"❌ Error: Data file {json_path} missing.")
        return
        
    df = pd.read_json(json_path, lines=True).sort_values(by=["date", "id"])
    if len(df) < window_size + test_draws + 10:
        print(f"⚠️ Warning: Not enough data for backtest (Need {window_size + test_draws + 10} draws).")
        return

    # Configuration based on product
    from vietlott.config.products import get_config
    conf = get_config(product_code)
    max_val = conf.max_value
    output_size = conf.size_output
    
    # Initialize Predictor
    p = LSTMPredictor(window_size=window_size, max_num=max_val)
    all_data = p.prepare_data(df)
    
    hits = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    total_tickets = 0
    
    # We will slide through the test range
    # For each point, we train on data BEFORE that point and predict the NEXT draw
    start_idx = len(all_data) - test_draws
    
    for i in range(start_idx, len(all_data)):
        train_data = all_data[:i]
        actual_result_binary = all_data[i]
        actual_nums = np.where(actual_result_binary == 1)[0] + 1
        
        # Build and train (Simplified training for backtest speed)
        X, y = p.create_sequences(train_data)
        p.build_model(input_shape=(X.shape[1], X.shape[2]))
        p.train(X, y, epochs=15) # Faster training for test
        
        # Predict 10 tickets using Quantum Diversity Filter
        last_window = train_data[-window_size:]
        batch_tickets = p.predict_diverse_batch(last_window, df_context=df.iloc[:i], batch_size=10, count=output_size, diversity_weight=0.6)
        
        for ticket in batch_tickets:
            match_count = len(set(ticket) & set(actual_nums))
            hits[match_count] += 1
            total_tickets += 1
            
        print(f"   Draw {i-start_idx+1}/{test_draws} done.")

    # Report
    print(f"\n📈 BACKTEST RESULTS FOR {product_code.upper()}:")
    print(f"   Total Tickets: {total_tickets}")
    print(f"   Matches Distribution:")
    for k, v in hits.items():
        pct = (v / total_tickets) * 100
        print(f"   - {k} số: {v} lần ({pct:.2f}%)")
    
    jackpots = hits[6]
    wins_3plus = sum(hits[k] for k in range(3, 7))
    win_rate = (wins_3plus / total_tickets) * 100
    
    print(f"\n   🏆 Win Rate (>= 3 số): {win_rate:.2f}%")
    if jackpots > 0:
        print(f"   🔥 JACKPOT HITS: {jackpots} !!!")
    
    return win_rate

if __name__ == "__main__":
    import sys
    products = ["power_655", "power_645", "max3d_pro", "max3d", "lotto", "keno", "bingo18"]
    
    if len(sys.argv) > 1:
        products = [sys.argv[1]]
    
    summary = {}
    for product in products:
        try:
            wr = run_backtest(product, test_draws=5) # 5 draws x 10 tickets = 50 samples
            summary[product] = wr
        except Exception as e:
            print(f"❌ Failed backtest for {product}: {e}")
    
    print("\n" + "="*40)
    print("🏆 BẢNG TỔNG HỢP HIỆU SUẤT TRƯỚC (BACKTEST)")
    print("="*40)
    sorted_summary = sorted(summary.items(), key=lambda x: x[1], reverse=True)
    for p, wr in sorted_summary:
        print(f"🔹 {p: <15}: {wr: >6.2f}% Win Rate")
    print("="*40)
    if sorted_summary:
        print(f"🚀 KHUYÊN DÙNG: Bạn nên chơi {sorted_summary[0][0].upper()} vì AI đang có phong độ tốt nhất!")
