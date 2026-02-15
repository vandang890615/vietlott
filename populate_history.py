
import json
import os
import sys
import pandas as pd
from datetime import datetime
import numpy as np

# Setup path
sys.path.append(os.path.join(os.getcwd(), 'src', 'vietlott', 'predictor'))

def populate_power_history():
    print("🚀 Đang tái hiện lịch sử 50 kỳ Power 6/55 (Thuật toán v4.0)...")
    
    # 1. Load Data
    data_path = os.path.join("data", "power655.jsonl")
    df = pd.read_json(data_path, lines=True).sort_values("id")
    
    # Get last 50 draws
    total_draws = len(df)
    start_idx = total_draws - 60 # Lấy dư ra chút
    if start_idx < 0: start_idx = 0
    
    # Import Predictor
    try:
        from ultra_predictor import NumberScorer, TicketOptimizer
    except ImportError:
        # Fallback manual import if needed, but pythonpath should handle
        pass

    history_entries = []
    
    # Loop through the last 50 draws (simulating past predictions)
    # Target: Predict draw 'i', utilizing data up to 'i-1'
    
    for i in range(total_draws - 50, total_draws):
        target_row = df.iloc[i]
        past_data = df.iloc[:i] # Data available before the draw
        
        draw_id = target_row['id']
        draw_date = target_row['date']
        actual_result = target_row['result']
        
        # --- RUN PREDICTION (v4.0 Logic) ---
        # 1. Scorer
        # We need to adapt NumberScorer to accept dataframe or list of results
        # UltraPredictor reads file directly. We can mock the file or just extract stats manually.
        # Faster way: Use NumberScorer logic but feed it sliced data? 
        # NumberScorer takes 'data' list.
        
        past_results = past_data['result'].tolist()
        
        # Init Scorer (55 numbers)
        scorer = NumberScorer(past_results, max_num=55)
        final_scores = scorer.compute_all_signals()
        pair_matrix = scorer.get_pair_matrix()
        
        # 2. Optimize Tickets
        optimizer = TicketOptimizer(max_num=55, draws=past_results)
        
        # Mock AI probs (Fast mode)
        ai_probs = np.array([final_scores.get(n, 0) for n in range(1, 56)])
        
        tickets = optimizer.generate_optimal_tickets(
            final_scores, ai_probs, pair_matrix, count=10
        )
        
        # Clean tickets (convert list of lists cleanly)
        tickets = [list(t) for t in tickets]
        
        # --- CHECK RESULT ---
        match_counts = []
        is_jackpot = False
        for t in tickets:
            matches = set(t).intersection(set(actual_result))
            match_counts.append(len(matches))
            if len(matches) == 6: is_jackpot = True
            
        # --- CREATE LOG ENTRY ---
        entry = {
            "product": "power_655",
            "date": str(draw_date).split()[0] if hasattr(draw_date, 'strftime') else str(draw_date),
            "timestamp": f"{str(draw_date).split()[0]} 18:00:00", # Mock time
            "prediction": f"Vé tốt nhất: {tickets[0]}",
            "tickets": tickets,
            "strategy": "v4.0 Hybrid (Backtest)",
            "result": "MISS",
            "checked": True,
            "actual_result": actual_result,
            "actual_draw_id": int(draw_id),
            "match_count": match_counts
        }
        history_entries.append(entry)
        
        # Progress bar
        sys.stdout.write(f"\r⏳ Processed Draw #{draw_id} ")
        sys.stdout.flush()

    print("\n✅ Đã tạo xong 50 kỳ lịch sử.")
    
    # 3. Merge with existing log (keep non-Power entries like Keno/Max3D)
    log_path = os.path.join("data", "audit_log.json")
    existing_data = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            
    # Filter out old Power 6/55 entries to replace with strictly these 50
    # Keep Keno/Max3D/Bingo
    other_entries = [e for e in existing_data if e.get('product') not in ['power_655', 'power655']]
    
    # Combine (Oldest first in JSON usually, but GUI reverses it. We append new history.)
    # Actually, history entries are past. 'other_entries' are recent/future.
    # Let's put history first, then others.
    final_log = history_entries + other_entries
    
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(final_log, f, indent=4, ensure_ascii=False)
        
    print(f"💾 Đã lưu vào {log_path}")

if __name__ == "__main__":
    populate_power_history()
