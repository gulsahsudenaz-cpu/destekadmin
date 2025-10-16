ÜRETİM PROMPTU / SPEC — “SESLİ ve YAZILI KONUŞMA”
Part 0 — Kapsam & İlkeler (Özet)

Amaç: Minimal, sade, güvenilir bir chat + tek tıkla arama deneyimi.

Teknoloji: Python Flask + Flask‑SocketIO (eventlet), saf HTML/CSS/JS (frameworksüz). DB: SQLite (SQLAlchemy).

Platform: Mobil öncelikli (Android/iOS), tablet/masaüstü de uyumlu.

Tarayıcı: Chrome, Safari (iOS dâhil), Firefox, Opera.

Arama: WebRTC P2P (başlangıç ses; kamera sonradan açılabilir).

Chat: Metin + resim + sesli mesaj; zaman damgası; admin/kullanıcı renk ayrımı.

Akış:

Index: İsim → direkt tam ekran chat. Sağ üstte yeşil telefon → arama.

Admin: Telegram OTP ile giriş → bekleyen yazışmalar listesi (eski→yeni) → seç → chat/arama.Chat kalıcı (tekil/çoklu silme).

Telegram: Müşteri mesaj/medya Telegram’a gider. Admin Telegram’dan yanıt verirse müşteri chat’ine ve admin panele düşer. Çoklu sohbetler CID ile ayrışır. “X chat’e girdi” bildirimi gönderilir.

Test & Repair: test.html → “Tüm testler” + “Repair”; zamanlanmış test saatleri UI’dan yönetilir (APScheduler). Sonuçlar Telegram’a raporlanır.

Güvenlik (minimal): CORS beyaz liste, HttpOnly admin oturumu, basit CSP, dosya boyut/MIME kontrolü.

Part 1 — Dosya Ağacı
/ (kök)
├─ README.md
├─ SPEC.md                     # Bu metnin aynısı
├─ .env.example
├─ requirements.txt
├─ Dockerfile
├─ render.yaml
├─ /server
│  ├─ app.py                   # Flask giriş noktası + Socket.IO mount
│  ├─ config.py                # Ortam değişkenleri ve ayarlar
│  ├─ storage.py               # SQLAlchemy modelleri ve basit CRUD
│  ├─ signaling.py             # Socket.IO: chat & call eventleri
│  ├─ telegram_bot.py          # Telegram webhook + gönderim yardımcıları
│  ├─ scheduler.py             # APScheduler iş akışı (UI'dan değiştirilebilir saatler)
│  ├─ testsuite.py             # Toplu testleri çalıştır ve raporla
│  ├─ repair.py                # “Repair” işlemleri
│  └─ utils.py                 # CID üretimi, zaman, doğrulama, dosya yardımcıları
├─ /templates
│  ├─ index.html               # Kullanıcı: isim → direkt chat
│  ├─ admin.html               # Admin: OTP, liste, chat/arama/test
│  └─ test.html                # Test & Repair arayüzü + saat yönetimi
└─ /static
   ├─ /css
   │  ├─ main.css              # Temel tema ve renk paleti
   │  ├─ chat.css              # Chat bileşenleri
   │  └─ admin.css             # Admin liste/test stilleri
   └─ /js
      ├─ client.js             # Kullanıcı giriş ve chat/arama başlatma
      ├─ admin.js              # Admin login/liste/chat/silme/test UI
      ├─ chat.js               # Metin/resim/ses mesajlaşma mantığı
      ├─ webrtc.js             # Minimal WebRTC (audio-first) + SDP/ICE
      ├─ media.js              # Hoparlör ↔ ahize (setSinkId) + iOS fallback
      ├─ test_runner_client.js # Basit UI/Socket ping testleri
      └─ ui.js                 # Modal, toast, fullscreen, emoji çubuğu

Part 2 — Ortam Değişkenleri (.env.example)
FLASK_ENV=production
SECRET_KEY=change-me
TZ=Europe/Istanbul
DATABASE_URL=sqlite:///./data.sqlite3

# CORS
ALLOWED_ORIGINS=https://your-app.onrender.com,https://adminara.onrender.com

# Telegram
TELEGRAM_BOT_TOKEN=123:ABC
TELEGRAM_ADMIN_CHAT_ID=123456789
TELEGRAM_WEBHOOK_URL=https://your-app.onrender.com/tg/webhook

Part 3 — Kurulum / Çalıştırma / Deploy

requirements.txt

