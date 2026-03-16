# config.py
class Config:
    # Camera settings
    CAMERA_URL = 0  # Webcam laptop mac dinh (0). Thu 1, 2 neu may co nhieu camera.
    
    # Detection settings
    CONFIDENCE_THRESHOLD = 0.5
    TARGET_CLASSES = [0, 2, 5, 7]  # person, car, bus, truck (có thể thay đổi)
    
    # Protected zone (khu vực cần bảo vệ)
    PROTECTED_ZONE = {
        'x1': 200,
        'y1': 150,
        'x2': 500,
        'y2': 350
    }
    
    # Missile settings
    MISSILE_SPEED = 10
    EXPLOSION_RADIUS = 50
    
    # GUI settings
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    FPS = 30