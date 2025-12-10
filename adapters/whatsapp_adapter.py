import requests, time
from config import settings
from utils.logger import logger

class WhatsAppAdapter:
    def __init__(self):
        self.token = settings.WHATSAPP_TOKEN
        self.phone_number_id = settings.PHONE_NUMBER_ID
        if not self.token or not self.phone_number_id:
            raise RuntimeError("WhatsApp credentials not configured")
        self.base = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{self.phone_number_id}"

    def _headers(self):
        t = self.token
        if not t.startswith("Bearer"):
            t = f"Bearer {t}"
        return {"Authorization": t, "Content-Type": "application/json"}

    def send_text(self, to_phone, text):
        url = f"{self.base}/messages"
        payload = {"messaging_product": "whatsapp", "to": to_phone, "type": "text", "text": {"body": text}}
        return self._post_with_retry(url, payload)

    def send_template(self, to_phone, template_name, language="es_ES", components=None):
        url = f"{self.base}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "template",
            "template": {"name": template_name, "language": {"code": language}}
        }
        if components:
            payload["template"]["components"] = components
        return self._post_with_retry(url, payload)

    def _post_with_retry(self, url, payload):
        headers = self._headers()
        for attempt in range(3):
            r = requests.post(url, json=payload, headers=headers, timeout=15)
            if r.status_code in (200,201):
                return r.json()
            logger.warning(f"WhatsApp send status={r.status_code} body={r.text}")
            if r.status_code in (401,403):
                raise Exception("Authentication error sending WhatsApp message")
            time.sleep((attempt+1)*1.5)
        return None
