
import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))
sys.path.append(os.path.join(os.getcwd(), "src", "vietlott", "predictor"))

from lstm_predictor import LSTMPredictor
from signal_scorer import PositionalSignalScorer, apply_positional_signals

def analyze_bingo18():
    print("=== PHÂN TÍCH CHUYÊN SÂU AI BINGO 18 v9.5 ===")
    
    # 1. Load Data
    path = "data/bingo18.jsonl"
    if not os.path.exists(path):
        print(f"Lỗi: Không tìm thấy file {path}")
        return
        
    df = pd.read_json(path, lines=True).sort_values(by=["date", "id"])
    print(f"[*] Đã tải {len(df)} kỳ quay gần nhất.")
    
    # 2. Setup Predictor
    p = LSTMPredictor(window_size=25, max_num=6, mode="positional", slots=3)
    data = p.prepare_data(df)
    X, y = p.create_sequences(data)
    
    print(f"[*] Đang huấn luyện Neural Core (Window: 25, Slots: 3)...")
    p.build_model(input_shape=(X.shape[1], X.shape[2]))
    p.train(X, y, epochs=10) # Run short training for analysis
    
    # 3. Get Raw AI Probabilities for the next draw
    last_window = data[-p.window_size:]
    raw_probs = p.model.predict(last_window.reshape(1, p.window_size, -1), verbose=0)[0]
    raw_probs = raw_probs.reshape(3, 6) # 3 slots, 6 numbers each
    
    print("\n[📊] XÁC SUẤT NGUYÊN BẢN TỪ MẠNG NEURAL (Hạng mục 1-6):")
    for i in range(3):
        row_str = " | ".join([f"{n}: {raw_probs[i, n-1]:.2%}" for n in range(1, 7)])
        print(f" Slot {i+1} (Vị trí {i+1}): {row_str}")
        
    # 4. Analyze Signals (Gap & Frequency)
    scorer = PositionalSignalScorer(df, max_num=6, slots=3)
    freq, gap = scorer.get_positional_signals()
    
    print("\n[📡] PHÂN TÍCH TÍN HIỆU THỊ TRƯỜNG (BIAS):")
    for i in range(3):
        top_freq = np.argmax(freq[i]) + 1
        top_gap = np.argmax(gap[i]) + 1
        print(f" Vị trí {i+1}: Số hay về nhất: {top_freq} | Số 'Gan' nhất (đang lặn): {top_gap}")
        
    # 5. Fusion (Combining AI + Signals)
    final_probs = apply_positional_signals(raw_probs, freq, gap)
    
    print("\n[🎯] XÁC SUẤT SAU KHI TỐI ƯU (AI + Signals):")
    for i in range(3):
        best_num = np.argmax(final_probs[i]) + 1
        row_str = " | ".join([f"{n}: {final_probs[i, n-1]:.2%}" for n in range(1, 7)])
        print(f" Vị trí {i+1}: {row_str} -> CHỐT: {best_num}")
        
    # 6. Diversified Tickets
    print("\n[🎟️] DANH SÁCH 3 BỘ SỐ TỐI ƯU NHẤT:")
    tickets = p.predict_diverse_batch(data[-p.window_size:], df_context=df, batch_size=3, count=3, diversity_weight=0.4)
    for i, t in enumerate(tickets):
        m_sum = sum(t)
        tx = "NHỎ" if m_sum <= 9 else "HÒA" if m_sum <= 11 else "LỚN"
        print(f" Bộ {i+1:02d}: {t} -> Tổng: {m_sum} ({tx})")

    # 7. Triple Hunter Analysis
    all_triples = [[i,i,i] for i in range(1,7)]
    latest_draws = df.sort_values(by="id", ascending=False).head(500)
    triple_gaps = {}
    for triple in all_triples:
        gap_val = 500
        for i, res in enumerate(latest_draws['result']):
            if list(res) == triple:
                gap_val = i
                break
        triple_gaps[tuple(triple)] = gap_val
    
    target_triple = max(triple_gaps, key=triple_gaps.get)
    print(f"\n[💎] PHÂN TÍCH SĂN BỘ BA (TRIPLE HUNTER):")
    print(f" Mục tiêu tiềm năng nhất: {'-'.join(map(str, target_triple))}")
    print(f" Số kỳ đã vắng bóng: {triple_gaps[target_triple]} kỳ.")
    print(f" Chiến thuật: Nuôi bộ {target_triple[0]}x3 và bọc lót ô {'NHỎ' if sum(target_triple)<=9 else 'LỚN'}.")

if __name__ == "__main__":
    analyze_bingo18()
