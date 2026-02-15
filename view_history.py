
import json
import os

def view_history():
    path = os.path.join(os.getcwd(), 'data', 'audit_log.json')
    if not os.path.exists(path):
        print("Chưa có lịch sử dự đoán.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("\n📜 LỊCH SỬ DỰ ĐOÁN TOÀN DIỆN (SYSTEM RESET)")
    print("="*60)
    for entry in data:
        prod = entry.get('product', '').upper().replace('_', ' ')
        algo = entry.get('strategy', 'N/A')
        pred = entry.get('prediction', '')
        
        print(f"🔹 SẢN PHẨM: {prod}")
        print(f"   🛠️ Chiến thuật: {algo}")
        print(f"   🎯 Dự đoán chính: {pred}")
        
        tickets = entry.get('tickets', [])
        if tickets and len(tickets) > 0:
            print(f"   🎫 Chi tiết ({len(tickets)} vé):")
            # In tối đa 3 vé đầu tiên
            for i, t in enumerate(tickets[:3]):
                t_str = " ".join([str(n).zfill(2) for n in t]) if isinstance(t, list) else str(t)
                print(f"      {i+1}. {t_str}")
            if len(tickets) > 3:
                print(f"      ... (và {len(tickets)-3} vé khác)")
        
        print("-" * 60)

if __name__ == "__main__":
    view_history()
