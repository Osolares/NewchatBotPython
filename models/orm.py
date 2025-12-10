# models/orm.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import datetime

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)        # 'telegram', 'whatsapp'
    platform_id = Column(String, index=True)     # chat_id or phone
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)
    platform_id = Column(String)
    incoming = Column(Boolean, default=True)
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    processed = Column(Boolean, default=False)

class ScheduledMessage(Base):
    __tablename__ = "scheduled_messages"
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String)
    platform_id = Column(String)
    text = Column(Text)
    send_at = Column(DateTime, index=True)
    sent = Column(Boolean, default=False)

def init_db():
    Base.metadata.create_all(bind=engine)
