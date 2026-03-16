# main.py
import tkinter as tk
from detector import TargetDetector
from tracker import TargetTracker
from missile_sim import MissileLauncher
from gui_app import IronDomeGUI
from config import Config

def main():
    print("=" * 50)
    print("IRON DOME DEFENSE SYSTEM")
    print("=" * 50)
    print("\nĐang khởi tạo hệ thống...")
    
    # Khởi tạo các thành phần
    config = Config()
    detector = TargetDetector()
    tracker = TargetTracker()
    launcher = MissileLauncher()
    
    # Tạo giao diện
    root = tk.Tk()
    app = IronDomeGUI(root, detector, tracker, launcher, config)
    
    print("Hệ thống đã sẵn sàng!")
    print("\nHướng dẫn:")
    print("1. Đảm bảo webcam laptop đang hoạt động")
    print("2. Nhấn 'Kết nối Camera' để bắt đầu")
    print("3. Nhấn 'Bắt đầu theo dõi' để phát hiện mục tiêu")
    print("4. Tick 'Tự động khai hỏa' để bắn tự động")
    print("=" * 50)
    
    # Chạy ứng dụng
    root.protocol("WM_DELETE_WINDOW", app.quit_app)
    root.mainloop()

if __name__ == "__main__":
    main()