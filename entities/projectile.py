import pygame
import math
from entities.base_entity import BaseEntity
from config import WORLD_WIDTH, WORLD_HEIGHT, PROJECTILE_LIFETIME

class Projectile(BaseEntity):
    def __init__(self, x, y, dx, dy, speed, damage, color, owner="player",
                 aoe_radius=0, piercing=False, size=8):
        super().__init__(x, y, size * 2, size * 2)
        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length
        self.vx = dx * speed
        self.vy = dy * speed
        self.damage = damage
        self.color = color
        self.owner = owner
        self.aoe_radius = aoe_radius
        self.piercing = piercing
        self.radius = size
        self.lifetime = PROJECTILE_LIFETIME
        self.hit_targets = set()

    def update(self, dt: float):
        super().update(dt)
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
        if not (0 <= self.x <= WORLD_WIDTH and 0 <= self.y <= WORLD_HEIGHT):
            self.alive = False

    def draw(self, screen, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        r = self.radius
        glow_color = tuple(min(255, c + 80) for c in self.color)
        pygame.draw.circle(screen, glow_color, (sx, sy), r + 2)
        pygame.draw.circle(screen, self.color, (sx, sy), r)
