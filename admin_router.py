from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from config import settings
from models.orm import SessionLocal, Template, Holiday

from pydantic import BaseModel
from models.orm import BusinessHours, SpecialHours
from datetime import time

router = APIRouter(prefix="/admin", tags=["admin"])

class TemplateIn(BaseModel):
    name: str
    platform: str | None = None
    language: str = "es"
    title: str | None = None
    body: str
    components: dict | None = None
    active: bool = True

def admin_guard(x_api_key: str = Header(None)):
    secret = settings.ADMIN_API_KEY
    if not secret or x_api_key != secret:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True

@router.post("/templates", dependencies=[Depends(admin_guard)])
def create_template(payload: TemplateIn):
    db = SessionLocal()
    t = Template(
        name=payload.name,
        platform=payload.platform,
        language=payload.language,
        title=payload.title,
        body=payload.body,
        components=payload.components,
        active=payload.active
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    db.close()
    return {"ok": True, "template_id": t.id}

@router.get("/templates", dependencies=[Depends(admin_guard)])
def list_templates():
    db = SessionLocal()
    ts = db.query(Template).all()
    db.close()
    return ts

@router.put("/templates/{template_id}", dependencies=[Depends(admin_guard)])
def update_template(template_id: int, payload: TemplateIn):
    db = SessionLocal()
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.dict().items():
        setattr(t, k, v)
    db.add(t)
    db.commit()
    db.refresh(t)
    db.close()
    return {"ok": True}

@router.post("/holidays", dependencies=[Depends(admin_guard)])
def add_holiday(payload: dict):
    db = SessionLocal()
    h = Holiday(date=payload.get('date'), name=payload.get('name'), active=payload.get('active', True))
    db.add(h)
    db.commit()
    db.refresh(h)
    db.close()
    return {"ok": True, "id": h.id}

class BusinessHoursIn(BaseModel):
    weekday: int  # 0..6
    open_time: str  # "08:00"
    close_time: str # "18:00"
    active: bool = True

class SpecialHoursIn(BaseModel):
    date: str  # "YYYY-MM-DD"
    open_time: str | None = None
    close_time: str | None = None
    note: str | None = None
    active: bool = True

# Business hours CRUD
@router.post("/business_hours", dependencies=[Depends(admin_guard)])
def create_business_hours(payload: BusinessHoursIn):
    db = SessionLocal()
    ot = datetime.strptime(payload.open_time, "%H:%M").time()
    ct = datetime.strptime(payload.close_time, "%H:%M").time()
    row = BusinessHours(weekday=payload.weekday, open_time=ot, close_time=ct, active=payload.active)
    db.add(row)
    db.commit()
    db.refresh(row)
    db.close()
    return {"ok": True, "id": row.id}

@router.get("/business_hours", dependencies=[Depends(admin_guard)])
def list_business_hours():
    db = SessionLocal()
    rows = db.query(BusinessHours).all()
    db.close()
    return rows

@router.post("/special_hours", dependencies=[Depends(admin_guard)])
def create_special_hours(payload: SpecialHoursIn):
    db = SessionLocal()
    ot = datetime.strptime(payload.open_time, "%H:%M").time() if payload.open_time else None
    ct = datetime.strptime(payload.close_time, "%H:%M").time() if payload.close_time else None
    row = SpecialHours(date=payload.date, open_time=ot, close_time=ct, note=payload.note, active=payload.active)
    db.add(row)
    db.commit()
    db.refresh(row)
    db.close()
    return {"ok": True, "id": row.id}

@router.get("/special_hours", dependencies=[Depends(admin_guard)])
def list_special_hours():
    db = SessionLocal()
    rows = db.query(SpecialHours).all()
    db.close()
    return rows
