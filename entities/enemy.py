import pygame
import math
from entities.base_entity import BaseEntity
from core.constants import WHITE, RED
from config import WORLD_WIDTH, WORLD_HEIGHT

class Enemy(BaseEntity):
    def __init__(self, x: float, y: float, data: dict):
        r = data.get("size", 18)
        super().__init__(x, y, r * 2, r * 2)
        self.data = data
        self.name = data["name"]
        self.max_health = data["health"]
        self.health = self.max_health
        self.attack = data["attack"]
        self.defense = data.get("defense", 0)
        self.speed = data["speed"]
        self.exp_reward = data["exp_reward"]
        self.gold_reward = data["gold_reward"]
        self.fragment_drop_chance = data.get("fragment_drop_chance", 0.05)
        self.detect_range = data.get("detect_range", 250)
        self.attack_range = data.get("attack_range", 50)
        self.attack_cooldown_max = data.get("attack_cooldown", 1.5)
        self.attack_cooldown = 0.0
        self.color = tuple(data.get("color", [200, 60, 60]))
        self.faction = data.get("faction", "pirate")   # "marine" | "pirate" | "beast"
        self.radius = r
        self.ai = None
        self.freeze_timer = 0.0
        self.hurt_timer = 0.0
        self._anim_t = 0.0

    def take_damage(self, amount: int) -> int:
        damage = max(1, amount - self.defense // 2)
        self.health -= damage
        self.hurt_timer = 0.2
        if self.health <= 0:
            self.health = 0
            self.alive = False
        return damage

    def freeze(self, duration: float):
        self.freeze_timer = max(self.freeze_timer, duration)

    def update(self, dt: float):
        self._anim_t += dt
        if self.freeze_timer > 0:
            self.freeze_timer -= dt
            self.vx = 0
            self.vy = 0
        else:
            if self.ai:
                self.ai.update(dt, self)
        super().update(dt)
        self.clamp_to_world(WORLD_WIDTH, WORLD_HEIGHT)
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.hurt_timer > 0:
            self.hurt_timer -= dt

    def can_attack(self) -> bool:
        return self.attack_cooldown <= 0

    def reset_attack_cooldown(self):
        self.attack_cooldown = self.attack_cooldown_max

    def draw(self, screen, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        r = self.radius
        frozen = self.freeze_timer > 0
        hurt   = self.hurt_timer > 0

        if frozen:
            self._draw_frozen(screen, sx, sy, r)
        elif self.faction == "marine":
            self._draw_chibi_marine(screen, sx, sy, r, hurt)
        elif self.faction == "pirate":
            self._draw_chibi_pirate(screen, sx, sy, r, hurt)
        else:
            self._draw_chibi_beast(screen, sx, sy, r, hurt)

        # HP 條
        bar_w = r * 2 + 4
        bar_h = 5
        bx = sx - bar_w // 2
        by = sy - r - 14
        pygame.draw.rect(screen, (80, 0, 0), (bx, by, bar_w, bar_h))
        hp_w = int(bar_w * self.health / self.max_health)
        pygame.draw.rect(screen, RED, (bx, by, hp_w, bar_h))
        pygame.draw.rect(screen, WHITE, (bx, by, bar_w, bar_h), 1)

    # ── Q版繪製 helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _S(n, r, base=18):
        return max(1, int(n * r / base))

    def _draw_frozen(self, screen, sx, sy, r):
        ICE = (148, 205, 242)
        pygame.draw.circle(screen, ICE, (sx, sy), r)
        pygame.draw.circle(screen, (210, 238, 255), (sx, sy), r, 3)
        S = lambda n: self._S(n, r)
        for i in range(6):
            a = math.radians(i * 60)
            ix = sx + int(math.cos(a) * r)
            iy = sy + int(math.sin(a) * r)
            pygame.draw.line(screen, (210, 238, 255), (sx, sy), (ix, iy), S(2))

    def _draw_chibi_marine(self, screen, sx, sy, r, hurt):
        """海軍 Q版：藍色制服大頭小兵，誇大海軍帽"""
        S = lambda n: self._S(n, r)
        UNIFORM = (255, 180, 180) if hurt else (85, 118, 195)
        CAP     = (28, 45, 115)
        SKIN    = (255, 200, 180) if hurt else (215, 178, 128)
        WHITE_C = (238, 238, 245)

        hy  = sy - S(8)
        hr  = S(11)   # 大頭

        # 短腿
        lt = sy + S(12)
        pygame.draw.rect(screen, (22, 35, 90),
                         (sx - S(8), lt, S(7), S(10)), border_radius=S(2))
        pygame.draw.rect(screen, (22, 35, 90),
                         (sx + S(1), lt, S(7), S(10)), border_radius=S(2))
        pygame.draw.ellipse(screen, (18, 12, 8),
                            (sx - S(9), lt + S(9), S(9), S(5)))
        pygame.draw.ellipse(screen, (18, 12, 8),
                            (sx + S(0), lt + S(9), S(9), S(5)))

        # 制服身體（圓潤Q版）
        bw, bh = S(20), S(18)
        pygame.draw.rect(screen, UNIFORM,
                         (sx - bw // 2, sy - S(4), bw, bh), border_radius=S(5))
        # 白色正義大衣（兩側）
        pygame.draw.polygon(screen, WHITE_C, [
            (sx - bw // 2 - S(2), sy),
            (sx - bw // 2 - S(6), sy + S(14)),
            (sx - bw // 2 + S(2), sy + S(10)),
        ])
        pygame.draw.polygon(screen, WHITE_C, [
            (sx + bw // 2 + S(2), sy),
            (sx + bw // 2 + S(6), sy + S(14)),
            (sx + bw // 2 - S(2), sy + S(10)),
        ])
        # 手臂
        pygame.draw.rect(screen, SKIN,
                         (sx - bw // 2 - S(5), sy - S(2), S(5), S(10)), border_radius=S(2))
        pygame.draw.circle(screen, SKIN, (sx - bw // 2 - S(3), sy + S(8)), S(4))
        pygame.draw.rect(screen, SKIN,
                         (sx + bw // 2, sy - S(2), S(5), S(10)), border_radius=S(2))
        pygame.draw.circle(screen, SKIN, (sx + bw // 2 + S(2), sy + S(8)), S(4))

        # 大頭
        pygame.draw.circle(screen, SKIN, (sx, hy), hr)

        # 誇大海軍帽
        cw = hr * 2 + S(8)
        cy2 = hy - hr + S(3)
        ch = S(9)
        pygame.draw.rect(screen, CAP,
                         (sx - cw // 2, cy2 - ch, cw, ch), border_radius=S(3))
        pygame.draw.rect(screen, CAP,
                         (sx - cw // 2 - S(4), cy2, cw + S(8), S(4)), border_radius=S(2))

        # Q版表情（瞪眼）
        ey = hy + S(2)
        eox = S(4)
        for ex in [sx - eox, sx + eox]:
            pygame.draw.circle(screen, (248, 246, 242), (ex, ey), S(4))
            pygame.draw.circle(screen, (20, 30, 80), (ex, ey), S(2))
            pygame.draw.circle(screen, (255, 255, 255), (ex - S(1), ey - S(1)), S(1))
        # 眉毛（嚴肅）
        pygame.draw.line(screen, (20, 15, 8),
                         (sx - eox - S(4), ey - S(5)), (sx - eox + S(2), ey - S(3)), S(2))
        pygame.draw.line(screen, (20, 15, 8),
                         (sx + eox - S(2), ey - S(3)), (sx + eox + S(4), ey - S(5)), S(2))
        # 嘴（嚴肅）
        pygame.draw.line(screen, (180, 145, 108),
                         (sx - S(4), hy + S(7)), (sx + S(4), hy + S(7)), S(1))

    def _draw_chibi_pirate(self, screen, sx, sy, r, hurt):
        """海賊 Q版：紅頭巾大頭海盜，叉腿持劍"""
        S = lambda n: self._S(n, r)
        BODY_C  = (255, 175, 175) if hurt else tuple(self.color)
        SKIN    = (255, 200, 175) if hurt else (210, 172, 125)
        BANDANA = (195, 38, 38)
        PANTS   = (55, 38, 25)
        SHOE    = (22, 15, 8)

        hy = sy - S(8)
        hr = S(11)

        # 短腿
        lt = sy + S(12)
        pygame.draw.rect(screen, PANTS,
                         (sx - S(8), lt, S(7), S(10)), border_radius=S(2))
        pygame.draw.rect(screen, PANTS,
                         (sx + S(1), lt, S(7), S(10)), border_radius=S(2))
        pygame.draw.ellipse(screen, SHOE, (sx - S(9), lt + S(9), S(9), S(5)))
        pygame.draw.ellipse(screen, SHOE, (sx + S(0), lt + S(9), S(9), S(5)))

        # 身體
        bw, bh = S(20), S(18)
        pygame.draw.rect(screen, BODY_C,
                         (sx - bw // 2, sy - S(4), bw, bh), border_radius=S(5))
        # 腰帶
        pygame.draw.rect(screen, (38, 28, 12),
                         (sx - bw // 2, sy + S(8), bw, S(4)), border_radius=S(1))
        # 手臂
        pygame.draw.rect(screen, SKIN,
                         (sx - bw // 2 - S(5), sy - S(2), S(5), S(10)), border_radius=S(2))
        pygame.draw.circle(screen, SKIN, (sx - bw // 2 - S(3), sy + S(8)), S(4))
        # 右手持劍
        pygame.draw.rect(screen, SKIN,
                         (sx + bw // 2, sy - S(4), S(5), S(10)), border_radius=S(2))
        pygame.draw.circle(screen, SKIN, (sx + bw // 2 + S(2), sy + S(6)), S(4))
        pygame.draw.line(screen, (188, 180, 162),
                         (sx + bw // 2 + S(3), sy + S(4)),
                         (sx + bw // 2 + S(12), sy - S(8)), S(2))
        pygame.draw.rect(screen, (88, 62, 30),
                         (sx + bw // 2 + S(1), sy + S(2), S(4), S(4)), border_radius=S(1))

        # 大頭
        pygame.draw.circle(screen, SKIN, (sx, hy), hr)

        # 紅色誇大頭巾
        brim_y = hy - hr + S(3)
        pygame.draw.rect(screen, BANDANA,
                         (sx - hr - S(2), brim_y - S(4), hr * 2 + S(4), S(8)), border_radius=S(3))
        # 頭巾結（右側）
        pygame.draw.circle(screen, BANDANA, (sx + hr + S(2), brim_y), S(5))
        pygame.draw.line(screen, BANDANA, (sx + hr + S(2), brim_y),
                         (sx + hr + S(8), brim_y + S(5)), S(2))
        pygame.draw.line(screen, BANDANA, (sx + hr + S(2), brim_y),
                         (sx + hr + S(8), brim_y - S(4)), S(2))

        # Q版表情（兇狠）
        ey = hy + S(3)
        eox = S(4)
        for ex in [sx - eox, sx + eox]:
            pygame.draw.circle(screen, (248, 244, 240), (ex, ey), S(4))
            pygame.draw.circle(screen, (28, 18, 10), (ex, ey), S(2))
            pygame.draw.circle(screen, (255, 255, 255), (ex - S(1), ey - S(1)), S(1))
        # V形眉毛（兇）
        pygame.draw.line(screen, (22, 14, 8),
                         (sx - eox - S(4), ey - S(5)), (sx - eox, ey - S(2)), S(2))
        pygame.draw.line(screen, (22, 14, 8),
                         (sx + eox, ey - S(2)), (sx + eox + S(4), ey - S(5)), S(2))
        # 露齒壞笑
        pygame.draw.arc(screen, (22, 14, 8),
                        (sx - S(5), hy + S(6), S(10), S(6)), math.pi * 1.1, math.pi * 1.9, S(2))
        pygame.draw.line(screen, (255, 252, 248),
                         (sx - S(3), hy + S(8)), (sx + S(3), hy + S(8)), S(1))

    def _draw_chibi_beast(self, screen, sx, sy, r, hurt):
        """海王類 Q版：大眼睛可怕海獸，大嘴巴，毛茸茸"""
        S = lambda n: self._S(n, r)
        FUR    = (255, 175, 160) if hurt else tuple(self.color)
        FUR_D  = tuple(max(0, c - 35) for c in (FUR if not hurt else self.color))
        EYE_C  = (255, 220, 20)
        TOOTH  = (245, 242, 235)

        hy = sy - S(5)
        hr = S(13)   # 頭超大（野獸是整個圓）

        # 毛茸身體（有紋路感）
        pygame.draw.circle(screen, FUR, (sx, sy), r)
        # 身體暗面
        pygame.draw.circle(screen, FUR_D, (sx + S(3), sy + S(3)), r - S(3))
        # 毛邊（鋸齒狀小圓）
        for i in range(8):
            a = math.radians(i * 45)
            fx = sx + int(math.cos(a) * (r - S(2)))
            fy = sy + int(math.sin(a) * (r - S(2)))
            pygame.draw.circle(screen, FUR, (fx, fy), S(4))

        # 耳朵（尖耳）
        pygame.draw.polygon(screen, FUR, [
            (sx - hr, sy - hr + S(2)),
            (sx - hr - S(5), sy - hr - S(6)),
            (sx - hr + S(4), sy - hr - S(2)),
        ])
        pygame.draw.polygon(screen, FUR, [
            (sx + hr, sy - hr + S(2)),
            (sx + hr + S(5), sy - hr - S(6)),
            (sx + hr - S(4), sy - hr - S(2)),
        ])

        # Q版大眼睛（兇猛）
        ey = sy - S(4)
        eox = S(6)
        for ex in [sx - eox, sx + eox]:
            pygame.draw.circle(screen, EYE_C, (ex, ey), S(5))
            pygame.draw.circle(screen, (30, 20, 10), (ex, ey + S(1)), S(3))
            pygame.draw.circle(screen, (255, 255, 255), (ex - S(1), ey - S(2)), S(1))
        # 粗眉毛（向下壓，兇）
        pygame.draw.line(screen, (22, 14, 8),
                         (sx - eox - S(5), ey - S(6)), (sx - eox + S(3), ey - S(2)), S(3))
        pygame.draw.line(screen, (22, 14, 8),
                         (sx + eox - S(3), ey - S(2)), (sx + eox + S(5), ey - S(6)), S(3))

        # 大嘴（帶牙齒）
        mouth_y = sy + S(4)
        pygame.draw.arc(screen, (22, 14, 8),
                        (sx - S(8), mouth_y - S(4), S(16), S(10)), 0, math.pi, S(3))
        for i, tx in enumerate([-S(5), -S(1), S(3)]):
            th = S(5) if i == 1 else S(3)
            pygame.draw.polygon(screen, TOOTH, [
                (sx + tx, mouth_y),
                (sx + tx + S(3), mouth_y),
                (sx + tx + S(2), mouth_y + th),
            ])

    def _draw_marine(self, screen, sx, sy, r, body_color):
        pass  # replaced by _draw_chibi_marine

    def _draw_pirate(self, screen, sx, sy, r, body_color):
        pass  # replaced by _draw_chibi_pirate
