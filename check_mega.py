import json
data = json.load(open('data/audit_log.json', encoding='utf-8'))
mega = [e for e in data if '645' in e['product']]
for e in mega[-20:]:
    print(f"{e['timestamp']} - Draw ID: {e.get('actual_draw_id')} - Checked: {e.get('checked')}")
