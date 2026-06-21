import pygame
import math
from core.constants import WHITE, YELLOW
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.font_helper import get_font

_ACTIONS = ["resume", "save", "menu"]
_LABELS  = ["▶  繼續遊戲", "💾  儲存遊戲", "⬅  回主選單"]

class PauseMenu:
    def __init__(self):
        self.font_title = get_font(44, bold=True)
        self.font_btn   = get_font(22, bold=True)
        self.font_m     = get_font(18)
        self.font_s     = get_font(15)
        self._sel = 0
        self._t   = 0.0
        self._btn_rects = []

    def update(self, dt, events) -> str:
        self._t += dt
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE:
                    return "resume"
                elif k in (pygame.K_UP, pygame.K_w):
                    self._sel = (self._sel - 1) % len(_ACTIONS)
                elif k in (pygame.K_DOWN, pygame.K_s):
                    self._sel = (self._sel + 1) % len(_ACTIONS)
                elif k in (pygame.K_RETURN, pygame.K_SPACE):
                    return _ACTIONS[self._sel]
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self._btn_rects):
                    if rect.collidepoint(event.pos):
                        return _ACTIONS[i]
            if event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(self._btn_rects):
                    if rect.collidepoint(mouse_pos):
                        self._sel = i
        return ""

    def draw(self, screen, player=None):
        has_player = player is not None
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        panel_w = 560
        panel_h = 500 if has_player else 290
        px = SCREEN_WIDTH // 2 - panel_w // 2
        py = SCREEN_HEIGHT // 2 - panel_h // 2

        pygame.draw.rect(screen, (15, 15, 35), (px, py, panel_w, panel_h), border_radius=14)
        pygame.draw.rect(screen, (80, 100, 180), (px, py, panel_w, panel_h), 2, border_radius=14)

        # ── Title ─────────────────────────────────────────────────────────────
        title = self.font_title.render("⏸  暫停", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 14))

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_w, btn_h = 280, 46
        btn_x = SCREEN_WIDTH // 2 - btn_w // 2
        self._btn_rects = []
        btn_colors = [(55, 80, 140), (55, 80, 140), (90, 40, 40)]
        btn_hover   = [(80, 110, 190), (80, 110, 190), (130, 60, 60)]
        for i, label in enumerate(_LABELS):
            by = py + 70 + i * 56
            is_sel = (i == self._sel)
            col = btn_hover[i] if is_sel else btn_colors[i]
            rect = pygame.Rect(btn_x, by, btn_w, btn_h)
            self._btn_rects.append(rect)
            pygame.draw.rect(screen, col, rect, border_radius=8)
            if is_sel:
                pulse = int(160 + 95 * math.sin(self._t * 5))
                pygame.draw.rect(screen, (pulse, pulse, 80), rect, 3, border_radius=8)
            else:
                pygame.draw.rect(screen, WHITE, rect, 1, border_radius=8)
            surf = self.font_btn.render(label, True, WHITE)
            screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                               rect.centery - surf.get_height() // 2))

        # Key hint
        hint = self.font_s.render("↑↓ 選擇  Enter 確認  ESC 繼續", True, (110, 110, 135))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, py + 248))

        if not has_player:
            return

        # ── Divider ───────────────────────────────────────────────────────────
        div_y = py + 266
        pygame.draw.line(screen, (60, 60, 100),
                         (px + 20, div_y), (px + panel_w - 20, div_y), 1)

        # ── Stats (two-column layout) ──────────────────────────────────────────
        sx    = px + 28          # left column x
        mid_x = px + panel_w // 2 + 10   # right column x
        sy    = div_y + 10

        fruit_name = player.current_fruit["name"] if player.current_fruit else "未覺醒"
        fruit_col  = tuple(player.current_fruit["color"]) if player.current_fruit else (140, 140, 140)

        left_stats = [
            (f"等級：Lv.{player.level}", YELLOW),
            (f"血量：{player.health} / {player.max_health}", (100, 220, 100)),
            (f"攻擊力：{player.base_attack}", (220, 160, 100)),
            (f"防禦力：{player.defense}", (120, 180, 255)),
        ]
        right_stats = [
            (f"稱號：{player.title}", (210, 210, 190)),
            (f"暴擊率：{player.crit_rate}%", (240, 220, 80)),
            (f"金幣：{player.gold} G", (255, 215, 0)),
            (f"果實：{fruit_name}", fruit_col),
        ]
        for i, (text, col) in enumerate(left_stats):
            s = self.font_m.render(text, True, col)
            screen.blit(s, (sx, sy + i * 26))
        for i, (text, col) in enumerate(right_stats):
            s = self.font_m.render(text, True, col)
            screen.blit(s, (mid_x, sy + i * 26))

        # ── Items section ─────────────────────────────────────────────────────
        iy = sy + 4 * 26 + 10
        pygame.draw.line(screen, (60, 60, 100),
                         (px + 20, iy - 4), (px + panel_w - 20, iy - 4), 1)

        itl = self.font_s.render("▸ 道具欄  （遊戲中使用）", True, (160, 160, 190))
        screen.blit(itl, (sx, iy))

        potions = getattr(player, "potions", 0)
        tickets = getattr(player, "gacha_tickets", 0)
        frags   = sum(player.fruit_fragments.values())

        rows = [
            (f"💊 生命藥水  ×{potions}/5",
             "按 H 鍵使用，回復 50% 血量",
             (100, 240, 130) if potions > 0 else (70, 70, 70)),
            (f"🎰 抽卡券  ×{tickets} 張",
             "靠近祭壇按 T → 切換到抽卡頁籤",
             (120, 180, 255) if tickets > 0 else (70, 70, 70)),
            (f"💎 果實碎片  共 {frags} 片",
             "靠近祭壇按 T → 切換到果實覺醒頁籤",
             (200, 180, 100) if frags > 0 else (70, 70, 70)),
        ]
        for ri, (main, hint_txt, col) in enumerate(rows):
            ry = iy + 22 + ri * 42
            ms = self.font_m.render(main, True, col)
            screen.blit(ms, (sx, ry))
            hs = self.font_s.render(hint_txt, True, (130, 130, 150))
            screen.blit(hs, (sx + 10, ry + 21))
