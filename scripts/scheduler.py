# scripts/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from config import settings
from datetime import datetime
from models.orm import SessionLocal, ScheduledMessage
from adapters.telegram_adapter import TelegramAdapter
from utils.logger import logger

sched = BackgroundScheduler(timezone=settings.TIMEZONE)
telegram = TelegramAdapter()

def send_scheduled_messages():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        q = db.query(ScheduledMessage).filter(ScheduledMessage.sent==False, ScheduledMessage.send_at <= now).all()
        for msg in q:
            if msg.platform == "telegram":
                telegram.send_message(msg.platform_id, msg.text)
            # agregar whatsapp adapter si activo
            msg.sent = True
            db.add(msg)
        db.commit()
    except Exception as e:
        logger.warning(f"scheduler error {e}")
    finally:
        db.close()

sched.add_job(send_scheduled_messages, "interval", seconds=30)
sched.start()
