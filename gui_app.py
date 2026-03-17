# gui_app.py
import tkinter as tk
from tkinter import ttk, messagebox
try:
    import cv2
except Exception:
    cv2 = None

try:
    import numpy as np
except Exception:
    np = None

try:
    from PIL import Image, ImageTk, ImageDraw
except Exception:
    Image = None
    ImageTk = None
    ImageDraw = None

import time

class IronDomeGUI:
    def __init__(self, root, detector, tracker, launcher, config):
        self.root = root
        self.detector = detector
        self.tracker = tracker
        self.launcher = launcher
        self.config = config
        self.preview_size = (420, 290)
        self.heatmap_size = (460, 320)
        min_window_width = self.preview_size[0] + self.heatmap_size[0] + 80
        window_width = max(config.WINDOW_WIDTH, min_window_width)
        
        self.root.title("Shield System AI")
        self.root.geometry(f"{window_width}x{config.WINDOW_HEIGHT}")
        self.root.minsize(window_width, config.WINDOW_HEIGHT)
        self.root.configure(bg="#111827")
        
        # Biến trạng thái
        self.is_running = False
        self.is_tracking = False
        self.camera = None
        self.current_frame = None
        self.last_fire_time = 0.0
        self.fire_cooldown = getattr(config, "FIRE_COOLDOWN_SECONDS", 1.0)
        self.launcher.missile_speed = getattr(config, "MISSILE_SPEED", self.launcher.missile_speed)
        self.auto_fire_var = tk.BooleanVar(value=True)
        self.auto_fire_label_var = tk.StringVar()
        self.ai_direction_var = tk.StringVar(value="Đang chờ mục tiêu")
        self.ai_velocity_var = tk.StringVar(value="0.0 px/frame")
        self.ai_prediction_var = tk.StringVar(value="Chưa có dữ liệu")
        self.ai_fire_rate_var = tk.StringVar(value=f"1 tên lửa / {self.fire_cooldown:.1f}s")
        self.ai_decision_var = tk.StringVar(value="AI đang ở chế độ giám sát")

        self.setup_styles()
        self.setup_ui()
        self.update_auto_fire_button()
        self.update_ai_status_panel()
        if cv2 is None:
            self.add_status("Thiếu thư viện opencv-python: tạm tắt camera.")
        if Image is None or ImageTk is None:
            self.add_status("Thiếu thư viện Pillow: không thể hiển thị frame camera.")

    def setup_styles(self):
        """Thiết lập style giúp giao diện hiện đại và dễ thao tác hơn."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("App.TFrame", background="#111827")
        self.style.configure("Card.TFrame", background="#1f2937")
        self.style.configure("CardTitle.TLabel", background="#1f2937", foreground="#f3f4f6", font=("Segoe UI", 11, "bold"))
        self.style.configure("CardSubtitle.TLabel", background="#1f2937", foreground="#9ca3af", font=("Segoe UI", 10))
        self.style.configure("MetricLabel.TLabel", background="#1f2937", foreground="#94a3b8", font=("Segoe UI", 10, "bold"))
        self.style.configure("MetricValue.TLabel", background="#1f2937", foreground="#f8fafc", font=("Segoe UI", 13, "bold"))
        self.style.configure("MetricNote.TLabel", background="#1f2937", foreground="#cbd5e1", font=("Segoe UI", 10), wraplength=420, justify="left")
        self.style.configure(
            "Title.TLabel",
            background="#111827",
            foreground="#f9fafb",
            font=("Segoe UI", 18, "bold")
        )
        self.style.configure(
            "Subtitle.TLabel",
            background="#111827",
            foreground="#9ca3af",
            font=("Segoe UI", 10)
        )
        self.style.configure(
            "TLabelframe",
            background="#1f2937",
            foreground="#e5e7eb",
            borderwidth=1,
            relief="solid"
        )
        self.style.configure(
            "TLabelframe.Label",
            background="#1f2937",
            foreground="#f3f4f6",
            font=("Segoe UI", 11, "bold")
        )
        self.style.configure(
            "Primary.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=(14, 10),
            background="#2563eb",
            foreground="#ffffff",
            borderwidth=0
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", "#1d4ed8"), ("disabled", "#374151")],
            foreground=[("disabled", "#9ca3af")]
        )
        self.style.configure(
            "Accent.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=(14, 10),
            background="#16a34a",
            foreground="#ffffff",
            borderwidth=0
        )
        self.style.map(
            "Accent.TButton",
            background=[("active", "#15803d"), ("disabled", "#374151")],
            foreground=[("disabled", "#9ca3af")]
        )
        self.style.configure(
            "Danger.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=(14, 10),
            background="#dc2626",
            foreground="#ffffff",
            borderwidth=0
        )
        self.style.map(
            "Danger.TButton",
            background=[("active", "#b91c1c")]
        )
        self.style.configure(
            "Warning.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=(14, 10),
            background="#f59e0b",
            foreground="#111827",
            borderwidth=0
        )
        self.style.map(
            "Warning.TButton",
            background=[("active", "#d97706")]
        )
        self.style.configure(
            "TCheckbutton",
            background="#111827",
            foreground="#e5e7eb",
            font=("Segoe UI", 11, "bold")
        )
        
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Frame chính
        main_frame = ttk.Frame(self.root, style="App.TFrame", padding="14")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame, style="App.TFrame")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Label(header_frame, text="Shield System AI - Bang dieu khien", style="Title.TLabel").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(
            header_frame,
            text="Theo doi muc tieu theo thoi gian thuc va dieu khien phong thu",
            style="Subtitle.TLabel"
        ).grid(row=1, column=0, sticky=tk.W)
        
        # Khu vực hiển thị camera
        video_frame = ttk.LabelFrame(main_frame, text="Camera Feed", padding="8")
        video_frame.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        video_frame.columnconfigure(0, weight=1, uniform="video-split")
        video_frame.columnconfigure(1, weight=1, uniform="video-split")
        video_frame.rowconfigure(0, weight=1)
        
        self.video_label = ttk.Label(
            video_frame,
            anchor="center",
            text="Khung camera preview",
            style="Subtitle.TLabel"
        )
        self.video_label.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(0, 10))

        ai_top_panel = ttk.Frame(video_frame, style="Card.TFrame", padding=(16, 14, 16, 14))
        ai_top_panel.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.W, tk.E))
        ai_top_panel.columnconfigure(1, weight=1)

        ttk.Label(ai_top_panel, text="AI DỰ ĐOÁN HƯỚNG DI CHUYỂN",
                  style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 14))

        metrics = [
            ("Hướng di chuyển",  self.ai_direction_var,  1),
            ("Vận tốc mục tiêu", self.ai_velocity_var,   2),
            ("Vị trí dự đoán",   self.ai_prediction_var, 3),
            ("Nhịp bắn an toàn", self.ai_fire_rate_var,  4),
        ]
        for label_text, var, row in metrics:
            ttk.Label(ai_top_panel, text=label_text,
                      style="MetricLabel.TLabel").grid(row=row, column=0, sticky=tk.W, padx=(0, 16), pady=(0, 10))
            ttk.Label(ai_top_panel, textvariable=var,
                      style="MetricValue.TLabel").grid(row=row, column=1, sticky=tk.W, pady=(0, 10))

        ttk.Label(ai_top_panel, text="Đánh giá AI",
                  style="MetricLabel.TLabel").grid(row=5, column=0, sticky=(tk.N, tk.W), padx=(0, 16))
        ttk.Label(ai_top_panel, textvariable=self.ai_decision_var,
                  style="MetricNote.TLabel").grid(row=5, column=1, sticky=(tk.W, tk.E))

        self.heatmap_label = None
        
        # Thanh điều khiển
        control_frame = ttk.Frame(main_frame, style="App.TFrame")
        control_frame.grid(row=1, column=0, pady=(6, 8), sticky=(tk.W, tk.E))
        for i in range(4):
            control_frame.columnconfigure(i, weight=1)
        
        self.start_btn = ttk.Button(
            control_frame,
            text="Kết nối Camera",
            command=self.toggle_camera,
            style="Primary.TButton",
            width=20
        )
        self.start_btn.grid(row=0, column=0, padx=6, pady=2, sticky=(tk.W, tk.E))
        
        self.track_btn = ttk.Button(
            control_frame,
            text="Bắt đầu theo dõi",
            command=self.toggle_tracking,
            state='disabled',
            style="Accent.TButton",
            width=20
        )
        self.track_btn.grid(row=0, column=1, padx=6, pady=2, sticky=(tk.W, tk.E))

        self.auto_fire_btn = tk.Checkbutton(
            control_frame,
            variable=self.auto_fire_var
            ,textvariable=self.auto_fire_label_var,
            command=self.toggle_auto_fire,
            indicatoron=False,
            bd=0,
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=16,
            pady=10,
            cursor="hand2",
            highlightthickness=0,
            selectcolor="#111827"
        )
        self.auto_fire_btn.grid(row=0, column=2, padx=6, pady=2, sticky=(tk.W, tk.E))
        
        self.quit_btn = ttk.Button(
            control_frame,
            text="Thoát",
            command=self.quit_app,
            style="Danger.TButton",
            width=16
        )
        self.quit_btn.grid(row=0, column=3, padx=6, pady=2, sticky=(tk.W, tk.E))
        
        # Khu vực trạng thái hệ thống (nhỏ, full-width)
        info_frame = ttk.LabelFrame(main_frame, text="Trạng thái hệ thống", padding="6")
        info_frame.grid(row=3, column=0, pady=(4, 0), sticky=(tk.W, tk.E))
        info_frame.columnconfigure(0, weight=1)

        self.status_text = tk.Text(
            info_frame,
            height=11,
            bg="#0f172a",
            fg="#e2e8f0",
            insertbackground="#f8fafc",
            relief="flat",
            font=("Consolas", 10),
            wrap="word"
        )
        self.status_text.grid(row=0, column=0, padx=4, pady=4, sticky=(tk.W, tk.E))

        scrollbar = ttk.Scrollbar(info_frame, orient='vertical',
                                  command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), pady=4)
        self.status_text.configure(yscrollcommand=scrollbar.set)

        self.add_status("Hệ thống đã sẵn sàng. Nhấn 'Kết nối Camera' để bắt đầu.")
        
    def add_status(self, message):
        """Thêm thông báo vào khung trạng thái"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)

    def toggle_auto_fire(self):
        """Cập nhật giao diện và trạng thái tự động khai hỏa."""
        self.update_auto_fire_button()
        mode = "Đã bật" if self.auto_fire_var.get() else "Đã tắt"
        self.update_ai_status_panel(note=f"{mode} chế độ tự động khai hỏa")

    def update_auto_fire_button(self):
        """Làm mới giao diện nút tự động khai hỏa."""
        is_enabled = self.auto_fire_var.get()
        self.auto_fire_label_var.set("Tự động khai hỏa: BẬT" if is_enabled else "Tự động khai hỏa: TẮT")
        self.auto_fire_btn.configure(
            bg="#0f766e" if is_enabled else "#334155",
            fg="#f8fafc",
            activebackground="#115e59" if is_enabled else "#1e293b",
            activeforeground="#f8fafc"
        )

    def update_ai_status_panel(self, target=None, predicted_pos=None, note=None):
        """Cập nhật bảng dự đoán AI ở nửa phải phía dưới."""
        if target is None:
            cooldown_remaining = max(0.0, self.fire_cooldown - (time.time() - self.last_fire_time))
            self.ai_direction_var.set("Đang chờ mục tiêu")
            self.ai_velocity_var.set("0.0 px/frame")
            self.ai_prediction_var.set("Chưa có dữ liệu")
            self.ai_fire_rate_var.set(f"1 tên lửa / {self.fire_cooldown:.1f}s | chờ {cooldown_remaining:.1f}s")
            self.ai_decision_var.set(note or "AI đang quét mục tiêu và học chuyển động")
            return

        velocity = target.get('velocity', (0, 0))
        speed = float(np.linalg.norm(velocity)) if np is not None else 0.0
        direction = self.describe_direction()
        prediction_text = f"({predicted_pos[0]}, {predicted_pos[1]})" if predicted_pos else "Đang nội suy thêm"
        cooldown_remaining = max(0.0, self.fire_cooldown - (time.time() - self.last_fire_time))
        cooldown_text = "sẵn sàng" if cooldown_remaining == 0 else f"chờ {cooldown_remaining:.1f}s"

        self.ai_direction_var.set(direction.upper())
        self.ai_velocity_var.set(f"{speed:.1f} px/frame")
        self.ai_prediction_var.set(prediction_text)
        self.ai_fire_rate_var.set(f"1 tên lửa / {self.fire_cooldown:.1f}s | {cooldown_text}")
        self.ai_decision_var.set(note or "Mục tiêu đang được theo dõi liên tục")
        
    def toggle_camera(self):
        """Kết nối/ngắt kết nối camera"""
        if cv2 is None:
            messagebox.showerror("Thiếu thư viện", "Chưa cài opencv-python. Hãy cài trước khi mở camera.")
            return

        if not self.is_running:
            try:
                source = self.config.CAMERA_URL
                if isinstance(source, str) and source.isdigit():
                    source = int(source)

                self.camera = cv2.VideoCapture(source)

                # Fallback: neu nguon cau hinh loi, thu webcam laptop mac dinh.
                if not self.camera.isOpened() and source != 0:
                    self.camera.release()
                    self.camera = cv2.VideoCapture(0)

                # Thu camera thu 2 neu camera 0 khong san sang.
                if not self.camera.isOpened() and source != 1:
                    self.camera.release()
                    self.camera = cv2.VideoCapture(1)

                if self.camera.isOpened():
                    self.is_running = True
                    self.start_btn.config(text="Ngắt kết nối")
                    self.track_btn.config(state='normal', text="Bắt đầu theo dõi", style="Accent.TButton")
                    self.add_status("Đã kết nối webcam laptop thành công!")
                    self.update_ai_status_panel(note="Camera đã sẵn sàng, chờ khóa mục tiêu")
                    self.update_frame()
                else:
                    messagebox.showerror("Lỗi", "Không thể kết nối webcam. Thu doi CAMERA_URL = 0 hoac 1 trong config.py")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi kết nối camera: {str(e)}")
        else:
            self.is_running = False
            self.is_tracking = False
            self.tracker.clear()
            if self.camera:
                self.camera.release()
            self.start_btn.config(text="Kết nối Camera")
            self.track_btn.config(state='disabled', text="Bắt đầu theo dõi", style="Accent.TButton")
            self.update_ai_status_panel(note="Camera đã ngắt, AI tạm dừng phân tích")
            self.add_status("Đã ngắt kết nối camera.")

    def toggle_tracking(self):
        """Bật/tắt theo dõi mục tiêu."""
        if not self.is_running:
            self.add_status("Hãy kết nối camera trước khi bật theo dõi.")
            return

        if not self.is_tracking:
            self.is_tracking = True
            self.track_btn.config(text="Tắt theo dõi", style="Warning.TButton")
            self.update_ai_status_panel(note="AI đang học quỹ đạo đối phương")
            self.add_status("Đã bật theo dõi mục tiêu.")
        else:
            self.is_tracking = False
            self.tracker.clear()
            self.track_btn.config(text="Bắt đầu theo dõi", style="Accent.TButton")
            self.update_ai_status_panel(note="Đã tắt theo dõi, AI quay về chế độ giám sát")
            self.add_status("Đã tắt theo dõi mục tiêu.")
        
    def update_frame(self):
        """Cập nhật frame từ camera"""
        if self.is_running:
            if self.camera is None or not self.camera.isOpened():
                self.add_status("Mất kết nối camera.")
                self.toggle_camera()
                return

            ret, frame = self.camera.read()
            if ret:
                self.current_frame = frame.copy()
                
                # Phát hiện và theo dõi mục tiêu
                if self.is_tracking:
                    self.process_targets(frame)
                else:
                    self.update_ai_status_panel(note="Theo dõi đang tắt, chỉ hiển thị camera trực tiếp")
                
                # Vẽ vùng bảo vệ
                self.draw_protected_zone(frame)
                
                # Vẽ bệ phóng
                self.draw_launcher(frame)
                
                # Chuyển đổi frame để hiển thị
                self.display_frame(frame)
                
            # Tiếp tục cập nhật
            self.root.after(30, self.update_frame)
            
    def process_targets(self, frame):
        """Xử lý phát hiện và theo dõi mục tiêu"""
        if not self.tracker.current_target:
            # Phát hiện mục tiêu mới
            detections = self.detector.detect(frame)
            if detections:
                target = detections[0]
                bbox = target['bbox']
                self.tracker.add_tracker(frame, bbox)
                self.update_ai_status_panel(
                    target=self.tracker.current_target,
                    predicted_pos=None,
                    note="Đã khóa mục tiêu, AI đang thu thập thêm quỹ đạo"
                )
                self.add_status(f"Đã phát hiện mục tiêu! Độ tin cậy: {target['confidence']:.2f}")
            else:
                self.update_ai_status_panel(note="AI chưa phát hiện mục tiêu trong khung hình")
        else:
            # Theo dõi mục tiêu hiện tại
            target = self.tracker.update(frame)
            if target:
                # Vẽ bounding box
                x, y, w, h = target['bbox']
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, target['center'], 5, (0, 0, 255), -1)
                
                # Hiển thị vận tốc
                velocity = target['velocity']
                cv2.putText(frame, f"Velocity: ({velocity[0]:.1f}, {velocity[1]:.1f})", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Dự đoán vị trí tương lai
                predicted_pos = self.tracker.predict_future_position()
                if predicted_pos:
                    cv2.circle(frame, predicted_pos, 10, (255, 255, 0), 2)
                    
                # Kiểm tra và khai hỏa
                if self.auto_fire_var.get():
                    note = self.check_and_fire(target, predicted_pos)
                else:
                    note = "Tự động khai hỏa đang tắt, AI chỉ giám sát mục tiêu"

                self.update_ai_status_panel(target=target, predicted_pos=predicted_pos, note=note)
            else:
                self.update_ai_status_panel(note="Mất dấu mục tiêu, AI đang quét lại")
                    
    def draw_protected_zone(self, frame):
        """Vẽ khu vực bảo vệ"""
        pz = self.config.PROTECTED_ZONE
        cv2.rectangle(frame, (pz['x1'], pz['y1']), (pz['x2'], pz['y2']), 
                     (255, 0, 0), 2)
        cv2.putText(frame, "PROTECTED ZONE", (pz['x1'], pz['y1'] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
    def draw_launcher(self, frame):
        """Vẽ bệ phóng tên lửa"""
        cv2.circle(frame, self.launcher.position, 10, (0, 0, 255), -1)
        cv2.putText(frame, "LAUNCHER", 
                   (self.launcher.position[0] - 30, self.launcher.position[1] - 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Vẽ tên lửa đang bay
        for missile in self.launcher.active_missiles:
            if missile.is_active:
                cv2.circle(frame, (int(missile.current_pos[0]), 
                                  int(missile.current_pos[1])), 5, (0, 255, 255), -1)
                # Vẽ đường bay
                for i in range(1, len(missile.trajectory)):
                    cv2.line(frame, missile.trajectory[i-1], missile.trajectory[i], 
                            (0, 255, 255), 1)
            elif missile.has_hit:
                # Vẽ hiệu ứng nổ
                for particle in missile.explosion_particles:
                    if particle['life'] > 0:
                        cv2.circle(frame, (int(particle['pos'][0]), 
                                          int(particle['pos'][1])), 
                                 3, (0, 0, 255), -1)
                        # Cập nhật vị trí hạt
                        particle['pos'][0] += particle['vel'][0]
                        particle['pos'][1] += particle['vel'][1]
                        particle['life'] -= 1
                        
    def check_and_fire(self, target, predicted_pos=None):
        """Kiểm tra và bắn tên lửa nếu cần"""
        predicted_pos = predicted_pos or self.tracker.predict_future_position(frames_ahead=10)
        if not predicted_pos:
            return "Chưa đủ dữ liệu để dự đoán điểm chặn"
            
        pz = self.config.PROTECTED_ZONE
        
        # Kiểm tra nếu mục tiêu đang tiến vào vùng bảo vệ
        if (pz['x1'] <= predicted_pos[0] <= pz['x2'] and 
            pz['y1'] <= predicted_pos[1] <= pz['y2']):
            elapsed = time.time() - self.last_fire_time
            if elapsed < self.fire_cooldown:
                return f"Bệ phóng đang hồi nạp, còn {self.fire_cooldown - elapsed:.1f}s"
            
            # Bắn tên lửa vào vị trí dự đoán
            self.launcher.fire(target['center'])
            self.last_fire_time = time.time()
            self.add_status(f"Đã khai hỏa! Mục tiêu tại {target['center']}")
            return "Đã khai hỏa theo dự đoán AI"
        return "Mục tiêu chưa tiến vào vùng cần đánh chặn"
            
    def display_frame(self, frame):
        """Hiển thị frame lên giao diện"""
        if cv2 is None or Image is None or ImageTk is None:
            return

        w = self.video_label.winfo_width()
        h = self.video_label.winfo_height()
        if w < 10 or h < 10:
            w, h = self.preview_size
        else:
            # Giới hạn nhẹ để camera không quá to trên màn hình lớn.
            w = min(w, self.preview_size[0])
            h = min(h, self.preview_size[1])

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        frame_pil = frame_pil.resize((w, h), Image.Resampling.LANCZOS)

        frame_tk = ImageTk.PhotoImage(frame_pil)
        self.video_label.config(image=frame_tk)
        self.video_label.image = frame_tk

    def update_heatmap(self, frame_shape):
        """Hiển thị heatmap quỹ đạo và hướng di chuyển dự đoán ở bên phải camera."""
        if cv2 is None or np is None or Image is None or ImageTk is None or ImageDraw is None:
            self.heatmap_label.config(text="Thiếu thư viện để dựng heatmap", image="")
            self.heatmap_label.image = None
            return

        hmap_w = self.heatmap_label.winfo_width()
        hmap_h = self.heatmap_label.winfo_height()
        # Fallback to camera label height if heatmap label not yet sized
        if hmap_w < 10:
            hmap_w = self.heatmap_size[0]
        if hmap_h < 10:
            hmap_h = max(self.video_label.winfo_height(), self.heatmap_size[1])

        heatmap = self.build_prediction_heatmap(frame_shape, hmap_w, hmap_h)
        heatmap_tk = ImageTk.PhotoImage(heatmap)
        self.heatmap_label.config(image=heatmap_tk, text="")
        self.heatmap_label.image = heatmap_tk

    def build_prediction_heatmap(self, frame_shape, hmap_w=None, hmap_h=None):
        """Dựng heatmap từ lịch sử di chuyển và các điểm dự đoán tương lai."""
        frame_height, frame_width = frame_shape[:2]
        heatmap_width = hmap_w or self.heatmap_size[0]
        heatmap_height = hmap_h or self.heatmap_size[1]

        intensity_map = np.zeros((heatmap_height, heatmap_width), dtype=np.float32)
        trajectory_points = []

        history_points = list(self.tracker.target_positions)
        if self.tracker.current_target:
            history_points.append(self.tracker.current_target['center'])

        for index, point in enumerate(history_points):
            mapped_point = self.map_point_to_heatmap(point, frame_width, frame_height, heatmap_width, heatmap_height)
            trajectory_points.append(mapped_point)
            radius = max(12, 22 + index * 2)
            intensity = min(255, 60 + index * 25)
            cv2.circle(intensity_map, mapped_point, radius, intensity, -1)

        future_points = self.get_prediction_points(frame_width, frame_height)
        for index, point in enumerate(future_points):
            mapped_point = self.map_point_to_heatmap(point, frame_width, frame_height, heatmap_width, heatmap_height)
            trajectory_points.append(mapped_point)
            radius = max(10, 26 - index * 2)
            intensity = max(120, 255 - index * 25)
            cv2.circle(intensity_map, mapped_point, radius, intensity, -1)

        if np.any(intensity_map):
            intensity_map = cv2.GaussianBlur(intensity_map, (0, 0), sigmaX=18, sigmaY=18)
            normalized = cv2.normalize(intensity_map, None, 0, 255, cv2.NORM_MINMAX)
            heatmap_array = cv2.applyColorMap(normalized.astype(np.uint8), cv2.COLORMAP_JET)
            heatmap_array = cv2.cvtColor(heatmap_array, cv2.COLOR_BGR2RGB)
        else:
            heatmap_array = np.full((heatmap_height, heatmap_width, 3), (18, 24, 38), dtype=np.uint8)

        heatmap_image = Image.fromarray(heatmap_array)
        draw = ImageDraw.Draw(heatmap_image)

        self.draw_heatmap_grid(draw, heatmap_width, heatmap_height)

        if len(trajectory_points) > 1:
            draw.line(trajectory_points, fill="#f8fafc", width=2)

        for point in trajectory_points[:-1]:
            draw.ellipse((point[0] - 3, point[1] - 3, point[0] + 3, point[1] + 3), fill="#fde68a")

        if trajectory_points:
            last_x, last_y = trajectory_points[-1]
            draw.ellipse((last_x - 6, last_y - 6, last_x + 6, last_y + 6), fill="#ffffff", outline="#111827")

        direction_label = self.describe_direction()
        draw.rounded_rectangle((10, 10, heatmap_width - 10, 44), radius=10, fill=(15, 23, 42, 215))
        draw.text((18, 18), f"Huong du doan: {direction_label}", fill="#e5e7eb")

        return heatmap_image

    def draw_heatmap_grid(self, draw, width, height):
        """Vẽ lưới tham chiếu giúp dễ đọc heatmap hơn."""
        for x in range(0, width, 40):
            draw.line((x, 0, x, height), fill="#334155", width=1)
        for y in range(0, height, 40):
            draw.line((0, y, width, y), fill="#334155", width=1)

    def get_prediction_points(self, frame_width, frame_height):
        """Tạo chuỗi điểm dự đoán theo vận tốc trung bình gần nhất."""
        if not self.tracker.current_target or len(self.tracker.velocity_history) < 2:
            return []

        avg_velocity = np.mean(self.tracker.velocity_history, axis=0)
        current_x, current_y = self.tracker.current_target['center']
        prediction_points = []

        for step in range(1, 6):
            next_x = int(current_x + avg_velocity[0] * step * 2)
            next_y = int(current_y + avg_velocity[1] * step * 2)
            next_x = max(0, min(frame_width - 1, next_x))
            next_y = max(0, min(frame_height - 1, next_y))
            prediction_points.append((next_x, next_y))

        return prediction_points

    def map_point_to_heatmap(self, point, frame_width, frame_height, hmap_w=None, hmap_h=None):
        """Scale điểm trong frame camera sang hệ toạ độ heatmap."""
        w = hmap_w or self.heatmap_size[0]
        h = hmap_h or self.heatmap_size[1]
        x = int(point[0] * w / max(1, frame_width))
        y = int(point[1] * h / max(1, frame_height))
        x = max(0, min(w - 1, x))
        y = max(0, min(h - 1, y))
        return (x, y)

    def describe_direction(self):
        """Mô tả ngắn hướng di chuyển hiện tại của mục tiêu."""
        if len(self.tracker.velocity_history) < 2:
            return "on dinh"

        avg_velocity = np.mean(self.tracker.velocity_history, axis=0)
        horizontal = "phai" if avg_velocity[0] > 1 else "trai" if avg_velocity[0] < -1 else "giu nguyen"
        vertical = "xuong" if avg_velocity[1] > 1 else "len" if avg_velocity[1] < -1 else "giu nguyen"

        if horizontal == "giu nguyen" and vertical == "giu nguyen":
            return "on dinh"
        if horizontal == "giu nguyen":
            return vertical
        if vertical == "giu nguyen":
            return horizontal
        return f"{vertical} {horizontal}"
        
    def quit_app(self):
        """Thoát ứng dụng"""
        if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát?"):
            self.is_running = False
            if self.camera:
                self.camera.release()
            self.root.quit()
            self.root.destroy()