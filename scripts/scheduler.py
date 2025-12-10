from apscheduler.schedulers.background import BackgroundScheduler
from config import settings
from datetime import datetime
from models.orm import SessionLocal, ScheduledMessage
from adapters.telegram_adapter import TelegramAdapter
from adapters.whatsapp_adapter import WhatsAppAdapter
from utils.logger import logger

sched = BackgroundScheduler(timezone=settings.TIMEZONE)

try:
    telegram = TelegramAdapter()
except Exception:
    telegram = None
try:
    whatsapp = WhatsAppAdapter()
except Exception:
    whatsapp = None

def send_scheduled_messages():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        q = db.query(ScheduledMessage).filter(ScheduledMessage.sent==False, ScheduledMessage.send_at <= now).all()
        for msg in q:
            if msg.platform == "telegram" and telegram:
                telegram.send_message(msg.platform_id, msg.text)
            if msg.platform == "whatsapp" and whatsapp:
                whatsapp.send_text(msg.platform_id, msg.text)
            msg.sent = True
            db.add(msg)
        db.commit()
    except Exception as e:
        logger.warning(f"scheduler error {e}")
    finally:
        db.close()

sched.add_job(send_scheduled_messages, "interval", seconds=30)
