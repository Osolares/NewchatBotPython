from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import PlainTextResponse
from config import settings
from adapters.telegram_adapter import TelegramAdapter
from adapters.whatsapp_adapter import WhatsAppAdapter
from bot.processor import process_message
from utils.security import verify_x_hub_signature
from utils.logger import logger
from models.orm import init_db
from scripts import scheduler
from utils.rate_limiter import rate_limiter
from admin_router import router as admin_router


# ------------------------------------------------------------
# Inicialización de la aplicación
# ------------------------------------------------------------
app = FastAPI(title="InterMotores Multibot")
init_db()


# ------------------------------------------------------------
# Adaptadores
# ------------------------------------------------------------
# Telegram
if settings.TELEGRAM_BOT_TOKEN:
    tg = TelegramAdapter()
else:
    tg = None

# WhatsApp
if settings.WHATSAPP_TOKEN and settings.PHONE_NUMBER_ID:
    wa = WhatsAppAdapter()
else:
    wa = None


# ------------------------------------------------------------
# Rutas administrativas
# ------------------------------------------------------------
app.include_router(admin_router)


# ------------------------------------------------------------
# Webhook Telegram
# ------------------------------------------------------------
@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    if tg is None:
        logger.error("Telegram adapter not initialized")
        return PlainTextResponse("Telegram disabled")

    body = await request.json()

    chat_id, text, user = tg.parse_update(body)

    if not chat_id or not text:
        return PlainTextResponse("ok")

    # Rate limiting por usuario
    key = f"telegram:{chat_id}"
    if not rate_limiter.allow(key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Procesar mensaje
    reply = process_message("telegram", str(chat_id), text, user_meta=user)

    tg.send_typing(chat_id)
    tg.send_message(chat_id, reply)

    return PlainTextResponse("ok")


# ------------------------------------------------------------
# Webhook WhatsApp - Verificación
# ------------------------------------------------------------
@app.get("/webhook/whatsapp")
async def verify_whatsapp(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None
):
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
    
    raise HTTPException(status_code=403, detail="Verification failed")


# ------------------------------------------------------------
# Webhook WhatsApp - Mensajes
# ------------------------------------------------------------
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    if wa is None:
        logger.error("WhatsApp adapter not initialized")
        return {"ok": True}

    body_bytes = await request.body()

    # Validar firma de Meta (si está configurada)
    if settings.FACEBOOK_APP_SECRET:
        if not verify_x_hub_signature(body_bytes, x_hub_signature_256):
            raise HTTPException(status_code=403, detail="Invalid signature")

    body = await request.json()

    try:
        entries = body.get("entry", [])
        for e in entries:
            changes = e.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])

                if not messages:
                    continue

                for msg in messages:
                    if msg.get("type") != "text":
                        continue

                    from_number = msg["from"]
                    text = msg["text"]["body"]

                    key = f"whatsapp:{from_number}"
                    if not rate_limiter.allow(key):
                        raise HTTPException(status_code=429, detail="Rate limit exceeded")

                    reply = process_message("whatsapp", from_number, text)

                    wa.send_text_message(from_number, reply)

        return {"ok": True}

    except Exception as ex:
        logger.exception("Error processing WhatsApp webhook")
        return {"ok": False, "error": str(ex)}


# ------------------------------------------------------------
# Root
# ------------------------------------------------------------
@app.get("/")
async def root():
    return {"status": "ok", "message": "InterMotores Multibot Running"}
