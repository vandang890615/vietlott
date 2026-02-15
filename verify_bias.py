
import sys
import os
import collections

# Add path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
sys.path.insert(0, os.path.join(os.getcwd(), 'src', 'vietlott', 'predictor'))

try:
    from ultra_predictor import run_ultra_prediction
except ImportError:
    # Manual import if needed or just rely on path
    import ultra_predictor

print("🔍 ĐANG KIỂM TRA ĐỘ BỀN VỮNG CỦA THUẬT TOÁN v4.0...")
print("   Mục tiêu: Chứng minh số 53, 54, 55 đã bị LOẠI BỎ HOÀN TOÀN.")

# Run prediction for Power 6/55
# Generate lots of tickets to be sure
report, tickets = ultra_predictor.run_ultra_prediction("power_655", use_ai=False) 

# Flatten all numbers
all_nums = [n for t in tickets for n in t]
counts = collections.Counter(all_nums)

print(f"\n📊 KẾT QUẢ KIỂM TRA TRÊN {len(tickets)} VÉ:")

dead_nums = [53, 54, 55]
found_dead = False
for num in dead_nums:
    count = counts.get(num, 0)
    print(f"   ❌ Số {num}: Xuất hiện {count} lần")
    if count > 0:
        found_dead = True

hot_nums = [22, 34, 9]
print("\n🔥 KỂM TRA SỐ NÓNG (Bias):")
for num in hot_nums:
    count = counts.get(num, 0)
    print(f"   ✅ Số {num}: Xuất hiện {count} lần")

print("\n------------------------------------------------")
if not found_dead:
    print("✅ CHỨNG MINH THÀNH CÔNG: Số 53, 54, 55 ĐÃ BIẾN MẤT KHỎI DỰ ĐOÁN!")
    print("   Thuật toán v4.0 đã hoạt động chính xác.")
else:
    print("⚠️ THẤT BẠI: Vẫn còn số chết xuất hiện.")
