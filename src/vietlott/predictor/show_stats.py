#!/usr/bin/env python3
"""Đọc audit_log.json và hiển thị thống kê hiệu suất."""
import json
import os
from collections import Counter

log_path = os.path.join(os.getcwd(), "data", "audit_log.json")
with open(log_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total entries: {len(data)}")
print()

for product in ["power_645", "power_655"]:
    prod_name = "MEGA 6/45" if "645" in product else "POWER 6/55"
    entries = [e for e in data if e["product"] == product and e.get("checked")]
    
    if not entries:
        print(f"{prod_name}: Không có dữ liệu")
        continue
    
    all_matches = []
    for entry in entries:
        all_matches.extend(entry.get("match_count", []))
    
    dist = Counter(all_matches)
    total = len(all_matches)
    
    print(f"{'='*55}")
    print(f"  {prod_name} - {len(entries)} kỳ, {total} vé")
    print(f"{'='*55}")
    
    for i in range(7):
        count = dist.get(i, 0)
        pct = count / total * 100 if total > 0 else 0
        bar = "#" * int(pct * 2)
        emoji = " <<<" if i >= 4 else ""
        print(f"  Trùng {i} số: {count:4d} vé ({pct:5.1f}%) {bar}{emoji}")
    
    wins = sum(dist.get(i, 0) for i in range(3, 7))
    win_rate = wins / total * 100 if total > 0 else 0
    print(f"\n  Tỷ lệ trúng (>=3 số): {wins}/{total} = {win_rate:.1f}%")
    
    best_per_draw = [max(e["match_count"]) for e in entries]
    avg_best = sum(best_per_draw) / len(best_per_draw) if best_per_draw else 0
    max_best = max(best_per_draw) if best_per_draw else 0
    print(f"  TB best match/kỳ: {avg_best:.2f}/6")
    print(f"  Max match: {max_best}/6")
    
    # Show each draw detail
    print(f"\n  Chi tiết từng kỳ:")
    for entry in entries:
        best = max(entry["match_count"])
        emoji = "🏆" if best >= 5 else ("🎯" if best == 4 else ("✅" if best == 3 else "⬜"))
        print(f"    {emoji} #{entry['actual_draw_id']} ({entry['timestamp'][:10]}): Best={best}/6  matches={entry['match_count']}")
    print()
