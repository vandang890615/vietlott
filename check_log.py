import json
import os

log_file = "data/audit_log.json"
if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    unchecked = [e for e in data if not e.get("checked")]
    print(f"Total entries: {len(data)}")
    print(f"Unchecked entries: {len(unchecked)}")
    for e in unchecked:
        print(f"Found unchecked: {e['timestamp']} - {e['product']}")
else:
    print("File not found")