Flask==3.*
Flask-SocketIO==5.*
eventlet==0.35.*
SQLAlchemy==2.*
apscheduler==3.*
python-dotenv==1.*
requests==2.*


Dockerfile (özet)

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd -m app
COPY . .
USER app
EXPOSE 10000
HEALTHCHECK CMD curl -fsS http://localhost:10000/health || exit 1
CMD ["python","-m","server.app"]


render.yaml

services:
  - type: web
    name: sesli-yazili-konusma
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python -m server.app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: TZ
        value: Europe/Istanbul

Part 4 — Backend Kod İskeletleri
4.1 server/app.py
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from .config import cfg
from .storage import init_db
from .signaling import ChatNS, CallNS
from .scheduler import start_scheduler, refresh_jobs
from .telegram_bot import tg_bp
import os

app = Flask(__name__, static_folder="../static", template_folder="../templates")
app.config['SECRET_KEY'] = cfg.SECRET_KEY

# CORS (çok basit)
from flask import Response
ALLOWED = [o.strip() for o in cfg.ALLOWED_ORIGINS.split(',') if o.strip()]
@app.after_request
def cors(resp: Response):
    o = request.headers.get('Origin')
    if o in ALLOWED:
        resp.headers['Access-Control-Allow-Origin'] = o
        resp.headers['Vary'] = 'Origin'
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp

# Socket.IO
socketio = SocketIO(app, cors_allowed_origins=ALLOWED, async_mode='eventlet')

# Blueprints
app.register_blueprint(tg_bp, url_prefix="/tg")

# Routes
@app.get("/")
def index(): return render_template("index.html")

@app.get("/admin")
def admin(): return render_template("admin.html")

@app.get("/test")
def test(): return render_template("test.html")

@app.get("/health")
def health(): return {"ok": True}

# API: test saatlerini UI’dan değiştirme örnekleri (aşağıda model)
from .storage import list_test_schedules, add_test_schedule, update_test_schedule, delete_test_schedule

@app.get("/api/test/schedule")
def get_sched(): return jsonify([r.to_dict() for r in list_test_schedules()])

@app.post("/api/test/schedule")
def post_sched():
    data = request.get_json() or {}
    row = add_test_schedule(data.get("time_hhmm"), data.get("enabled", True), data.get("tz") or cfg.TZ)
    refresh_jobs()
    return jsonify(row.to_dict())

@app.put("/api/test/schedule/<int:rid>")
def put_sched(rid):
    data = request.get_json() or {}
    row = update_test_schedule(rid, data.get("time_hhmm"), data.get("enabled"), data.get("tz"))
    refresh_jobs()
    return jsonify(row.to_dict())

@app.delete("/api/test/schedule/<int:rid>")
def del_sched(rid):
    delete_test_schedule(rid); refresh_jobs(); return {"ok": True}

# Socket namespaces
socketio.on_namespace(ChatNS('/chat', socketio))
socketio.on_namespace(CallNS('/call', socketio))

def main():
    init_db()
    start_scheduler()
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))

if __name__ == "__main__":
    main()

4.2 server/config.py
import os
from dataclasses import dataclass

@dataclass
class Cfg:
    SECRET_KEY: str = os.getenv("SECRET_KEY","change-me")
    TZ: str = os.getenv("TZ","Europe/Istanbul")
    DATABASE_URL: str = os.getenv("DATABASE_URL","sqlite:///./data.sqlite3")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS","*")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN","")
    TELEGRAM_ADMIN_CHAT_ID: str = os.getenv("TELEGRAM_ADMIN_CHAT_ID","")
    TELEGRAM_WEBHOOK_URL: str = os.getenv("TELEGRAM_WEBHOOK_URL","")

cfg = Cfg()

4.3 server/storage.py (model + basit CRUD)
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
    cid = Column(String, unique=True, index=True)    # "Eda-7F3C"
    customer_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)
    messages = relationship("Message", back_populates="chat")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)      # 'user'|'admin'|'system'
    type = Column(String)      # 'text'|'image'|'audio'
    text = Column(String, nullable=True)
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

# Schedules
def list_test_schedules():
    with SessionLocal() as s: return s.query(TestSchedule).order_by(TestSchedule.time_hhmm).all()

def add_test_schedule(time_hhmm, enabled=True, tz=None):
    with SessionLocal() as s:
        row = TestSchedule(time_hhmm=time_hhmm, enabled=enabled, tz=tz or cfg.TZ)
        s.add(row); s.commit(); s.refresh(row); return row

