# services/woocommerce_service.py
from config import settings
import requests
from utils.logger import logger

class WooCommerceService:
    def __init__(self):
        self.base = settings.WC_URL
        self.ck = settings.WC_CONSUMER_KEY
        self.cs = settings.WC_CONSUMER_SECRET

    def list_promotions(self, limit=5):
        try:
            url = f"{self.base}/wp-json/wc/v3/products?per_page={limit}"
            r = requests.get(url, auth=(self.ck, self.cs), timeout=15)
            r.raise_for_status()
            items = r.json()
            return [{"name": i.get("name"), "price": i.get("price")} for i in items]
        except Exception as e:
            logger.warning(f"WooCommerce error: {e}")
            return []
