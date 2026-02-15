import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta

# CORE v11.0 - ULTRA PREDICTOR ENGINE
class VietlottGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏆 VIETLOTT AI ULTRA PRO v5.0 - CYBERNETIC PREDICTOR")
        self.root.geometry("1280x820")
        self.root.configure(bg="#050510")
        self.is_busy = False # Block multi-clicks
        self.status_var = tk.StringVar(value="✅ HỆ THỐNG SẴN SÀNG")
        self.clock_var = tk.StringVar(value="--:--:--")
        
        # --- HEADER ---
        header = tk.Frame(root, bg="#000", pady=10, highlightbackground="#00fff2", highlightthickness=1)
        header.pack(fill="x", padx=10, pady=5)
        
        # Title with neon glow effect (simulated)
        title_lbl = tk.Label(header, text="⚡ VIETLOTT AI ULTRA PRO v5.0 ⚡", font=("Segoe UI", 24, "bold"), fg="#00fff2", bg="#000")
        title_lbl.pack()
        tk.Label(header, text="THE MOST ADVANCED LOTTERY PREDICTION ENGINE IN VIETNAM", font=("Segoe UI", 9), fg="#666", bg="#000").pack()

        # COMPACT TECH INFO (Modern Monospace)
        tech_bar = tk.Frame(header, bg="#1a1a1a")
        tech_bar.pack(fill="x")
        tech_str = "CORE: Ensemble AI (BiLSTM+Transformer+GRU) | 7-Signal Scoring | Hot Zone + Coverage Optimization | TensorFlow 2.x"
        tk.Label(tech_bar, text=tech_str, font=("Consolas", 8), fg="#00cc88", bg="#1a1a1a").pack(side="left", padx=10)
        
        # Real-time Clock in Header
        tk.Label(tech_bar, textvariable=self.clock_var, font=("Consolas", 9, "bold"), fg="#00fff2", bg="#1a1a1a").pack(side="right", padx=10)

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

        # --- VISUAL FX LAYER (Matrix + Brainwave) ---
        self.fx_canvas = tk.Canvas(self.root, width=1280, height=50, bg="#000000", highlightthickness=0)
        self.fx_canvas.pack(fill="x", side="bottom")
        self.brain_wave_ids = []
        for i in range(50):
            # Create thicker vertical bars for equalizer effect
            line = self.fx_canvas.create_line(i*26, 25, i*26, 25, fill="#00ff00", width=4)
            self.brain_wave_ids.append(line)

        # --- BODY (Tabbed Interface - Game Centric) ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#050510", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1a1a2e", foreground="#888", padding=[15, 10], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#00fff2")], foreground=[("selected", "#000")])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # DEFINE GAME TABS DIRECTLY (No more Dashboard/System top-level tabs)
        self.tab_mega = tk.Frame(self.notebook, bg="#050510"); self.notebook.add(self.tab_mega, text="MEGA 6/45")
        self.tab_power = tk.Frame(self.notebook, bg="#050510"); self.notebook.add(self.tab_power, text="POWER 6/55")
        self.tab_max3d_pro = tk.Frame(self.notebook, bg="#050510"); self.notebook.add(self.tab_max3d_pro, text="MAX 3D PRO")
        self.tab_max3d = tk.Frame(self.notebook, bg="#050510"); self.notebook.add(self.tab_max3d, text="MAX 3D/3D+")
        self.tab_keno = tk.Frame(self.notebook, bg="#050510"); self.notebook.add(self.tab_keno, text="KENO")
        self.tab_bingo = tk.Frame(self.notebook, bg="#050510"); self.notebook.add(self.tab_bingo, text="BINGO 18")
        self.tab_lotto = tk.Frame(self.notebook, bg="#050510"); self.notebook.add(self.tab_lotto, text="LOTTO")
        
        # Global System Tab (At the end)
        self.tab_system = tk.Frame(self.notebook, bg="#050510"); self.notebook.add(self.tab_system, text="⚙️ HỆ THỐNG")

        # Setup Content for Each Game Tab
        mega_desc = "🧠 Ensemble Deep Learning (BiLSTM + Transformer + GRU) với 50 epochs training. Signal Scoring: 7 lớp."
        self._setup_product_tab(self.tab_mega, "power_645", "SOI CẦU MEGA 6/45", self.predict_mega, mega_desc)
        
        power_desc = "🧪 Hybrid Neural Network (BiLSTM + GRU) chuyên sâu cho chu kỳ số lớn. Tùy biến Heuristic."
        self._setup_product_tab(self.tab_power, "power_655", "SOI CẦU POWER 6/55", self.predict_power, power_desc)
        
        max3d_pro_desc = "🧬 Machine Bias Correction & Matrix Coverage Optimizer. Phân tích sai số máy quay."
        self._setup_product_tab(self.tab_max3d_pro, "max3d_pro", "SOI CẦU MAX 3D PRO", self.predict_max3d, max3d_pro_desc)
        
        max3d_desc = "📊 Digit Frequency Analysis & Positional Bias (RE-Pos Edition). Phân tích xác suất vị trí."
        self._setup_product_tab(self.tab_max3d, "max3d", "SOI CẦU MAX 3D/3D+", self.predict_max3d_basic, max3d_desc)
        
        keno_desc = "⚡ Time-Lag Derivative & RE-Bias Engine. Dựa trên dao động thời gian thực của máy chủ quay."
        self._setup_product_tab(self.tab_keno, "keno", "SOI CẦU KENO", self.predict_keno, keno_desc)
        
        bingo_desc = "🧠 Neural Network (BiLSTM + GRU) + Pattern Optimizer. Phân tích chu kỳ Tài/Xỉu & tần suất số nóng."
        self._setup_product_tab(self.tab_bingo, "bingo18", "SOI CẦU BINGO 18", lambda: self.start_prediction("bingo18"), bingo_desc)
        
        lotto_desc = "🔄 Cyclic Frequency Analysis v2.0. Phát hiện chu kỳ nóng và điểm rơi xác suất."
        self._setup_product_tab(self.tab_lotto, "lotto", "SOI CẦU LOTTO", lambda: self.start_prediction("lotto"), lotto_desc)

        # Setup System Tab
        self._setup_global_system_tab()

        # Init flags
        self.timer_running = False
        self.marquee_running = False
        
        # STATUS BAR
        s_bar = tk.Frame(root, height=30, bg="#111")
        s_bar.pack(side="bottom", fill="x")
        tk.Label(s_bar, textvariable=self.status_var, font=("Segoe UI", 9), fg="#00fff2", bg="#111", anchor="w").pack(side="left", padx=10)
        tk.Label(s_bar, text="v5.1.0 STABLE | Protected Mode: ON | CPU: Optimized", font=("Segoe UI", 8), fg="#666", bg="#111", anchor="e").pack(side="right", padx=10)

        # Start background tasks
        self.start_timer_thread()
        self.run_smart_marquee()
        self.start_auto_schedule_thread()
        self.start_auto_pilot_thread() # New Auto Pilot Engine
        self.refresh_ui_data()
        
        self.root.after(1000, self.announce_today_games)
        
        self.log_to_terminal(">>> VIETLOTT AI KERNEL v5.0 INITIALIZED...")
        self.log_to_terminal(">>> ALL ENGINES GO. WAITING FOR COMMANDS.", "success")
        
        # KÍCH HOẠT REAL-TIME SYNC & STARTUP REPORT
        self.root.after(3000, lambda: self.update_data(silent=True))
        self.root.after(5000, self._render_performance_summary)

    def log_to_terminal(self, msg, tag=None):
        ts = datetime.now().strftime("%H:%M:%S")
        self.terminal.config(state="normal")
        # auto-scroll
        at_bottom = self.terminal.yview()[1] == 1.0
        self.terminal.insert(tk.END, f"[{ts}] ", "info")
        self.terminal.insert(tk.END, f"{msg}\n", tag)
        if at_bottom:
            self.terminal.see(tk.END)
        self.terminal.config(state="disabled")

    def _setup_product_tab(self, frame, prod_code, title, predict_cmd, algo_text):
        """Autonomous Game Tab with History, Controls, and Detailed Audit"""
        frame.grid_columnconfigure(0, weight=3, minsize=300) # History
        frame.grid_columnconfigure(1, weight=4, minsize=400) # Controls/Results
        frame.grid_columnconfigure(2, weight=3, minsize=320) # Stats/Audit Detail
        frame.grid_rowconfigure(0, weight=1)
        
        # --- COL 1: HISTORY ---
        c_hist = tk.LabelFrame(frame, text=" 📜 LỊCH SỬ KẾT QUẢ ", fg="#00e5ff", bg="#050510", font=("Arial", 10, "bold"))
        c_hist.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        attr_hist = f"hist_{prod_code}"
        txt_h = tk.Text(c_hist, font=("Consolas", 9), bg="#050510", fg="#aaa", borderwidth=0)
        txt_h.pack(fill="both", expand=True, padx=5, pady=5)
        txt_h.insert(tk.END, "Đang tải dữ liệu...\n")
        setattr(self, attr_hist, txt_h)

        # --- COL 2: MAIN CONTROLS ---
        c_main = tk.Frame(frame, bg="#050510")
        c_main.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        lbl_t = tk.Label(c_main, text=title, font=("Arial", 16, "bold"), fg="#fff", bg="#050510")
        lbl_t.pack(pady=5)
        
        # Algorithm Specs (Integrated per user request)
        c_algo = tk.Frame(c_main, bg="#0a0a20", bd=1, relief="flat", padx=10, pady=10)
        c_algo.pack(fill="x", pady=5)
        tk.Label(c_algo, text="🧠 THUẬT TOÁN AI ĐANG DÙNG:", font=("Arial", 8, "bold"), fg="#888", bg="#0a0a20").pack(anchor="w")
        tk.Label(c_algo, text=algo_text, font=("Arial", 9), fg="#00ff88", bg="#0a0a20", wraplength=350, justify="left").pack(anchor="w", pady=(2,0))

        # Controls
        ctrl_f = tk.Frame(c_main, bg="#050510")
        ctrl_f.pack(fill="x", pady=10)
        
        btn_soi = ttk.Button(ctrl_f, text="🤖 CHỐT SỐ AI NGAY", command=predict_cmd)
        btn_soi.pack(side="left", expand=True, fill="x", padx=5)
        setattr(self, f"btn_{prod_code}", btn_soi)
        
        btn_sync = ttk.Button(ctrl_f, text="🔄 CẬP NHẬT", command=lambda: self.update_single_data(prod_code))
        btn_sync.pack(side="left", padx=5)
        
        # Results Display
        c_res = tk.LabelFrame(c_main, text=" 🎯 DỰ BÁO KỲ TIẾP THEO ", fg="#00ff88", bg="#000", font=("Arial", 11, "bold"))
        c_res.pack(fill="both", expand=True, pady=5)
        
        txt_r = tk.Text(c_res, font=("Consolas", 12, "bold"), bg="#000", fg="#00ff88", borderwidth=0)
        txt_r.pack(fill="both", expand=True, padx=10, pady=10)
        txt_r.insert(tk.END, "--- CHƯA CÓ DỰ BÁO ---\nNhấn 'Chốt Số AI' để bắt đầu.")
        setattr(self, f"res_{prod_code}", txt_r)
        
        # Options
        opt_f = tk.Frame(c_main, bg="#050510")
        opt_f.pack(fill="x")
        v_save = tk.BooleanVar(value=True); setattr(self, f"autosave_{prod_code}", v_save)
        tk.Checkbutton(opt_f, text="Tự động lưu vào Audit Log", variable=v_save, fg="#666", bg="#050510", selectcolor="#000").pack(side="left")

        # High-Frequency Options (Keno/Bingo)
        if prod_code in ["keno", "bingo18"]:
            v_auto = tk.BooleanVar(value=False); setattr(self, f"auto_{prod_code}", v_auto)
            tk.Checkbutton(opt_f, text="⚡ AUTO: Tự động dự đoán & đối soát", variable=v_auto, fg="#00ff88", bg="#050510", selectcolor="#000").pack(side="left", padx=10)

        # --- COL 3: STATS & AUDIT DETAIL ---
        c_stat = tk.Frame(frame, bg="#050510")
        c_stat.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        self._create_mini_stat_card(c_stat, prod_code)
        
        # Audit Explorer
        c_audit = tk.LabelFrame(c_stat, text=" 🔍 CHI TIẾT ĐỐI SOÁT ", fg="#ffcc00", bg="#0a0a1a", font=("Arial", 9, "bold"))
        c_audit.pack(fill="both", expand=True, pady=5)
        
        # Selection List
        lst_a = tk.Listbox(c_audit, font=("Consolas", 8), bg="#0a0a1a", fg="#ffcc00", borderwidth=0, selectbackground="#333", height=8 if prod_code != "keno" else 15)
        lst_a.pack(fill="x", padx=2, pady=2)
        setattr(self, f"audit_list_{prod_code}", lst_a)
        
        # Detail Viewer
        txt_ad = tk.Text(c_audit, font=("Consolas", 8), bg="#000", fg="#ccc", borderwidth=0, height=10 if prod_code != "keno" else 5)
        txt_ad.pack(fill="both", expand=True, padx=2, pady=2)
        txt_ad.tag_configure("header", foreground="#ff00ff", font=("Consolas", 8, "bold"))
        txt_ad.tag_configure("success", foreground="#00ff88"); txt_ad.tag_configure("match", background="#004400", foreground="#00ff88", font=("Consolas", 8, "bold"))
        setattr(self, f"audit_detail_{prod_code}", txt_ad)
        
        # Bind selection
        lst_a.bind("<<ListboxSelect>>", lambda e, p=prod_code: self._on_select_game_audit(p))

    def _on_select_game_audit(self, prod):
        lst = getattr(self, f"audit_list_{prod}", None)
        txt = getattr(self, f"audit_detail_{prod}", None)
        if not lst or not txt: return
        
        sel = lst.curselection()
        if not sel: return
        
        # Data filtering (matching _load_audit_logic)
        log_path = os.path.join(os.getcwd(), "data", "audit_log.json")
        try:
            with open(log_path, "r", encoding="utf-8") as f: data = json.load(f)
            data.sort(key=lambda x: x.get('timestamp') or x.get('date', ''), reverse=True)
            
            # Find the actual entry matching the index in the list
            if prod == "max3d": filtered = [x for x in data if x.get('product') in ["max3d", "max3d_plus"]]
            else: filtered = [x for x in data if x.get('product') == prod or x.get('product') == prod.replace('_', '')]
            
            entry = filtered[sel[0]]
            
            txt.config(state="normal")
            txt.delete("1.0", tk.END)
            
            d_id = entry.get('actual_draw_id') if entry.get('checked') else entry.get('target_draw_id')
            header_id = f"Kỳ {d_id}" if d_id and d_id != "None" else (entry.get('timestamp') or entry.get('date', ''))[5:16]
            txt.insert(tk.END, f"📊 CHI TIẾT [{prod.upper()}] - {header_id}\n", "header")
            
            if entry.get('checked'):
                actual = entry.get('actual_result', [])
                actual_ints = [int(n) for n in actual]
                txt.insert(tk.END, f"✅ KẾT QUẢ: ", "success")
                
                if "bingo" in prod: 
                    res_fmt = "-".join(map(str, actual))
                    actual_sum = sum(actual_ints)
                    tx = "TÀI" if actual_sum > 10 else "XỈU"
                    txt.insert(tk.END, res_fmt + f" ({tx} {actual_sum})\n")
                else: 
                    res_fmt = " ".join([f"{int(n):02d}" for n in actual])
                    txt.insert(tk.END, res_fmt + "\n")
                
                tickets = entry.get('tickets') or entry.get('predictions', []) or [entry.get('prediction')]
                match_counts = entry.get('match_count', [0]*len(tickets))
                
                for i, t in enumerate(tickets):
                    txt.insert(tk.END, f" #{i+1:02d}: ")
                    if isinstance(t, (list, tuple)):
                        for n in sorted(t):
                             n_int = int(n)
                             if n_int in actual_ints: txt.insert(tk.END, f"{n_int:02d} ", "match")
                             else: txt.insert(tk.END, f"{n_int:02d} ")
                        txt.insert(tk.END, f" ({match_counts[i]})\n")
                    else: txt.insert(tk.END, f"{t}\n")
            else:
                txt.insert(tk.END, "\n⏳ TRẠNG THÁI: CHỜ QUAY THƯỞNG...\n")
                tickets = entry.get('tickets') or entry.get('predictions', [])
                for i, t in enumerate(tickets):
                    # Consistent formatting for pending entries
                    if isinstance(t, list):
                        if "bingo" in prod: t_str = "-".join(map(str, t))
                        else: t_str = " ".join([f"{int(n):02d}" for n in sorted(t)])
                    else: t_str = str(t)
                    txt.insert(tk.END, f" #{i+1:02d}: {t_str}\n")
            
            txt.config(state="disabled")
        except Exception as e:
            print(f"Error viewing game audit: {e}")

    def _create_mini_stat_card(self, parent, prod):
        f = tk.Frame(parent, bg="#1a1a2e", highlightbackground="#333", highlightthickness=1)
        f.pack(fill="x", pady=5)
        
        tk.Label(f, text="HIỆU SUẤT AI", font=("Arial", 8, "bold"), fg="#888", bg="#1a1a2e").pack(pady=(5,0))
        
        rate_val = tk.Label(f, text="--%", font=("Arial", 24, "bold"), fg="#00ff88", bg="#1a1a2e")
        rate_val.pack()
        setattr(self, f"lbl_rate_{prod}", rate_val)
        
        info_val = tk.Label(f, text="0 vé / 0 trúng", font=("Arial", 8), fg="#ccc", bg="#1a1a2e")
        info_val.pack(pady=(0,5))
        setattr(self, f"lbl_info_{prod}", info_val)

    def predict_mega(self):
        self.start_prediction("power_645")

    def predict_power(self):
        self.start_prediction("power_655")

    def _setup_global_system_tab(self):
        """Global System Utils - Enhanced with Audit Details"""
        frame = self.tab_system
        frame.grid_columnconfigure(0, weight=1) # Log
        frame.grid_columnconfigure(1, weight=1) # Tools
        frame.grid_columnconfigure(2, weight=1) # Audit Info
        frame.grid_rowconfigure(0, weight=1)
        
        # 1. Global Log
        c_log = tk.LabelFrame(frame, text=" 💾 GLOBAL SYSTEM LOG ", fg="#00ff00", bg="#000", font=("Consolas", 10, "bold"))
        c_log.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.terminal = tk.Text(c_log, font=("Consolas", 9), bg="#000", fg="#00ff00", borderwidth=0)
        self.terminal.pack(fill="both", expand=True)
        self.terminal.tag_configure("info", foreground="#00e5ff"); self.terminal.tag_configure("warn", foreground="#ffff00"); self.terminal.tag_configure("err", foreground="#ff4d4d"); self.terminal.tag_configure("success", foreground="#00ff88")

        # 2. Tools & Engine Status
        c_tool = tk.LabelFrame(frame, text=" 🛠️ CÔNG CỤ QUẢN TRỊ ", fg="#ffcc00", bg="#141414")
        c_tool.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.btn_crawl = ttk.Button(c_tool, text="📥 CẬP NHẬT TOÀN BỘ DỮ LIỆU", command=self.update_data)
        self.btn_crawl.pack(fill="x", pady=5)
        
        self.btn_deep = ttk.Button(c_tool, text="📥 DEEP SYNC (3000 KỲ)", command=self.deep_sync)
        self.btn_deep.pack(fill="x", pady=5)
        
        self.btn_audit = ttk.Button(c_tool, text="🔍 KIỂM TRA ĐỐI SOÁT TOÀN BỘ", command=self.run_audit)
        self.btn_audit.pack(fill="x", pady=5)
        
        self.btn_ultra = ttk.Button(c_tool, text="🏆 ULTRA PREDICTION v2.0 (GLOBAL)", command=self.run_ultra_prediction)
        self.btn_ultra.pack(fill="x", pady=5)
        
        self.btn_bias = ttk.Button(c_tool, text="🧬 PHÂN TÍCH BIAS HỆ THỐNG", command=self.run_bias_analysis)
        self.btn_bias.pack(fill="x", pady=5)
        
        self.hist_text = tk.Text(c_tool, font=("Consolas", 9), bg="#050510", fg="#aaa", height=10, borderwidth=0)
        self.hist_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.hist_text.insert(tk.END, ">>> SYSTEM READY.\n")

        # 3. GLOBAL AUDIT DETAILS (Answer: "Trúng như thế nào?")
        c_audit = tk.LabelFrame(frame, text=" 📊 CHI TIẾT ĐỐI SOÁT TOÀN CỤC ", fg="#00fff2", bg="#050510")
        c_audit.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        self.full_audit_list = tk.Listbox(c_audit, bg="#000", fg="#00fff2", font=("Consolas", 9), borderwidth=0, selectbackground="#333", height=12)
        self.full_audit_list.pack(fill="x")
        self.full_audit_list.bind("<<ListboxSelect>>", self.on_select_audit_full)
        
        self.audit_detail = tk.Text(c_audit, bg="#000", fg="#ccc", font=("Consolas", 9), borderwidth=0, padx=5, pady=5)
        self.audit_detail.pack(fill="both", expand=True)
        self.audit_detail.tag_configure("header", foreground="#ff00ff", font=("Consolas", 10, "bold"))
        self.audit_detail.tag_configure("success", foreground="#00ff88", font=("Consolas", 9, "bold"))
        self.audit_detail.tag_configure("match", background="#004400", foreground="#00ff88", font=("Consolas", 9, "bold"))

    def on_select_audit_full(self, event):
        sel = self.full_audit_list.curselection()
        if not sel or not hasattr(self, 'last_audit_data'): return
        
        try:
            entry = self.last_audit_data[sel[0]]
            prod = entry.get('product', '').upper()
            
            d_id = entry.get('actual_draw_id') if entry.get('checked') else entry.get('target_draw_id')
            header_id = f"Kỳ {d_id}" if d_id and d_id != "None" else (entry.get('timestamp') or entry.get('date', ''))[5:16]
            
            self.audit_detail.config(state="normal")
            self.audit_detail.delete("1.0", tk.END)
            self.audit_detail.insert(tk.END, f"📊 CHI TIẾT ĐỐI SOÁT [{prod}] - {header_id}\n", "header")
            self.audit_detail.insert(tk.END, "="*45 + "\n")
            
            if entry.get('checked'):
                actual = entry.get('actual_result', [])
                draw_id = entry.get('actual_draw_id', '?')
                self.audit_detail.insert(tk.END, f"✅ KẾT QUẢ KỲ #{draw_id}: ", "success")
                
                # Consistent formatting
                if "bingo" in prod.lower(): 
                    res_fmt = "-".join(map(str, actual))
                    actual_sum = sum([int(n) for n in actual])
                    tx = "TÀI" if actual_sum > 10 else "XỈU"
                    self.audit_detail.insert(tk.END, res_fmt + f" ({tx} {actual_sum})\n\n")
                else: 
                    res_fmt = " ".join([f"{n:02d}" for n in actual])
                    self.audit_detail.insert(tk.END, res_fmt + "\n\n")
                
                tickets = entry.get('tickets') or entry.get('predictions', []) or [entry.get('prediction')]
                match_counts = entry.get('match_count', [0]*len(tickets))
                
                for i, t in enumerate(tickets):
                    if not isinstance(t, (list, tuple)):
                        self.audit_detail.insert(tk.END, f" Vé {i+1:02d}: {t}\n")
                        continue
                        
                    self.audit_detail.insert(tk.END, f" Vé {i+1:02d}: ")
                    for n in sorted(t):
                         n_int = int(n)
                         if n_int in actual: self.audit_detail.insert(tk.END, f"{n_int:02d} ", "match")
                         else: self.audit_detail.insert(tk.END, f"{n_int:02d} ")
                    self.audit_detail.insert(tk.END, f"({match_counts[i]} số)\n")
            else:
                self.audit_detail.insert(tk.END, "\n⏳ TRẠNG THÁI: ĐANG CHỜ QUAY THƯỞNG...\n")
                self.audit_detail.insert(tk.END, "Vui lòng 'Cập nhật kết quả mới' sau giờ quay để đối soát.\n\n")
                tickets = entry.get('tickets') or entry.get('predictions', []) or [entry.get('prediction')]
                for i, t in enumerate(tickets):
                    t_str = " ".join([f"{int(n):02d}" for n in sorted(t)]) if isinstance(t, (list, tuple)) else str(t)
                    self.audit_detail.insert(tk.END, f" Vé {i+1:02d}: {t_str}\n")
            
            self.audit_detail.config(state="disabled")
        except Exception as e:
            self.log_to_terminal(f"Error viewing audit detail: {e}", "err")

    def run_smart_marquee(self):
        if self.marquee_running: return
        self.marquee_running = True
        def _loop():
            try:
                self.marquee_canvas.itemconfig(self.marquee_item, text=self.marquee_content)
                self.marquee_pos -= 2
                if self.marquee_pos < -3000: self.marquee_pos = 1400
                self.marquee_canvas.coords(self.marquee_item, self.marquee_pos, 15)
                self.root.after(30, _loop)
            except Exception:
                pass
        _loop()

    def get_target_draw_id(self, prod):
        """Helper to calculate the next logical Draw ID for any product"""
        try:
            from vietlott.config.products import get_config
            import pandas as pd
            conf = get_config(prod)
            if not os.path.exists(conf.raw_path): return "?"
            
            df = pd.read_json(conf.raw_path, lines=True)
            if df.empty: return "?"
            
            last_id = str(df.iloc[-1].get('id', '')).strip()
            if not last_id: return "?"
            
            clean_id = last_id.replace('#', '').strip()
            new_val = int(clean_id) + 1
            
            if last_id.startswith('#'):
                padding = len(clean_id)
                return f"#{new_val:0{padding}d}"
            return str(new_val)
        except:
            return "?"

    def get_next_draw(self, prod):
        now = datetime.now()
        days = [2, 4, 6] if "645" in prod else [1, 3, 5]
        for i in range(8):
            target = (now + timedelta(days=i)).replace(hour=18, minute=30, second=0, microsecond=0)
            if target.weekday() in days and target > now: return target
        return now

    def start_timer_thread(self):
        if self.timer_running: return
        self.timer_running = True
        def _tick():
            try:
                t45, t55 = self.get_next_draw("power_645"), self.get_next_draw("power_655")
                now = datetime.now()
                d45, d55 = (t45-now).total_seconds(), (t55-now).total_seconds()
                h1, r1 = divmod(int(max(0, d45)), 3600); m1, s1 = divmod(r1, 60)
                h2, r2 = divmod(int(max(0, d55)), 3600); m2, s2 = divmod(r2, 60)
                self.timer_45.config(text=f"Mega 6/45: {h1:02d}:{m1:02d}:{s1:02d}")
                self.timer_55.config(text=f"Power 6/55: {h2:02d}:{m2:02d}:{s2:02d}")
                # Kinetic Pulse Update
                pulse = ["🌐", "⚡", "📡", "🧬"]
                tick_symbol = pulse[int(now.timestamp()) % len(pulse)]
                self.clock_var.set(f"{tick_symbol} {now.strftime('%H:%M:%S')}")
                
                self.root.after(1000, _tick)
            except Exception as e:
                self.log_to_terminal(f"Timer error: {str(e)}", "err")
                self.timer_running = False
        _tick()

        if not hasattr(self, 'fx_running'):
            self.fx_running = True
            threading.Thread(target=self._run_visual_fx, daemon=True).start()

    def _run_visual_fx(self):
        """Simulate Brainwave & Matrix Rain (Threaded for smoothness)"""
        import random, math
        
        # Matrix Setup
        drops = [0] * 50 # 50 columns
        
        while True:
            try:
                # 1. Brainwave Animation (Sine Wave)
                t = time.time() * 8
                for i, line_id in enumerate(self.brain_wave_ids):
                    # Complex wave synthesis
                    h1 = math.sin(t + i*0.2) * 5
                    h2 = math.cos(t*0.5 + i*0.1) * 3
                    height = (h1 + h2)
                    
                    if self.is_busy: 
                        height *= 2.5 # Intensity increases when predicting
                        color = "#ff0055" # Red Alert
                    else:
                        color = "#00ff88" # Stable Green
                        
                    self.root.after(0, lambda l=line_id, c=color: self.fx_canvas.itemconfig(l, fill=c))
                    
                    # Vertical bar visualizer
                    x = i * 26
                    y_base = 25 # Center of 50px high canvas
                    self.root.after(0, lambda l=line_id, _x=x, _h=height: self.fx_canvas.coords(l, _x, 25-_h, _x, 25+_h))

                # 2. Matrix Rain (Simulated on FX Canvas background or separate layer?)
                # Since we reused the canvas, let's just make the brainwave look cooler for now to avoid clutter
                # To do real matrix rain we need a full screen canvas overlay which might block UI.
                # Instead, let's make the "Marquee" look like Matrix code falling occasionally.
                
                if random.random() < 0.1: # Random glitch effect
                    glitch_text = "".join([chr(random.randint(0x30A0, 0x30FF)) for _ in range(10)]) # Katakana
                    self.root.after(0, lambda t=glitch_text: self.marquee_canvas.itemconfig(self.marquee_item, text=f"SYSTEM_BREACH: {t}"))
                elif random.random() < 0.05:
                     self.root.after(0, lambda: self.marquee_canvas.itemconfig(self.marquee_item, text=self.marquee_content))

                time.sleep(0.05)
            except: 
                break

    def refresh_ui_data(self):
        threading.Thread(target=self._async_load, daemon=True).start()

    def _async_load(self):
        def _task():
            try:
                # 1. Update HISTORY Column (Actual Results)
                prods = [
                    ("power_655", "power655"), ("power_645", "power645"),
                    ("max3d", "max3d"), ("max3d_plus", "max3d"), ("max3d_pro", "max3d_pro"),
                    ("keno", "keno"), ("lotto", "lotto"), ("bingo18", "bingo18")
                ]
                import pandas as pd
                
                for key_attr, key_file in prods:
                    widget = getattr(self, f"hist_{key_attr}", None)
                    if not widget: continue
                    
                    try:
                        path = os.path.join("data", f"{key_file}.jsonl")
                        if os.path.exists(path):
                            # Read last 30 lines efficiently
                            lines = []
                            with open(path, 'r') as f:
                                all_lines = f.readlines()
                                lines = all_lines[-30:] # Last 30
                            
                            hist_str = ""
                            for ln in reversed(lines):
                                try:
                                    row = json.loads(ln)
                                    d_id = row.get('id', '?')
                                    date = row.get('date', '?')[:10]
                                    res = row.get('result', [])
                                    
                                    # Format result
                                    if "max3d" in key_attr:
                                        s = " ".join([f"{int(n):03d}" for n in res[:4]]) # Show top prizes
                                    elif "keno" in key_attr:
                                        s = " ".join([f"{int(n):02d}" for n in sorted(res)])
                                        if len(s) > 30: s = s[:27] + "..."
                                    elif "bingo" in key_attr:
                                        s = "-".join(map(str, res))
                                    else:
                                        s = " ".join([f"{int(n):02d}" for n in sorted(res)])
                                        
                                    id_str = f"#{d_id}" if not str(d_id).startswith('#') else d_id
                                    hist_str += f"{id_str} ({date}): {s}\n"
                                except: pass
                            
                            self.root.after(0, lambda w=widget, c=hist_str: self._safe_update_text(w, c))
                    except Exception as e:
                        print(f"Error loading hist for {key_attr}: {e}")

                # 2. Update STATS & AUDIT Columns
                self.root.after(0, self._load_audit_logic)
                self.root.after(0, self._render_performance_summary)
                
            except Exception as e:
                print(f"Async Load Error: {e}")
        threading.Thread(target=_task, daemon=True).start()

    def _safe_update_text(self, widget, content):
        try:
            widget.config(state="normal")
            widget.delete("1.0", tk.END)
            widget.insert(tk.END, content)
            widget.config(state="disabled")
        except: pass

    def _update_ui(self, hist_str):
        # Obsolete, replaced by _safe_update_text per widget
        pass

    def _load_audit_logic(self):
        log_path = os.path.join(os.getcwd(), "data", "audit_log.json")
        if not os.path.exists(log_path): return
        try:
             with open(log_path, "r", encoding="utf-8") as f: data = json.load(f)
             data.sort(key=lambda x: x.get('timestamp') or x.get('date', ''), reverse=True)
             self.last_audit_data = data
        except: return

        # Helper to calculate stats safely
        count_stats = {} # key: (wins, total)

        prods = [
            ("power_655", "power_655"), ("power_645", "power_645"),
            ("max3d_pro", "max3d_pro"), ("max3d", "max3d"),
            ("keno", "keno"), ("lotto", "lotto"), ("bingo18", "bingo18")
        ]

        from lstm_predictor import get_detailed_stats

        for pk, attr_key in prods:
            audit_box = getattr(self, f"audit_{attr_key}", None) # Obsolete
            audit_list = getattr(self, f"audit_list_{attr_key}", None)
            res_box = getattr(self, f"res_{attr_key}", None)
            lbl_rate = getattr(self, f"lbl_rate_{attr_key}", None)
            lbl_info = getattr(self, f"lbl_info_{attr_key}", None)
            
            # Filter logs for this product
            if attr_key == "max3d":
                logs = [x for x in data if x.get('product') in ["max3d", "max3d_plus"]]
            else:
                logs = [x for x in data if x.get('product') == attr_key or x.get('product') == pk]
            
            # Update Audit List (New)
            if audit_list:
                audit_list.delete(0, tk.END)
                for e in logs[:30]:
                    checked = e.get('checked', False)
                    # Priority: actual_draw_id > target_draw_id > timestamp
                    d_id = e.get('actual_draw_id') or e.get('target_draw_id')
                    
                    if not d_id or d_id == "None" or d_id == "?":
                        d_id = (e.get('timestamp') or e.get('date', '?'))[5:16]
                    else:
                        # Clean ID for display
                        d_id = str(d_id).strip()
                        if not d_id.startswith('#'): d_id = f"#{d_id}"
                    
                    status = "✅" if checked else "⏳"
                    max_m = max(e.get('match_count', [0])) if checked else 0
                    res_txt = f"{max_m}s" if checked and max_m > 0 else "Lo" if checked else "Wait"
                    audit_list.insert(tk.END, f" {status} {d_id[:12]: <12} | {res_txt: <4}")

            # Update Latest Result Box remains same logic
            if res_box:
                active = next((e for e in logs if not e.get('checked')), None)
                content = ""
                if active:
                    t_id = active.get('target_draw_id', '?')
                    ts = (active.get('timestamp') or active.get('date', '?'))[5:16]
                    content += f"💎 ĐANG CHỜ KỲ {t_id} ({ts}):\n"
                    tickets = active.get('tickets') or active.get('predictions') or []
                    for i, t in enumerate(tickets):
                        t_val = t
                        if isinstance(t, list): 
                            if "bingo" in attr_key: t_val = "-".join(map(str, t))
                            else: t_val = " ".join([f"{int(n):02d}" for n in sorted(t)])
                        content += f" #{i+1:02d}: {t_val}\n"
                else:
                    content = "\n🎯 SẴN SÀNG DỰ BÁO.\nNhấn nút SOI CẦU để bắt đầu."
                self._safe_update_text(res_box, content)

            # Update Win Rate Card
            try:
                stats = get_detailed_stats(attr_key) 
                if not stats and pk != attr_key: stats = get_detailed_stats(pk)
                if stats and lbl_rate:
                    wr = stats.get('win_rate', 0)
                    wins = stats.get('wins', 0); total = stats.get('total_tickets', 0)
                    color = "#00ff88" if wr >= 10 else "#ffcc00" if wr > 0 else "#ff4d4d"
                    lbl_rate.config(text=f"{wr}%", fg=color)
                    lbl_info.config(text=f"{wins}/{total} vé thắng")
            except: pass

        # Update Marquee & Global Audit
        msg_list = []
        for pk, attr_key in prods:
            logs = [x for x in data if x.get('product') == attr_key or x.get('product') == pk]
            active = next((e for e in logs if not e.get('checked')), None)
            if active: msg_list.append(f"⏳ {attr_key.upper()} đang chờ kết quả")
        
        if msg_list: self.marquee_content = "  ||  ".join(msg_list) + "  ||  Hệ thống AI v6.0 vận hành ổn định.  "
        else: self.marquee_content = "📡 Hệ thống đang giám sát dữ liệu... Sẵn sàng soi cầu cho kỳ quay tiếp theo!  "

        if hasattr(self, 'full_audit_list'):
            self.full_audit_list.delete(0, tk.END)
            for e in data[:50]:
                status = "✅" if e.get('checked') else "⏳"
                ts = (e.get('timestamp') or e.get('date', '?'))[5:16]
                prod = e.get('product', '').upper().replace('_', '.')
                m_list = e.get('match_count', [0])
                res = f"W({max(m_list)})" if e.get('checked') and any(m > 0 for m in m_list) else "Lo" if e.get('checked') else "Wait"
                self.full_audit_list.insert(tk.END, f" {status} {ts} | {prod: <8} | {res}")

    def _render_performance_summary(self):
        """Prints a consolidated system summary to the global log"""
        self.log_to_terminal("╔══════════════════════════════════════════════════════════════════════╗", "header")
        self.log_to_terminal("║              🚀  VIETLOTT AI SYSTEM SUMMARY v6.0  🚀              ║", "header")
        self.log_to_terminal("╚══════════════════════════════════════════════════════════════════════╝", "header")
        
        prods = [
            ("power_655", "P.6/55"), ("power_645", "M.6/45"),
            ("max3d", "M3D"), ("max3d_pro", "M3D Pro"),
            ("keno", "Keno"), ("lotto", "Lotto"), ("bingo18", "Bingo")
        ]
        
        from lstm_predictor import get_detailed_stats
        for pk, short_name in prods:
            stats = get_detailed_stats(pk)
            wr = stats.get('win_rate', 0) if stats else 0
            total = stats.get('total_tickets', 0) if stats else 0
            
            tag = "success" if wr > 10 else "info" if wr > 0 else "warn"
            row = f"   > {short_name: <10} | Win: {wr: >5}% | Total Sync: {total: >5} tickets"
            self.log_to_terminal(row, tag)
            
        self.log_to_terminal("────────────────────────────────────────────────────────────────────────", "info")
        self.log_to_terminal("   AI STATUS: HEURISTIC ENGINE ONLINE | BIAS PROTECTOR ACTIVE", "success")

    def run_silent_audit(self, pk):
        def _task():
            try:
                from lstm_predictor import check_audit_log
                subprocess.run([sys.executable, "src/vietlott/cli/crawl.py", pk, "--index_to", "1"], creationflags=0x08000000)
                check_audit_log(product_filter=pk)
                self.root.after(0, self.refresh_ui_data)
            except Exception as e:
                self.log_to_terminal(f"Silent audit error ({pk}): {e}", "err")
        threading.Thread(target=_task).start()

    def start_prediction(self, prod):
        if self.is_busy: return
        self.is_busy = True
        self.log_to_terminal(f">>> STARTING PREDICTION FOR {prod.upper()}...", "info")
        self.status_var.set(f"🤖 Đang soi cầu {prod}...")
        
        btn = getattr(self, f"btn_{prod}", None)
        if btn: btn.config(state="disabled")
        
        def _p():
            try:
                # Import và xử lý
                from lstm_predictor import LSTMPredictor, log_predictions
                import pandas as pd
                import random
                from datetime import datetime, timedelta

                # Lấy cấu hình sản phẩm chính xác từ ProductConfig
                from vietlott.config.products import get_config
                conf = get_config(prod)
                json_path = str(conf.raw_path)
                
                # 1. FORCE SILENT CRAWL UPDATE BEFORE PREDICTION (To know the real next ID)
                self.log_to_terminal(f">>> SYNCING LATEST STATE FOR {prod.upper()}...", "info")
                subprocess.run(
                    [sys.executable, "src/vietlott/cli/crawl.py", prod, "--index_to", "1"], 
                    creationflags=0x08000000, capture_output=True, timeout=30, text=True
                )
                
                # Load Data (Freshly updated)
                df = pd.read_json(json_path, lines=True).sort_values(by=["date", "id"])
                if df.empty:
                    raise ValueError(f"Dữ liệu {prod} bị trống. Vui lòng cập nhật lại!")
                
                # 2. CALCULATE TARGET ID
                target_id = self.get_target_draw_id(prod)
                
                self.log_to_terminal(f"🎯 MỤC TIÊU DỰ BÁO: KỲ {target_id}", "header")
                self.status_var.set(f"🧠 AI đang soi cho Kỳ {target_id}...")
                
                # 3. DUPLICATE CHECK
                log_path = os.path.join(os.getcwd(), "data", "audit_log.json")
                if os.path.exists(log_path):
                    with open(log_path, "r", encoding="utf-8") as f: a_data = json.load(f)
                    if any(x.get('product') == prod and str(x.get('target_draw_id')) == target_id for x in a_data):
                        self.log_to_terminal(f"⚠️ Đã có dự báo cho {prod.upper()} kỳ {target_id}. Không chốt trùng.", "warn")
                        self.root.after(0, lambda: self.status_var.set(f"✅ Đã có vé kỳ {target_id}"))
                        return

                # Lấy cấu hình sản phẩm
                conf = get_config(prod)
                max_n = conf.max_value
                output_n = conf.size_output
                
                p = LSTMPredictor(window_size=15, max_num=max_n)
                d = p.prepare_data(df)
                X, y = p.create_sequences(d)
                p.build_model(input_shape=(X.shape[1], X.shape[2]))
                
                # Training
                self.log_to_terminal(f">>> STARTING DEEP LEARNING TRAINING FOR {prod.upper()}...", "warn")
                self.root.after(0, lambda: self.status_var.set(f"🧠 Đang huấn luyện AI (30 epochs)..."))
                p.train(X, y, epochs=30)
                self.log_to_terminal(f">>> TRAINING COMPLETE. OPTIMIZING PREDICTIONS...", "success")
                
                # Dự đoán với Quantum-Inspired Diversity Filter (AI + Diversity Optimization)
                if prod == "lotto":
                    self.log_to_terminal(">>> ACTIVATING ULTRA-COVERAGE MODE FOR LOTTO (35-NUM MANIFOLD)...", "warn")
                    # Tăng trọng số đa dạng lên 0.9 để phủ kín 35 số của Lotto
                    tickets = p.predict_diverse_batch(d[-p.window_size:], df_context=df, batch_size=10, count=output_n, diversity_weight=0.9)
                else:
                    self.log_to_terminal(">>> RUNNING ENSEMBLE INFERENCE + QUANTUM DIVERSITY FILTER...", "info")
                    tickets = p.predict_diverse_batch(d[-p.window_size:], df_context=df, batch_size=10, count=output_n, diversity_weight=0.6)
                    
                self.log_to_terminal(f">>> GENERATED {len(tickets)} DIVERSIFIED CYBERNETIC TICKETS.", "success")
                
                # Save log if Auto-Save is checked
                save_var = getattr(self, f"autosave_{prod}", None)
                if save_var and save_var.get():
                    log_predictions(prod, tickets, target_draw_id=target_id)
                    self.log_to_terminal(f">>> AUTO-SAVED PREDICTIONS FOR KỲ {target_id}.", "success")
                
                # Cập nhật UI
                self.root.after(0, self.refresh_ui_data)
                self.root.after(0, lambda: self.status_var.set("✅ Đã hoàn thành dự báo mới!"))
                
            except Exception as e:
                error_msg = f"❌ Lỗi khi soi cầu:\n\n{type(e).__name__}: {str(e)}"
                self.root.after(0, lambda: self.status_var.set(f"❌ Lỗi: {str(e)[:50]}..."))
                self.root.after(0, lambda m=error_msg: messagebox.showerror("Lỗi!", m))
            finally:
                self.is_busy = False
                if btn: self.root.after(0, lambda: btn.config(state="normal"))
                
        threading.Thread(target=_p, daemon=True).start()


    def start_auto_schedule_thread(self):
        def _loop():
            # Initial wait
            time.sleep(10)
            while True:
                try:
                    now = datetime.now()
                    # Check Keno/Bingo every 5 mins for Bingo (which is 10 min cycle)
                    if (hasattr(self, 'auto_keno') and self.auto_keno.get()) or \
                       (hasattr(self, 'auto_bingo18') and self.auto_bingo18.get()):
                        if now.minute % 5 == 0: 
                             if self.auto_keno.get(): self._auto_process("keno", 1)
                             if self.auto_bingo18.get(): self._auto_process("bingo18", 1)
                    
                    time.sleep(60) # Scan every minute
                except Exception as e:
                    print(f"Auto Schedule Error: {e}")
                    time.sleep(60)
        
        threading.Thread(target=_loop, daemon=True).start()

    def start_auto_pilot_thread(self):
        """
        AI AUTO PILOT v1.5 - Fully autonomous management
        - Morning: Auto-Prediction for today's draws
        - Evening: Auto-Crawl & Auto-Audit
        """
        def _pilot():
            self.log_to_terminal(">>> AI AUTO PILOT ENGINE ENGAGED.", "success")
            
            # --- STARTUP SYNC ---
            self.log_to_terminal(">>> INITIALIZING STARTUP AUDIT...", "info")
            self.update_data(silent=True)
            time.sleep(60)
            threading.Thread(target=self.run_audit, daemon=True).start()
            
            last_checked_hour = -1
            
            while True:
                try:
                    now = datetime.now()
                    hour = now.hour
                    weekday = now.weekday()
                    
                    # 1. Identify Today's Games
                    today_schedule = self.get_today_schedule()
                    
                    # 2. Morning Tasks (09:00 - 10:00): Auto Prediction
                    if hour == 9 and last_checked_hour != hour:
                        self.log_to_terminal(f">>> MORNING CHECK: Identifying targets for {now.strftime('%d/%m/%Y')}...")
                        for prod in today_schedule:
                            if prod not in ["keno", "bingo18"]:
                                if not self.check_if_predicted_today(prod):
                                    self.log_to_terminal(f">>> AUTO-PILOT: Triggering prediction for {prod.upper()}...", "warn")
                                    # Use a separate thread to avoid blocking loop
                                    threading.Thread(target=lambda p=prod: self.start_prediction(p), daemon=True).start()
                                    time.sleep(20) # Gap between predictions
                        last_checked_hour = hour

                    # 3. Evening Tasks (19:00 - 20:00): Auto Crawl & Audit
                    if hour == 19 and last_checked_hour != hour:
                        self.log_to_terminal(">>> EVENING CHECK: Draw time finished. Fetching results...", "info")
                        self.update_data(silent=True)
                        time.sleep(300) 
                        self.log_to_terminal(">>> AUTO-PILOT: Running global audit...", "success")
                        threading.Thread(target=self.run_audit, daemon=True).start()
                        last_checked_hour = hour
                    
                    # 4. Periodic background update (Every 1 hour)
                    if now.minute == 30: # At half-past every hour
                         self.log_to_terminal(">>> AUTO-PILOT: Periodic background sync...", "info")
                         self.update_data(silent=True)
                         time.sleep(60) # Avoid double-trigger in same minute
                    
                    # 4. Reporting (Every hour)
                    if hour != last_checked_hour and hour % 4 == 0:
                        self.announce_today_games()
                        last_checked_hour = hour

                    time.sleep(300) # Check every 5 mins
                except Exception as e:
                    self.log_to_terminal(f"Auto Pilot Error: {e}", "err")
                    time.sleep(60)
        
        threading.Thread(target=_pilot, daemon=True).start()

    def get_today_schedule(self):
        wd = datetime.now().weekday()
        # 0:Mon, 1:Tue, 2:Wed, 3:Thu, 4:Fri, 5:Sat, 6:Sun
        schedule = {
            0: ["max3d"],
            1: ["power_655", "max3d_pro"],
            2: ["power_645", "max3d"],
            3: ["power_655", "max3d_pro"],
            4: ["power_645", "max3d"],
            5: ["power_655", "max3d_pro"],
            6: ["power_645"]
        }
        # Keno/Bingo/Lotto are daily
        today = schedule.get(wd, []) + ["keno", "bingo18", "lotto", "max3d_plus"]
        return today

    def check_if_predicted_today(self, prod):
        """Check if a prediction exists for today in audit_log.json"""
        try:
            log_path = os.path.join(os.getcwd(), "data", "audit_log.json")
            if not os.path.exists(log_path): return False
            with open(log_path, "r", encoding="utf-8") as f: data = json.load(f)
            
            today_str = datetime.now().strftime("%Y-%m-%d")
            # Look for product + today's date in timestamp
            for e in data:
                if e.get("product") == prod and today_str in e.get("timestamp", ""):
                    return True
            return False
        except Exception:
            return False

    def announce_today_games(self):
        today = self.get_today_schedule()
        names = {
            "power_655": "Power 6/55", "power_645": "Mega 6/45", 
            "max3d": "Max 3D", "max3d_plus": "Max 3D+", "max3d_pro": "Max 3D Pro",
            "keno": "Keno", "bingo18": "Bingo 18", "lotto": "Lotto"
        }
        today_names = [names.get(p, p) for p in today]
        msg = f"📅 HÔM NAY QUAY THƯỞNG: {', '.join(today_names)}"
        self.log_to_terminal(msg, "header")
        self.status_var.set(msg)
        self.marquee_content = f"  🔥 {msg}  ||  ⚡ Hệ thống AI đang giám sát real-time...  "

    def _auto_process(self, prod, limit):
        def _task():
            try:
                import subprocess, sys
                self.log_to_terminal(f"📡 AUTO-SYNC: Kiểm tra kết quả mới cho {prod.upper()}...", "info")
                res = subprocess.run(
                    [sys.executable, "src/vietlott/cli/crawl.py", prod, "--index_to", str(limit)], 
                    creationflags=0x08000000, capture_output=True, timeout=60, text=True
                )
                if res.returncode == 0:
                    # After crawl, immediately run audit to see if we won the last prediction
                    from lstm_predictor import check_audit_log
                    check_audit_log(product_filter=prod)
                    
                    self.root.after(0, self.refresh_ui_data)
                    self.log_to_terminal(f"✅ AUTO-SYNC: {prod.upper()} đã cập nhật & đối soát xong.", "success")
                    
                    # Logic: If last prediction is now checked, trigger NEW prediction
                    # For safety, we only auto-predict if there is NO pending prediction
                    self.root.after(2000, lambda: self._trigger_auto_predict_if_needed(prod))
                else:
                    self.log_to_terminal(f"Auto-process/Crawl failed for {prod}: {res.stderr[:50]}", "err")
            except Exception as e:
                self.log_to_terminal(f"Auto-process error ({prod}): {e}", "err")
        threading.Thread(target=_task, daemon=True).start()

    def _trigger_auto_predict_if_needed(self, prod):
        # Read audit log to see if we have pending
        log_path = os.path.join(os.getcwd(), "data", "audit_log.json")
        try:
            with open(log_path, "r", encoding="utf-8") as f: data = json.load(f)
            prod_logs = [x for x in data if x.get('product') == prod]
            has_pending = any(not x.get('checked') for x in prod_logs[:1])
            if not has_pending:
                self.log_to_terminal(f"🎲 AUTO-PILOT: Phát hiện kỳ mới {prod.upper()}. Khởi động dự đoán...", "warn")
                self.start_prediction(prod)
        except: pass

    def update_single_data(self, prod):
        """Update only one product from within its tab"""
        btn = getattr(self, f"btn_{prod}", None)
        if btn: btn.config(state="disabled")
        self.status_var.set(f"🌐 Đang cập nhật dữ liệu {prod.upper()}...")
        
        def _task():
            try:
                import subprocess, sys
                res = subprocess.run(
                    [sys.executable, "src/vietlott/cli/crawl.py", prod, "--index_to", "3"],
                    creationflags=0x08000000, capture_output=True, timeout=60, text=True
                )
                if res.returncode == 0:
                    self.log_to_terminal(f"✅ Đã cập nhật xong dữ liệu {prod}.", "success")
                    self.root.after(0, self.refresh_ui_data)
                    # Trigger silent audit for this product
                    from lstm_predictor import check_audit_log
                    check_audit_log(product_filter=prod)
                else:
                    self.log_to_terminal(f"❌ Lỗi cập nhật {prod}: {res.stderr[:100]}", "err")
            except Exception as e:
                self.log_to_terminal(f"Error ({prod}): {e}", "err")
            finally:
                if btn: self.root.after(0, lambda: btn.config(state="normal"))
        
        threading.Thread(target=_task, daemon=True).start()

    def update_data(self, deep=False, silent=False):
        """Cập nhật dữ liệu toàn bộ hệ thống."""
        if not silent:
            for b in [self.btn_crawl, self.btn_deep, self.btn_audit]:
                if b: 
                    try: b.config(state="disabled")
                    except: pass
            self.status_var.set("🌐 Đang kết nối..." if not deep else "🧬 ULTRA DEEP SYNC ACTIVE...")
        
        idx_to = "300" if deep else "3"
        timeout = 600 if deep else 60
        
        def _crawl():
            import subprocess, sys
            success_count = 0
            error_msgs = []
            try:
                prods = [
                    ("power_655", idx_to), ("power_645", idx_to),
                    ("max3d", idx_to), ("max3d_pro", idx_to),
                    ("keno", "2" if not deep else "20"),
                    ("bingo18", "2" if not deep else "20"),
                    ("lotto", idx_to)
                ]

                for p_id, p_idx in prods:
                    self.root.after(0, lambda p=p_id: self.status_var.set(f"🌐 Đang cào {p}..."))
                    try:
                        result = subprocess.run(
                            [sys.executable, "src/vietlott/cli/crawl.py", p_id, "--index_to", p_idx], 
                            creationflags=0x08000000, capture_output=True, timeout=timeout, text=True
                        )
                        if result.returncode == 0: success_count += 1
                        else: error_msgs.append(f"{p_id}: Error")
                    except Exception: error_msgs.append(f"{p_id}: Timeout")

                self.root.after(0, self.refresh_ui_data)
                if success_count > 0:
                     threading.Thread(target=self.run_audit, daemon=True).start()

                msg = f"✅ Đồng bộ hoàn tất {success_count}/7 game."
                self.log_to_terminal(msg, "success" if success_count==7 else "warn")
                if not silent:
                    self.root.after(0, lambda m=msg: messagebox.showinfo("Kết quả Sync", m))
                
            except Exception as e:
                self.log_to_terminal(f"Crawl Error: {e}", "err")
            finally:
                self.root.after(0, self._enable_all_system_buttons)
                self.is_busy = False

        threading.Thread(target=_crawl, daemon=True).start()

    def _enable_all_system_buttons(self):
        btns = [self.btn_crawl, self.btn_deep, self.btn_audit, self.btn_ultra, self.btn_bias]
        for b in btns:
            try: b.config(state="normal")
            except: pass

    def deep_sync(self):
        msg = "🚀 BẬT CHẾ ĐỘ ULTRA DEEP SYNC?\n\n- Hệ thống sẽ cào ~3000 kỳ quay.\n- Cung cấp dữ liệu từ 2017 - nay cho AI.\n- Bạn đồng ý?"
        if messagebox.askyesno("Xác nhận", msg):
            self.update_data(deep=True)

    def run_audit(self):
        """Kiểm tra kết quả dự đoán toàn cục"""
        # Disable buttons directly without hasattr check on objects
        for b in [self.btn_audit, self.btn_crawl]:
            try: b.config(state="disabled")
            except: pass
            
        self.status_var.set("🔍 Đang đối soát toàn bộ dự đoán...")
        
        def _audit():
            try:
                from lstm_predictor import check_audit_log
                check_audit_log()
                self.root.after(0, lambda: self.status_var.set("✅ Đã đối soát xong!"))
                self.root.after(0, self.refresh_ui_data)
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"❌ Lỗi: {str(e)[:50]}"))
            finally:
                self.root.after(0, self._enable_all_system_buttons)
        
        threading.Thread(target=_audit, daemon=True).start()

    def run_ultra_prediction(self):
        """Chạy module Ultra Predictor v2.0 - Thuật toán siêu cấp"""
        
        # Ask for product type
        dialog = tk.Toplevel(self.root)
        dialog.title("ULTRA PREDICTOR v2.0")
        dialog.geometry("350x220")
        dialog.configure(bg="#0d0d2b")
        dialog.transient(self.root)
        dialog.grab_set()
        
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        geo_str = f"+{root_x + root_w//2 - 175}+{root_y + root_h//2 - 110}"
        dialog.geometry(geo_str)
        
        choice_var = tk.StringVar(value="")
        mode_var = tk.BooleanVar(value=True)
        
        tk.Label(dialog, text="🏆 ULTRA PREDICTOR v2.0", fg="#ffd700", bg="#0d0d2b", font=("Arial", 14, "bold")).pack(pady=8)
        tk.Label(dialog, text="Ensemble AI + Hot Zone + Coverage", fg="#aaa", bg="#0d0d2b", font=("Arial", 9)).pack()
        
        tk.Label(dialog, text="Chọn loại vé:", fg="#fff", bg="#0d0d2b", font=("Arial", 10)).pack(pady=(10, 5))
        
        def set_choice(val):
            choice_var.set(val)
            dialog.destroy()
        
        ttk.Button(dialog, text="🔴 Mega 6/45 (ULTRA)", command=lambda: set_choice("power_645")).pack(fill="x", padx=30, pady=3)
        ttk.Button(dialog, text="🟠 Power 6/55 (ULTRA)", command=lambda: set_choice("power_655")).pack(fill="x", padx=30, pady=3)
        
        tk.Checkbutton(dialog, text="Sử dụng AI Ensemble (chờ 2-3 phút)", variable=mode_var, fg="#ccc", bg="#0d0d2b", selectcolor="#1a1a3a", font=("Arial", 9)).pack(pady=5)
        
        self.root.wait_window(dialog)
        selected_prod = choice_var.get()
        
        if not selected_prod:
            return
        
        # Check for unchecked predictions
        log_path = os.path.join(os.getcwd(), "data", "audit_log.json")
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                p_list = [e for e in data if e['product'] == selected_prod or e['product'] == selected_prod.replace("_","")]
                if p_list and not p_list[-1].get('checked', False):
                    prod_name = "Mega 6/45" if "645" in selected_prod else "Power 6/55"
                    msg = f"⚠️ Đã có dự đoán cho {prod_name} chưa được kiểm tra!\n\n"
                    msg += "Vui lòng: Cập nhật dữ liệu → Kiểm tra dự đoán → Rồi soi tiếp!"
                    messagebox.showwarning("Chưa kiểm tra dự đoán cũ!", msg)
                    return
            except Exception as e:
                self.log_to_terminal(f"Error checking audit log: {e}", "err")
        
        # Run Ultra Prediction
        self.btn_ultra.config(state="disabled")
        use_ai = mode_var.get()
        prod_name = "Mega 6/45" if "645" in selected_prod else "Power 6/55"
        mode_str = "AI Ensemble" if use_ai else "Thống kê nhanh"
        self.status_var.set(f"🏆 ULTRA: Đang phân tích {prod_name} ({mode_str})...")
        
        def _run():
            try:
                # Import here to avoid circular dependencies
                from ultra_predictor import UltraPredictor
                ultra_p = UltraPredictor(selected_prod)
                
                self.log_to_terminal(f">>> RUNNING ULTRA V3.0 FOR {selected_prod.upper()}...", "warn")
                self.log_to_terminal(">>> MODELS: BiLSTM | Transformer | GRU Ensemble", "info")
                self.log_to_terminal(">>> SIGNALS: 7-Signal Scorer + Machine Bias + Hot Zone", "info")
                
                # Run the prediction
                report, tickets = ultra_p.run_ultra_prediction(use_ai=use_ai, gui_callback=self.log_to_terminal)
                
                self.log_to_terminal(f">>> ULTRA PREDICTION FINISHED. FOUND {len(tickets)} OPTIMIZED SETS.", "success")
                self.root.after(0, lambda: self._show_report(report))
                self.root.after(0, lambda: self.status_var.set(f"✅ ULTRA hoàn tất! {len(tickets)} bộ số tối ưu."))
                
                if tickets:
                    def ask_save():
                        if messagebox.askyesno("🏆 Chốt số ULTRA?",
                                             f"Hệ thống ULTRA đã tìm thấy {len(tickets)} bộ số tối ưu cho {prod_name}.\n\n"
                                             f"Chiến lược: {'Ensemble AI + ' if use_ai else ''}7-Signal Scoring + Hot Zone + Coverage\n\n"
                                             "Bạn có muốn chốt làm DỰ ĐOÁN CHÍNH THỨC?"):
                            try:
                                from lstm_predictor import log_predictions
                                log_predictions(selected_prod, tickets)
                                self.refresh_ui_data()
                                messagebox.showinfo("Thành công", f"✅ Đã lưu {len(tickets)} bộ số ULTRA vào lịch sử dự báo!")
                            except Exception as log_err:
                                messagebox.showerror("Lỗi lưu", str(log_err))
                    
                    self.root.after(0, ask_save)
                
                self.root.after(0, lambda: self.btn_ultra.config(state="normal"))
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                self.root.after(0, lambda: self.status_var.set(f"❌ Lỗi: {str(e)[:60]}"))
                self.root.after(0, lambda m=f"❌ Lỗi ULTRA:\n\n{str(e)}\n\n{error_detail[-300:]}": messagebox.showerror("Lỗi", m))
                self.root.after(0, lambda: self.btn_ultra.config(state="normal"))
        
        threading.Thread(target=_run, daemon=True).start()
        

    def run_reverse_engineering(self):
        """Chạy module Reverse Engineering"""
        
        # 1. Ask for product type
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
        
        if not selected_prod: return
        
        # 2. Run Analysis
        self.btn_reverse.config(state="disabled")
        prod_name = "Mega 6/45" if "645" in selected_prod else "Power 6/55"
        self.status_var.set(f"🧠 Đang phân tích chuyên sâu {prod_name} (chờ 1-2 phút)...")
        
        def _run():
            try:
                # Dynamic import
                try:
                    import reverse_engineering as re_engine
                except ImportError:
                    # Fallback for nested stricture if needed, though PYTHONPATH handles it
                    sys.path.append(os.path.join(os.getcwd(), 'src', 'vietlott', 'predictor'))
                    import reverse_engineering as re_engine

                # Run analysis
                self.log_to_terminal(f">>> STARTING REVERSE ENGINEERING FOR {prod_name}...", "info")
                report, tickets = re_engine.run_analysis_and_get_report(selected_prod)
                
                # Show report
                self.root.after(0, lambda: self._show_report(report))
                self.root.after(0, lambda: self.status_var.set(f"✅ Đã xong! Tìm thấy {len(tickets)} bộ số tối ưu."))
                
                # 3. Ask to SAVE predictions
                if tickets:
                    def ask_save():
                        if messagebox.askyesno("Chốt số RE?", 
                                             f"Reverse Engineering đã tìm thấy {len(tickets)} bộ số tối ưu.\n\n"
                                             "Bạn có muốn dùng chúng làm DỰ ĐOÁN CHÍNH THỨC kỳ này?"):
                             try:
                                 from lstm_predictor import log_predictions
                                 log_predictions(selected_prod, tickets)
                                 self.refresh_ui_data()
                                 messagebox.showinfo("Thành công", "Đã lưu bộ số Reverse Engineering vào lịch sử!")
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
        """Hiển thị bảng thống kê hiệu suất bằng các thẻ (Cards) trực quan"""
        try:
            from lstm_predictor import get_detailed_stats
            
            # Clear container
            for widget in self.stat_container.winfo_children(): widget.destroy()
            
            prods_to_check = [
                ("power_655", "POWER 6/55"),
                ("power_645", "MEGA 6/45"),
                ("max3d", "MAX 3D"),
                ("max3d_pro", "MAX 3D PRO"),
                ("keno", "KENO"),
                ("lotto", "LOTTO"),
                ("bingo18", "BINGO 18")
            ]
            
            for i, (pk, name) in enumerate(prods_to_check):
                stats = get_detailed_stats(pk)
                
                # Create Card Frame
                card = tk.Frame(self.stat_container, bg="#1a1a2e", padx=15, pady=10, highlightbackground="#333", highlightthickness=1)
                card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
                
                tk.Label(card, text=name, font=("Segoe UI", 11, "bold"), fg="#00fff2", bg="#1a1a2e").pack(anchor="w")
                
                if stats:
                    wr = stats['win_rate']
                    color = "#00ff88" if wr > 20 else "#ffcc00" if wr > 5 else "#ff4d4d"
                    
                    tk.Label(card, text=f"{wr}%", font=("Impact", 24), fg=color, bg="#1a1a2e").pack(pady=5)
                    tk.Label(card, text="TỶ LỆ THẮNG", font=("Segoe UI", 7), fg="#666", bg="#1a1a2e").pack()
                    
                    info_f = tk.Frame(card, bg="#1a1a2e")
                    info_f.pack(fill="x", pady=5)
                    tk.Label(info_f, text=f"Kỳ quay: {stats['total_draws']}", font=("Segoe UI", 8), fg="#ccc", bg="#1a1a2e").pack(side="left")
                    tk.Label(info_f, text=f" | Vé trúng: {stats['wins']}", font=("Segoe UI", 8), fg="#00ff88", bg="#1a1a2e").pack(side="left")
                else:
                    tk.Label(card, text="N/A", font=("Impact", 24), fg="#444", bg="#1a1a2e").pack(pady=5)
                    tk.Label(card, text="CHƯA CÓ DỮ LIỆU", font=("Segoe UI", 8), fg="#666", bg="#1a1a2e").pack()

            self.status_var.set("✅ Đã cập nhật thống kê hiệu suất dạng thẻ.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo thống kê: {str(e)}")

    def show_extended_history(self):
        """Hiển thị lịch sử các sản phẩm mở rộng (Keno, Bingo, Max3D)"""
        top = tk.Toplevel(self.root)
        top.title("LỊCH SỬ DỰ ĐOÁN MỞ RỘNG (Keno, Bingo18, Max3D)")
        top.geometry("700x500")
        top.configure(bg="#1a1a1a")
        
        txt = tk.Text(top, font=("Consolas", 10), bg="#000", fg="#00ff88", padx=10, pady=10)
        txt.pack(fill="both", expand=True)
        
        try:
            log_path = os.path.join(os.getcwd(), "data", "audit_log.json")
            if not os.path.exists(log_path):
                txt.insert(tk.END, "Chưa có dữ liệu lịch sử.")
                return
                
            with open(log_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Filter non-Power/Mega
            others = [e for e in data if e['product'] not in ['power_655', 'power_645', 'power655', 'power645']]
            
            if not others:
                txt.insert(tk.END, "Chưa có dự đoán nào cho Keno/Bingo/Max3D.\nHãy chạy 'System Reset' hoặc các tool chuyên biệt.")
                return
            
            txt.insert(tk.END, "📜 DANH SÁCH DỰ ĐOÁN MỚI NHẤT\n")
            txt.insert(tk.END, "========================================\n\n")
            
            for e in reversed(others):
                prod = e.get('product', '').upper().replace('_', ' ')
                ts = e.get('date', 'N/A')
                algo = e.get('strategy', 'N/A')
                pred = e.get('prediction', '')
                
                txt.insert(tk.END, f"🔹 [{prod}] - {ts}\n")
                txt.insert(tk.END, f"   Chiến thuật: {algo}\n")
                txt.insert(tk.END, f"   DỰ ĐOÁN: {pred}\n")
                
                tickets = e.get('tickets', [])
                if tickets and len(tickets) > 0:
                     txt.insert(tk.END, f"   Chi tiết vé:\n")
                     for i, t in enumerate(tickets[:5]): # Show max 5
                         t_str = str(t)
                         txt.insert(tk.END, f"     {i+1}. {t_str}\n")
                
                txt.insert(tk.END, "-" * 40 + "\n")
                
            txt.config(state="disabled")
            
        except Exception as e:
            txt.insert(tk.END, f"Lỗi đọc dữ liệu: {e}")


    # --- ENHANCED PREDICTION METHODS ---
    # --- ENHANCED PREDICTION METHODS ---
    def predict_keno(self):
        btn = getattr(self, "btn_keno", None)
        if btn: btn.config(state="disabled")
        self.status_var.set("🤖 Đang tính toán Keno RE Bias...")
        threading.Thread(target=self._run_keno, daemon=True).start()

    def _run_keno(self):
        try:
            from keno_predictor import get_current_time_slot, get_hot_numbers_by_slot
            import random
            
            slot_key, slot_name = get_current_time_slot()
            hot_nums = get_hot_numbers_by_slot(slot_key)
            
            tickets = []
            for _ in range(3):
                t = sorted(hot_nums[:6] + random.sample(hot_nums[6:20], 4))
                tickets.append(t)
            
            p_str = " ".join([f"{n:02d}" for n in tickets[0]])
            self._save_custom_log("keno", tickets, p_str, f"RE Time Bias ({slot_key})")
            
            def _up():
                res_box = getattr(self, "res_keno", None)
                if res_box:
                    res_box.config(state="normal"); res_box.delete("1.0", tk.END)
                    res_box.insert(tk.END, f"🎯 DỰ ĐOÁN BẬC 10 ({slot_key.upper()}):\n")
                    for i, t in enumerate(tickets):
                        res_box.insert(tk.END, f"Vé {i+1}: {' '.join([f'{n:02d}' for n in t])}\n")
                    res_box.config(state="disabled")
                
                self.refresh_ui_data()
                btn = getattr(self, "btn_keno", None)
                if btn: btn.config(state="normal")
                self.status_var.set("✅ Keno đã chốt bộ số!")
                messagebox.showinfo("Keno Success", f"Đã chốt 3 bộ Keno Bậc 10 khung {slot_name}!")

            self.root.after(0, _up)
        except Exception as e:
            btn = getattr(self, "btn_keno", None)
            if btn: self.root.after(0, lambda: btn.config(state="normal"))

    def predict_max3d(self):
        btn = getattr(self, "btn_max3d_pro", None)
        if btn: btn.config(state="disabled")
        self.status_var.set("🤖 Đang tính toán cặp số Max 3D Pro...")
        threading.Thread(target=self._run_max3d, daemon=True).start()

    def _run_max3d(self):
        try:
            from max3d_bingo_predictor import predict_max3d_pro
            tickets = predict_max3d_pro()
            
            p_str = f"{tickets[0][0]}-{tickets[0][1]}"
            self._save_custom_log("max3d_pro", tickets, p_str, "Machine Bias Correction")
            
            def _up():
                res_box = getattr(self, "res_max3d_pro", None)
                if res_box:
                    res_box.config(state="normal"); res_box.delete("1.0", tk.END)
                    res_box.insert(tk.END, "🎯 CẶP SỐ MAX 3D PRO:\n")
                    for i, t in enumerate(tickets[:3]):
                        res_box.insert(tk.END, f"Cặp {i+1}: {t[0]} - {t[1]}\n")
                    res_box.config(state="disabled")
                
                self.refresh_ui_data()
                btn = getattr(self, "btn_max3d_pro", None)
                if btn: btn.config(state="normal")
                self.status_var.set("✅ Max 3D Pro đã chốt cặp số!")
                messagebox.showinfo("Max 3D Pro", "Đã chốt các cặp số Max 3D Pro mới!")

            self.root.after(0, _up)
        except Exception as e:
            btn = getattr(self, "btn_max3d_pro", None)
            if btn: self.root.after(0, lambda: btn.config(state="normal"))

    def predict_max3d_plus(self):
        # Redirect to generic max3d if needed or use its own
        self.predict_max3d()

    def predict_bingo(self):
        btn = getattr(self, "btn_bingo18", None)
        if btn: btn.config(state="disabled")
        self.status_var.set("🤖 Đang phân tích Bingo18...")
        threading.Thread(target=self._run_bingo, daemon=True).start()

    def _run_bingo(self):
        try:
            from max3d_bingo_predictor import predict_bingo18
            import random
            res = predict_bingo18()
            
            def gen_bingo_num(is_tai):
                while True:
                    nums = [random.randint(1,6) for _ in range(3)]
                    s = sum(nums)
                    if (is_tai and s > 10) or (not is_tai and s <= 10): return nums

            is_tai = res['tai_xiu'] == "Tài"
            tickets = [gen_bingo_num(is_tai) for _ in range(3)]
            p_str = f"{res['tai_xiu']} ({res['sum_range']})"
            self._save_custom_log("bingo18", tickets, p_str, res['desc'])
            
            def _up():
                res_box = getattr(self, "res_bingo18", None)
                if res_box:
                    res_box.config(state="normal"); res_box.delete("1.0", tk.END)
                    res_box.insert(tk.END, f"🎯 DỰ BÁO: {res['tai_xiu']} ({res['sum_range']})\n")
                    res_box.insert(tk.END, f"💡 Gợi ý bộ 3 số:\n")
                    for i, t in enumerate(tickets):
                        res_box.insert(tk.END, f"   {i+1}. {'-'.join(map(str, t))}\n")
                    res_box.config(state="disabled")
                
                self.refresh_ui_data()
                btn = getattr(self, "btn_bingo18", None)
                if btn: btn.config(state="normal")
                self.status_var.set("✅ Bingo18 đã hoàn thành dự báo!")
                messagebox.showinfo("Bingo18", f"Dự báo: {res['tai_xiu']}\nCơ sở: {res['desc']}")

            self.root.after(0, _up)
        except Exception as e:
            btn = getattr(self, "btn_bingo18", None)
            if btn: self.root.after(0, lambda: btn.config(state="normal"))

    def predict_max3d_basic(self):
        btn = getattr(self, "btn_max3d", None)
        if btn: btn.config(state="disabled")
        self.status_var.set("🤖 Đang tính toán Max 3D...")
        threading.Thread(target=self._run_max3d_basic, daemon=True).start()

    def _run_max3d_basic(self):
        try:
            from max3d_bingo_predictor import predict_max3d
            pairs = predict_max3d("max3d") 
            tickets = [p[0] for p in pairs]
            self._save_custom_log("max3d", tickets, tickets[0], "Statistical Pair Extraction")
            
            def _up():
                res_box = getattr(self, "res_max3d", None)
                if res_box:
                    res_box.config(state="normal"); res_box.delete("1.0", tk.END)
                    res_box.insert(tk.END, f"🎯 TOP 5 BỘ SỐ MAX 3D:\n{'-'*30}\n")
                    for i, t in enumerate(tickets):
                        res_box.insert(tk.END, f"  Bộ {i+1}: {t}\n")
                    res_box.config(state="disabled")
                
                self.refresh_ui_data()
                btn = getattr(self, "btn_max3d", None)
                if btn: btn.config(state="normal")
                self.status_var.set("✅ Max 3D đã hoàn thành dự phòng!")
            
            self.root.after(0, _up)
        except:
            btn = getattr(self, "btn_max3d", None)
            if btn: self.root.after(0, lambda: btn.config(state="normal"))

    def _save_custom_log(self, prod, tickets, pred_str, strat):
        path = os.path.join(os.getcwd(), "data", "audit_log.json")
        data = []
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f: data = json.load(f)
            except: data = []
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        target_id = self.get_target_draw_id(prod)
        
        entry = {
            "product": prod,
            "date": now,
            "timestamp": now,
            "target_draw_id": target_id,
            "prediction": pred_str,
            "predictions": tickets, 
            "tickets": tickets,
            "strategy": strat,
            "result": None,
            "checked": False
        }
        data.append(entry)
        with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

    def run_bias_analysis(self):
        self.log_to_terminal(">>> ĐANG KIỂM TRA BIAS TOÀN HỆ THỐNG...", "warn")
        self.status_var.set("🧬 AI đang quét mẫu số liệu (Bias Detection)...")
        
        def _task():
            try:
                import subprocess, sys, os
                my_env = os.environ.copy()
                my_env["PYTHONPATH"] = "src"
                
                result = subprocess.run(
                    [sys.executable, "src/vietlott/bias_analyzer.py"],
                    capture_output=True, text=True, encoding='utf-8', creationflags=0x08000000,
                    env=my_env
                )
                report = result.stdout
                if result.stderr:
                    report += f"\n--- Error Log ---\n{result.stderr}"
                
                if not report.strip():
                    report = "⚠️ Không có dữ liệu phản hồi từ script phân tích."
                
                def _up():
                    self.log_to_terminal("✅ PHÂN TÍCH BIAS HOÀN TẤT.", "success")
                    # Show in a popup or terminal
                    from tkinter import scrolledtext
                    top = tk.Toplevel(self.root)
                    top.title("BÁO CÁO PHÂN TÍCH BIAS (DỊ THƯỜNG)")
                    top.geometry("700x500")
                    top.configure(bg="#0a0a1a")
                    
                    st = scrolledtext.ScrolledText(top, bg="#000", fg="#00ff88", font=("Consolas", 10))
                    st.pack(fill="both", expand=True, padx=10, pady=10)
                    st.insert(tk.END, report)
                    st.config(state="disabled")
                    
                    self.status_var.set("✅ Phân tích Bias hoàn tất.")
                
                self.root.after(0, _up)
            except Exception as e:
                self.log_to_terminal(f"Bias Error: {e}", "err")

        threading.Thread(target=_task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    app = VietlottGUI(root); root.mainloop()

