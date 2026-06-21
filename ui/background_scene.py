"""
4 種程式繪製動態選單背景，每次啟動隨機選一種。

場景：
  0 - 星空海洋   (深夜、星星閃爍、月光水面、緩慢波浪)
  1 - 大風暴     (翻騰烏雲、閃電、洶湧巨浪)
  2 - 日落港口   (橙紅晚霞、剪影海島、帆船、平靜波光)
  3 - 海軍總部   (藍白建築輪廓、海軍旗飄揚、巡邏探照燈)
"""

import pygame
import math
import random


class _Star:
    def __init__(self, w, h):
        self.x = random.randint(0, w)
        self.y = random.randint(0, h)
        self.r = random.choice([1, 1, 1, 2])
        self.phase = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(0.8, 2.5)

    def brightness(self, t):
        return 0.5 + 0.5 * math.sin(self.phase + t * self.speed)


class _Cloud:
    def __init__(self, w, h, dark=False):
        self.w = w
        self.h = h
        self.y = random.randint(20, h // 2)
        self.x = random.uniform(-200, w + 200)
        self.speed = random.uniform(18, 55)
        self.width = random.randint(120, 300)
        self.height = random.randint(40, 90)
        self.dark = dark
        self.color_base = (40, 40, 55) if dark else (210, 200, 190)

    def update(self, dt, w):
        self.x += self.speed * dt
        if self.x > w + 250:
            self.x = -250
            self.y = random.randint(20, self.h // 4)


class _Wave:
    def __init__(self, y_base, amplitude, speed, color, phase=0.0):
        self.y_base = y_base
        self.amplitude = amplitude
        self.speed = speed
        self.color = color
        self.phase = phase


class BackgroundScene:
    def __init__(self, w: int, h: int, scene_id: int = -1):
        self.w = w
        self.h = h
        self.scene_id = random.choice([2, 2, 3, 3, 0]) if scene_id < 0 else scene_id
        self.t = 0.0
        self._lightning_timer = 0.0
        self._lightning_flash = 0.0
        self._searchlight_angle = 0.0
        self._setup()

    def _setup(self):
        w, h = self.w, self.h
        sid = self.scene_id

        # ── 場景0：星空海洋 ──────────────────────────────
        if sid == 0:
            self._stars = [_Star(w, h) for _ in range(180)]
            self._waves = [
                _Wave(h * 0.68, 14, 0.55, (15, 40, 80),  0.0),
                _Wave(h * 0.72, 10, 0.80, (20, 55, 100), 1.1),
                _Wave(h * 0.76, 7,  1.10, (28, 70, 120), 0.5),
                _Wave(h * 0.82, 5,  1.40, (35, 85, 140), 2.2),
                _Wave(h * 0.90, 3,  1.70, (45, 100,155), 3.0),
            ]
            self._moon_x = w * 0.78
            self._moon_y = h * 0.18

        # ── 場景1：大風暴 ─────────────────────────────────
        elif sid == 1:
            self._clouds = [_Cloud(w, h, dark=True) for _ in range(14)]
            self._waves = [
                _Wave(h * 0.60, 30, 1.3, (20, 30, 50),  0.0),
                _Wave(h * 0.66, 22, 1.8, (25, 38, 65),  0.7),
                _Wave(h * 0.73, 16, 2.2, (30, 48, 80),  1.5),
                _Wave(h * 0.80, 10, 2.6, (38, 58, 95),  2.4),
                _Wave(h * 0.88, 6,  3.0, (48, 70, 110), 3.3),
            ]
            self._rain_drops = [
                (random.randint(0, w), random.uniform(0, h),
                 random.uniform(6, 14)) for _ in range(120)
            ]
            self._lightning_timer = random.uniform(2, 5)

        # ── 場景2：日落港口 ───────────────────────────────
        elif sid == 2:
            self._clouds = [_Cloud(w, h, dark=False) for _ in range(8)]
            self._waves = [
                _Wave(h * 0.70, 8,  0.45, (180, 80, 30),  0.0),
                _Wave(h * 0.75, 6,  0.65, (190, 95, 40),  0.8),
                _Wave(h * 0.80, 4,  0.85, (200, 110, 55), 1.6),
                _Wave(h * 0.86, 3,  1.05, (210, 130, 70), 2.4),
                _Wave(h * 0.92, 2,  1.25, (220, 150, 90), 3.2),
            ]
            # 帆船位置
            self._ship_x = w * 0.75
            self._ship_y_base = h * 0.62
            # 海島輪廓點 (剪影)
            self._island = [
                (w * 0.05, h * 0.68), (w * 0.08, h * 0.58),
                (w * 0.13, h * 0.52), (w * 0.18, h * 0.55),
                (w * 0.23, h * 0.62), (w * 0.26, h * 0.70),
            ]

        # ── 場景3：海軍總部 ───────────────────────────────
        elif sid == 3:
            self._stars = [_Star(w, h // 2) for _ in range(60)]
            self._waves = [
                _Wave(h * 0.78, 6,  0.50, (40, 80, 140),  0.0),
                _Wave(h * 0.83, 4,  0.75, (50, 95, 160),  1.2),
                _Wave(h * 0.88, 3,  1.00, (60, 110, 175), 2.4),
                _Wave(h * 0.93, 2,  1.30, (70, 125, 190), 3.6),
            ]
            self._flag_angle = 0.0
            self._searchlight_angle = 0.0

    # ── 公用繪製波浪 ──────────────────────────────────────
    def _draw_waves(self, screen):
        w = self.w
        for wv in self._waves:
            pts = [(0, self.h)]
            for x in range(0, w + 10, 6):
                y = wv.y_base + wv.amplitude * math.sin(
                    x * 0.012 + self.t * wv.speed + wv.phase)
                pts.append((x, int(y)))
            pts.append((w, self.h))
            pygame.draw.polygon(screen, wv.color, pts)

    # ── 更新 ──────────────────────────────────────────────
    def update(self, dt: float):
        self.t += dt
        if self.scene_id == 1:
            self._lightning_timer -= dt
            if self._lightning_timer <= 0:
                self._lightning_flash = 0.12
                self._lightning_timer = random.uniform(3, 8)
            if self._lightning_flash > 0:
                self._lightning_flash -= dt
            drops = self._rain_drops
            self._rain_drops = [
                (x, (y + spd * 60 * dt) % self.h, spd)
                for x, y, spd in drops
            ]
            for c in self._clouds:
                c.update(dt, self.w)
        elif self.scene_id == 2:
            for c in self._clouds:
                c.update(dt, self.w)
        elif self.scene_id == 3:
            self._searchlight_angle += dt * 0.4

    # ── 繪製 ──────────────────────────────────────────────
    def draw(self, screen):
        sid = self.scene_id
        if sid == 0:
            self._draw_starry_ocean(screen)
        elif sid == 1:
            self._draw_storm(screen)
        elif sid == 2:
            self._draw_sunset_port(screen)
        elif sid == 3:
            self._draw_marine_hq(screen)

    # ═══════════════════════════════════════════════════════
    def _draw_starry_ocean(self, screen):
        w, h = self.w, self.h
        # 天空漸層（深藍→靛藍）
        for y in range(int(h * 0.75)):
            r = max(0, int(5 + y * 0.12))
            g = max(0, int(8 + y * 0.06))
            b = min(255, int(30 + y * 0.38))
            pygame.draw.line(screen, (r, g, b), (0, y), (w, y))

        # 月亮
        mx, my = int(self._moon_x), int(self._moon_y)
        glow_r = 55 + int(8 * math.sin(self.t * 0.5))
        pygame.draw.circle(screen, (40, 50, 80), (mx, my), glow_r)
        pygame.draw.circle(screen, (200, 210, 180), (mx, my), 34)
        pygame.draw.circle(screen, (230, 235, 210), (mx, my), 30)
        pygame.draw.circle(screen, (100, 105, 90), (mx - 8, my - 6), 7)
        pygame.draw.circle(screen, (100, 105, 90), (mx + 12, my + 4), 5)

        # 月光水面反射
        refl_y = int(h * 0.68)
        for i in range(8):
            rx = mx + random.randint(-20, 20)
            ry = refl_y + i * 8
            rw = max(2, 24 - i * 3)
            alpha = max(30, 160 - i * 20)
            s = pygame.Surface((rw, 3), pygame.SRCALPHA)
            s.fill((200, 210, 180, alpha))
            screen.blit(s, (rx - rw // 2, ry))

        # 星星
        for star in self._stars:
            b = star.brightness(self.t)
            c = int(200 * b)
            pygame.draw.circle(screen, (c, c, int(c * 0.9)),
                                (star.x, star.y), star.r)

        self._draw_waves(screen)

        # 海水漸層（填充波浪下方）
        pygame.draw.rect(screen, (15, 40, 80), (0, int(h * 0.95), w, h))

    # ═══════════════════════════════════════════════════════
    def _draw_storm(self, screen):
        w, h = self.w, self.h

        # 閃電提亮
        if self._lightning_flash > 0:
            ratio = self._lightning_flash / 0.12
            bg = (int(40 + 60 * ratio), int(40 + 50 * ratio), int(60 + 60 * ratio))
        else:
            bg = (18, 18, 28)
        screen.fill(bg)

        # 烏雲
        for c in self._clouds:
            clr = (35 + int(self.t * 2 % 10), 32, 48)
            pygame.draw.ellipse(screen, clr,
                                (int(c.x) - c.width // 2, c.y,
                                 c.width, c.height))
            clr2 = (28, 26, 40)
            pygame.draw.ellipse(screen, clr2,
                                (int(c.x) - c.width // 3, c.y + 10,
                                 c.width // 2, c.height // 2))

        # 閃電
        if self._lightning_flash > 0.06:
            lx = random.randint(w // 4, w * 3 // 4)
            pts = [(lx, 0)]
            y = 0
            while y < h * 0.55:
                y += random.randint(20, 50)
                pts.append((lx + random.randint(-30, 30), y))
            if len(pts) > 1:
                pygame.draw.lines(screen, (255, 255, 200), False, pts, 2)
                pygame.draw.lines(screen, (220, 220, 255), False, pts, 1)

        # 雨滴
        for x, y, spd in self._rain_drops:
            ex = x + int(spd * 1.2)
            ey = y + int(spd * 3)
            pygame.draw.line(screen, (90, 120, 170),
                             (int(x), int(y)), (int(ex), int(ey)), 1)

        self._draw_waves(screen)
        pygame.draw.rect(screen, (20, 30, 50), (0, int(h * 0.95), w, h))

    # ═══════════════════════════════════════════════════════
    def _draw_sunset_port(self, screen):
        w, h = self.w, self.h

        # 天空漸層（橙→粉→紫）
        colors = [
            (255, 90, 20), (255, 130, 40), (255, 160, 80),
            (230, 140, 120), (180, 110, 160), (100, 80, 140),
        ]
        band = int(h * 0.7) // len(colors)
        for i, (r, g, b) in enumerate(colors):
            ni = min(i + 1, len(colors) - 1)
            nr, ng, nb = colors[ni]
            for dy in range(band):
                ratio = dy / band
                cr = int(r + (nr - r) * ratio)
                cg = int(g + (ng - g) * ratio)
                cb = int(b + (nb - b) * ratio)
                pygame.draw.line(screen, (cr, cg, cb),
                                 (0, i * band + dy), (w, i * band + dy))

        # 太陽
        sun_x = int(w * 0.62)
        sun_y = int(h * 0.38)
        pygame.draw.circle(screen, (255, 80, 10), (sun_x, sun_y), 46)
        pygame.draw.circle(screen, (255, 140, 30), (sun_x, sun_y), 38)
        pygame.draw.circle(screen, (255, 200, 80), (sun_x, sun_y), 28)
        # 太陽光線
        for i in range(12):
            angle = math.radians(i * 30 + self.t * 8)
            r1, r2 = 52, 70
            x1 = sun_x + int(math.cos(angle) * r1)
            y1 = sun_y + int(math.sin(angle) * r1)
            x2 = sun_x + int(math.cos(angle) * r2)
            y2 = sun_y + int(math.sin(angle) * r2)
            pygame.draw.line(screen, (255, 160, 50), (x1, y1), (x2, y2), 2)

        # 雲
        for c in self._clouds:
            alpha = 160
            clr = (250, 180, 120)
            pygame.draw.ellipse(screen, clr,
                                (int(c.x) - c.width // 2, c.y,
                                 c.width, c.height))
            clr2 = (255, 200, 140)
            pygame.draw.ellipse(screen, clr2,
                                (int(c.x) - c.width // 3, c.y - 10,
                                 c.width // 2, c.height // 2))

        # 海島剪影
        if len(self._island) > 2:
            island_pts = list(self._island) + [
                (self._island[-1][0], h), (self._island[0][0], h)
            ]
            pygame.draw.polygon(screen, (20, 15, 25), island_pts)
            # 椰子樹
            tx = int(self._island[2][0])
            ty = int(self._island[2][1])
            pygame.draw.line(screen, (25, 18, 10), (tx, ty), (tx - 10, ty - 40), 3)
            for angle in (-60, -30, 10, 40):
                rad = math.radians(angle - 90)
                lx = tx - 10 + int(math.cos(rad) * 22)
                ly = ty - 40 + int(math.sin(rad) * 22)
                pygame.draw.line(screen, (15, 35, 10),
                                 (tx - 10, ty - 40), (lx, ly), 2)

        # 帆船剪影
        ship_y = self._ship_y_base + 6 * math.sin(self.t * 0.6)
        sx = int(self._ship_x)
        sy = int(ship_y)
        hull = [(sx - 28, sy + 8), (sx + 28, sy + 8),
                (sx + 22, sy + 20), (sx - 22, sy + 20)]
        pygame.draw.polygon(screen, (25, 18, 12), hull)
        pygame.draw.line(screen, (25, 18, 12), (sx, sy + 8), (sx, sy - 40), 2)
        pygame.draw.polygon(screen, (40, 25, 15), [
            (sx, sy - 38), (sx + 24, sy + 6), (sx, sy + 6)])
        pygame.draw.polygon(screen, (35, 22, 12), [
            (sx, sy - 20), (sx - 16, sy + 2), (sx, sy + 2)])

        self._draw_waves(screen)
        pygame.draw.rect(screen, (180, 80, 30), (0, int(h * 0.96), w, h))

    # ═══════════════════════════════════════════════════════
    def _draw_marine_hq(self, screen):
        w, h = self.w, self.h

        # 天空（夜晚→黎明過渡）
        dawn_ratio = 0.5 + 0.5 * math.sin(self.t * 0.15)
        for y in range(int(h * 0.78)):
            r = int(5 + 40 * dawn_ratio * (y / (h * 0.78)))
            g = int(10 + 30 * dawn_ratio * (y / (h * 0.78)))
            b = int(35 + 60 * (y / (h * 0.78)))
            pygame.draw.line(screen, (r, g, b), (0, y), (w, y))

        # 星星（夜晚才亮）
        for star in self._stars:
            b_val = star.brightness(self.t) * (1 - dawn_ratio * 0.7)
            c = int(200 * b_val)
            if c > 20:
                pygame.draw.circle(screen, (c, c, int(c * 0.9)),
                                    (star.x, star.y), star.r)

        # 探照燈（兩道）— 單一 SRCALPHA surface 重複使用
        sl_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for i, base_ang in enumerate([0.0, math.pi]):
            ang = self._searchlight_angle + base_ang
            lx = int(w * (0.3 + i * 0.4))
            ly = int(h * 0.74)
            ex = lx + int(math.cos(ang) * 350)
            ey = ly + int(math.sin(ang) * 350 * 0.4)
            for width in range(5, 0, -1):
                alpha_val = 15 + (5 - width) * 5
                pygame.draw.line(sl_surf, (200, 220, 255, alpha_val),
                                 (lx, ly), (ex, ey), width * 3)
        screen.blit(sl_surf, (0, 0))

        # 海軍總部建築輪廓
        bldg_color = (30, 45, 90)
        bldg_lit   = (40, 60, 120)
        # 主樓
        pygame.draw.rect(screen, bldg_color, (w // 2 - 100, int(h * 0.38), 200, int(h * 0.38)))
        # 圓頂
        pygame.draw.circle(screen, bldg_color, (w // 2, int(h * 0.38)), 60)
        # 旗桿
        pygame.draw.line(screen, (180, 180, 200),
                         (w // 2, int(h * 0.12)), (w // 2, int(h * 0.38)), 3)
        # 海軍旗（飄揚）
        flag_w, flag_h = 70, 40
        flag_pts = []
        for fx in range(flag_w):
            wave = 5 * math.sin(fx * 0.15 + self.t * 2.5)
            flag_pts.append((w // 2 + fx, int(h * 0.12) + int(wave)))
        bottom_pts = []
        for fx in range(flag_w - 1, -1, -1):
            wave = 5 * math.sin(fx * 0.15 + self.t * 2.5)
            bottom_pts.append((w // 2 + fx, int(h * 0.12) + flag_h + int(wave)))
        if len(flag_pts) > 2:
            pygame.draw.polygon(screen, (180, 200, 240), flag_pts + bottom_pts)
            # 正義 (Justice) 字用矩形代替
            mid_y = int(h * 0.12) + flag_h // 2
            mid_x = w // 2 + flag_w // 2
            pygame.draw.rect(screen, (30, 50, 120),
                             (mid_x - 12, mid_y - 8, 24, 16), border_radius=3)

        # 側翼建築
        for i, (bx, bw, bh_ratio) in enumerate([
            (w // 2 - 280, 100, 0.28),
            (w // 2 - 180, 70,  0.22),
            (w // 2 + 110, 70,  0.22),
            (w // 2 + 180, 100, 0.28),
        ]):
            bh = int(h * bh_ratio)
            by = int(h * 0.76) - bh
            pygame.draw.rect(screen, bldg_color, (bx, by, bw, bh))
            # 窗戶燈光
            for wy in range(by + 8, by + bh - 8, 18):
                for wx in range(bx + 8, bx + bw - 8, 14):
                    if random.random() > 0.3:
                        pygame.draw.rect(screen, (200, 190, 100),
                                         (wx, wy, 6, 8))

        self._draw_waves(screen)
        pygame.draw.rect(screen, (30, 55, 110), (0, int(h * 0.94), w, h))
