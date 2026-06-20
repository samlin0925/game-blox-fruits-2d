import pygame
import random
from utils.font_helper import get_font

class FloatingTextItem:
    def __init__(self, wx, wy, text, color, big=False):
        self.wx = float(wx)
        self.wy = float(wy)
        self.text = text
        self.color = color
        self.big = big
        self.lifetime = 1.6 if big else 1.2
        self.max_lifetime = self.lifetime
        self.vy = -80 if not big else -120
        self.vx = random.uniform(-20, 20)
        self.font = get_font(30 if big else 20, bold=big)

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        self.wy += self.vy * dt
        self.wx += self.vx * dt
        self.vy += 20 * dt
        return self.lifetime > 0

    def draw(self, screen, camera):
        alpha = self.lifetime / self.max_lifetime
        sx, sy = camera.world_to_screen(self.wx, self.wy)
        if not (0 <= sx <= screen.get_width() and 0 <= sy <= screen.get_height()):
            return
        color = tuple(int(c * alpha) for c in self.color)
        surf = self.font.render(self.text, True, color)
        screen.blit(surf, (sx - surf.get_width() // 2, sy))


class FloatingTextManager:
    def __init__(self):
        self._items = []

    def add(self, wx, wy, text, color=(255, 255, 255), big=False):
        self._items.append(FloatingTextItem(wx, wy, text, color, big))

    def update(self, dt: float):
        self._items = [item for item in self._items if item.update(dt)]

    def draw(self, screen, camera):
        for item in self._items:
            item.draw(screen, camera)
