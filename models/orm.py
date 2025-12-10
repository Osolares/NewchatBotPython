from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, JSON
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
    platform = Column(String, index=True)
    platform_id = Column(String, index=True)
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

class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    platform = Column(String, nullable=True)
    language = Column(String, default="es")
    title = Column(String, nullable=True)
    body = Column(Text)
    components = Column(JSON, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Holiday(Base):
    __tablename__ = "holidays"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    name = Column(String)
    active = Column(Boolean, default=True)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)
    platform_id = Column(String, index=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)
    state = Column(String, default="open")
    meta = Column(JSON, nullable=True)

class UserState(Base):
    __tablename__ = "user_state"
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)
    platform_id = Column(String, index=True)
    current_flow = Column(String, nullable=True)
    step = Column(String, nullable=True)
    data = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
