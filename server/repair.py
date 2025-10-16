def run_repair():
    from .storage import SessionLocal, ChatSession, Message
    from datetime import datetime, timedelta
    
    repaired_items = []
    
    # Eski inactive chat'leri temizle (30 günden eski)
    try:
        with SessionLocal() as s:
            threshold = datetime.utcnow() - timedelta(days=30)
            old_chats = s.query(ChatSession).filter(ChatSession.created_at < threshold, ChatSession.active == False).all()
            for chat in old_chats:
                s.delete(chat)
            s.commit()
            repaired_items.append(f"Eski {len(old_chats)} chat temizlendi")
    except Exception as e:
        repaired_items.append(f"Chat temizlik hatası: {str(e)}")
    
    # Silinmiş mesajları fiziksel olarak temizle (opsiyonel)
    try:
        with SessionLocal() as s:
            deleted_msgs = s.query(Message).filter(Message.deleted == True).all()
            count = len(deleted_msgs)
            for msg in deleted_msgs:
                s.delete(msg)
            s.commit()
            repaired_items.append(f"{count} silinmiş mesaj temizlendi")
    except Exception as e:
        repaired_items.append(f"Mesaj temizlik hatası: {str(e)}")
    
    return {"repaired": True, "notes": repaired_items}
