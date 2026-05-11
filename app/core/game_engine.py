"""
Clase GameEngine
Maneja el control del juego
"""

import time
import json
from pathlib import Path
from .pet import Pet
from .save_manager import SaveManager

# Ruta de ruleset.json
BASE_DIR = Path(__file__).parent.parent
RULES = json.load(open(BASE_DIR / "data" / "rules" / "ruleset.json"))

class GameEngine:
    def __init__(self):
        self.save_manager = SaveManager()
        self.pet = self.save_manager.load_state()
        self.update()

    def update(self):
        if not self.pet.is_alive():
            return

        now = time.time()
        # Usamos un "getter" para obtener el tiempo sin tocar el state directamente
        last_update = self.pet.get_last_update() 

        if last_update == 0:
            self.pet.set_last_update(now)
            self.save_manager.save_state(self.pet)
            return

        delta = now - last_update

        # Le pasamos la pelota a la mascota: "Toma el tiempo y las reglas, actualízate tú"
        # Este método procesará el hambre, basura y energía internamente
        updated = self.pet.process_time_passes(delta)

        if updated:
            self.pet.set_last_update(now)
            self.save_manager.save_state(self.pet)

    # --- WRAPPERS PARA ACCIONES (Simplifican la vida a FastAPI) ---

    def feed_pet(self):
        if self.pet.is_alive():
            self.pet.feed() #[cite: 1]
            self.save_manager.save_state(self.pet)
            return True
        return False

    def train_pet(self, stat_type: str, won: bool):
        if self.pet.is_alive():
            result = self.pet.train(stat_type, won) #[cite: 1]
            self.save_manager.save_state(self.pet)
            return result
        return {"success": False, "message": "La mascota ha fallecido."}

    def get_status(self):
        """Devuelve el estado actualizado para el frontend"""
        self.update() # Forzamos actualización antes de enviar datos
        return self.pet.to_dict() #[cite: 1]