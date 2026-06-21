import random
import math
from entities.enemy import Enemy
from entities.boss import Boss
from entities.projectile import Projectile
from entities.item import DroppedItem
from ai.patrol_ai import PatrolAI
from ai.chase_ai import ChaseAI
from ai.boss_ai import BossAI
from utils.data_loader import load
from config import (WORLD_WIDTH, WORLD_HEIGHT, MAX_ENEMIES,
                    SPAWN_MARGIN, ENEMY_SPAWN_INTERVAL)

_ZONE_BOSS_THRESHOLD = 20   # kills needed per zone before boss spawns


class EntityManager:
    def __init__(self, player):
        self.player = player
        self.enemies = []
        self.bosses = []
        self.projectiles = []
        self.items = []
        self._spawn_timer = 0.0
        self._kill_count = 0
        self._zone_kill_count = 0   # resets after each boss dies
        self._boss_index = 0
        self._boss_active = False
        self._post_boss_timer = 0.0  # cooldown after boss death before next boss
        self._enemy_data = load("enemies.json")["enemies"]
        self._boss_data = load("bosses.json")["bosses"]
        self._zone = 1
        self._zone_changed = False  # True for one frame after boss dies

    # ── Properties ─────────────────────────────────────────────────────────────

    @property
    def kill_count(self):
        return self._kill_count

    @property
    def zone_kill_count(self):
        return self._zone_kill_count

    @property
    def boss_index(self):
        return self._boss_index

    @property
    def total_bosses(self):
        return len(self._boss_data)

    @property
    def post_boss_timer(self):
        return self._post_boss_timer

    @property
    def zone_changed(self) -> bool:
        v = self._zone_changed
        self._zone_changed = False
        return v

    def set_kill_count(self, v):
        self._kill_count = v
        self._zone_kill_count = min(v, _ZONE_BOSS_THRESHOLD - 1)

    def set_boss_index(self, v):
        self._boss_index = v
        self._zone = min(3, v + 1)

    # ── Main update ────────────────────────────────────────────────────────────

    def update(self, dt: float, particles, camera):
        # Post-boss transition: pause spawning, let player breathe
        if self._post_boss_timer > 0:
            self._post_boss_timer -= dt
            for item in list(self.items):
                item.update(dt)
            self.items = [i for i in self.items if i.alive]
            for p in list(self.projectiles):
                p.update(dt)
            self.projectiles = [p for p in self.projectiles if p.alive]
            return

        self._spawn_timer -= dt
        if self._spawn_timer <= 0:
            self._try_spawn_enemy()
            self._spawn_timer = ENEMY_SPAWN_INTERVAL

        for e in list(self.enemies):
            e.update(dt)
        self._separate_enemies()
        for b in list(self.bosses):
            skill = b.ai.update(dt, b) if b.ai else None
            if skill:
                self._boss_use_skill(b, skill, particles)
            b.update(dt)

        dead_enemies = [e for e in self.enemies if not e.alive]
        dead_bosses  = [b for b in self.bosses  if not b.alive]
        new_kills = len(dead_enemies) + len(dead_bosses)
        self._kill_count      += new_kills
        self._zone_kill_count += new_kills

        if dead_bosses:
            for b in dead_bosses:
                particles.emit_explosion(b.x, b.y, b.color, 50, 350)
                camera.shake(25, 1.5)
                # Grant EXP and gold directly — values defined in bosses.json
                self.player.experience += b.exp_reward
                self.player.gold += b.gold_reward
                frag = b.fragment_reward
                if frag:
                    from systems.gacha_system import get_fruit_by_id
                    fruit = get_fruit_by_id(frag["fruit_id"])
                    if fruit:
                        for _ in range(frag["count"]):
                            item = DroppedItem(
                                b.x + random.randint(-60, 60),
                                b.y + random.randint(-60, 60),
                                "fragment", 1, tuple(fruit["color"]), fruit["id"])
                            self.items.append(item)
            self._boss_active = False
            self._boss_index += 1
            self._zone = min(3, self._boss_index + 1)
            self._zone_kill_count = 0       # reset kill count for new zone
            self._post_boss_timer = 12.0    # 12 second transition cooldown
            self._zone_changed = True       # signal GSM to teleport player
            self.enemies.clear()            # clear zone enemies

        self.enemies = [e for e in self.enemies if e.alive]
        self.bosses  = [b for b in self.bosses  if b.alive]

        # Spawn next boss only after cooldown and enough zone kills
        if (not self._boss_active
                and self._post_boss_timer <= 0
                and self._boss_index < len(self._boss_data)
                and self._zone_kill_count >= _ZONE_BOSS_THRESHOLD):
            self._spawn_boss()

        for p in list(self.projectiles):
            p.update(dt)
        self.projectiles = [p for p in self.projectiles if p.alive]

        for item in list(self.items):
            item.update(dt)
        self.items = [i for i in self.items if i.alive]

    # ── Spawn helpers ──────────────────────────────────────────────────────────

    def _try_spawn_enemy(self):
        if len(self.enemies) >= MAX_ENEMIES:
            return
        zone = self._zone
        pool = [e for e in self._enemy_data if e.get("zone", 1) <= zone]
        if not pool:
            pool = self._enemy_data[:2]
        data = random.choice(pool)
        x, y = self._random_spawn_pos()
        enemy = Enemy(x, y, data)
        if data.get("ai_type") == "patrol":
            enemy.ai = PatrolAI(self.player, x, y)
        else:
            enemy.ai = ChaseAI(self.player)
        self.enemies.append(enemy)

    def _spawn_boss(self):
        if self._boss_index >= len(self._boss_data):
            return
        data = self._boss_data[self._boss_index]
        bx = self.player.x + random.choice([-600, 600])
        by = self.player.y + random.choice([-400, 400])
        bx = max(200, min(WORLD_WIDTH - 200, bx))
        by = max(200, min(WORLD_HEIGHT - 200, by))
        boss = Boss(bx, by, data)
        boss.ai = BossAI(self.player)
        self.bosses.append(boss)
        self._boss_active = True
        self.enemies.clear()

    def _boss_use_skill(self, boss, skill, particles):
        if not boss.can_use_skill(skill):
            return
        boss.use_skill(skill)
        color = tuple(skill.get("color", [255, 100, 0]))
        if skill.get("aoe_radius", 0) > 0:
            aoe_r = skill["aoe_radius"]
            dist_to_player = math.hypot(
                self.player.x - boss.x, self.player.y - boss.y)
            if dist_to_player < aoe_r:
                self.player.take_damage(
                    int(boss.attack * skill["damage_multiplier"]))
                # Only freeze the player if they're inside the AOE
                freeze = skill.get("freeze_duration", 0)
                if freeze:
                    self.player.freeze(freeze)
            particles.emit_boss_skill(boss.x, boss.y, color)
        else:
            dx = self.player.x - boss.x
            dy = self.player.y - boss.y
            proj = Projectile(boss.x, boss.y, dx, dy, 350,
                               int(boss.attack * skill["damage_multiplier"]),
                               color, owner="boss",
                               piercing=skill.get("piercing", False), size=14)
            self.projectiles.append(proj)

    def _separate_enemies(self):
        """Push overlapping enemies apart so they spread into a ring, not a pile."""
        entities = [e for e in self.enemies if e.alive]
        n = len(entities)
        for i in range(n):
            a = entities[i]
            for j in range(i + 1, n):
                b = entities[j]
                dx = a.x - b.x
                dy = a.y - b.y
                dist = math.hypot(dx, dy)
                min_dist = a.radius + b.radius + 4  # tiny gap between sprites
                if 0 < dist < min_dist:
                    # Push both apart equally
                    push = (min_dist - dist) * 0.5
                    nx, ny = dx / dist, dy / dist
                    a.x += nx * push
                    a.y += ny * push
                    b.x -= nx * push
                    b.y -= ny * push
                elif dist == 0:
                    # Exact overlap: push randomly
                    import random as _r
                    angle = _r.uniform(0, 6.283)
                    a.x += math.cos(angle) * min_dist * 0.5
                    a.y += math.sin(angle) * min_dist * 0.5

    def _random_spawn_pos(self):
        px, py = self.player.x, self.player.y
        for _ in range(20):
            side = random.randint(0, 3)
            if side == 0:
                x = random.uniform(0, WORLD_WIDTH)
                y = max(0, py - 450)
            elif side == 1:
                x = random.uniform(0, WORLD_WIDTH)
                y = min(WORLD_HEIGHT, py + 450)
            elif side == 2:
                x = max(0, px - 650)
                y = random.uniform(0, WORLD_HEIGHT)
            else:
                x = min(WORLD_WIDTH, px + 650)
                y = random.uniform(0, WORLD_HEIGHT)
            dist = math.hypot(x - px, y - py)
            if 300 < dist < 700:
                return x, y
        return random.uniform(200, WORLD_WIDTH - 200), random.uniform(200, WORLD_HEIGHT - 200)

    # ── Projectile firing ──────────────────────────────────────────────────────

    def fire_projectile(self, x, y, dx, dy, speed, damage, color,
                        aoe_radius=0, piercing=False, hit_count=1, size=8):
        if hit_count <= 1:
            proj = Projectile(x, y, dx, dy, speed, damage, color,
                               owner="player", aoe_radius=aoe_radius,
                               piercing=piercing, size=size)
            self.projectiles.append(proj)
        else:
            base_angle = math.atan2(dy, dx)
            spread = math.radians(15)
            for i in range(hit_count):
                offset = (i - hit_count / 2) * spread / max(1, hit_count - 1)
                angle = base_angle + offset
                ndx = math.cos(angle)
                ndy = math.sin(angle)
                proj = Projectile(x, y, ndx, ndy, speed, damage, color,
                                   owner="player", size=size)
                self.projectiles.append(proj)

    # ── Draw ───────────────────────────────────────────────────────────────────

    def draw(self, screen, camera):
        for item in self.items:
            item.draw(screen, camera)
        for e in self.enemies:
            e.draw(screen, camera)
        for b in self.bosses:
            b.draw(screen, camera)
        for p in self.projectiles:
            p.draw(screen, camera)
