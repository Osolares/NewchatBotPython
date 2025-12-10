import requests
from config import settings
from utils.logger import logger


BASE = "https://api.telegram.org/bot"


class TelegramAdapter:
def __init__(self, token=None):
self.token = token or settings.TELEGRAM_BOT_TOKEN
if not self.token:
raise RuntimeError("TELEGRAM_BOT_TOKEN not configured")
self.api = f"{BASE}{self.token}"


def send_message(self, chat_id, text, parse_mode="Markdown"):
url = f"{self.api}/sendMessage"
payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
try:
r = requests.post(url, json=payload, timeout=15)
if r.status_code == 200:
return r.json()
logger.warning(f"Telegram send_message status={r.status_code} body={r.text}")
except Exception as e:
logger.warning(f"Telegram error: {e}")
return None


def send_typing(self, chat_id):
url = f"{self.api}/sendChatAction"
try:
requests.post(url, json={"chat_id": chat_id, "action": "typing"}, timeout=5)
except Exception as e:
logger.warning(f"send_typing error: {e}")


def parse_update(self, update_json):
message = update_json.get("message", {}) or update_json.get("edited_message", {})
text = message.get("text") or message.get("caption", "")
chat_id = message.get("chat", {}).get("id")
user = message.get("from", {})
return chat_id, text, user