# TEST PLAN: ENHANCED LOTTERY GUI & NEW FEATURES

**Objective:** Verify the successful integration of Lotto 5/35, Max 3D tabs, Real-time Auto-Scheduler, and GUI stability.

## 1. GUI Structure Verification
- [ ] **Launch Application**: Run `python src/vietlott/predictor/gui_app.py`.
- [ ] **Window Title**: Verify title contains "VIETLOTT AI ULTRA PRO v5.0".
- [ ] **Tab Navigation**:
    - [ ] **Mega 6/45**: Check for "SOI CẦU MEGA" button and history list.
    - [ ] **Power 6/55**: Check for "SOI CẦU POWER" button and history list.
    - [ ] **Max 3D**: Check for "SOI BỘ SỐ MAX 3D" button and unique UI.
    - [ ] **Max 3D Pro**: Check for "SOI CẶP SỐ MAX 3D PRO" button.
    - [ ] **Keno**: Check for "SOI BẬC 10 KENO" button.
    - [ ] **Lotto**: Check for "SOI CẦU LOTTO" button (New Feature).
    - [ ] **Bingo 18**: Check for "SOI TÀI/XỈU" button.

## 2. Crawler Integration Test
- [ ] **Manual Crawl**: Click "CẬP NHẬT KẾT QUẢ MỚI" (or "TẢI/LÀM MỚI DỮ LIỆU HỆ THỐNG").
- [ ] **Terminal Output**: Verify logs show crawling attempts for:
    - Power 6/55
    - Mega 6/45
    - Max 3D
    - Max 3D Pro
    - Keno
    - Lotto (New)
- [ ] **Data Files**: Check if `data/lotto.jsonl` is created/updated.

## 3. Prediction Logic Test
- [ ] **Lotto 5/35**:
    - Select Lotto tab.
    - Click "SOI CẦU LOTTO".
    - Verify terminal shows "LSTM Training" (Check `max_num=35`).
    - Verify prediction results appear in the result box.
- [ ] **Max 3D Pro**:
    - Select Max 3D Pro tab.
    - Click "SOI CẶP SỐ".
    - Verify result formatting (e.g., "123-456").
- [ ] **Bingo 18**:
    - Select Bingo 18 tab.
    - Click "SOI TÀI/XỈU".
    - Verify result (Tài/Xỉu and sum range).

## 4. Auto-Scheduler & Real-time Features
- [ ] **Enable Auto**: Check "Tự động soi cầu (Real-time)" on Keno tab.
- [ ] **Wait**: Wait for 5-6 minutes (Keno cycle).
- [ ] **Verify Log**: Check terminal for ">>> AUTO: Checking for new KENO results...".
- [ ] **Verify Auto-Save**: Ensure predictions are saved to `data/audit_log.json` without user intervention (if "Tự động lưu" is checked).

## 5. Audit & History
- [ ] **Audit Tab**: Click "KIỂM TRA DỰ ĐOÁN CŨ".
- [ ] **History Display**: Verify distinct history lists for each product are correctly loaded from `audit_log.json`.
- [ ] **Status Icons**: Check for ✅ (Correct) or ⏳ (Pending) icons in the history lists.

## 6. Stability Check
- [ ] **Switching Tabs**: Rapidly switch between tabs while prediction is running. Verify no crashes.
- [ ] **Concurrent Processes**: Run "Cập nhật kết quả" and "Soi cầu" simultaneously (should be blocked or handled gracefully by `is_busy` flag).

---
**Status**: Ready for execution.
