# scripts/seed_templates.py
from models.orm import SessionLocal, Template
from datetime import datetime

templates = [
    {"name":"out_of_hours","platform":None,"language":"es","title":"Fuera de horario","body":"Hola {name}, gracias por escribirnos. Nuestro horario de atención es Lunes a Viernes 08:00-18:00. Te responderemos en el próximo horario.","active":True},
    {"name":"followup_on_open","platform":None,"language":"es","title":"Seguimiento tras apertura","body":"Hola {name}, ya estamos en horario. ¿En qué puedo ayudarte ahora?","active":True},
    {"name":"generic_fallback","platform":None,"language":"es","title":"Respuesta por defecto","body":"Lo siento, no entendí tu petición. ¿Puedes reformularla o escribir 'ayuda' para opciones?","active":True},
    {"name":"greeting","platform":None,"language":"es","title":"Saludo","body":"¡Hola {name}! Soy el asistente de InterMotores. ¿En qué puedo ayudarte hoy?","active":True},
    {"name":"offer_list","platform":None,"language":"es","title":"Ofertas","body":"Estas son las ofertas actuales:\\n{items}","active":True},
]

db = SessionLocal()
for t in templates:
    existing = db.query(Template).filter(Template.name==t["name"]).first()
    if existing:
        print("Skipping existing:", t["name"])
        continue
    tpl = Template(
        name=t["name"],
        platform=t["platform"],
        language=t["language"],
        title=t["title"],
        body=t["body"],
        components=None,
        active=t["active"],
        created_at=datetime.utcnow()
    )
    db.add(tpl)
db.commit()
db.close()
print("Templates seeded")
