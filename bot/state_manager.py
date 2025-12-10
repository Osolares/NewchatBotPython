# bot/state_manager.py
from models.orm import SessionLocal, User, Message
from utils.logger import logger

class StateManager:
    def __init__(self):
        pass

    def get_state(self, platform, platform_id):
        # simple: se puede cargar contexto desde DB si quieres persistencia
        return {"platform": platform, "platform_id": platform_id}
