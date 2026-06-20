import pygame
from ui.button import Button
from core.constants import WHITE, YELLOW
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.font_helper import get_font

class PauseMenu:
    def __init__(self):
        self.font_title = get_font(48, bold=True)
        cx = SCREEN_WIDTH // 2
        self.btn_resume = Button(cx - 120, 290, 240, 50, "繼續遊戲", font_size=24)
        self.btn_save   = Button(cx - 120, 355, 240, 50, "儲存遊戲", font_size=24)
        self.btn_menu   = Button(cx - 120, 420, 240, 50, "回主選單",
                                  color=(80, 50, 50), hover_color=(120, 70, 70), font_size=24)

    def update(self, dt, events) -> str:
        mouse_pos = pygame.mouse.get_pos()
        for btn in [self.btn_resume, self.btn_save, self.btn_menu]:
            btn.update(mouse_pos)
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "resume"
            if self.btn_resume.is_clicked(event):
                return "resume"
            if self.btn_save.is_clicked(event):
                return "save"
            if self.btn_menu.is_clicked(event):
                return "menu"
        return ""

    def draw(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        panel_w, panel_h = 380, 320
        px = SCREEN_WIDTH // 2 - panel_w // 2
        py = SCREEN_HEIGHT // 2 - panel_h // 2 - 20
        pygame.draw.rect(screen, (20, 20, 40), (px, py, panel_w, panel_h),
                         border_radius=12)
        pygame.draw.rect(screen, (100, 120, 200), (px, py, panel_w, panel_h),
                         2, border_radius=12)
        title = self.font_title.render("暫停", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 30))
        for btn in [self.btn_resume, self.btn_save, self.btn_menu]:
            btn.draw(screen)
