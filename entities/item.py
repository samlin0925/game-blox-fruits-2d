import pygame
import math
from entities.base_entity import BaseEntity
from core.constants import YELLOW, WHITE

class DroppedItem(BaseEntity):
    def __init__(self, x, y, item_type: str, value=1, color=(255, 215, 0),
                 fruit_id: str = None):
        super().__init__(x, y, 16, 16)
        self.item_type = item_type
        self.value = value
        self.color = color
        self.fruit_id = fruit_id
        self.bob_timer = 0.0
        self.lifetime = 15.0

    def update(self, dt: float):
        self.bob_timer += dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, screen, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        bob = int(math.sin(self.bob_timer * 4) * 3)
        cy = sy + bob

        if self.item_type == "health":
            # Red heart shape
            r = 7
            RED_H  = (230, 50, 60)
            RED_HL = (255, 120, 130)
            pygame.draw.circle(screen, RED_H, (sx - r // 2, cy - r // 4), r // 2 + 1)
            pygame.draw.circle(screen, RED_H, (sx + r // 2, cy - r // 4), r // 2 + 1)
            pygame.draw.polygon(screen, RED_H, [
                (sx - r, cy - r // 4),
                (sx + r, cy - r // 4),
                (sx, cy + r),
            ])
            pygame.draw.circle(screen, RED_HL, (sx - r // 3, cy - r // 3), max(1, r // 4))
        else:
            pygame.draw.circle(screen, self.color, (sx, cy), 8)
            pygame.draw.circle(screen, WHITE, (sx, cy), 8, 1)
            if self.item_type == "fragment":
                inner = tuple(min(255, c + 60) for c in self.color)
                pygame.draw.circle(screen, inner, (sx, cy), 4)
