import pygame
import math
import random as _rnd
from core.constants import DARK
from config import (WORLD_WIDTH, WORLD_HEIGHT, ZONE_COLORS, ZONE_ACCENT,
                    ZONE_BOUNDARIES, ALTAR_POS, ALTAR_RADIUS)
from utils.font_helper import get_font

_DECO_SEED = 42


class SceneManager:
    def __init__(self):
        self._tile_size = 80
        self._altar_pulse = 0.0
        self._t = 0.0
        self._particles = []
        self._particle_timer = 0.0
        self._decos = self._gen_decorations()

    # ── Decoration generation ─────────────────────────────────────────────────

    def _gen_decorations(self):
        rng = _rnd.Random(_DECO_SEED)
        decos = []
        z0, z1, z2, z3 = ZONE_BOUNDARIES

        # Zone 1 (新手海島): trees + rocks + bushes
        for _ in range(40):
            x = rng.randint(z0 + 50, z1 - 50)
            y = rng.randint(60, WORLD_HEIGHT - 60)
            sz = rng.randint(16, 34)
            decos.append(('tree', x, y, sz, rng.randint(0, 2), 0))
        for _ in range(18):
            x = rng.randint(z0 + 30, z1 - 30)
            y = rng.randint(40, WORLD_HEIGHT - 40)
            sz = rng.randint(8, 18)
            c = (rng.randint(108, 138), rng.randint(103, 132), rng.randint(98, 128))
            decos.append(('rock', x, y, sz, c, 0))
        for _ in range(12):
            x = rng.randint(z0 + 40, z1 - 40)
            y = rng.randint(50, WORLD_HEIGHT - 50)
            sz = rng.randint(8, 14)
            decos.append(('bush', x, y, sz, 0, 0))

        # Zone 2 (火山基地): lava rocks + fire pillars + ash mounds
        for _ in range(28):
            x = rng.randint(z1 + 30, z2 - 30)
            y = rng.randint(50, WORLD_HEIGHT - 50)
            sz = rng.randint(14, 30)
            decos.append(('lava_rock', x, y, sz, 0, 0))
        for _ in range(14):
            x = rng.randint(z1 + 50, z2 - 50)
            y = rng.randint(60, WORLD_HEIGHT - 60)
            sz = rng.randint(20, 42)
            off = rng.uniform(0, math.pi * 2)
            decos.append(('fire_pillar', x, y, sz, 0, off))
        for _ in range(10):
            x = rng.randint(z1 + 30, z2 - 30)
            y = rng.randint(40, WORLD_HEIGHT - 40)
            sz = rng.randint(10, 20)
            decos.append(('ash_mound', x, y, sz, 0, 0))

        # Zone 3 (傳說城堡): ice pillars + ruins + snow mounds
        for _ in range(22):
            x = rng.randint(z2 + 30, z3 - 30)
            y = rng.randint(50, WORLD_HEIGHT - 50)
            sz = rng.randint(18, 42)
            decos.append(('ice_pillar', x, y, sz, 0, 0))
        for _ in range(16):
            x = rng.randint(z2 + 30, z3 - 30)
            y = rng.randint(50, WORLD_HEIGHT - 50)
            sz = rng.randint(22, 52)
            w = rng.randint(30, 80)
            gap = rng.randint(5, 20)
            decos.append(('ruin', x, y, sz, (w, gap), 0))
        for _ in range(12):
            x = rng.randint(z2 + 20, z3 - 20)
            y = rng.randint(40, WORLD_HEIGHT - 40)
            sz = rng.randint(10, 24)
            decos.append(('snow_mound', x, y, sz, 0, 0))

        return decos

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float):
        self._altar_pulse += dt * 2
        self._t += dt

        self._particle_timer += dt
        if self._particle_timer >= 0.12:
            self._particle_timer = 0.0
            self._emit_ambient()

        alive = []
        for p in self._particles:
            p[0] -= dt
            p[1] += p[3] * dt
            p[2] += p[4] * dt
            if p[0] > 0:
                alive.append(p)
        if len(alive) > 80:
            alive = alive[-80:]
        self._particles = alive

    def _emit_ambient(self):
        rng = _rnd.Random()
        z0, z1, z2, z3 = ZONE_BOUNDARIES
        # Zone 1: green leaves drifting upward
        for _ in range(2):
            px = rng.randint(z0, z1)
            py = rng.randint(0, WORLD_HEIGHT)
            life = rng.uniform(2.5, 5.0)
            c = (rng.randint(35, 75), rng.randint(130, 175), rng.randint(35, 75))
            self._particles.append([life, float(px), float(py),
                                     rng.uniform(-14, 14), rng.uniform(-28, -8), c, rng.randint(2, 4)])
        # Zone 2: orange embers rising
        for _ in range(3):
            px = rng.randint(z1, z2)
            py = rng.randint(WORLD_HEIGHT // 3, WORLD_HEIGHT)
            life = rng.uniform(1.0, 2.5)
            c = (rng.randint(220, 255), rng.randint(60, 150), 0)
            self._particles.append([life, float(px), float(py),
                                     rng.uniform(-10, 10), rng.uniform(-45, -18), c, rng.randint(1, 3)])
        # Zone 3: white snow drifting down
        for _ in range(3):
            px = rng.randint(z2, z3)
            py = rng.randint(0, WORLD_HEIGHT // 2)
            life = rng.uniform(3.0, 6.0)
            self._particles.append([life, float(px), float(py),
                                     rng.uniform(-8, 8), rng.uniform(14, 32), (215, 235, 255), rng.randint(1, 3)])

    # ── Draw ─────────────────────────────────────────────────────────────────

    def draw_world(self, screen, camera):
        self._draw_background(screen, camera)
        self._draw_world_border(screen, camera)
        self._draw_decorations(screen, camera)
        self._draw_particles(screen, camera)
        self._draw_altar(screen, camera)
        self._draw_zone_labels(screen, camera)

    def _draw_background(self, screen, camera):
        cam_x = int(camera.x)
        cam_y = int(camera.y)
        sw = screen.get_width()
        sh = screen.get_height()
        ts = self._tile_size

        for xi in range(-1, sw // ts + 2):
            wx = xi * ts + (cam_x // ts) * ts
            zone_idx = min(2, max(0, int(wx / (WORLD_WIDTH / 3))))
            color = ZONE_COLORS[zone_idx]
            sx = xi * ts - (cam_x % ts)
            pygame.draw.rect(screen, color, (sx, 0, ts + 1, sh))

        for xi in range(-1, sw // ts + 2):
            wx = xi * ts + (cam_x // ts) * ts
            zone_idx = min(2, max(0, int(wx / (WORLD_WIDTH / 3))))
            lc = tuple(min(255, c + 12) for c in ZONE_COLORS[zone_idx])
            sx2 = xi * ts - (cam_x % ts)
            pygame.draw.line(screen, lc, (sx2, 0), (sx2, sh), 1)
        for yi in range(-1, sh // ts + 2):
            sy2 = yi * ts - (cam_y % ts)
            pygame.draw.line(screen, tuple(min(255, c + 12) for c in ZONE_COLORS[0]),
                             (0, sy2), (sw, sy2), 1)

    def _draw_world_border(self, screen, camera):
        sw, sh = screen.get_width(), screen.get_height()
        t = self._t
        OCEAN = (18, 55, 115)
        WAVE  = (38, 95, 175)

        left_sx, _ = camera.world_to_screen(0, 0)
        if left_sx > 0:
            pygame.draw.rect(screen, OCEAN, (0, 0, int(left_sx), sh))
            for i in range(sh // 28 + 2):
                wy = i * 28 + int(math.sin(t * 1.4 + i * 0.9) * 6)
                pygame.draw.arc(screen, WAVE, (int(left_sx) - 28, wy, 38, 18), 0, math.pi, 2)

        right_sx, _ = camera.world_to_screen(WORLD_WIDTH, 0)
        if right_sx < sw:
            pygame.draw.rect(screen, OCEAN, (int(right_sx), 0, sw - int(right_sx), sh))
            for i in range(sh // 28 + 2):
                wy = i * 28 + int(math.sin(t * 1.4 + i * 0.9 + 1.2) * 6)
                pygame.draw.arc(screen, WAVE, (int(right_sx) - 10, wy, 38, 18), 0, math.pi, 2)

        _, top_sy = camera.world_to_screen(0, 0)
        if top_sy > 0:
            pygame.draw.rect(screen, OCEAN, (0, 0, sw, int(top_sy)))
            for i in range(sw // 38 + 2):
                wx = i * 38 + int(math.sin(t * 1.1 + i * 0.7) * 8)
                pygame.draw.arc(screen, WAVE, (wx, int(top_sy) - 14, 48, 22), 0, math.pi, 2)

        _, bot_sy = camera.world_to_screen(0, WORLD_HEIGHT)
        if bot_sy < sh:
            pygame.draw.rect(screen, OCEAN, (0, int(bot_sy), sw, sh - int(bot_sy)))
            for i in range(sw // 38 + 2):
                wx = i * 38 + int(math.sin(t * 1.1 + i * 0.7 + 2.0) * 8)
                pygame.draw.arc(screen, WAVE, (wx, int(bot_sy) - 10, 48, 22), 0, math.pi, 2)

    def _draw_decorations(self, screen, camera):
        sw, sh = screen.get_width(), screen.get_height()
        t = self._t
        for entry in self._decos:
            dtype = entry[0]
            wx, wy = entry[1], entry[2]
            sz = entry[3]
            extra = entry[4]
            off = entry[5]
            sx, sy = camera.world_to_screen(wx, wy)
            if sx < -120 or sx > sw + 120 or sy < -120 or sy > sh + 120:
                continue

            if dtype == 'tree':
                self._dd_tree(screen, sx, sy, sz, extra)
            elif dtype == 'rock':
                self._dd_rock(screen, sx, sy, sz, extra)
            elif dtype == 'bush':
                self._dd_bush(screen, sx, sy, sz)
            elif dtype == 'lava_rock':
                self._dd_lava_rock(screen, sx, sy, sz)
            elif dtype == 'fire_pillar':
                self._dd_fire_pillar(screen, sx, sy, sz, t + off)
            elif dtype == 'ash_mound':
                self._dd_ash_mound(screen, sx, sy, sz)
            elif dtype == 'ice_pillar':
                self._dd_ice_pillar(screen, sx, sy, sz)
            elif dtype == 'ruin':
                w, gap = extra if extra else (40, 10)
                self._dd_ruin(screen, sx, sy, sz, w, gap)
            elif dtype == 'snow_mound':
                self._dd_snow_mound(screen, sx, sy, sz)

    # ── Individual decoration drawers ─────────────────────────────────────────

    def _dd_tree(self, screen, sx, sy, sz, variant):
        tw = max(4, sz // 5)
        th = sz + 8
        pygame.draw.rect(screen, (88, 52, 22), (sx - tw // 2, sy - th // 2, tw, th), border_radius=2)
        cr = sz + 6
        for dx, dy_off, col in [
            (0,        -th // 2 - cr // 2,  (35, 115, 35)),
            (-cr // 2, -th // 2 - cr // 3,  (52, 145, 52)),
            (cr // 2,  -th // 2 - cr // 3,  (52, 145, 52)),
        ]:
            pygame.draw.circle(screen, col, (sx + dx, sy + dy_off), cr - 4)
        pygame.draw.circle(screen, (38, 125, 38), (sx, sy - th // 2 - cr // 2), cr)
        if variant >= 1:
            pygame.draw.circle(screen, (26, 95, 26), (sx, sy - th // 2 - cr), cr // 2)

    def _dd_rock(self, screen, sx, sy, sz, color):
        pts = [
            (sx - sz,         sy),
            (sx - sz + sz//3, sy - sz * 2 // 3),
            (sx,              sy - sz),
            (sx + sz * 2//3,  sy - sz * 2 // 3),
            (sx + sz,         sy),
        ]
        pygame.draw.polygon(screen, color, pts)
        hl = tuple(min(255, c + 28) for c in color)
        pygame.draw.polygon(screen, hl, pts, 1)

    def _dd_bush(self, screen, sx, sy, sz):
        pygame.draw.circle(screen, (40, 110, 40), (sx, sy), sz)
        pygame.draw.circle(screen, (60, 140, 55), (sx - sz // 2, sy - sz // 4), sz - 2)
        pygame.draw.circle(screen, (60, 140, 55), (sx + sz // 2, sy - sz // 4), sz - 2)

    def _dd_lava_rock(self, screen, sx, sy, sz):
        DROCK = (42, 22, 12)
        CRACK = (215, 75, 0)
        pygame.draw.circle(screen, DROCK, (sx, sy), sz)
        pygame.draw.circle(screen, (28, 12, 6), (sx, sy), sz, 2)
        for i in range(3):
            a = math.radians(i * 120 + 30)
            ex = sx + int(math.cos(a) * sz * 0.7)
            ey = sy + int(math.sin(a) * sz * 0.7)
            pygame.draw.line(screen, CRACK, (sx, sy), (ex, ey), max(1, sz // 8))
        if sz > 16:
            pygame.draw.circle(screen, CRACK, (sx, sy), sz // 3)
            pygame.draw.circle(screen, (255, 180, 60), (sx, sy), sz // 6)

    def _dd_fire_pillar(self, screen, sx, sy, sz, t):
        hw = max(4, sz // 3)
        pygame.draw.rect(screen, (48, 28, 18), (sx - hw, sy - sz // 3, hw * 2, sz // 2), border_radius=3)
        lh = sz * 2
        for dy_frac, col, rad_f in [
            (0.0,  (255, 45, 0),   1.0),
            (0.35, (255, 130, 0),  0.68),
            (0.65, (255, 215, 40), 0.38),
        ]:
            wave = int(math.sin(t * 4.5 + dy_frac * 6) * 3)
            fy = sy - sz // 3 - int(lh * dy_frac)
            fr = max(2, int(hw * rad_f) + wave)
            pygame.draw.circle(screen, col, (sx + wave, fy), fr)

    def _dd_ash_mound(self, screen, sx, sy, sz):
        pygame.draw.ellipse(screen, (95, 88, 80),
                            (sx - sz, sy - sz // 3, sz * 2, sz // 2 + 4))
        pygame.draw.ellipse(screen, (115, 108, 100),
                            (sx - sz + 4, sy - sz // 3, sz * 2 - 8, sz // 2), 1)

    def _dd_ice_pillar(self, screen, sx, sy, sz):
        iw = max(4, sz // 3)
        ih = sz * 2
        ICE  = (148, 205, 242)
        ICEL = (215, 240, 255)
        ICED = (98, 162, 212)
        pygame.draw.rect(screen, ICE, (sx - iw, sy - ih, iw * 2, ih), border_radius=3)
        pygame.draw.polygon(screen, ICEL, [
            (sx,      sy - ih - sz // 2),
            (sx - iw, sy - ih),
            (sx + iw, sy - ih),
        ])
        pygame.draw.line(screen, ICEL, (sx - iw // 2, sy - ih + 4), (sx - iw // 2, sy - 4), max(1, iw // 2))
        pygame.draw.rect(screen, ICED, (sx - iw, sy - ih, iw * 2, ih), 1, border_radius=3)

    def _dd_ruin(self, screen, sx, sy, sz, w, gap):
        STONE  = (128, 118, 108)
        STONED = (88, 80, 72)
        pygame.draw.rect(screen, STONE, (sx - w // 2, sy - sz, w // 3, sz), border_radius=2)
        pygame.draw.rect(screen, STONED, (sx - w // 2, sy - sz, w // 3, sz), 1, border_radius=2)
        rx = sx - w // 2 + w // 3 + gap
        pygame.draw.rect(screen, STONE, (rx, sy - sz + sz // 4, w // 3, sz * 3 // 4), border_radius=2)
        pygame.draw.rect(screen, STONED, (rx, sy - sz + sz // 4, w // 3, sz * 3 // 4), 1, border_radius=2)
        pygame.draw.circle(screen, STONED, (sx, sy - 4), gap // 2 + 2)

    def _dd_snow_mound(self, screen, sx, sy, sz):
        pygame.draw.ellipse(screen, (185, 205, 230), (sx - sz, sy - sz // 4, sz * 2, sz // 2 + 6))
        pygame.draw.ellipse(screen, (225, 238, 252), (sx - sz + 3, sy - sz // 4, sz * 2 - 6, sz // 2 + 2))

    # ── Ambient particles ─────────────────────────────────────────────────────

    def _draw_particles(self, screen, camera):
        for p in self._particles:
            life, px, py, _vx, _vy, color, pr = p
            sx, sy = camera.world_to_screen(px, py)
            if sx < -10 or sy < -10 or sx > screen.get_width() + 10 or sy > screen.get_height() + 10:
                continue
            alpha = min(1.0, life / 3.0)
            c = tuple(max(0, min(255, int(ch * alpha))) for ch in color)
            pygame.draw.circle(screen, c, (sx, sy), max(1, pr))

    # ── Altar ─────────────────────────────────────────────────────────────────

    def _draw_altar(self, screen, camera):
        ax, ay = ALTAR_POS
        sx, sy = camera.world_to_screen(ax, ay)
        r = ALTAR_RADIUS
        pulse = abs(math.sin(self._altar_pulse)) * 0.4 + 0.6
        gold = (int(200 * pulse), int(160 * pulse), 0)
        hex_pts = [
            (sx,             sy - r),
            (sx + r * 0.866, sy - r * 0.5),
            (sx + r * 0.866, sy + r * 0.5),
            (sx,             sy + r),
            (sx - r * 0.866, sy + r * 0.5),
            (sx - r * 0.866, sy - r * 0.5),
        ]
        pygame.draw.polygon(screen, (38, 28, 8), hex_pts)
        pygame.draw.polygon(screen, gold, hex_pts, 3)
        inner_r = int(r * 0.5 * pulse)
        pygame.draw.circle(screen, (255, 200, 0), (sx, sy), inner_r)
        for i in range(6):
            a = math.radians(self._altar_pulse * 40 + i * 60)
            rx2 = sx + int(math.cos(a) * r * 0.7)
            ry2 = sy + int(math.sin(a) * r * 0.7)
            pygame.draw.circle(screen, (255, 220, 80), (rx2, ry2), 4)

    def _draw_zone_labels(self, screen, camera):
        font = get_font(14, bold=True)
        zone_names = ["新手海島", "火山基地", "傳說城堡"]
        for i, name in enumerate(zone_names):
            wx = ZONE_BOUNDARIES[i] + (ZONE_BOUNDARIES[i + 1] - ZONE_BOUNDARIES[i]) // 2
            wy = 80
            sx, sy = camera.world_to_screen(wx, wy)
            if -100 < sx < screen.get_width() + 100:
                surf = font.render(name, True, (200, 200, 200))
                screen.blit(surf, (sx - surf.get_width() // 2, sy))

    def is_near_altar(self, player_x, player_y) -> bool:
        return math.hypot(player_x - ALTAR_POS[0],
                          player_y - ALTAR_POS[1]) < ALTAR_RADIUS + 40
