import math
from utils.data_loader import load

def exp_required(level: int) -> int:
    base = 100
    return int(base * (level ** 1.5))

def check_level_up(player) -> list:
    level_ups = []
    while True:
        needed = exp_required(player.level)
        if player.experience >= needed and player.level < 99:
            player.experience -= needed
            player.level += 1
            _apply_stat_gain(player)
            level_ups.append(player.level)
            _check_milestone(player)
        else:
            break
    return level_ups

def _apply_stat_gain(player):
    data = load("levels.json")
    gains = data["stat_per_level"]
    player.base_attack += gains["attack"]
    player.defense += gains["defense"]
    player.max_health += gains["health"]
    player.health = player.max_health  # restore to full HP on level up

def _check_milestone(player):
    data = load("levels.json")
    for ms in data["milestones"]:
        if ms["level"] == player.level:
            player.experience += ms.get("reward_exp", 0)
            player.gold += ms.get("reward_gold", 0)
            player.title = ms.get("reward_title", player.title)
            tickets = ms.get("free_gacha", 0)
            if tickets > 0:
                player.gacha_tickets = getattr(player, "gacha_tickets", 0) + tickets
            return ms
    return None

def get_milestone(level: int):
    data = load("levels.json")
    for ms in data["milestones"]:
        if ms["level"] == level:
            return ms
    return None
