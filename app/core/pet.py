"""
Clase Pet
"""

from .state import PetState

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
RULES = json.load(open(BASE_DIR / "data" / "rules" / "ruleset.json"))

class Pet:
    def __init__(self, state: PetState):
        self.state = state

    # Alimentar - Aumenta en 1 el medidor de hambre
    def feed(self):
        max_hunger = RULES["stats"]["max_hunger"]
        self.state.hunger = min(self.state.hunger + 1, max_hunger)

    # Entrenar - Aumenta el medidor de fuerza y velocidad
    def train(self):
        energy_cost = RULES["training"]["energy_cost"]

        if self.state.energy >= energy_cost:
            # FUERZA
            max_strength = RULES["stats"]["max_strength_by_stage"][self.state.stage]
            strength_gain = RULES["training"]["strength_gain"]

            # VELOCIDAD
            max_speed = RULES["stats"]["max_speed_by_stage"][self.state.stage]
            speed_gain = RULES["training"]["speed_gain"]

            self.state.strength = min(self.state.strength + strength_gain, max_strength)
            self.state.speed = min(self.state.speed + speed_gain, max_speed)
            self.state.energy -= energy_cost

    def is_alive(self):
        return self.state.hp > 0
    
    def to_dict(self):
        return self.state.model_dump()