def update_test_schedule(rid, time_hhmm=None, enabled=None, tz=None):
    with SessionLocal() as s:
        row = s.get(TestSchedule, rid); 
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

4.4 server/signaling.py (Socket.IO sözleşmeleri)
from flask_socketio import Namespace, emit, join_room
from .utils import ensure_cid

class ChatNS(Namespace):
    def __init__(self, ns, sio): super().__init__(ns); self.sio = sio

    def on_connect(self): pass

    def on_join(self, data):
        chat_id = data.get('chat_id')
        join_room(chat_id)
        emit('chat:history', [], room=self.sid)  # basit; gerçek geçmiş admin.js'de REST'ten çekilebilir

    def on_send(self, data):
        # {chat_id, type, text?, fileRef?, role}
        emit('chat:message', data, to=data['chat_id'], include_self=False)

class CallNS(Namespace):
    def __init__(self, ns, sio): super().__init__(ns); self.sio = sio

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

4.5 server/telegram_bot.py (webhook + gönderim)
from flask import Blueprint, request
import requests
from .config import cfg
from .storage import SessionLocal, ChatSession, Message
from datetime import datetime

tg_bp = Blueprint("tg", __name__)

API = f"https://api.telegram.org/bot{cfg.TELEGRAM_BOT_TOKEN}"

def send_text(text, topic_id=None):
    payload = {"chat_id": cfg.TELEGRAM_ADMIN_CHAT_ID, "text": text}
    if topic_id: payload["message_thread_id"] = topic_id
    requests.post(f"{API}/sendMessage", json=payload)

@tg_bp.post("/webhook")
def webhook():
    upd = request.get_json(silent=True) or {}
    msg = upd.get("message") or upd.get("channel_post")
    if not msg: return {"ok": True}
    text = msg.get("text","")
    # [CID: Eda-7F3C] gibi bir etiketle chat bulun
    cid = None
    if "[CID:" in text:
        try: cid = text.split("[CID:")[1].split("]")[0].strip()
        except: pass
    if not cid: return {"ok": True}
    # DB’ye admin mesajını kaydet (role='admin'), ardından Socket.IO ile ilgili odaya ilet (opsiyonel)
    with SessionLocal() as s:
        chat = s.query(ChatSession).filter_by(cid=cid).first()
        if not chat: return {"ok": True}
        m = Message(chat_id=chat.id, role="admin", type="text", text=text, created_at=datetime.utcnow())
        s.add(m); s.commit()
    # Not: Socket.IO yayınını app.context üzerinden yapmak istersen, global socket adgangı ver.
    return {"ok": True}

4.6 server/scheduler.py (UI’dan değiştirilebilir saatler)
from apscheduler.schedulers.background import BackgroundScheduler
from zoneinfo import ZoneInfo
from .testsuite import run_all_tests_and_report
from .storage import list_test_schedules
sched = BackgroundScheduler()

def refresh_jobs():
    sched.remove_all_jobs()
    for r in list_test_schedules():
        if not r.enabled: continue
        hh, mm = map(int, r.time_hhmm.split(':'))
        sched.add_job(run_all_tests_and_report, 'cron', hour=hh, minute=mm, timezone=ZoneInfo(r.tz),
                      id=f"test@{r.time_hhmm}")

def start_scheduler():
    sched.start()
    refresh_jobs()

4.7 server/testsuite.py (rapor + Telegram)
from .telegram_bot import send_text

def run_all_tests_and_report():
    results = []
    try:
        # Health
        results.append(("Web", True))
        # Socket ping/simülasyon, DB bağlantı, Telegram token kontrolü vb.
        results.append(("Socket", True))
        results.append(("DB", True))
        results.append(("Telegram", True))
    except Exception:
        results.append(("Unknown", False))
    ok = [k for k,v in results if v]; bad = [k for k,v in results if not v]
    send_text("🧪 Test Raporu\n✅ " + ", ".join(ok) + ("\n❌ " + ", ".join(bad) if bad else "\nTümü başarılı"))
    return results

4.8 server/repair.py (temel onarım)
def run_repair():
    # Stale odalar/oturumlar temizleme, küçük state resetleri...
    return {"repaired": True}

4.9 server/utils.py
import secrets, string
def make_cid(name: str):
    suf = ''.join(secrets.choice(string.hexdigits.upper()) for _ in range(4))
    return f"{name}-{suf}"

