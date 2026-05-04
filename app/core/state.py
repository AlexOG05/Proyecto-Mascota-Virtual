"""
Script para estado de mascotas
"""

# Imports
from pydantic import BaseModel

# Clase PetState
class PetState(BaseModel):
    name: str = "punchy"
    hp: int = 6                 # 0 - 6
    hunger: int = 3             # 0 - 6
    energy: int = 100           # 0 - 6

    strength: int = 0           # 0 - 100
    speed: int = 0              # 0 - 100

    xp: int = 0                 # Depende de la evolución a alcanzar
    stage: int = 1              # 1 - 6 (Nivel de evolución)
    waste: int = 0              # 0 - 3 (Archivos Basura)
    last_update: float = 0