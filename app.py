# app.py
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import PlainTextResponse
from config import settings
from adapters.telegram_adapter import TelegramAdapter
from adapters.whatsapp_adapter import WhatsAppAdapter
from bot.processor import process_message
from utils.security import verify_x_hub_signature
from utils.logger import logger
from models.orm import init_db
from scripts.scheduler import sched  # inicia scheduler
from utils.rate_limiter import rate_limiter

app = FastAPI(title="InterMotores Multibot")

# inicializar db
init_db()

tg = TelegramAdapter() if settings.TELEGRAM_BOT_TOKEN else None
wa = None
if settings.WHATSAPP_TOKEN and settings.PHONE_NUMBER_ID:
    wa = WhatsAppAdapter()

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    body = await request.json()
    chat_id, text, user = tg.parse_update(body)
    if not chat_id or not text:
        return PlainTextResponse("ok")
    # rate limit
    key = f"telegram:{chat_id}"
    if not rate_limiter.allow(key):
        raise HTTPException(status_code=429, detail="Rate limit")
    # process
    reply = process_message("telegram", str(chat_id), text, user_meta=user)
    tg.send_typing(chat_id)
    tg.send_message(chat_id, reply)
    return PlainTextResponse("ok")

# WhatsApp webhook (verify + receive)
@app.get("/webhook/whatsapp")
async def verify_whatsapp(hub_mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    body_bytes = await request.body()
    # valida firma si tienes app secret
    if settings.FACEBOOK_APP_SECRET:
        if not verify_x_hub_signature(body_bytes, x_hub_signature_256):
            raise HTTPException(status_code=403, detail="Invalid signature")
    body = await request.json()
    # parsea la estructura de WhatsApp
    try:
        entries = body.get("entry", [])
        for e in entries:
            for change in e.get("changes", []):
                val = change.get("value", {})
                messages = val.get("messages", [])
                for m in messages:
                    phone = m.get("from")
                    text = m.get("text", {}).get("body", "")
                    # rate limit
                    key = f"whatsapp:{phone}"
                    if not rate_limiter.allow(key):
                        continue
                    reply = process_message("whatsapp", phone, text, user_meta=m.get("from"))
                    # si fuera fuera de horario, encola o usa plantilla
                    if wa:
                        wa.send_text(phone, reply)
    except Exception as e:
        logger.warning(f"whatsapp webhook parse error {e}")
    return PlainTextResponse("ok")
