import random
from ai.base_ai import BaseAI
from core.constants import AIState

class BossAI(BaseAI):
    def __init__(self, player_ref):
        super().__init__(player_ref)
        self.skill_check_timer = 0.0

    def update(self, dt: float, entity):
        dist = self.distance_to_player(entity)
        self.skill_check_timer -= dt

        if dist <= entity.radius + 20:
            entity.vx = 0
            entity.vy = 0
            self.state = AIState.ATTACK
        else:
            self.state = AIState.CHASE
            ndx, ndy = self.direction_to_player(entity)
            entity.vx = ndx * entity.speed
            entity.vy = ndy * entity.speed

        if self.skill_check_timer <= 0:
            self.skill_check_timer = 2.0
            available = entity.get_available_skills()
            if available and dist < 500:
                skill = random.choice([s for s in available
                                       if entity.can_use_skill(s)] or [None])
                if skill:
                    return skill
        return None
