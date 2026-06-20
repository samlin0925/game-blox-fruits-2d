"""
開場前言動畫（新遊戲前播放）
3 個故事板，每板 10 秒，文字速度與時長完全同步（30 秒總計）。
Space / Enter = 加速跳到下一板
ESC           = 直接跳過全部
"""

import pygame
import math
import random
from utils.font_helper import get_font
from config import SCREEN_WIDTH, SCREEN_HEIGHT


# ── Panel definitions ─────────────────────────────────────────────────────────
# chars_per_sec is auto-calculated to fill the full duration.

_PANELS = [
    {
        "bg":     (8, 12, 35),
        "accent": (100, 150, 220),
        "title":  "偉大的航路",
        "lines": [
            "在這片無盡的大海上，",
            "存在著一條令人聞風喪膽的海域——",
            "「偉大的航路」。",
            "",
            "傳說中，最強大的秘寶惡魔果實",
            "就散落在這片海域的每個角落。",
        ],
        "deco":     "ocean_ship",
        "duration": 10.0,
    },
    {
        "bg":     (30, 8, 8),
        "accent": (220, 80, 50),
        "title":  "追殺令",
        "lines": [
            "海軍三大將——",
            "赤犬、黃猿、青雉——",
            "已對你下達了全面緝拿令。",
            "",
            "你的懸賞金足以讓整個偉大航路",
            "的海賊都來追殺你。",
        ],
        "deco":     "wanted_poster",
        "duration": 10.0,
    },
    {
        "bg":     (5, 20, 10),
        "accent": (80, 200, 120),
        "title":  "唯一的希望",
        "lines": [
            "傳說中，集齊惡魔果實的覺醒者，",
            "能夠對抗三大將的力量。",
            "",
            "找到果實碎片，前往祭壇覺醒，",
            "這是你唯一的機會。",
            "",
            "你的冒險，就此開始……",
        ],
        "deco":     "hero_awaken",
        "duration": 10.0,
    },
]


def _panel_chars_per_sec(panel: dict) -> float:
    total = sum(len(ln) for ln in panel["lines"])
    if total == 0:
        return 1.0
    return total / (panel["duration"] * 0.9)   # use 90% of duration for text


