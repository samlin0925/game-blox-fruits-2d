import pygame
from core.constants import WHITE, YELLOW
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.font_helper import get_font
from systems.gacha_system import get_all_fruits

class DialogBox:
    def __init__(self):
        self.font_l = get_font(36, bold=True)
        self.font_m = get_font(22)
        self.font_s = get_font(16)

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

    def draw_altar(self, screen, player) -> str:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        panel_w, panel_h = 700, 470
        px = SCREEN_WIDTH // 2 - panel_w // 2
        py = SCREEN_HEIGHT // 2 - panel_h // 2
        pygame.draw.rect(screen, (20, 15, 35), (px, py, panel_w, panel_h),
                         border_radius=12)
        pygame.draw.rect(screen, (200, 160, 0), (px, py, panel_w, panel_h),
                         3, border_radius=12)
        title = self.font_l.render("果實祭壇 - 選擇覺醒", True, YELLOW)
        screen.blit(title,
                    (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 18))
        fruits = get_all_fruits()
        row_h = 62
        for i, fruit in enumerate(fruits):
            fy = py + 82 + i * row_h
            frag_count = player.fruit_fragments.get(fruit["id"], 0)
            req = fruit["fragments_required"]
            can = frag_count >= req
            row_color = (30, 50, 30) if can else (30, 20, 30)
            pygame.draw.rect(screen, row_color,
                             (px + 12, fy, panel_w - 24, row_h - 6),
                             border_radius=6)
            border_c = tuple(fruit["color"]) if can else (60, 60, 60)
            pygame.draw.rect(screen, border_c,
                             (px + 12, fy, panel_w - 24, row_h - 6),
                             2, border_radius=6)
            pygame.draw.circle(screen, tuple(fruit["color"]),
                                (px + 42, fy + row_h // 2 - 3), 14)
            name_s = self.font_m.render(
                fruit["name"], True, tuple(fruit["color"]) if can else (120, 120, 120))
            screen.blit(name_s, (px + 68, fy + 6))
            rarity_s = self.font_s.render(
                f"[{fruit['rarity'].upper()}]", True, (160, 160, 160))
            screen.blit(rarity_s, (px + 68, fy + 30))
            frag_text = f"{frag_count}/{req} 碎片"
            frag_color = (100, 255, 100) if can else (200, 100, 100)
            frag_s = self.font_m.render(frag_text, True, frag_color)
            screen.blit(frag_s,
                        (px + panel_w - frag_s.get_width() - 130, fy + 16))
            if can:
                st_s = self.font_s.render("可覺醒", True, (100, 255, 100))
            else:
                st_s = self.font_s.render(f"還需 {req - frag_count} 片", True, (160, 160, 160))
            screen.blit(st_s,
                        (px + panel_w - st_s.get_width() - 24, fy + 16))
        close = self.font_s.render("按 T 或 ESC 關閉祭壇", True, (150, 150, 150))
        screen.blit(close,
                    (SCREEN_WIDTH // 2 - close.get_width() // 2, py + panel_h - 28))
        return ""
