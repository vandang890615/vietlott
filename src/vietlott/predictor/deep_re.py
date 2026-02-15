#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEEP REVERSE ENGINEERING v2.0 - TÌM QUY LUẬT ẨN
=================================================
Phân tích thống kê chuyên sâu để phát hiện:
1. Machine Bias (số bị thiên lệch)
2. Position Bias (thiên vị vị trí)
3. Autocorrelation (tương quan giữa các kỳ)  
4. Cycle Detection (chu kỳ ẩn)
5. Gap Analysis (khoảng cách xuất hiện)
6. Pair Correlation (cặp số hay đi cùng)
7. Sum/Modular Patterns (quy luật tổng/dư)
8. Day-of-week Bias (thiên vị theo ngày)
9. Hot/Cold Streaks (chuỗi nóng/lạnh)
10. Transition Matrix (ma trận chuyển tiếp)
"""

import numpy as np
import json
import os
import sys
from collections import Counter, defaultdict
from itertools import combinations
from datetime import datetime
from scipy import stats

def load_draws(filepath):
    """Load draws from jsonl file."""
    draws = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if 'result' in data:
                    nums = sorted([int(n) for n in data['result']])[:6]
                    draws.append({
                        'numbers': nums,
                        'id': data.get('id', ''),
                        'date': data.get('date', ''),
                    })
            except:
                continue
    return draws


def analyze_frequency_bias(draws, max_num, prod_name):
    """Test 1: Chi-squared test - số nào xuất hiện nhiều/ít hơn kỳ vọng?"""
    print(f"\n{'='*70}")
    print(f"🔬 TEST 1: FREQUENCY BIAS (Chi-squared) - {prod_name}")
    print(f"{'='*70}")
    
    freq = Counter()
    for d in draws:
        freq.update(d['numbers'])
    
    total_drawn = sum(freq.values())
    expected = total_drawn / max_num
    
    # Chi-squared test
    observed = [freq.get(i, 0) for i in range(1, max_num + 1)]
    chi2, p_value = stats.chisquare(observed)
    
    print(f"  📊 Tổng số lần quay: {len(draws)}")
    print(f"  📊 Kỳ vọng mỗi số: {expected:.1f} lần")
    print(f"  📊 Chi-squared: {chi2:.2f}, p-value: {p_value:.6f}")
    
    if p_value < 0.05:
        print(f"  ⚠️  KẾT QUẢ: CÓ THIÊN LỆCH THỐNG KÊ (p < 0.05)")
        print(f"       → Phân bố KHÔNG đều - có thể có bias!")
    elif p_value < 0.10:
        print(f"  🟡 KẾT QUẢ: GẦN THIÊN LỆCH (0.05 < p < 0.10)")
    else:
        print(f"  ✅ KẾT QUẢ: Phân bố đồng đều (p = {p_value:.4f})")
    
    # Top số xuất hiện nhiều/ít nhất
    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n  🔥 TOP 10 số xuất hiện NHIỀU nhất:")
    for num, count in sorted_freq[:10]:
        deviation = (count - expected) / expected * 100
        bar = "█" * int(count / expected * 15)
        print(f"      Số {num:2d}: {count:4d} lần ({deviation:+.1f}% vs kỳ vọng) {bar}")
    
    print(f"\n  ❄️  TOP 10 số xuất hiện ÍT nhất:")
    for num, count in sorted_freq[-10:]:
        deviation = (count - expected) / expected * 100
        print(f"      Số {num:2d}: {count:4d} lần ({deviation:+.1f}% vs kỳ vọng)")
    
    # Anomaly detection: số nào lệch > 2 sigma?
    std_freq = np.std(observed)
    mean_freq = np.mean(observed)
    anomalies = []
    for num in range(1, max_num + 1):
        z_score = (freq.get(num, 0) - mean_freq) / std_freq
        if abs(z_score) > 2:
            anomalies.append((num, freq.get(num, 0), z_score))
    
    if anomalies:
        print(f"\n  🚨 SỐ BẤT THƯỜNG (|z| > 2 sigma):")
        for num, count, z in sorted(anomalies, key=lambda x: abs(x[2]), reverse=True):
            label = "NÓNG" if z > 0 else "LẠNH"
            print(f"      Số {num:2d}: z={z:+.2f} ({label}) - {count} lần")
    
    return freq, anomalies


def analyze_position_bias(draws, max_num, prod_name):
    """Test 2: Position Bias - số nào thường xuất hiện ở vị trí nào?"""
    print(f"\n{'='*70}")
    print(f"🔬 TEST 2: POSITION BIAS - {prod_name}")
    print(f"{'='*70}")
    
    pos_freq = defaultdict(lambda: Counter())
    for d in draws:
        sorted_nums = sorted(d['numbers'])
        for pos, num in enumerate(sorted_nums):
            pos_freq[pos][num] += 1
    
    print(f"  📊 Phân tích thiên vị vị trí (số được sắp xếp tăng dần):")
    
    biased_positions = []
    for pos in range(6):
        counts = pos_freq[pos]
        top3 = counts.most_common(3)
        total = sum(counts.values())
        expected_per_num = total / max_num
        
        # Chi-squared for this position
        observed = [counts.get(i, 0) for i in range(1, max_num + 1)]
        chi2, p_val = stats.chisquare(observed)
        
        print(f"\n    Vị trí {pos+1} (nhỏ→lớn):")
        print(f"      Chi2={chi2:.1f}, p={p_val:.4f}", end="")
        if p_val < 0.01:
            print(" ⚠️ CÓ BIAS MẠNH!")
            biased_positions.append(pos)
        elif p_val < 0.05:
            print(" 🟡 Có bias nhẹ")
        else:
            print(" ✅ OK")
        
        for num, cnt in top3:
            pct = cnt / total * 100
            print(f"      → Số {num:2d} chiếm {pct:.1f}% ({cnt}/{total})")
    
    return biased_positions


def analyze_autocorrelation(draws, max_num, prod_name):
    """Test 3: Autocorrelation - kỳ sau có liên quan kỳ trước?"""
    print(f"\n{'='*70}")
    print(f"🔬 TEST 3: AUTOCORRELATION (Tương quan giữa các kỳ) - {prod_name}")
    print(f"{'='*70}")
    
    # Chuyển thành binary vectors
    vectors = []
    for d in draws:
        vec = np.zeros(max_num)
        for n in d['numbers']:
            vec[n-1] = 1
        vectors.append(vec)
    
    vectors = np.array(vectors)
    
    # Test autocorrelation ở các lag khác nhau
    print(f"  📊 Tương quan giữa kỳ t và kỳ t+lag:")
    
    significant_lags = []
    for lag in range(1, 21):
        if lag >= len(vectors):
            break
        correlations = []
        for num_idx in range(max_num):
            series = vectors[:, num_idx]
            corr = np.corrcoef(series[:-lag], series[lag:])[0, 1]
            if not np.isnan(corr):
                correlations.append(corr)
        
        avg_corr = np.mean(correlations) if correlations else 0
        max_corr = max(correlations) if correlations else 0
        
        emoji = "🔴" if abs(avg_corr) > 0.05 else ("🟡" if abs(avg_corr) > 0.02 else "⬜")
        bar = "█" * int(abs(avg_corr) * 200)
        print(f"    Lag {lag:2d}: avg_corr={avg_corr:+.4f} max_corr={max_corr:+.4f} {emoji} {bar}")
        
        if abs(avg_corr) > 0.03:
            significant_lags.append((lag, avg_corr))
    
    if significant_lags:
        print(f"\n  🚨 LAG CÓ TƯƠNG QUAN:")
        for lag, corr in significant_lags:
            direction = "CÙNG CHIỀU" if corr > 0 else "NGƯỢC CHIỀU"
            print(f"      Lag {lag}: r={corr:+.4f} ({direction})")
            if corr > 0:
                print(f"      → Số xuất hiện kỳ trước có xu hướng xuất hiện lại sau {lag} kỳ!")
            else:
                print(f"      → Số xuất hiện kỳ trước ÍT xuất hiện sau {lag} kỳ!")
    else:
        print(f"\n  ✅ Không tìm thấy autocorrelation đáng kể")
    
    return significant_lags


def analyze_gap_patterns(draws, max_num, prod_name):
    """Test 4: Gap Analysis - khoảng cách xuất hiện có chu kỳ không?"""
    print(f"\n{'='*70}")
    print(f"🔬 TEST 4: GAP ANALYSIS (Chu kỳ xuất hiện) - {prod_name}")
    print(f"{'='*70}")
    
    # Tính gap cho mỗi số
    gaps = defaultdict(list)
    last_seen = {}
    
    for i, d in enumerate(draws):
        for num in d['numbers']:
            if num in last_seen:
                gap = i - last_seen[num]
                gaps[num].append(gap)
            last_seen[num] = i
    
    # Phân tích gap distribution
    print(f"\n  📊 Thống kê khoảng cách (gap) giữa các lần xuất hiện:")
    
    all_gaps = []
    gap_stats = {}
    for num in range(1, max_num + 1):
        if gaps[num]:
            mean_gap = np.mean(gaps[num])
            std_gap = np.std(gaps[num])
            max_gap = max(gaps[num])
            min_gap = min(gaps[num])
            all_gaps.extend(gaps[num])
            gap_stats[num] = {
                'mean': mean_gap, 'std': std_gap, 
                'max': max_gap, 'min': min_gap,
                'cv': std_gap / mean_gap if mean_gap > 0 else 0  # coefficient of variation
            }
    
    # Tìm số có khoảng cách đều đặn nhất (CV thấp nhất)
    sorted_by_regularity = sorted(gap_stats.items(), key=lambda x: x[1]['cv'])
    
    print(f"\n  ⏰ TOP 10 số có CHU KỲ ĐỀU ĐẶN nhất (Coefficient of Variation thấp nhất):")
    for num, st in sorted_by_regularity[:10]:
        print(f"      Số {num:2d}: Mean gap={st['mean']:.1f}, Std={st['std']:.1f}, CV={st['cv']:.3f} ({'Rất đều!' if st['cv'] < 0.4 else 'Tương đối đều' if st['cv'] < 0.6 else 'Khá ngẫu nhiên'})")
    
    # Tìm số "quá hạn" - gap hiện tại > mean + 1.5*std
    print(f"\n  🔥 SỐ 'QUÁ HẠN' (chưa xuất hiện lâu bất thường):")
    overdue = []
    current_gap = {}
    for num in range(1, max_num + 1):
        if num in last_seen:
            current_gap[num] = len(draws) - 1 - last_seen[num]
    
    for num, cg in current_gap.items():
        if num in gap_stats:
            st = gap_stats[num]
            z = (cg - st['mean']) / st['std'] if st['std'] > 0 else 0
            if z > 1.5:
                overdue.append((num, cg, st['mean'], z))
    
    overdue.sort(key=lambda x: x[3], reverse=True)
    for num, cg, mean_g, z in overdue[:10]:
        print(f"      Số {num:2d}: Đã {cg} kỳ chưa xuất hiện (Mean={mean_g:.1f}, z={z:.1f}σ)")
    
    if not overdue:
        print("      Không có số quá hạn đáng kể")
    
    return gap_stats, overdue


def analyze_pair_correlation(draws, max_num, prod_name):
    """Test 5: Pair Correlation - cặp số nào hay đi cùng?"""
    print(f"\n{'='*70}")
    print(f"🔬 TEST 5: PAIR CORRELATION - {prod_name}")
    print(f"{'='*70}")
    
    pair_count = Counter()
    freq = Counter()
    n_draws = len(draws)
    
    for d in draws:
        nums = d['numbers']
        freq.update(nums)
        for pair in combinations(nums, 2):
            pair_count[tuple(sorted(pair))] += 1
    
    # Tính expected pair frequency
    # P(A and B) expected = P(A) * P(B) * adjustment
    # For 6/max_num: P(pair) = C(max_num-2, 4) / C(max_num, 6)
    
    significant_pairs = []
    for pair, count in pair_count.items():
        a, b = pair
        # Expected co-occurrence under independence
        p_a = freq[a] / n_draws
        p_b = freq[b] / n_draws
        expected = p_a * p_b * n_draws * (6*5) / (max_num * (max_num-1)) * max_num * (max_num-1) / (6*5)
        # Simpler: expected = n_draws * C(max_num-2, 4) / C(max_num, 6)
        expected_simple = n_draws * 6 * 5 / (max_num * (max_num - 1))
        
        if expected_simple > 0:
            ratio = count / expected_simple
            if ratio > 1.8 or ratio < 0.3:
                significant_pairs.append((pair, count, expected_simple, ratio))
    
    # Top pairs
    top_pairs = pair_count.most_common(15)
    print(f"\n  🔗 TOP 15 cặp số HAY ĐI CÙNG nhất:")
    for pair, count in top_pairs:
        expected_simple = n_draws * 6 * 5 / (max_num * (max_num - 1))
        ratio = count / expected_simple
        bar = "█" * int(ratio * 10)
        emoji = "🔴" if ratio > 1.5 else ("🟡" if ratio > 1.2 else "⬜")
        print(f"      ({pair[0]:2d}, {pair[1]:2d}): {count:3d} lần (×{ratio:.2f} vs kỳ vọng) {emoji} {bar}")
    
    if significant_pairs:
        print(f"\n  🚨 CẶP SỐ BẤT THƯỜNG (ratio > 1.8x hoặc < 0.3x):")
        significant_pairs.sort(key=lambda x: x[3], reverse=True)
        for pair, count, exp, ratio in significant_pairs[:10]:
            label = "HAY ĐI CÙNG" if ratio > 1 else "HIẾM ĐI CÙNG"
            print(f"      ({pair[0]:2d}, {pair[1]:2d}): {count} lần vs kỳ vọng {exp:.1f} (×{ratio:.2f}) → {label}")
    
    return significant_pairs


def analyze_sum_patterns(draws, max_num, prod_name):
    """Test 6: Sum & Modular Patterns"""
    print(f"\n{'='*70}")
    print(f"🔬 TEST 6: SUM & MODULAR PATTERNS - {prod_name}")
    print(f"{'='*70}")
    
    sums = [sum(d['numbers']) for d in draws]
    
    print(f"\n  📊 Thống kê tổng:")
    print(f"      Mean: {np.mean(sums):.1f}")
    print(f"      Std: {np.std(sums):.1f}")
    print(f"      Min: {min(sums)}, Max: {max(sums)}")
    print(f"      P25: {np.percentile(sums, 25):.0f}, P50: {np.percentile(sums, 50):.0f}, P75: {np.percentile(sums, 75):.0f}")
    
    # Test normality
    _, p_norm = stats.normaltest(sums)
    print(f"      Normality test p-value: {p_norm:.6f} ({'Phân bố chuẩn ✅' if p_norm > 0.05 else 'KHÔNG phân bố chuẩn ⚠️'})")
    
    # Sum mod patterns
    print(f"\n  🔢 Phân tích SUM mod N:")
    for mod in [3, 5, 7, 10]:
        remainders = [s % mod for s in sums]
        dist = Counter(remainders)
        expected = len(sums) / mod
        chi2, p = stats.chisquare([dist.get(i, 0) for i in range(mod)])
        
        emoji = "⚠️ BIAS!" if p < 0.05 else "✅ OK"
        print(f"      Sum mod {mod}: chi2={chi2:.1f}, p={p:.4f} {emoji}")
        if p < 0.05:
            most_common = dist.most_common(1)[0]
            print(f"         → Dư {most_common[0]} xuất hiện {most_common[1]} lần ({most_common[1]/len(sums)*100:.1f}%)")
    
    # Consecutive sum trends
    print(f"\n  📈 Trend tổng liên tiếp:")
    sum_diffs = [sums[i+1] - sums[i] for i in range(len(sums)-1)]
    up_count = sum(1 for d in sum_diffs if d > 0)
    down_count = sum(1 for d in sum_diffs if d < 0)
    equal_count = sum(1 for d in sum_diffs if d == 0)
    
    print(f"      Tăng: {up_count} ({up_count/len(sum_diffs)*100:.1f}%)")
    print(f"      Giảm: {down_count} ({down_count/len(sum_diffs)*100:.1f}%)")
    print(f"      Bằng: {equal_count} ({equal_count/len(sum_diffs)*100:.1f}%)")
    
    return sums


def analyze_day_of_week(draws, prod_name):
    """Test 7: Day-of-week bias"""
    print(f"\n{'='*70}")
    print(f"🔬 TEST 7: DAY-OF-WEEK BIAS - {prod_name}")
    print(f"{'='*70}")
    
    day_freq = defaultdict(lambda: Counter())
    day_count = Counter()
    day_names = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
    
    for d in draws:
        try:
            date = datetime.strptime(d['date'], '%Y-%m-%d')
            dow = date.weekday()
            day_count[dow] += 1
            day_freq[dow].update(d['numbers'])
        except:
            continue
    
    if not day_count:
        print("  ❌ Không thể phân tích ngày (thiếu dữ liệu date)")
        return
    
    print(f"\n  📅 Phân bố quay theo ngày:")
    for dow in range(7):
        count = day_count.get(dow, 0)
        if count > 0:
            print(f"      {day_names[dow]}: {count} kỳ")
    
    # Tìm số nào hay ra vào ngày nào
    print(f"\n  📊 Số hay xuất hiện theo ngày (top 3 mỗi ngày):")
    for dow in sorted(day_count.keys()):
        if day_count[dow] >= 10:  # Cần ít nhất 10 kỳ
            top3 = day_freq[dow].most_common(3)
            total = sum(day_freq[dow].values())
            top_str = ", ".join([f"Số {n}({c})" for n, c in top3])
            print(f"      {day_names[dow]}: {top_str}")


def analyze_transition_matrix(draws, max_num, prod_name):
    """Test 8: Transition patterns - sau số X thường ra số gì?"""
    print(f"\n{'='*70}")
    print(f"🔬 TEST 8: TRANSITION PATTERNS - {prod_name}")
    print(f"{'='*70}")
    
    # Track: nếu số X xuất hiện kỳ này, số nào hay xuất hiện kỳ sau?
    transitions = defaultdict(Counter)
    
    for i in range(len(draws) - 1):
        current = draws[i]['numbers']
        next_draw = draws[i + 1]['numbers']
        for num in current:
            transitions[num].update(next_draw)
    
    print(f"\n  📊 Sau số X, số nào hay xuất hiện nhất?")
    
    strong_transitions = []
    for num in range(1, max_num + 1):
        if transitions[num]:
            total = sum(transitions[num].values())
            top = transitions[num].most_common(3)
            expected_per = total / max_num
            
            for next_num, count in top:
                ratio = count / expected_per if expected_per > 0 else 0
                if ratio > 1.5:
                    strong_transitions.append((num, next_num, count, expected_per, ratio))
    
    strong_transitions.sort(key=lambda x: x[4], reverse=True)
    
    print(f"\n  🔗 TOP 15 transition MẠNH nhất (ratio > 1.5x):")
    for num, next_num, count, exp, ratio in strong_transitions[:15]:
        print(f"      Số {num:2d} → Số {next_num:2d}: {count} lần (×{ratio:.2f} vs kỳ vọng)")
    
    return strong_transitions


def analyze_hot_cold_streaks(draws, max_num, prod_name):
    """Test 9: Hot/Cold streaks - chuỗi nóng lạnh"""
    print(f"\n{'='*70}")
    print(f"🔬 TEST 9: HOT/COLD STREAKS - {prod_name}")
    print(f"{'='*70}")
    
    # Tính max streak (xuất hiện liên tiếp) cho mỗi số
    max_hot = {}  # max consecutive appearances
    max_cold = {}  # max consecutive absences
    
    for num in range(1, max_num + 1):
        hot_streak = 0
        cold_streak = 0
        max_h = 0
        max_c = 0
        
        for d in draws:
            if num in d['numbers']:
                hot_streak += 1
                if cold_streak > max_c:
                    max_c = cold_streak
                cold_streak = 0
            else:
                cold_streak += 1
                if hot_streak > max_h:
                    max_h = hot_streak
                hot_streak = 0
        
        max_h = max(max_h, hot_streak)
        max_c = max(max_c, cold_streak)
        max_hot[num] = max_h
        max_cold[num] = max_c
    
    # Top hot streaks
    sorted_hot = sorted(max_hot.items(), key=lambda x: x[1], reverse=True)
    print(f"\n  🔥 TOP 10 chuỗi NÓNG dài nhất (xuất hiện liên tiếp):")
    for num, streak in sorted_hot[:10]:
        bar = "█" * streak
        print(f"      Số {num:2d}: {streak} kỳ liên tiếp {bar}")
    
    # Top cold streaks
    sorted_cold = sorted(max_cold.items(), key=lambda x: x[1], reverse=True)
    print(f"\n  ❄️  TOP 10 chuỗi LẠNH dài nhất (vắng mặt liên tiếp):")
    for num, streak in sorted_cold[:10]:
        print(f"      Số {num:2d}: {streak} kỳ vắng mặt")
    
    # Current streaks (for prediction)
    print(f"\n  🎯 STREAK HIỆN TẠI (dùng cho dự đoán):")
    current_hot = {}
    current_cold = {}
    
    for num in range(1, max_num + 1):
        streak = 0
        for d in reversed(draws):
            if num in d['numbers']:
                streak += 1
            else:
                break
        current_hot[num] = streak
        
        streak = 0
        for d in reversed(draws):
            if num not in d['numbers']:
                streak += 1
            else:
                break
        current_cold[num] = streak
    
    hot_now = [(n, s) for n, s in current_hot.items() if s >= 2]
    hot_now.sort(key=lambda x: x[1], reverse=True)
    if hot_now:
        print(f"    🔥 Đang NÓNG (xuất hiện ≥2 kỳ liên tiếp):")
        for num, streak in hot_now:
            print(f"        Số {num:2d}: {streak} kỳ liên tiếp")
    
    cold_now = [(n, s) for n, s in current_cold.items() if s >= 15]
    cold_now.sort(key=lambda x: x[1], reverse=True)
    if cold_now:
        print(f"    ❄️  Đang LẠNH (vắng mặt ≥15 kỳ):")
        for num, streak in cold_now[:10]:
            print(f"        Số {num:2d}: {streak} kỳ vắng mặt")
    
    return current_hot, current_cold


def analyze_even_odd_pattern(draws, prod_name):
    """Test 10: Even/Odd & High/Low patterns"""
    print(f"\n{'='*70}")
    print(f"🔬 TEST 10: EVEN/ODD & HIGH/LOW PATTERNS - {prod_name}")
    print(f"{'='*70}")
    
    even_counts = []
    high_counts = []
    max_num = max(max(d['numbers']) for d in draws)
    mid = max_num // 2
    
    for d in draws:
        evens = sum(1 for n in d['numbers'] if n % 2 == 0)
        highs = sum(1 for n in d['numbers'] if n > mid)
        even_counts.append(evens)
        high_counts.append(highs)
    
    # Even/Odd distribution
    even_dist = Counter(even_counts)
    print(f"\n  📊 Phân bố Chẵn/Lẻ:")
    for ec in range(7):
        count = even_dist.get(ec, 0)
        pct = count / len(draws) * 100
        bar = "█" * int(pct / 2)
        print(f"      {ec}C/{6-ec}L: {count:4d} ({pct:5.1f}%) {bar}")
    
    # Consecutive even/odd patterns
    print(f"\n  📈 Xu hướng chẵn/lẻ liên tiếp:")
    same_count = 0
    for i in range(1, len(even_counts)):
        if even_counts[i] == even_counts[i-1]:
            same_count += 1
    pct_same = same_count / (len(even_counts) - 1) * 100
    print(f"      Tỷ lệ giữ nguyên chẵn/lẻ: {pct_same:.1f}%")
    
    # High/Low distribution
    high_dist = Counter(high_counts)
    print(f"\n  📊 Phân bố Cao/Thấp (>{mid}):")
    for hc in range(7):
        count = high_dist.get(hc, 0)
        pct = count / len(draws) * 100
        bar = "█" * int(pct / 2)
        print(f"      {hc}C/{6-hc}T: {count:4d} ({pct:5.1f}%) {bar}")


def generate_prediction_from_patterns(freq_anomalies, gap_overdue, transitions, 
                                       current_hot, current_cold, max_num, prod_name):
    """Tổng hợp tất cả patterns thành dự đoán."""
    print(f"\n{'='*70}")
    print(f"🎯 TỔNG HỢP DỰ ĐOÁN TỪ REVERSE ENGINEERING - {prod_name}")
    print(f"{'='*70}")
    
    scores = defaultdict(float)
    reasons = defaultdict(list)
    
    # 1. Frequency anomalies (hot numbers)
    for num, count, z in freq_anomalies:
        if z > 0:  # Hot numbers
            scores[num] += z * 0.3
            reasons[num].append(f"Freq anomaly z={z:.1f}")
    
    # 2. Overdue numbers (gap analysis)
    for num, cg, mean_g, z in gap_overdue:
        scores[num] += z * 0.25
        reasons[num].append(f"Overdue {cg} kỳ (z={z:.1f})")
    
    # 3. Current hot streaks
    for num, streak in current_hot.items():
        if streak >= 2:
            scores[num] += streak * 0.5
            reasons[num].append(f"Hot streak {streak}")
    
    # 4. Current cold (contrarian - might be due)
    for num, streak in current_cold.items():
        if streak >= 12:
            scores[num] += (streak - 10) * 0.1
            reasons[num].append(f"Cold {streak} kỳ (due?)")
    
    # 5. Strong transitions from last draw
    for num, next_num, count, exp, ratio in transitions[:30]:
        scores[next_num] += (ratio - 1) * 0.2
        reasons[next_num].append(f"Transition từ {num} (×{ratio:.1f})")
    
    # Sort and display
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n  🏆 TOP 20 số được RE khuyên chọn:")
    for num, score in sorted_scores[:20]:
        reason_str = " | ".join(reasons[num][:3])
        bar = "█" * int(score * 5)
        print(f"      Số {num:2d}: Score={score:.2f} {bar}")
        print(f"            Lý do: {reason_str}")
    
    return sorted_scores


def main():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  🔬 DEEP REVERSE ENGINEERING v2.0 - TÌM QUY LUẬT ẨN    ║")
    print("║  Phân tích 10 yếu tố thống kê chuyên sâu               ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"  📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for product_type in ["power_645", "power_655"]:
        max_num = 55 if "655" in product_type else 45
        filename = "power655.jsonl" if "655" in product_type else "power645.jsonl"
        prod_name = "POWER 6/55" if "655" in product_type else "MEGA 6/45"
        
        filepath = os.path.join(os.getcwd(), 'data', filename)
        if not os.path.exists(filepath):
            filepath = os.path.join(base_dir, '..', '..', '..', 'data', filename)
        
        if not os.path.exists(filepath):
            print(f"❌ Không tìm thấy {filename}")
            continue
        
        draws = load_draws(filepath)
        
        print(f"\n\n{'#'*70}")
        print(f"### REVERSE ENGINEERING: {prod_name} ({len(draws)} kỳ) ###")
        print(f"{'#'*70}")
        
        # Run all tests
        freq, anomalies = analyze_frequency_bias(draws, max_num, prod_name)
        analyze_position_bias(draws, max_num, prod_name)
        autocorr = analyze_autocorrelation(draws, max_num, prod_name)
        gap_stats, overdue = analyze_gap_patterns(draws, max_num, prod_name)
        pairs = analyze_pair_correlation(draws, max_num, prod_name)
        analyze_sum_patterns(draws, max_num, prod_name)
        analyze_day_of_week(draws, prod_name)
        transitions = analyze_transition_matrix(draws, max_num, prod_name)
        current_hot, current_cold = analyze_hot_cold_streaks(draws, max_num, prod_name)
        analyze_even_odd_pattern(draws, prod_name)
        
        # Synthesize predictions
        generate_prediction_from_patterns(
            anomalies, overdue, transitions,
            current_hot, current_cold, max_num, prod_name
        )
    
    print(f"\n\n{'='*70}")
    print("✅ HOÀN TẤT REVERSE ENGINEERING!")
    print("💡 Dùng kết quả trên để tinh chỉnh thuật toán Ultra Predictor")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