class IntroCutscene:
    def __init__(self):
        self.font_title = get_font(36, bold=True)
        self.font_body  = get_font(22)
        self.font_hint  = get_font(15)
        self._panel = 0
        self._char_pos = 0.0
        self._timer = 0.0
        self._done = False
        self._t = 0.0          # animation clock (resets each panel)
        self._global_t = 0.0   # global clock (never resets)

        rng = random.Random(42)
        self._stars = [
            (rng.randint(0, SCREEN_WIDTH),
             rng.randint(0, SCREEN_HEIGHT),
             rng.choice([1, 1, 2]),
             rng.uniform(0, 6.28))
            for _ in range(150)
        ]
        # Ship wave offsets
        self._wave_offsets = [rng.uniform(0, 6.28) for _ in range(12)]
        # Fruit orb angles for hero panel
        self._orb_angles = [i * (2 * math.pi / 5) for i in range(5)]
        self._orb_colors = [
            (80, 220, 80),   # rubber
            (255, 80, 50),   # flame
            (80, 180, 255),  # ice
            (180, 60, 200),  # dragon
            (240, 160, 40),  # leopard
        ]

    @property
    def done(self):
        return self._done

    def update(self, dt: float, events) -> bool:
        if self._done:
            return True
        self._t += dt
        self._global_t += dt
        panel = _PANELS[self._panel]
        total_chars = sum(len(ln) for ln in panel["lines"])
        cps = _panel_chars_per_sec(panel)
        self._char_pos += cps * dt
        self._timer += dt

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._done = True
                    return True
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if self._char_pos < total_chars:
                        self._char_pos = float(total_chars + 1)
                    else:
                        self._advance()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._char_pos < total_chars:
                    self._char_pos = float(total_chars + 1)
                else:
                    self._advance()

        if self._timer >= panel["duration"] and self._char_pos >= total_chars:
            self._advance()

        return self._done

    def _advance(self):
        self._panel += 1
        if self._panel >= len(_PANELS):
            self._done = True
        else:
            self._char_pos = 0.0
            self._timer = 0.0
            self._t = 0.0

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, screen):
        if self._done:
            return
        panel = _PANELS[self._panel]
        accent = panel["accent"]
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT

        screen.fill(panel["bg"])

        deco = panel.get("deco", "")
        if deco == "ocean_ship":
            self._draw_ocean_ship(screen, w, h, accent)
        elif deco == "wanted_poster":
            self._draw_wanted_poster(screen, w, h)
        elif deco == "hero_awaken":
            self._draw_hero_awaken(screen, w, h, accent)

        # Divider lines
        pygame.draw.line(screen, accent, (60, 100), (w - 60, 100), 2)
        pygame.draw.line(screen, accent, (60, h - 60), (w - 60, h - 60), 1)

        # Panel title
        title_surf = self.font_title.render(panel["title"], True, accent)
        screen.blit(title_surf, (80, 50))

        # Progress dots
        for i in range(len(_PANELS)):
            dot_c = accent if i == self._panel else (60, 60, 80)
            pygame.draw.circle(screen, dot_c,
                                (w // 2 - (len(_PANELS) - 1) * 12 + i * 24, 92), 5)

        # Typewriter text
        chars_shown = int(self._char_pos)
        remaining = chars_shown
        for li, line in enumerate(panel["lines"]):
            if remaining < 0:
                break
            visible = line[:remaining] if remaining < len(line) else line
            remaining -= len(line)
            if visible and line:
                surf = self.font_body.render(visible, True, (240, 240, 255))
                screen.blit(surf, (80, 130 + li * 42))

        # Blinking cursor while typing
        total_chars = sum(len(ln) for ln in panel["lines"])
        if self._char_pos < total_chars:
            if int(self._t * 4) % 2 == 0:
                pygame.draw.rect(screen, accent,
                                 (82, 130 + len(panel["lines"]) * 42 - 36, 12, 26))
        else:
            # Progress bar
            progress = self._timer / panel["duration"]
            bar_w = int((w - 160) * min(1.0, progress))
            pygame.draw.rect(screen, (40, 40, 55), (80, h - 45, w - 160, 6),
                             border_radius=3)
            pygame.draw.rect(screen, accent, (80, h - 45, bar_w, 6),
                             border_radius=3)
            hint = ("Space / 點擊 繼續    ESC 跳過"
                    if self._panel < len(_PANELS) - 1
                    else "Space / 點擊 開始冒險    ESC 跳過")
            hs = self.font_hint.render(hint, True, (160, 160, 180))
            screen.blit(hs, (w // 2 - hs.get_width() // 2, h - 58))

        # Fade in
        if self._t < 0.6:
            fade = pygame.Surface((w, h))
            fade.fill((0, 0, 0))
            fade.set_alpha(int(255 * (1 - self._t / 0.6)))
            screen.blit(fade, (0, 0))

    # ── Panel 0: Ocean & Chibi Ship ───────────────────────────────────────────

    def _draw_ocean_ship(self, screen, w, h, accent):
        t = self._t

        # Stars
        for sx, sy, sr, sphase in self._stars:
            bval = 0.5 + 0.5 * math.sin(sphase + t * 1.2)
            c = int(180 * bval)
            pygame.draw.circle(screen, (c, c, int(c * 0.95)), (sx, sy), sr)

        # Moon
        mx, my = w - 120, 110
        pygame.draw.circle(screen, (240, 235, 200), (mx, my), 38)
        pygame.draw.circle(screen, (220, 215, 175), (mx, my), 38, 2)
        pygame.draw.circle(screen, (180, 175, 130), (mx - 10, my - 8), 10)
        pygame.draw.circle(screen, (180, 175, 130), (mx + 14, my + 4), 7)
        # Moon reflection on water
        for i in range(5):
            ry = h - 80 + i * 12
            rx = w - 120 + int(math.sin(t * 2 + i * 0.8) * 8)
            pygame.draw.line(screen, (240, 230, 170), (rx - 15, ry), (rx + 15, ry), 1)

        # Ocean waves at the bottom third
        ocean_y = h - 180
        # Deep ocean background
        pygame.draw.rect(screen, (12, 35, 85),
                         (w // 2 - 10, ocean_y, w // 2 + 10, h - ocean_y))
        # Waves
        for i, off in enumerate(self._wave_offsets[:8]):
            wy = ocean_y + i * 14
            wave_color = (20 + i * 5, 60 + i * 8, 130 + i * 6)
            points = []
            for xi in range(w // 2, w + 30, 8):
                wy_offset = int(math.sin(xi * 0.04 + t * 1.5 + off) * 5)
                points.append((xi, wy + wy_offset))
            if len(points) > 1:
                pygame.draw.lines(screen, wave_color, False, points, 2)

        # ── Chibi pirate ship (right side) ──
        ship_x = w - 200 + int(math.sin(t * 0.8) * 6)
        ship_y = ocean_y + 30 + int(math.sin(t * 1.1) * 4)

        # Hull shadow
        pygame.draw.polygon(screen, (30, 20, 10), [
            (ship_x - 68, ship_y + 38),
            (ship_x + 68, ship_y + 38),
            (ship_x + 55, ship_y + 72),
            (ship_x - 55, ship_y + 72),
        ])
        # Hull
        HULL = (100, 55, 20)
        HULL_L = (140, 80, 35)
        pygame.draw.polygon(screen, HULL, [
            (ship_x - 65, ship_y + 35),
            (ship_x + 65, ship_y + 35),
            (ship_x + 52, ship_y + 68),
            (ship_x - 52, ship_y + 68),
        ])
        # Hull highlight stripe
        pygame.draw.line(screen, HULL_L,
                         (ship_x - 60, ship_y + 40),
                         (ship_x + 60, ship_y + 40), 3)
        # Port holes
        for px_off in [-30, 0, 30]:
            pygame.draw.circle(screen, (200, 170, 100),
                                (ship_x + px_off, ship_y + 52), 6)
            pygame.draw.circle(screen, (60, 40, 15),
                                (ship_x + px_off, ship_y + 52), 6, 1)

        # Mast
        pygame.draw.line(screen, (80, 45, 15),
                         (ship_x, ship_y + 35), (ship_x, ship_y - 90), 5)
        # Cross arm
        pygame.draw.line(screen, (80, 45, 15),
                         (ship_x - 42, ship_y - 50),
                         (ship_x + 42, ship_y - 50), 4)

        # Main sail (cream, billowing)
        sail_billow = int(math.sin(t * 1.5) * 8)
        pygame.draw.polygon(screen, (240, 230, 195), [
            (ship_x - 40, ship_y - 50),
            (ship_x + 40, ship_y - 50),
            (ship_x + 35 + sail_billow, ship_y + 30),
            (ship_x - 35 - sail_billow, ship_y + 30),
        ])
        pygame.draw.polygon(screen, (200, 190, 160), [
            (ship_x - 40, ship_y - 50),
            (ship_x + 40, ship_y - 50),
            (ship_x + 35 + sail_billow, ship_y + 30),
            (ship_x - 35 - sail_billow, ship_y + 30),
        ], 2)
        # Jolly Roger on sail
        skx, sky = ship_x, ship_y - 20
        pygame.draw.circle(screen, (40, 35, 30), (skx, sky), 14)
        pygame.draw.circle(screen, (200, 195, 185), (skx - 4, sky - 3), 4)
        pygame.draw.circle(screen, (200, 195, 185), (skx + 4, sky - 3), 4)
        pygame.draw.line(screen, (200, 195, 185), (skx - 8, sky + 5), (skx + 8, sky + 5), 2)
        pygame.draw.line(screen, (200, 195, 185), (skx - 6, sky + 8), (skx + 6, sky + 8), 2)

        # Top sail
        pygame.draw.polygon(screen, (230, 220, 185), [
            (ship_x - 22, ship_y - 90),
            (ship_x + 22, ship_y - 90),
            (ship_x + 18, ship_y - 56),
            (ship_x - 18, ship_y - 56),
        ])

        # Flag at top
        flag_wave = int(math.sin(t * 3) * 5)
        pygame.draw.polygon(screen, (200, 30, 30), [
            (ship_x + 1, ship_y - 92),
            (ship_x + 20 + flag_wave, ship_y - 84),
            (ship_x + 1, ship_y - 78),
        ])

        # Bow figurehead (simple chibi lion head)
        pygame.draw.circle(screen, (220, 180, 90),
                            (ship_x - 65, ship_y + 45), 14)
        pygame.draw.circle(screen, (200, 150, 60),
                            (ship_x - 65, ship_y + 45), 14, 2)
        # Mane
        for a in range(0, 360, 45):
            ra = math.radians(a)
            mx2 = ship_x - 65 + int(math.cos(ra) * 16)
            my2 = ship_y + 45 + int(math.sin(ra) * 16)
            pygame.draw.circle(screen, (180, 120, 40), (mx2, my2), 5)
        # Eyes
        pygame.draw.circle(screen, (30, 20, 10),
                            (ship_x - 70, ship_y + 42), 3)
        pygame.draw.circle(screen, (30, 20, 10),
                            (ship_x - 60, ship_y + 42), 3)
        pygame.draw.arc(screen, (30, 20, 10),
                        (ship_x - 73, ship_y + 46, 16, 8), math.pi, 0, 2)

    # ── Panel 1: Wanted Poster ────────────────────────────────────────────────

    def _draw_wanted_poster(self, screen, w, h):
        t = self._t

        # Dark red background texture (hatching)
        for i in range(0, w, 28):
            pygame.draw.line(screen, (38, 10, 10), (i, 0), (i + 20, h), 1)

        # "MARINES" watermark stamp (rotated text simulation)
        stamp_x, stamp_y = w - 260, h // 2 + 60
        stamp_font = get_font(28, bold=True)
        stamp_s = stamp_font.render("M A R I N E S", True, (60, 12, 12))
        screen.blit(stamp_s, (stamp_x, stamp_y))

        # Poster parchment
        pw, ph = 300, 400
        poster_x = w - pw - 50
        poster_y = h // 2 - ph // 2 + int(math.sin(t * 0.5) * 3)

        # Parchment aging layers
        pygame.draw.rect(screen, (185, 160, 90),
                         (poster_x + 4, poster_y + 4, pw, ph), border_radius=8)
        pygame.draw.rect(screen, (210, 185, 115),
                         (poster_x, poster_y, pw, ph), border_radius=8)
        # Inner frame
        pygame.draw.rect(screen, (170, 140, 70),
                         (poster_x + 8, poster_y + 8, pw - 16, ph - 16), 3, border_radius=6)

        # "WANTED" header
        w_font = get_font(30, bold=True)
        wanted_s = w_font.render("WANTED", True, (170, 25, 15))
        screen.blit(wanted_s, (poster_x + pw // 2 - wanted_s.get_width() // 2,
                                poster_y + 14))
        # Underline
        pygame.draw.line(screen, (140, 100, 40),
                         (poster_x + 18, poster_y + 50),
                         (poster_x + pw - 18, poster_y + 50), 2)

        # ── Chibi character portrait (Luffy-style) ──
        face_x = poster_x + pw // 2
        face_y = poster_y + 140

        # Neck & body
        pygame.draw.rect(screen, (230, 190, 140),
                         (face_x - 10, face_y + 36, 20, 30), border_radius=4)
        pygame.draw.ellipse(screen, (210, 80, 60),
                            (face_x - 32, face_y + 55, 64, 40))

        # Face (big chibi Q-round head)
        pygame.draw.circle(screen, (245, 205, 155), (face_x, face_y), 48)
        pygame.draw.circle(screen, (210, 170, 115), (face_x, face_y), 48, 2)

        # Straw hat brim
        brim_y = face_y - 30
        pygame.draw.ellipse(screen, (195, 155, 60),
                            (face_x - 58, brim_y - 4, 116, 22))
        pygame.draw.ellipse(screen, (170, 130, 40),
                            (face_x - 58, brim_y - 4, 116, 22), 2)
        # Hat dome
        hat_pts = [
            (face_x - 36, brim_y + 6),
            (face_x - 32, brim_y - 32),
            (face_x, brim_y - 44),
            (face_x + 32, brim_y - 32),
            (face_x + 36, brim_y + 6),
        ]
        pygame.draw.polygon(screen, (210, 170, 60), hat_pts)
        pygame.draw.polygon(screen, (170, 130, 40), hat_pts, 2)
        # Red band on hat
        pygame.draw.line(screen, (200, 35, 30),
                         (face_x - 32, brim_y - 6),
                         (face_x + 32, brim_y - 6), 8)

        # Eyes (big bright chibi eyes)
        for ex, ey in [(face_x - 16, face_y - 8), (face_x + 16, face_y - 8)]:
            pygame.draw.circle(screen, (255, 255, 255), (ex, ey), 11)
            pygame.draw.circle(screen, (30, 20, 10), (ex, ey), 7)
            pygame.draw.circle(screen, (255, 255, 255), (ex + 3, ey - 3), 3)

        # X scar under left eye
        sx_c = face_x - 16
        sy_c = face_y + 4
        pygame.draw.line(screen, (190, 90, 80), (sx_c - 6, sy_c - 4), (sx_c + 6, sy_c + 4), 2)
        pygame.draw.line(screen, (190, 90, 80), (sx_c + 6, sy_c - 4), (sx_c - 6, sy_c + 4), 2)

        # Big smile
        pygame.draw.arc(screen, (30, 20, 10),
                        (face_x - 28, face_y + 8, 56, 28),
                        math.pi, 0, 4)
        # Teeth
        pygame.draw.rect(screen, (255, 255, 255), (face_x - 14, face_y + 20, 28, 10), border_radius=3)

        # Round chibi nose
        pygame.draw.circle(screen, (210, 160, 110), (face_x, face_y + 6), 6)

        # Ears
        for ex in [face_x - 48, face_x + 48]:
            pygame.draw.circle(screen, (245, 205, 155), (ex, face_y), 12)
            pygame.draw.circle(screen, (210, 170, 115), (ex, face_y), 12, 1)

        # "DEAD OR ALIVE" text
        doa_font = get_font(14, bold=True)
        doa_s = doa_font.render("DEAD  OR  ALIVE", True, (165, 22, 12))
        screen.blit(doa_s, (poster_x + pw // 2 - doa_s.get_width() // 2,
                             poster_y + ph - 100))
        pygame.draw.line(screen, (140, 100, 40),
                         (poster_x + 18, poster_y + ph - 104),
                         (poster_x + pw - 18, poster_y + ph - 104), 1)

        # Bounty amount
        b_font = get_font(18, bold=True)
        bounty_s = b_font.render("1,500,000,000", True, (30, 20, 10))
        screen.blit(bounty_s, (poster_x + pw // 2 - bounty_s.get_width() // 2,
                                poster_y + ph - 76))
        bell_s = self.font_hint.render("貝利", True, (80, 60, 20))
        screen.blit(bell_s, (poster_x + pw // 2 - bell_s.get_width() // 2,
                              poster_y + ph - 50))

        # Animated "STAMP" overlay on poster
        if self._timer > 2.0:
            stamp2_font = get_font(36, bold=True)
            stamp2_s = stamp2_font.render("緝拿中", True, (180, 20, 20))
            # Slight rotation simulation via surface
            stamp2_surf = pygame.Surface((stamp2_s.get_width() + 20,
                                          stamp2_s.get_height() + 10),
                                          pygame.SRCALPHA)
            pygame.draw.rect(stamp2_surf, (180, 20, 20, 80),
                             (0, 0, stamp2_surf.get_width(), stamp2_surf.get_height()),
                             3)
            stamp2_surf.blit(stamp2_s, (10, 5))
            screen.blit(stamp2_surf,
                        (poster_x + pw // 2 - stamp2_surf.get_width() // 2 - 10,
                         poster_y + ph // 2 - 20))

    # ── Panel 2: Hero Awakening ───────────────────────────────────────────────

    def _draw_hero_awaken(self, screen, w, h, accent):
        t = self._t

        # Stars
        for sx, sy, sr, sphase in self._stars:
            bval = 0.4 + 0.6 * abs(math.sin(sphase + t * 0.8))
            c = int(200 * bval)
            pygame.draw.circle(screen, (c, c, int(c * 0.8)), (sx, sy), sr)

        # Central light rays
        cx, cy = w // 2 + 160, h // 2 + 20
        ray_count = 12
        for i in range(ray_count):
            angle = math.radians(i * (360 / ray_count) + t * 15)
            ray_len = 200 + 60 * math.sin(t * 2 + i * 0.5)
            ex = cx + int(math.cos(angle) * ray_len)
            ey = cy + int(math.sin(angle) * ray_len)
            alpha_ray = int(60 + 40 * math.sin(t * 3 + i))
            ray_s = pygame.Surface((abs(ex - cx) + 10, abs(ey - cy) + 10), pygame.SRCALPHA)
            ray_color = (*accent, alpha_ray)
            pygame.draw.line(screen, ray_color, (cx, cy), (ex, ey), 2)

        # Orbiting fruit orbs (5 fruits)
        orb_r = 90
        for i, (orb_color, init_angle) in enumerate(zip(self._orb_colors, self._orb_angles)):
            angle = init_angle + t * (0.8 + i * 0.1)
            ox = cx + int(math.cos(angle) * orb_r)
            oy = cy + int(math.sin(angle) * orb_r)

            # Glow
            glow_s = pygame.Surface((36, 36), pygame.SRCALPHA)
            pygame.draw.circle(glow_s, (*orb_color, 60), (18, 18), 18)
            screen.blit(glow_s, (ox - 18, oy - 18))

            # Orb body
            pygame.draw.circle(screen, orb_color, (ox, oy), 12)
            pygame.draw.circle(screen, (255, 255, 255), (ox, oy), 12, 1)
            pygame.draw.circle(screen, (255, 255, 255), (ox - 3, oy - 3), 3)

            # Spiral trail behind orb
            trail_angle = angle - 0.4
            tx2 = cx + int(math.cos(trail_angle) * orb_r)
            ty2 = cy + int(math.sin(trail_angle) * orb_r)
            tc = tuple(max(0, v - 60) for v in orb_color)
            pygame.draw.line(screen, tc, (tx2, ty2), (ox, oy), 2)

        # ── Chibi hero character ──
        hero_x = cx
        hero_y = cy

        # Hover animation
        hover = int(math.sin(t * 2) * 5)
        hero_y += hover

        # Shadow below
        pygame.draw.ellipse(screen, (0, 30, 10),
                            (hero_x - 30, hero_y + 60, 60, 16))

        # Body (red vest)
        pygame.draw.ellipse(screen, (200, 40, 40),
                            (hero_x - 22, hero_y + 22, 44, 42))

        # Arms stretched out
        pygame.draw.line(screen, (245, 205, 155),
                         (hero_x - 22, hero_y + 30),
                         (hero_x - 55, hero_y + 20), 10)
        pygame.draw.line(screen, (245, 205, 155),
                         (hero_x + 22, hero_y + 30),
                         (hero_x + 55, hero_y + 20), 10)
        # Fists
        pygame.draw.circle(screen, (245, 205, 155), (hero_x - 55, hero_y + 20), 9)
        pygame.draw.circle(screen, (245, 205, 155), (hero_x + 55, hero_y + 20), 9)

        # Shorts (blue)
        pygame.draw.ellipse(screen, (50, 80, 200),
                            (hero_x - 18, hero_y + 44, 36, 30))

        # Legs
        pygame.draw.line(screen, (245, 205, 155),
                         (hero_x - 10, hero_y + 62),
                         (hero_x - 12, hero_y + 82), 10)
        pygame.draw.line(screen, (245, 205, 155),
                         (hero_x + 10, hero_y + 62),
                         (hero_x + 12, hero_y + 82), 10)

        # Head
        pygame.draw.circle(screen, (245, 205, 155), (hero_x, hero_y), 34)
        pygame.draw.circle(screen, (210, 170, 115), (hero_x, hero_y), 34, 2)

        # Straw hat
        brim_y2 = hero_y - 22
        pygame.draw.ellipse(screen, (195, 155, 60),
                            (hero_x - 42, brim_y2 - 3, 84, 16))
        pygame.draw.ellipse(screen, (170, 130, 40),
                            (hero_x - 42, brim_y2 - 3, 84, 16), 2)
        hat_pts2 = [
            (hero_x - 26, brim_y2 + 4),
            (hero_x - 22, brim_y2 - 24),
            (hero_x, brim_y2 - 32),
            (hero_x + 22, brim_y2 - 24),
            (hero_x + 26, brim_y2 + 4),
        ]
        pygame.draw.polygon(screen, (210, 170, 60), hat_pts2)
        pygame.draw.polygon(screen, (170, 130, 40), hat_pts2, 2)
        pygame.draw.line(screen, (200, 35, 30),
                         (hero_x - 22, brim_y2 - 4),
                         (hero_x + 22, brim_y2 - 4), 6)

        # Eyes (determined look)
        for ex, ey in [(hero_x - 12, hero_y - 6), (hero_x + 12, hero_y - 6)]:
            pygame.draw.circle(screen, (255, 255, 255), (ex, ey), 8)
            pygame.draw.circle(screen, (30, 20, 10), (ex, ey), 5)
            pygame.draw.circle(screen, (255, 255, 255), (ex + 2, ey - 2), 2)

        # Big grin
        pygame.draw.arc(screen, (30, 20, 10),
                        (hero_x - 20, hero_y + 6, 40, 20),
                        math.pi, 0, 4)

        # Aura glow around hero
        aura_r = int(80 + 15 * math.sin(t * 3))
        aura_s = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
        aura_alpha = int(30 + 20 * math.sin(t * 2))
        pygame.draw.circle(aura_s, (*accent, aura_alpha),
                           (aura_r, aura_r), aura_r)
        screen.blit(aura_s, (hero_x - aura_r, hero_y - aura_r + hover))

        # "AWAKENED!" text that pulses in at t > 6
        if t > 6.0:
            aw_alpha = min(255, int((t - 6.0) * 120))
            aw_font = get_font(28, bold=True)
            aw_s = aw_font.render("覺醒者降臨！", True, accent)
            aw_surf = pygame.Surface((aw_s.get_width(), aw_s.get_height()), pygame.SRCALPHA)
            aw_surf.blit(aw_s, (0, 0))
            aw_surf.set_alpha(aw_alpha)
            screen.blit(aw_surf, (w // 2 + 160 - aw_s.get_width() // 2, h - 220))
