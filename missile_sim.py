    # missile_sim.py
import math
import time
import numpy as np

class Missile:
    def __init__(self, start_pos, target_pos, speed=10):
        self.start_pos = start_pos
        self.target_pos = target_pos
        self.speed = speed
        self.current_pos = list(start_pos)
        self.is_active = True
        self.has_hit = False
        self.trajectory = [start_pos]
        self.explosion_particles = []
        
        # Tính toán đường bay
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.direction = (dx/distance, dy/distance)
        else:
            self.direction = (0, 0)
    
    def update(self):
        """Cập nhật vị trí tên lửa"""
        if not self.is_active:
            return
            
        # Di chuyển tên lửa
        self.current_pos[0] += self.direction[0] * self.speed
        self.current_pos[1] += self.direction[1] * self.speed
        self.trajectory.append(tuple(self.current_pos))
        
        # Kiểm tra va chạm
        dx = self.current_pos[0] - self.target_pos[0]
        dy = self.current_pos[1] - self.target_pos[1]
        distance_to_target = math.sqrt(dx**2 + dy**2)
        
        if distance_to_target < self.speed:
            self.explode()
    
    def explode(self):
        """Tạo hiệu ứng nổ"""
        self.has_hit = True
        self.is_active = False
        
        # Tạo các hạt cho hiệu ứng nổ
        for _ in range(20):
            angle = np.random.uniform(0, 2 * math.pi)
            speed = np.random.uniform(2, 8)
            self.explosion_particles.append({
                'pos': list(self.current_pos),
                'vel': (math.cos(angle) * speed, math.sin(angle) * speed),
                'life': 30
            })

class MissileLauncher:
    def __init__(self, position=(400, 500)):
        self.position = position
        self.active_missiles = []
        self.missile_speed = 10
        
    def fire(self, target_pos):
        """Bắn tên lửa vào mục tiêu"""
        missile = Missile(self.position, target_pos, self.missile_speed)
        self.active_missiles.append(missile)
        return missile
    
    def update_all(self):
        """Cập nhật tất cả tên lửa"""
        for missile in self.active_missiles[:]:
            missile.update()
            if not missile.is_active:
                self.active_missiles.remove(missile)