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
        speed = math.hypot(self.vx, self.vy)

        # Trail effect
        if speed > 10:
            norm_x = self.vx / speed
            norm_y = self.vy / speed
            for i in range(1, 4):
                trail_dist = i * r * 1.8
                tx = sx - int(norm_x * trail_dist)
                ty = sy - int(norm_y * trail_dist)
                trail_alpha = (4 - i) / 5.0
                trail_r = max(1, int(r * trail_alpha * 0.7))
                tc = tuple(max(0, int(c * trail_alpha * 0.55)) for c in self.color)
                if any(c > 5 for c in tc):
                    pygame.draw.circle(screen, tc, (tx, ty), trail_r)

        # Outer glow
        glow_color = tuple(min(255, c + 80) for c in self.color)
        pygame.draw.circle(screen, glow_color, (sx, sy), r + 3)

        # Main body
        pygame.draw.circle(screen, self.color, (sx, sy), r)

        # Bright white core
        pygame.draw.circle(screen, (255, 255, 255), (sx, sy), max(1, r // 2))

        # Extra cross-glow for boss projectiles
        if self.owner == "boss" and r >= 10:
            dim = tuple(max(0, c - 50) for c in self.color)
            pygame.draw.line(screen, glow_color, (sx - r - 4, sy), (sx + r + 4, sy), 1)
            pygame.draw.line(screen, glow_color, (sx, sy - r - 4), (sx, sy + r + 4), 1)
