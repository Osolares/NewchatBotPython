# bot/processor.py
from services.langgraph_service import LangGraphService
from services.woocommerce_service import WooCommerceService
from utils.logger import logger
from bot.state_manager import StateManager
from datetime import datetime
import re

lang = LangGraphService()
wc = WooCommerceService()
state_mgr = StateManager()

def process_message(platform, platform_id, text, user_meta=None):
    """
    Procesa un mensaje entrante y devuelve la respuesta a enviar.
    - platform: 'telegram' | 'whatsapp'
    - platform_id: chat_id o phone
    - text: texto bruto
    """
    # registro de estado
    state = state_mgr.get_state(platform, platform_id)

    # sanear texto
    t = (text or "").strip()
    if not t:
        return "No entendí tu mensaje."

    t_lower = t.lower()

    # ejemplos de flujos
    if re.search(r'\b(hola|buenas|buenos)\b', t_lower):
        return f"¡Hola! Soy InterMotores. ¿En qué puedo ayudarte hoy?"

    if "oferta" in t_lower or "ofertas" in t_lower:
        # consulta a WooCommerce para obtener ofertas
        products = wc.list_promotions(limit=5)
        lines = ["Nuestras ofertas actuales:"]
        for p in products:
            lines.append(f"- {p.get('name')} — {p.get('price')}")
        return "\n".join(lines)

    # Delegar a LangGraph para flujos conversacionales complejos si aplica
    if should_use_langgraph(t_lower):
        reply = lang.query(t, user_id=f"{platform}:{platform_id}")
        return reply

    # default
    return "No tengo una respuesta automática para eso. ¿Quieres que te transfiera a un agente?"

def should_use_langgraph(text):
    # política: usa LLM solo para preguntas abiertas, no para transaccional
    triggers = ["ayuda", "explica", "como", "qué", "quién"]
    return any(t in text for t in triggers)
