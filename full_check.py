import json
import os
from datetime import datetime

log_file = "data/audit_log.json"
if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Total entries: {len(data)}")
    
    # Check mega
    mega = [e for e in data if '645' in e['product']]
    print(f"Total Mega entries: {len(mega)}")
    if mega:
        last = mega[-1]
        print(f"Last Mega: {last.get('timestamp')} - Checked: {last.get('checked')}")
        if last.get('checked'):
             print(f"Last Mega checked against ID: {last.get('actual_draw_id')}")

    # Check power
    power = [e for e in data if '655' in e['product']]
    print(f"Total Power entries: {len(power)}")
    if power:
        last = power[-1]
        print(f"Last Power: {last.get('timestamp')} - Checked: {last.get('checked')}")
        if last.get('checked'):
             print(f"Last Power checked against ID: {last.get('actual_draw_id')}")

    unchecked = [e for e in data if not e.get('checked')]
    print(f"Total Unchecked: {len(unchecked)}")
    for e in unchecked:
        print(f"Unchecked: {e.get('product')} at {e.get('timestamp')}")
else:
    print("File not found")
