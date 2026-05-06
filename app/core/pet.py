"""
Clase Pet
"""

from .state import PetState
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
with open(BASE_DIR / "data" / "rules" / "ruleset.json") as f:
    RULES = json.load(f)

class Pet:
    def __init__(self, state: PetState = None):
        self.state = state if state else PetState()

    # --- MÉTODOS DE CUIDADO Y ENTRENAMIENTO ---

    def feed(self):
        max_hunger = RULES["stats"]["max_hunger"]
        self.state.hunger = min(self.state.hunger + 1, max_hunger)

    def train(self, stat_type: str, won_minigame: bool):
        if self.state.stage == 1:
            return {"success": False, "message": "Punchy no puede entrenar."}

        energy_cost = RULES["training"]["energy_cost"]

        if self.state.energy < energy_cost:
            return {"success": False, "message": "Sin energía suficiente."}

        self.state.energy -= energy_cost

        if not won_minigame:
            return {"success": True, "message": "Minijuego perdido, sin ganancia."}

        pet_rules = RULES["stats"]["by_pet_type"].get(self.state.codepet)
        if not pet_rules:
            return {"success": False, "message": "Error leyendo datos de la mascota."}

        current_level = self.state.level - 1

        match stat_type:
            case "strength":
                max_val = pet_rules["max_strength_by_level"][current_level]
                gain = RULES["training"]["strength_gain"]
                self.state.strength = min(self.state.strength + gain, max_val)
            case "speed":
                max_val = pet_rules["max_speed_by_level"][current_level]
                gain = RULES["training"]["speed_gain"]
                self.state.speed = min(self.state.speed + gain, max_val)
            case "hp":
                max_val = pet_rules["max_combat_hp_by_level"][current_level]
                gain = RULES["training"].get("combat_hp_gain", 5)
                self.state.combat_hp = min(self.state.combat_hp + gain, max_val)

        return {"success": True}

    # --- PROGRESIÓN Y EVOLUCIÓN ---

    def gain_xp(self, amount: int):
        current_stage = self.state.stage - 1
        stage_max_level = RULES["progression"]["max_level_by_stage"][current_stage]

        if self.state.level >= stage_max_level:
            return

        self.state.xp += amount
        xp_levels = RULES["progression"]["xp_required_by_level"]

        while self.state.level < stage_max_level:
            next_level = self.state.level
            if next_level >= len(xp_levels):
                break
            if self.state.xp >= xp_levels[next_level]:
                self._level_up()
            else:
                break

    def _level_up(self):
        self.state.level += 1
        self.state.hp = RULES["stats"]["max_hp"]
        self.state.hunger = RULES["stats"]["max_hunger"]
        self.state.energy = RULES["stats"]["max_energy"]
        self.state.xp = 0

    def check_evolution(self):
        evolutions = RULES.get("evolutions", {}).get(self.state.codepet)
        if not evolutions:
            return

        for evo in evolutions:
            if self.state.stage == evo["required_stage"]:
                if self.state.level >= RULES["progression"]["max_level_by_stage"][self.state.stage - 1] and 
                (self.state.strength >= evo["min_strength"] or self.state.speed >= evo["min_speed"]):

                    self.state.codepet = evo["target_pet"]
                    self.state.stage += 1

                    self.state.hp = RULES["stats"]["max_hp"]
                    self.state.hunger = RULES["stats"]["max_hunger"]
                    self.state.energy = RULES["stats"]["max_energy"]

                    self.state.level = 1
                    self.state.xp = 0
                    break

    # --- MÉTODOS VITALES ---

    def take_damage(self, amount: int):
        self.state.hp = max(0, self.state.hp - amount)
        if self.state.hp == 0:
            self._die()

    def heal(self, amount: int):
        max_hp = RULES["stats"]["max_hp"]
        self.state.hp = min(max_hp, self.state.hp + amount)

    def add_waste(self, amount: int):
        max_waste = RULES["decay"]["max_waste"]
        self.state.waste = min(max_waste, self.state.waste + amount)
        if self.state.waste >= max_waste:
            self.take_damage(RULES["decay"]["hp_loss_when_max_waste"])

    def clean(self):
        self.state.waste = 0

    # --- CONTROL DE ESTADO ---

    def get_last_update(self):
        return self.state.last_update

    def set_last_update(self, value):
        self.state.last_update = value

    def process_time_passes(self, delta: float):
        updated = False

        hunger_interval = RULES["decay"]["hunger_interval"]
        hunger_ticks = int(delta // hunger_interval)
        if hunger_ticks > 0:
            self.state.hunger = max(0, self.state.hunger - hunger_ticks)
            if self.state.hunger <= 0:
                self.take_damage(RULES["decay"]["hp_loss_when_starving"])
            updated = True

        waste_interval = RULES["decay"]["waste_spawn_interval"]
        waste_ticks = int(delta // waste_interval)
        if waste_ticks > 0:
            self.add_waste(waste_ticks)
            updated = True

        energy_interval = RULES["energy"]["recover_interval"]
        energy_ticks = int(delta // energy_interval)
        if energy_ticks > 0 and self.state.hunger > 0:
            gain = energy_ticks * RULES["energy"]["recover_amount"]
            self.state.energy = min(self.state.energy + gain, RULES["stats"]["max_energy"])
            updated = True

        return updated

    def _die(self):
        self.state.codepet = "dead"

    def is_alive(self):
        return self.state.hp > 0

    def to_dict(self):
        return self.state.model_dump()