#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTEST ULTRA PREDICTOR v3.0 - MULTI-ZONE
===========================================
50 kỳ × 18 vé = 900 vé mỗi sản phẩm

Nâng cấp:
- 50 kỳ thay vì 20 → thống kê đáng tin cậy hơn
- 18 vé/kỳ thay vì 10 → phủ sóng rộng hơn
- Multi-Zone strategy → Core + Extended + Wild
"""

import numpy as np
import json
import os
import sys
from datetime import datetime
from collections import Counter
from itertools import combinations
from typing import List, Dict, Tuple

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.dirname(__file__))

from ultra_predictor import NumberScorer, TicketOptimizer


def load_draws(filepath: str) -> List[dict]:
    """Load draws from jsonl file."""
    draws = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if 'result' in data:
                    nums = sorted([int(n) for n in data['result']])
                    draws.append({
                        'numbers': nums[:6],
                        'all_numbers': nums,
                        'id': data.get('id', ''),
                        'date': data.get('date', ''),
                    })
            except:
                continue
    return draws


def predict_for_draw(draws_before: List[List[int]], max_num: int, num_tickets: int = 18) -> List[List[int]]:
    """
    Dự đoán cho kỳ tiếp theo dựa trên dữ liệu lịch sử.
    Chỉ dùng thống kê (không AI) để backtest nhanh.
    """
    if len(draws_before) < 30:
        return []

    # 1. Number Scoring
    scorer = NumberScorer(draws_before, max_num)
    number_scores = scorer.compute_all_signals()
    pair_matrix = scorer.get_pair_matrix()

    # Dùng statistical scores thay cho AI probs
    ai_probs = np.array([number_scores.get(i + 1, 0) for i in range(max_num)])

    # 2. Ticket Optimization (Multi-Zone)
    optimizer = TicketOptimizer(max_num, draws_before)
    tickets = optimizer.generate_optimal_tickets(
        number_scores, ai_probs, pair_matrix, count=num_tickets
    )

    return tickets


def run_backtest(product_type: str, num_draws_to_test: int = 50, num_tickets: int = 18):
    """Chạy backtest cho product_type và trả về audit entries."""
    max_num = 55 if "655" in product_type else 45
    filename = "power655.jsonl" if "655" in product_type else "power645.jsonl"
    prod_name = "POWER 6/55" if "655" in product_type else "MEGA 6/45"

    # Locate file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    paths_to_try = [
        os.path.join(os.getcwd(), 'data', filename),
        os.path.join(base_dir, '..', '..', '..', 'data', filename),
    ]

    target_file = None
    for p in paths_to_try:
        if os.path.exists(p):
            target_file = p
            break

    if not target_file:
        print(f"  ❌ Không tìm thấy file: {filename}")
        return []

    # Load all draws
    all_draws = load_draws(target_file)
    print(f"\n{'='*70}")
    print(f"🏆 BACKTEST ULTRA v3.0 MULTI-ZONE - {prod_name}")
    print(f"{'='*70}")
    print(f"  📂 Loaded {len(all_draws)} kỳ quay")
    print(f"  🔄 Sẽ test {num_draws_to_test} kỳ gần nhất × {num_tickets} vé/kỳ")
    print(f"  📊 Tổng: {num_draws_to_test * num_tickets} vé")
    print(f"  ⏳ Đang chạy...\n")

    audit_entries = []
    total_matches_all = []

    # Need at least 50 draws for training
    start_idx = max(50, len(all_draws) - num_draws_to_test)

    for test_idx in range(start_idx, len(all_draws)):
        draw = all_draws[test_idx]
        draws_before = [d['numbers'] for d in all_draws[:test_idx]]

        # Suppress print output from predictor
        import io
        from contextlib import redirect_stdout
        f = io.StringIO()

        with redirect_stdout(f):
            tickets = predict_for_draw(draws_before, max_num, num_tickets)

        if not tickets:
            continue

        # Compare with actual result
        actual_nums = [int(x) for x in draw['all_numbers']]
        actual_6 = [int(x) for x in draw['numbers']]

        matches = []
        matches_detail = []
        for ticket in tickets:
            ticket_ints = [int(x) for x in ticket]
            matched = sorted(list(set(ticket_ints) & set(actual_nums)))
            matches.append(len(matched))
            matches_detail.append(matched)

        best_match = max(matches)
        total_matches_all.extend(matches)

        # Create audit entry
        draw_date = draw['date']
        if isinstance(draw_date, str):
            timestamp = draw_date + " 15:00:00"
        else:
            timestamp = str(draw_date) + " 15:00:00"

        entry = {
            "timestamp": timestamp,
            "product": product_type,
            "predictions": [[int(x) for x in t] for t in tickets],
            "checked": True,
            "actual_result": [int(x) for x in actual_nums],
            "actual_draw_id": str(draw['id']),
            "match_count": [int(x) for x in matches],
            "matches_detail": [[int(x) for x in m] for m in matches_detail],
        }
        audit_entries.append(entry)

        # Progress log
        draw_num = test_idx - start_idx + 1
        total = len(all_draws) - start_idx
        
        # Count matches per category for this draw
        m3plus = sum(1 for m in matches if m >= 3)
        m4plus = sum(1 for m in matches if m >= 4)
        
        best_emoji = "🏆" if best_match >= 5 else ("🎯" if best_match >= 4 else ("✅" if best_match >= 3 else "⬜"))
        extra = ""
        if m4plus > 0:
            extra = f" 🎯×{m4plus}"
        elif m3plus > 0:
            extra = f" ✅×{m3plus}"
        
        print(f"  {best_emoji} #{draw['id']} ({draw['date']}): Best={best_match}/6{extra}  ({draw_num}/{total})")

    # Summary
    if total_matches_all:
        dist = Counter(total_matches_all)
        total_tickets = len(total_matches_all)

        print(f"\n{'='*70}")
        print(f"📊 TỔNG KẾT BACKTEST - {prod_name}")
        print(f"   {num_draws_to_test} kỳ × {num_tickets} vé = {total_tickets} vé tổng cộng")
        print(f"{'='*70}")
        
        for i in range(7):
            count = dist.get(i, 0)
            pct = count / total_tickets * 100
            bar = "█" * int(pct)
            emoji = "🏆" if i >= 5 else ("🎯" if i == 4 else ("✅" if i == 3 else ""))
            print(f"  Trùng {i} số: {count:4d} vé ({pct:5.1f}%) {bar} {emoji}")

        wins3 = sum(dist.get(i, 0) for i in range(3, 7))
        wins4 = sum(dist.get(i, 0) for i in range(4, 7))
        win3_rate = wins3 / total_tickets * 100
        win4_rate = wins4 / total_tickets * 100
        
        print(f"\n  🎯 Tỷ lệ trúng (≥3 số): {wins3}/{total_tickets} = {win3_rate:.1f}%")
        print(f"  🏆 Tỷ lệ trúng (≥4 số): {wins4}/{total_tickets} = {win4_rate:.2f}%")

        # Per-draw statistics
        best_per_draw = [max(e['match_count']) for e in audit_entries]
        avg_best = np.mean(best_per_draw)
        max_best = max(best_per_draw)
        
        draws_with_3plus = sum(1 for b in best_per_draw if b >= 3)
        draws_with_4plus = sum(1 for b in best_per_draw if b >= 4)
        
        print(f"\n  📈 Trung bình best match/kỳ: {avg_best:.2f}/6")
        print(f"  🏆 Match cao nhất: {max_best}/6")
        print(f"  ✅ Kỳ có ≥3 match: {draws_with_3plus}/{len(audit_entries)} ({draws_with_3plus/len(audit_entries)*100:.0f}%)")
        print(f"  🎯 Kỳ có ≥4 match: {draws_with_4plus}/{len(audit_entries)} ({draws_with_4plus/len(audit_entries)*100:.0f}%)")
        
        # Random baseline comparison
        if max_num == 45:
            random_3plus = 2.8  # P(≥3) per ticket for 6/45
            random_4plus = 0.14
        else:
            random_3plus = 1.7
            random_4plus = 0.06
        
        print(f"\n  📊 So sánh với RANDOM:")
        print(f"     Random ≥3: {random_3plus:.1f}% | Ultra: {win3_rate:.1f}% | Gấp {win3_rate/random_3plus:.1f}x")
        print(f"     Random ≥4: {random_4plus:.2f}% | Ultra: {win4_rate:.2f}% | Gấp {win4_rate/random_4plus:.1f}x")

    return audit_entries


def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║  🏆 BACKTEST ULTRA v3.0 - MULTI-ZONE (50 kỳ × 18 vé) ║")
    print("║  Xoá dữ liệu cũ & Chạy thuật toán nâng cấp          ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"  📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # 1. Xóa audit log cũ
    log_path = os.path.join(os.getcwd(), "data", "audit_log.json")
    if os.path.exists(log_path):
        import shutil
        backup_path = log_path + ".backup"
        shutil.copy2(log_path, backup_path)
        print(f"\n  💾 Đã backup audit_log cũ → audit_log.json.backup")

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump([], f)
    print(f"  🗑️  Đã xoá audit_log.json")

    # 2. Chạy backtest cho cả 2 sản phẩm
    all_entries = []
    
    NUM_DRAWS = 50
    NUM_TICKETS = 18

    # Mega 6/45 - Tạm skip để focus Power 6/55
    entries_645 = [] # run_backtest("power_645", num_draws_to_test=NUM_DRAWS, num_tickets=NUM_TICKETS)
    all_entries.extend(entries_645)

    # Power 6/55 - FOCUS TEST
    entries_655 = run_backtest("power_655", num_draws_to_test=70, num_tickets=18)
    all_entries.extend(entries_655)

    # 3. Sắp xếp theo timestamp và lưu
    all_entries.sort(key=lambda x: x['timestamp'])

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, indent=4, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"✅ ĐÃ HOÀN TẤT BACKTEST v3.0!")
    print(f"  📝 Đã ghi {len(all_entries)} entries vào audit_log.json")
    print(f"  📂 Power 6/45: {len(entries_645)} kỳ × {NUM_TICKETS} vé")
    print(f"  📂 Power 6/55: {len(entries_655)} kỳ × {NUM_TICKETS} vé")
    print(f"  📊 Tổng: {len(all_entries) * NUM_TICKETS} vé đã backtest")
    print(f"{'='*70}")
    print(f"\n  💡 Mở phần mềm → Nhấn 'THỐNG KÊ HIỆU SUẤT' để xem kết quả!")


if __name__ == "__main__":
    main()
