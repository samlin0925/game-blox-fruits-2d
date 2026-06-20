import random
from utils.math_utils import lerp, clamp
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT

class CameraManager:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self._shake_intensity = 0.0
        self._shake_duration = 0.0
        self._offset_x = 0
        self._offset_y = 0

    def follow(self, target_x: float, target_y: float, dt: float):
        desired_x = target_x - SCREEN_WIDTH / 2
        desired_y = target_y - SCREEN_HEIGHT / 2
        self.x = lerp(self.x, desired_x, min(1.0, dt * 8))
        self.y = lerp(self.y, desired_y, min(1.0, dt * 8))
        self.x = clamp(self.x, 0, WORLD_WIDTH - SCREEN_WIDTH)
        self.y = clamp(self.y, 0, WORLD_HEIGHT - SCREEN_HEIGHT)

    def shake(self, intensity: float, duration: float):
        if intensity > self._shake_intensity:
            self._shake_intensity = intensity
            self._shake_duration = duration

    def update(self, dt: float):
        if self._shake_duration > 0:
            self._shake_duration -= dt
            self._offset_x = random.randint(-int(self._shake_intensity),
                                             int(self._shake_intensity))
            self._offset_y = random.randint(-int(self._shake_intensity),
                                             int(self._shake_intensity))
            if self._shake_duration <= 0:
                self._shake_intensity = 0
                self._offset_x = 0
                self._offset_y = 0
        else:
            self._offset_x = 0
            self._offset_y = 0

    def world_to_screen(self, wx: float, wy: float) -> tuple:
        sx = int(wx - self.x) + self._offset_x
        sy = int(wy - self.y) + self._offset_y
        return sx, sy

    def screen_to_world(self, sx: int, sy: int) -> tuple:
        return sx + self.x, sy + self.y
