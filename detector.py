# detector.py
try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

class TargetDetector:
    def __init__(self):
        self.model = None
        self.model_load_failed = False
        self.confidence_threshold = 0.5
        self.target_classes = [0, 2, 4, 5, 7]  # person, car, airplane, bus, truck

    def _ensure_model(self):
        """Nạp model theo kiểu lazy-load để tránh crash khi thiếu thư viện."""
        if self.model is not None or self.model_load_failed:
            return

        if YOLO is None:
            self.model_load_failed = True
            print("Cảnh báo: thiếu thư viện ultralytics, tạm tắt phát hiện mục tiêu.")
            return

        try:
            print("Đang tải mô hình YOLOv8...")
            self.model = YOLO('yolov8n.pt')  # Model nhẹ, chạy nhanh
            print("Đã tải xong mô hình!")
        except Exception as exc:
            self.model_load_failed = True
            print(f"Cảnh báo: không thể tải YOLO ({exc}). Tạm tắt phát hiện mục tiêu.")
        
    def detect(self, frame):
        """Phát hiện vật thể trong frame"""
        self._ensure_model()
        if self.model is None:
            return []

        results = self.model(frame, verbose=False)[0]
        class_names = getattr(results, 'names', None)
        if class_names is None:
            class_names = getattr(self.model, 'names', {})
        detections = []
        
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            if isinstance(class_names, dict):
                class_name = str(class_names.get(class_id, f"class_{class_id}"))
            elif isinstance(class_names, list) and 0 <= class_id < len(class_names):
                class_name = str(class_names[class_id])
            else:
                class_name = f"class_{class_id}"

            class_name_lower = class_name.lower()
            is_airborne = any(keyword in class_name_lower for keyword in ("airplane", "plane", "drone", "uav", "helicopter"))
            
            if confidence > self.confidence_threshold and (class_id in self.target_classes or is_airborne):
                width = max(1, x2 - x1)
                height = max(1, y2 - y1)
                detections.append({
                    'bbox': (x1, y1, width, height),
                    'center': ((x1 + x2)//2, (y1 + y2)//2),
                    'confidence': confidence,
                    'class_id': class_id,
                    'class_name': class_name
                })
        
        return detections