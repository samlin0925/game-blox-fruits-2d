import pygame
import random
import math

class Particle:
    __slots__ = ("x", "y", "vx", "vy", "lifetime", "max_lifetime",
                 "color", "size", "gravity")

    def __init__(self, x, y, vx, vy, lifetime, color, size=4, gravity=0):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.lifetime = float(lifetime)
        self.max_lifetime = float(lifetime)
        self.color = color
        self.size = size
        self.gravity = gravity

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        return self.lifetime > 0

    def draw(self, screen, camera):
        alpha = self.lifetime / self.max_lifetime
        r = max(1, int(self.size * alpha))
        sx, sy = camera.world_to_screen(self.x, self.y)
        color = tuple(int(c * alpha) for c in self.color)
        pygame.draw.circle(screen, color, (sx, sy), r)


class ParticleSystem:
    def __init__(self):
        self._particles = []

    def emit(self, x, y, color, count=8, speed=120, lifetime=0.8,
             size=5, spread=360, gravity=0):
        for _ in range(count):
            angle = math.radians(random.uniform(0, spread))
            spd = random.uniform(speed * 0.5, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            lt = random.uniform(lifetime * 0.5, lifetime)
            sz = random.uniform(size * 0.6, size)
            self._particles.append(
                Particle(x, y, vx, vy, lt, color, sz, gravity))

    def emit_explosion(self, x, y, color, count=20, speed=200):
        self.emit(x, y, color, count, speed, 1.0, 8, 360, 80)

    def emit_level_up(self, x, y):
        self.emit(x, y, (255, 215, 0), 30, 180, 1.5, 6, 360, -50)
        self.emit(x, y, (255, 255, 150), 15, 250, 1.2, 4, 360, 0)

    def emit_hit(self, x, y, color, count=6):
        self.emit(x, y, color, count, 150, 0.4, 4, 360, 100)

    def emit_boss_skill(self, x, y, color):
        self.emit(x, y, color, 40, 300, 1.5, 10, 360, 0)

    def update(self, dt: float):
        self._particles = [p for p in self._particles if p.update(dt)]

    def draw(self, screen, camera):
        for p in self._particles:
            p.draw(screen, camera)
