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


class RingParticle:
    """Expanding shockwave ring."""
    __slots__ = ("x", "y", "max_radius", "lifetime", "max_lifetime", "color", "width")

    def __init__(self, x, y, color, max_radius=70, lifetime=0.45, width=3):
        self.x = float(x)
        self.y = float(y)
        self.max_radius = float(max_radius)
        self.lifetime = float(lifetime)
        self.max_lifetime = float(lifetime)
        self.color = color
        self.width = width

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, screen, camera):
        alpha = self.lifetime / self.max_lifetime
        progress = 1.0 - alpha
        r = max(2, int(self.max_radius * progress))
        sx, sy = camera.world_to_screen(self.x, self.y)
        color = tuple(int(c * alpha) for c in self.color)
        if any(c > 4 for c in color):
            w = max(1, int(self.width * alpha))
            pygame.draw.circle(screen, color, (sx, sy), r, w)


class SparkParticle:
    """Thin bright spark / line particle."""
    __slots__ = ("x", "y", "x2", "y2", "vx", "vy", "lifetime", "max_lifetime", "color")

    def __init__(self, x, y, vx, vy, lifetime, color):
        self.x = float(x)
        self.y = float(y)
        self.x2 = float(x)
        self.y2 = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.lifetime = float(lifetime)
        self.max_lifetime = float(lifetime)
        self.color = color

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        speed = math.hypot(self.vx, self.vy)
        tail = min(18.0, speed * 0.06)
        nx = self.vx / max(1, speed)
        ny = self.vy / max(1, speed)
        self.x2 = self.x - nx * tail
        self.y2 = self.y - ny * tail
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.88
        self.vy *= 0.88
        return self.lifetime > 0

    def draw(self, screen, camera):
        alpha = self.lifetime / self.max_lifetime
        sx1, sy1 = camera.world_to_screen(self.x, self.y)
        sx2, sy2 = camera.world_to_screen(self.x2, self.y2)
        color = tuple(int(c * alpha) for c in self.color)
        if any(c > 4 for c in color):
            pygame.draw.line(screen, color, (sx1, sy1), (sx2, sy2), 2)


class ParticleSystem:
    def __init__(self):
        self._particles = []
        self._rings = []
        self._sparks = []

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
        # Secondary smaller burst
        bright = tuple(min(255, c + 80) for c in color)
        self.emit(x, y, bright, count // 2, speed * 0.6, 0.6, 4, 360, 50)
        self._rings.append(RingParticle(x, y, color, max_radius=80, lifetime=0.5, width=4))
        self._rings.append(RingParticle(x, y, (255, 255, 200), max_radius=50, lifetime=0.35, width=2))

    def emit_level_up(self, x, y):
        self.emit(x, y, (255, 215, 0), 30, 180, 1.5, 6, 360, -50)
        self.emit(x, y, (255, 255, 150), 15, 250, 1.2, 4, 360, 0)
        self._rings.append(RingParticle(x, y, (255, 215, 0), 100, 0.6, 3))

    def emit_hit(self, x, y, color, count=8):
        """Directional spark burst on hit."""
        self.emit(x, y, color, count, 180, 0.4, 4, 360, 120)
        bright = tuple(min(255, c + 100) for c in color)
        # Sparks
        for _ in range(5):
            angle = math.radians(random.uniform(0, 360))
            spd = random.uniform(200, 350)
            self._sparks.append(SparkParticle(
                x, y, math.cos(angle) * spd, math.sin(angle) * spd,
                random.uniform(0.15, 0.35), bright))

    def emit_crit(self, x, y):
        """Gold star-burst for critical hits."""
        GOLD = (255, 215, 0)
        WHITE = (255, 255, 220)
        self.emit(x, y, GOLD, 20, 280, 0.7, 7, 360, 40)
        self.emit(x, y, WHITE, 10, 350, 0.5, 4, 360, 20)
        self._rings.append(RingParticle(x, y, GOLD, 65, 0.4, 3))
        self._rings.append(RingParticle(x, y, WHITE, 40, 0.25, 2))
        for _ in range(8):
            angle = math.radians(random.uniform(0, 360))
            spd = random.uniform(300, 500)
            self._sparks.append(SparkParticle(
                x, y, math.cos(angle) * spd, math.sin(angle) * spd,
                0.3, GOLD))

    def emit_boss_skill(self, x, y, color):
        self.emit(x, y, color, 40, 300, 1.5, 10, 360, 0)
        bright = tuple(min(255, c + 60) for c in color)
        self._rings.append(RingParticle(x, y, color, 120, 0.7, 5))
        self._rings.append(RingParticle(x, y, bright, 80, 0.5, 3))
        for _ in range(12):
            angle = math.radians(random.uniform(0, 360))
            spd = random.uniform(250, 450)
            self._sparks.append(SparkParticle(
                x, y, math.cos(angle) * spd, math.sin(angle) * spd,
                0.4, bright))

    def update(self, dt: float):
        self._particles = [p for p in self._particles if p.update(dt)]
        self._rings = [r for r in self._rings if r.update(dt)]
        self._sparks = [s for s in self._sparks if s.update(dt)]

    def draw(self, screen, camera):
        for r in self._rings:
            r.draw(screen, camera)
        for p in self._particles:
            p.draw(screen, camera)
        for s in self._sparks:
            s.draw(screen, camera)
