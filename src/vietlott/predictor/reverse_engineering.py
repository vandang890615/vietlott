#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REVERSE ENGINEERING XỔ SỐ - PHÁT HIỆN QUY LUẬT ẨN (ADVANCED)
Cập nhật:
- Thêm cấu hình độ nhạy (Sensitivity Levels)
- Module Deep Learning: 
  + LSTM (Recurrent)
  + Transformer (Attention Mechanism)
- Chiến lược LỌC SỐ (Reduction Strategy): Loại bỏ bộ số xác suất thấp
"""

import numpy as np
from collections import Counter, defaultdict
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
from scipy import stats
import json
import os
import argparse
import random
import sys

# Suppress TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# ================= CLASS UTILS =================
class SensitivityConfig:
    def __init__(self, level: str = 'normal'):
        self.level = level
        if level == 'high':
            self.p_value_threshold = 0.10
            self.corr_threshold = 0.15
            self.position_bias_pct = 0.12
            self.sum_std_threshold = 18
            self.modulo_bias_threshold = 0.05
        else:
            self.p_value_threshold = 0.05
            self.corr_threshold = 0.3
            self.position_bias_pct = 0.15
            self.sum_std_threshold = 12
            self.modulo_bias_threshold = 0.10

class HiddenPatternDetector:
    def __init__(self, config: SensitivityConfig, product_type="power_645"):
        self.history = []
        self.config = config
        self.anomalies = []
        self.stats = {} 
        self.product_type = product_type
        self.max_num = 55 if "655" in product_type else 45
        
    def add_draw(self, numbers: List[int], draw_id: str = None, date: str = None):
        if not numbers: return
        self.history.append({
            'numbers': sorted(numbers),
            'draw_id': draw_id or str(len(self.history) + 1),
            'date': date
        })

    def load_from_jsonl(self, filepath: str):
        print(f"Loading data from {filepath}...")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if 'result' in data:
                            numbers = [int(n) for n in data['result']]
                            self.add_draw(numbers, data.get('id'), data.get('date'))
                    except: continue
            self.history.sort(key=lambda x: x['draw_id'])
            print(f"Loaded {len(self.history)} draws (Max Num: {self.max_num}).")
        except Exception as e:
            print(f"Error loading: {e}")

    def analyze_basic_stats(self):
        """Calculate basic stats for filtering later"""
        sums = [sum(d['numbers']) for d in self.history]
        self.stats['mean_sum'] = np.mean(sums)
        self.stats['std_sum'] = np.std(sums)
        
        # Even/Odd Stats
        even_counts = [len([n for n in d['numbers'] if n % 2 == 0]) for d in self.history]
        self.stats['even_odd_dist'] = Counter(even_counts)
        
        print("\n📊 THỐNG KÊ CƠ BẢN (Dùng cho bộ lọc):")
        print(f"   - Tổng trung bình: {self.stats['mean_sum']:.1f} (Std: {self.stats['std_sum']:.1f})")
        print(f"   - Phân bố Chẵn/Lẻ phổ biến nhất: {self.stats['even_odd_dist'].most_common(1)[0][0]} số chẵn")

    def report(self):
        pass

# ================= DEEP LEARNING MODULES =================

class DeepLearningPredictor:
    def __init__(self, history, max_num=45):
        self.history = history
        self.look_back = 10
        self.num_classes = max_num # 45 or 55
    
    def prepare_data(self):
        print(f"   - Preparing data (Lookback={self.look_back}, MaxNum={self.num_classes})...")
        data_vectors = []
        for draw in self.history:
            vec = np.zeros(self.num_classes)
            for num in draw['numbers']:
                if 1 <= num <= self.num_classes:
                    vec[num-1] = 1
            data_vectors.append(vec)
            
        data_vectors = np.array(data_vectors)
        X, y = [], []
        for i in range(len(data_vectors) - self.look_back):
            X.append(data_vectors[i:(i + self.look_back)])
            y.append(data_vectors[i + self.look_back])
        return np.array(X), np.array(y)
    
    def evaluate(self, model, X_test, y_test):
        print("\n   - Đánh giá trên tập Test:")
        predictions = model.predict(X_test, verbose=0)
        avg_matches = 0
        for i in range(len(predictions)):
            pred_probs = predictions[i]
            top_6_indices = pred_probs.argsort()[-6:][::-1]
            predicted_nums = [idx + 1 for idx in top_6_indices]
            
            real_nums_indices = np.where(y_test[i] == 1)[0]
            real_nums = [idx + 1 for idx in real_nums_indices]
            
            matches = len(set(predicted_nums) & set(real_nums))
            avg_matches += matches
        
        avg_matches /= len(predictions)
        print(f"   🔴 Số lượng trùng khớp trung bình: {avg_matches:.2f} / 6 số")
        return avg_matches

    def predict_next_probs(self, model, X_last):
        """Return the probability distribution for the next draw."""
        last_sequence = X_last[-1].reshape(1, self.look_back, self.num_classes)
        next_pred_probs = model.predict(last_sequence, verbose=0)[0]
        return next_pred_probs

class TransformerPredictor(DeepLearningPredictor):
    def run(self, epochs=20):
        print("\n" + "🤖"*30)
        print("KHỞI ĐỘNG MODULE TRANSFORMER (ATTENTION)")
        print("🤖"*30)
        
        try:
            import tensorflow as tf
            from tensorflow.keras import layers, models, optimizers
        except ImportError:
            return None

        X, y = self.prepare_data()
        test_size = 50
        if len(X) > test_size:
            X_train, X_test = X[:-test_size], X[-test_size:]
            y_train, y_test = y[:-test_size], y[-test_size:]
        else:
            X_train, X_test = X, X
            y_train, y_test = y, y

        # Transformer Block Integration
        inputs = layers.Input(shape=(self.look_back, self.num_classes))
        
        # Multi-Head Attention
        attention = layers.MultiHeadAttention(num_heads=4, key_dim=32)(inputs, inputs)
        attention = layers.Dropout(0.1)(attention)
        res = layers.Add()([inputs, attention])
        res = layers.LayerNormalization(epsilon=1e-6)(res)
        
        # Feed Forward
        x = layers.GlobalAveragePooling1D()(res)
        x = layers.Dense(128, activation="relu")(x)
        x = layers.Dropout(0.3)(x)
        outputs = layers.Dense(self.num_classes, activation="sigmoid")(x)
        
        model = models.Model(inputs=inputs, outputs=outputs)
        model.compile(loss='binary_crossentropy', optimizer=optimizers.Adam(0.001), metrics=['accuracy'])
        
        print(f"   - Training Transformer ({epochs} epochs)...")
        model.fit(X_train, y_train, epochs=epochs, batch_size=32, verbose=0)
        
        if len(X) > test_size:
            self.evaluate(model, X_test, y_test)
            
        probs = self.predict_next_probs(model, X)
        
        # Print top prediction for log
        top_6_indices = probs.argsort()[-6:][::-1]
        vals = sorted([idx + 1 for idx in top_6_indices])
        print(f"🔮 DỰ ĐOÁN (TRANSFORMER TOP 6): {vals}")
        
        return probs

# ================= FILTERING STRATEGY =================

class FilterStrategy:
    def __init__(self, history, max_num=45, ai_probs=None):
        self.history = history
        self.max_num = max_num
        self.ai_probs = ai_probs
        
        # Calculate stats for boundaries
        sums = [sum(d['numbers']) for d in history]
        if sums:
            self.min_sum = np.percentile(sums, 5)  # Loại bỏ 5% thấp nhất
            self.max_sum = np.percentile(sums, 95) # Loại bỏ 5% cao nhất
        else:
            self.min_sum = 0
            self.max_sum = 999
            
    def check_sum(self, nums):
        s = sum(nums)
        return self.min_sum <= s <= self.max_sum
    
    def check_even_odd(self, nums):
        # Chấp nhận tỷ lệ chẵn lẻ: 2:4, 3:3, 4:2
        evens = len([n for n in nums if n % 2 == 0])
        return 2 <= evens <= 4
        
    def check_consecutive(self, nums):
        # Không quá 2 bộ số liên tiếp (VD: 1,2,3 là không tốt)
        sorted_nums = sorted(nums)
        for i in range(len(sorted_nums)-2):
            if sorted_nums[i+2] == sorted_nums[i+1] + 1 == sorted_nums[i] + 2:
                return False
        return True
    
    def check_last_digit(self, nums):
        # Đa dạng đuôi số: Cần ít nhất 4 đuôi số khác nhau
        lds = set(n % 10 for n in nums)
        return len(lds) >= 4

    def generate_optimized_tickets(self, count=10):
        print("\n" + "🛡️"*30)
        print("CHIẾN LƯỢC LỌC & TỐI ƯU (AI-DRIVEN REDUCTION)")
        print("🛡️"*30)
        print(f"   -> Sử dụng xác suất từ mô hình Transformer để lấy mẫu")
        print(f"   -> Loại bỏ bộ số có Tổng ngoài [{self.min_sum:.0f}, {self.max_sum:.0f}]")
        print(f"   -> Chỉ nhận tỷ lệ Chẵn/Lẻ: 2:4, 3:3, 4:2")
        print(f"   -> Loại bỏ bộ 3 số liên tiếp (VD: 1,2,3)")
        print(f"   -> Yêu cầu ít nhất 4 đuôi số khác nhau")
        
        valid_tickets = []
        attempts = 0
        max_attempts = count * 10000 # Increased attempts as finding valid weighted samples might be harder
        
        # Prepare probabilities
        if self.ai_probs is not None:
            # Normalize to sum to 1
            p = self.ai_probs
            p = p / np.sum(p)
            print("   -> Đã áp dụng trọng số AI cho việc tạo vé.")
        else:
            p = None
            print("   -> Cảnh báo: Không có trọng số AI, sử dụng ngẫu nhiên.")
            
        while len(valid_tickets) < count and attempts < max_attempts:
            attempts += 1
            
            try:
                # Weighted random generation if probs available
                if p is not None:
                    # Choose 6 numbers based on AI probability
                    # range(1, self.max_num + 1) corresponds to indices 0..max_num-1
                    # self.ai_probs has length self.max_num (hopefully)
                    nums = np.random.choice(
                        range(1, self.max_num + 1), 
                        size=6, 
                        replace=False, 
                        p=p
                    )
                    nums = sorted(nums)
                else:
                    nums = sorted(random.sample(range(1, self.max_num + 1), 6))
            except Exception as e:
                # Fallback if probability math fails
                nums = sorted(random.sample(range(1, self.max_num + 1), 6))
            
            # Apply Filters
            if not self.check_sum(nums): continue
            if not self.check_even_odd(nums): continue
            if not self.check_consecutive(nums): continue
            if not self.check_last_digit(nums): continue
            
            # Check for duplicates
            if list(nums) not in valid_tickets:
                valid_tickets.append(list(nums))
        
        print(f"\n✅ Đã tạo {len(valid_tickets)} bộ số tối ưu (sau {attempts} lần thử):")
        for i, t in enumerate(valid_tickets, 1):
            print(f"   {i}. {t} (Tổng: {sum(t)})")
        return valid_tickets

def run_analysis_and_get_report(product_type="power_645"):
    """
    Run the full analysis and return the report as a string AND the generated tickets.
    Returns: (report_string, tickets_list)
    """
    import io
    from contextlib import redirect_stdout
    
    # Configure path based on product
    filename = "power655.jsonl" if "655" in product_type else "power645.jsonl"
    max_num = 55 if "655" in product_type else 45
    
    # Locate file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Try typical locations
    paths_to_try = [
        os.path.join(os.getcwd(), 'data', filename),
        os.path.join(base_dir, '..', '..', '..', 'data', filename),
        os.path.join(base_dir, 'data', filename)
    ]
    
    target_file_path = None
    for p in paths_to_try:
        if os.path.exists(p):
            target_file_path = p
            break
            
    # Capture stdout
    f = io.StringIO()
    tickets = []
    
    with redirect_stdout(f):
        if not target_file_path:
            print(f"❌ Không tìm thấy file dữ liệu: {filename}")
            return f.getvalue(), []

        print(f"🎯 ĐANG PHÂN TÍCH: {product_type.upper().replace('_', ' ')}")
        
        # 1. Load Data
        detector = HiddenPatternDetector(SensitivityConfig(level='normal'), product_type)
        detector.load_from_jsonl(target_file_path)
        detector.analyze_basic_stats()

        # 2. Run Transformer
        transformer = TransformerPredictor(detector.history, max_num=max_num)
        # Use more epochs for deeper analysis
        probs = transformer.run(epochs=30) 
        
        # 3. Run Filter Strategy with AI Probs
        filter_strat = FilterStrategy(detector.history, max_num=max_num, ai_probs=probs)
        tickets = filter_strat.generate_optimized_tickets(count=10)

    return f.getvalue(), tickets

def main():
    # Test run
    report, tickets = run_analysis_and_get_report("power_645")
    print(report)
    print("Tickets returned:", tickets)

if __name__ == "__main__":
    main()
