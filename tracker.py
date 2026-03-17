# tracker.py
try:
    import cv2
except Exception:
    cv2 = None
import numpy as np
from collections import deque

class TargetTracker:
    def __init__(self, max_history=30):
        self.trackers = []
        self.tracker_types = []
        self.target_positions = deque(maxlen=max_history)
        self.velocity_history = deque(maxlen=10)
        self.current_target = None
        self.target_lost_counter = 0
        self.max_lost_frames = 10
        self.fallback_mode = False

    def _create_tracker(self):
        """Tạo tracker khả dụng theo phiên bản OpenCV hiện tại."""
        if cv2 is None:
            return None

        creators = [
            'TrackerCSRT_create',
            'TrackerKCF_create',
            'TrackerMIL_create',
        ]

        for name in creators:
            creator = getattr(cv2, name, None)
            if callable(creator):
                return creator()

        legacy = getattr(cv2, 'legacy', None)
        if legacy is not None:
            for name in creators:
                creator = getattr(legacy, name, None)
                if callable(creator):
                    return creator()

        return None
        
    def add_tracker(self, frame, bbox, class_id=None, class_name=None):
        """Thêm tracker mới cho mục tiêu"""
        x, y, w, h = [int(v) for v in bbox]
        w = max(1, w)
        h = max(1, h)

        tracker = self._create_tracker()
        if tracker is not None:
            tracker.init(frame, (x, y, w, h))
            self.trackers.append(tracker)
            self.tracker_types.append('OpenCV')
            self.fallback_mode = False
        else:
            self.fallback_mode = True

        center = (x + w // 2, y + h // 2)
        self.current_target = {
            'bbox': (x, y, w, h),
            'center': center,
            'velocity': (0, 0),
            'class_id': class_id,
            'class_name': class_name or "unknown"
        }
        
    def update(self, frame):
        """Cập nhật vị trí mục tiêu"""
        if self.fallback_mode and self.current_target:
            x, y, w, h = self.current_target['bbox']
            vx, vy = self.current_target['velocity']
            previous_class_id = self.current_target.get('class_id')
            previous_class_name = self.current_target.get('class_name', "unknown")
            next_center = (x + w // 2 + int(vx), y + h // 2 + int(vy))
            self.current_target = {
                'bbox': (x + int(vx), y + int(vy), w, h),
                'center': next_center,
                'velocity': (vx, vy),
                'class_id': previous_class_id,
                'class_name': previous_class_name
            }
            return self.current_target

        if not self.trackers:
            return None
            
        success, bbox = self.trackers[-1].update(frame)
        
        if success:
            x, y, w, h = [int(v) for v in bbox]
            center = (x + w//2, y + h//2)
            previous_class_id = self.current_target.get('class_id') if self.current_target else None
            previous_class_name = self.current_target.get('class_name') if self.current_target else "unknown"
            
            # Lưu vị trí hiện tại
            if self.current_target:
                self.target_positions.append(self.current_target['center'])
            
            self.current_target = {
                'bbox': (x, y, w, h),
                'center': center,
                'velocity': self._calculate_velocity(center),
                'class_id': previous_class_id,
                'class_name': previous_class_name
            }
            
            self.target_lost_counter = 0
            return self.current_target
        else:
            self.target_lost_counter += 1
            if self.target_lost_counter > self.max_lost_frames:
                self.clear()
            return None
    
    def _calculate_velocity(self, current_center):
        """Tính vận tốc dựa trên lịch sử vị trí"""
        if len(self.target_positions) > 1:
            prev_center = self.target_positions[-1]
            dx = current_center[0] - prev_center[0]
            dy = current_center[1] - prev_center[1]
            velocity = (dx, dy)
            self.velocity_history.append(velocity)
            return velocity
        return (0, 0)
    
    def predict_future_position(self, frames_ahead=5):
        """Dự đoán vị trí tương lai"""
        if not self.current_target or len(self.velocity_history) < 3:
            return None
            
        avg_velocity = np.mean(self.velocity_history, axis=0)
        current_center = self.current_target['center']
        
        predicted_x = int(current_center[0] + avg_velocity[0] * frames_ahead)
        predicted_y = int(current_center[1] + avg_velocity[1] * frames_ahead)
        
        return (predicted_x, predicted_y)
    
    def clear(self):
        """Xóa tất cả trackers"""
        self.trackers.clear()
        self.tracker_types.clear()
        self.target_positions.clear()
        self.velocity_history.clear()
        self.current_target = None
        self.target_lost_counter = 0
        self.fallback_mode = False