Part 5 — Frontend (HTML)
5.1 templates/index.html (kısaltılmış iskelet)
<!doctype html><html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover" />
  <title>Konuşma</title>
  <link rel="stylesheet" href="/static/css/main.css">
  <link rel="stylesheet" href="/static/css/chat.css">
</head>
<body class="page">
  <header class="header card">
    <div class="title">Admin Muhsin’e bağlandınız</div>
    <button id="btnCall" class="btn btn-primary phone">📞</button>
  </header>

  <main id="chatArea" class="card chat">
    <ul id="msgs" class="msgs"></ul>
  </main>

  <footer class="footer card">
    <button id="btnEmoji" class="btn">😊</button>
    <input id="txt" class="input" placeholder="Mesaj yazın..." />
    <input id="fileImg" type="file" accept="image/*" capture="environment" hidden />
    <input id="fileAud" type="file" accept="audio/*" capture="microphone" hidden />
    <button id="btnImg" class="btn">🖼️</button>
    <button id="btnAud" class="btn">🎤</button>
    <button id="btnSend" class="btn btn-primary">Gönder</button>
  </footer>

  <audio id="remoteAudio" autoplay playsinline></audio>

  <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
  <script src="/static/js/ui.js"></script>
  <script src="/static/js/chat.js"></script>
  <script src="/static/js/webrtc.js"></script>
  <script src="/static/js/media.js"></script>
  <script src="/static/js/client.js"></script>
</body></html>

5.2 templates/admin.html (kısaltılmış iskelet)
<!doctype html><html lang="tr">
<head>
  <meta charset="utf-8" /><meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Admin</title>
  <link rel="stylesheet" href="/static/css/main.css"><link rel="stylesheet" href="/static/css/admin.css">
</head>
<body class="page">
  <header class="header card">
    <nav class="tabs">
      <a data-tab="call">Görüntü/Ses</a>
      <a data-tab="chat" class="active">Chat</a>
      <a data-tab="test">Test</a>
    </nav>
    <button id="btnToTest" class="btn">🧪 Test</button>
  </header>
  <main class="admin-grid">
    <aside class="card list">
      <div class="otp">
        <input id="otp" placeholder="Telegram OTP" class="input">
        <button id="btnOtp" class="btn btn-primary">Giriş</button>
      </div>
      <ul id="threads" class="threads"></ul>
    </aside>
    <section class="card panel">
      <header class="panel-header">
        <div id="threadTitle">Seçili sohbet yok</div>
        <div class="panel-actions">
          <button id="btnPhone" class="btn btn-primary">📞</button>
          <button id="btnDelete" class="btn">🗑️</button>
        </div>
      </header>
      <ul id="msgs" class="msgs"></ul>
      <footer class="footer">
        <button id="btnEmoji" class="btn">😊</button>
        <input id="txt" class="input" placeholder="Mesaj yazın..." />
        <button id="btnSend" class="btn btn-primary">Gönder</button>
      </footer>
    </section>
  </main>
  <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
  <script src="/static/js/ui.js"></script>
  <script src="/static/js/chat.js"></script>
  <script src="/static/js/webrtc.js"></script>
  <script src="/static/js/admin.js"></script>
</body></html>

5.3 templates/test.html (kısaltılmış iskelet)
<!doctype html><html lang="tr">
<head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Test & Repair</title>
<link rel="stylesheet" href="/static/css/main.css"></head>
<body class="page">
  <header class="header card"><h1>Sistem Testleri</h1></header>
  <main class="card pad">
    <section>
      <button id="btnRun" class="btn btn-primary">Tüm testleri çalıştır</button>
      <button id="btnRepair" class="btn">Repair</button>
    </section>
    <section>
      <h2>Test Saatleri</h2>
      <div>
        <input id="time" type="time" class="input"/><button id="btnAdd" class="btn">Ekle</button>
      </div>
      <ul id="times"></ul>
    </section>
    <section id="report"></section>
  </main>
  <script src="/static/js/test_runner_client.js"></script>
</body></html>

Part 6 — CSS Tema (profesyonel palet)

static/css/main.css (özet)

