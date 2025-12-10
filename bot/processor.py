from services.langgraph_service import LangGraphService
from services.woocommerce_service import WooCommerceService
from utils.logger import logger
from bot.state_manager import StateManager
from bot.flows.vehicle_search import start as vs_start, handle as vs_handle
from utils.timeutils import is_open_now
from models.orm import SessionLocal, Template

import re
# al inicio del archivo, agregar
from advanced.time_rules import is_open_now, schedule_message_at_next_open

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


# ... dentro de process_message(...)
    # 2. fuera de horario?
    if not is_open_now():
        tpl = get_template("out_of_hours", platform=platform)
        name = (user_meta.get('first_name') if isinstance(user_meta, dict) else '')
        reply_text = tpl.body.format(name=name) if tpl else "Gracias por escribirnos. Nuestro horario es L-V 08:00-18:00. Te responderemos en el próximo horario."

        # Opcional: encolar un recordatorio para enviar al abrir
        # Solo encolamos si no existe un ScheduledMessage similar (evitamos duplicados)
        try:
            # build follow-up text (puedes personalizar)
            follow_up_tpl = get_template("followup_on_open", platform=platform)
            follow_text = follow_up_tpl.body.format(name=name) if follow_up_tpl else f"Hola {name}, te escribimos en horario de atención. ¿En qué puedo ayudarte?"
            schedule_message_at_next_open(platform, platform_id, follow_text)
        except Exception as e:
            logger.warning(f"Could not schedule follow-up: {e}")

        return reply_text


    #if not is_open_now():
    #    tpl = get_template("out_of_hours", platform=platform)
    #    if tpl:
    #        name = (user_meta.get('first_name') if isinstance(user_meta, dict) else '')
    #        return tpl.body.format(name=name)
    #    return "Gracias por escribirnos. Nuestro horario de atención es L-V 08:00-18:00. Te responderemos en el próximo horario."

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
