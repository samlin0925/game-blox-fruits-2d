"""
開場前言動畫（新遊戲前播放）
3 個故事板，每板文字打字機效果呈現。
Space / Enter = 加速跳到下一板
ESC           = 直接跳過全部
"""

import pygame
import math
import random
from utils.font_helper import get_font
from config import SCREEN_WIDTH, SCREEN_HEIGHT


_PANELS = [
    {
        "bg": (8, 12, 35),
        "accent": (100, 150, 220),
        "title": "偉大的航路",
        "lines": [
            "在這片無盡的大海上，",
            "存在著一條令人聞風喪膽的海域——",
            "「偉大的航路」。",
            "",
            "傳說中，最強大的秘寶惡魔果實",
            "就散落在這片海域的每個角落。",
        ],
        "deco": "stars",
        "duration": 5.5,
    },
    {
        "bg": (30, 8, 8),
        "accent": (220, 80, 50),
        "title": "追殺令",
        "lines": [
            "海軍三大將——",
            "赤犬、黃猿、青雉——",
            "已對你下達了全面緝拿令。",
            "",
            "你的懸賞金足以讓整個偉大航路",
            "的海賊都來追殺你。",
        ],
        "deco": "wanted",
        "duration": 5.5,
    },
    {
        "bg": (5, 20, 10),
        "accent": (80, 200, 120),
        "title": "唯一的希望",
        "lines": [
            "傳說中，集齊惡魔果實的覺醒者，",
            "能夠對抗三大將的力量。",
            "",
            "找到果實碎片，前往祭壇覺醒，",
            "這是你唯一的機會。",
            "",
            "你的冒險，就此開始……",
        ],
        "deco": "glow",
        "duration": 6.0,
    },
]

_CHARS_PER_SEC = 28


