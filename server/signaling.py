from flask_socketio import Namespace, emit, join_room
from flask import request
from .storage import get_or_create_chat, add_message, list_messages
from .utils import make_cid

class ChatNS(Namespace):
    def __init__(self, ns):
        super().__init__(ns)

    def on_connect(self): pass

    def on_join(self, data):
        room = data.get('chat_id'); name = data.get('name')
        get_or_create_chat(room, name, make_cid)
        join_room(room)
        # mevcut geçmişi sadece katılana gönder
        msgs = list_messages(room)
        emit('chat:history', msgs, room=request.sid)

    def on_send(self, data):
        room = data.get('chat_id')
        role = data.get('role','user'); type_ = data.get('type','text')
        text = data.get('text'); media_url = data.get('media_url')
        m = add_message(room, role, type_, text, media_url)
        payload = dict(role=role, type=type_, text=text, media_url=media_url, time=data.get('time'))
        # Odaya yayın (gönderen hariç)
        emit('chat:message', payload, to=room, include_self=False)
        # Telegram'a basit forward (yalnızca text)
        if type_ == 'text' and text:
            try:
                from .telegram_bot import send_text_for_room
                send_text_for_room(room, text)
            except Exception:
                pass

class CallNS(Namespace):
    def __init__(self, ns):
        super().__init__(ns)

    def on_join(self, data): join_room(data['chat_id'])

    def on_call_ring(self, data):
        emit('call:incoming', {'chat_id': data['chat_id'], 'fromName': data.get('from')},
             to=data['chat_id'], include_self=False)

    def on_call_accept(self, data): emit('call:accepted', {'chat_id': data['chat_id']}, to=data['chat_id'])
    def on_call_decline(self, data): emit('call:declined', {'chat_id': data['chat_id']}, to=data['chat_id'])
    def on_rtc_offer(self, data):    emit('rtc:offer', data, to=data['chat_id'], include_self=False)
    def on_rtc_answer(self, data):   emit('rtc:answer', data, to=data['chat_id'], include_self=False)
    def on_rtc_candidate(self, data):emit('rtc:candidate', data, to=data['chat_id'], include_self=False)
    def on_call_end(self, data):     emit('call:ended', {'chat_id': data['chat_id']}, to=data['chat_id'])
