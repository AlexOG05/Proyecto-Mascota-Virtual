"""
Clase para la gestión de guardado y carga
"""

import json
from pathlib import Path
from .state import PetState
from .pet import Pet

class SaveManager:
    def __init__(self, filename: str = "save.json"):
        # Configurar las rutas
        self.base_dir = Path(__file__).parent.parent
        self.save_file = self.base_dir / "data" / "saves" / filename

    def load_state(self) -> Pet:
        try:
            # Verificar existencia de archivo
            if not self.save_file.exists():
                print("No se encontró partida guardada. Creando una nueva mascota...")
                return Pet(PetState())

            with open(self.save_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            return Pet(PetState(**data))

        except json.JSONDecodeError:
            print("¡Advertencia! El archivo está corrupto. Iniciando partida nueva...")
            return Pet(PetState())
            
        except Exception as e:
            print(f"Error inesperado al cargar la partida: {e}")
            return Pet(PetState())

    def save_state(self, pet: Pet):
        try:
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(pet.state.model_dump(), f, indent=4)
                
        except Exception as e:
            print(f"Error crítico al intentar guardar la partida: {e}")