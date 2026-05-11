"""
Clase Pet
"""

from .state import PetState
import json
from pathlib import Path
import time

BASE_DIR = Path(__file__).parent.parent
_RULES_PATH = BASE_DIR / "data" / "rules" / "ruleset.json"

try:
    with open(_RULES_PATH) as f:
        RULES = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"No se encontró el archivo de reglas en: {_RULES_PATH}")
except json.JSONDecodeError as e:
    raise ValueError(f"Error al parsear ruleset.json: {e}")

class Pet:
    def __init__(self, state: PetState = None):
        self.state = state if state else PetState()

    # --- MÉTODOS DE CUIDADO Y ENTRENAMIENTO ---

    def feed(self):
        max_hunger = RULES["stats"]["max_hunger"]
        self.state.hunger = min(self.state.hunger + 1, max_hunger)
        self.state.last_fed = time.time()

    def train(self, stat_type: str, won_minigame: bool):
        pet_rules = RULES["stats"]["by_pet_type"].get(self.state.codepet)
        if not pet_rules or not any([
            pet_rules["max_strength_by_level"],
            pet_rules["max_speed_by_level"],
            pet_rules["max_combat_hp_by_level"],
        ]):
            return {"success": False, "message": f"{self.state.codepet} no puede entrenar."}

        energy_cost = RULES["training"]["energy_cost"]

        if self.state.energy < energy_cost:
            return {"success": False, "message": "Sin energía suficiente."}

        self.state.energy -= energy_cost

        if not won_minigame:
            return {"success": True, "message": "Minijuego perdido, sin ganancia."}

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
            case _:
                return {"success": False, "message": f"Tipo de stat desconocido: {stat_type}"}

        return {"success": True}

    # --- PROGRESIÓN Y EVOLUCIÓN ---

    def gain_xp(self, amount: int):
        current_stage = self.state.stage - 1
        stage_max_level = RULES["progression"]["max_level_by_stage"][current_stage]

        if self.state.level >= stage_max_level:
            self.check_evolution()
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
        self.check_evolution()

    @staticmethod
    def _stats_meet_evo(state, evo: dict) -> bool:
        # min = 0 significa que ese stat no es requisito
        strength_ok = state.strength >= evo["min_strength"] if evo["min_strength"] > 0 else True
        speed_ok    = state.speed    >= evo["min_speed"]    if evo["min_speed"]    > 0 else True
        return strength_ok and speed_ok

    def check_evolution(self):
        evolutions = RULES.get("evolutions", {}).get(self.state.codepet)
        if not evolutions:
            return None

        max_level = RULES["progression"]["max_level_by_stage"][self.state.stage - 1]

        for evo in evolutions:
            if self.state.stage != evo["required_stage"]:
                continue
            if self.state.level < max_level:
                continue
            if not self._stats_meet_evo(self.state, evo):
                continue

            self.state.codepet   = evo["target_pet"]
            self.state.stage    += 1
            self.state.hp        = RULES["stats"]["max_hp"]
            self.state.hunger    = RULES["stats"]["max_hunger"]
            self.state.energy    = RULES["stats"]["max_energy"]
            self.state.level     = 1
            self.state.xp        = 0
            self.state.strength  = 0
            self.state.speed     = 0
            self.state.combat_hp = 10
            break

    # --- MÉTODOS VITALES ---

    def take_damage(self, amount: int):
        self.state.hp = max(0, self.state.hp - amount)
        if self.state.hp == 0:
            self._die()

    def heal(self, amount: int):
        max_hp = RULES["stats"]["max_hp"]
        self.state.hp = min(max_hp, self.state.hp + amount)
        self.lose_xp(RULES["actions"]["heal_xp_cost"])

    def lose_xp(self, amount: int):
        self.state.xp = max(0, self.state.xp - amount)

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

    def is_hungry(self) -> bool:
        if self.state.last_fed is None:
            return True
        return (time.time() - self.state.last_fed) >= RULES["decay"]["hunger_interval"]

    def process_time_passes(self, delta: float):
        delta *= RULES["time"]["time_multiplier"]
        updated = False

        # Hambre
        hunger_interval = RULES["decay"]["hunger_interval"]
        hunger_ticks = int(delta // hunger_interval)
        if hunger_ticks > 0:
            self.state.hunger = max(0, self.state.hunger - hunger_ticks)
            updated = True

        if self.state.hunger <= 0:
            now = time.time()
            last = self.state.last_starve_tick or 0
            if (now - last) >= hunger_interval:
                self.take_damage(RULES["decay"]["hp_loss_when_starving"])
                self.state.last_starve_tick = now
                updated = True

        # Basura
        waste_interval = RULES["decay"]["waste_spawn_interval"]
        waste_ticks = int(delta // waste_interval)
        if waste_ticks > 0:
            self.add_waste(waste_ticks)
            updated = True

        # Energia
        energy_interval = RULES["energy"]["recover_interval"]
        energy_ticks = int(delta // energy_interval)
        if energy_ticks > 0 and self.state.hunger > 0:
            gain = energy_ticks * RULES["energy"]["recover_amount"]
            self.state.energy = min(self.state.energy + gain, RULES["stats"]["max_energy"])
            updated = True

        return updated

    def _die(self):
        self.state.hp = 0
        self.state.codepet = "dead"

    def is_alive(self):
        return self.state.hp > 0 and self.state.codepet != "dead"

    def _stat_caps(self) -> dict:
        pet_rules = RULES["stats"]["by_pet_type"].get(self.state.codepet)
        max_level = RULES["progression"]["max_level_by_stage"][self.state.stage - 1]
        if not pet_rules:
            return {"strength": 0, "speed": 0, "combat_hp": 0, "max_level": max_level}
        idx = self.state.level - 1
        def cap(arr): return arr[idx] if idx < len(arr) else 0
        return {
            "strength":  cap(pet_rules["max_strength_by_level"]),
            "speed":     cap(pet_rules["max_speed_by_level"]),
            "combat_hp": cap(pet_rules["max_combat_hp_by_level"]),
            "max_level": max_level,
        }

    def _evolution_info(self) -> list:
        evolutions = RULES.get("evolutions", {}).get(self.state.codepet, [])
        max_level = RULES["progression"]["max_level_by_stage"][self.state.stage - 1]
        result = []
        for evo in evolutions:
            level_ok    = self.state.level >= max_level
            strength_ok = self.state.strength >= evo["min_strength"] if evo["min_strength"] > 0 else True
            speed_ok    = self.state.speed    >= evo["min_speed"]    if evo["min_speed"]    > 0 else True
            result.append({
                "target":       evo["target_pet"],
                "min_strength": evo["min_strength"],
                "min_speed":    evo["min_speed"],
                "level_ok":     level_ok,
                "strength_ok":  strength_ok,
                "speed_ok":     speed_ok,
                "can_evolve":   level_ok and strength_ok and speed_ok,
            })
        return result

    def to_dict(self):
        data = self.state.model_dump()
        data["evolutions"] = self._evolution_info()
        data["stat_caps"]  = self._stat_caps()
        return data