import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from .config import cfg
from .storage import init_db, list_test_schedules, add_test_schedule, update_test_schedule, delete_test_schedule, list_chats, list_messages, delete_messages
from .signaling import ChatNS, CallNS
from .scheduler import start_scheduler, refresh_jobs
from .telegram_bot import tg_bp
from .testsuite import run_all_tests_and_report
from .repair import run_repair
from .logger import setup_logging
from .middleware import rate_limit, security_headers

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'), template_folder=os.path.join(BASE_DIR, 'templates'))
app.config['SECRET_KEY'] = cfg.SECRET_KEY

# CORS ve güvenlik
ALLOWED = [o.strip() for o in cfg.ALLOWED_ORIGINS.split(',') if o.strip()]

@app.after_request
def cors_and_security(resp):
    # CORS
    o = request.headers.get('Origin')
    if o in ALLOWED or '*' in ALLOWED:
        resp.headers['Access-Control-Allow-Origin'] = o if o in ALLOWED else '*'
        resp.headers['Vary'] = 'Origin'
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    # Güvenlik header'ları
    resp = security_headers(resp)
    
    # CSP
    csp = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.socket.io 'unsafe-inline'; "
        "connect-src 'self' wss: ws: https:; "
        "img-src 'self' data: blob:; "
        "media-src 'self' blob:; "
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self' data:; "
        "object-src 'none'; "
        "base-uri 'self'"
    )
    resp.headers['Content-Security-Policy'] = csp
    
    return resp

# Socket.IO
socketio = SocketIO(app, cors_allowed_origins=ALLOWED, async_mode='threading')

# Blueprints
app.register_blueprint(tg_bp, url_prefix="/tg")

# Pages
@app.get("/")
def index(): return render_template("index.html")

@app.get("/admin")
def admin(): return render_template("admin.html")

@app.get("/test")
def test(): return render_template("test.html")

@app.get("/health")
def health(): return {"ok": True}

# Admin API
from .storage import list_chats, list_messages, delete_messages

@app.get("/api/admin/chats")
def api_admin_chats():
    """Bekleyen sohbetler listesi (eski→yeni)"""
    return jsonify(list_chats())

@app.get("/api/admin/messages")
def api_admin_messages():
    """Belirli bir sohbetin mesaj geçmişi"""
    room = request.args.get("room")
    return jsonify(list_messages(room) if room else [])

@app.post("/api/admin/messages/delete")
def api_admin_delete():
    """Mesajları sil (tekil/çoklu)"""
    data = request.get_json() or {}
    room = data.get("room"); all_msgs = data.get("all", True); ids = data.get("ids")
    cnt = delete_messages(room, all_msgs=all_msgs, ids=ids)
    return {"deleted": cnt}

# Test schedule API
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
    return jsonify(row.to_dict() if row else {"ok":False})

@app.delete("/api/test/schedule/<int:rid>")
def del_sched(rid):
    delete_test_schedule(rid); refresh_jobs(); return {"ok": True}

# Test/Repair
@app.post("/api/test/run")
@rate_limit(max_requests=5, window=300)  # 5 dakikada 5 test
def run_tests_now():
    app.logger.info("Manual test run initiated")
    res = run_all_tests_and_report()
    return {"ok": True, "results": res}

@app.post("/api/repair/run")
@rate_limit(max_requests=3, window=600)  # 10 dakikada 3 repair
def run_repair_now():
    app.logger.info("Manual repair run initiated")
    return run_repair()

# Socket namespaces (SPEC'e göre socketio parametresi kaldırıldı)
socketio.on_namespace(ChatNS('/chat'))
socketio.on_namespace(CallNS('/call'))

def main():
    # Logging kurulumu
    logger = setup_logging(app)
    logger.info("Starting Destek Admin application")
    
    # Veritabanı ve scheduler
    init_db()
    start_scheduler()
    
    # Uygulama başlat
    port = int(os.environ.get("PORT", "10000"))
    logger.info(f"Server starting on port {port}")
    
    socketio.run(
        app, 
        host="0.0.0.0", 
        port=port,
        debug=os.getenv('FLASK_ENV') != 'production'
    )

if __name__ == "__main__":
    main()
