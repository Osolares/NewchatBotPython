# bot/templates.py
import json
from config import settings
from datetime import datetime

def out_of_hours_message(name=None):
    text = "Gracias por contactarnos. Nuestro horario de atención es de Lunes a Viernes 8:00-18:00. Te responderemos lo antes posible."
    if name:
        return f"Hola {name}, {text}"
    return text

# bot/templates.py (función util)
from models.orm import SessionLocal, Template

def get_template(name, platform=None, language="es"):
    db = SessionLocal()
    q = db.query(Template).filter(Template.name==name, Template.active==True)
    if platform:
        t = q.filter((Template.platform==platform) | (Template.platform==None)).first()
    else:
        t = q.first()
    db.close()
    return t

# ejemplo de uso en processor
t = get_template("out_of_hours", platform=platform, language="es")
if t:
    reply_text = t.body.format(name=user_name or "")
else:
    reply_text = "Nuestro horario es..."
