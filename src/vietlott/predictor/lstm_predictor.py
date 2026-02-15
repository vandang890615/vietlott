import numpy as np
import pandas as pd
# tensorflow and sklearn moved to local imports within methods
from loguru import logger
import os
import json
from datetime import datetime, timedelta

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
        from tensorflow.keras.models import Model
        from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, Bidirectional, Attention, LayerNormalization, Concatenate
        
        # Modern Functional API Model
        inputs = Input(shape=input_shape)
        
        # 1. Bidirectional LSTM for context
        lstm1 = Bidirectional(LSTM(128, return_sequences=True))(inputs)
        lstm1 = LayerNormalization()(lstm1)
        dropout1 = Dropout(0.2)(lstm1)
        
        lstm2 = Bidirectional(LSTM(64, return_sequences=True))(dropout1)
        lstm2 = LayerNormalization()(lstm2)
        
        # 2. Simple Attention Mechanism
        # Query, Value, Key
        query = Dense(128)(lstm2)
        value = Dense(128)(lstm1) # Skip connection from first layer
        attn_out = Attention(use_scale=True)([query, value])
        
        # 3. Aggregation
        flat = tf.keras.layers.GlobalAveragePooling1D()(attn_out)
        
        # 4. Dense Layers
        dense1 = Dense(128, activation='relu')(flat)
        dropout2 = Dropout(0.2)(dense1)
        dense2 = Dense(64, activation='relu')(dropout2)
        
        output = Dense(self.max_num, activation='sigmoid')(dense2)
        
        model = Model(inputs=inputs, outputs=output)
        model.compile(optimizer='adam', loss='binary_crossentropy')
        self.model = model
        return model

    def train(self, X, y, epochs=30, batch_size=32):
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)

    def predict_diverse_batch(self, last_window, df_context=None, batch_size=10, count=6, diversity_weight=0.5):
        """
        Generate a batch of tickets with maximized diversity using a penalty mechanism.
        'Quantum-Inspired' approach to spread coverage over the probability manifold.
        """
        last_window_expanded = np.expand_dims(last_window, axis=0)
        base_probs = self.model.predict(last_window_expanded, verbose=0)[0]
        
        # Signal Fusion
        if df_context is not None:
            try:
                from vietlott.predictor.signal_scorer import SignalScorer, apply_signals
                scorer = SignalScorer(df_context, self.max_num)
                freq, gap = scorer.get_signals()
                base_probs = apply_signals(base_probs, freq, gap)
            except: pass

        tickets = []
        counts = np.zeros(self.max_num) # Track how many times each number is used in the batch

        for _ in range(batch_size):
            # Apply diversity penalty: more used = lower prob
            # penalty factor: 1.0 - (usage_count / current_batch_index) * weight
            penalty = np.ones(self.max_num)
            if len(tickets) > 0:
                penalty = 1.0 - (counts * diversity_weight / len(tickets))
                penalty = np.clip(penalty, 0.1, 1.0) # Don't zero out completely

            adjusted_probs = base_probs * penalty
            normalized_probs = adjusted_probs / np.sum(adjusted_probs)
            
            try:
                choice_indices = np.random.choice(
                    range(1, self.max_num + 1), 
                    size=count, 
                    replace=False, 
                    p=normalized_probs
                )
                ticket = sorted([int(n) for n in choice_indices])
            except:
                # Fallback to top numbers if sampling fails
                ticket = sorted(np.argsort(adjusted_probs)[-count:] + 1)
            
            tickets.append(ticket)
            # Update counts for next iteration
            for n in ticket:
                counts[n-1] += 1
                
        return tickets

    def predict_next(self, last_window, df_context=None, temperature=1.0, count=6):
        """Predict by sampling from the probability distribution with signal fusion."""
        last_window_expanded = np.expand_dims(last_window, axis=0)
        probs = self.model.predict(last_window_expanded, verbose=0)[0]
        
        # Signal Fusion if context is provided
        if df_context is not None:
            try:
                from vietlott.predictor.signal_scorer import SignalScorer, apply_signals
                scorer = SignalScorer(df_context, self.max_num)
                freq, gap = scorer.get_signals()
                probs = apply_signals(probs, freq, gap)
            except Exception as e:
                logger.error(f"Signal Fusion failed: {e}")

        # Apply temperature
        if temperature != 1.0:
            probs = np.power(probs, 1.0 / temperature)
            probs = probs / np.sum(probs)
        
        normalized_probs = probs / np.sum(probs)
        
        # Sample numbers without replacement
        try:
            choice_indices = np.random.choice(
                range(1, self.max_num + 1), 
                size=count, 
                replace=False, 
                p=normalized_probs
            )
            return sorted([int(n) for n in choice_indices])
        except Exception:
            # Fallback
            return sorted(np.argsort(probs)[-count:] + 1)

