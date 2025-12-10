import requests
from config import settings
from utils.logger import logger

class WooCommerceService:
    def __init__(self):
        self.base = settings.WC_URL.rstrip('/') if settings.WC_URL else None
        self.ck = settings.WC_CONSUMER_KEY
        self.cs = settings.WC_CONSUMER_SECRET

    def list_promotions(self, limit=5):
        try:
            if not self.base:
                return []
            url = f"{self.base}/wp-json/wc/v3/products?per_page={limit}"
            r = requests.get(url, auth=(self.ck, self.cs), timeout=15)
            r.raise_for_status()
            items = r.json()
            return [{"name": i.get("name"), "price": i.get("price")} for i in items]
        except Exception as e:
            logger.warning(f"WooCommerce error: {e}")
            return []

    def search_by_brand_model(self, brand, model, limit=10):
        try:
            if not self.base:
                return []
            term = f"{brand} {model}"
            url = f"{self.base}/wp-json/wc/v3/products?search={term}&per_page={limit}"
            r = requests.get(url, auth=(self.ck, self.cs), timeout=15)
            r.raise_for_status()
            items = r.json()
            return items
        except Exception as e:
            logger.warning(f"WooCommerce search error: {e}")
            return []
