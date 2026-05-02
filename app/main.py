from fastapi import FastAPI
from core.game import load_state, save_state, feed, train

app = FastAPI()

@app.get("/")
def root():
    return {"message": "VPet API funcionando."}

@app.get("/state")
def get_state():
    return load_state()

@app.post("/feed")
def feed_pet():
    state = load_state()
    state = feed(state)
    save_state(state)
    return state

@app.post("/train")
def train_pet():
    state = load_state()
    state = train(state)
    save_state(state)
    return state