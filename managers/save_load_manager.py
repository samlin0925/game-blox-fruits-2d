import json
import os
from config import SAVE_FILE

def save_game(player, kill_count: int, boss_index: int):
    data = {
        "level": player.level,
        "experience": player.experience,
        "health": player.health,
        "max_health": player.max_health,
        "base_attack": player.base_attack,
        "defense": player.defense,
        "crit_rate": player.crit_rate,
        "gold": player.gold,
        "title": player.title,
        "fruit_fragments": player.fruit_fragments,
        "current_fruit_id": player.current_fruit["id"] if player.current_fruit else None,
        "kill_count": kill_count,
        "boss_index": boss_index,
        "potions": getattr(player, "potions", 0),
        "gacha_tickets": getattr(player, "gacha_tickets", 0),
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_game(player) -> dict:
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        os.remove(SAVE_FILE)
        return None
    player.level = data.get("level", 1)
    player.experience = data.get("experience", 0)
    player.max_health = data.get("max_health", 150)
    player.health = data.get("health", player.max_health)
    player.base_attack = data.get("base_attack", 12)
    player.defense = data.get("defense", 5)
    player.crit_rate = data.get("crit_rate", 10)
    player.gold = data.get("gold", 0)
    player.title = data.get("title", "新手冒險者")
    player.fruit_fragments = data.get("fruit_fragments", {})
    player.potions = data.get("potions", 0)
    player.gacha_tickets = data.get("gacha_tickets", 0)
    fid = data.get("current_fruit_id")
    if fid:
        from systems.gacha_system import get_fruit_by_id
        player.current_fruit = get_fruit_by_id(fid)
    return data

def delete_save():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
