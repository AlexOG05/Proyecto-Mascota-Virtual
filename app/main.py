"""
Script Inicial
"""

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from core.game import load_state, save_state
from core.pet import Pet
from core.state import PetState
from core.game_loop import apply_decay

import time

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
    pet = load_state()
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
    save_state(pet)
    return pet.to_dict()

# Portal de noticias
@app.get("/news")
def game(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "news.html"        
    )

# Portal de guía
@app.get("/guide")
def game(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "guide.html"        
    )

# Portal de cuentas
@app.get("/account")
def game(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "user.html"        
    )

@app.post("/api/tick")
def tick():
    pet = load_state()
    apply_decay(pet)
    save_state(pet)
    return pet.to_dict()


@app.get("/api/state")
def get_state():
    pet = load_state()
    return pet.to_dict()