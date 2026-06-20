from utils.data_loader import load

class CheatCodeManager:
    def __init__(self, player, inventory, entity_manager, camera):
        self.player = player
        self.inventory = inventory
        self.entity_manager = entity_manager
        self.camera = camera
        self.used_codes = {}
        self._load()

    def _load(self):
        data = load("cheat_codes.json")
        self.cheat_data = {
            c["code"]: c for c in data["codes"] if c.get("active", True)
        }

    def execute(self, code: str) -> dict:
        code = code.upper().strip()
        if code not in self.cheat_data:
            return {"success": False, "message": "無效的密技碼"}

        cd = self.cheat_data[code]
        max_uses = cd.get("max_uses_per_session", 3)
        used = self.used_codes.get(code, 0)
        if used >= max_uses:
            return {"success": False, "message": f"已達使用上限 ({max_uses}次)"}

        effect = cd["effect"]
        msg = cd["description"]

        if effect == "invincibility":
            self.player.invincible = True
            self.player.invincible_timer = cd.get("duration", 30)
        elif effect == "add_currency":
            self.inventory.add_gold(cd["amount"])
        elif effect == "free_gacha":
            from systems.gacha_system import pull_gacha
            results = pull_gacha(cd["count"])
            for fruit in results:
                self.inventory.add_fragment(fruit["id"], 1)
            msg = f"抽到: {', '.join(f['name'] for f in results[:3])}..."
        elif effect == "gain_experience":
            self.inventory.add_experience(cd["amount"])
        elif effect == "unlock_all_fruits":
            from systems.gacha_system import get_all_fruits
            for fruit in get_all_fruits():
                self.inventory.add_fragment(fruit["id"], fruit["fragments_required"])
        elif effect == "set_level":
            target_level = cd.get("level", 50)
            from systems.experience_system import exp_required, _apply_stat_gain
            while self.player.level < target_level:
                self.player.level += 1
                _apply_stat_gain(self.player)
        elif effect == "kill_all_enemies":
            for e in list(self.entity_manager.enemies):
                e.alive = False
            for b in list(self.entity_manager.bosses):
                b.alive = False

        self.used_codes[code] = used + 1
        self.camera.shake(15, 0.5)
        return {"success": True, "message": f"成功: {msg}"}

    def reset_session(self):
        self.used_codes = {}
