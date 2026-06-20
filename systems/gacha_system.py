import random
from utils.data_loader import load

def get_all_fruits() -> list:
    return load("fruits.json")["fruits"]

def get_fruit_by_id(fruit_id: str) -> dict:
    for f in get_all_fruits():
        if f["id"] == fruit_id:
            return f
    return None

def pull_gacha(count: int = 1) -> list:
    fruits = get_all_fruits()
    weights = [f["weight"] for f in fruits]
    results = random.choices(fruits, weights=weights, k=count)
    return results

def check_and_awaken(player) -> list:
    awakened = []
    fruits = get_all_fruits()
    for fruit in fruits:
        fid = fruit["id"]
        req = fruit["fragments_required"]
        if player.fruit_fragments.get(fid, 0) >= req:
            player.fruit_fragments[fid] -= req
            player.equip_fruit(fruit)
            awakened.append(fruit)
    return awakened

def awaken_single(player, fruit_id: str) -> bool:
    """Awaken one specific fruit by ID. Returns True if successful."""
    fruit = get_fruit_by_id(fruit_id)
    if not fruit:
        return False
    req = fruit["fragments_required"]
    if player.fruit_fragments.get(fruit_id, 0) >= req:
        player.fruit_fragments[fruit_id] -= req
        player.equip_fruit(fruit)
        return True
    return False
