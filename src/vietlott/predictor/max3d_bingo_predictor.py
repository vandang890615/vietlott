import random
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter

def _load_data(product_code):
    """Load JSONL data for a product."""
    path = os.path.join("data", f"{product_code}.jsonl")
    if not os.path.exists(path):
        return None
    try:
        return pd.read_json(path, lines=True)
    except:
        return None

def predict_max3d(product_code="max3d", count=5):
    """
    Advanced Max 3D prediction using Frequency Bias and Pair Analysis.
    Works for Max 3D, Max 3D+, and Max 3D Pro.
    """
    df = _load_data("max3d" if "plus" in product_code else product_code)
    
    if df is None or df.empty:
        # Fallback to random if no data
        return [[f"{random.randint(0, 999):03d}", f"{random.randint(0, 999):03d}"] for _ in range(count)]

    # 1. Frequency Analysis
    all_draws = [val for res in df['result'] for val in res]
    freq = Counter(all_draws)
    
    # Get top 50 hot numbers
    hot_nums = [n for n, c in freq.most_common(50)]
    
    # 2. Pair Analysis (which 3-digit numbers appear together)
    pairs = Counter()
    for res in df['result']:
        res_sorted = sorted(res)
        for i in range(len(res_sorted)):
            for j in range(i + 1, len(res_sorted)):
                pairs[(res_sorted[i], res_sorted[j])] += 1
                
    hot_pairs = [p for p, c in pairs.most_common(30)]

    predictions = []
    for _ in range(count):
        # 50% chance to pick a hot pair, 50% to pick two hot numbers
        if random.random() > 0.5 and hot_pairs:
            pair = random.choice(hot_pairs)
            num1, num2 = pair
        else:
            num1 = random.choice(hot_nums)
            num2 = random.choice(hot_nums)
            while num1 == num2:
                num2 = random.choice(hot_nums)
        
        predictions.append([f"{int(num1):03d}", f"{int(num2):03d}"])
        
    return predictions

def predict_max3d_pro(count=5):
    return predict_max3d("max3d_pro", count)

def predict_bingo18(count=3):
    """
    Predict Bingo 18 by analyzing dice sum distribution and frequency.
    """
    df = _load_data("bingo18")
    
    if df is None or df.empty:
        # Theoretical bias
        now = datetime.now()
        hour = now.hour
        is_tai = 6 <= hour < 14 # Afternoon tends to be Xỉu?
        return {"tai_xiu": "Tài" if is_tai else "Xỉu", "sum_range": "11-13" if is_tai else "8-10", "desc": "Time Bias Heuristic"}

    # Frequency analysis
    all_sums = [sum(res) for res in df['result']]
    sum_freq = Counter(all_sums)
    hot_sum = sum_freq.most_common(1)[0][0]
    
    tai_count = sum(1 for s in all_sums if s > 10)
    xiu_count = len(all_sums) - tai_count
    
    is_tai = tai_count > xiu_count
    
    prediction = {
        "tai_xiu": "Tài" if is_tai else "Xỉu",
        "sum_range": f"{hot_sum-1}-{hot_sum+1}",
        "desc": f"Thống kê {len(df)} kỳ: {'Tài' if is_tai else 'Xỉu'} đang ưu thế ({max(tai_count, xiu_count)} kỳ)."
    }
    return prediction

if __name__ == "__main__":
    print("Max3D Pro Prediction:", predict_max3d_pro())
    print("Bingo18 Prediction:", predict_bingo18())
