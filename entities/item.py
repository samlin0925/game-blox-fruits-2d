import pygame
import math
from entities.base_entity import BaseEntity
from core.constants import WHITE

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
        bob = int(math.sin(self.bob_timer * 4) * 5)
        cy = sy + bob
        t = self.bob_timer

        # Flash warning when about to despawn
        if self.lifetime < 3.0 and int(t * 6) % 2 == 0:
            return

        if self.item_type == "health":
            self._draw_health(screen, sx, cy, t)
        elif self.item_type == "gold":
            self._draw_gold(screen, sx, cy, t)
        elif self.item_type == "fragment":
            self._draw_fragment(screen, sx, cy, t)
        else:
            self._draw_generic(screen, sx, cy)

    def _glow_circle(self, screen, cx, cy, r, color_rgb, alpha):
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color_rgb, alpha), (r + 1, r + 1), r)
        screen.blit(s, (cx - r - 1, cy - r - 1))

    def _draw_health(self, screen, sx, cy, t):
        pulse = 0.65 + 0.35 * math.sin(t * 5)

        # Pulsing soft glow
        self._glow_circle(screen, sx, cy, int(20 * pulse), (255, 60, 80), 55)

        # Outer ring indicator
        ring_r = 14
        pygame.draw.circle(screen, (255, 100, 120), (sx, cy), ring_r, 2)

        # Heart shape (larger)
        r = 10
        RED_H  = (230, 50, 60)
        RED_HL = (255, 150, 160)
        pygame.draw.circle(screen, RED_H, (sx - r // 2, cy - r // 4), r // 2 + 2)
        pygame.draw.circle(screen, RED_H, (sx + r // 2, cy - r // 4), r // 2 + 2)
        pygame.draw.polygon(screen, RED_H, [
            (sx - r - 1, cy - r // 4),
            (sx + r + 1, cy - r // 4),
            (sx, cy + r + 2),
        ])
        # Highlight
        pygame.draw.circle(screen, RED_HL, (sx - r // 3, cy - r // 3), max(1, r // 3))

        # + Cross indicator above
        cross_y = cy - r - 10
        pygame.draw.line(screen, (255, 200, 200), (sx, cross_y - 5), (sx, cross_y + 5), 2)
        pygame.draw.line(screen, (255, 200, 200), (sx - 5, cross_y), (sx + 5, cross_y), 2)

    def _draw_gold(self, screen, sx, cy, t):
        pulse = 0.65 + 0.35 * math.sin(t * 6)

        # Pulsing golden glow
        self._glow_circle(screen, sx, cy, int(20 * pulse), (255, 215, 0), 65)

        # Spinning coin (squish effect for 3D spin)
        scale_x = abs(math.cos(t * 3.5))
        coin_w = max(3, int(12 * (0.25 + 0.75 * scale_x)))
        coin_h = 12
        GOLD   = (255, 215, 0)
        GOLD_D = (180, 145, 0)
        GOLD_L = (255, 240, 120)

        pygame.draw.ellipse(screen, GOLD_D, (sx - coin_w - 2, cy - coin_h + 2, (coin_w + 2) * 2, coin_h * 2))
        pygame.draw.ellipse(screen, GOLD,   (sx - coin_w, cy - coin_h, coin_w * 2, coin_h * 2))
        if coin_w > 5:
            pygame.draw.ellipse(screen, GOLD_L, (sx - coin_w + 2, cy - coin_h + 2, max(4, coin_w - 2), coin_h - 2))

        # Animated sparkle star above coin
        star_y = cy - 22 - int(math.sin(t * 4) * 3)
        star_size = 4
        for i in range(4):
            angle = math.radians(i * 90 + t * 120)
            ex = sx + int(math.cos(angle) * star_size * 2)
            ey = star_y + int(math.sin(angle) * star_size * 2)
            pygame.draw.line(screen, (255, 240, 100), (sx, star_y), (ex, ey), 1)
        pygame.draw.circle(screen, (255, 255, 200), (sx, star_y), 2)

        # "G" text indicator - draw manually
        gx, gy = sx - 4, cy - 3
        pygame.draw.arc(screen, (120, 90, 0),
                        (gx - 3, gy - 4, 14, 12), math.radians(30), math.radians(330), 2)
        pygame.draw.line(screen, (120, 90, 0), (gx + 7, gy), (gx + 4, gy), 2)

    def _draw_fragment(self, screen, sx, cy, t):
        c = tuple(self.color[:3])
        bright = tuple(min(255, v + 80) for v in c)
        pulse = 0.65 + 0.35 * math.sin(t * 5)

        # Soft outer glow
        self._glow_circle(screen, sx, cy, int(22 * pulse), c, 50)

        # Rotating dashed outer ring
        ring_r = 15
        for i in range(8):
            angle = math.radians(i * 45 + t * 90)
            rx = sx + int(math.cos(angle) * ring_r)
            ry = cy + int(math.sin(angle) * ring_r)
            dot_col = bright if i % 2 == 0 else c
            pygame.draw.circle(screen, dot_col, (rx, ry), 2)

        # Main crystal body
        r = 10
        pygame.draw.circle(screen, c, (sx, cy), r)
        pygame.draw.circle(screen, bright, (sx, cy), r - 4)
        pygame.draw.circle(screen, WHITE, (sx, cy), r, 2)

        # White specular highlight
        pygame.draw.circle(screen, (255, 255, 255), (sx - 3, cy - 3), 3)
        pygame.draw.circle(screen, (255, 255, 255), (sx - 3, cy - 3), 1)

        # Diamond marker above
        dia_y = cy - r - 12
        ds = 5
        pygame.draw.polygon(screen, bright, [
            (sx, dia_y - ds), (sx + ds, dia_y), (sx, dia_y + ds), (sx - ds, dia_y),
        ])
        pygame.draw.polygon(screen, WHITE, [
            (sx, dia_y - ds), (sx + ds, dia_y), (sx, dia_y + ds), (sx - ds, dia_y),
        ], 1)

    def _draw_generic(self, screen, sx, cy):
        pygame.draw.circle(screen, self.color[:3], (sx, cy), 8)
        pygame.draw.circle(screen, WHITE, (sx, cy), 8, 1)