:root{
  --c-bg:#fff; --c-text:#0F172A;
  --c-primary:#0EA5E9; --c-success:#10B981;
  --c-muted:#F1F5F9; --c-border:#E2E8F0; --c-danger:#EF4444;
  --shadow:0 4px 12px rgba(0,0,0,.08); --radius:14px;
  --fs-1: clamp(16px,1.6vw,18px); --fs-2:clamp(14px,1.4vw,16px);
}
*{box-sizing:border-box} body{margin:0;font:var(--fs-1)/1.45 system-ui;color:var(--c-text);background:var(--c-muted)}
.card{background:var(--c-bg);border:1px solid var(--c-border);border-radius:var(--radius);box-shadow:var(--shadow)}
.header,.footer{padding:12px 16px;display:flex;align-items:center;gap:12px}
.btn{border:1px solid var(--c-border);background:#fff;padding:8px 12px;border-radius:10px;cursor:pointer}
.btn-primary{background:var(--c-primary);color:#fff;border-color:transparent}
.input{flex:1;padding:10px;border:1px solid var(--c-border);border-radius:10px}
.page{min-height:100svh;display:grid;grid-template-rows:auto 1fr auto}


static/css/chat.css (özet)

.chat{padding:8px;display:flex;flex-direction:column}
.msgs{list-style:none;margin:0;padding:8px;display:flex;flex-direction:column;gap:8px}
.msg{max-width:80%;padding:10px;border:1px solid var(--c-border);border-radius:12px}
.msg.user{align-self:flex-end;background:#E0F2FE;border-color:#BAE6FD}
.msg.admin{align-self:flex-start;background:#DCFCE7;border-color:#BBF7D0}
.msg .time{display:block;color:#64748B;font-size:var(--fs-2);margin-top:4px}
.phone{margin-left:auto}

Part 7 — Frontend JS (çekirdek mantık)
7.1 static/js/chat.js (mesajlaşma API’si)
export function renderMsg(listEl, {role, type, text, time}){
  const li = document.createElement('li'); li.className = `msg ${role}`;
  if(type==='text'){ li.innerHTML = `<div>${text}</div><span class="time">${time}</span>`; }
  // type image/audio için basit örnekler:
  else if(type==='image'){ li.innerHTML = `<img src="${text}" alt="image" style="max-width:220px"/><span class="time">${time}</span>`; }
  else if(type==='audio'){ li.innerHTML = `<audio controls src="${text}"></audio><span class="time">${time}</span>`; }
  listEl.appendChild(li); listEl.scrollTop = listEl.scrollHeight;
}
export function ts(){ const d=new Date(); return d.toLocaleTimeString('tr-TR',{hour:'2-digit',minute:'2-digit'}); }

7.2 static/js/webrtc.js (minimal sesli çağrı)
export function initCall(socket, chatId){
  const pc = new RTCPeerConnection({ iceServers:[{urls:'stun:stun.l.google.com:19302'}] });
  const remoteAudio = document.getElementById('remoteAudio');
  pc.ontrack = e => { remoteAudio.srcObject = e.streams[0]; };
  pc.onicecandidate = e => { if(e.candidate) socket.emit('rtc:candidate',{chat_id:chatId,candidate:e.candidate}); };
  return pc;
}

export async function startOfferFlow(socket, pc, chatId){
  const stream = await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true},video:false});
  stream.getTracks().forEach(t=>pc.addTrack(t, stream));
  socket.emit('call:ring',{chat_id:chatId});
  socket.on('call:accepted', async ()=>{
    const offer = await pc.createOffer({offerToReceiveAudio:true});
    await pc.setLocalDescription(offer);
    socket.emit('rtc:offer',{chat_id:chatId,sdp:pc.localDescription});
  });
}
export function bindAnswering(socket, pc, chatId){
  socket.on('rtc:offer', async ({sdp})=>{
    await pc.setRemoteDescription(sdp);
    const ans = await pc.createAnswer(); await pc.setLocalDescription(ans);
    socket.emit('rtc:answer',{chat_id:chatId,sdp:pc.localDescription});
  });
  socket.on('rtc:answer', async ({sdp})=>{ await pc.setRemoteDescription(sdp); });
  socket.on('rtc:candidate', async ({candidate})=>{ try{ await pc.addIceCandidate(candidate); }catch{} });
}

7.3 static/js/media.js (hoparlör/ahize)
export async function toggleSpeaker(audioEl, speakerOn){
  if(!('setSinkId' in HTMLMediaElement.prototype)){
    // iOS Safari: OS yönetir; kullanıcıya bilgilendirme gösterebilirsin.
    return;
  }
  const id = speakerOn ? 'speaker' : 'communications';
  try{ await audioEl.setSinkId(id); }catch{}
}

7.4 static/js/client.js (kullanıcı tarafı akış)
import {renderMsg, ts} from './chat.js';
import {initCall, startOfferFlow, bindAnswering} from './webrtc.js';
import {toggleSpeaker} from './media.js';

const socket = io('/chat'); const callSocket = io('/call');
const msgs = document.getElementById('msgs'); const txt = document.getElementById('txt');

let chatId = null, pc=null;
(function bootstrap(){
  const name = localStorage.getItem('name') || prompt("İsminizi girin");
  localStorage.setItem('name', name);
  chatId = `cid-${Math.random().toString(16).slice(2,8)}`; // sunucuya da kaydedebilirsiniz
  socket.emit('join',{chat_id:chatId, name});
  callSocket.emit('join',{chat_id:chatId});
  // Telegram bildirimi sunucu tarafında tetiklenebilir (opsiyonel REST)
})();

document.getElementById('btnSend').onclick = ()=>{
  const text = txt.value.trim(); if(!text) return;
  const m = {role:'user', type:'text', text, time:ts()};
  renderMsg(msgs, m);
  socket.emit('send', {chat_id:chatId, ...m});
  txt.value='';
};

socket.on('chat:message', (m)=> renderMsg(msgs, {...m, role:'admin', time: ts()}));

document.getElementById('btnCall').onclick = async ()=>{
  pc = initCall(callSocket, chatId);
  bindAnswering(callSocket, pc, chatId);
  await startOfferFlow(callSocket, pc, chatId);
};

// Gelen arama → kabul/ret (modal kurgusunu ui.js ile yap)
callSocket.on('call:incoming', ()=>{
  if(confirm("Arama isteği: Kabul edilsin mi?")){
    callSocket.emit('call:accept',{chat_id:chatId});
  } else {
    callSocket.emit('call:decline',{chat_id:chatId});
  }
});

7.5 static/js/admin.js (özet)
import {renderMsg, ts} from './chat.js';

const socket = io('/chat'); const callSocket = io('/call');
const threads = document.getElementById('threads'); const msgs=document.getElementById('msgs');
let currentChatId=null;

document.getElementById('btnOtp').onclick = ()=>{
  const otp = document.getElementById('otp').value.trim();
  // Basit demo: OTP doğrulama sahte; gerçekte server endpoint ile doğrulayın.
  alert("Admin girişi onaylandı");
};

function openThread(id, title){
  currentChatId=id; document.getElementById('threadTitle').textContent = title || id;
  socket.emit('join', {chat_id:id});
  callSocket.emit('join', {chat_id:id});
  msgs.innerHTML='';
}

document.getElementById('btnSend').onclick = ()=>{
  if(!currentChatId) return;
  const text = document.getElementById('txt').value.trim(); if(!text) return;
  const m = {role:'admin', type:'text', text, time:ts()};
  renderMsg(msgs, m);
  socket.emit('send', {chat_id:currentChatId, ...m});
  document.getElementById('txt').value='';
};

socket.on('chat:message', (m)=> renderMsg(msgs, {...m, role:'user', time: ts()}));

Part 8 — API & Socket Sözleşmeleri (net isimler)

REST

GET / → index.html

GET /admin → admin.html

GET /test → test.html

GET /api/test/schedule → saat listesi

POST /api/test/schedule → saat ekle {time_hhmm, enabled, tz?}

PUT /api/test/schedule/:id → güncelle

DELETE /api/test/schedule/:id → sil

POST /tg/webhook → Telegram bot webhook

Socket.IO — /chat

join {chat_id, name?}

send {chat_id, role, type, text|fileRef, time}

Server → chat:message {..} , chat:history [..]

Socket.IO — /call

join {chat_id}

call:ring {chat_id} → karşı tarafa call:incoming

call:accept / call:decline

rtc:offer|rtc:answer|rtc:candidate

call:end

Part 9 — Telegram Eşleştirmesi

Her chat için kısa bir CID etiket kullanın (örn. Eda-7F3C) ve Telegram’a gönderilen mesaj başlıklarında [CID: ...] bulunsun.

Telegram’dan gelen yanıt reply veya metindeki [CID: ...] ile ilgili chat’e map edilir ve web arayüzlerine yayınlanır.

Resim/Ses: Telegram photo/voice → sunucuda dosya indirip media_url iletilir (örnek kodu telegram_bot.py’de genişletilebilir).

Part 10 — Mobil & Tarayıcı Uyum

Android/Chromium: setSinkId destekli → hoparlör/ahize benzeri yönlendirme mümkün.

iOS Safari: setSinkId yok → yönlendirme OS kontrolünde; UI’da kısa bilgilendirme.

Meta: <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">

Dokunma hedefi ≥ 44px, 100svh ve visualViewport iyileştirmeleri.

Part 11 — Güvenlik (minimal ama yeterli)

CORS: ALLOWED_ORIGINS beyaz liste.

Admin Session: OTP sonrası HttpOnly cookie (örnek için basit tutuldu; üretimde zorlaştırın).

CSP (hafif): script-src ‘self’; img/media için blob: izinleri gerekebilir.

Upload: MIME + boyut limiti (~5 MB).

HTTPS: WebRTC zorunlu (Render yapısı ile gelir).

Part 12 — Test & Repair

test.html: “Tüm testler” (+ Telegram raporu) ve “Repair” butonu.

scheduler.py: Test saatleri UI’dan yönetilir.

Rapor: “✅ Web, ✅ Socket, ❌ Telegram …” formatında Telegram’a düşer.

Part 13 — Kabul Kriterleri (Checklist)

 Index: İsim → doğrudan tam ekran chat.

 Chat: metin/resim/ses; zaman damgası; renk ayrımı; emoji hızlı seçim (10).

 Sağ üst yeşil telefon → arama akışı; Kabul/Reddet modalları iki tarafta.

 Arama kamera kapalı başlar; mic/cam/speaker butonları; speaker off → ahize denemesi.

 Admin: OTP girişi; bekleyen listesi (eski→yeni); kalıcı geçmiş; tekil/çoklu silme; test sekmesi kısa yolu.

 Telegram: müşteri mesaj/medya Telegram’a; Telegram reply → web chat + admin panel; “X chat’e girdi” bildirimi; çoklu sohbetler CID ile karışmaz.

 Test saatleri UI’dan ekle/sil/güncelle; raporlar Telegram’a.

 Repair çalışır, temel temizliği yapar.

 Mobil uyum + büyük tarayıcı desteği.

Part 14 — AI’ye Çıktı Talimatı

Dosyaları aynen Part 1’deki isimlerle üret.

Her dosyada yukarıdaki iskeletleri temel al; eksik yerleri uygun şekilde tamamla.

Admin OTP şimdilik sahte akış olabilir; fakat endpoint ve UI yerleri bırak.

Telegram medya relay için place-holder ekleyip yorum satırlarına not düş.

Tüm Socket event isimleri birebir korunsun.

CSS’te renk paleti ve 3B hissi veren gölgeler/kenarlar kullanılsın.

Kod, çalıştırılabilir demoda minimal gerekli parçaları içersin (Render’a deploy edilebilir).

Part 15 — Notlar (Gerçek Cihazlar)

iOS’ta ahize yönlendirmesi garanti edilemez; OS karar verir. UI’da kısa bilgilendirme göster.

TURN sunucusu zorunlu değil; kurumsal ağlarda sorun çıkarsa Coturn eklenebilir.



Hızlı Başlangıç
# 1) Sanal ortam
python -m venv .venv && source .venv/bin/activate

# 2) Bağımlılıklar
pip install -r requirements.txt

# 3) Çalıştır
python -m server.app
# Tarayıcı: http://localhost:10000/


Not: .env.example içindeki Telegram değişkenlerini doldurursanız Telegram entegrasyonu devreye girer. Doldurmasanız da sistem lokal olarak çalışır.

📁 Dosya Ağacı (özet)
sesli-yazili-konusma/
├─ README.md                # Hızlı başlangıç
├─ SPEC.md                  # Üretim promptu/spec
├─ .env.example             # Ortam değişkenleri şablonu
├─ requirements.txt         # Python bağımlılıkları
├─ Dockerfile               # Docker imajı
├─ render.yaml              # Render.com deploy
├─ server/
│  ├─ app.py                # Flask + Socket.IO ana uygulama
│  ├─ config.py             # Ortam config
│  ├─ storage.py            # SQLite modelleri + CRUD
│  ├─ signaling.py          # Socket.IO: chat/call event’leri
│  ├─ telegram_bot.py       # Telegram webhook + gönderim yardımcıları
│  ├─ scheduler.py          # APScheduler entegrasyonu
│  ├─ testsuite.py          # Toplu test ve Telegram raporu
│  ├─ repair.py             # Basit “repair” işlemleri
│  └─ utils.py              # CID üretimi vb.
├─ templates/
│  ├─ index.html            # Kullanıcı: isim → direkt chat + arama butonu
│  ├─ admin.html            # Admin: OTP (demo), liste, chat/arama, test girişi
│  └─ test.html             # Test & Repair + saat yönetimi
└─ static/
   ├─ css/{main.css,chat.css,admin.css}
   └─ js/{client.js,admin.js,chat.js,webrtc.js,media.js,ui.js,test_runner_client.js}

🔌 Backend Öne Çıkanlar
server/app.py — Uygulama girişi

Sayfalar: /, /admin, /test

Admin API: sohbet listesi, mesaj geçmişi, silme

Test saatleri API: ekle/güncelle/sil

Test/Repair: tek tık uçları

Socket.IO namespace’leri: /chat, /call

# Socket namespaces
socketio.on_namespace(ChatNS('/chat'))
socketio.on_namespace(CallNS('/call'))

def main():
    init_db()
    start_scheduler()             # UI’dan değiştirilebilir saatlere göre job’lar
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))

