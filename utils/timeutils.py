from datetime import datetime, time
import pytz
from config import settings
from models.orm import SessionLocal, Holiday

def is_holiday(date_iso_str):
    db = SessionLocal()
    h = db.query(Holiday).filter(Holiday.date==date_iso_str, Holiday.active==True).first()
    db.close()
    return bool(h)

def is_open_now():
    tz = pytz.timezone(settings.TIMEZONE)
    now = datetime.now(tz)
    date_iso = now.date().isoformat()
    if is_holiday(date_iso):
        return False
    wd = now.weekday()
    if wd >=0 and wd <=4:
        open_from = time(8,0)
        open_to = time(18,0)
        return open_from <= now.time() <= open_to
    return False
