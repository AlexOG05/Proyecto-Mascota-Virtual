"""
Script que maneja el control del tiempo
"""

import time
from .pet import Pet

import json
from pathlib import Path

# RUTA DE RULESET
BASE_DIR = Path(__file__).parent.parent
RULES = json.load(open(BASE_DIR / "data" / "rules" / "ruleset.json"))

def apply_decay(pet: Pet):
    now = time.time()
    delta = now - pet.state.last_update

    # Manejo de energía
    energy_interval = RULES["energy"]["recover_interval"]
    energy_amount = RULES["energy"]["recover_amount"]
    max_energy = RULES["stats"]["max_energy"]

    energy_ticks = int(delta // energy_interval)
    if energy_ticks > 0 and pet.state.hunger > 0:
        pet.state.energy = min(pet.state.energy + (energy_ticks * energy_amount), max_energy)

    # Manejo de Hambre
    hunger_interval = RULES["decay"]["hunger_interval"]
    hunger_hp_loss = RULES["decay"]["hp_loss_when_starving"]

    hunger_ticks = int(delta // hunger_interval)
    if hunger_ticks > 0:
        pet.state.hunger = max(0, pet.state.hunger - hunger_ticks)

    if pet.state.hunger <= 0 and hunger_ticks > 1:
        pet.state.hp = max(0, pet.state.hp - hunger_hp_loss)

    # Manejo de basura
    waste_interval = RULES["decay"]["waste_spawn_interval"]
    waste_hp_loss = RULES["decay"]["hp_loss_when_max_waste"]
    max_waste = RULES["decay"]["max_waste"]

    waste_ticks = int(delta // waste_interval)
    if waste_ticks > 0:
        pet.state.waste = min(pet.state.waste + waste_ticks, max_waste)

    if pet.state.waste >= max_waste and waste_ticks > 1:
        pet.state.hp = max(0, pet.state.hp - waste_hp_loss)

    # Actualizar tiempo
    pet.state.last_update = now