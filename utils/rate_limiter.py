# utils/logger.py
import logging
logger = logging.getLogger("multibot")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# utils/rate_limiter.py
import time
from collections import defaultdict
from typing import Dict

class SimpleRateLimiter:
    """
    Token bucket per user in-memory (stateless Redis optional).
    Not permanent across restarts. For production, use Redis.
    """
    def __init__(self, calls=20, period=60):
        self.calls = calls
        self.period = period
        self.store: Dict[str, list] = defaultdict(list)

    def allow(self, key: str) -> bool:
        now = time.time()
        window = now - self.period
        arr = self.store[key]
        # remove old
        while arr and arr[0] < window:
            arr.pop(0)
        if len(arr) < self.calls:
            arr.append(now)
            self.store[key] = arr
            return True
        return False

rate_limiter = SimpleRateLimiter(calls=20, period=60)
