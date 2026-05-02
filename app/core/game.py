"""
Script de lógica de juego
"""

# Imports
import json
import time
from .state import PetState

# Archivo de guardado
SAVE_FILE = "data/saves/save.json"

# Cargar estado de Mascota
def load_state() -> PetState:
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        return PetState(**data)
    except:
        return PetState()

# Guardar estado de mascota 
def save_state(state: PetState):
    with open(SAVE_FILE, "w") as f:
        json.dump(state.model_dump(), f)

# Paso del tiempo
def apply_time_decay(state):
    now = time.time()

    if state.last_update == 0:
        state.last_update = now
        return state
    
    delta = now - state.last_update

# Acciones Digimon
def feed(state: PetState) -> PetState:
    state.hunger = max(0, state.hunger - 10)
    state.fun = min(100, state.energy + 2)
    return state

def train(state: PetState) -> PetState:
    state.xp += 10
    state.fun = max(0, state.fun - 5)
    return state
