from ai.base_ai import BaseAI
from core.constants import AIState

class ChaseAI(BaseAI):
    def __init__(self, player_ref):
        super().__init__(player_ref)

    def update(self, dt: float, entity):
        dist = self.distance_to_player(entity)
        if dist <= entity.attack_range:
            entity.vx = 0
            entity.vy = 0
            self.state = AIState.ATTACK
        else:
            self.state = AIState.CHASE
            ndx, ndy = self.direction_to_player(entity)
            entity.vx = ndx * entity.speed
            entity.vy = ndy * entity.speed
