import pygame
from core.constants import WHITE
from utils.font_helper import get_font

class Button:
    def __init__(self, x, y, width, height, text,
                 color=(60, 80, 120), hover_color=(80, 110, 160),
                 text_color=WHITE, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = get_font(font_size, bold=True)
        self._hovered = False

    def update(self, mouse_pos):
        self._hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        color = self.hover_color if self._hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)
        surf = self.font.render(self.text, True, self.text_color)
        x = self.rect.centerx - surf.get_width() // 2
        y = self.rect.centery - surf.get_height() // 2
        screen.blit(surf, (x, y))

    def is_clicked(self, event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and self.rect.collidepoint(event.pos))
