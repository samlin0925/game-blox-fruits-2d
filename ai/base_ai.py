from core.constants import AIState

class BaseAI:
    def __init__(self, player_ref):
        self.player = player_ref
        self.state = AIState.PATROL
        self.state_timer = 0.0

    def update(self, dt: float, entity):
        raise NotImplementedError

    def distance_to_player(self, entity) -> float:
        from utils.math_utils import distance
        return distance(entity.center, self.player.center)

    def direction_to_player(self, entity):
        from utils.math_utils import normalize
        dx = self.player.x - entity.x
        dy = self.player.y - entity.y
        return normalize(dx, dy)
