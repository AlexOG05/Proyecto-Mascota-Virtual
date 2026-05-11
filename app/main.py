"""
Script Inicial
"""

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from core.save_manager import SaveManager
from core.pet import Pet
from core.state import PetState
from core.combat_manager import CombatManager
from core.battle_logger import BattleLogger
from pydantic import BaseModel

import time

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Schemas
class NameRequest(BaseModel):
    name: str

class TrainRequest(BaseModel):
    stat_type: str
    won_minigame: bool

class FightRequest(BaseModel):
    zone_index: int
    won_minigame: bool

save_manager = SaveManager()
combat_manager = CombatManager()
battle_logger = BattleLogger()

@app.get("/api/battle-history")
def battle_history():
    return battle_logger.get_recent(20)

# Landing Page
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "index.html"
        )

# Página de Juego
@app.get("/game")
def game(request: Request):
    pet = save_manager.load_state()
    return templates.TemplateResponse(
        request = request,
        name = "game.html",
        context = {
            "pet": pet.to_dict()
        }
    )

# Nueva partida
@app.post("/api/new-game")
def new_game():
    pet = Pet(PetState())
    pet.state.last_update = time.time()
    save_manager.save_state(pet)
    return pet.to_dict()

# Portal de noticias
@app.get("/news")
def news(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "news.html"
    )

# Portal de guía
@app.get("/guide")
def guide(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "guide.html"
    )

@app.post("/api/tick")
def tick():
    pet = save_manager.load_state()
    now = time.time()
    last = pet.get_last_update()
    if last:
        updated = pet.process_time_passes(now - last)
        if updated:
            pet.set_last_update(now)
    else:
        pet.set_last_update(now)
    save_manager.save_state(pet)
    return pet.to_dict()

@app.get("/api/state")
def get_state():
    pet = save_manager.load_state()
    return pet.to_dict()



@app.post("/api/train")
def train(req: TrainRequest):
    pet = save_manager.load_state()
    result = pet.train(req.stat_type, req.won_minigame)
    save_manager.save_state(pet)
    return {**result, **pet.to_dict()}

@app.post("/api/set-name")
def set_name(req: NameRequest):
    name = req.name.strip()[:20]
    if not name:
        return {"success": False, "message": "Nombre no válido."}
    pet = save_manager.load_state()
    pet.state.name = name
    save_manager.save_state(pet)
    return {"success": True, **pet.to_dict()}

@app.post("/api/feed")
def feed():
    pet = save_manager.load_state()
    max_hunger = pet.state.hunger >= 6
    if not max_hunger:
        pet.feed()
        save_manager.save_state(pet)
        return {"success": True, "message": "Alimentado.", **pet.to_dict()}
    return {"success": False, "message": "Ya tiene el hambre llena.", **pet.to_dict()}

@app.post("/api/clean")
def clean():
    pet = save_manager.load_state()
    if pet.state.waste == 0:
        return {"success": False, "message": "No hay archivos basura.", **pet.to_dict()}
    pet.clean()
    save_manager.save_state(pet)
    return {"success": True, "message": "Archivos eliminados.", **pet.to_dict()}

@app.post("/api/heal")
def heal():
    pet = save_manager.load_state()
    if pet.state.hp >= 6:
        return {"success": False, "message": "Ya tiene la vida al máximo.", **pet.to_dict()}
    pet.heal(1)
    save_manager.save_state(pet)
    return {"success": True, "message": "Vida restaurada. -20 XP.", **pet.to_dict()}

@app.get("/api/zones")
def get_zones():
    pet = save_manager.load_state()
    return combat_manager.available_zones(pet)

@app.post("/api/fight")
def fight(req: FightRequest):
    pet = save_manager.load_state()
    result = combat_manager.fight(pet, req.zone_index, req.won_minigame)
    save_manager.save_state(pet)
    return {**result, **pet.to_dict()}
