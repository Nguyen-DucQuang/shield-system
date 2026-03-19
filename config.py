# config.py
class Config:
    # Camera settings
    CAMERA_URL = 0  # Default laptop webcam (0). Try 1 or 2 if your machine has multiple cameras.
    
    # Detection settings
    CONFIDENCE_THRESHOLD = 0.5
    TARGET_CLASSES = [0, 2, 5, 7]  # person, car, bus, truck (can be changed)
    
    # Protected zone
    PROTECTED_ZONE = {
        'x1': 200,
        'y1': 150,
        'x2': 500,
        'y2': 350
    }
    
    # Missile settings
    MISSILE_SPEED = 10
    EXPLOSION_RADIUS = 50
    FIRE_COOLDOWN_SECONDS = 1.0
    
    # GUI settings
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 780
    FPS = 60