# CodePets

Mascota virtual de navegador inspirada en los Tamagotchi, ambientada en el mundo de la programación. Cuida, entrena y evoluciona tu codepet desde una tarjeta perforada hasta un framework moderno.

---

## ¿Qué es CodePets?

El jugador adopta un codepet llamado **Punchy** y debe mantenerlo con vida alimentándolo, limpiando sus archivos basura y curándolo cuando pierde vida. A medida que pelea y entrena, acumula experiencia y mejora sus estadísticas, lo que le permite evolucionar a través de un árbol ramificado de **9 formas** distintas.

El juego corre en tiempo real: aunque el navegador esté cerrado, el hambre sigue bajando y la basura sigue acumulándose. Al volver, el servidor calcula todo el tiempo transcurrido y aplica las consecuencias.

---

## Tecnologías

- **Backend:** Python · FastAPI · Pydantic v2
- **Frontend:** HTML · CSS · JavaScript Vanilla
- **Almacenamiento:** JSON (partida) · CSV (historial de batallas)

---

## Instalación y ejecución

**Requisitos:** Python 3.10+

```bash
# 1. Clonar el repositorio
git clone https://github.com/AlexOG05/Proyecto-Mascota-Virtual.git
cd Proyecto-Mascota-Virtual

# 2. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Arrancar el servidor
cd app
uvicorn main:app --reload
```

Abrir en el navegador: **http://localhost:8000**

---

## Árbol de evoluciones

```
Punchy → Machina → Ssembly ──→ Pythark ──→ Reinhardt
                         │            └──→ Anakhon
                         └──→ Duke    ──→ Springolem
                                      └──→ Dukeotlin
```

Las bifurcaciones dependen de los stats entrenados (strength o speed).
