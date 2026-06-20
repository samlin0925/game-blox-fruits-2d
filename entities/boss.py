import pygame
import math
from entities.base_entity import BaseEntity
from core.constants import WHITE, RED, YELLOW, ORANGE
from config import WORLD_WIDTH, WORLD_HEIGHT

# ── Boss sprite helpers ──────────────────────────────────────────────────────

def _S(n, r, base=50):
    return max(1, int(n * r / base))


def _hurt_flash(screen, sx, sy, r):
    flash = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    pygame.draw.circle(flash, (255, 255, 255, 110), (r * 2, r * 2), r)
    screen.blit(flash, (sx - r * 2, sy - r * 2))


def _draw_akainu(screen, sx, sy, r, aa, phase, hurt):
    """赤犬 Q版：大頭壯漢，超大海軍帽，白大衣披肩，右手岩漿拳"""
    def S(n): return _S(n, r)
    import math as _m

    SKIN   = (75, 44, 33)
    COAT   = (234, 234, 240)
    COAT_D = (190, 194, 205)
    CAP    = (212, 222, 240)
    HAIR   = (20, 14, 10)
    PANTS  = (28, 22, 22)
    SHOE   = (16, 10, 8)
    MAGMA  = (255, 68, 0)
    LAVA   = (255, 188, 42)

    # 岩漿光環
    n_pts = 6 if phase == 2 else 4
    for i in range(n_pts):
        a = _m.radians(aa * (2 if phase == 2 else 1) + i * (360 // n_pts))
        ax = sx + int(_m.cos(a) * (r + S(13)))
        ay = sy + int(_m.sin(a) * (r + S(13)))
        pygame.draw.circle(screen, MAGMA, (ax, ay), S(9))
        pygame.draw.circle(screen, LAVA if phase == 2 else (255, 200, 80), (ax, ay), S(5))

    # Q版：腳短小
    lt = sy + S(18)
    lh, lw = S(20), S(10)
    pygame.draw.rect(screen, PANTS, (sx - S(14), lt, lw, lh), border_radius=S(4))
    pygame.draw.rect(screen, PANTS, (sx + S(4), lt, lw, lh), border_radius=S(4))
    pygame.draw.ellipse(screen, SHOE, (sx - S(16), lt + lh - S(5), S(14), S(7)))
    pygame.draw.ellipse(screen, SHOE, (sx + S(2), lt + lh - S(5), S(14), S(7)))

    # Q版大身體（圓潤）
    hy = sy - S(22)
    hr = S(18)   # 大頭！
    body_w, body_h = S(30), S(28)
    pygame.draw.rect(screen, SKIN,
                     (sx - body_w // 2, sy - S(8), body_w, body_h), border_radius=S(8))

    # 白大衣（披肩式，更寬）
    coat_pts = [
        (sx - S(38), hy + hr - S(2)),
        (sx + S(38), hy + hr - S(2)),
        (sx + S(22), sy + S(22)),
        (sx - S(22), sy + S(22)),
    ]
    pygame.draw.polygon(screen, COAT, coat_pts)
    pygame.draw.polygon(screen, COAT_D, coat_pts, S(2))
    pygame.draw.line(screen, COAT_D, (sx, hy + hr + S(2)), (sx, sy + S(18)), S(2))

    # 手臂（粗壯）
    at = sy - S(8)
    ah = S(24)
    pygame.draw.rect(screen, SKIN, (sx - S(38), at, S(10), ah), border_radius=S(4))
    pygame.draw.circle(screen, SKIN, (sx - S(33), at + ah), S(7))
    pygame.draw.rect(screen, MAGMA, (sx + S(28), at, S(10), ah), border_radius=S(4))
    fist_c = LAVA if phase == 2 else (220, 92, 12)
    pygame.draw.circle(screen, fist_c, (sx + S(33), at + ah), S(9))
    if phase == 2:
        pygame.draw.circle(screen, (255, 235, 130), (sx + S(33), at + ah), S(5))

    # 大頭
    pygame.draw.circle(screen, SKIN, (sx, hy), hr)

    # 捲髮（黑色）
    pygame.draw.ellipse(screen, HAIR,
                        (sx - hr + S(2), hy - hr - S(2), (hr - S(2)) * 2, hr + S(3)))
    for dx, dyo in [(-S(11), S(3)), (S(11), S(3)), (-S(4), -S(3)), (S(4), -S(3))]:
        pygame.draw.circle(screen, HAIR, (sx + dx, hy - hr + dyo), S(7))

    # 超大海軍帽（Q版誇張比例）
    cw = hr * 2 + S(12)
    cy2 = hy - hr + S(4)
    ch = S(14)
    pygame.draw.rect(screen, CAP, (sx - cw // 2, cy2 - ch, cw, ch), border_radius=S(4))
    pygame.draw.rect(screen, CAP,
                     (sx - cw // 2 - S(7), cy2, cw + S(14), S(5)), border_radius=S(3))
    pygame.draw.rect(screen, COAT_D,
                     (sx - cw // 2 - S(7), cy2, cw + S(14), S(5)), S(1), border_radius=S(3))
    # 帽子上的正義徽章
    pygame.draw.circle(screen, COAT_D, (sx, cy2 - ch // 2), S(5))
    pygame.draw.circle(screen, (185, 192, 210), (sx, cy2 - ch // 2), S(3))

    # Q版憤怒表情
    ey = hy + S(3)
    eox = S(6)
    # 粗眉毛（憤怒下壓）
    pygame.draw.line(screen, HAIR, (sx - eox - S(7), ey - S(7)), (sx - eox + S(2), ey - S(2)), S(3))
    pygame.draw.line(screen, HAIR, (sx + eox - S(2), ey - S(2)), (sx + eox + S(7), ey - S(7)), S(3))
    # Q版大圓眼
    pygame.draw.circle(screen, (250, 248, 244), (sx - eox, ey), S(5))
    pygame.draw.circle(screen, (18, 12, 8), (sx - eox, ey), S(3))
    pygame.draw.circle(screen, (250, 248, 244), (sx + eox, ey), S(5))
    pygame.draw.circle(screen, (18, 12, 8), (sx + eox, ey), S(3))
    # 高光
    pygame.draw.circle(screen, (255, 255, 255), (sx - eox - S(1), ey - S(2)), S(1))
    pygame.draw.circle(screen, (255, 255, 255), (sx + eox - S(1), ey - S(2)), S(1))
    # 嚴肅嘴
    pygame.draw.line(screen, HAIR, (sx - S(6), hy + S(13)), (sx + S(6), hy + S(13)), S(2))

    # 第2階段岩漿滴落
    if phase == 2:
        for i in range(4):
            dx2 = sx - S(8) + i * S(7)
            dh = S(10 + i * 2)
            pygame.draw.ellipse(screen, MAGMA, (dx2 - S(3), sy + S(22), S(6), dh))

    if hurt:
        _hurt_flash(screen, sx, sy, r)


def _draw_kizaru(screen, sx, sy, r, aa, phase, hurt):
    """黃猿 Q版：細高身材，超大墨鏡，白大衣，金色光芒"""
    def S(n): return _S(n, r, 48)
    import math as _m

    SKIN  = (208, 182, 145)
    COAT  = (240, 240, 244)
    COAT_D = (196, 200, 212)
    HAIR  = (28, 22, 16)
    PANTS = (35, 32, 28)
    SHOE  = (22, 18, 14)
    GOLD  = (255, 228, 50)
    LGOLD = (255, 248, 155)
    GLASS = (22, 18, 14)

    # 黃金光芒
    n_pts = 8 if phase == 2 else 5
    for i in range(n_pts):
        a = _m.radians(aa * (3 if phase == 2 else 1.5) + i * (360 // n_pts))
        dist = r + S(10 + (i % 2) * 6)
        ax = sx + int(_m.cos(a) * dist)
        ay = sy + int(_m.sin(a) * dist)
        pygame.draw.circle(screen, GOLD, (ax, ay), S(7))
        pygame.draw.circle(screen, LGOLD, (ax, ay), S(3))
    if phase == 2:
        for i in range(4):
            a = _m.radians(aa * 4 + i * 90)
            bx = sx + int(_m.cos(a) * (r + S(24)))
            by = sy + int(_m.sin(a) * (r + S(24)))
            pygame.draw.line(screen, GOLD, (sx, sy), (bx, by), S(3))

    hy = sy - S(24)
    hr = S(16)  # Q版大頭

    # Q版短腿
    lt = sy + S(18)
    lh, lw = S(20), S(9)
    pygame.draw.rect(screen, PANTS, (sx - S(12), lt, lw, lh), border_radius=S(3))
    pygame.draw.rect(screen, PANTS, (sx + S(3), lt, lw, lh), border_radius=S(3))
    pygame.draw.ellipse(screen, SHOE, (sx - S(14), lt + lh - S(4), S(13), S(7)))
    pygame.draw.ellipse(screen, SHOE, (sx + S(1), lt + lh - S(4), S(13), S(7)))

    # 大衣（細長身材）
    coat_top = hy + hr - S(2)
    coat_pts = [
        (sx - S(24), coat_top),
        (sx + S(24), coat_top),
        (sx + S(18), sy + S(22)),
        (sx - S(18), sy + S(22)),
    ]
    pygame.draw.polygon(screen, COAT, coat_pts)
    pygame.draw.polygon(screen, COAT_D, coat_pts, S(2))
    pygame.draw.line(screen, COAT_D, (sx, coat_top + S(2)), (sx, sy + S(18)), S(2))

    # 細手臂
    at = sy - S(8)
    ah = S(22)
    arm_c = SKIN if phase == 1 else (220, 200, 160)
    pygame.draw.rect(screen, arm_c, (sx - S(30), at, S(8), ah), border_radius=S(3))
    pygame.draw.circle(screen, arm_c, (sx - S(26), at + ah), S(5))
    pygame.draw.rect(screen, arm_c, (sx + S(22), at, S(8), ah), border_radius=S(3))
    fist_c = GOLD if phase == 2 else arm_c
    pygame.draw.circle(screen, fist_c, (sx + S(26), at + ah), S(6))
    if phase == 2:
        pygame.draw.circle(screen, LGOLD, (sx + S(26), at + ah), S(3))

    # 細長身體
    pygame.draw.rect(screen, SKIN, (sx - S(12), sy - S(10), S(24), S(30)), border_radius=S(5))

    # 大頭（Q版）
    pygame.draw.circle(screen, SKIN, (sx, hy), hr)

    # 梳後的黑髮
    pygame.draw.ellipse(screen, HAIR, (sx - hr + S(2), hy - hr, hr * 2 - S(4), hr + S(4)))
    pygame.draw.circle(screen, HAIR, (sx + S(8), hy - hr + S(2)), S(8))

    # 超大墨鏡（Q版誇張）——黃猿最標誌性特徵
    sg_y = hy + S(2)
    sg_h = S(6)
    sg_w = hr + S(5)
    pygame.draw.rect(screen, GLASS, (sx - sg_w, sg_y - sg_h // 2, sg_w * 2, sg_h), border_radius=S(3))
    # 鏡架橋
    pygame.draw.line(screen, (45, 40, 35), (sx - S(2), sg_y), (sx + S(2), sg_y), S(1))
    # 外框
    pygame.draw.rect(screen, (42, 38, 32),
                     (sx - sg_w, sg_y - sg_h // 2, sg_w * 2, sg_h), S(1), border_radius=S(3))
    # 玻璃反光（讓墨鏡有光澤感）
    pygame.draw.line(screen, (55, 52, 45),
                     (sx - sg_w + S(2), sg_y - sg_h // 2 + S(1)),
                     (sx - S(4), sg_y - sg_h // 2 + S(1)), S(1))
    pygame.draw.line(screen, (55, 52, 45),
                     (sx + S(4), sg_y - sg_h // 2 + S(1)),
                     (sx + sg_w - S(2), sg_y - sg_h // 2 + S(1)), S(1))

    # 鼻子 + 隨意微笑
    pygame.draw.circle(screen, (178, 152, 115), (sx, hy + S(8)), S(2))
    pygame.draw.arc(screen, (155, 130, 96),
                    (sx - S(5), hy + S(10), S(10), S(7)), _m.pi * 1.1, _m.pi * 1.9, max(1, S(1)))

    if hurt:
        _hurt_flash(screen, sx, sy, r)


def _draw_aokiji(screen, sx, sy, r, aa, phase, hurt):
    """青雉 Q版：大頭慵懶臉，超大眼袋，腳邊冰柱，海軍大衣"""
    def S(n): return _S(n, r, 52)
    import math as _m

    SKIN  = (162, 135, 102)
    COAT  = (235, 238, 246)
    COAT_D = (190, 196, 214)
    HAIR  = (22, 18, 14)
    PANTS = (32, 28, 26)
    SHOE  = (18, 14, 12)
    ICE   = (128, 198, 240)
    ICEL  = (208, 238, 255)
    ICED  = (88, 158, 210)

    hy = sy - S(22)
    hr = S(18)  # Q版超大頭

    # 冰晶光環
    n_pts = 6 if phase == 2 else 4
    for i in range(n_pts):
        a = _m.radians(aa + i * (360 // n_pts))
        ax = sx + int(_m.cos(a) * (r + S(12)))
        ay = sy + int(_m.sin(a) * (r + S(12)))
        pygame.draw.circle(screen, ICE, (ax, ay), S(8))
        pygame.draw.circle(screen, ICEL, (ax, ay), S(4))
    if phase == 2:
        for i in range(8):
            a = _m.radians(aa * 2 + i * 45)
            for length in range(r + S(10), r + S(28), S(5)):
                spx = sx + int(_m.cos(a) * length)
                spy = sy + int(_m.sin(a) * length)
                sr2 = max(1, S(7) - (length - r - S(10)) // S(4))
                pygame.draw.circle(screen, ICE, (spx, spy), sr2)

    # 腳邊冰柱（最標誌性的視覺元素）
    lt = sy + S(18)
    for ix, is_tall in [(-S(18), True), (S(12), False), (-S(34), False)]:
        iw = S(7)
        ih = S(20) if is_tall else S(13)
        pygame.draw.rect(screen, ICE, (sx + ix - iw // 2, lt, iw, ih), border_radius=S(2))
        pygame.draw.polygon(screen, ICEL, [
            (sx + ix, lt - S(9) if is_tall else lt - S(6)),
            (sx + ix - iw // 2, lt),
            (sx + ix + iw // 2, lt),
        ])
        pygame.draw.line(screen, ICEL,
                         (sx + ix - iw // 3, lt + S(2)),
                         (sx + ix - iw // 3, lt + ih - S(2)), max(1, S(2)))

    # Q版短腿
    lh, lw = S(20), S(10)
    pygame.draw.rect(screen, PANTS, (sx - S(14), lt, lw, lh), border_radius=S(3))
    pygame.draw.rect(screen, PANTS, (sx + S(4), lt, lw, lh), border_radius=S(3))
    pygame.draw.ellipse(screen, SHOE, (sx - S(16), lt + lh - S(5), S(13), S(7)))
    pygame.draw.ellipse(screen, SHOE, (sx + S(3), lt + lh - S(5), S(13), S(7)))

    # 大衣（隨意敞開）
    coat_top = hy + hr - S(2)
    coat_pts = [
        (sx - S(30), coat_top),
        (sx + S(30), coat_top),
        (sx + S(22), sy + S(22)),
        (sx - S(22), sy + S(22)),
    ]
    pygame.draw.polygon(screen, COAT, coat_pts)
    pygame.draw.polygon(screen, COAT_D, coat_pts, S(2))
    pygame.draw.line(screen, COAT_D, (sx, coat_top + S(2)), (sx, sy + S(16)), S(2))

    # 手臂（懶散姿勢）
    at = sy - S(8)
    ah = S(24)
    pygame.draw.rect(screen, SKIN, (sx - S(34), at + S(4), S(9), ah - S(4)), border_radius=S(3))
    pygame.draw.circle(screen, SKIN, (sx - S(30), at + ah), S(6))
    pygame.draw.rect(screen, SKIN, (sx + S(25), at, S(9), ah), border_radius=S(3))
    fist_c = ICED if phase >= 1 else SKIN
    pygame.draw.circle(screen, fist_c, (sx + S(30), at + ah), S(7))
    if phase == 2:
        pygame.draw.circle(screen, ICEL, (sx + S(30), at + ah), S(4))

    # 身體
    pygame.draw.rect(screen, SKIN, (sx - S(14), sy - S(10), S(28), S(30)), border_radius=S(5))

    # 超大頭（Q版）
    pygame.draw.circle(screen, SKIN, (sx, hy), hr)

    # 輕描淡寫的頭髮
    pygame.draw.ellipse(screen, HAIR, (sx - hr + S(2), hy - hr, hr * 2 - S(4), hr + S(3)))
    pygame.draw.circle(screen, HAIR, (sx - S(7), hy - hr + S(2)), S(8))
    pygame.draw.circle(screen, HAIR, (sx + S(5), hy - hr - S(1)), S(7))

    # 海軍帽（稍微歪戴，很休閒）
    cw = hr * 2 + S(8)
    cy2 = hy - hr + S(5)
    ch = S(12)
    pygame.draw.rect(screen, (212, 220, 238),
                     (sx - cw // 2 + S(3), cy2 - ch, cw, ch), border_radius=S(3))
    pygame.draw.rect(screen, (212, 220, 238),
                     (sx - cw // 2 - S(3) + S(3), cy2, cw + S(6), S(5)), border_radius=S(3))
    pygame.draw.rect(screen, COAT_D,
                     (sx - cw // 2 - S(3) + S(3), cy2, cw + S(6), S(5)), S(1), border_radius=S(3))

    # Q版「昏昏欲睡」表情（眼皮厚重下垂）
    ey = hy + S(4)
    eox = S(6)
    er = S(5)
    # 眼白
    pygame.draw.circle(screen, (250, 248, 244), (sx - eox, ey), er)
    pygame.draw.circle(screen, (250, 248, 244), (sx + eox, ey), er)
    # 虹膜（被眼皮半遮，顯露下半部分）
    pygame.draw.circle(screen, (22, 18, 14), (sx - eox, ey + S(1)), er - S(1))
    pygame.draw.circle(screen, (22, 18, 14), (sx + eox, ey + S(1)), er - S(1))
    # 超厚眼皮線（昏睡感）
    pygame.draw.line(screen, HAIR, (sx - eox - S(5), ey - S(2)), (sx - eox + S(5), ey - S(1)), S(3))
    pygame.draw.line(screen, HAIR, (sx + eox - S(5), ey - S(1)), (sx + eox + S(5), ey - S(2)), S(3))
    # 眼袋（Q版誇張）
    pygame.draw.arc(screen, (145, 115, 82),
                    (sx - eox - S(4), ey, S(8), S(4)), 0, _m.pi, S(1))
    pygame.draw.arc(screen, (145, 115, 82),
                    (sx + eox - S(4), ey, S(8), S(4)), 0, _m.pi, S(1))
    # 高光
    pygame.draw.circle(screen, (255, 255, 255), (sx - eox - S(1), ey - S(2)), S(1))
    pygame.draw.circle(screen, (255, 255, 255), (sx + eox - S(1), ey - S(2)), S(1))

    # 鼻子
    pygame.draw.circle(screen, (148, 118, 84), (sx, hy + S(10)), S(2))
    # 沒睡醒的嘴（微張）
    pygame.draw.arc(screen, (128, 98, 70),
                    (sx - S(5), hy + S(12), S(10), S(6)), 0, _m.pi, S(1))

    # 第2階段：嘴裡呼出冰霧
    if phase == 2:
        for i in range(5):
            a = _m.radians(-85 + i * 18)
            bx = sx + int(_m.cos(a) * S(14 + i * 5))
            by2 = hy + hr + int(_m.sin(a) * S(14 + i * 5))
            pygame.draw.circle(screen, ICE, (bx, by2), S(4 - i // 2))

    if hurt:
        _hurt_flash(screen, sx, sy, r)


def _draw_boss_generic(screen, sx, sy, r, color, aa, phase, hurt):
    aura_c = YELLOW if phase == 1 else (255, 80, 30)
    for i in range(3):
        a = math.radians(aa + i * 120)
        ax = sx + int(math.cos(a) * (r + 8))
        ay = sy + int(math.sin(a) * (r + 8))
        pygame.draw.circle(screen, aura_c, (ax, ay), 6)
    c = (255, 255, 255) if hurt else color
    pygame.draw.circle(screen, c, (sx, sy), r)
    inner = tuple(min(255, v + 60) for v in color)
    pygame.draw.circle(screen, inner, (sx, sy), r // 2)
    pygame.draw.circle(screen, aura_c, (sx, sy), r, 3)
    if hurt:
        _hurt_flash(screen, sx, sy, r)


# ─────────────────────────────────────────────────────────────────────────────
class Boss(BaseEntity):
    def __init__(self, x: float, y: float, data: dict):
        r = data.get("size", 50)
        super().__init__(x, y, r * 2, r * 2)
        self.data = data
        self.name = data["name"]
        self.title = data.get("title", "")
        self.max_health = data["health"]
        self.health = self.max_health
        self.attack = data["attack"]
        self.defense = data.get("defense", 20)
        self.speed = data["speed"]
        self.exp_reward = data["exp_reward"]
        self.gold_reward = data["gold_reward"]
        self.fragment_reward = data.get("fragment_reward", {})
        self.color = tuple(data.get("color", [180, 30, 30]))
        self.radius = r
        self.phase = 1
        self.phase2_threshold = data.get("phase2_threshold", 0.5)
        self.skills = data.get("skills", [])
        self.skill_timers = {s["name"]: 0.0 for s in self.skills}
        self.ai = None
        self.hurt_timer = 0.0
        self.aura_angle = 0.0
        self.freeze_timer = 0.0
        self.attack_cooldown = 0.0
        self.attack_cooldown_max = data.get("attack_cooldown", 1.2)

    def can_attack(self) -> bool:
        return self.attack_cooldown <= 0

    def reset_attack_cooldown(self):
        self.attack_cooldown = self.attack_cooldown_max

    def get_available_skills(self):
        return [s for s in self.skills
                if not s.get("phase2_only", False) or self.phase == 2]

    def take_damage(self, amount: int) -> int:
        damage = max(1, amount - self.defense // 3)
        self.health -= damage
        self.hurt_timer = 0.15
        hp_ratio = self.health / self.max_health
        if self.phase == 1 and hp_ratio <= self.phase2_threshold:
            self.phase = 2
            self.speed = int(self.speed * 1.3)
        if self.health <= 0:
            self.health = 0
            self.alive = False
        return damage

    def update(self, dt: float):
        if self.freeze_timer > 0:
            self.freeze_timer -= dt
            self.vx = 0
            self.vy = 0
        super().update(dt)
        self.clamp_to_world(WORLD_WIDTH, WORLD_HEIGHT)
        for name in self.skill_timers:
            if self.skill_timers[name] > 0:
                self.skill_timers[name] -= dt
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        self.aura_angle += dt * 90

    def can_use_skill(self, skill: dict) -> bool:
        return self.skill_timers.get(skill["name"], 0) <= 0

    def use_skill(self, skill: dict):
        self.skill_timers[skill["name"]] = skill["cooldown"]

    def draw(self, screen, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        r = self.radius
        bid = self.data.get("id", "")
        hurt = self.hurt_timer > 0
        ph = self.phase
        aa = self.aura_angle

        if bid == "akainu":
            _draw_akainu(screen, sx, sy, r, aa, ph, hurt)
        elif bid == "kizaru":
            _draw_kizaru(screen, sx, sy, r, aa, ph, hurt)
        elif bid == "aokiji":
            _draw_aokiji(screen, sx, sy, r, aa, ph, hurt)
        else:
            _draw_boss_generic(screen, sx, sy, r, self.color, aa, ph, hurt)

        # HP bar
        bar_w = r * 3
        bar_h = 10
        bx = sx - bar_w // 2
        by = sy - r - 30
        pygame.draw.rect(screen, (60, 0, 0), (bx, by, bar_w, bar_h))
        hp_w = int(bar_w * self.health / self.max_health)
        hp_color = (220, 50, 50) if ph == 1 else (255, 120, 0)
        pygame.draw.rect(screen, hp_color, (bx, by, hp_w, bar_h))
        pygame.draw.rect(screen, YELLOW, (bx, by, bar_w, bar_h), 2)

        # Name label
        from utils.font_helper import get_font
        font = get_font(13, bold=True)
        label = f"{self.name}  {'★★ 第2階段' if ph == 2 else ''}"
        ls = font.render(label, True, YELLOW if ph == 2 else (220, 210, 180))
        screen.blit(ls, (sx - ls.get_width() // 2, by - 18))
