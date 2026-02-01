import numpy as np
import pandas as pd
# tensorflow and sklearn moved to local imports within methods
from loguru import logger
import os
import json
from datetime import datetime

# Setup configuration
try:
    from vietlott.config.products import get_config
except ImportError:
    class DummyConfig:
        def __init__(self, name):
            # Try filenames with and without underscores
            p1 = f"data/{name}.jsonl"
            p2 = f"data/{name.replace('_', '')}.jsonl"
            self.raw_path = p1 if os.path.exists(p1) else p2
    def get_config(name):
        return DummyConfig(name)

class LSTMPredictor:
    def __init__(self, window_size=15, max_num=55):
        from sklearn.preprocessing import MultiLabelBinarizer
        self.window_size = window_size
        self.max_num = max_num
        self.mlb = MultiLabelBinarizer(classes=range(1, max_num + 1))
        self.model = None

    def prepare_data(self, df):
        """Prepare binary vectors for each draw."""
        if 'result' in df.columns:
            # Result is like [1, 2, 3, 4, 5, 6]
            draws = [sorted(list(map(int, r))) for r in df['result']]
        else:
            cols = ['num_1', 'num_2', 'num_3', 'num_4', 'num_5', 'num_6']
            draws = df[cols].values.tolist()
            draws = [sorted(d) for d in draws]
        
        # Convert to binary vectors (Multi-label)
        binary_data = self.mlb.fit_transform(draws)
        return binary_data

    def create_sequences(self, data):
        X, y = [], []
        for i in range(len(data) - self.window_size):
            X.append(data[i:(i + self.window_size)])
            y.append(data[i + self.window_size])
        return np.array(X), np.array(y)

    def build_model(self, input_shape):
        import tensorflow as tf
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(128),
            Dropout(0.2),
            Dense(64, activation='relu'),
            Dense(self.max_num, activation='sigmoid') # Probability for each number
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy')
        self.model = model
        return model

    def train(self, X, y, epochs=30, batch_size=32):
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)

    def predict_next(self, last_window, temperature=1.0):
        """Predict by sampling from the probability distribution."""
        last_window_expanded = np.expand_dims(last_window, axis=0)
        probs = self.model.predict(last_window_expanded, verbose=0)[0]
        
        # Apply temperature to sharpen or flatten the distribution
        if temperature != 1.0:
            probs = np.power(probs, 1.0 / temperature)
            probs = probs / np.sum(probs)
        
        # Get indices of numbers, sorted by probability
        # Instead of just taking the top 6, let's sample to get variety
        # But we need exactly 6.
        # Simple sampling logic: 
        # Normalize probs to sum to 1 for sampling (the model uses sigmoid so they don't sum to 1)
        normalized_probs = probs / np.sum(probs)
        
        # Sample 6 numbers without replacement
        try:
            choice_indices = np.random.choice(
                range(1, self.max_num + 1), 
                size=6, 
                replace=False, 
                p=normalized_probs
            )
            return sorted([int(n) for n in choice_indices])
        except:
            # Fallback if sampling fails (e.g. all zeros)
            return sorted(np.argsort(probs)[-6:] + 1)

def log_predictions(product, tickets):
    """Save predictions to a log file for future audit."""
    log_file = "data/audit_log.json"
    audit_data = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                audit_data = json.load(f)
            except:
                pass
    
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "product": product,
        "predictions": [[int(n) for n in t] for t in tickets],
        "checked": False,
        "actual_result": None,
        "match_count": []
    }
    audit_data.append(entry)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=4, ensure_ascii=False)

