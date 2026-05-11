"""
Script para estado de mascotas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class PetState(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    # Información de mascota
    name: str = "Sin Nombre"                        # Apodo proporcionado por el usuario
    codepet: str = "punchy"                         # Tipo de mascota (define el sprite)

    # Estadísticas vitales
    hp: int = Field(default=6, ge=0, le=6)          # 0 - 6 (Vida vital)
    hunger: int = Field(default=6, ge=0, le=6)      # 0 - 6 (Medidor de hambre)
    energy: int = Field(default=100, ge=0, le=100)  # 0 - 100 (Medidor de energía)
    waste: int = Field(default=0, ge=0, le=3)       # 0 - 3 (Archivos Basura)

    # Estadísticas de combate
    combat_hp: int = Field(default=10, ge=0, le=100)  # 0 - 100 (Vida de combate)
    strength: int = Field(default=0, ge=0, le=100)    # 0 - 100 (Fuerza de combate)
    speed: int = Field(default=0, ge=0, le=100)       # 0 - 100 (Velocidad de combate)

    # Estadísticas de evolución y control
    xp: int = Field(default=0, ge=0)                  # Progreso evoltivo
    level: int = Field(default=1, ge=1, le=10)        # 1 - 10 (Nivel de mascota)
    stage: int = Field(default=1, ge=1, le=5)         # 1 - 5 (Nivel de evolución/Etapa)
    last_update: Optional[float] = None               # Última actualización (None = nunca)
    last_fed: Optional[float] = None                  # Última vez alimentado (None = nunca)
    last_starve_tick: Optional[float] = None          # Último daño por hambre (None = nunca)