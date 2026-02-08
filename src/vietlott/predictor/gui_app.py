import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import json
import subprocess
import sys
from datetime import datetime, timedelta

# CORE v10.8 - INTELLIGENT FLOW & COMPACT TECH
class VietlottGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VIETLOTT AI PRO v10.8 - LỘ TRÌNH DỰ ĐOÁN THÔNG MINH")
        self.root.geometry("1400x880")
        self.root.configure(bg="#0a0a0a")
        
        # --- HEADER ---
        header = tk.Frame(root, bg="#1a1a1a", pady=5)
        header.pack(fill="x")
        
        # Title
        tk.Label(header, text="🛡️ VIETLOTT AI PREDICTOR PRO", font=("Segoe UI", 20, "bold"), fg="#00e5ff", bg="#1a1a1a").pack(pady=5)

        # COMPACT TECH INFO (Modern Monospace)
        tech_bar = tk.Frame(header, bg="#1a1a1a")
        tech_bar.pack(fill="x")
        tech_str = "CORE: LSTM Deep Learning | ENV: Python 3.11 | LIB: TensorFlow, Pandas, Sklearn | UI: Modernized Tkinter"
        tk.Label(tech_bar, text=tech_str, font=("Consolas", 8), fg="#00cc88", bg="#1a1a1a").pack()

        # COUNTDOWN (High contrast font)
        timer_frame = tk.Frame(header, bg="#1a1a1a")
        timer_frame.pack(pady=5)
        self.timer_45 = tk.Label(timer_frame, text="Mega 6/45: --:--:--", font=("Consolas", 14, "bold"), fg="#ff4d4d", bg="#1a1a1a")
        self.timer_45.pack(side="left", padx=40)
        self.timer_55 = tk.Label(timer_frame, text="Power 6/55: --:--:--", font=("Consolas", 14, "bold"), fg="#ffa366", bg="#1a1a1a")
        self.timer_55.pack(side="left", padx=40)

        # MARQUEE
        self.marquee_frame = tk.Frame(root, bg="#000", height=30)
        self.marquee_frame.pack(fill="x")
        self.marquee_canvas = tk.Canvas(self.marquee_frame, height=30, bg="#000", highlightthickness=0)
        self.marquee_canvas.pack(fill="both", expand=True)
        self.marquee_content = "Đang khởi động hệ thống dự báo thông minh..."
        self.marquee_item = self.marquee_canvas.create_text(1400, 15, text="", font=("Courier New", 12, "bold"), fill="#aa8800", anchor="w")
        self.marquee_pos = 1400

        # --- BODY (1:1:1 Grid) ---
        body = tk.Frame(root, bg="#0a0a0a", padx=10, pady=5)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_columnconfigure(2, weight=1)
        body.grid_rowconfigure(0, weight=1)

        c0 = tk.LabelFrame(body, text=" 🔴 DỰ ĐOÁN MEGA 6/45 ", fg="#ff4d4d", bg="#141414", font=("Arial", 11, "bold"), padx=5, pady=5)
        c0.grid(row=0, column=0, sticky="nsew", padx=5)
        self.btn_soi_45 = ttk.Button(c0, text="🔥 SOI CẦU MEGA MỚI", command=lambda: self.start_prediction("power_645"), state="disabled")
        self.btn_soi_45.pack(fill="x")
        tk.Label(c0, text="Lưu ý: Bạn nên sử dụng 'PHÂN TÍCH CHUYÊN SÂU'", font=("Arial", 8, "italic"), fg="#ff9999", bg="#141414").pack()
        self.lock_45 = tk.Text(c0, font=("Consolas", 10), bg="#1a0d0d", fg="#ffaaaa", borderwidth=0, height=12)
        self.lock_45.pack(fill="x", pady=5)
        
        tk.Label(c0, text="📅 Lịch sử dự báo:", fg="#ffcc00", bg="#141414", font=("Arial", 9)).pack(anchor="w")
        self.list_45 = tk.Listbox(c0, bg="#000", fg="#aaa", font=("Consolas", 9), height=5, borderwidth=0)
        self.list_45.pack(fill="x")
        self.list_45.bind("<<ListboxSelect>>", lambda e: self.on_select_history("power_645"))
        self.audit_45 = tk.Text(c0, font=("Consolas", 10), bg="#0d1a0d", fg="#aaffaa", borderwidth=0)
        self.audit_45.pack(fill="both", expand=True, pady=5)

        # COLUMN 1: KẾT QUẢ + CONTROL BUTTONS
        c1 = tk.LabelFrame(body, text=" ⏳ KẾT QUẢ MỚI NHẤT ", fg="#00ff88", bg="#141414", font=("Arial", 11, "bold"), padx=5, pady=5)
        c1.grid(row=0, column=1, sticky="nsew", padx=5)
        
        # BẢNG ĐIỀU KHIỂN HỆ THỐNG
        ctrl_frame = tk.LabelFrame(c1, text=" 🛠️ BẢNG ĐIỀU KHIỂN ", fg="#ffcc00", bg="#1a1a1a", font=("Arial", 9, "bold"), padx=5, pady=5)
        ctrl_frame.pack(fill="x", pady=(0, 5))
        
        # Grid layout for buttons
        ctrl_frame.columnconfigure(0, weight=1)
        ctrl_frame.columnconfigure(1, weight=1)

        self.btn_crawl = ttk.Button(ctrl_frame, text="🌐 CẬP NHẬT DỮ LIỆU", command=self.update_data)
        self.btn_crawl.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        self.btn_audit = ttk.Button(ctrl_frame, text="🔍 KIỂM TRA DỰ ĐOÁN", command=self.run_audit)
        self.btn_audit.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)

        self.btn_reverse = ttk.Button(ctrl_frame, text="🧠 PHÂN TÍCH CHUYÊN SÂU", command=self.run_reverse_engineering)
        self.btn_reverse.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        self.btn_stats = ttk.Button(ctrl_frame, text="📊 THỐNG KÊ HIỆU SUẤT", command=self.show_overall_stats)
        self.btn_stats.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        
        self.hist_text = tk.Text(c1, font=("Consolas", 10), bg="#000", fg="#e0e0e0", borderwidth=0)
        self.hist_text.pack(fill="both", expand=True)

        c2 = tk.LabelFrame(body, text=" 🟠 DỰ ĐOÁN POWER 6/55 ", fg="#ffa366", bg="#141414", font=("Arial", 11, "bold"), padx=5, pady=5)
        c2.grid(row=0, column=2, sticky="nsew", padx=5)
        self.btn_soi_55 = ttk.Button(c2, text="🔥 SOI CẦU POWER MỚI", command=lambda: self.start_prediction("power_655"), state="disabled")
        self.btn_soi_55.pack(fill="x")
        tk.Label(c2, text="Lưu ý: Bạn nên sử dụng 'PHÂN TÍCH CHUYÊN SÂU'", font=("Arial", 8, "italic"), fg="#ffccaa", bg="#141414").pack()
        self.lock_55 = tk.Text(c2, font=("Consolas", 10), bg="#1a140d", fg="#ffccaa", borderwidth=0, height=12)
        self.lock_55.pack(fill="x", pady=5)
        
        tk.Label(c2, text="📅 Lịch sử dự báo:", fg="#ffcc00", bg="#141414", font=("Arial", 9)).pack(anchor="w")
        self.list_55 = tk.Listbox(c2, bg="#000", fg="#aaa", font=("Consolas", 9), height=5, borderwidth=0)
        self.list_55.pack(fill="x")
        self.list_55.bind("<<ListboxSelect>>", lambda e: self.on_select_history("power_655"))
        self.audit_55 = tk.Text(c2, font=("Consolas", 10), bg="#0d1a0d", fg="#aaffaa", borderwidth=0)
        self.audit_55.pack(fill="both", expand=True, pady=5)

        # Tags
        for w in [self.audit_45, self.audit_55]:
            w.tag_configure("match", foreground="#ff3333", font=("Consolas", 10, "bold"))
            w.tag_configure("header", foreground="#ffff00", font=("Consolas", 10, "bold"))

        # FOOTER
        self.status_var = tk.StringVar(value="🚀 Sẵn sàng.")
        tk.Label(root, textvariable=self.status_var, bg="#1a1a1a", fg="#00ff88", anchor="w", padx=15).pack(fill="x", side="bottom")

        self.run_smart_marquee(); self.start_timer_thread(); self.refresh_ui_data()

    def run_smart_marquee(self):
        try:
            self.marquee_canvas.itemconfig(self.marquee_item, text=self.marquee_content)
            self.marquee_pos -= 2
            if self.marquee_pos < -3000: self.marquee_pos = 1400
            self.marquee_canvas.coords(self.marquee_item, self.marquee_pos, 15)
            self.root.after(30, self.run_smart_marquee)
        except: pass

    def get_next_draw(self, prod):
        now = datetime.now()
        days = [2, 4, 6] if "645" in prod else [1, 3, 5]
        for i in range(8):
            target = (now + timedelta(days=i)).replace(hour=18, minute=30, second=0, microsecond=0)
            if target.weekday() in days and target > now: return target
        return now

    def start_timer_thread(self):
        def _tick():
            try:
                t45, t55 = self.get_next_draw("power_645"), self.get_next_draw("power_655")
                now = datetime.now()
                d45, d55 = (t45-now).total_seconds(), (t55-now).total_seconds()
                h1, r1 = divmod(int(max(0, d45)), 3600); m1, s1 = divmod(r1, 60)
                h2, r2 = divmod(int(max(0, d55)), 3600); m2, s2 = divmod(r2, 60)
                self.timer_45.config(text=f"Mega 6/45: {h1:02d}:{m1:02d}:{s1:02d}")
                self.timer_55.config(text=f"Power 6/55: {h2:02d}:{m2:02d}:{s2:02d}")
                self.root.after(1000, _tick)
            except: pass
        _tick()

    def refresh_ui_data(self):
        threading.Thread(target=self._async_load, daemon=True).start()

    def _async_load(self):
        try:
            import pandas as pd
            base = os.getcwd(); hist = "--- KỲ QUAY GẦN NHẤT ---\n\n"
            for pk in ["power_645", "power_655"]:
                path = os.path.join(base, "data", pk.replace("_","")+".jsonl")
                pname = "MEGA" if "645" in pk else "POWER"
                if os.path.exists(path):
                    df = pd.read_json(path, lines=True).sort_values(by=["date"], ascending=False)
                    hist += f"[{pname}]\n"
                    for _, r in df.head(10).iterrows():
                        res_str = "-".join([f"{n:02d}" for n in sorted(r['result'])])
                        d_str = r['date'].strftime("%d/%m/%Y") if hasattr(r['date'], 'strftime') else str(r['date']).split()[0]
                        hist += f"#{r['id']} ({d_str}) | {res_str}\n"
                    hist += "\n"
            self.root.after(0, lambda: self._update_ui(hist))
        except: pass

    def _update_ui(self, hist_str):
        self.hist_text.config(state="normal"); self.hist_text.delete("1.0", tk.END); self.hist_text.insert(tk.END, hist_str); self.hist_text.config(state="disabled")
        self._load_audit_logic()

    def _load_audit_logic(self):
        log_path = os.path.join(os.getcwd(), "data", "audit_log.json")
        if not os.path.exists(log_path): return
        with open(log_path, "r", encoding="utf-8") as f: data = json.load(f)
        
        msgs = []
        for pk in ["power_645", "power_655"]:
            prod_name = "MEGA" if "645" in pk else "POWER"
            p_list = [e for e in data if e['product'] == pk or e['product'] == pk.replace("_","")]
            lb = self.list_45 if "645" in pk else self.list_55
            lb.delete(0, tk.END)
            # SHOW ALL PREDICTIONS IN LIST
            for e in reversed(p_list): lb.insert(tk.END, f"{('✅' if e.get('checked') else '⏳')} {e['timestamp']}")
            
            p_box = self.lock_45 if "645" in pk else self.lock_55
            p_box.config(state="normal"); p_box.delete("1.0", tk.END)
            
            # Logic: Show last UNCHECKED prediction as active
            active = next((e for e in reversed(p_list) if not e.get('checked')), None)
            if active:
                p_box.insert(tk.END, f"💎 ĐANG CHỜ QUAY ({active['timestamp']}):\n{'-'*40}\n")
                for i, t in enumerate(active['predictions']):
                    p_box.insert(tk.END, f" Vé {i+1:02d}: {' '.join([f'{n:02d}' for n in sorted(t)])}\n")
                msgs.append(f"⏳ {prod_name}: Đang chờ dự thưởng.")
            else:
                p_box.insert(tk.END, "\n\n   🍀 KỲ NÀY CHƯA DỰ ĐOÁN\n   Bấm 'SOI CẦU MỚI' để chốt số!")
                msgs.append(f"🍀 {prod_name}: Sẵn sàng soi cầu!")
            p_box.config(state="disabled")
        if msgs: self.marquee_content = "  ||  ".join(msgs) + "  "

    def on_select_history(self, pk):
        lb = self.list_45 if "645" in pk else self.list_55
        sel = lb.curselection()
        if not sel: return
        log_path = os.path.join(os.getcwd(), "data", "audit_log.json")
        with open(log_path, "r", encoding="utf-8") as f: data = json.load(f)
        p_list = list(reversed([e for e in data if e['product'] == pk or e['product'] == pk.replace("_","")]))
        entry = p_list[sel[0]]
        
        au_w = self.audit_45 if "645" in pk else self.audit_55
        au_w.config(state="normal"); au_w.delete("1.0", tk.END)
        if entry.get('checked'):
            au_w.insert(tk.END, f"📊 KQ KỲ #{entry.get('actual_draw_id','?')}\n", "header")
            au_w.insert(tk.END, f" KQ: {' '.join([f'{n:02d}' for n in entry.get('actual_result',[])])}\n{'-'*35}\n")
            for i, pred in enumerate(entry['predictions']):
                au_w.insert(tk.END, f" Vé {i+1:02d}: ")
                for n in sorted(pred):
                    if n in entry.get('actual_result',[]): au_w.insert(tk.END, f"{n:02d} ", "match")
                    else: au_w.insert(tk.END, f"{n:02d} ")
                au_w.insert(tk.END, f"({entry['match_count'][i]})\n")
        else:
            au_w.insert(tk.END, f"⌛ Đang kiểm tra kỳ mới...\n")
            self.run_silent_audit(pk)
        au_w.config(state="disabled")

    def run_silent_audit(self, pk):
        def _task():
            try:
                from lstm_predictor import check_audit_log
                subprocess.run([sys.executable, "src/vietlott/cli/crawl.py", pk, "--index_to", "1"], creationflags=0x08000000)
                check_audit_log(product_filter=pk)
                self.root.after(0, self.refresh_ui_data)
            except: pass
        threading.Thread(target=_task).start()

    def start_prediction(self, prod):
        """Bắt đầu soi cầu mới"""
        log_path = os.path.join(os.getcwd(), "data", "audit_log.json")
        
        # Kiểm tra xem có dự đoán chưa kiểm tra không
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Lấy danh sách dự đoán của sản phẩm này
                p_list = [e for e in data if e['product'] == prod or e['product'] == prod.replace("_","")]
                
                if p_list:
                    latest = p_list[-1]  # Dự đoán mới nhất
                    
                    # CHỈ CHẶN nếu chưa kiểm tra (checked = false hoặc None)
                    if not latest.get('checked', False):
                        prod_name = "Mega 6/45" if "645" in prod else "Power 6/55"
                        msg = f"⚠️ Đã có dự đoán cho {prod_name} chưa được kiểm tra!\n\n"
                        msg += f"Dự đoán lúc: {latest['timestamp']}\n\n"
                        msg += "Vui lòng:\n"
                        msg += "1. Nhấn '🌐 CẬP NHẬT KẾT QUẢ MỚI'\n"
                        msg += "2. Nhấn '🔍 KIỂM TRA DỰ ĐOÁN'\n"
                        msg += "3. Sau đó mới soi cầu kỳ tiếp theo!"
                        
                        messagebox.showwarning("Chưa kiểm tra dự đoán cũ!", msg)
                        return
            except Exception as e:
                # Nếu lỗi đọc file, cho phép tiếp tục
                pass
        
        # Bắt đầu soi cầu
        self.status_var.set(f"🤖 Đang soi cầu {prod}...")
        
        # Disable cả 2 nút soi cầu để tránh spam
        btn_45 = getattr(self, 'btn_soi_45', None)
        btn_55 = getattr(self, 'btn_soi_55', None)
        
        def _p():
            try:
                # Import và xử lý
                from lstm_predictor import LSTMPredictor, log_predictions
                import pandas as pd
                
                df = pd.read_json(os.path.join("data", prod.replace("_","")+".jsonl"), lines=True).sort_values(by=["date", "id"])
                p = LSTMPredictor(window_size=15, max_num=(55 if "655" in prod else 45))
                d = p.prepare_data(df)
                X, y = p.create_sequences(d)
                p.build_model(input_shape=(X.shape[1], X.shape[2]))
                
                # Training (tăng lên 50-60 giây để chính xác hơn)
                self.root.after(0, lambda: self.status_var.set(f"🧠 Đang huấn luyện AI Deep Learning (30 epochs)..."))
                p.train(X, y, epochs=30)
                
                # Dự đoán
                self.root.after(0, lambda: self.status_var.set(f"🔮 Đang tạo dự đoán..."))
                tickets = [p.predict_next(d[-p.window_size:]) for _ in range(10)]
                
                # Lưu log
                log_predictions(prod, tickets)
                
                # Cập nhật UI
                self.root.after(0, self.refresh_ui_data)
                self.root.after(0, lambda: self.status_var.set("✅ Đã hoàn thành dự báo mới!"))
                
                # Hiện thông báo thành công
                prod_name = "Mega 6/45" if "645" in prod else "Power 6/55"
                msg = f"✅ Đã tạo xong 10 bộ số dự đoán cho {prod_name}!\n\n"
                msg += "Xem trong 'Lịch sử dự báo' bên dưới."
                self.root.after(0, lambda: messagebox.showinfo("Thành công!", msg))
                
            except Exception as e:
                # Hiển thị lỗi rõ ràng
                error_msg = f"❌ Lỗi khi soi cầu:\n\n{type(e).__name__}: {str(e)}"
                self.root.after(0, lambda: self.status_var.set(f"❌ Lỗi: {str(e)[:50]}..."))
                self.root.after(0, lambda m=error_msg: messagebox.showerror("Lỗi!", m))
                
        threading.Thread(target=_p, daemon=True).start()


    def update_data(self):
        """Cập nhật dữ liệu mới từ vietlott.vn"""
        self.btn_crawl.config(state="disabled")
        self.btn_audit.config(state="disabled")
        self.status_var.set("🌐 Đang tải kết quả mới từ vietlott.vn...")
        
        def _crawl():
            success_count = 0
            error_msgs = []
            
            try:
                import subprocess, sys
                
                # Crawl Power 6/55
                self.root.after(0, lambda: self.status_var.set("🌐 Đang tải Power 6/55..."))
                try:
                    result = subprocess.run(
                        [sys.executable, "src/vietlott/cli/crawl.py", "power_655", "--index_to", "2"], 
                        creationflags=0x08000000, 
                        capture_output=True,
                        timeout=30,  # Timeout 30 giây
                        text=True
                    )
                    if result.returncode == 0:
                        success_count += 1
                    else:
                        error_msgs.append(f"Power 6/55: {result.stderr[:100] if result.stderr else 'Unknown error'}")
                except subprocess.TimeoutExpired:
                    error_msgs.append("Power 6/55: Timeout (quá 30s)")
                except Exception as e:
                    error_msgs.append(f"Power 6/55: {str(e)[:100]}")
                
                # Crawl Mega 6/45
                self.root.after(0, lambda: self.status_var.set("🌐 Đang tải Mega 6/45..."))
                try:
                    result = subprocess.run(
                        [sys.executable, "src/vietlott/cli/crawl.py", "power_645", "--index_to", "2"], 
                        creationflags=0x08000000, 
                        capture_output=True,
                        timeout=30,
                        text=True
                    )
                    if result.returncode == 0:
                        success_count += 1
                    else:
                        error_msgs.append(f"Mega 6/45: {result.stderr[:100] if result.stderr else 'Unknown error'}")
                except subprocess.TimeoutExpired:
                    error_msgs.append("Mega 6/45: Timeout (quá 30s)")
                except Exception as e:
                    error_msgs.append(f"Mega 6/45: {str(e)[:100]}")
                
                # Thông báo kết quả
                if success_count == 2:
                    self.root.after(0, lambda: self.status_var.set("✅ Đã cập nhật xong! Nhấn 'Kiểm tra dự đoán' để đối soát."))
                elif success_count == 1:
                    self.root.after(0, lambda: self.status_var.set(f"⚠️ Cập nhật 1/2 thành công. {error_msgs[0] if error_msgs else ''}"))
                else:
                    msg = "❌ Không cập nhật được. "
                    if error_msgs:
                        msg += error_msgs[0]
                    self.root.after(0, lambda m=msg: self.status_var.set(m))
                
                self.root.after(0, lambda: self.btn_crawl.config(state="normal"))
                self.root.after(0, lambda: self.btn_audit.config(state="normal"))
                self.root.after(0, self.refresh_ui_data)
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"❌ Lỗi: {str(e)}"))
                self.root.after(0, lambda: self.btn_crawl.config(state="normal"))
                self.root.after(0, lambda: self.btn_audit.config(state="normal"))
        
        threading.Thread(target=_crawl, daemon=True).start()

    def run_audit(self):
        """Kiểm tra kết quả dự đoán"""
        self.btn_audit.config(state="disabled")
        self.btn_crawl.config(state="disabled")
        self.status_var.set("🔍 Đang kiểm tra các dự đoán cũ...")
        
        def _audit():
            try:
                from lstm_predictor import check_audit_log
                check_audit_log()
                self.root.after(0, lambda: self.status_var.set("✅ Đã kiểm tra xong! Xem kết quả trong 'Lịch sử dự báo'."))
                self.root.after(0, lambda: self.btn_audit.config(state="normal"))
                self.root.after(0, lambda: self.btn_crawl.config(state="normal"))
                self.root.after(0, self.refresh_ui_data)
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"❌ Lỗi: {str(e)}"))
                self.root.after(0, lambda: self.btn_audit.config(state="normal"))
                self.root.after(0, lambda: self.btn_crawl.config(state="normal"))
        
        threading.Thread(target=_audit, daemon=True).start()

    def run_reverse_engineering(self):
        """Chạy module Reverse Engineering"""
        
        # 1. Ask for product type
        from tkinter import simpledialog
        
        # Create a custom dialog for selection
        dialog = tk.Toplevel(self.root)
        dialog.title("Chọn loại vé phân tích")
        dialog.geometry("300x150")
        dialog.configure(bg="#222")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        geo_str = f"+{root_x + root_w//2 - 150}+{root_y + root_h//2 - 75}"
        dialog.geometry(geo_str)
        
        choice_var = tk.StringVar(value="")
        
        tk.Label(dialog, text="Bạn muốn phân tích chuyên sâu cho:", fg="#fff", bg="#222", font=("Arial", 10)).pack(pady=10)
        
        def set_choice(val):
            choice_var.set(val)
            dialog.destroy()
            
        ttk.Button(dialog, text="🔴 Mega 6/45", command=lambda: set_choice("power_645")).pack(fill="x", padx=20, pady=5)
        ttk.Button(dialog, text="🟠 Power 6/55", command=lambda: set_choice("power_655")).pack(fill="x", padx=20, pady=5)
        
        self.root.wait_window(dialog)
        selected_prod = choice_var.get()
        
        if not selected_prod:
            return # Cancelled
            
        # 2. Run Analysis
        self.btn_reverse.config(state="disabled")
        prod_name = "Mega 6/45" if "645" in selected_prod else "Power 6/55"
        self.status_var.set(f"🧠 Đang phân tích chuyên sâu {prod_name} (chờ 1-2 phút)...")
        
        def _run():
            try:
                # Import dynamically
                try:
                    from . import reverse_engineering
                except ImportError:
                    import reverse_engineering
                
                # Run analysis
                report, tickets = reverse_engineering.run_analysis_and_get_report(selected_prod)
                
                # Show report
                self.root.after(0, lambda: self._show_report(report))
                self.root.after(0, lambda: self.status_var.set(f"✅ Đã xong! Tìm thấy {len(tickets)} bộ số tối ưu."))
                
                # 3. Ask to SAVE predictions
                if tickets:
                    def ask_save():
                        if messagebox.askyesno("Chốt số?", 
                                             f"Hệ thống đã tìm thấy {len(tickets)} bộ số tối ưu cho {prod_name}.\n\n"
                                             "Bạn có muốn dùng 10 bộ số này làm DỰ ĐOÁN CHÍNH THỨC kỳ này không?"):
                             # Calls logger
                             try:
                                 from lstm_predictor import log_predictions
                                 log_predictions(selected_prod, tickets)
                                 self.refresh_ui_data()
                                 messagebox.showinfo("Thành công", "Đã lưu 10 bộ số vào lịch sử dự báo!")
                             except Exception as log_err:
                                 messagebox.showerror("Lỗi lưu", str(log_err))
                                 
                    self.root.after(0, ask_save)
                
                self.root.after(0, lambda: self.btn_reverse.config(state="normal"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"❌ Lỗi: {str(e)}"))
                self.root.after(0, lambda: messagebox.showerror("Lỗi phân tích", str(e)))
                self.root.after(0, lambda: self.btn_reverse.config(state="normal"))
        
        threading.Thread(target=_run, daemon=True).start()

    def _show_report(self, report):
        self.hist_text.config(state="normal")
        self.hist_text.delete("1.0", tk.END)
        self.hist_text.insert(tk.END, report)
        self.hist_text.config(state="disabled")

    def show_overall_stats(self):
        """Hiển thị bảng thống kê hiệu suất dựa trên audit_log.json"""
        try:
            from lstm_predictor import get_detailed_stats
            
            stats_45 = get_detailed_stats("power_645")
            stats_55 = get_detailed_stats("power_655")
            
            report = "📊 BÁO CÁO HIỆU SUẤT DỰ ĐOÁN TOÀN HỆ THỐNG\n"
            report += "═" * 45 + "\n\n"
            
            for name, stats in [("MEGA 6/45", stats_45), ("POWER 6/55", stats_55)]:
                report += f"▶️ SẢN PHẨM: {name}\n"
                if stats:
                    report += f"   - Tổng số kỳ đã soi: {stats['total_draws']}\n"
                    report += f"   - Tổng số vé đã chốt: {stats['total_tickets']}\n"
                    report += f"   - Số vé trúng (>= 3 số): {stats['wins']}\n"
                    report += f"   - Tỷ lệ thắng trung bình: {stats['win_rate']}%\n"
                    report += "   - Chi tiết trúng khớp:\n"
                    for i in range(7):
                        count = stats['distribution'].get(i, 0)
                        pct = (count / stats['total_tickets'] * 100) if stats['total_tickets'] > 0 else 0
                        report += f"      + Trùng {i} số: {count} vé ({pct:.1f}%)\n"
                else:
                    report += "   - (Chưa có dữ liệu đối soát cho sản phẩm này)\n"
                report += "\n"
            
            report += "═" * 45 + "\n"
            report += f"Cập nhật lúc: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            report += "Mẹo: Hãy dùng 'Phân tích chuyên sâu' để tăng tỷ lệ trúng!"
            
            self._show_report(report)
            self.status_var.set("✅ Đã hiển thị thống kê hiệu suất.")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo thống kê: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    app = VietlottGUI(root); root.mainloop()

