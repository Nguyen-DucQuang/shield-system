# gui_app.py
import tkinter as tk
from tkinter import ttk, messagebox
try:
    import cv2
except Exception:
    cv2 = None

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

import time

class IronDomeGUI:
    def __init__(self, root, detector, tracker, launcher, config):
        self.root = root
        self.detector = detector
        self.tracker = tracker
        self.launcher = launcher
        self.config = config
        
        self.root.title("Shield System AI")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.configure(bg="#111827")
        
        # Biến trạng thái
        self.is_running = False
        self.is_tracking = False
        self.auto_fire = True
        self.camera = None
        self.current_frame = None
        self.preview_size = (560, 300)

        self.setup_styles()
        self.setup_ui()
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
        video_frame.grid(row=2, column=0, pady=5, sticky=tk.W)
        video_frame.columnconfigure(0, weight=1)
        
        self.video_label = ttk.Label(
            video_frame,
            anchor="center",
            text="Khung camera preview",
            style="Subtitle.TLabel"
        )
        self.video_label.grid(row=0, column=0, sticky=tk.W)
        
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
        
        self.auto_fire_var = tk.BooleanVar(value=True)
        self.auto_fire_cb = ttk.Checkbutton(
            control_frame,
            text="Tự động khai hỏa",
            variable=self.auto_fire_var
        )
        self.auto_fire_cb.grid(row=0, column=2, padx=6, pady=2, sticky=tk.W)
        
        self.quit_btn = ttk.Button(
            control_frame,
            text="Thoát",
            command=self.quit_app,
            style="Danger.TButton",
            width=16
        )
        self.quit_btn.grid(row=0, column=3, padx=6, pady=2, sticky=(tk.W, tk.E))
        
        # Khu vực thông tin
        info_frame = ttk.LabelFrame(main_frame, text="Trạng thái hệ thống", padding="8")
        info_frame.grid(row=3, column=0, pady=(4, 0), sticky=(tk.W, tk.E, tk.N, tk.S))
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        
        self.status_text = tk.Text(
            info_frame,
            height=6,
            width=70,
            bg="#0f172a",
            fg="#e2e8f0",
            insertbackground="#f8fafc",
            relief="flat",
            font=("Consolas", 10),
            wrap="word"
        )
        self.status_text.grid(row=0, column=0, padx=4, pady=4, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar cho status
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
            self.add_status("Đã ngắt kết nối camera.")

    def toggle_tracking(self):
        """Bật/tắt theo dõi mục tiêu."""
        if not self.is_running:
            self.add_status("Hãy kết nối camera trước khi bật theo dõi.")
            return

        if not self.is_tracking:
            self.is_tracking = True
            self.track_btn.config(text="Tắt theo dõi", style="Warning.TButton")
            self.add_status("Đã bật theo dõi mục tiêu.")
        else:
            self.is_tracking = False
            self.tracker.clear()
            self.track_btn.config(text="Bắt đầu theo dõi", style="Accent.TButton")
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
                self.add_status(f"Đã phát hiện mục tiêu! Độ tin cậy: {target['confidence']:.2f}")
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
                    self.check_and_fire(target)
                    
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
                        
    def check_and_fire(self, target):
        """Kiểm tra và bắn tên lửa nếu cần"""
        predicted_pos = self.tracker.predict_future_position(frames_ahead=10)
        if not predicted_pos:
            return
            
        pz = self.config.PROTECTED_ZONE
        
        # Kiểm tra nếu mục tiêu đang tiến vào vùng bảo vệ
        if (pz['x1'] <= predicted_pos[0] <= pz['x2'] and 
            pz['y1'] <= predicted_pos[1] <= pz['y2']):
            
            # Bắn tên lửa vào vị trí dự đoán
            self.launcher.fire(target['center'])
            self.add_status(f"Đã khai hỏa! Mục tiêu tại {target['center']}")
            
    def display_frame(self, frame):
        """Hiển thị frame lên giao diện"""
        if cv2 is None or Image is None or ImageTk is None:
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        
        # Resize để vừa với khung hình
        frame_pil = frame_pil.resize(self.preview_size, Image.Resampling.LANCZOS)
        
        frame_tk = ImageTk.PhotoImage(frame_pil)
        self.video_label.config(image=frame_tk)
        self.video_label.image = frame_tk
        
    def quit_app(self):
        """Thoát ứng dụng"""
        if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát?"):
            self.is_running = False
            if self.camera:
                self.camera.release()
            self.root.quit()
            self.root.destroy()