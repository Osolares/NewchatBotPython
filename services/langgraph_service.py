# services/langgraph_service.py
import requests
from config import settings
from utils.logger import logger

class LangGraphService:
    def __init__(self):
        self.url = settings.LANGGRAPH_ENDPOINT
        self.key = settings.LANGGRAPH_API_KEY

    def query(self, prompt, user_id=None):
        if not self.url or not self.key:
            # fallback simple
            return "Lo siento, el servicio de LLM no está disponible actualmente."
        try:
            r = requests.post(self.url, json={"prompt": prompt, "user_id": user_id}, headers={"Authorization": f"Bearer {self.key}"}, timeout=15)
            r.raise_for_status()
            return r.json().get("reply", "")
        except Exception as e:
            logger.warning(f"LangGraph query failed: {e}")
            return "Error consultando el servicio de lenguaje."
