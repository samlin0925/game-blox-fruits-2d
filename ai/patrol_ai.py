import random
import math
from ai.base_ai import BaseAI
from core.constants import AIState

class PatrolAI(BaseAI):
    def __init__(self, player_ref, home_x: float, home_y: float):
        super().__init__(player_ref)
        self.home_x = home_x
        self.home_y = home_y
        self.target_x = home_x
        self.target_y = home_y
        self.patrol_radius = 150
        self._pick_new_target()

    def _pick_new_target(self):
        angle = random.uniform(0, math.pi * 2)
        r = random.uniform(30, self.patrol_radius)
        self.target_x = self.home_x + math.cos(angle) * r
        self.target_y = self.home_y + math.sin(angle) * r
        self.state_timer = random.uniform(3, 6)

    def update(self, dt: float, entity):
        dist = self.distance_to_player(entity)
        if dist < entity.detect_range:
            self.state = AIState.CHASE
        else:
            self.state = AIState.PATROL

        if self.state == AIState.PATROL:
            dx = self.target_x - entity.x
            dy = self.target_y - entity.y
            d = math.hypot(dx, dy)
            if d < 10 or self.state_timer <= 0:
                self._pick_new_target()
            else:
                entity.vx = (dx / d) * entity.speed * 0.5
                entity.vy = (dy / d) * entity.speed * 0.5
                self.state_timer -= dt
        else:
            ndx, ndy = self.direction_to_player(entity)
            entity.vx = ndx * entity.speed
            entity.vy = ndy * entity.speed
