"""
通關結局動畫（擊敗全部三位大將後觸發）
4 個故事板 + 滾動字幕
Space/Enter = 加速，ESC = 跳過
"""

import pygame
import math
import random
from utils.font_helper import get_font
from config import SCREEN_WIDTH, SCREEN_HEIGHT


_PANELS = [
    {
        "bg": (30, 8, 8),
        "accent": (255, 100, 50),
        "title": "最後一戰",
        "lines": [
            "赤犬、黃猿、青雉……",
            "三位海軍大將，",
            "皆倒在了你的腳下。",
            "",
            "偉大的航路，為之震撼。",
        ],
        "deco": "fire",
        "duration": 5.0,
    },
    {
        "bg": (5, 15, 40),
        "accent": (100, 180, 255),
        "title": "傳說的誕生",
        "lines": [
            "你的名字，",
            "開始在整個大海上流傳。",
            "",
            "「那個人……」",
            "「擊敗了三大將……」",
            "「他是下一個海賊王！」",
        ],
        "deco": "stars",
        "duration": 5.5,
    },
    {
        "bg": (5, 25, 10),
        "accent": (120, 220, 100),
        "title": "果實的覺醒",
        "lines": [
            "惡魔果實的力量在你體內燃燒，",
            "超越了任何前人的極限。",
            "",
            "偉大的航路，",
            "終於向你敞開了她的大門。",
        ],
        "deco": "glow",
        "duration": 5.5,
    },
    {
        "bg": (10, 5, 25),
        "accent": (255, 215, 0),
        "title": "海賊王",
        "lines": [
            "在這片廣闊的大海上，",
            "只有一個人能成為海賊王。",
            "",
            "「我會成為海賊王！」",
            "",
            "—— 這個夢想，",
            "今天成真了。",
        ],
        "deco": "gold",
        "duration": 7.0,
    },
]

_CREDITS = [
    ("", ""),
    ("製作", "Sam Lin"),
    ("", ""),
    ("引擎", "Python 3.10 + Pygame 2.6"),
    ("音樂音效", "NumPy 程式合成"),
    ("美術", "全程式繪製"),
    ("", ""),
    ("感謝遊玩", ""),
    ("", ""),
    ("特別致敬", "尾田榮一郎《航海王》"),
    ("", ""),
    ("GAME CLEAR", ""),
]

_CHARS_PER_SEC = 25


