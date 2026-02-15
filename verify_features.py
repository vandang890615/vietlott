import sys
import os
import random
import json
import logging
from datetime import datetime
from vietlott.predictor.lstm_predictor import LSTMPredictor, log_predictions
# Assuming max3d_bingo_predictor is in path
sys.path.append(os.path.join(os.getcwd(), 'src', 'vietlott', 'predictor'))
from max3d_bingo_predictor import predict_max3d_pro, predict_bingo18

logging.basicConfig(level=logging.INFO)

print("="*50)
print("TESTING NEW FEATURES LOGIC")
print("="*50)

# 1. LOTTO 5/35 (Mock Data + LSTM)
print("\n[1] TEST LOTTO 5/35 PREDICTION")
try:
    # 1a. Ensure data/lotto.jsonl exists with mock data
    lotto_path = "data/lotto.jsonl"
    if not os.path.exists(lotto_path):
        print("  Generating mock data for Lotto...")
        with open(lotto_path, "w") as f:
            for i in range(100):
                res = sorted(random.sample(range(1, 36), 5))
                entry = {"id": f"{i+1:05d}", "date": f"2026-01-{i%30+1:02d}", "result": res}
                f.write(json.dumps(entry) + "\n")
    
    # 1b. Run LSTM Prediction (headless)
    print("  Importing LSTMPredictor...")
    import pandas as pd
    df = pd.read_json(lotto_path, lines=True)
    p = LSTMPredictor(window_size=15, max_num=35) # Max 35
    d = p.prepare_data(df)
    X, y = p.create_sequences(d)
    print("  Building model...")
    p.build_model(input_shape=(X.shape[1], X.shape[2]))
    print("  Training model (short epoch)...")
    p.train(X, y, epochs=2, batch_size=32)
    next_seq = d[-15:]
    if len(next_seq) < 15:
        print("  Not enough data for prediction (Test failed)")
    else:
        pred = p.predict_next(next_seq)
        print(f"  Result: {pred}")
        print("  [SUCCESS] Lotto Prediction Logic Works")

except Exception as e:
    print(f"  [FAILED] {e}")


# 2. MAX 3D PRO
print("\n[2] TEST MAX 3D PRO PREDICTION")
try:
    res = predict_max3d_pro()
    print(f"  Result: {res}")
    if len(res) > 0 and len(res[0]) == 2:
        print("  [SUCCESS] Max 3D Pro Logic Works")
    else:
        print("  [FAILED] Unexpected result format")
except Exception as e:
    print(f"  [FAILED] {e}")


# 3. BINGO 18
print("\n[3] TEST BINGO 18 PREDICTION")
try:
    res = predict_bingo18()
    print(f"  Result: {res}")
    if "tai_xiu" in res:
        print("  [SUCCESS] Bingo 18 Logic Works")
    else:
        print("  [FAILED] Missing keys")
except Exception as e:
    print(f"  [FAILED] {e}")

print("\n="*50)
print("TEST COMPLETE")
