"""
Clase CombatManager
Gestiona la lógica de combate
"""

import json
import random
from pathlib import Path
from .pet import Pet
from .battle_logger import BattleLogger

_logger = BattleLogger()

BASE_DIR = Path(__file__).parent.parent
RULES = json.load(open(BASE_DIR / "data" / "rules" / "ruleset.json"))


class CombatManager:

    def available_zones(self, pet: Pet) -> list:
        return [
            {"index": i, **{k: v for k, v in z.items() if k != "enemy"}}
            for i, z in enumerate(RULES["battle"]["zones"])
            if pet.state.stage >= z["min_stage"] and pet.state.level >= z["min_level"]
        ]

    def fight(self, pet: Pet, zone_index: int, minigame_won: bool) -> dict:
        zones = RULES["battle"]["zones"]

        if zone_index >= len(zones):
            return {"success": False, "message": "Zona no válida."}

        zone = zones[zone_index]
        if pet.state.stage < zone["min_stage"] or pet.state.level < zone["min_level"]:
            return {"success": False, "message": "No cumples los requisitos para esta zona."}

        enemy = zone["enemy"]

        # Probabilidad base según stats
        pet_power   = pet.state.strength + pet.state.speed + pet.state.combat_hp
        enemy_power = enemy["strength"]  + enemy["speed"]  + enemy["combat_hp"]
        total = pet_power + enemy_power
        base_chance = (pet_power / total) if total > 0 else 0.5
        base_chance = max(0.2, min(0.8, base_chance))

        # El minijuego añade un bonus de probabilidad
        if minigame_won:
            base_chance = min(0.9, base_chance + 0.2)

        pet_won = random.random() < base_chance

        result = {
            "success":      True,
            "won":          pet_won,
            "enemy_sprite": enemy["sprite"],
            "enemy_name":   enemy["name"],
        }

        if pet_won:
            multiplier = RULES["battle"]["minigame_bonus"]["win" if minigame_won else "lose"]
            xp_gained  = int(zone["xp_reward"] * multiplier)
            pet.gain_xp(xp_gained)
            result["xp_gained"] = xp_gained
            result["message"]   = f"¡Victoria contra {enemy['name']}! +{xp_gained} XP."
        else:
            pet.take_damage(RULES["battle"]["hp_loss_on_defeat"])
            result["xp_gained"] = 0
            result["message"]   = (
                f"Derrota contra {enemy['name']}. "
                f"-{RULES['battle']['hp_loss_on_defeat']} HP."
            )

        _logger.log(
            pet_name  = pet.state.name,
            codepet   = pet.state.codepet,
            zone      = zone["name"],
            enemy     = enemy["name"],
            won       = pet_won,
            xp_gained = result["xp_gained"],
        )

        return result