class EndingCutscene:
    def __init__(self, player=None):
        self.font_title  = get_font(38, bold=True)
        self.font_body   = get_font(22)
        self.font_hint   = get_font(15)
        self.font_credit = get_font(26, bold=True)
        self.font_credit_val = get_font(24)
        self._player = player
        self._panel = 0
        self._char_pos = 0.0
        self._timer = 0.0
        self._done = False
        self._in_credits = False
        self._credit_scroll = float(SCREEN_HEIGHT)
        self._t = 0.0
        self._particles = []
        self._stars = [
            (random.randint(0, SCREEN_WIDTH),
             random.randint(0, SCREEN_HEIGHT),
             random.choice([1, 1, 2]),
             random.uniform(0, 6.28))
            for _ in range(140)
        ]

    @property
    def done(self):
        return self._done

    def update(self, dt: float, events) -> bool:
        if self._done:
            return True
        self._t += dt

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._done = True
                    return True
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self._fast_forward()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._fast_forward()

        if self._in_credits:
            self._credit_scroll -= dt * 55
            line_h = 50
            total_h = len(_CREDITS) * line_h + SCREEN_HEIGHT
            if self._credit_scroll < -total_h:
                self._done = True
            return self._done

        panel = _PANELS[self._panel]
        total_chars = sum(len(ln) for ln in panel["lines"])
        self._char_pos += _CHARS_PER_SEC * dt
        self._timer += dt

        # 金色粒子（最後一板）
        if self._panel == len(_PANELS) - 1 and self._t > 1.0:
            if random.random() < 0.35:
                self._particles.append({
                    "x": random.uniform(0, SCREEN_WIDTH),
                    "y": random.uniform(SCREEN_HEIGHT * 0.3, SCREEN_HEIGHT * 0.8),
                    "vx": random.uniform(-30, 30),
                    "vy": random.uniform(-80, -20),
                    "life": random.uniform(1.5, 3.0),
                    "max_life": 3.0,
                    "r": random.randint(4, 10),
                    "c": (255, random.randint(180, 215), 0),
                })
        for p in self._particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
        self._particles = [p for p in self._particles if p["life"] > 0]

        if self._timer >= panel["duration"] and self._char_pos >= total_chars:
            self._advance()

        return self._done

    def _fast_forward(self):
        if self._in_credits:
            self._credit_scroll -= 200
        else:
            panel = _PANELS[self._panel]
            total_chars = sum(len(ln) for ln in panel["lines"])
            if self._char_pos < total_chars:
                self._char_pos = total_chars + 1
            else:
                self._advance()

    def _advance(self):
        self._panel += 1
        if self._panel >= len(_PANELS):
            self._in_credits = True
            self._credit_scroll = float(SCREEN_HEIGHT)
        else:
            self._char_pos = 0.0
            self._timer = 0.0
            self._t = 0.0

    def draw(self, screen):
        if self._done:
            return
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT

        if self._in_credits:
            self._draw_credits(screen)
            return

        panel = _PANELS[self._panel]
        bg = panel["bg"]
        accent = panel["accent"]
        screen.fill(bg)

        deco = panel.get("deco", "")

        if deco in ("stars", "gold"):
            for sx, sy, sr, sphase in self._stars:
                bval = 0.5 + 0.5 * math.sin(sphase + self._t * 1.2)
                c = int(200 * bval)
                pygame.draw.circle(screen, (c, c, int(c * 0.9)), (sx, sy), sr)

        if deco == "fire":
            for i in range(20):
                fx = random.randint(0, w)
                fy = random.randint(int(h * 0.7), h)
                fr = random.randint(4, 18)
                fc = (255, random.randint(60, 160), 0)
                s = pygame.Surface((fr * 2, fr * 3), pygame.SRCALPHA)
                pygame.draw.ellipse(s, (*fc, 120), (0, fr, fr * 2, fr * 2))
                pygame.draw.ellipse(s, (255, 200, 0, 80), (fr // 2, 0, fr, fr * 2))
                screen.blit(s, (fx - fr, fy - fr))

        if deco == "glow":
            glow_r = int(150 + 25 * math.sin(self._t * 1.2))
            s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*accent, 25), (glow_r, glow_r), glow_r)
            screen.blit(s, (w // 2 - glow_r, h // 2 - glow_r - 40))

        if deco == "gold":
            for p in self._particles:
                alpha = int(255 * (p["life"] / p["max_life"]))
                s = pygame.Surface((p["r"] * 2, p["r"] * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*p["c"], alpha), (p["r"], p["r"]), p["r"])
                screen.blit(s, (int(p["x"]) - p["r"], int(p["y"]) - p["r"]))

        # 頁碼
        for i in range(len(_PANELS)):
            dot_c = accent if i == self._panel else (50, 50, 65)
            pygame.draw.circle(screen, dot_c,
                                (w // 2 - (len(_PANELS) - 1) * 12 + i * 24, 92), 5)

        pygame.draw.line(screen, accent, (60, 100), (w - 60, 100), 2)

        # 標題
        ts = self.font_title.render(panel["title"], True, accent)
        screen.blit(ts, (80, 46))

        # 打字機文字
        chars_shown = int(self._char_pos)
        remaining = chars_shown
        for li, line in enumerate(panel["lines"]):
            if remaining < 0:
                break
            visible = line[:remaining] if remaining < len(line) else line
            remaining -= len(line)
            if visible and line:
                sf = self.font_body.render(visible, True, (240, 240, 255))
                screen.blit(sf, (80, 130 + li * 44))

        total_chars = sum(len(ln) for ln in panel["lines"])
        if self._char_pos >= total_chars:
            progress = self._timer / panel["duration"]
            bar_w = int((w - 160) * min(1.0, progress))
            pygame.draw.rect(screen, (40, 40, 55), (80, h - 45, w - 160, 6), border_radius=3)
            pygame.draw.rect(screen, accent, (80, h - 45, bar_w, 6), border_radius=3)
            label = "Space 繼續    ESC 跳過" if self._panel < len(_PANELS) - 1 else "Space 查看製作人員    ESC 結束"
            hs = self.font_hint.render(label, True, (140, 140, 160))
            screen.blit(hs, (w // 2 - hs.get_width() // 2, h - 58))

        if self._t < 0.6:
            fade = pygame.Surface((w, h))
            fade.fill((0, 0, 0))
            fade.set_alpha(int(255 * (1 - self._t / 0.6)))
            screen.blit(fade, (0, 0))

    def _draw_credits(self, screen):
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT
        screen.fill((5, 5, 15))
        for sx, sy, sr, sphase in self._stars:
            bval = 0.4 + 0.4 * math.sin(sphase + self._t * 0.8)
            c = int(160 * bval)
            pygame.draw.circle(screen, (c, c, int(c * 0.9)), (sx, sy), sr)

        line_h = 50
        y0 = int(self._credit_scroll)
        for i, (label, value) in enumerate(_CREDITS):
            y = y0 + i * line_h
            if y < -line_h or y > h + line_h:
                continue
            if label == "GAME CLEAR":
                gc = self.font_title.render("GAME CLEAR", True, (255, 215, 0))
                screen.blit(gc, (w // 2 - gc.get_width() // 2, y))
            elif label and value:
                ls = self.font_credit.render(label, True, (180, 180, 220))
                vs = self.font_credit_val.render(value, True, (255, 255, 255))
                screen.blit(ls, (w // 2 - 180, y))
                screen.blit(vs, (w // 2 + 20, y + 2))
            elif label:
                ls = self.font_credit.render(label, True, (220, 200, 150))
                screen.blit(ls, (w // 2 - ls.get_width() // 2, y))

        hs = self.font_hint.render("ESC 結束", True, (100, 100, 120))
        screen.blit(hs, (w // 2 - hs.get_width() // 2, h - 40))
