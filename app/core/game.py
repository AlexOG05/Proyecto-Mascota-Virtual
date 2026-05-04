"""
Script de lógica de juego
"""

# Imports
import json

from pathlib import Path

from .state import PetState
from .pet import Pet

# Archivo de guardado
BASE_DIR = Path(__file__).parent.parent
SAVE_FILE = BASE_DIR / "data" / "saves" / "save.json"

# Cargar estado de Mascota
def load_state() -> Pet:
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        return Pet(PetState(**data))
    except:
        return Pet(PetState())

# Guardar estado de mascota 
def save_state(pet: Pet):
    with open(SAVE_FILE, "w") as f:
        json.dump(pet.to_dict(), f, indent=4)

