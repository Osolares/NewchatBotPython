# bot/templates.py
import json
from config import settings
from datetime import datetime

def out_of_hours_message(name=None):
    text = "Gracias por contactarnos. Nuestro horario de atención es de Lunes a Viernes 8:00-18:00. Te responderemos lo antes posible."
    if name:
        return f"Hola {name}, {text}"
    return text
