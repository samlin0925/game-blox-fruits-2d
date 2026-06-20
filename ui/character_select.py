import pygame
import math
from utils.font_helper import get_font
from utils.data_loader import load
from ui.sprite_draw import draw_character
from config import SCREEN_WIDTH, SCREEN_HEIGHT

_CARD_W, _CARD_H = 190, 280
_CARD_GAP = 22
_TOTAL_W = _CARD_W * 5 + _CARD_GAP * 4
_START_X = (SCREEN_WIDTH - _TOTAL_W) // 2
_CARD_Y = SCREEN_HEIGHT // 2 - _CARD_H // 2 - 10



class CharacterSelectScreen:
    def __init__(self):
        self.font_title = get_font(40, bold=True)
        self.font_name  = get_font(20, bold=True)
        self.font_sub   = get_font(15)
        self.font_pass  = get_font(14)
        self.font_hint  = get_font(18)

        data = load("characters.json")
        self.characters = data["characters"]
        self.selected = 0
        self._t = 0.0
        self._confirm_flash = 0.0

    def update(self, dt: float, events) -> str:
        self._t += dt
        if self._confirm_flash > 0:
            self._confirm_flash -= dt

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a,
                                 pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.characters)
                elif event.key in (pygame.K_RIGHT, pygame.K_d,
                                   pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.characters)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._confirm_flash = 0.3
                    return self.characters[self.selected]["id"]
                elif event.key == pygame.K_ESCAPE:
                    return "back"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, char in enumerate(self.characters):
                    cx = _START_X + i * (_CARD_W + _CARD_GAP) + _CARD_W // 2
                    if abs(mx - cx) < _CARD_W // 2 and abs(my - _CARD_Y - _CARD_H // 2) < _CARD_H // 2:
                        if self.selected == i:
                            self._confirm_flash = 0.3
                            return char["id"]
                        self.selected = i
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                for i in range(len(self.characters)):
                    cx = _START_X + i * (_CARD_W + _CARD_GAP) + _CARD_W // 2
                    if abs(mx - cx) < _CARD_W // 2 and abs(my - _CARD_Y - _CARD_H // 2) < _CARD_H // 2:
                        self.selected = i
        return ""

    def draw(self, screen):
        # 背景漸層（深藍海洋風）
        screen.fill((8, 18, 42))
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT
        for y in range(h):
            alpha = int(y / h * 40)
            r = min(255, 8 + alpha)
            g = min(255, 18 + alpha // 2)
            b = min(255, 42 + alpha)
            pygame.draw.line(screen, (r, g, b), (0, y), (w, y))

        # 海浪裝飾
        for i in range(8):
            wave_y = h - 80 + int(math.sin(self._t * 1.2 + i * 0.8) * 8)
            wave_x = (i * (w // 7) - int(self._t * 30) % (w // 7 + 60)) % w
            pygame.draw.arc(screen, (30, 80, 160),
                            (wave_x - 40, wave_y, 80, 30), 0, math.pi, 3)

        # 標題
        title1 = self.font_title.render("海賊王 2D", True, (255, 215, 0))
        title2 = self.font_title.render("選擇你的角色", True, (220, 220, 255))
        screen.blit(title1, (w // 2 - title1.get_width() // 2, 28))
        screen.blit(title2, (w // 2 - title2.get_width() // 2, 78))

        # 角色卡片
        for i, char in enumerate(self.characters):
            is_sel = (i == self.selected)
            cx = _START_X + i * (_CARD_W + _CARD_GAP)
            cy_card = _CARD_Y - (18 if is_sel else 0)
            card_rect = (cx, cy_card, _CARD_W, _CARD_H)

            # 卡片底色
            if is_sel:
                border_color = (255, 215, 0)
                bg_color = (35, 28, 10)
            else:
                border_color = (60, 80, 120)
                bg_color = (18, 22, 40)

            pygame.draw.rect(screen, bg_color, card_rect, border_radius=14)
            pygame.draw.rect(screen, border_color, card_rect, 2 if not is_sel else 3,
                             border_radius=14)

            sprite_cx = cx + _CARD_W // 2
            sprite_cy = cy_card + 105
            scale = 1.12 + 0.05 * math.sin(self._t * 3) if is_sel else 1.0
            draw_character(screen, sprite_cx, sprite_cy, char,
                           r=int(32 * scale), t=self._t)

            # 名字
            name_s = self.font_name.render(char["name"], True,
                                           (255, 215, 0) if is_sel else (200, 200, 220))
            screen.blit(name_s, (cx + _CARD_W // 2 - name_s.get_width() // 2,
                                  cy_card + 155))

            # 頭銜
            title_s = self.font_sub.render(char["title"], True, (160, 160, 200))
            screen.blit(title_s, (cx + _CARD_W // 2 - title_s.get_width() // 2,
                                   cy_card + 178))

            # 被選中時顯示說明
            if is_sel:
                # 能力加成
                bonus = char["stat_bonus"]
                lines = []
                if bonus["max_health"]:  lines.append(f"HP +{bonus['max_health']}")
                if bonus["base_attack"]: lines.append(f"攻擊 +{bonus['base_attack']}")
                if bonus["defense"]:     lines.append(f"防禦 +{bonus['defense']}")
                if bonus["crit_rate"]:   lines.append(f"暴擊 +{bonus['crit_rate']}%")
                if bonus["speed"]:       lines.append(f"速度 +{bonus['speed']}")
                for j, line in enumerate(lines):
                    s = self.font_sub.render(line, True, (100, 220, 120))
                    screen.blit(s, (cx + _CARD_W // 2 - s.get_width() // 2,
                                    cy_card + 202 + j * 20))

        # 被選角色的被動技能說明（底部）
        sel_char = self.characters[self.selected]
        passive_bg = pygame.Surface((700, 52), pygame.SRCALPHA)
        passive_bg.fill((0, 0, 0, 160))
        screen.blit(passive_bg, (w // 2 - 350, h - 108))
        ps = self.font_pass.render(f"被動技能: {sel_char['passive']}", True, (255, 200, 80))
        desc_s = self.font_pass.render(sel_char["description"], True, (180, 180, 220))
        screen.blit(ps,    (w // 2 - ps.get_width() // 2, h - 104))
        screen.blit(desc_s, (w // 2 - desc_s.get_width() // 2, h - 84))

        # 操作提示
        hint_s = self.font_hint.render("← → 選擇角色   Enter 確認   ESC 返回", True,
                                        (140, 160, 200))
        screen.blit(hint_s, (w // 2 - hint_s.get_width() // 2, h - 46))

        # 確認閃爍
        if self._confirm_flash > 0:
            flash = pygame.Surface((w, h), pygame.SRCALPHA)
            alpha = int(self._confirm_flash / 0.3 * 120)
            flash.fill((255, 255, 255, alpha))
            screen.blit(flash, (0, 0))
