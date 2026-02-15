
import sys
import os
import json
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))
sys.path.append(os.path.join(os.getcwd(), "src", "vietlott", "predictor"))

from lstm_predictor import log_predictions, check_audit_log

def test_bingo_id_audit():
    print("--- TESTING BINGO 18 AUDIT FLOW ---")
    
    # 1. Create a mock draw in data/bingo18.jsonl
    mock_id = "#999999"
    mock_result = [1, 2, 3]
    mock_row = {"date": "2026-02-15", "id": mock_id, "result": mock_result, "page": 1}
    
    path = "data/bingo18.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(mock_row) + "\n")
    print(f"Created mock draw {mock_id} in {path}")
    
    # 2. Log a prediction for THAT SPECIFIC ID
    # In real flow, last_id is #999999, so next is #1000000
    target_id = "#1000000"
    mock_pred = [[1, 2, 3], [4, 5, 6]]
    
    log_predictions("bingo18", mock_pred, target_draw_id=target_id)
    print(f"Logged prediction for target ID: {target_id}")
    
    # 3. Check audit log (should be UNCHECKED)
    res = check_audit_log(product_filter="bingo18")
    print(f"Audit result (should be 0 because #1000000 not in data yet): {res}")
    
    # 4. Add the actual result for #1000000
    final_row = {"date": "2026-02-15", "id": target_id, "result": [1, 5, 6], "page": 1}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(final_row) + "\n")
    print(f"Added result for {target_id} to {path}")
    
    # 5. Run audit again (should now be CHECKED)
    res = check_audit_log(product_filter="bingo18")
    print(f"Audit result (should be 1): {res}")
    
    # 6. Verify matches
    with open("data/audit_log.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        last = data[-1]
        if last.get("checked") and last.get("target_draw_id") == target_id:
            print(f"SUCCESS: Match count for {target_id}: {last.get('match_count')}")
            print(f"Matches Detail: {last.get('matches_detail')}")
        else:
            print("FAILURE: Audit did not match correctly.")

if __name__ == "__main__":
    if not os.path.exists("data"): os.makedirs("data")
    test_bingo_id_audit()
