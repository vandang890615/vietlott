#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RE KENO & BINGO18 - ANALYSIS
============================
Phân tích chuyên sâu cho Keno (20/80) và Bingo18 (từ Keno).
Đặc biệt tập trung vào TIME BIAS (khung giờ) và FREQUENCY BIAS.
"""

import json
import os
import sys
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from scipy import stats

def load_keno_data(filepath):
    print(f"📂 Đang tải dữ liệu Keno từ {filepath}...")
    draws = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if 'result' in data:
                    # Keno có 20 số
                    nums = sorted([int(n) for n in data['result']])
                    
                    # Parse timestamp if available, else use date + fake time based on draw id?
                    # Keno quay từ 06:00 đến 21:55, 10 phút/kỳ
                    # ID format usually #00xxxxx
                    draw_id = data.get('id', '').replace('#', '')
                    date_str = data.get('date', '')
                    
                    draws.append({
                        'id': draw_id,
                        'date': date_str,
                        'numbers': nums,
                        'even_odd': data.get('odd_even', ''),
                        'big_small': data.get('big_small', '')
                    })
            except Exception:
                continue
    print(f"✅ Đã tải {len(draws)} kỳ quay Keno.")
    return draws

def analyze_time_bias(draws):
    """Phân tích bias theo khung giờ (sáng, trưa, chiều, tối)."""
    print(f"\n{'='*60}")
    print("⏰ PHÂN TÍCH TIME BIAS (THEO KHUNG GIỜ)")
    print(f"{'='*60}")
    
    # Keno quay liên tục, ta chia theo giờ dựa trên draw ID hoặc giả định
    # 96 kỳ/ngày
    # Giả sử draw ID tăng dần đều
    
    # Chia thành 4 khung:
    # 1. Sáng (06:00 - 10:00)
    # 2. Trưa (10:00 - 14:00)
    # 3. Chiều (14:00 - 18:00)
    # 4. Tối (18:00 - 22:00)
    
    # Vì không có giờ chính xác trong json, ta dùng modulo ID
    # Mỗi ngày có khoảng 95-96 kỳ
    
    slots = {0: 'Sáng', 1: 'Trưa', 2: 'Chiều', 3: 'Tối'}
    slot_freq = defaultdict(Counter)
    
    for d in draws:
        try:
            # Ước lượng slot dựa trên ID (tương đối)
            # Giả sử ID % 96 cho ra kỳ trong ngày
            did = int(d['id'])
            daily_idx = did % 96
            
            if daily_idx < 24: slot = 0
            elif daily_idx < 48: slot = 1
            elif daily_idx < 72: slot = 2
            else: slot = 3
            
            slot_freq[slot].update(d['numbers'])
        except:
            continue
            
    print("\n  📊 Top 5 số hay ra nhất theo khung giờ:")
    for s in range(4):
        freq = slot_freq[s]
        total = sum(freq.values())
        top5 = freq.most_common(5)
        top_str = ", ".join([f"{n}({c})" for n,c in top5])
        print(f"    🌅 {slots[s]}: {top_str}")

def analyze_keno_frequency(draws):
    """Phân tích tần suất 80 số."""
    print(f"\n{'='*60}")
    print("📊 PHÂN TÍCH TẦN SUẤT (1-80)")
    print(f"{'='*60}")
    
    freq = Counter()
    for d in draws:
        freq.update(d['numbers'])
        
    expected = len(draws) * 20 / 80  # Mỗi kỳ ra 20 số → xác suất 1/4
    
    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    
    print(f"  Kỳ vọng mỗi số: {expected:.1f} lần")
    
    print("\n  🔥 TOP 10 SỐ NÓNG NHẤT:")
    for n, c in sorted_freq[:10]:
        dev = (c - expected) / expected * 100
        print(f"    Số {n:02d}: {c} lần ({dev:+.1f}%)")
        
    print("\n  ❄️ TOP 10 SỐ LẠNH NHẤT:")
    for n, c in sorted_freq[-10:]:
        dev = (c - expected) / expected * 100
        print(f"    Số {n:02d}: {c} lần ({dev:+.1f}%)")
        
    return freq

def analyze_bingo_patterns(draws):
    """Phân tích pattern tổng số (Bingo)."""
    print(f"\n{'='*60}")
    print("🎲 PHÂN TÍCH BINGO/SUM PATTERNS")
    print(f"{'='*60}")
    # Keno result sum ranges from 210 to 1410 (theoretical)
    # Average sum = 20 * 40.5 = 810
    
    sums = []
    for d in draws:
        s = sum(d['numbers'])
        sums.append(s)
        
    avg = np.mean(sums)
    print(f"  Trung bình tổng: {avg:.1f} (Lý thuyết: 810)")
    
    # Chẵn/Lẻ tổng
    even_sum = sum(1 for s in sums if s % 2 == 0)
    print(f"  Tổng Chẵn: {even_sum} ({even_sum/len(sums)*100:.1f}%)")
    print(f"  Tổng Lẻ:   {len(sums)-even_sum} ({(len(sums)-even_sum)/len(sums)*100:.1f}%)")
    
    # Tài/Xỉu (trên/dưới 810)
    tai = sum(1 for s in sums if s > 810)
    print(f"  Tài (>810): {tai} ({tai/len(sums)*100:.1f}%)")
    print(f"  Xỉu (<=810): {len(sums)-tai} ({(len(sums)-tai)/len(sums)*100:.1f}%)")

def analyze_consecutive_draws(draws):
    """Số nào hay ra lại ngay kỳ sau?"""
    print(f"\n{'='*60}")
    print("cw PHÂN TÍCH LẶP (REPEAT NUMBERS)")
    print(f"{'='*60}")
    
    repeats = defaultdict(int)
    total_repeats = 0
    
    for i in range(len(draws)-1):
        curr = set(draws[i]['numbers'])
        next_d = set(draws[i+1]['numbers'])
        
        common = curr & next_d
        total_repeats += len(common)
        
        for n in common:
            repeats[n] += 1
            
    avg_repeat = total_repeats / (len(draws)-1)
    print(f"  Trung bình mỗi kỳ lặp lại: {avg_repeat:.1f} số từ kỳ trước")
    
    top_repeats = sorted(repeats.items(), key=lambda x: x[1], reverse=True)
    print("\n  🔄 TOP 10 số hay lặp lại nhất:")
    for n, c in top_repeats[:10]:
        print(f"    Số {n:02d}: {c} lần lặp")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(os.getcwd(), 'data', 'keno.jsonl')
    
    if not os.path.exists(path):
        print("❌ Không tìm thấy data/keno.jsonl")
        return
        
    draws = load_keno_data(path)
    
    if not draws:
        return

    # Run analysis
    analyze_keno_frequency(draws)
    analyze_time_bias(draws)
    analyze_bingo_patterns(draws)
    analyze_consecutive_draws(draws)
    
    print("\n✅ KENO/BINGO RE COMPLETE")

if __name__ == "__main__":
    main()
