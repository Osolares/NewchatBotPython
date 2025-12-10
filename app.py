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


app = FastAPI(title="InterMotores Multibot")
init_db()


if settings.TELEGRAM_BOT_TOKEN:
tg = TelegramAdapter()
else:
tg = None


wa = None
if settings.WHATSAPP_TOKEN and settings.PHONE_NUMBER_ID:
wa = WhatsAppAdapter()


app.include_router(admin_router)


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
body = await request.json()
chat_id, text, user = tg.parse_update(body)
if not chat_id or not text:
return PlainTextResponse("ok")
key = f"telegram:{chat_id}"
if not rate_limiter.allow(key):
raise HTTPException(status_code=429, detail="Rate limit")
reply = process_message("telegram", str(chat_id), text, user_meta=user)
tg.send_typing(chat_id)
tg.send_message(chat_id, reply)
return PlainTextResponse("ok")


@app.get("/webhook/whatsapp")
async def verify_whatsapp(hub_mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
return PlainTextResponse(hub_challenge)
raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, x_hub_signature_256: str = Header(None)):
body_bytes = await request.body()
if settings.FACEBOOK_APP_SECRET:
if not verify_x_hub_signature(body_bytes, x_hub_signature_256):
raise HTTPException(status_code=403, detail="Invalid signature")
body = await request.json()
try:
entries = body.get("entry", [])
for e in entries:
return {"ok": True}