def check_audit_log(product_filter=None):
    """Check past predictions against latest data, optionally filtered by product."""
    log_file = "data/audit_log.json"
    if not os.path.exists(log_file):
        return 0
    
    with open(log_file, "r", encoding="utf-8") as f:
        audit_data = json.load(f)
    
    changed = False
    new_matches = 0
    
    for entry in audit_data:
        # Filter if requested
        if product_filter and entry["product"] != product_filter:
            continue
            
        if entry["checked"]:
            continue
            
        config = get_config(entry["product"])
        if not os.path.exists(config.raw_path):
            continue
            
        df = pd.read_json(config.raw_path, lines=True).sort_values(by=["date"], ascending=True)
        if df.empty: continue
        
        # 1. Get prediction date time
        p_time = pd.to_datetime(entry["timestamp"])
            
        # 2. Find the first draw that happened STRICTLY AFTER prediction time
        def get_available_dt(d_val):
             if isinstance(d_val, str):
                 dt = datetime.strptime(d_val, "%Y-%m-%d")
             else:
                 dt = d_val
             return dt.replace(hour=19, minute=0, second=0)
             
        valid_draws = df[df['date'].apply(lambda x: get_available_dt(x)) > p_time]
        
        if valid_draws.empty:
            continue # Result isn't out yet or no future draw found
            
        target_draw = valid_draws.iloc[0]
        actual_nums = sorted([int(n) for n in target_draw['result']])
        draw_id = str(target_draw.get('id', 'N/A'))
        
        matches = []
        matches_detail = []
        for pred in entry["predictions"]:
            matched_nums = sorted(list(set(pred) & set(actual_nums)))
            matches.append(len(matched_nums))
            matches_detail.append(matched_nums)
        
        entry["checked"] = True
        entry["actual_result"] = actual_nums
        entry["actual_draw_id"] = draw_id
        entry["match_count"] = matches
        entry["matches_detail"] = matches_detail
        changed = True
        new_matches += 1

    if changed:
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, indent=4, ensure_ascii=False)
            
    return new_matches

def get_detailed_stats(product_filter=None):
    """Analyze win/loss ratios and performance trends."""
    log_file = "data/audit_log.json"
    if not os.path.exists(log_file):
        return None
    
    with open(log_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    checked = [e for e in data if e.get("checked")]
    if product_filter:
        checked = [e for e in checked if e["product"] == product_filter]
        
    if not checked:
        return None
        
    total_tickets = 0
    hit_counts = {i: 0 for i in range(7)}
    
    for entry in checked:
        m_counts = entry.get("match_count", [])
        total_tickets += len(m_counts)
        for c in m_counts:
            if c in hit_counts:
                hit_counts[c] += 1
            elif c > 6:
                hit_counts[6] += 1 # Handle extra numbers if any
                
    wins = sum(hit_counts[i] for i in range(3, 7))
    win_rate = (wins / total_tickets * 100) if total_tickets > 0 else 0
    
    return {
        "total_draws": len(checked),
        "total_tickets": total_tickets,
        "wins": wins,
        "win_rate": round(win_rate, 2),
        "distribution": hit_counts,
        "latest_audit": checked[-1]["timestamp"] if checked else "N/A"
    }
    # Test script same as before
    import sys
    product_name = "power645"
    if len(sys.argv) > 1:
        product_name = sys.argv[1]
    
    max_num = 55 if "655" in product_name else 45
    predictor = LSTMPredictor(window_size=12, max_num=max_num)
    config = get_config(product_name)
    df = pd.read_json(config.raw_path, lines=True).iloc[::-1]
    data = predictor.prepare_data(df)
    X, y = predictor.create_sequences(data)
    predictor.build_model(input_shape=(X.shape[1], X.shape[2]))
    predictor.train(X, y, epochs=30)
    
    print(f"\nPredictions for {product_name}:")
    last_window = data[-predictor.window_size:]
    results = []
    for i in range(10):
        res = predictor.predict_next(last_window, temperature=0.8 + (i*0.1))
        results.append(res)
        print(f"Vé {i+1:02d}: {res}")
    
    log_predictions(product_name, results)
    print("\nĐã lưu dự đoán vào audit_log.json")
