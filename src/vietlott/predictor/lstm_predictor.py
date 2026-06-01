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
    def __init__(self, window_size=15, max_num=55, mode="standard", slots=6):
        from sklearn.preprocessing import MultiLabelBinarizer
        self.window_size = window_size
        self.max_num = max_num
        self.mode = mode  # "standard" or "positional"
        self.slots = slots
        if self.mode == "standard":
            self.mlb = MultiLabelBinarizer(classes=range(1, max_num + 1))
        else:
            self.mlb = None
        self.model = None

    def prepare_data(self, df):
        """Prepare encoded vectors based on the selected mode."""
        if self.mode == "positional":
            return self._prepare_positional_data(df)
        
        # Standard Multi-label binary encoding
        if 'result' in df.columns:
            draws = []
            for r in df['result']:
                raw = list(map(int, r))
                # Power 6/55: 7 numbers, first 6 are main, 7th is bonus
                if len(raw) == 7 and self.max_num == 55:
                    draws.append(sorted(raw[:6]))
                # Lotto: 6 numbers, first 5 are main, 6th is special
                elif len(raw) == 6 and self.max_num == 35:
                    draws.append(sorted(raw[:5]))
                else:
                    draws.append(sorted(raw))
        else:
            cols = ['num_1', 'num_2', 'num_3', 'num_4', 'num_5', 'num_6']
            draws = df[cols].values.tolist()
            draws = [sorted(d) for d in draws]
        
        binary_data = self.mlb.fit_transform(draws)
        return binary_data

    def _prepare_positional_data(self, df):
        """Encodes each slot as a one-hot vector and concatenates them."""
        encoded_draws = []
        for r in df['result']:
            row_encoded = []
            for s in range(self.slots):
                one_hot = np.zeros(self.max_num)
                if s < len(r):
                    val = int(r[s])
                    if 1 <= val <= self.max_num:
                        one_hot[val-1] = 1.0
                row_encoded.extend(one_hot)
            encoded_draws.append(row_encoded)
        return np.array(encoded_draws)

    def create_sequences(self, data):
        X, y = [], []
        for i in range(len(data) - self.window_size):
            X.append(data[i:(i + self.window_size)])
            y.append(data[i + self.window_size])
        return np.array(X), np.array(y)

    def build_model(self, input_shape):
        import tensorflow as tf
        from tensorflow.keras.models import Model
        from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, Bidirectional, Attention, LayerNormalization, GlobalAveragePooling1D
        
        inputs = Input(shape=input_shape)
        
        # 1. Advanced Temporal Processing
        x = Bidirectional(LSTM(256, return_sequences=True))(inputs)
        x = LayerNormalization()(x)
        x = Dropout(0.25)(x)
        
        x = Bidirectional(LSTM(128, return_sequences=True))(x)
        x = LayerNormalization()(x)
        
        # 2. Attention for key draw signals
        query = Dense(256)(x)
        value = Dense(256)(x)
        attn_out = Attention(use_scale=True)([query, value])
        
        # 3. Aggregation and Interpretation
        pool = GlobalAveragePooling1D()(attn_out)
        
        dense = Dense(512, activation='swish')(pool)
        dense = Dropout(0.3)(dense)
        dense = Dense(256, activation='swish')(dense)
        
        # Output logic
        if self.mode == "positional":
            final_dim = self.max_num * self.slots
            # We use sigmoid here for independence or could branch into multiple softmax heads
            outputs = Dense(final_dim, activation='sigmoid')(dense)
        else:
            outputs = Dense(self.max_num, activation='sigmoid')(dense)
            
        model = Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer='adam', loss='binary_crossentropy')
        self.model = model
        return model

    def train(self, X, y, epochs=30, batch_size=32):
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)

    def predict_diverse_batch(self, last_window, df_context=None, batch_size=10, count=6, diversity_weight=0.5):
        """Quantum diversity filtering with support for positional and standard modes."""
        last_window_expanded = np.expand_dims(last_window, axis=0)
        raw_probs = self.model.predict(last_window_expanded, verbose=0)[0]
        
        # Signal Fusion and Shaping
        if self.mode == "positional":
            # Reshape raw_probs to (slots, max_num)
            shaped_probs = raw_probs.reshape((self.slots, self.max_num))
            if df_context is not None:
                from vietlott.predictor.signal_scorer import PositionalSignalScorer, apply_positional_signals
                scorer = PositionalSignalScorer(df_context, self.max_num, slots=self.slots)
                f, g = scorer.get_positional_signals()
                shaped_probs = apply_positional_signals(shaped_probs, f, g)
        else:
            shaped_probs = raw_probs
            if df_context is not None:
                from vietlott.predictor.signal_scorer import SignalScorer, apply_signals
                scorer = SignalScorer(df_context, self.max_num)
                f, g = scorer.get_signals()
                shaped_probs = apply_signals(shaped_probs, f, g)

        tickets = []
        counts = np.zeros(self.max_num)
        
        for _ in range(batch_size):
            if self.mode == "positional":
                ticket = []
                for s in range(self.slots):
                    s_probs = shaped_probs[s]
                    # Penalty for global diversity if needed, or per-slot diversity
                    adj_s = s_probs * np.exp(-diversity_weight * counts / (batch_size + 1))
                    adj_s = adj_s / (np.sum(adj_s) + 1e-12) # Robust normalization
                    val = np.random.choice(range(1, self.max_num + 1), p=adj_s)
                    ticket.append(int(val))
                    counts[val-1] += 0.33 # Slower penalty for slots
            else:
                # Standard diversity filtering
                adj = shaped_probs * np.exp(-diversity_weight * counts / (batch_size + 1))
                adj = adj / (np.sum(adj) + 1e-12) # Robust normalization
                choice = np.random.choice(range(1, self.max_num + 1), size=count, replace=False, p=adj)
                ticket = sorted([int(n) for n in choice])
                for n in ticket: counts[n-1] += 1
            
            tickets.append(ticket)
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
            
        # Modified: Only skip if really done AND has all Bingo extras if it's Bingo
        is_bingo = entry.get("product") == "bingo18"
        if entry["checked"]:
            # Re-process Power/Lotto entries to fix bonus_number if missing
            needs_bonus_fix = (
                entry["product"] in ["power_655", "power655", "lotto"] and
                "bonus_number" not in entry
            )
            if not needs_bonus_fix:
                if not is_bingo or "any_matches_count" in entry:
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
            # Find the first draw whose date is on or after the prediction date
            df['_date_parsed'] = pd.to_datetime(df['date'])
            # For predictions without ID: find first draw AFTER prediction time
            # Use date comparison (most data only has date, not time)
            future_draws = df[df['_date_parsed'] >= p_time.normalize()]
            if not future_draws.empty:
                target_draw = future_draws.iloc[0]
            df.drop(columns=['_date_parsed'], inplace=True, errors='ignore')

        if target_draw is None:
            continue # Result isn't out yet
            
        actual_raw = target_draw['result']
        # Preserve bonus/special number position for Power 6/55 and Lotto
        if entry["product"] == "bingo18":
            actual_nums = [int(n) for n in actual_raw]
        elif entry["product"] in ["power_655", "power655"] and len(actual_raw) >= 7:
            # Power 6/55: 6 main numbers sorted + bonus (7th) at end
            actual_nums = sorted([int(n) for n in actual_raw[:6]]) + [int(actual_raw[6])]
        elif entry["product"] == "lotto" and len(actual_raw) >= 6:
            # Lotto: 5 main numbers sorted + special (6th) at end
            actual_nums = sorted([int(n) for n in actual_raw[:5]]) + [int(actual_raw[5])]
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

            # Bingo 18: Positional Match (Order matters)
            if entry["product"] == "bingo18":
                matched_nums = []
                count = 0
                for i in range(min(len(pred), len(actual_nums))):
                    if int(pred[i]) == int(actual_nums[i]):
                        matched_nums.append(int(pred[i]))
                        count += 1
                matches.append(count)
                matches_detail.append(matched_nums)
            else:
                # Other games: Set-based (order doesn't matter)
                matched_nums = sorted(list(set(pred) & set(actual_nums)))
                matches.append(len(matched_nums))
                matches_detail.append(matched_nums)
        
        entry["checked"] = True
        entry["actual_result"] = actual_nums
        entry["actual_draw_id"] = draw_id
        entry["match_count"] = matches
        entry["matches_detail"] = matches_detail
        
        # Store bonus/special number for easy display access
        if entry["product"] in ["power_655", "power655"] and len(actual_raw) >= 7:
            entry["bonus_number"] = int(actual_raw[6])
        elif entry["product"] == "lotto" and len(actual_raw) >= 6:
            entry["bonus_number"] = int(actual_raw[5])
        
        # Special: Bingo 18 Enhanced Audit (Matching App Styles)
        if entry["product"] == "bingo18":
            actual_sum = sum(actual_nums)
            if 3 <= actual_sum <= 9: actual_tx = "NHỎ"
            elif 10 <= actual_sum <= 11: actual_tx = "HÒA"
            else: actual_tx = "LỚN"
            entry["prediction_tx"] = actual_tx
            
            # Additional: Track 'Any Match' (Trùng 1 số) for each ticket
            any_matches = []
            for pred in preds:
                # How many unique predicted numbers exist in the actual result?
                m_any = sorted(list(set(pred) & set(actual_nums)))
                any_matches.append(len(m_any))
            entry["any_matches_count"] = any_matches
            
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
        
    # Special parsing for Bingo 18
    if product_filter == "bingo18":
        total_tickets = 0
        p_wins = 0 # Positional wins (exact order)
        any_wins = 0 # Any match wins (bao lo)
        tx_wins = 0 # Tai/Xiu wins
        trend = [] # Last 15 sum results: 0=Nho, 1=Hoa, 2=Lon
        
        hit_counts = {i: 0 for i in range(4)}
        for entry in checked:
            actual_sum = sum(entry.get("actual_result", []))
            tx_res = 0 if actual_sum <= 9 else 1 if actual_sum <= 11 else 2
            trend.append(tx_res)
            
            # Predictor's choice
            preds = entry.get("tickets") or entry.get("predictions") or []
            m_pos = entry.get("match_count", [])
            m_any = entry.get("any_matches_count", m_pos)
            
            total_tickets += len(preds)
            for i in range(len(preds)):
                if m_pos[i] > 0: p_wins += 1
                if m_any[i] > 0: any_wins += 1
                c = m_pos[i]
                if c in hit_counts:
                    hit_counts[c] += 1
                elif c > 3:
                    hit_counts[3] += 1
            
        return {
            "total_draws": len(checked),
            "total_tickets": total_tickets,
            "win_rate": round((any_wins/total_tickets*100), 2) if total_tickets > 0 else 0,
            "p_win_rate": round((p_wins/total_tickets*100), 2) if total_tickets > 0 else 0,
            "any_win_rate": round((any_wins/total_tickets*100), 2) if total_tickets > 0 else 0,
            "distribution": hit_counts,
            "trend": trend[-15:], # Last 15 sum categories
            "latest_audit": checked[-1]["timestamp"] if checked else "N/A"
        }
    
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