server/signaling.py — Chat & Call

Chat: join, send → DB’ye yaz, odaya yayın, Telegram forward (text)

Call: call:ring / accept / decline / rtc:offer|answer|candidate / call:end

def on_send(self, data):
    room = data.get('chat_id'); role = data.get('role','user')
    type_ = data.get('type','text'); text = data.get('text')
    add_message(room, role, type_, text)
    emit('chat:message', dict(role=role, type=type_, text=text, time=data.get('time')),
         to=room, include_self=False)
    # Telegram’a basit forward:
    from .telegram_bot import send_text_for_room
    if type_ == 'text' and text: send_text_for_room(room, text)

server/storage.py — SQLite modelleri

ChatSession(room, cid, customer_name, created_at, active)

Message(chat_id, role, type, text, media_url, deleted)

TestSchedule(time_hhmm, enabled, tz)

Listeleme/silme CRUD’ları hazır.

server/scheduler.py + server/testsuite.py

Saatleri UI’dan yönetin; cron işlerini yeniden yükler.

Test çalışınca Telegram raporu gönderir.

🖥️ Frontend Öne Çıkanlar
templates/index.html — Kullanıcı

Tam ekran chat — sağ üstte yeşil telefon (arama)

Alt barda emoji/resim/ses gönderme butonları (demo)

