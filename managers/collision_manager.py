import math
from systems.damage_system import calculate_damage
from entities.item import DroppedItem
import random

class CollisionManager:
    def __init__(self, entity_manager, particle_system, floating_text, audio,
                 experience_system, camera):
        self.em = entity_manager
        self.particles = particle_system
        self.floating = floating_text
        self.audio = audio
        self.exp_sys = experience_system
        self.camera = camera

    def _circle_overlap(self, ax, ay, ar, bx, by, br) -> bool:
        return math.hypot(ax - bx, ay - by) < ar + br

    def process(self, player):
        self._player_vs_enemies(player)
        self._projectiles_vs_enemies(player)
        self._projectiles_vs_player(player)
        self._player_vs_items(player)

    def _char_id(self, player):
        cd = getattr(player, "character_data", None)
        return cd["id"] if cd else ""

    def _player_vs_enemies(self, player):
        import random as _rnd
        cid = self._char_id(player)
        for enemy in list(self.em.enemies) + list(self.em.bosses):
            if not enemy.alive:
                continue
            dist = math.hypot(player.x - enemy.x, player.y - enemy.y)
            if dist < (player.width // 2 + enemy.radius) and enemy.can_attack():
                # 路飛被動：30% 免傷
                if cid == "luffy" and _rnd.random() < 0.30:
                    self.floating.add(player.x, player.y - 30, "橡皮免傷!", (255, 160, 60))
                    enemy.reset_attack_cooldown()
                    continue
                dmg = max(1, enemy.attack - player.defense // 3)
                actual = player.take_damage(dmg)
                if actual > 0:
                    self.floating.add(player.x, player.y - 30,
                                      f"-{actual}", (255, 80, 80))
                    self.particles.emit_hit(player.x, player.y, (255, 80, 80))
                    self.audio.play("hit")
                enemy.reset_attack_cooldown()

    def _projectiles_vs_enemies(self, player):
        for proj in list(self.em.projectiles):
            if not proj.alive or proj.owner != "player":
                continue
            targets = list(self.em.enemies) + list(self.em.bosses)
            for enemy in targets:
                if not enemy.alive:
                    continue
                eid = id(enemy)
                if eid in proj.hit_targets:
                    continue
                dist = math.hypot(proj.x - enemy.x, proj.y - enemy.y)
                hit_radius = enemy.radius + proj.radius
                if proj.aoe_radius > 0:
                    if dist < proj.aoe_radius:
                        self._deal_proj_damage(proj, enemy, player)
                        proj.hit_targets.add(eid)
                        if not proj.piercing:
                            proj.alive = False
                else:
                    if dist < hit_radius:
                        self._deal_proj_damage(proj, enemy, player)
                        proj.hit_targets.add(eid)
                        if not proj.piercing:
                            proj.alive = False

    def _deal_proj_damage(self, proj, enemy, player):
        cid = self._char_id(player)
        # 羅被動：技能投射物無視防禦
        eff_defense = 0 if (cid == "law" and proj.owner == "player") else enemy.defense
        dmg, dtype = calculate_damage(
            proj.damage, 1.0, player.get_crit_rate(), eff_defense)
        actual = enemy.take_damage(dmg)
        from core.constants import DamageType
        if dtype == DamageType.CRITICAL:
            # 索隆被動：暴擊傷害 +50%
            if cid == "zoro":
                extra = actual // 2
                actual = enemy.take_damage(extra)  # extra hit
                text = f"三刀流! {actual + extra}"
                actual = actual + extra
            else:
                text = f"CRIT! {actual}"
            color = (255, 215, 0)
            self.camera.shake(5, 0.15)
            self.audio.play("crit")
        else:
            color = (255, 255, 255)
            text = str(actual)
            self.audio.play("attack")
        self.floating.add(enemy.x, enemy.y - enemy.radius - 10, text, color,
                          big=(dtype == DamageType.CRITICAL))
        self.particles.emit_hit(enemy.x, enemy.y, proj.color)
        if not enemy.alive:
            self._on_enemy_death(enemy, player)

    def _on_enemy_death(self, enemy, player):
        player.experience += enemy.exp_reward
        # 娜美被動：雙倍金幣
        cid = self._char_id(player)
        gold = enemy.gold_reward * (2 if cid == "nami" else 1)
        player.gold += gold
        gold_label = f"+{gold} G" + (" x2!" if cid == "nami" else "")
        self.floating.add(enemy.x, enemy.y - 40,
                          f"+{enemy.exp_reward} EXP", (100, 220, 100))
        self.floating.add(enemy.x, enemy.y - 60, gold_label, (255, 215, 0))
        self.particles.emit_explosion(enemy.x, enemy.y, enemy.color)
        self.audio.play("explosion")
        # Health drop (15% chance, heals 30–50 HP)
        if random.random() < 0.15:
            heal_val = random.randint(30, 50)
            item = DroppedItem(enemy.x, enemy.y + 20, "health", heal_val, (230, 50, 60))
            self.em.items.append(item)

        if hasattr(enemy, "fragment_drop_chance") and random.random() < enemy.fragment_drop_chance:
            from systems.gacha_system import get_all_fruits
            import random as rnd
            fruits = get_all_fruits()
            weights = [f["weight"] for f in fruits]
            fruit = rnd.choices(fruits, weights=weights, k=1)[0]
            item = DroppedItem(enemy.x, enemy.y, "fragment", 1,
                               tuple(fruit["color"]), fruit["id"])
            self.em.items.append(item)

    def _projectiles_vs_player(self, player):
        for proj in list(self.em.projectiles):
            if not proj.alive or proj.owner == "player":
                continue
            dist = math.hypot(proj.x - player.x, proj.y - player.y)
            if dist < player.width // 2 + proj.radius:
                actual = player.take_damage(proj.damage)
                if actual > 0:
                    self.floating.add(player.x, player.y - 30,
                                      f"-{actual}", (255, 80, 80))
                    self.particles.emit_hit(player.x, player.y, (255, 80, 80))
                proj.alive = False

    def _player_vs_items(self, player):
        for item in list(self.em.items):
            if not item.alive:
                continue
            dist = math.hypot(player.x - item.x, player.y - item.y)
            if dist < player.width // 2 + 12:
                if item.item_type == "fragment" and item.fruit_id:
                    player.add_fragment(item.fruit_id, 1)
                    self.floating.add(item.x, item.y - 20,
                                      "碎片 +1", (180, 120, 220))
                elif item.item_type == "gold":
                    player.gold += item.value
                elif item.item_type == "health":
                    player.heal(item.value)
                self.audio.play("item")
                item.alive = False
