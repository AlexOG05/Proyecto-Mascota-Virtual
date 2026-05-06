"""
Script para estado de mascotas
"""

from pydantic import BaseModel

class PetState(BaseModel):
    # Información de mascota
    name: str = "Sin Nombre"    # Apodo proporcionado por el usuario
    codepet: str = "punchy"     # Tipo de mascota (define el sprite)

    # Estadísticas vitales
    hp: int = 6                 # 0 - 6 (Vida vital)
    hunger: int = 3             # 0 - 6 (Medidor de hambre)
    energy: int = 100           # 0 - 100 (Medidor de energía)
    waste: int = 0              # 0 - 3 (Archivos Basura)

    # Estadísticas de combate
    combat_hp: int = 100        # 0 - 100 (Vida de combate)
    strength: int = 0           # 0 - 100 (Fuerza de combate)
    speed: int = 0              # 0 - 100 (Velocidad de combate)

    # Estadísticas de evolución y control
    xp: int = 0                 # Progreso hacia la evolución
    level: int = 1              # 1- 10 (Nivel de mascota)
    stage: int = 1              # 1 - 6 (Nivel de evolución/Etapa)
    last_update: float = 0