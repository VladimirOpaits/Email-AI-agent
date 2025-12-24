import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD")
IMAP_MAILBOX = os.getenv("IMAP_MAILBOX", "INBOX")
REDIS_BASE_URL = os.getenv("REDIS_BASE_URL", "redis://localhost:6379/0")

CELERY_BROKER_URL = f"{REDIS_BASE_URL}/0"
CELERY_RESULT_BACKEND = f"{REDIS_BASE_URL}/1"