def log_predictions(product, tickets, target_draw_id=None):
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
        "target_draw_id": str(target_draw_id) if target_draw_id else None,
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
    from datetime import datetime, timedelta
    import pandas as pd
    
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
        
        def get_numeric_id(val):
            try: return int(str(val).replace('#', '').strip())
            except: return None

        # 1. Match by Draw ID if available
        target_draw = None
        t_id_numeric = get_numeric_id(entry.get("target_draw_id"))
        
        if t_id_numeric is not None:
            # Optimize: filter by numeric ID
            match_rows = df[df['id'].apply(get_numeric_id) == t_id_numeric]
            if not match_rows.empty:
                target_draw = match_rows.iloc[0]
        
        # 2. HEALING LOGIC: If ID match failed or ID is missing, try to find the next draw in sequence
        if target_draw is None:
            p_time = pd.to_datetime(entry["timestamp"])
            # For Bingo/Keno - strict sequence finding if no ID: 
            # find first draw in history that occurs AFTER prediction time
            # Note: Bingo/Keno data usually has date only, or simulated time.
            # We look for the first draw whose date/time is >= prediction time.
            
            # Since some data only has 'date', we prefer ID if it exists and just hasn't appeared yet.
            # If we definitely don't have a valid target_id_numeric, we can't heal safely 
            # without risking matching the wrong draw. 
            pass # We wait for the ID to appear or be calculated.

        if target_draw is None:
            continue # Result isn't out yet
            
        actual_raw = target_draw['result']
        # For Bingo18/Max3D, order might matter or user expects original. For others, sort for set-matching display.
        if entry["product"] == "bingo18":
            actual_nums = [int(n) for n in actual_raw]
        else:
            actual_nums = sorted([int(n) for n in actual_raw])

        draw_id = str(target_draw.get('id', 'N/A'))
        
        matches = []
        matches_detail = []
        # Support legacy keys
        preds = entry.get("predictions") or entry.get("tickets")
        if not preds and "prediction" in entry:
            preds = [entry["prediction"]]
        
        if not preds: continue

        for pred in preds:
            # Ensure pred is a list of integers
            if isinstance(pred, str):
                 try: pred = [int(s) for s in pred.split()]
                 except: continue
            if not isinstance(pred, list): continue

            # For Bingo18, we highlight based on existence, but preserve order in display header
            matched_nums = sorted(list(set(pred) & set(actual_nums)))
            matches.append(len(matched_nums))
            matches_detail.append(matched_nums)
        
        entry["checked"] = True
        entry["actual_result"] = actual_nums
        entry["actual_draw_id"] = draw_id
        entry["match_count"] = matches
        entry["matches_detail"] = matches_detail
        
        # Special: Bingo 18 Tai/Xiu Audit
        if entry["product"] == "bingo18":
            actual_sum = sum(actual_nums)
            actual_tx = "Tài" if actual_sum > 10 else "Xỉu"
            entry["prediction_tx"] = actual_tx
            
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
