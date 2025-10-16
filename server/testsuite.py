from .telegram_bot import send_text

def run_all_tests_and_report():
    results = []
    # Web health check
    try:
        import requests
        r = requests.get('http://localhost:10000/health', timeout=5)
        results.append(("Web", r.status_code == 200))
    except Exception:
        results.append(("Web", False))
    
    # DB check
    try:
        from .storage import SessionLocal
        with SessionLocal() as s:
            s.execute('SELECT 1')
        results.append(("DB", True))
    except Exception:
        results.append(("DB", False))
    
    # Telegram check
    try:
        from .config import cfg
        has_token = bool(cfg.TELEGRAM_BOT_TOKEN and cfg.TELEGRAM_ADMIN_CHAT_ID)
        results.append(("Telegram", has_token))
    except Exception:
        results.append(("Telegram", False))
    
    ok = [k for k,v in results if v]; bad = [k for k,v in results if not v]
    msg = "🧪 Test Raporu\n" + ("✅ " + ", ".join(ok) if ok else "") + (("\n❌ " + ", ".join(bad)) if bad else "\nTümü başarılı")
    send_text(msg)
    return results
