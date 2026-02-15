#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA PREDICTOR v2.0 - HỆ THỐNG DỰ ĐOÁN SIÊU CẤP
=====================================================
Chiến lược: Multi-Signal Ensemble + Combinatorial Coverage Optimization

Cải tiến so với phiên bản cũ:
1. Multi-Signal Scoring: 7 tín hiệu khác nhau để chấm điểm mỗi số
2. Ensemble AI: Kết hợp LSTM + Transformer + GRU + Statistical
3. Hot Zone Detection: Phát hiện 12-18 số "nóng" nhất
4. Pair Co-occurrence: Phân tích cặp số hay xuất hiện cùng nhau
5. Cycle Detection: Phát hiện chu kỳ xuất hiện của từng số
6. Smart Ticket Generation: Tối ưu hóa phủ sóng giữa 10 vé
7. Advanced Filters: Lọc thông minh theo quy luật thống kê

Mục tiêu: Nâng từ 3-4 số trúng lên 5-6 số trúng
"""

import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from itertools import combinations
from typing import List, Dict, Tuple, Optional
import json
import os
import sys
from datetime import datetime
from loguru import logger

# Suppress TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    from vietlott.config.products import get_config
except ImportError:
    class DummyConfig:
        def __init__(self, name):
            p1 = f"data/{name}.jsonl"
            p2 = f"data/{name.replace('_', '')}.jsonl"
            self.raw_path = p1 if os.path.exists(p1) else p2
    def get_config(name):
        return DummyConfig(name)


# ═══════════════════════════════════════════════════
# 1. NUMBER SCORER - Chấm điểm mỗi số bằng nhiều tín hiệu
# ═══════════════════════════════════════════════════

class NumberScorer:
    """Chấm điểm mỗi số từ 1 đến max_num bằng 7 tín hiệu khác nhau."""
    
    def __init__(self, draws: List[List[int]], max_num: int = 45):
        self.draws = draws  # List of sorted number lists
        self.max_num = max_num
        self.num_draws = len(draws)
        self.scores = {}  # {number: {signal_name: score}}
        
    def compute_all_signals(self) -> Dict[int, float]:
        """Tính tất cả tín hiệu và trả về điểm tổng hợp cho mỗi số."""
        print("   📊 Tính toán 9 tín hiệu dự đoán (đã tích hợp RE Bias)...")
        
        s1 = self._frequency_score()
        s2 = self._recency_score()
        s3 = self._gap_analysis_score()
        s4 = self._cycle_detection_score()
        s5 = self._position_bias_score()
        s6 = self._momentum_score()
        s7 = self._co_occurrence_boost()
        s8 = self._streak_score()
        s9 = self._machine_bias_score() # Tín hiệu 9: RE Bias
        
        # Trọng số cho mỗi tín hiệu (v3.0 - Hybrid RE)
        weights = {
            'frequency': 0.05,
            'recency': 0.20,       # Giảm nhẹ để nhường chỗ cho bias
            'gap': 0.15,
            'cycle': 0.05,
            'position': 0.05,
            'momentum': 0.15,
            'cooccurrence': 0.05,
            'streak': 0.10,
            'machine_bias': 0.20,  # TRỌNG SỐ CAO: Bias máy quay thực tế
        }
        
        final_scores = {}
        for num in range(1, self.max_num + 1):
            score = (
                weights['frequency'] * s1.get(num, 0) +
                weights['recency'] * s2.get(num, 0) +
                weights['gap'] * s3.get(num, 0) +
                weights['cycle'] * s4.get(num, 0) +
                weights['position'] * s5.get(num, 0) +
                weights['momentum'] * s6.get(num, 0) +
                weights['cooccurrence'] * s7.get(num, 0) +
                weights['streak'] * s8.get(num, 0) +
                weights['machine_bias'] * s9.get(num, 0)
            )
            
            # HARD FILTER: Dead numbers (Bias < 0) -> Score = -100
            if s9.get(num, 0) < 0:
                score = -100.0
                
            final_scores[num] = score
            
            
        # Normalize to [0, 1] (Handling Dead Numbers)
        valid_scores = [v for v in final_scores.values() if v > -50]
        max_s = max(valid_scores) if valid_scores else 1
        min_s = min(valid_scores) if valid_scores else 0
        range_s = max_s - min_s if max_s != min_s else 1
        
        for num in final_scores:
            if final_scores[num] <= -50:
                final_scores[num] = 0.0  # DEAD NUMBER -> 0 probability
            else:
                val = (final_scores[num] - min_s) / range_s
                final_scores[num] = max(0.001, val) # Ensure at least tiny probability for valid nums
                
        return final_scores
    
    def _frequency_score(self) -> Dict[int, float]:
        """Tín hiệu 1: Tần suất xuất hiện tổng thể."""
        counter = Counter()
        for draw in self.draws:
            counter.update(draw)
        
        max_freq = max(counter.values()) if counter else 1
        return {num: counter.get(num, 0) / max_freq for num in range(1, self.max_num + 1)}
    
    def _recency_score(self) -> Dict[int, float]:
        """Tín hiệu 2: Tần suất gần đây với time-decay mạnh (exponential)."""
        recent_window = min(20, len(self.draws))  # Giảm window xuống 20
        recent_draws = self.draws[-recent_window:]
        
        scores = defaultdict(float)
        for i, draw in enumerate(recent_draws):
            # Decay mạnh hơn: 5 kỳ gần nhất chiếm phần lớn
            weight = np.exp(-0.15 * (recent_window - 1 - i))
            for num in draw:
                scores[num] += weight
        
        max_s = max(scores.values()) if scores else 1
        return {num: scores.get(num, 0) / max_s for num in range(1, self.max_num + 1)}
    
    def _gap_analysis_score(self) -> Dict[int, float]:
        """Tín hiệu 3: Khoảng cách từ lần xuất hiện cuối (số "quá hạn")."""
        last_seen = {}
        for i, draw in enumerate(self.draws):
            for num in draw:
                last_seen[num] = i
        
        # Tính gap trung bình cho mỗi số
        avg_gaps = {}
        for num in range(1, self.max_num + 1):
            appearances = [i for i, draw in enumerate(self.draws) if num in draw]
            if len(appearances) >= 2:
                gaps = [appearances[j+1] - appearances[j] for j in range(len(appearances)-1)]
                avg_gaps[num] = np.mean(gaps)
            else:
                avg_gaps[num] = len(self.draws)  # Rất hiếm xuất hiện
        
        scores = {}
        for num in range(1, self.max_num + 1):
            current_gap = self.num_draws - 1 - last_seen.get(num, 0)
            avg_gap = avg_gaps.get(num, self.num_draws)
            
            if avg_gap > 0:
                # Nếu current_gap > avg_gap → số này "quá hạn" → điểm cao
                ratio = current_gap / avg_gap
                # Sigmoid-like function: cao nhất khi ratio ≈ 1.0-1.5
                scores[num] = 1.0 / (1.0 + np.exp(-2 * (ratio - 1.0)))
            else:
                scores[num] = 0.5
        
        max_s = max(scores.values()) if scores else 1
        return {num: scores[num] / max_s for num in scores}
    
    def _cycle_detection_score(self) -> Dict[int, float]:
        """Tín hiệu 4: Phát hiện chu kỳ xuất hiện."""
        scores = {}
        for num in range(1, self.max_num + 1):
            appearances = [i for i, draw in enumerate(self.draws) if num in draw]
            
            if len(appearances) < 3:
                scores[num] = 0.3
                continue
            
            # Tính các khoảng cách giữa các lần xuất hiện
            gaps = [appearances[j+1] - appearances[j] for j in range(len(appearances)-1)]
            
            if len(gaps) < 2:
                scores[num] = 0.3
                continue
            
            # Tìm chu kỳ phổ biến nhất
            gap_counter = Counter(gaps)
            most_common_gap, common_count = gap_counter.most_common(1)[0]
            
            # Kiểm tra xem số này có "đến lượt" theo chu kỳ không
            current_gap = self.num_draws - 1 - appearances[-1]
            
            # Nếu current_gap gần bằng most_common_gap → điểm cao
            cycle_score = np.exp(-abs(current_gap - most_common_gap) / max(most_common_gap, 1))
            
            # Bonus nếu chu kỳ ổn định (variance thấp)
            stability = common_count / len(gaps)
            
            scores[num] = cycle_score * (0.5 + 0.5 * stability)
        
        max_s = max(scores.values()) if scores else 1
        return {num: scores[num] / max_s for num in scores}
    
    def _position_bias_score(self) -> Dict[int, float]:
        """Tín hiệu 5: Thiên vị theo vị trí (số thứ 1-6 trong bộ)."""
        # Một số số có xu hướng xuất hiện ở vị trí nhất định
        position_counts = defaultdict(lambda: defaultdict(int))
        
        for draw in self.draws:
            sorted_draw = sorted(draw[:6])  # Chỉ lấy 6 số chính
            for pos, num in enumerate(sorted_draw):
                position_counts[num][pos] += 1
        
        scores = {}
        for num in range(1, self.max_num + 1):
            if num in position_counts:
                total = sum(position_counts[num].values())
                # Số có xu hướng vị trí rõ ràng → điểm cao hơn
                max_pos_count = max(position_counts[num].values())
                scores[num] = max_pos_count / max(total, 1)
            else:
                scores[num] = 0.0
        
        max_s = max(scores.values()) if scores else 1
        return {num: scores[num] / max_s for num in scores}
    
    def _momentum_score(self) -> Dict[int, float]:
        """Tín hiệu 6: Đà tăng/giảm (so sánh tần suất gần đây vs. tổng thể)."""
        # Tần suất tổng thể
        overall_freq = Counter()
        for draw in self.draws:
            overall_freq.update(draw)
        
        # Tần suất 10 kỳ gần nhất (ngắn hơn để bắt trend nhanh)
        recent_window = min(10, len(self.draws))
        recent_freq = Counter()
        for draw in self.draws[-recent_window:]:
            recent_freq.update(draw)
        
        scores = {}
        for num in range(1, self.max_num + 1):
            overall_rate = overall_freq.get(num, 0) / max(self.num_draws, 1)
            recent_rate = recent_freq.get(num, 0) / max(recent_window, 1)
            
            # Momentum = recent_rate / overall_rate
            if overall_rate > 0:
                momentum = recent_rate / overall_rate
                # Số đang "nóng" (momentum > 1) → điểm cao
                scores[num] = min(momentum, 4.0) / 4.0  # Mở rộng thang
            else:
                scores[num] = 0.0
        
        max_s = max(scores.values()) if scores else 1
        return {num: scores[num] / max_s for num in scores}
    
    def _co_occurrence_boost(self) -> Dict[int, float]:
        """Tín hiệu 7: Hay đi cùng với các số khác (pair analysis - gần đây)."""
        # Chỉ dùng 40 kỳ gần nhất cho pair analysis (focus recent)
        recent_draws = self.draws[-min(40, len(self.draws)):]
        pair_counts = Counter()
        for i, draw in enumerate(recent_draws):
            weight = 1.0 + 0.5 * (i / len(recent_draws))  # Recent pairs weighted more
            nums = sorted(draw[:6])
            for pair in combinations(nums, 2):
                pair_counts[pair] += weight
        
        # Cho mỗi số, tính "sức mạnh liên kết" trung bình
        scores = {}
        for num in range(1, self.max_num + 1):
            relevant_pairs = [(p, c) for p, c in pair_counts.items() if num in p]
            if relevant_pairs:
                avg_pair_strength = np.mean([c for _, c in relevant_pairs])
                scores[num] = avg_pair_strength
            else:
                scores[num] = 0.0
        
        max_s = max(scores.values()) if scores else 1
        return {num: scores[num] / max_s for num in scores}
    
    def _streak_score(self) -> Dict[int, float]:
        """Tín hiệu 8 (MỚI): Phát hiện số xuất hiện liên tục gần đây."""
        scores = {}
        window = min(8, len(self.draws))  # Check 8 kỳ gần nhất
        recent = self.draws[-window:]
        
        for num in range(1, self.max_num + 1):
            # Đếm trong bao nhiêu kỳ gần đây số này xuất hiện
            appearances = sum(1 for draw in recent if num in draw)
            
            # Streak bonus: xuất hiện 2+ lần trong 8 kỳ gần nhất
            if appearances >= 4:
                scores[num] = 1.0  # Xuất hiện 4+/8 kỳ → siêu nóng
            elif appearances >= 3:
                scores[num] = 0.85
            elif appearances >= 2:
                scores[num] = 0.6
            elif appearances >= 1:
                scores[num] = 0.3
            else:
                scores[num] = 0.0
            
            # Extra bonus: xuất hiện trong kỳ GẦN NHẤT
            if num in recent[-1]:
                scores[num] = min(1.0, scores[num] + 0.15)
            # Extra bonus: xuất hiện trong 2 kỳ gần nhất liên tiếp
            if len(recent) >= 2 and num in recent[-1] and num in recent[-2]:
                scores[num] = min(1.0, scores[num] + 0.10)
        
        max_s = max(scores.values()) if scores else 1
        return {num: scores[num] / max_s for num in scores}

    def _machine_bias_score(self) -> Dict[int, float]:
        """Tín hiệu 9 (MỚI - QUAN TRỌNG): Bias máy quay từ Reverse Engineering."""
        scores = {}
        
        # POWER 6/55 BIAS
        # Phát hiện từ RE: Số > 50 cực hiếm, đặc biệt 53-55 là "số chết"
        if self.max_num == 55:
            # 1. Dead Zone (Vùng chết) - Phạt cực nặng
            for num in range(1, self.max_num + 1):
                if num in [55, 54]:      # Tử huyệt: Chưa bao giờ ra hoặc cực hiếm
                    scores[num] = -1.0   # Score âm để chắc chắn không được chọn
                elif num in [53, 52]:    # Rất lạnh
                    scores[num] = 0.1
                elif num in [50, 51, 48, 49]: # Lạnh
                    scores[num] = 0.2
                elif num in [45, 46, 47]:     # Hơi lạnh
                    scores[num] = 0.3
                else:
                    scores[num] = 0.5    # Neutral baseline
            
            # 2. Hot Bias (Vùng nóng) - Boost số máy quay "thích"
            hot_bias_nums = [22, 34, 9, 20, 8, 23, 3, 31, 1, 12]
            for num in hot_bias_nums:
                scores[num] = min(1.0, scores[num] + 0.4)
                
            # 3. Pair Bias Boost - Cặp số hay đi cùng nhau (từ RE)
            pair_boost = {
                13: 0.2, 9: 0.1,  # Pair (9, 13)
                11: 0.2, 22: 0.1, # Pair (11, 22)
            }
            for num, boost in pair_boost.items():
                if scores[num] > 0: # Chỉ boost nếu không phải số chết
                    scores[num] = min(1.0, scores[num] + boost)
                
        # MEGA 6/45 FAIRNESS
        # Phát hiện từ RE: Máy quay Mega rất công bằng, không có dead zone
        else:
            for num in range(1, self.max_num + 1):
                scores[num] = 0.5  # Neutral baseline
            
            # Chỉ boost nhẹ các số hay ra vì bias vị trí (tự nhiên)
            pos_bias_nums = [1, 2, 4, 3, 5]
            for num in pos_bias_nums:
                scores[num] = min(1.0, scores[num] + 0.1)
            
            # Cặp số hay đi cùng (từ RE)
            pair_boost = {
                10: 0.1, 22: 0.1,
                18: 0.1, 29: 0.1,
                24: 0.1, 37: 0.1
            }
            for num, boost in pair_boost.items():
                scores[num] = min(1.0, scores[num] + boost)
                
        return scores
    
    def get_pair_matrix(self) -> Dict[Tuple[int, int], float]:
        """Trả về ma trận co-occurrence cho tất cả cặp số (focus gần đây)."""
        pair_counts = Counter()
        recent_draws = self.draws[-min(40, len(self.draws)):]  # Giảm xuống 40 kỳ
        for i, draw in enumerate(recent_draws):
            weight = 1.0 + (i / len(recent_draws))  # Recent weighted more
            nums = sorted(draw[:6])
            for pair in combinations(nums, 2):
                pair_counts[pair] += weight
        
        # Normalize
        max_c = max(pair_counts.values()) if pair_counts else 1
        return {pair: count / max_c for pair, count in pair_counts.items()}


# ═══════════════════════════════════════════════════
# 2. DEEP ENSEMBLE - Kết hợp nhiều mô hình AI
# ═══════════════════════════════════════════════════

class DeepEnsemble:
    """Kết hợp LSTM sâu + Transformer nâng cao để cho xác suất mỗi số."""
    
    def __init__(self, draws: List[List[int]], max_num: int = 45):
        self.draws = draws
        self.max_num = max_num
        self.look_back = min(20, len(draws) - 1)  # Cửa sổ lùi 20 kỳ
        
    def _prepare_binary_data(self) -> np.ndarray:
        """Chuyển draws thành binary vectors."""
        vectors = []
        for draw in self.draws:
            vec = np.zeros(self.max_num)
            for num in draw:
                if 1 <= num <= self.max_num:
                    vec[num - 1] = 1
            vectors.append(vec)
        return np.array(vectors)
    
    def _create_sequences(self, data: np.ndarray):
        """Tạo sequences cho time series."""
        X, y = [], []
        for i in range(len(data) - self.look_back):
            X.append(data[i:(i + self.look_back)])
            y.append(data[i + self.look_back])
        return np.array(X), np.array(y)
    
    def run_enhanced_lstm(self, epochs: int = 50) -> Optional[np.ndarray]:
        """LSTM nâng cao: Bi-directional + 3 tầng + Attention."""
        try:
            import tensorflow as tf
            from tensorflow.keras import layers, models, optimizers, callbacks
        except ImportError:
            print("   ⚠️ TensorFlow không khả dụng, bỏ qua LSTM.")
            return None
        
        print("   🧠 Training Enhanced Bi-LSTM (3 tầng + Attention)...")
        
        data = self._prepare_binary_data()
        X, y = self._create_sequences(data)
        
        if len(X) < 10:
            print("   ⚠️ Không đủ dữ liệu cho LSTM.")
            return None
        
        # Split
        split = max(1, len(X) - 50)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        # Enhanced LSTM Architecture
        inputs = layers.Input(shape=(self.look_back, self.max_num))
        
        # Bidirectional LSTM layer 1
        x = layers.Bidirectional(layers.LSTM(128, return_sequences=True))(inputs)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.2)(x)
        
        # Bidirectional LSTM layer 2
        x = layers.Bidirectional(layers.LSTM(64, return_sequences=True))(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.2)(x)
        
        # Self-attention mechanism
        attention = layers.MultiHeadAttention(num_heads=4, key_dim=32)(x, x)
        x = layers.Add()([x, attention])
        x = layers.LayerNormalization()(x)
        
        # LSTM layer 3  
        x = layers.LSTM(64)(x)
        x = layers.Dropout(0.3)(x)
        
        # Dense layers
        x = layers.Dense(128, activation='relu')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(64, activation='relu')(x)
        outputs = layers.Dense(self.max_num, activation='sigmoid')(x)
        
        model = models.Model(inputs=inputs, outputs=outputs)
        model.compile(
            loss='binary_crossentropy',
            optimizer=optimizers.Adam(learning_rate=0.001),
            metrics=['accuracy']
        )
        
        # Training with callbacks
        early_stop = callbacks.EarlyStopping(
            monitor='val_loss', patience=10, restore_best_weights=True, verbose=0
        )
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=5, verbose=0
        )
        
        model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=16,
            callbacks=[early_stop, reduce_lr],
            verbose=0
        )
        
        # Evaluate
        if len(X_test) > 0:
            preds = model.predict(X_test, verbose=0)
            avg_match = 0
            for i in range(len(preds)):
                top6 = np.argsort(preds[i])[-6:]
                actual = np.where(y_test[i] == 1)[0]
                avg_match += len(set(top6) & set(actual))
            avg_match /= len(preds)
            print(f"   📈 LSTM Test accuracy: {avg_match:.2f}/6 trùng khớp TB")
        
        # Predict next
        last_seq = data[-self.look_back:].reshape(1, self.look_back, self.max_num)
        probs = model.predict(last_seq, verbose=0)[0]
        
        return probs
    
    def run_deep_transformer(self, epochs: int = 50) -> Optional[np.ndarray]:
        """Transformer nâng cao với multiple attention layers."""
        try:
            import tensorflow as tf
            from tensorflow.keras import layers, models, optimizers, callbacks
        except ImportError:
            print("   ⚠️ TensorFlow không khả dụng, bỏ qua Transformer.")
            return None
        
        print("   🤖 Training Deep Transformer (3 blocks, 8 heads)...")
        
        data = self._prepare_binary_data()
        X, y = self._create_sequences(data)
        
        if len(X) < 10:
            return None
        
        split = max(1, len(X) - 50)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        # Transformer Architecture - 3 blocks
        inputs = layers.Input(shape=(self.look_back, self.max_num))
        
        # Positional encoding via dense projection
        x = layers.Dense(64)(inputs)
        
        # Transformer Block 1
        attn1 = layers.MultiHeadAttention(num_heads=8, key_dim=32)(x, x)
        attn1 = layers.Dropout(0.1)(attn1)
        x = layers.Add()([x, attn1])
        x = layers.LayerNormalization(epsilon=1e-6)(x)
        ff1 = layers.Dense(128, activation='gelu')(x)
        ff1 = layers.Dense(64)(ff1)
        ff1 = layers.Dropout(0.1)(ff1)
        x = layers.Add()([x, ff1])
        x = layers.LayerNormalization(epsilon=1e-6)(x)
        
        # Transformer Block 2
        attn2 = layers.MultiHeadAttention(num_heads=8, key_dim=32)(x, x)
        attn2 = layers.Dropout(0.1)(attn2)
        x = layers.Add()([x, attn2])
        x = layers.LayerNormalization(epsilon=1e-6)(x)
        ff2 = layers.Dense(128, activation='gelu')(x)
        ff2 = layers.Dense(64)(ff2)
        ff2 = layers.Dropout(0.1)(ff2)
        x = layers.Add()([x, ff2])
        x = layers.LayerNormalization(epsilon=1e-6)(x)
        
        # Transformer Block 3
        attn3 = layers.MultiHeadAttention(num_heads=4, key_dim=32)(x, x)
        attn3 = layers.Dropout(0.1)(attn3)
        x = layers.Add()([x, attn3])
        x = layers.LayerNormalization(epsilon=1e-6)(x)
        
        # Output
        x = layers.GlobalAveragePooling1D()(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(64, activation='relu')(x)
        outputs = layers.Dense(self.max_num, activation='sigmoid')(x)
        
        model = models.Model(inputs=inputs, outputs=outputs)
        model.compile(
            loss='binary_crossentropy',
            optimizer=optimizers.Adam(learning_rate=0.001),
            metrics=['accuracy']
        )
        
        early_stop = callbacks.EarlyStopping(
            monitor='val_loss', patience=10, restore_best_weights=True, verbose=0
        )
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=5, verbose=0
        )
        
        model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=16,
            callbacks=[early_stop, reduce_lr],
            verbose=0
        )
        
        # Evaluate
        if len(X_test) > 0:
            preds = model.predict(X_test, verbose=0)
            avg_match = 0
            for i in range(len(preds)):
                top6 = np.argsort(preds[i])[-6:]
                actual = np.where(y_test[i] == 1)[0]
                avg_match += len(set(top6) & set(actual))
            avg_match /= len(preds)
            print(f"   📈 Transformer Test accuracy: {avg_match:.2f}/6 trùng khớp TB")
        
        # Predict next
        last_seq = data[-self.look_back:].reshape(1, self.look_back, self.max_num)
        probs = model.predict(last_seq, verbose=0)[0]
        
        return probs
    
    def run_gru_model(self, epochs: int = 40) -> Optional[np.ndarray]:
        """GRU model - nhanh hơn LSTM, đôi khi tốt hơn."""
        try:
            import tensorflow as tf
            from tensorflow.keras import layers, models, optimizers, callbacks
        except ImportError:
            return None
        
        print("   ⚡ Training GRU Model (2 tầng)...")
        
        data = self._prepare_binary_data()
        X, y = self._create_sequences(data)
        
        if len(X) < 10:
            return None
        
        split = max(1, len(X) - 50)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        inputs = layers.Input(shape=(self.look_back, self.max_num))
        x = layers.GRU(128, return_sequences=True)(inputs)
        x = layers.Dropout(0.2)(x)
        x = layers.GRU(64)(x)
        x = layers.Dropout(0.2)(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        outputs = layers.Dense(self.max_num, activation='sigmoid')(x)
        
        model = models.Model(inputs=inputs, outputs=outputs)
        model.compile(loss='binary_crossentropy', optimizer='adam')
        
        early_stop = callbacks.EarlyStopping(
            monitor='val_loss', patience=8, restore_best_weights=True, verbose=0
        )
        
        model.fit(X_train, y_train, validation_data=(X_test, y_test),
                  epochs=epochs, batch_size=16, callbacks=[early_stop], verbose=0)
        
        last_seq = data[-self.look_back:].reshape(1, self.look_back, self.max_num)
        probs = model.predict(last_seq, verbose=0)[0]
        
        return probs
    
    def get_ensemble_probabilities(self) -> np.ndarray:
        """Chạy tất cả models và kết hợp xác suất."""
        print("\n" + "🔥" * 30)
        print("KHỞI ĐỘNG DEEP ENSEMBLE AI (3 Models)")
        print("🔥" * 30)
        
        all_probs = []
        weights = []
        
        # Model 1: Enhanced LSTM (trọng số cao nhất)
        lstm_probs = self.run_enhanced_lstm(epochs=50)
        if lstm_probs is not None:
            all_probs.append(lstm_probs)
            weights.append(0.40)
        
        # Model 2: Deep Transformer
        transformer_probs = self.run_deep_transformer(epochs=50)
        if transformer_probs is not None:
            all_probs.append(transformer_probs)
            weights.append(0.35)
        
        # Model 3: GRU
        gru_probs = self.run_gru_model(epochs=40)
        if gru_probs is not None:
            all_probs.append(gru_probs)
            weights.append(0.25)
        
        if not all_probs:
            print("   ❌ Không có model nào chạy được!")
            return np.ones(self.max_num) / self.max_num
        
        # Normalize weights
        total_w = sum(weights[:len(all_probs)])
        weights = [w / total_w for w in weights[:len(all_probs)]]
        
        # Weighted average
        ensemble = np.zeros(self.max_num)
        for probs, weight in zip(all_probs, weights):
            ensemble += weight * probs
        
        print(f"\n   ✅ Ensemble hoàn tất ({len(all_probs)} models)")
        top6 = np.argsort(ensemble)[-6:][::-1]
        top6_nums = sorted([i + 1 for i in top6])
        print(f"   🔮 Top 6 từ AI: {top6_nums}")
        
        return ensemble


# ═══════════════════════════════════════════════════
# 3. TICKET OPTIMIZER - Tối ưu hóa bộ vé
# ═══════════════════════════════════════════════════

class TicketOptimizer:
    """Tạo bộ vé tối ưu bằng chiến lược MULTI-ZONE v3.0."""
    
    def __init__(self, max_num: int = 45, draws: List[List[int]] = None):
        self.max_num = max_num
        self.draws = draws or []
        
        # Tính thống kê cho filters
        sums = [sum(d[:6]) for d in self.draws] if self.draws else []
        if sums:
            self.min_sum = np.percentile(sums, 5)
            self.max_sum = np.percentile(sums, 95)
            self.mean_sum = np.mean(sums)
        else:
            self.min_sum = 60
            self.max_sum = 200
            self.mean_sum = 130
    
    def _passes_filters(self, nums: List[int], strict: bool = True) -> bool:
        """Kiểm tra bộ số có hợp lệ theo các bộ lọc thống kê.
        strict=True: lọc nghiêm (cho core zone)
        strict=False: lọc nhẹ (cho extended/wild zone)
        """
        nums = sorted(nums)
        
        # Filter 1: Tổng trong khoảng hợp lý
        s = sum(nums)
        if strict:
            if not (self.min_sum <= s <= self.max_sum):
                return False
        else:
            # Relaxed: mở rộng 15%
            margin = (self.max_sum - self.min_sum) * 0.15
            if not (self.min_sum - margin <= s <= self.max_sum + margin):
                return False
        
        # Filter 2: Tỷ lệ chẵn/lẻ
        evens = sum(1 for n in nums if n % 2 == 0)
        if strict:
            if evens < 2 or evens > 4:
                return False
        else:
            if evens < 1 or evens > 5:
                return False
        
        # Filter 3: Không quá 2 số liên tiếp (VD: 1,2,3 là xấu)
        for i in range(len(nums) - 2):
            if nums[i+2] == nums[i+1] + 1 == nums[i] + 2:
                return False
        
        # Filter 4: Ít nhất 3 đuôi số khác nhau (relaxed from 4)
        last_digits = set(n % 10 for n in nums)
        min_digits = 4 if strict else 3
        if len(last_digits) < min_digits:
            return False
        
        # Filter 5: Trải đều qua các decade (ít nhất 3 decades)
        decades = set(n // 10 for n in nums)
        min_decades = 3 if strict else 2
        if len(decades) < min_decades:
            return False
        
        # Filter 6: Khoảng cách lớn nhất
        max_gap = max(nums[i+1] - nums[i] for i in range(len(nums) - 1))
        max_allowed = self.max_num * 0.55 if strict else self.max_num * 0.7
        if max_gap > max_allowed:
            return False
        
        return True
    
    def _score_ticket(self, ticket, combined_scores, pair_matrix) -> float:
        """Chấm điểm một bộ vé."""
        # Điểm 1: Tổng điểm individual
        individual_score = sum(combined_scores.get(n, 0) for n in ticket)
        
        # Điểm 2: Pair bonus
        pair_score = 0
        for pair in combinations(ticket, 2):
            pair_key = tuple(sorted(pair))
            pair_score += pair_matrix.get(pair_key, 0)
        
        # Điểm 3: Sum proximity
        sum_diff = abs(sum(ticket) - self.mean_sum)
        sum_score = np.exp(-sum_diff / 50)
        
        return (
            0.45 * individual_score / 6 +
            0.35 * pair_score / 15 +
            0.20 * sum_score
        )
    
    def generate_optimal_tickets(
        self,
        number_scores: Dict[int, float],
        ai_probs: np.ndarray,
        pair_matrix: Dict[Tuple[int, int], float],
        count: int = 18
    ) -> List[List[int]]:
        """
        CHIẾN LƯỢC HYBRID v4.0 = Ultra (Hot Zone) + RE (Weighted Random):
        
        Zone A (CORE - 8 số): 8 vé tập trung nhất → mục tiêu 4-6 số trúng
        Zone B (EXTENDED - 14 số): 4 vé phủ rộng hơn → mục tiêu 3-5 số trúng  
        Zone C (RE-RANDOM - TẤT CẢ số): 6 vé random có trọng số → bắt số bất ngờ
        
        Tổng: 18 vé tối ưu
        """
        print("\n" + "🏆" * 30)
        print("HYBRID OPTIMIZER v4.0 (Ultra + RE) - 18 VÉ")
        print("🏆" * 30)
        
        # BƯỚC 1: Kết hợp điểm statistical + AI
        combined_scores = {}
        for num in range(1, self.max_num + 1):
            stat_score = number_scores.get(num, 0)
            ai_score = ai_probs[num - 1] if num - 1 < len(ai_probs) else 0
            combined_scores[num] = 0.50 * stat_score + 0.50 * ai_score
        
        sorted_numbers = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        # BƯỚC 2: Tạo zones
        core_size = 8 if self.max_num <= 45 else 9
        ext_size = 14 if self.max_num <= 45 else 16
        
        core_zone = [num for num, _ in sorted_numbers[:core_size]]
        ext_zone = [num for num, _ in sorted_numbers[:ext_size]]
        
        print(f"\n   🔴 CORE ZONE  ({len(core_zone)} số): {sorted(core_zone)}")
        print(f"   🟡 EXT ZONE   ({len(ext_zone)} số): {sorted(ext_zone)}")
        print(f"   � RE-RANDOM  (TẤT CẢ {self.max_num} số, weighted sampling)")
        
        print(f"\n   📊 Điểm Top {ext_size} số:")
        for num, score in sorted_numbers[:ext_size]:
            zone = "🔴" if num in core_zone else "🟡"
            bar = "█" * int(score * 25)
            print(f"      {zone} Số {num:2d}: {score:.3f} {bar}")
        
        # BƯỚC 3: Tạo candidates cho mỗi zone
        print(f"\n   ⚙️ Đang tạo tổ hợp...")
        
        # Zone A: Core (brute force)
        core_candidates = list(combinations(core_zone, 6))
        core_scored = []
        for ticket in core_candidates:
            ticket = sorted(list(ticket))
            if self._passes_filters(ticket, strict=True):
                score = self._score_ticket(ticket, combined_scores, pair_matrix)
                core_scored.append((ticket, score))
        core_scored.sort(key=lambda x: x[1], reverse=True)
        
        # Zone B: Extended (brute force)
        ext_candidates = list(combinations(ext_zone, 6))
        ext_scored = []
        for ticket in ext_candidates:
            ticket = sorted(list(ticket))
            if self._passes_filters(ticket, strict=True):
                score = self._score_ticket(ticket, combined_scores, pair_matrix)
                ext_scored.append((ticket, score))
        core_set = set(tuple(t) for t, _ in core_scored)
        ext_scored = [(t, s) for t, s in ext_scored if tuple(t) not in core_set]
        ext_scored.sort(key=lambda x: x[1], reverse=True)
        
        # Zone C: RE-STYLE WEIGHTED RANDOM (Reverse Engineering approach)
        # Key: sample từ TẤT CẢ số, không giới hạn hot zone
        re_scored = self._generate_re_tickets(combined_scores, pair_matrix, n_tickets=200)
        # Loại trùng với core/ext
        ext_set = set(tuple(t) for t, _ in ext_scored)
        re_scored = [(t, s) for t, s in re_scored if tuple(t) not in core_set and tuple(t) not in ext_set]
        re_scored.sort(key=lambda x: x[1], reverse=True)
        
        print(f"   ✅ Core: {len(core_scored)} | Ext: {len(ext_scored)} | RE-Random: {len(re_scored)}")
        
        # BƯỚC 4: Phân bổ vé
        core_count = min(8, count * 8 // 18)   # ~44% cho core (tập trung)
        ext_count = min(4, count * 4 // 18)    # ~22% cho extended
        re_count = count - core_count - ext_count  # ~33% cho RE-random (nhiều hơn!)
        
        selected_core = self._select_with_coverage(core_scored, core_count)
        selected_ext = self._select_with_coverage(ext_scored, ext_count)
        selected_re = self._select_with_coverage(re_scored, re_count)
        
        all_selected = selected_core + selected_ext + selected_re
        
        # In kết quả
        print(f"\n   🎯 ĐÃ CHỌN {len(all_selected)} BỘ SỐ TỐI ƯU:")
        for i, ticket in enumerate(all_selected, 1):
            if i <= len(selected_core):
                zone_label = "🔴 CORE"
            elif i <= len(selected_core) + len(selected_ext):
                zone_label = "🟡 EXT "
            else:
                zone_label = "� RE  "
            score = self._score_ticket(ticket, combined_scores, pair_matrix)
            print(f"      {zone_label} {i:2d}. {ticket} (Σ={sum(ticket)}, Score={score:.4f})")
        
        # Thống kê coverage
        all_nums = set()
        for t in all_selected:
            all_nums.update(t)
        
        core_nums = set()
        for t in selected_core:
            core_nums.update(t)
        re_only_nums = all_nums - set(ext_zone)
        
        print(f"\n   📊 Phủ sóng: {len(all_nums)} số tổng cộng")
        print(f"   📊 Các số: {sorted(all_nums)}")
        if re_only_nums:
            print(f"   🟣 Số từ RE (ngoài hot zone): {sorted(re_only_nums)}")
        
        return all_selected
    
    def _generate_re_tickets(
        self,
        combined_scores: Dict[int, float],
        pair_matrix: Dict,
        n_tickets: int = 200
    ) -> List[Tuple[List[int], float]]:
        """
        Reverse Engineering style: Weighted random sampling từ TẤT CẢ số.
        Dùng combined_scores làm trọng số sampling.
        """
        # Tạo probability distribution từ scores
        all_nums = list(range(1, self.max_num + 1))
        raw_probs = np.array([combined_scores.get(n, 0) for n in all_nums])
        
        # Boost: nâng min prob lên để số ít điểm vẫn có cơ hội
        raw_probs = raw_probs + 0.05  # Floor probability
        probs = raw_probs / raw_probs.sum()
        
        scored_tickets = []
        seen = set()
        attempts = 0
        max_attempts = n_tickets * 50
        
        while len(scored_tickets) < n_tickets and attempts < max_attempts:
            attempts += 1
            try:
                ticket = sorted(np.random.choice(all_nums, size=6, replace=False, p=probs).tolist())
            except Exception:
                ticket = sorted(np.random.choice(all_nums, size=6, replace=False).tolist())
            
            ticket_key = tuple(ticket)
            if ticket_key in seen:
                continue
            seen.add(ticket_key)
            
            if not self._passes_filters(ticket, strict=False):
                continue
            
            score = self._score_ticket(ticket, combined_scores, pair_matrix)
            scored_tickets.append((ticket, score))
        
        return scored_tickets
    
    def _smart_sample_tickets(
        self,
        hot_zone: List[int],
        scores: Dict[int, float],
        pair_matrix: Dict,
        n_samples: int
    ) -> List[Tuple[int, ...]]:
        """Sampling thông minh dựa trên xác suất."""
        probs = np.array([scores.get(n, 0) for n in hot_zone])
        probs_sum = probs.sum()
        if probs_sum > 0:
            probs = probs / probs_sum
        else:
            probs = np.ones(len(hot_zone)) / len(hot_zone)
        
        candidates = set()
        for _ in range(n_samples):
            try:
                ticket = tuple(sorted(np.random.choice(hot_zone, size=6, replace=False, p=probs)))
                candidates.add(ticket)
            except Exception:
                ticket = tuple(sorted(np.random.choice(hot_zone, size=6, replace=False)))
                candidates.add(ticket)
        
        return list(candidates)
    
    def _select_with_coverage(
        self,
        scored_candidates: List[Tuple[List[int], float]],
        count: int
    ) -> List[List[int]]:
        """Chọn tickets sao cho maximize coverage + score."""
        if not scored_candidates:
            return []
        
        selected = []
        covered_pairs = set()
        covered_numbers = set()
        
        for _ in range(count):
            best_ticket = None
            best_value = -1
            
            # Scan top 500 candidates (mở rộng)
            for ticket, score in scored_candidates[:500]:
                if ticket in selected:
                    continue
                
                # Đếm số cặp MỚI mà ticket này thêm vào
                new_pairs = 0
                for pair in combinations(ticket, 2):
                    if pair not in covered_pairs:
                        new_pairs += 1
                
                # Đếm số MỚI
                new_nums = len(set(ticket) - covered_numbers)
                
                # Value = score * (1 + coverage_bonus)
                coverage_bonus = new_pairs / 15 + new_nums / 6
                value = score * (1 + 0.4 * coverage_bonus)
                
                if value > best_value:
                    best_value = value
                    best_ticket = ticket
            
            if best_ticket is not None:
                selected.append(best_ticket)
                for pair in combinations(best_ticket, 2):
                    covered_pairs.add(pair)
                covered_numbers.update(best_ticket)
            else:
                for ticket, score in scored_candidates:
                    if ticket not in selected:
                        selected.append(ticket)
                        break
        
        return selected


# ═══════════════════════════════════════════════════
# 4. MAIN ENTRY POINT
# ═══════════════════════════════════════════════════

def run_ultra_prediction(product_type: str = "power_645", use_ai: bool = True) -> Tuple[str, List[List[int]]]:
    """
    Chạy dự đoán ULTRA và trả về (report_string, tickets_list).
    
    Args:
        product_type: "power_645" hoặc "power_655"
        use_ai: True để dùng Deep Learning ensemble, False chỉ dùng thống kê
    
    Returns:
        (report: str, tickets: List[List[int]])
    """
    import io
    from contextlib import redirect_stdout
    
    max_num = 55 if "655" in product_type else 45
    filename = "power655.jsonl" if "655" in product_type else "power645.jsonl"
    prod_name = "POWER 6/55" if "655" in product_type else "MEGA 6/45"
    
    # Locate data file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    paths_to_try = [
        os.path.join(os.getcwd(), 'data', filename),
        os.path.join(base_dir, '..', '..', '..', 'data', filename),
        os.path.join(base_dir, 'data', filename)
    ]
    
    target_file = None
    for p in paths_to_try:
        if os.path.exists(p):
            target_file = p
            break
    
    f = io.StringIO()
    tickets = []
    
    with redirect_stdout(f):
        if not target_file:
            print(f"❌ Không tìm thấy file dữ liệu: {filename}")
            return f.getvalue(), []
        
        print("=" * 60)
        print(f"🏆 ULTRA PREDICTOR v2.0 - {prod_name}")
        print(f"📅 Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        # 1. Load data
        print(f"\n📂 Loading data từ {filename}...")
        draws = []
        with open(target_file, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    data = json.loads(line)
                    if 'result' in data:
                        nums = sorted([int(n) for n in data['result']])[:6]
                        draws.append(nums)
                except Exception:
                    continue
        
        # Sort by draw order (file is already ordered)
        print(f"   ✅ Loaded {len(draws)} kỳ quay")
        
        # Show latest 5 draws
        print(f"\n   📋 5 kỳ gần nhất:")
        for i, draw in enumerate(draws[-5:], 1):
            print(f"      {i}. {draw} (Tổng: {sum(draw)})")
        
        # 2. Number Scoring (Statistical Analysis)
        print("\n" + "📊" * 30)
        print("PHÂN TÍCH THỐNG KÊ ĐA TÍN HIỆU")
        print("📊" * 30)
        
        scorer = NumberScorer(draws, max_num)
        number_scores = scorer.compute_all_signals()
        pair_matrix = scorer.get_pair_matrix()
        
        # Show top 20 numbers by statistical score
        sorted_by_stat = sorted(number_scores.items(), key=lambda x: x[1], reverse=True)
        print(f"\n   🔝 TOP 20 số có điểm thống kê cao nhất:")
        for num, score in sorted_by_stat[:20]:
            bar = "█" * int(score * 25)
            print(f"      Số {num:2d}: {score:.3f} {bar}")
        
        # 3. AI Ensemble (if enabled)
        if use_ai:
            ensemble = DeepEnsemble(draws, max_num)
            ai_probs = ensemble.get_ensemble_probabilities()
        else:
            print("\n   ⚡ Chế độ nhanh: Chỉ dùng thống kê (không AI)")
            ai_probs = np.array([number_scores.get(i+1, 0) for i in range(max_num)])
        
        # 4. Ticket Optimization
        optimizer = TicketOptimizer(max_num, draws)
        tickets = optimizer.generate_optimal_tickets(
            number_scores, ai_probs, pair_matrix, count=18
        )
        
        # 5. Summary
        print("\n" + "=" * 60)
        print("🎯 KẾT QUẢ DỰ ĐOÁN HYBRID v4.0 (Ultra + RE)")
        print("=" * 60)
        
        for i, ticket in enumerate(tickets, 1):
            print(f"   Vé {i:2d}: {' '.join([f'{n:02d}' for n in ticket])} (Tổng: {sum(ticket)})")
        
        print(f"\n💡 LƯU Ý:")
        print(f"   - Hybrid: {len(set(n for t in tickets for n in t))} số phủ sóng")
        print(f"   - Sử dụng {3 if use_ai else 0} mô hình AI + 8 tín hiệu thống kê")
        cs = 8 if max_num <= 45 else 9
        es = 14 if max_num <= 45 else 16
        print(f"   - Chiến lược: Core({cs}) + Extended({es}) + RE-Random(ALL)")
        print(f"   - RE-Random: sampling từ TẤT CẢ {max_num} số với trọng số thông minh")
        print(f"   - Tối ưu hóa coverage giữa {len(tickets)} vé")
        print("=" * 60)
    
    return f.getvalue(), tickets


# Direct run
if __name__ == "__main__":
    import sys
    product = "power_645"
    if len(sys.argv) > 1:
        product = sys.argv[1]
    
    report, tickets = run_ultra_prediction(product, use_ai=True)
    print(report)
