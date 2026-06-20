import random
from core.constants import DamageType

def calculate_damage(attacker_atk: int, damage_multiplier: float,
                     crit_rate: float, defender_def: int = 0) -> tuple:
    base = attacker_atk * damage_multiplier
    is_crit = random.random() * 100 < crit_rate
    if is_crit:
        base *= 1.75
    final = max(1, int(base) - defender_def // 2)
    dtype = DamageType.CRITICAL if is_crit else DamageType.NORMAL
    return final, dtype
