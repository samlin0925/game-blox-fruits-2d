import pygame
import math
from entities.base_entity import BaseEntity
from core.constants import WHITE, YELLOW, RED, GREEN, DARK
from config import WORLD_WIDTH, WORLD_HEIGHT, PLAYER_BASE_SPEED
from ui.sprite_draw import draw_character

class Player(BaseEntity):
    SIZE = 22

    def __init__(self, x: float, y: float):
        super().__init__(x, y, Player.SIZE * 2, Player.SIZE * 2)
        self.level = 1
        self.experience = 0
        self.max_health = 150
        self.health = self.max_health
        self.base_attack = 12
        self.defense = 5
        self.crit_rate = 10
        self.gold = 0
        self.title = "新手冒險者"

        self.character_data = None   # set by GameStateManager after character select
        self.current_fruit = None
        self.fruit_fragments = {}
        self.invincible = False
        self.invincible_timer = 0.0
        self.invincible_flash = 0.0

        self.facing_x = 1.0
        self.facing_y = 0.0

        self.attack_cooldown = 0.0
        self.skill_cooldown = 0.0

        self.hurt_timer = 0.0
        self.freeze_timer = 0.0
        self.speed = PLAYER_BASE_SPEED
        self._draw_t = 0.0

        self._keys = None

    def get_attack(self) -> int:
        atk = self.base_attack
        if self.current_fruit:
            if self.current_fruit["id"] == "dragon":
                atk = int(atk * 1.5)
            elif self.current_fruit["id"] == "flame":
                atk = int(atk * 1.15)
        return atk

    def get_crit_rate(self) -> float:
        rate = self.crit_rate
        if self.current_fruit and self.current_fruit["id"] == "leopard":
            rate += 40
        return min(rate, 95)

    def handle_input(self, keys):
        self._keys = keys

    def update(self, dt: float):
        keys = self._keys
        if keys is None:
            return
        if self.freeze_timer > 0:
            self.freeze_timer -= dt
            self.vx = self.vy = 0
        else:
            dx = dy = 0
            if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1

            length = math.hypot(dx, dy)
            if length > 0:
                dx /= length
                dy /= length
                self.facing_x = dx
                self.facing_y = dy

            self.vx = dx * self.speed
            self.vy = dy * self.speed
        super().update(dt)
        self.clamp_to_world(WORLD_WIDTH, WORLD_HEIGHT)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.skill_cooldown > 0:
            self.skill_cooldown -= dt

        if self.invincible:
            self.invincible_timer -= dt
            self.invincible_flash += dt
            if self.invincible_timer <= 0:
                self.invincible = False

        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        self._draw_t += dt

    def freeze(self, duration: float):
        self.freeze_timer = max(self.freeze_timer, duration)
        self.hurt_timer = max(self.hurt_timer, duration)

    def take_damage(self, amount: int) -> int:
        if self.invincible:
            return 0
        damage = max(1, amount - self.defense // 2)
        self.health = max(0, self.health - damage)
        self.hurt_timer = 0.3
        if self.health <= 0:
            self.alive = False
        return damage

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def add_fragment(self, fruit_id: str, count: int = 1):
        self.fruit_fragments[fruit_id] = self.fruit_fragments.get(fruit_id, 0) + count

    def equip_fruit(self, fruit_data: dict):
        self.current_fruit = fruit_data

    def get_body_color(self) -> tuple:
        if self.character_data:
            return tuple(self.character_data["body_color"])
        if self.current_fruit:
            return tuple(self.current_fruit["character_color"])
        return (50, 120, 220)

    def apply_character(self, char_data: dict):
        """Apply character stats and store appearance data."""
        self.character_data = char_data
        b = char_data.get("stat_bonus", {})
        self.max_health  += b.get("max_health",  0)
        self.health       = self.max_health
        self.base_attack += b.get("base_attack", 0)
        self.defense     += b.get("defense",     0)
        self.crit_rate   += b.get("crit_rate",   0)
        self.speed       += b.get("speed",        0)
        self.title        = char_data.get("title", self.title)

    def draw(self, screen, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        r = Player.SIZE

        hurt  = self.hurt_timer > 0
        blink = self.invincible and int(self.invincible_flash * 8) % 2 == 0

        if self.character_data:
            draw_character(screen, sx, sy, self.character_data,
                           r=r, t=getattr(self, '_draw_t', 0.0),
                           hurt=hurt, blink=blink,
                           current_fruit=self.current_fruit)
        else:
            if not blink:
                color = (255, 80, 80) if hurt else self.get_body_color()
                pygame.draw.circle(screen, color, (sx, sy), r)
                pygame.draw.circle(screen, WHITE, (sx, sy), r, 2)
                if self.current_fruit:
                    pygame.draw.circle(screen, tuple(self.current_fruit["color"]),
                                       (sx, sy), r // 2)
            eye_ox = int(self.facing_x * 10)
            eye_oy = int(self.facing_y * 10)
            pygame.draw.circle(screen, (20, 20, 20), (sx + eye_ox, sy + eye_oy), 4)

        if self.invincible and not blink:
            pygame.draw.circle(screen, (100, 200, 255), (sx, sy), r + 4, 2)

        # 血條
        bar_w = 44
        bar_h = 6
        bx = sx - bar_w // 2
        by = sy - r - 30
        pygame.draw.rect(screen, (60, 0, 0), (bx, by, bar_w, bar_h))
        hp_w = int(bar_w * self.health / self.max_health)
        pygame.draw.rect(screen, (0, 200, 60), (bx, by, hp_w, bar_h))
        pygame.draw.rect(screen, WHITE, (bx, by, bar_w, bar_h), 1)
