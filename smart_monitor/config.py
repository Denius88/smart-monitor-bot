import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")

DB_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./monitor.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()