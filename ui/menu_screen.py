import pygame
import math
from core.constants import WHITE, YELLOW
from ui.button import Button
from ui.background_scene import BackgroundScene
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.font_helper import get_font

class MenuScreen:
    def __init__(self):
        self.font_title = get_font(64, bold=True)
        self.font_sub   = get_font(22)
        self.font_s     = get_font(16)
        cx = SCREEN_WIDTH // 2
        self.btn_new  = Button(cx - 130, 330, 260, 55, "新遊戲", font_size=26)
        self.btn_load = Button(cx - 130, 400, 260, 55, "繼續遊戲", font_size=26)
        self.btn_quit = Button(cx - 130, 470, 260, 55, "離開",
                               color=(100, 40, 40), hover_color=(140, 60, 60), font_size=26)
        self._timer = 0.0
        self._has_save = False
        self._bg = BackgroundScene(SCREEN_WIDTH, SCREEN_HEIGHT)
        self._focused = 0  # 0=新遊戲, 1=繼續, 2=離開

    def set_has_save(self, v: bool):
        self._has_save = v

    def update(self, dt: float, events) -> str:
        self._timer += dt
        self._bg.update(dt)
        mouse_pos = pygame.mouse.get_pos()
        for btn in [self.btn_new, self.btn_load, self.btn_quit]:
            btn.update(mouse_pos)
        num_items = 3 if self._has_save else 2  # 1=新遊戲, [2=繼續], 3=離開
        for event in events:
            if event.type == pygame.KEYDOWN:
                k = event.key
                if k in (pygame.K_UP, pygame.K_w):
                    self._focused = (self._focused - 1) % num_items
                elif k in (pygame.K_DOWN, pygame.K_s):
                    self._focused = (self._focused + 1) % num_items
                elif k in (pygame.K_RETURN, pygame.K_SPACE):
                    if self._focused == 0:
                        return "new_game"
                    elif self._focused == 1 and self._has_save:
                        return "load_game"
                    elif self._focused == (num_items - 1):
                        return "quit"
            if self.btn_new.is_clicked(event):
                return "new_game"
            if self.btn_load.is_clicked(event) and self._has_save:
                return "load_game"
            if self.btn_quit.is_clicked(event):
                return "quit"
        return ""

    def draw(self, screen):
        self._bg.draw(screen)
        # 輕薄半透明遮罩（避免陰暗感）
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 55))
        screen.blit(overlay, (0, 0))
        t = self._timer
        pulse = abs(math.sin(t * 1.5)) * 0.3 + 0.7

        # 標題光暈
        title_color = (int(255 * pulse), int(215 * pulse), 30)
        glow_surf = self.font_title.render("惡魔果實 2D", True,
                                            (80, 60, 0))
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            screen.blit(glow_surf,
                        (SCREEN_WIDTH // 2 - glow_surf.get_width() // 2 + dx,
                         160 + dy))
        title_surf = self.font_title.render("惡魔果實 2D", True, title_color)
        screen.blit(title_surf,
                    (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 160))

        sub_surf = self.font_sub.render(
            "Blox Fruits 2D  |  快節奏爽快冒險", True, (200, 200, 230))
        screen.blit(sub_surf,
                    (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, 250))
        self.btn_new.draw(screen)
        if self._has_save:
            self.btn_load.draw(screen)
        else:
            dim = Button(self.btn_load.rect.x, self.btn_load.rect.y,
                         self.btn_load.rect.width, self.btn_load.rect.height,
                         "繼續遊戲 (無存檔)",
                         color=(50, 50, 50), hover_color=(50, 50, 50), font_size=22)
            dim.draw(screen)
        self.btn_quit.draw(screen)
        # 方向鍵焦點指示
        focus_btns = [self.btn_new]
        if self._has_save:
            focus_btns.append(self.btn_load)
        focus_btns.append(self.btn_quit)
        if self._focused < len(focus_btns):
            fb = focus_btns[self._focused]
            p2 = abs(math.sin(t * 4)) * 0.5 + 0.5
            arrow_x = fb.rect.left - 24
            arrow_y = fb.rect.centery
            arrow_c = (int(255 * p2), int(200 * p2), 0)
            pygame.draw.polygon(screen, arrow_c, [
                (arrow_x, arrow_y - 8),
                (arrow_x + 16, arrow_y),
                (arrow_x, arrow_y + 8),
            ])
        tips = [
            "WASD 移動  |  J 攻擊  |  K 果實技能  |  H 喝藥水",
            "~ 密技碼  |  T 祭壇（覺醒/商店/抽卡）  |  ESC 暫停",
            "消滅敵人獲得碎片 → 祭壇覺醒果實 → 解鎖強力技能！",
        ]
        for i, tip in enumerate(tips):
            surf = self.font_s.render(tip, True, (160, 160, 200))
            screen.blit(surf,
                        (SCREEN_WIDTH // 2 - surf.get_width() // 2, 555 + i * 22))

        # 版本與作者
        from config import VERSION
        ver = self.font_s.render(f"{VERSION}  |  2026  |  Sam Lin", True, (120, 120, 150))
        screen.blit(ver, (SCREEN_WIDTH // 2 - ver.get_width() // 2, SCREEN_HEIGHT - 40))

        # 作者與測試人員名單
        credits = self.font_s.render(
            "作者：Sam Lin  |  測試：Beta Testers", True, (100, 130, 180))
        screen.blit(credits,
                    (SCREEN_WIDTH // 2 - credits.get_width() // 2, SCREEN_HEIGHT - 22))
