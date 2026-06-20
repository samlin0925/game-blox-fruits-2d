import pygame
import math
from core.constants import WHITE, YELLOW
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.font_helper import get_font
from systems.gacha_system import get_all_fruits

# ── Shop catalogue ─────────────────────────────────────────────────────────────
SHOP_ITEMS = [
    {
        "id": "gacha",
        "name": "碎片扭蛋",
        "desc": "隨機獲得 1 個惡魔果實碎片",
        "cost": 100,
        "icon_color": (180, 120, 220),
    },
    {
        "id": "heal",
        "name": "生命藥水",
        "desc": "立即恢復 50% 最大生命值",
        "cost": 200,
        "icon_color": (230, 50, 60),
    },
    {
        "id": "atk_up",
        "name": "力量強化",
        "desc": "本局永久 +8 攻擊力",
        "cost": 500,
        "icon_color": (255, 100, 50),
    },
    {
        "id": "def_up",
        "name": "防禦強化",
        "desc": "本局永久 +8 防禦力",
        "cost": 100,
        "icon_color": (80, 160, 255),
    },
    {
        "id": "crit_up",
        "name": "幸運符",
        "desc": "本局永久 +10% 暴擊率",
        "cost": 350,
        "icon_color": (255, 215, 0),
    },
]


class DialogBox:
    def __init__(self):
        self.font_l = get_font(36, bold=True)
        self.font_m = get_font(22)
        self.font_s = get_font(16)
        self._t = 0.0

    def update(self, dt: float):
        self._t += dt

    # ── In-game notifications ──────────────────────────────────────────────────

    def draw_game_over(self, screen, player, kill_count: int):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        title = self.font_l.render("GAME OVER", True, (220, 50, 50))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 220))
        lines = [
            f"等級: Lv.{player.level}",
            f"擊殺數: {kill_count}",
            f"金幣: {player.gold}",
            "",
            "R 重新開始  |  ESC 回主選單",
        ]
        for i, line in enumerate(lines):
            color = YELLOW if i < 3 else WHITE
            surf = self.font_m.render(line, True, color)
            screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2,
                                290 + i * 34))

    def draw_level_up_banner(self, screen, level: int, milestone=None):
        banner_h = 80
        s = pygame.Surface((SCREEN_WIDTH, banner_h), pygame.SRCALPHA)
        s.fill((255, 215, 0, 55))
        screen.blit(s, (0, SCREEN_HEIGHT // 2 - banner_h // 2))
        text = f"★ LEVEL UP!  Lv.{level} ★"
        surf = self.font_l.render(text, True, YELLOW)
        screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2,
                            SCREEN_HEIGHT // 2 - surf.get_height() // 2))
        if milestone:
            ms_surf = self.font_m.render(
                f"里程碑: {milestone['name']}  達成！", True, (255, 200, 100))
            screen.blit(ms_surf,
                        (SCREEN_WIDTH // 2 - ms_surf.get_width() // 2,
                         SCREEN_HEIGHT // 2 + 46))

    def draw_cheat_result(self, screen, message: str, timer: float):
        if timer <= 0:
            return
        alpha = min(255, int(timer * 255 / 2.5))
        is_success = "成功" in message or ("無效" not in message and "上限" not in message and "失敗" not in message)
        color = (50, 200, 80) if is_success else (200, 80, 80)
        surf = self.font_m.render(message, True, color)
        x = SCREEN_WIDTH // 2 - surf.get_width() // 2
        y = SCREEN_HEIGHT // 2 + 100
        bg = pygame.Surface((surf.get_width() + 20, surf.get_height() + 10),
                             pygame.SRCALPHA)
        bg.fill((0, 0, 0, min(200, alpha)))
        screen.blit(bg, (x - 10, y - 5))
        screen.blit(surf, (x, y))

    # ── Altar UI ───────────────────────────────────────────────────────────────

    def draw_altar(self, screen, player, selected_index: int = 0, tab: int = 0):
        """
        tab 0 = 果實覺醒
        tab 1 = 商店
        Returns "".
        """
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        panel_w, panel_h = 740, 500
        px = SCREEN_WIDTH // 2 - panel_w // 2
        py = SCREEN_HEIGHT // 2 - panel_h // 2

        pygame.draw.rect(screen, (18, 12, 32), (px, py, panel_w, panel_h),
                         border_radius=14)
        pygame.draw.rect(screen, (200, 160, 0), (px, py, panel_w, panel_h),
                         3, border_radius=14)

        # ── Tab bar ──────────────────────────────────────────────────────────
        tab_labels = ["⚔ 果實覺醒", "🛒 商店"]
        tab_w = panel_w // 2
        for ti, label in enumerate(tab_labels):
            tx = px + ti * tab_w
            ty = py
            is_active = (ti == tab)
            tab_bg = (40, 30, 60) if is_active else (20, 15, 30)
            tab_border = (255, 200, 0) if is_active else (80, 70, 100)
            pygame.draw.rect(screen, tab_bg,
                             (tx + 2, ty + 2, tab_w - 4, 40), border_radius=8)
            pygame.draw.rect(screen, tab_border,
                             (tx + 2, ty + 2, tab_w - 4, 40), 2, border_radius=8)
            lsurf = self.font_m.render(label, True,
                                        (255, 220, 80) if is_active else (140, 140, 160))
            screen.blit(lsurf, (tx + tab_w // 2 - lsurf.get_width() // 2, ty + 10))

        # ── Content area ─────────────────────────────────────────────────────
        content_y = py + 50
        if tab == 0:
            self._draw_awaken_tab(screen, player, px, content_y, panel_w, selected_index)
        else:
            self._draw_shop_tab(screen, player, px, content_y, panel_w, selected_index)

        # ── Bottom hint ───────────────────────────────────────────────────────
        hints = "↑↓ 選擇  ←→ 切換頁籤  Enter 確認  T/ESC 關閉"
        hint_s = self.font_s.render(hints, True, (140, 140, 160))
        screen.blit(hint_s,
                    (SCREEN_WIDTH // 2 - hint_s.get_width() // 2,
                     py + panel_h - 24))
        return ""

    def _draw_awaken_tab(self, screen, player, px, start_y, panel_w, selected):
        fruits = get_all_fruits()
        row_h = 64
        t = self._t
        for i, fruit in enumerate(fruits):
            fy = start_y + 8 + i * row_h
            frag_count = player.fruit_fragments.get(fruit["id"], 0)
            req = fruit["fragments_required"]
            can = frag_count >= req
            is_sel = (i == selected)

            # Row background
            if is_sel:
                row_bg = (50, 40, 80) if can else (50, 30, 50)
            else:
                row_bg = (28, 48, 28) if can else (28, 18, 28)
            pygame.draw.rect(screen, row_bg,
                             (px + 10, fy, panel_w - 20, row_h - 6),
                             border_radius=8)

            border_c = (tuple(fruit["color"]) if can else (60, 60, 60))
            if is_sel:
                # Pulsing selection border
                pulse = int(160 + 95 * math.sin(t * 4))
                border_c = (pulse, pulse, 50) if not can else (
                    min(255, fruit["color"][0] + 80),
                    min(255, fruit["color"][1] + 80),
                    min(255, fruit["color"][2] + 80),
                )
                pygame.draw.rect(screen, border_c,
                                 (px + 10, fy, panel_w - 20, row_h - 6),
                                 3, border_radius=8)
                # Selection arrow
                arrow_x = px + panel_w - 30
                arrow_y = fy + (row_h - 6) // 2
                pygame.draw.polygon(screen, (255, 220, 50), [
                    (arrow_x - 8, arrow_y - 8),
                    (arrow_x + 2, arrow_y),
                    (arrow_x - 8, arrow_y + 8),
                ])
            else:
                pygame.draw.rect(screen, border_c,
                                 (px + 10, fy, panel_w - 20, row_h - 6),
                                 2, border_radius=8)

            # Fruit color orb
            orb_x = px + 40
            orb_y = fy + (row_h - 6) // 2
            pygame.draw.circle(screen, tuple(fruit["color"]), (orb_x, orb_y), 14)
            pygame.draw.circle(screen, (255, 255, 255), (orb_x, orb_y), 14, 1)
            pygame.draw.circle(screen, (255, 255, 255), (orb_x - 4, orb_y - 4), 4)

            # Name + rarity
            name_c = tuple(fruit["color"]) if can else (120, 120, 120)
            name_s = self.font_m.render(fruit["name"], True, name_c)
            screen.blit(name_s, (px + 64, fy + 6))
            rar_s = self.font_s.render(
                f"[{fruit['rarity'].upper()}]", True, (160, 160, 160))
            screen.blit(rar_s, (px + 64, fy + 32))

            # Fragment count
            frag_text = f"{frag_count} / {req} 碎片"
            frag_color = (100, 255, 100) if can else (200, 100, 100)
            frag_s = self.font_m.render(frag_text, True, frag_color)
            screen.blit(frag_s, (px + panel_w - frag_s.get_width() - 130, fy + 16))

            # Status
            if can:
                st_s = self.font_s.render("✓ 可覺醒 [Enter]", True, (100, 255, 100))
            else:
                st_s = self.font_s.render(f"缺 {req - frag_count} 片", True, (160, 160, 160))
            screen.blit(st_s, (px + panel_w - st_s.get_width() - 20, fy + 36))

        # Currently equipped info
        if player.current_fruit:
            cf = player.current_fruit
            eq_s = self.font_s.render(
                f"裝備中: {cf['name']}", True, tuple(cf["color"]))
            screen.blit(eq_s, (px + 14, start_y + 8 + len(fruits) * row_h))

    def _draw_shop_tab(self, screen, player, px, start_y, panel_w, selected):
        row_h = 72
        t = self._t
        for i, item in enumerate(SHOP_ITEMS):
            fy = start_y + 8 + i * row_h
            can_afford = player.gold >= item["cost"]
            is_sel = (i == selected)

            if is_sel:
                row_bg = (40, 40, 20) if can_afford else (40, 20, 20)
            else:
                row_bg = (28, 28, 12) if can_afford else (22, 15, 15)
            pygame.draw.rect(screen, row_bg,
                             (px + 10, fy, panel_w - 20, row_h - 6),
                             border_radius=8)

            if is_sel:
                pulse = int(160 + 95 * math.sin(t * 4))
                border_c = (pulse, pulse, 50) if can_afford else (pulse, 60, 60)
                pygame.draw.rect(screen, border_c,
                                 (px + 10, fy, panel_w - 20, row_h - 6),
                                 3, border_radius=8)
                arrow_x = px + panel_w - 30
                arrow_y = fy + (row_h - 6) // 2
                pygame.draw.polygon(screen, (255, 220, 50), [
                    (arrow_x - 8, arrow_y - 8),
                    (arrow_x + 2, arrow_y),
                    (arrow_x - 8, arrow_y + 8),
                ])
            else:
                pygame.draw.rect(screen,
                                 (100, 90, 40) if can_afford else (60, 40, 40),
                                 (px + 10, fy, panel_w - 20, row_h - 6),
                                 1, border_radius=8)

            # Icon circle
            icon_x = px + 40
            icon_y = fy + (row_h - 6) // 2
            pygame.draw.circle(screen, item["icon_color"], (icon_x, icon_y), 14)
            pygame.draw.circle(screen, (255, 255, 255), (icon_x, icon_y), 14, 1)
            pygame.draw.circle(screen, (255, 255, 255), (icon_x - 4, icon_y - 4), 3)

            # Name + desc
            name_c = (255, 220, 100) if can_afford else (120, 120, 120)
            name_s = self.font_m.render(item["name"], True, name_c)
            screen.blit(name_s, (px + 64, fy + 6))
            desc_s = self.font_s.render(item["desc"], True, (180, 180, 180))
            screen.blit(desc_s, (px + 64, fy + 32))

            # Cost
            cost_c = (255, 215, 0) if can_afford else (180, 100, 100)
            cost_s = self.font_m.render(f"💰 {item['cost']} G", True, cost_c)
            screen.blit(cost_s, (px + panel_w - cost_s.get_width() - 20, fy + 18))

        # Player gold display
        gold_s = self.font_m.render(f"目前金幣: {player.gold} G", True, YELLOW)
        bottom_y = start_y + 8 + len(SHOP_ITEMS) * row_h + 4
        screen.blit(gold_s, (px + 14, bottom_y))
