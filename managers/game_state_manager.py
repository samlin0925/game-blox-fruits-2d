import pygame
import math
from core.constants import GameState, WHITE, YELLOW, RED
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT,
                    PLAYER_BASE_SPEED, PROJECTILE_BASE_SPEED, ALTAR_POS)
from entities.player import Player
from managers.camera_manager import CameraManager
from managers.entity_manager import EntityManager
from managers.inventory_manager import InventoryManager
from managers.collision_manager import CollisionManager
from managers.cheat_code_manager import CheatCodeManager
from managers.scene_manager import SceneManager
from managers.save_load_manager import save_game, load_game
from systems.experience_system import check_level_up, get_milestone
from systems.particle_system import ParticleSystem
from systems.audio_system import AudioSystem
from systems.gacha_system import pull_gacha, check_and_awaken
from ui.hud import HUD
from ui.floating_text import FloatingTextManager
from ui.menu_screen import MenuScreen
from ui.pause_menu import PauseMenu
from ui.dialog_box import DialogBox
from ui.character_select import CharacterSelectScreen
from ui.intro_cutscene import IntroCutscene
from ui.ending_cutscene import EndingCutscene
from utils.data_loader import load as load_data
import os
from config import SAVE_FILE

class GameStateManager:
    def __init__(self, screen):
        self.screen = screen
        self.state = GameState.MAIN_MENU

        self.menu = MenuScreen()
        self.menu.set_has_save(os.path.exists(SAVE_FILE))
        self.pause_menu = PauseMenu()
        self.dialog = DialogBox()
        self.char_select = CharacterSelectScreen()
        self.intro: IntroCutscene | None = None
        self.ending: EndingCutscene | None = None
        self.audio = AudioSystem()
        self.audio.play_music("bgm_menu")
        self._pending_load = False   # True = load save after char select

        self._playing_initialized = False
        self._level_up_banner_timer = 0.0
        self._level_up_level = 0
        self._level_up_milestone = None
        self._cheat_result_msg = ""
        self._cheat_result_timer = 0.0
        self._cheat_input = ""
        self._altar_open = False
        self._game_over_timer = 0.0

    def _init_playing(self, load=False, char_id: str = "luffy"):
        from_save = load   # rename to avoid shadowing the loader function
        cx, cy = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
        self.player = Player(cx, cy)

        # 載入並套用角色資料
        all_chars = load_data("characters.json")["characters"]
        char_data = next((c for c in all_chars if c["id"] == char_id), all_chars[0])
        self.player.apply_character(char_data)
        self._active_char_id = char_id
        self.camera = CameraManager()
        self.camera.x = cx - SCREEN_WIDTH / 2
        self.camera.y = cy - SCREEN_HEIGHT / 2
        self.particles = ParticleSystem()
        self.floating = FloatingTextManager()
        self.hud = HUD()
        self.entity_manager = EntityManager(self.player)
        self.inventory = InventoryManager(self.player)
        self.collision = CollisionManager(
            self.entity_manager, self.particles, self.floating, self.audio,
            None, self.camera)
        self.cheats = CheatCodeManager(
            self.player, self.inventory, self.entity_manager, self.camera)
        self.scene = SceneManager()
        self.audio.play_music("bgm_battle")

        if from_save:
            data = load_game(self.player)
            if data:
                self.entity_manager.set_kill_count(data.get("kill_count", 0))
                self.entity_manager.set_boss_index(data.get("boss_index", 0))

        self._playing_initialized = True
        self._level_up_banner_timer = 0.0
        self._altar_open = False
        self._cheat_input = ""

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "quit"

            if self.state == GameState.MAIN_MENU:
                pass
            elif self.state == GameState.PLAYING:
                self._handle_playing_event(event)
            elif self.state == GameState.PAUSED:
                pass
            elif self.state == GameState.CHEAT_INPUT:
                self._handle_cheat_event(event)
            elif self.state == GameState.GACHA_UI:
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_t, pygame.K_ESCAPE):
                    awakened = check_and_awaken(self.player)
                    if awakened:
                        for fruit in awakened:
                            self._cheat_result_msg = f"{fruit['name']} 覺醒！"
                            self._cheat_result_timer = 3.0
                            self.camera.shake(15, 1.0)
                            self.particles.emit_level_up(self.player.x, self.player.y)
                            self.audio.play("level_up")
                    self.state = GameState.PLAYING
                    self._altar_open = False
        return ""

    def _handle_playing_event(self, event):
        if event.type == pygame.KEYDOWN:
            k = event.key
            if k == pygame.K_ESCAPE:
                self.state = GameState.PAUSED
            elif k == pygame.K_BACKQUOTE or k == pygame.K_BACKSLASH:
                self.state = GameState.CHEAT_INPUT
                self._cheat_input = ""
            elif k == pygame.K_j:
                self._player_basic_attack()
            elif k == pygame.K_k:
                self._player_skill()
            elif k == pygame.K_t:
                if self.scene.is_near_altar(self.player.x, self.player.y):
                    self.state = GameState.GACHA_UI
                    self._altar_open = True

    def _handle_cheat_event(self, event):
        if event.type == pygame.KEYDOWN:
            k = event.key
            if k == pygame.K_RETURN:
                if self._cheat_input:
                    result = self.cheats.execute(self._cheat_input)
                    self._cheat_result_msg = result["message"]
                    self._cheat_result_timer = 3.0
                self.state = GameState.PLAYING
                self._cheat_input = ""
            elif k == pygame.K_ESCAPE:
                self.state = GameState.PLAYING
                self._cheat_input = ""
            elif k == pygame.K_BACKSPACE:
                self._cheat_input = self._cheat_input[:-1]
            else:
                char = event.unicode.upper()
                if char.isalnum() and len(self._cheat_input) < 20:
                    self._cheat_input += char

    def _player_basic_attack(self):
        if self.player.attack_cooldown > 0:
            return
        p = self.player
        base_dmg = p.get_attack()
        color = (180, 220, 255)
        self.entity_manager.fire_projectile(
            p.x, p.y, p.facing_x, p.facing_y,
            PROJECTILE_BASE_SPEED, base_dmg, color, size=7)
        self.player.attack_cooldown = 0.4
        self.audio.play("attack")

    def _player_skill(self):
        if not self.player.current_fruit:
            return
        skill = self.player.current_fruit["skill"]
        if self.player.skill_cooldown > 0:
            return
        p = self.player
        base_dmg = int(p.get_attack() * skill["damage_multiplier"])
        color = tuple(self.player.current_fruit["color"])
        speed = skill.get("projectile_speed", PROJECTILE_BASE_SPEED)
        aoe = skill.get("aoe_radius", 0)
        piercing = skill.get("piercing", False)
        hit_count = skill.get("hit_count", 1)
        cooldown = skill["cooldown"]
        if getattr(self, "_active_char_id", "") == "sanji":
            cooldown *= 0.75  # 香吉士被動：冷卻減少25%
        self.player.skill_cooldown = cooldown

        if aoe > 0 and speed == 0:
            self.camera.shake(12, 0.5)
            self.particles.emit_explosion(p.x, p.y, color, 25, 250)
            import math
            for enemy in list(self.entity_manager.enemies) + list(self.entity_manager.bosses):
                if not enemy.alive:
                    continue
                dist = math.hypot(enemy.x - p.x, enemy.y - p.y)
                if dist < aoe:
                    from systems.damage_system import calculate_damage
                    from core.constants import DamageType
                    dmg, dtype = calculate_damage(base_dmg, 1.0, p.get_crit_rate(), enemy.defense)
                    actual = enemy.take_damage(dmg)
                    tc = (255, 215, 0) if dtype == DamageType.CRITICAL else color
                    self.floating.add(enemy.x, enemy.y - 30,
                                      f"{'CRIT! ' if dtype == DamageType.CRITICAL else ''}{actual}", tc,
                                      big=(dtype == DamageType.CRITICAL))
                    # entity_manager.update() handles kill counting, boss drops, and list cleanup
            freeze = skill.get("freeze_duration", 0)
            if freeze:
                for enemy in self.entity_manager.enemies + self.entity_manager.bosses:
                    import math as m2
                    if m2.hypot(enemy.x - p.x, enemy.y - p.y) < aoe:
                        enemy.freeze(freeze)
        else:
            self.entity_manager.fire_projectile(
                p.x, p.y, p.facing_x, p.facing_y,
                speed, base_dmg, color,
                aoe_radius=aoe, piercing=piercing, hit_count=hit_count, size=12)

        self.audio.play("skill")
        self.camera.shake(8, 0.3)

    def update(self, dt: float):
        if self.state == GameState.MAIN_MENU:
            pass
        elif self.state == GameState.INTRO_CUTSCENE:
            pass   # handled in main.py
        elif self.state == GameState.ENDING_CUTSCENE:
            pass   # handled in main.py
        elif self.state == GameState.CHARACTER_SELECT:
            pass   # char_select.update() called from main.py
        elif self.state == GameState.PLAYING:
            self._update_playing(dt)
        elif self.state == GameState.PAUSED:
            pass
        elif self.state == GameState.GAME_OVER:
            self._game_over_timer += dt
        elif self.state == GameState.CHEAT_INPUT:
            if self._playing_initialized:
                self._update_playing_passive(dt)
        elif self.state == GameState.GACHA_UI:
            if self._playing_initialized:
                self._update_playing_passive(dt)

    def _update_playing(self, dt: float):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update(dt)

        if not self.player.alive:
            self.state = GameState.GAME_OVER
            self._game_over_timer = 0.0
            self.audio.stop_music()
            self.audio.play("game_over")
            return

        had_boss = bool(self.entity_manager.bosses)
        prev_boss_idx = self.entity_manager.boss_index
        self.entity_manager.update(dt, self.particles, self.camera)
        has_boss_now = bool(self.entity_manager.bosses)
        if not had_boss and has_boss_now:
            self.audio.play_music("bgm_boss")
            self.audio.play("boss")
        elif had_boss and not has_boss_now:
            new_idx = self.entity_manager.boss_index
            if new_idx > prev_boss_idx and new_idx >= self.entity_manager.total_bosses:
                # 全部大將擊敗 → 結局動畫
                self.audio.stop_music()
                self.ending = EndingCutscene(self.player)
                self.state = GameState.ENDING_CUTSCENE
                return
            self.audio.play_music("bgm_battle")
        self.collision.process(self.player)

        level_ups = check_level_up(self.player)
        for lv in level_ups:
            ms = get_milestone(lv)
            self._level_up_level = lv
            self._level_up_milestone = ms
            self._level_up_banner_timer = 2.5
            self.camera.shake(ms["camera_shake"]["intensity"] if ms else 8,
                              ms["camera_shake"]["duration"] if ms else 0.4)
            self.particles.emit_level_up(self.player.x, self.player.y)
            self.audio.play("level_up")
            self.floating.add(self.player.x, self.player.y - 60,
                              f"LEVEL UP! Lv.{lv}", (255, 215, 0), big=True)

        self._update_playing_passive(dt)

    def _update_playing_passive(self, dt: float):
        self.camera.follow(self.player.x, self.player.y, dt)
        self.camera.update(dt)
        self.particles.update(dt)
        self.floating.update(dt)
        self.scene.update(dt)
        self.hud.update(dt)
        if self._level_up_banner_timer > 0:
            self._level_up_banner_timer -= dt
        if self._cheat_result_timer > 0:
            self._cheat_result_timer -= dt

    def render(self):
        if self.state == GameState.MAIN_MENU:
            self.menu.draw(self.screen)
        elif self.state == GameState.INTRO_CUTSCENE:
            if self.intro:
                self.intro.draw(self.screen)
        elif self.state == GameState.ENDING_CUTSCENE:
            if self.ending:
                self.ending.draw(self.screen)
        elif self.state == GameState.CHARACTER_SELECT:
            self.char_select.draw(self.screen)
        elif self.state in (GameState.PLAYING, GameState.CHEAT_INPUT,
                             GameState.GACHA_UI):
            self._render_playing()
        elif self.state == GameState.PAUSED:
            self._render_playing()
            self.pause_menu.draw(self.screen)
        elif self.state == GameState.GAME_OVER:
            self._render_playing()
            self.dialog.draw_game_over(
                self.screen, self.player, self.entity_manager.kill_count)

    def _render_playing(self):
        self.scene.draw_world(self.screen, self.camera)
        self.entity_manager.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        self.particles.draw(self.screen, self.camera)
        self.floating.draw(self.screen, self.camera)
        near_altar = self.scene.is_near_altar(self.player.x, self.player.y)
        self.hud.draw(self.screen, self.player,
                      self.entity_manager.kill_count,
                      self.entity_manager.boss_index,
                      near_altar,
                      self.entity_manager.bosses)
        if self._level_up_banner_timer > 0:
            self.dialog.draw_level_up_banner(
                self.screen, self._level_up_level, self._level_up_milestone)
        if self._cheat_result_timer > 0:
            self.dialog.draw_cheat_result(
                self.screen, self._cheat_result_msg, self._cheat_result_timer)
        if self.state == GameState.CHEAT_INPUT:
            self._draw_cheat_input()
        if self.state == GameState.GACHA_UI:
            self.dialog.draw_altar(self.screen, self.player)

    def _draw_cheat_input(self):
        from utils.font_helper import get_font
        font = get_font(24)
        panel_w, panel_h = 500, 55
        px = SCREEN_WIDTH // 2 - panel_w // 2
        py = SCREEN_HEIGHT - 90
        pygame.draw.rect(self.screen, (0, 0, 0, 200),
                         (px, py, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(self.screen, (80, 200, 80),
                         (px, py, panel_w, panel_h), 2, border_radius=8)
        prompt = font.render(f"密技碼: {self._cheat_input}█", True, (80, 255, 80))
        self.screen.blit(prompt, (px + 12, py + 14))

    def handle_menu_result(self, result: str):
        if result == "new_game":
            self._pending_load = False
            self.intro = IntroCutscene()
            self.state = GameState.INTRO_CUTSCENE
        elif result == "load_game":
            self._pending_load = True
            self.state = GameState.CHARACTER_SELECT  # skip intro on load
        elif result == "quit":
            return "quit"
        return ""

    def handle_char_select_result(self, char_id: str):
        """Called when player confirms a character."""
        self._init_playing(load=self._pending_load, char_id=char_id)
        self.state = GameState.PLAYING

    def handle_pause_result(self, result: str):
        if result == "resume":
            self.state = GameState.PLAYING
        elif result == "save":
            save_game(self.player, self.entity_manager.kill_count,
                      self.entity_manager.boss_index)
            self._cheat_result_msg = "遊戲已儲存"
            self._cheat_result_timer = 2.0
            self.state = GameState.PLAYING
        elif result == "menu":
            self.state = GameState.MAIN_MENU
            self.menu.set_has_save(os.path.exists(SAVE_FILE))

    def handle_game_over_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._init_playing(load=False,
                                   char_id=getattr(self, "_active_char_id", "luffy"))
                self.state = GameState.PLAYING
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MAIN_MENU
