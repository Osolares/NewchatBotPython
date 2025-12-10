from models.orm import SessionLocal, UserState, Conversation
from datetime import datetime
from utils.logger import logger


class StateManager:
def __init__(self):
pass


def get_state(self, platform, platform_id):
db = SessionLocal()
s = db.query(UserState).filter(UserState.platform==platform, UserState.platform_id==platform_id).first()
if not s:
s = UserState(platform=platform, platform_id=platform_id, current_flow=None, step=None, data={})
db.add(s)
db.commit()
db.refresh(s)
db.close()
return s


def save_state(self, s):
db = SessionLocal()
db.add(s)
db.commit()
db.refresh(s)
db.close()


def clear_state(self, platform, platform_id):
db = SessionLocal()
s = db.query(UserState).filter(UserState.platform==platform, UserState.platform_id==platform_id).first()
if s:
s.current_flow = None
s.step = None
s.data = {}
db.add(s)
db.commit()
db.close()