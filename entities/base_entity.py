import pygame

class BaseEntity:
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.width / 2),
                           int(self.y - self.height / 2),
                           self.width, self.height)

    @property
    def center(self):
        return (self.x, self.y)

    def update(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, screen, camera):
        pass

    def clamp_to_world(self, world_w: int, world_h: int):
        half_w = self.width / 2
        half_h = self.height / 2
        self.x = max(half_w, min(world_w - half_w, self.x))
        self.y = max(half_h, min(world_h - half_h, self.y))
