# utils/security.py
import hmac
import hashlib
from config import settings
from typing import Optional

def verify_x_hub_signature(payload_bytes: bytes, signature_header: Optional[str]) -> bool:
    """
    Valida X-Hub-Signature-256 (firma de Facebook) para webhooks.
    """
    if not signature_header or not settings.FACEBOOK_APP_SECRET:
        return False
    try:
        expected = signature_header.split("sha256=")[1]
    except Exception:
        return False
    digest = hmac.new(settings.FACEBOOK_APP_SECRET.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, expected)
