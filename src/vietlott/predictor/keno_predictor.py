import datetime
import random
import os
import pandas as pd
from collections import Counter

def get_current_time_slot():
    now = datetime.datetime.now()
    hour = now.hour
    if 6 <= hour < 10: return 'sang', "🌅 SÁNG (06:00 - 10:00)"
    elif 10 <= hour < 14: return 'trua', "☀️ TRƯA (10:00 - 14:00)"
    elif 14 <= hour < 18: return 'chieu', "🌇 CHIỀU (14:00 - 18:00)"
    else: return 'toi', "🌃 TỐI (18:00 - 22:00)"

def calculate_keno_signals():
    """Analyze real keno history for hot/cold/gap signals."""
    path = os.path.join("data", "keno.jsonl")
    if not os.path.exists(path):
        return None, None
    
    try:
        df = pd.read_json(path, lines=True).sort_values(by="date", ascending=False).head(1000)
        if df.empty: return None, None
        
        all_nums = [n for res in df['result'] for n in res]
        counts = Counter(all_nums)
        
        # Gap analysis
        gaps = {}
        target_nums = list(range(1, 81))
        for n in target_nums:
            gap = 0
            for res in df['result']:
                if n in res: break
                gap += 1
            gaps[n] = gap
            
        return counts, gaps
    except:
        return None, None

def generate_keno_prediction(count=3):
    slot_key, slot_name = get_current_time_slot()
    counts, gaps = calculate_keno_signals()
    
    # Base hot numbers for slot (Heuristic)
    static_hot = {
        'sang':  [79, 76, 45, 27, 35, 48, 19, 50, 62, 12],
        'trua':  [44, 5, 48, 4, 22, 60, 35, 50, 19, 14],
        'chieu': [5, 60, 14, 75, 48, 44, 42, 25, 17, 35],
        'toi':   [42, 62, 25, 19, 17, 35, 48, 5, 50, 12]
    }.get(slot_key, [42, 62, 25, 19, 17])

    if not counts:
        # Fallback to static
        return [sorted(random.sample(static_hot + list(range(1,81)), 10)) for _ in range(count)]

    # Scoring numbers: Freq - Gap (we want high freq numbers that are DUE)
    # Actually, high gap in Keno is rare (>10 draws), so we favor high freq + low gap (momentum)
    scored_nums = []
    for n in range(1, 81):
        score = counts.get(n, 0) * 1.0 - gaps.get(n, 0) * 2.0
        # Boost if in time slot
        if n in static_hot: score += 50
        scored_nums.append((n, score))
    
    scored_nums.sort(key=lambda x: x[1], reverse=True)
    top_candidates = [n for n, s in scored_nums[:30]]
    
    tickets = []
    for _ in range(count):
        # Pick 10 numbers from top 30 candidates
        tickets.append(sorted(random.sample(top_candidates, 10)))
        
    return tickets

if __name__ == "__main__":
    tix = generate_keno_prediction()
    for i, t in enumerate(tix):
        print(f"Vé Keno {i+1}: {t}")
