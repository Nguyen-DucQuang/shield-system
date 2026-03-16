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
        
        self.root.title("Iron Dome Defense System")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        
        # Biến trạng thái
        self.is_running = False
        self.is_tracking = False
        self.auto_fire = True
        self.camera = None
        self.current_frame = None
        
        self.setup_ui()
        if cv2 is None:
            self.add_status("Thiếu thư viện opencv-python: tạm tắt camera.")
        if Image is None or ImageTk is None:
            self.add_status("Thiếu thư viện Pillow: không thể hiển thị frame camera.")
        
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Khu vực hiển thị camera
        video_frame = ttk.LabelFrame(main_frame, text="Camera Feed", padding="5")
        video_frame.grid(row=0, column=0, columnspan=3, pady=5)
        
        self.video_label = ttk.Label(video_frame)
        self.video_label.grid(row=0, column=0)
        
        # Thanh điều khiển
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="Kết nối Camera", 
                                   command=self.toggle_camera)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.track_btn = ttk.Button(control_frame, text="Bắt đầu theo dõi", 
                                   command=self.start_tracking, state='disabled')
        self.track_btn.grid(row=0, column=1, padx=5)
        
        self.auto_fire_var = tk.BooleanVar(value=True)
        self.auto_fire_cb = ttk.Checkbutton(control_frame, text="Tự động khai hỏa", 
                                           variable=self.auto_fire_var)
        self.auto_fire_cb.grid(row=0, column=2, padx=5)
        
        self.quit_btn = ttk.Button(control_frame, text="Thoát", 
                                  command=self.quit_app)
        self.quit_btn.grid(row=0, column=3, padx=5)
        
        # Khu vực thông tin
        info_frame = ttk.LabelFrame(main_frame, text="Trạng thái hệ thống", padding="5")
        info_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        
        self.status_text = tk.Text(info_frame, height=8, width=70)
        self.status_text.grid(row=0, column=0, padx=5)
        
        # Scrollbar cho status
        scrollbar = ttk.Scrollbar(info_frame, orient='vertical', 
                                  command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
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
                    self.track_btn.config(state='normal')
                    self.add_status("Đã kết nối webcam laptop thành công!")
                    self.update_frame()
                else:
                    messagebox.showerror("Lỗi", "Không thể kết nối webcam. Thu doi CAMERA_URL = 0 hoac 1 trong config.py")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi kết nối camera: {str(e)}")
        else:
            self.is_running = False
            self.is_tracking = False
            if self.camera:
                self.camera.release()
            self.start_btn.config(text="Kết nối Camera")
            self.track_btn.config(state='disabled')
            self.add_status("Đã ngắt kết nối camera.")
            
    def start_tracking(self):
        """Bắt đầu theo dõi mục tiêu"""
        self.is_tracking = True
        self.track_btn.config(text="Đang theo dõi...", state='disabled')
        self.add_status("Bắt đầu theo dõi mục tiêu...")
        
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
        frame_pil = frame_pil.resize((640, 480), Image.Resampling.LANCZOS)
        
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