import pygame
from core.constants import WHITE, YELLOW, RED
from systems.experience_system import exp_required
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.font_helper import get_font

class HUD:
    def __init__(self):
        self.font_l  = get_font(28, bold=True)
        self.font_m  = get_font(20, bold=True)
        self.font_s  = get_font(15)
        self._hint_timer = 0.0

    def update(self, dt: float):
        self._hint_timer += dt

    def draw(self, screen, player, kill_count: int, boss_index: int,
             near_altar: bool, boss_list: list):
        self._draw_hp_bar(screen, player)
        self._draw_exp_bar(screen, player)
        self._draw_gold(screen, player)
        self._draw_fruit_info(screen, player)
        self._draw_kill_counter(screen, kill_count, boss_index)
        self._draw_controls_hint(screen)
        if near_altar:
            self._draw_altar_hint(screen, player)
        if boss_list:
            self._draw_boss_bar(screen, boss_list[0])

    def _draw_hp_bar(self, screen, player):
        bw, bh = 220, 18
        bx, by = 12, 12
        pygame.draw.rect(screen, (60, 0, 0), (bx, by, bw, bh), border_radius=4)
        hp_w = int(bw * player.health / player.max_health)
        hp_color = ((0, 200, 80) if player.health > player.max_health * 0.5
                    else (220, 150, 0) if player.health > player.max_health * 0.25
                    else (220, 40, 40))
        pygame.draw.rect(screen, hp_color, (bx, by, hp_w, bh), border_radius=4)
        pygame.draw.rect(screen, WHITE, (bx, by, bw, bh), 2, border_radius=4)
        label = self.font_s.render(f"HP {player.health}/{player.max_health}", True, WHITE)
        screen.blit(label, (bx + 6, by + 2))
        lv_surf = self.font_m.render(f"Lv.{player.level}", True, YELLOW)
        screen.blit(lv_surf, (bx + bw + 8, by))

    def _draw_exp_bar(self, screen, player):
        bw, bh = 220, 10
        bx, by = 12, 36
        needed = exp_required(player.level)
        pygame.draw.rect(screen, (30, 30, 60), (bx, by, bw, bh), border_radius=3)
        exp_w = int(bw * min(1.0, player.experience / max(1, needed)))
        pygame.draw.rect(screen, (80, 120, 220), (bx, by, exp_w, bh), border_radius=3)
        pygame.draw.rect(screen, (100, 140, 255), (bx, by, bw, bh), 1, border_radius=3)
        exp_label = self.font_s.render(f"EXP {player.experience}/{needed}",
                                        True, (150, 180, 255))
        screen.blit(exp_label, (bx + 4, by - 1))

    def _draw_gold(self, screen, player):
        surf = self.font_m.render(f"G {player.gold}", True, YELLOW)
        screen.blit(surf, (SCREEN_WIDTH - surf.get_width() - 12, 12))

    def _draw_fruit_info(self, screen, player):
        x = SCREEN_WIDTH - 190
        y = 40
        if player.current_fruit:
            f = player.current_fruit
            pygame.draw.rect(screen, (30, 20, 50),
                             (x - 4, y - 4, 188, 72), border_radius=6)
            pygame.draw.rect(screen, tuple(f["color"]),
                             (x - 4, y - 4, 188, 72), 2, border_radius=6)
            name_surf = self.font_s.render(f["name"], True, tuple(f["color"]))
            screen.blit(name_surf, (x, y))
            cd = player.skill_cooldown
            cd_text = (f"技能 冷卻{cd:.1f}s" if cd > 0 else "[K] 技能就緒")
            cd_surf = self.font_s.render(cd_text, True,
                                          (150, 150, 255) if cd > 0 else (100, 255, 100))
            screen.blit(cd_surf, (x, y + 20))
            pass_surf = self.font_s.render(f["passive"], True, (200, 200, 200))
            screen.blit(pass_surf, (x, y + 40))
        else:
            surf = self.font_s.render("無果實 (前往祭壇覺醒)", True, (160, 160, 160))
            screen.blit(surf, (x - 50, y))

    def _draw_kill_counter(self, screen, kill_count: int, boss_index: int):
        from config import BOSS_KILL_THRESHOLD
        idx = min(boss_index, len(BOSS_KILL_THRESHOLD) - 1)
        next_boss = BOSS_KILL_THRESHOLD[idx]
        surf = self.font_s.render(
            f"擊殺: {kill_count} / {next_boss} -> Boss", True, (220, 180, 100))
        screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, 8))

    def _draw_controls_hint(self, screen):
        if int(self._hint_timer) % 10 < 7:
            hints = "WASD 移動  J 攻擊  K 技能  T 祭壇  ~ 密技  ESC 暫停"
            surf = self.font_s.render(hints, True, (120, 120, 120))
            screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2,
                                SCREEN_HEIGHT - 22))

    def _draw_altar_hint(self, screen, player):
        total = sum(player.fruit_fragments.values())
        text = f"[T] 開啟果實祭壇  (碎片: {total})"
        surf = self.font_m.render(text, True, YELLOW)
        bx = SCREEN_WIDTH // 2 - surf.get_width() // 2 - 10
        by = SCREEN_HEIGHT - 80
        overlay = pygame.Surface((surf.get_width() + 20, 36), pygame.SRCALPHA)
        overlay.fill((30, 25, 0, 200))
        screen.blit(overlay, (bx - 8, by - 6))
        screen.blit(surf, (bx, by))

    def _draw_boss_bar(self, screen, boss):
        bw = SCREEN_WIDTH - 200
        bh = 22
        bx = 100
        by = SCREEN_HEIGHT - 55
        pygame.draw.rect(screen, (40, 0, 0), (bx, by, bw, bh), border_radius=4)
        hp_w = int(bw * boss.health / boss.max_health)
        phase_color = (220, 50, 50) if boss.phase == 1 else (255, 120, 0)
        pygame.draw.rect(screen, phase_color, (bx, by, hp_w, bh), border_radius=4)
        pygame.draw.rect(screen, YELLOW, (bx, by, bw, bh), 2, border_radius=4)
        label = self.font_m.render(
            f"{boss.name} [{boss.title}]  {boss.health}/{boss.max_health}",
            True, WHITE)
        screen.blit(label, (bx + 8, by + 2))
        if boss.phase == 2:
            ph_surf = self.font_s.render("!! PHASE 2", True, (255, 150, 0))
            screen.blit(ph_surf, (bx + bw - ph_surf.get_width() - 8, by + 4))
