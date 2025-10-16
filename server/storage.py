from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from .config import cfg

Base = declarative_base()
engine = create_engine(cfg.DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True)
    room = Column(String, unique=True, index=True)     # WebSocket odası (chat_id)
    cid = Column(String, unique=True, index=True)      # Human-friendly CID (Eda-7F3C)
    customer_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)      # 'user'|'admin'|'system'
    type = Column(String)      # 'text'|'image'|'audio'
    text = Column(String, nullable=True)        # text veya media url
    media_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted = Column(Boolean, default=False)
    chat = relationship("ChatSession", back_populates="messages")

class AdminSession(Base):
    __tablename__ = "admin_sessions"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TestSchedule(Base):
    __tablename__ = "test_schedules"
    id = Column(Integer, primary_key=True)
    time_hhmm = Column(String)         # '10:00'
    enabled = Column(Boolean, default=True)
    tz = Column(String, default=cfg.TZ)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self): return dict(id=self.id, time_hhmm=self.time_hhmm, enabled=self.enabled, tz=self.tz)

def init_db():
    Base.metadata.create_all(engine)

# Schedules CRUD
def list_test_schedules():
    with SessionLocal() as s: return s.query(TestSchedule).order_by(TestSchedule.time_hhmm).all()

def add_test_schedule(time_hhmm, enabled=True, tz=None):
    with SessionLocal() as s:
        row = TestSchedule(time_hhmm=time_hhmm, enabled=enabled, tz=tz or cfg.TZ)
        s.add(row); s.commit(); s.refresh(row); return row

def update_test_schedule(rid, time_hhmm=None, enabled=None, tz=None):
    with SessionLocal() as s:
        row = s.get(TestSchedule, rid)
        if not row: return None
        if time_hhmm is not None: row.time_hhmm = time_hhmm
        if enabled is not None: row.enabled = enabled
        if tz is not None: row.tz = tz
        row.updated_at = datetime.utcnow()
        s.commit(); s.refresh(row); return row

def delete_test_schedule(rid):
    with SessionLocal() as s:
        row = s.get(TestSchedule, rid)
        if row: s.delete(row); s.commit()

# Chat helpers
def get_or_create_chat(room, name, cid_maker):
    with SessionLocal() as s:
        chat = s.query(ChatSession).filter_by(room=room).first()
        if chat:
            return chat
        cid = cid_maker(name or "Misafir")
        chat = ChatSession(room=room, customer_name=name, cid=cid, active=True)
        s.add(chat); s.commit(); s.refresh(chat)
        return chat

def add_message(room, role, type_, text=None, media_url=None):
    with SessionLocal() as s:
        chat = s.query(ChatSession).filter_by(room=room).first()
        if not chat: return None
        m = Message(chat_id=chat.id, role=role, type=type_, text=text, media_url=media_url)
        s.add(m); s.commit(); s.refresh(m); return m

def list_messages(room, limit=200):
    with SessionLocal() as s:
        chat = s.query(ChatSession).filter_by(room=room).first()
        if not chat: return []
        q = s.query(Message).filter(Message.chat_id==chat.id, Message.deleted==False).order_by(Message.created_at.asc())
        return [dict(id=m.id, role=m.role, type=m.type, text=m.text, media_url=m.media_url, created_at=m.created_at.isoformat()) for m in q.limit(limit).all()]

def list_chats(limit=100):
    with SessionLocal() as s:
        q = s.query(ChatSession).order_by(ChatSession.created_at.asc())
        return [dict(room=c.room, cid=c.cid, customer_name=c.customer_name, created_at=c.created_at.isoformat()) for c in q.limit(limit).all()]

def delete_messages(room, all_msgs=True, ids=None):
    with SessionLocal() as s:
        chat = s.query(ChatSession).filter_by(room=room).first()
        if not chat: return 0
        q = s.query(Message).filter(Message.chat_id==chat.id)
        if not all_msgs and ids:
            q = q.filter(Message.id.in_(ids))
        cnt = 0
        for m in q.all():
            m.deleted = True; cnt += 1
        s.commit(); return cnt
