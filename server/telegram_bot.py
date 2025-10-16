from flask import Blueprint, request
import requests
from .config import cfg
from .storage import SessionLocal, ChatSession, Message
from datetime import datetime

tg_bp = Blueprint("tg", __name__)
API = lambda method: f"https://api.telegram.org/bot{cfg.TELEGRAM_BOT_TOKEN}/{method}"

def send_text(text: str, thread_id: int | None = None):
    if not cfg.TELEGRAM_BOT_TOKEN or not cfg.TELEGRAM_ADMIN_CHAT_ID: 
        return {"ok": False, "reason":"missing token/chat id"}
    payload = {"chat_id": cfg.TELEGRAM_ADMIN_CHAT_ID, "text": text}
    if thread_id:
        payload["message_thread_id"] = thread_id
    try:
        requests.post(API("sendMessage"), json=payload, timeout=10)
    except Exception:
        pass
    return {"ok": True}

def send_text_for_room(room: str, text: str):
    """Müşteri mesajını Telegram'a CID etiketi ile gönder"""
    with SessionLocal() as s:
        chat = s.query(ChatSession).filter_by(room=room).first()
        if not chat:
            return {"ok": False, "reason": "chat not found"}
        tag = f"[CID: {chat.cid}]"
        customer = chat.customer_name or "Misafir"
    return send_text(f"{tag} {customer}: {text}")

@tg_bp.post("/webhook")
def webhook():
    upd = request.get_json(silent=True) or {}
    msg = upd.get("message") or upd.get("channel_post")
    if not msg: return {"ok": True}
    text = msg.get("text","")
    cid = None
    if "[CID:" in text:
        try: cid = text.split("[CID:")[1].split("]")[0].strip()
        except: pass
    if not cid: return {"ok": True}
    # İlgili chat'i bul ve admin mesajı olarak kaydet
    with SessionLocal() as s:
        chat = s.query(ChatSession).filter_by(cid=cid).first()
        if not chat: return {"ok": True}
        m = Message(chat_id=chat.id, role="admin", type="text", text=text, created_at=datetime.utcnow())
        s.add(m); s.commit()
    # Not: Socket.IO yayını eklemek istersen app içinden erişim tasarlanabilir.
    return {"ok": True}