class IntroCutscene:
    def __init__(self):
        self.font_title = get_font(36, bold=True)
        self.font_body  = get_font(22)
        self.font_hint  = get_font(15)
        self._panel = 0
        self._char_pos = 0.0   # how many characters revealed so far
        self._timer = 0.0
        self._done = False
        self._t = 0.0          # global time for animations
        self._stars = [
            (random.randint(0, SCREEN_WIDTH),
             random.randint(0, SCREEN_HEIGHT),
             random.choice([1, 1, 2]),
             random.uniform(0, 6.28))
            for _ in range(120)
        ]

    @property
    def done(self):
        return self._done

    def update(self, dt: float, events) -> bool:
        """Return True when cutscene is finished."""
        if self._done:
            return True
        self._t += dt
        panel = _PANELS[self._panel]
        total_chars = sum(len(ln) for ln in panel["lines"])
        self._char_pos += _CHARS_PER_SEC * dt
        self._timer += dt

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._done = True
                    return True
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if self._char_pos < total_chars:
                        self._char_pos = total_chars + 1  # skip typewriter
                    else:
                        self._advance()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._char_pos < total_chars:
                    self._char_pos = total_chars + 1
                else:
                    self._advance()

        # auto-advance after duration
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

    def draw(self, screen):
        if self._done:
            return
        panel = _PANELS[self._panel]
        bg = panel["bg"]
        accent = panel["accent"]
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT

        # 背景
        screen.fill(bg)

        # 裝飾
        deco = panel.get("deco", "")
        if deco == "stars" or deco == "glow":
            for sx, sy, sr, sphase in self._stars:
                bval = 0.5 + 0.5 * math.sin(sphase + self._t * 1.2)
                c = int(180 * bval)
                pygame.draw.circle(screen, (c, c, int(c * 0.95)), (sx, sy), sr)

        if deco == "wanted":
            # 海報紙底色
            pw, ph = 320, 400
            px, py = w - pw - 40, h // 2 - ph // 2
            pygame.draw.rect(screen, (200, 175, 100), (px, py, pw, ph),
                             border_radius=6)
            pygame.draw.rect(screen, (150, 120, 60), (px, py, pw, ph), 4,
                             border_radius=6)
            wf = self.font_title.render("WANTED", True, (180, 30, 20))
            screen.blit(wf, (px + pw // 2 - wf.get_width() // 2, py + 18))
            # 人頭圖案（圓臉）
            pygame.draw.circle(screen, (220, 180, 130),
                                (px + pw // 2, py + 180), 70)
            pygame.draw.circle(screen, (30, 25, 20),
                                (px + pw // 2 - 22, py + 165), 8)
            pygame.draw.circle(screen, (30, 25, 20),
                                (px + pw // 2 + 22, py + 165), 8)
            dead = self.font_body.render("DEAD OR ALIVE", True, (180, 30, 20))
            screen.blit(dead, (px + pw // 2 - dead.get_width() // 2, py + 275))
            bounty = self.font_title.render("1,500,000,000", True, (30, 20, 10))
            screen.blit(bounty, (px + pw // 2 - bounty.get_width() // 2, py + 315))
            bells = self.font_hint.render("貝利", True, (80, 60, 20))
            screen.blit(bells, (px + pw // 2 - bells.get_width() // 2, py + 358))

        if deco == "glow":
            # 中心光暈
            glow_r = int(120 + 20 * math.sin(self._t * 1.5))
            s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*accent, 30), (glow_r, glow_r), glow_r)
            screen.blit(s, (w // 2 - glow_r, h // 2 - glow_r))

        # 橫線分隔
        lc = tuple(min(255, c + 60) for c in accent)
        pygame.draw.line(screen, accent, (60, 100), (w - 60, 100), 2)
        pygame.draw.line(screen, accent, (60, h - 60), (w - 60, h - 60), 1)

        # 標題
        title_surf = self.font_title.render(panel["title"], True, accent)
        screen.blit(title_surf, (80, 50))

        # 頁碼點
        for i in range(len(_PANELS)):
            dot_c = accent if i == self._panel else (60, 60, 80)
            pygame.draw.circle(screen, dot_c, (w // 2 - (len(_PANELS) - 1) * 12 + i * 24, 92), 5)

        # 打字機文字
        chars_shown = int(self._char_pos)
        remaining = chars_shown
        lines = panel["lines"]
        for li, line in enumerate(lines):
            if remaining < 0:
                break
            visible = line[:remaining] if remaining < len(line) else line
            remaining -= len(line)
            if visible and line:
                surf = self.font_body.render(visible, True, (240, 240, 255))
                screen.blit(surf, (80, 130 + li * 40))

        # 打字游標閃爍
        total_chars = sum(len(ln) for ln in lines)
        if self._char_pos < total_chars:
            if int(self._t * 4) % 2 == 0:
                pygame.draw.rect(screen, accent,
                                 (80 + 10, 130 + len(lines) * 40 - 32, 12, 24))
        else:
            # 提示繼續
            progress = self._timer / _PANELS[self._panel]["duration"]
            bar_w = int((w - 160) * min(1.0, progress))
            pygame.draw.rect(screen, (40, 40, 55), (80, h - 45, w - 160, 6),
                             border_radius=3)
            pygame.draw.rect(screen, accent, (80, h - 45, bar_w, 6),
                             border_radius=3)
            hint = ("Space/點擊 繼續    ESC 跳過"
                    if self._panel < len(_PANELS) - 1
                    else "Space/點擊 開始冒險    ESC 跳過")
            hs = self.font_hint.render(hint, True, (140, 140, 160))
            screen.blit(hs, (w // 2 - hs.get_width() // 2, h - 58))

        # 淡入效果
        if self._t < 0.5:
            fade = pygame.Surface((w, h))
            fade.fill((0, 0, 0))
            fade.set_alpha(int(255 * (1 - self._t / 0.5)))
            screen.blit(fade, (0, 0))
