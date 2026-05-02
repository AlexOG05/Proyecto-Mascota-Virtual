"""
Script para estado de mascotas
"""

# Imports
from pydantic import BaseModel

# Clases Modelo Base
class PetState(BaseModel):
    name: str = "Tarjeta Perforada"
    hp: int = 6                 # 0 - 6
    hunger: int = 0             # 0 - 6
    energy: int = 0             # 0 - 6

    strength: int = 0           # 0 - 100
    speed: int = 0              # 0 - 100

    xp: int = 0                 # Depende de la evolución a alcanzar
    stage: int = 1              # 1 - 6 (Nivel de evolución)
    last_update: float = 0