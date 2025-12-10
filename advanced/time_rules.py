# advanced/time_rules.py
from datetime import datetime, time, timedelta
import pytz
from config import settings
from models.orm import SessionLocal, BusinessHours, SpecialHours, Holiday, ScheduledMessage
from utils.logger import logger

TZ = pytz.timezone(settings.TIMEZONE)

def _parse_time_obj(t):
    # t is a time object already if stored as Time in DB
    return t

def get_weekly_hours():
    """Retorna dict {weekday: (open_time, close_time)} para días activos"""
    db = SessionLocal()
    rows = db.query(BusinessHours).filter(BusinessHours.active==True).all()
    db.close()
    hours = {}
    for r in rows:
        hours[r.weekday] = (r.open_time, r.close_time)
    return hours

def get_special_hours_for_date(date_iso):
    """Devuelve SpecialHours row o None para la fecha ISO"""
    db = SessionLocal()
    s = db.query(SpecialHours).filter(SpecialHours.date==date_iso, SpecialHours.active==True).first()
    db.close()
    return s

def is_holiday(date_iso):
    db = SessionLocal()
    h = db.query(Holiday).filter(Holiday.date==date_iso, Holiday.active==True).first()
    db.close()
    return bool(h)

def _now_tz():
    return datetime.now(TZ)

def is_open_now():
    """
    Lógica completa:
    - Si hay special_hours (cerrado todo el día o horario especial) la respeta
    - Si es feriado (Holiday) devuelve False
    - Si no, usa business_hours por weekday
    """
    now = _now_tz()
    date_iso = now.date().isoformat()

    # 1) holiday check
    if is_holiday(date_iso):
        return False

    # 2) special hours
    s = get_special_hours_for_date(date_iso)
    if s:
        if s.open_time is None or s.close_time is None:
            return False  # cerrado todo el dia
        return s.open_time <= now.time() <= s.close_time

    # 3) weekly hours
    hours = get_weekly_hours()
    wd = now.weekday()
    if wd not in hours:
        return False
    open_time, close_time = hours[wd]
    if open_time is None or close_time is None:
        return False
    return open_time <= now.time() <= close_time

def next_opening_after(dt=None):
    """
    Retorna datetime (tz-aware) del siguiente inicio de horario después de dt (o ahora).
    Si hoy se cerró y reabre hoy, devuelve hoy's open_time if in future, else busca next day.
    """
    if dt is None:
        dt = _now_tz()
    db = SessionLocal()
    # build a search window de hasta 30 días
    for day_offset in range(0, 31):
        candidate = (dt + timedelta(days=day_offset)).astimezone(TZ)
        date_iso = candidate.date().isoformat()
        # skip holidays
        if is_holiday(date_iso):
            continue
        # special hours?
        s = db.query(SpecialHours).filter(SpecialHours.date==date_iso, SpecialHours.active==True).first()
        if s:
            # if closed all day -> skip
            if s.open_time is None or s.close_time is None:
                continue
            # compute opening datetime
            open_dt = TZ.localize(datetime.combine(candidate.date(), s.open_time))
            if open_dt > dt:
                db.close()
                return open_dt
            else:
                continue
        # weekly hours
        wd = candidate.weekday()
        bh = db.query(BusinessHours).filter(BusinessHours.weekday==wd, BusinessHours.active==True).first()
        if not bh:
            continue
        open_dt = TZ.localize(datetime.combine(candidate.date(), bh.open_time))
        if open_dt > dt:
            db.close()
            return open_dt
    db.close()
    return None

def schedule_message_at_next_open(platform, platform_id, text, meta=None):
    """
    Crea un ScheduledMessage para enviar al inicio del siguiente horario.
    """
    send_at = next_opening_after()
    if not send_at:
        logger.warning("No next opening found; message not scheduled")
        return None
    db = SessionLocal()
    sm = ScheduledMessage(platform=platform, platform_id=platform_id, text=text, send_at=send_at, sent=False)
    db.add(sm)
    db.commit()
    db.refresh(sm)
    db.close()
    return sm
