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
        "desc": "加入背包（最多5瓶），遊戲中按 H 使用",
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
        fade = min(1.0, timer / 0.4) * min(1.0, timer)
        alpha = int(255 * fade)
        fail_kw = ("不足", "已滿", "無效", "失敗", "上限")
        is_fail = any(k in message for k in fail_kw)
        text_col = (220, 80, 80) if is_fail else (80, 240, 120)
        border_col = (180, 50, 50, alpha) if is_fail else (60, 200, 100, alpha)

        font = get_font(20, bold=True)
        surf = font.render(message, True, text_col)
        pad_x, pad_y = 22, 10
        w = surf.get_width() + pad_x * 2
        h = surf.get_height() + pad_y * 2
        x = SCREEN_WIDTH // 2 - w // 2
        y = SCREEN_HEIGHT - 110

        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((8, 8, 20, min(220, alpha)))
        screen.blit(bg, (x, y))
        pygame.draw.rect(screen, border_col[:3], (x, y, w, h), 2, border_radius=6)
        screen.blit(surf, (x + pad_x, y + pad_y))

    # ── Boss announcement ──────────────────────────────────────────────────────

    def draw_boss_announce(self, screen, name: str, title: str, timer: float):
        if timer <= 0:
            return
        total = 4.0
        fade = min(1.0, timer / 1.0) * min(1.0, (total - timer) / 0.5 + 0.5)
        alpha = int(240 * fade)
        t = self._t
        banner_h = 130
        by = SCREEN_HEIGHT // 3 - banner_h // 2
        s = pygame.Surface((SCREEN_WIDTH, banner_h), pygame.SRCALPHA)
        s.fill((30, 0, 0, min(200, alpha)))
        screen.blit(s, (0, by))
        border_pulse = int(180 + 75 * math.sin(t * 6))
        pygame.draw.line(screen, (border_pulse, 40, 0), (0, by), (SCREEN_WIDTH, by), 3)
        pygame.draw.line(screen, (border_pulse, 40, 0), (0, by + banner_h), (SCREEN_WIDTH, by + banner_h), 3)

        warn_s = self.font_s.render("⚠ BOSS 登場！", True, (255, 80, 80))
        screen.blit(warn_s, (SCREEN_WIDTH // 2 - warn_s.get_width() // 2, by + 8))

        pulse = 0.85 + 0.15 * math.sin(t * 8)
        name_color = (int(255 * pulse), int(80 * pulse), int(40 * pulse))
        name_font = get_font(48, bold=True)
        name_s = name_font.render(name, True, name_color)
        screen.blit(name_s, (SCREEN_WIDTH // 2 - name_s.get_width() // 2, by + 32))

        if title:
            title_s = self.font_m.render(f"— {title} —", True, (255, 200, 100))
            screen.blit(title_s, (SCREEN_WIDTH // 2 - title_s.get_width() // 2, by + 92))

    # ── Gacha result display ───────────────────────────────────────────────────

    def draw_gacha_result(self, screen, results: list, timer: float):
        if not results or timer <= 0:
            return
        total = 6.0
        alpha = min(255, int(255 * min(1.0, timer / 0.5) * min(1.0, timer / 0.5)))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(200, alpha)))
        screen.blit(overlay, (0, 0))

        panel_w = min(720, SCREEN_WIDTH - 40)
        panel_h = 340
        px = SCREEN_WIDTH // 2 - panel_w // 2
        py = SCREEN_HEIGHT // 2 - panel_h // 2
        pygame.draw.rect(screen, (18, 8, 36), (px, py, panel_w, panel_h), border_radius=14)
        pygame.draw.rect(screen, (200, 160, 0), (px, py, panel_w, panel_h), 3, border_radius=14)

        title_s = self.font_l.render("🎰 抽卡結果", True, YELLOW)
        screen.blit(title_s, (SCREEN_WIDTH // 2 - title_s.get_width() // 2, py + 12))

        n = len(results)
        cell_w = max(60, (panel_w - 40) // max(1, n))
        for i, fruit in enumerate(results):
            cx = px + 20 + i * cell_w + cell_w // 2
            cy = py + 130
            rarity = fruit.get("rarity", "common")
            glow_c = (255, 200, 0) if rarity == "legendary" else (
                      (120, 200, 255) if rarity == "rare" else (100, 200, 100))
            # Glow ring
            glow_r = 28 + int(4 * math.sin(self._t * 5 + i))
            pygame.draw.circle(screen, glow_c, (cx, cy), glow_r, 3)
            pygame.draw.circle(screen, tuple(fruit["color"]), (cx, cy), 22)
            pygame.draw.circle(screen, (255, 255, 255), (cx, cy), 22, 1)
            pygame.draw.circle(screen, (255, 255, 255), (cx - 6, cy - 6), 6)

            name_s = self.font_s.render(fruit["name"], True, tuple(fruit["color"]))
            screen.blit(name_s, (cx - name_s.get_width() // 2, cy + 30))
            rar_c = (255, 200, 0) if rarity == "legendary" else (
                    (100, 180, 255) if rarity == "rare" else (180, 180, 180))
            rar_s = self.font_s.render(rarity.upper(), True, rar_c)
            screen.blit(rar_s, (cx - rar_s.get_width() // 2, cy + 50))

        hint_s = self.font_s.render("碎片已加入背包！前往覺醒頁籤使用", True, (160, 220, 160))
        screen.blit(hint_s, (SCREEN_WIDTH // 2 - hint_s.get_width() // 2, py + panel_h - 36))
        close_s = self.font_s.render("按 SPACE / ENTER 關閉，或等待自動消失", True, (120, 120, 140))
        screen.blit(close_s, (SCREEN_WIDTH // 2 - close_s.get_width() // 2, py + panel_h - 16))

    # ── Altar UI ───────────────────────────────────────────────────────────────

    def draw_altar(self, screen, player, selected_index: int = 0, tab: int = 0):
        """
        tab 0 = 果實覺醒
        tab 1 = 商店
        tab 2 = 抽卡
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
        tab_labels = ["⚔ 果實覺醒", "🛒 商店", "🎰 抽卡"]
        tab_w = panel_w // 3
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
            lsurf = self.font_s.render(label, True,
                                        (255, 220, 80) if is_active else (140, 140, 160))
            screen.blit(lsurf, (tx + tab_w // 2 - lsurf.get_width() // 2, ty + 12))

        # ── Content area ─────────────────────────────────────────────────────
        content_y = py + 50
        if tab == 0:
            self._draw_awaken_tab(screen, player, px, content_y, panel_w, selected_index)
        elif tab == 1:
            self._draw_shop_tab(screen, player, px, content_y, panel_w, selected_index)
        else:
            self._draw_gacha_tab(screen, player, px, content_y, panel_w, selected_index)

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

        # Player gold display + potion count
        gold_s = self.font_m.render(f"目前金幣: {player.gold} G", True, YELLOW)
        bottom_y = start_y + 8 + len(SHOP_ITEMS) * row_h + 4
        screen.blit(gold_s, (px + 14, bottom_y))
        potion_count = getattr(player, 'potions', 0)
        pot_s = self.font_s.render(f"藥水庫存: {potion_count}/5  (遊戲中按 H 使用)", True, (180, 255, 180))
        screen.blit(pot_s, (px + 14, bottom_y + 26))

    def _draw_gacha_tab(self, screen, player, px, start_y, panel_w, selected):
        t = self._t
        tickets = getattr(player, 'gacha_tickets', 0)
        cx = px + panel_w // 2

        # Title decoration
        pulse = 0.8 + 0.2 * math.sin(t * 2)
        for i in range(5):
            a = t * 1.5 + i * math.pi * 2 / 5
            dx = int(math.cos(a) * 60)
            dy = int(math.sin(a) * 20)
            orb_c = [(255, 100, 100), (255, 200, 50), (100, 255, 100),
                     (100, 150, 255), (200, 100, 255)][i]
            pygame.draw.circle(screen, orb_c, (cx + dx, start_y + 50 + dy), 6)

        title_s = self.font_l.render("惡魔果實抽卡", True, YELLOW)
        screen.blit(title_s, (cx - title_s.get_width() // 2, start_y + 20))

        # Tickets info
        ticket_s = self.font_m.render(f"抽卡券: {tickets} 張  (升等里程碑可獲得)", True,
                                       (180, 220, 255) if tickets > 0 else (120, 120, 140))
        screen.blit(ticket_s, (cx - ticket_s.get_width() // 2, start_y + 80))

        # Pull options
        options = [
            {"label": "1 抽", "sub": "100 金幣  或  1 張抽卡券", "id": "pull1", "cost": 100},
            {"label": "10 抽", "sub": "1000 金幣  或  10 張抽卡券", "id": "pull10", "cost": 1000},
        ]
        for i, opt in enumerate(options):
            fy = start_y + 120 + i * 100
            is_sel = (i == selected)
            can_afford = (player.gold >= opt["cost"] or
                          tickets >= (10 if i == 1 else 1))
            row_bg = (45, 35, 70) if is_sel else (28, 18, 48)
            pygame.draw.rect(screen, row_bg,
                             (px + 80, fy, panel_w - 160, 82), border_radius=10)
            border_c = (255, 200, 80) if is_sel else (80, 60, 120)
            pygame.draw.rect(screen, border_c,
                             (px + 80, fy, panel_w - 160, 82), 2, border_radius=10)
            if is_sel:
                pulse2 = int(160 + 95 * math.sin(t * 5))
                pygame.draw.rect(screen, (pulse2, pulse2, 50),
                                 (px + 80, fy, panel_w - 160, 82), 3, border_radius=10)

            lbl_s = get_font(30, bold=True).render(opt["label"], True,
                                                    (255, 220, 80) if can_afford else (120, 120, 120))
            screen.blit(lbl_s, (cx - lbl_s.get_width() // 2, fy + 8))
            sub_s = self.font_s.render(opt["sub"], True,
                                        (200, 200, 200) if can_afford else (90, 90, 90))
            screen.blit(sub_s, (cx - sub_s.get_width() // 2, fy + 50))

        # Rates info
        rates_y = start_y + 330
        rate_info = "橡膠 56%  火焰 20%  冰凍 16%  龍龍 4%  豹豹 4%"
        rate_s = self.font_s.render(rate_info, True, (150, 150, 170))
        screen.blit(rate_s, (cx - rate_s.get_width() // 2, rates_y))

        gold_s = self.font_s.render(f"目前金幣: {player.gold} G", True, YELLOW)
        screen.blit(gold_s, (px + 14, rates_y + 22))

    # ── Secret cheat menu (SAMLIN) ─────────────────────────────────────────────

    def draw_cheat_menu(self, screen, cheats: list, selected: int, used_counts: dict):
        _RARITY_COLORS = {
            "legendary": (255, 200, 50),
            "epic":      (200, 100, 255),
            "rare":      (80,  180, 255),
            "common":    (160, 160, 160),
        }
        _RARITY_STARS = {
            "legendary": "★★★",
            "epic":      "★★",
            "rare":      "★",
            "common":    "◆",
        }

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        screen.blit(overlay, (0, 0))

        row_h = 52
        panel_w = 700
        panel_h = 62 + len(cheats) * row_h + 44
        px = SCREEN_WIDTH // 2 - panel_w // 2
        py = SCREEN_HEIGHT // 2 - panel_h // 2

        pygame.draw.rect(screen, (10, 6, 22), (px, py, panel_w, panel_h), border_radius=16)
        # Animated golden border
        pulse_b = int(160 + 95 * math.sin(self._t * 2))
        pygame.draw.rect(screen, (pulse_b, pulse_b // 2, 0),
                         (px, py, panel_w, panel_h), 3, border_radius=16)

        title_font = get_font(28, bold=True)
        title_s = title_font.render("Sam 的密技選單", True, (255, 215, 0))
        screen.blit(title_s, (SCREEN_WIDTH // 2 - title_s.get_width() // 2, py + 14))

        t = self._t
        for i, cheat in enumerate(cheats):
            fy = py + 60 + i * row_h
            max_uses = cheat.get("max_uses_per_session", 3)
            used = used_counts.get(cheat["code"], 0)
            exhausted = used >= max_uses
            is_sel = (i == selected)
            rarity = cheat.get("rarity", "common")
            rc = _RARITY_COLORS.get(rarity, (160, 160, 160))

            # Row background
            if exhausted:
                row_bg = (18, 12, 18)
            elif is_sel:
                row_bg = (38, 26, 64)
            else:
                row_bg = (24, 16, 42)
            pygame.draw.rect(screen, row_bg,
                             (px + 10, fy, panel_w - 20, row_h - 6), border_radius=8)

            # Row border
            if is_sel and not exhausted:
                p = int(130 + 125 * math.sin(t * 5))
                border_c = (min(255, rc[0] * p // 180),
                            min(255, rc[1] * p // 180),
                            min(255, rc[2] * p // 180))
                pygame.draw.rect(screen, border_c,
                                 (px + 10, fy, panel_w - 20, row_h - 6), 2, border_radius=8)
            else:
                dim = tuple(c // (4 if exhausted else 2) for c in rc)
                pygame.draw.rect(screen, dim,
                                 (px + 10, fy, panel_w - 20, row_h - 6), 1, border_radius=8)

            # Rarity orb
            orb_x = px + 36
            orb_y = fy + (row_h - 6) // 2
            orb_c = tuple(c // 3 for c in rc) if exhausted else rc
            pygame.draw.circle(screen, orb_c, (orb_x, orb_y), 13)
            pygame.draw.circle(screen, (255, 255, 255), (orb_x, orb_y), 13, 1)
            star_s = self.font_s.render(
                _RARITY_STARS.get(rarity, "◆"), True,
                (70, 70, 70) if exhausted else (255, 255, 255))
            screen.blit(star_s, (orb_x - star_s.get_width() // 2,
                                  orb_y - star_s.get_height() // 2))

            # Description text
            mid_y = fy + (row_h - 6) // 2
            desc_c = ((80, 80, 80) if exhausted
                      else ((255, 220, 100) if is_sel else (210, 210, 210)))
            desc_s = self.font_m.render(cheat["description"], True, desc_c)
            screen.blit(desc_s, (px + 60, mid_y - desc_s.get_height() // 2))

            # Uses remaining badge (right side)
            left = max_uses - used
            badge_text = "已用盡" if exhausted else f"剩 {left}/{max_uses} 次"
            badge_c = (100, 60, 60) if exhausted else (100, 210, 110)
            badge_s = self.font_s.render(badge_text, True, badge_c)
            badge_x = px + panel_w - badge_s.get_width() - 16
            screen.blit(badge_s, (badge_x, mid_y - badge_s.get_height() // 2))

            # Selection arrow
            if is_sel and not exhausted:
                ax = badge_x - 18
                pygame.draw.polygon(screen, (255, 220, 50), [
                    (ax - 7, orb_y - 7), (ax + 3, orb_y), (ax - 7, orb_y + 7),
                ])

        # Footer hint
        hint_y = py + 60 + len(cheats) * row_h + 10
        hint_s = self.font_s.render(
            "↑↓ 選擇   Enter / Space 啟用   ESC 關閉", True, (130, 130, 155))
        screen.blit(hint_s, (SCREEN_WIDTH // 2 - hint_s.get_width() // 2, hint_y))
