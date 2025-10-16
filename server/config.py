import os
from dataclasses import dataclass

@dataclass
class Cfg:
    SECRET_KEY: str = os.getenv("SECRET_KEY","change-me")
    TZ: str = os.getenv("TZ","Europe/Istanbul")
    DATABASE_URL: str = os.getenv("DATABASE_URL","sqlite:///./data.sqlite3")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS","http://localhost:10000")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN","")
    TELEGRAM_ADMIN_CHAT_ID: str = os.getenv("TELEGRAM_ADMIN_CHAT_ID","")
    TELEGRAM_WEBHOOK_URL: str = os.getenv("TELEGRAM_WEBHOOK_URL","")

cfg = Cfg()
