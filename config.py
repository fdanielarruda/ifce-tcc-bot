import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL', '')
API_TIMEOUT = 10

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

TELEGRAM_CONNECT_TIMEOUT = float(os.getenv('TELEGRAM_CONNECT_TIMEOUT', '60.0'))
TELEGRAM_READ_TIMEOUT = float(os.getenv('TELEGRAM_READ_TIMEOUT', '60.0'))
TELEGRAM_WRITE_TIMEOUT = float(os.getenv('TELEGRAM_WRITE_TIMEOUT', '60.0'))
TELEGRAM_POOL_TIMEOUT = float(os.getenv('TELEGRAM_POOL_TIMEOUT', '60.0'))