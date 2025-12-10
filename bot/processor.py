from services.langgraph_service import LangGraphService
from services.woocommerce_service import WooCommerceService
from utils.logger import logger
from bot.state_manager import StateManager
from bot.flows.vehicle_search import start as vs_start, handle as vs_handle
from utils.timeutils import is_open_now
from models.orm import SessionLocal, Template

import re

lang = LangGraphService()
wc = WooCommerceService()
state_mgr = StateManager()

def get_template(name, platform=None, language="es"):
    db = SessionLocal()
    q = db.query(Template).filter(Template.name==name, Template.active==True)
    if platform:
        t = q.filter((Template.platform==platform) | (Template.platform==None)).first()
    else:
        t = q.first()
    db.close()
    return t

def should_use_langgraph(text):
    triggers = ["ayuda", "explica", "como", "qué", "quién"]
    return any(t in text for t in triggers)

def process_message(platform, platform_id, text, user_meta=None):
    t = (text or "").strip()
    if not t:
        return "No entendí tu mensaje."

    s = state_mgr.get_state(platform, platform_id)

    if not is_open_now():
        tpl = get_template("out_of_hours", platform=platform)
        if tpl:
            name = (user_meta.get('first_name') if isinstance(user_meta, dict) else '')
            return tpl.body.format(name=name)
        return "Gracias por escribirnos. Nuestro horario de atención es L-V 08:00-18:00. Te responderemos en el próximo horario."

    if s.current_flow == "vehicle_search":
        return vs_handle(platform, platform_id, t)

    if re.search(r'buscar|filtro|filtros|pieza|repuesto', t.lower()):
        return vs_start(platform, platform_id)

    if re.search(r'oferta|ofertas', t.lower()):
        products = wc.list_promotions(limit=5)
        if products:
            lines = ["Nuestras ofertas actuales:"]
            for p in products:
                lines.append(f"- {p.get('name')} — {p.get('price')}")
            return "\n".join(lines)
        return "No hay ofertas en este momento."

    if should_use_langgraph(t.lower()):
        return lang.query(t, user_id=f"{platform}:{platform_id}")

    tpl = get_template("generic_fallback", platform=platform)
    if tpl:
        return tpl.body
    return "No tengo una respuesta automática para eso. ¿Quieres que te transfiera a un agente?"
