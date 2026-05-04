from app.core.pet import Pet
from app.core.state import PetState

ps1 = PetState()
p1 = Pet(ps1)
print(p1.state.stage)