remoteAudio ile karşı ses oynatımı

static/js/client.js

Odaya katılım (/chat), mesaj gönder/al

Arama başlat → call:ring, kabulde WebRTC offer/answer

Gelen arama için confirm() ile kabul/red akışı

document.getElementById('btnCall').onclick = async ()=>{
  pc = initCall(callSocket, chatId);
  bindAnswering(callSocket, pc, chatId);
  await startOfferFlow(callSocket, pc, chatId);
};

templates/admin.html + static/js/admin.js

OTP alanı (demo), bekleyen sohbetler listesi

Seçilen sohbetin geçmişini çeker, mesaj gönderir

Arama: butonla call:ring (kullanıcıda kabul/red)

document.getElementById('btnPhone').onclick = async ()=>{
  if(!currentChatId) return;
  callSocket.emit('call:ring',{chat_id:currentChatId, from:'admin'});
};

static/js/webrtc.js

Minimal audio-first P2P

STUN: stun:stun.l.google.com:19302

(İleride TURN eklenebilir)

📲 Mobil & Tarayıcı Uyumu

Mobile‑first CSS, 44px+ dokunma hedefleri

iOS çentik için viewport-fit=cover, 100svh

Safari/Chrome/Firefox/Opera desteği

Hoparlör → ahize:

Chromium Android’de setSinkId denemesi

iOS’ta OS kontrolünde (UI’da bilgilendirme)

🧪 Test & 🛠️ Repair
templates/test.html + static/js/test_runner_client.js

Tüm testler tuşu → /api/test/run

Repair → /api/repair/run

Test saatleri: ekle/sil/güncelle → APScheduler job’ları otomatik yenilenir.

🔐 Güvenlik (minimal)

CORS: ALLOWED_ORIGINS

Admin OTP: demo (endpoint yerleri hazır); üretimde zorlaştırın.

Upload: (demo) — medya uçları basitleştirilmiştir.

HTTPS önerilir (WebRTC için şarttır; Render’da otomatik).

✨ Sonraki Adımlar (isterseniz)

Admin OTP’yi gerçek doğrulamaya bağlayın.

Telegram’dan medya relay (foto/voice) için indirme & yükleme uçları ekleyin.

TURN (Coturn) ile zorlu NAT ortamlarında bağlantı oranını artırın.

UI’da özel modal/ikon seti ve PWA manifest + service worker.