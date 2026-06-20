from systems.gacha_system import get_fruit_by_id

class InventoryManager:
    def __init__(self, player):
        self.player = player

    def add_gold(self, amount: int):
        self.player.gold += amount

    def add_experience(self, amount: int):
        self.player.experience += amount

    def add_fragment(self, fruit_id: str, count: int = 1):
        self.player.add_fragment(fruit_id, count)

    def equip_fruit_by_id(self, fruit_id: str) -> bool:
        fruit = get_fruit_by_id(fruit_id)
        if fruit:
            self.player.equip_fruit(fruit)
            return True
        return False

    def get_fragment_summary(self) -> dict:
        return dict(self.player.fruit_fragments)

    def can_awaken(self, fruit_id: str) -> bool:
        from systems.gacha_system import get_fruit_by_id
        fruit = get_fruit_by_id(fruit_id)
        if not fruit:
            return False
        req = fruit["fragments_required"]
        return self.player.fruit_fragments.get(fruit_id, 0) >= req
