import json
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/vnstock_db")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    _keys_raw = os.getenv("GEMINI_API_KEYS", "[]")
    try:
        GEMINI_API_KEYS = json.loads(_keys_raw)
    except json.JSONDecodeError:
        GEMINI_API_KEYS = []
    GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-2.5-flash")

    CACHE_DIR = os.getenv("CACHE_DIR", "cache")
    CACHE_EXPIRY_DAYS = int(os.getenv("CACHE_EXPIRY_DAYS", "7"))

config = Config()