import time
from collections import defaultdict
from typing import Dict


class SimpleRateLimiter:
def __init__(self, calls=20, period=60):
self.calls = calls
self.period = period
self.store: Dict[str, list] = defaultdict(list)


def allow(self, key: str) -> bool:
now = time.time()
window = now - self.period
arr = self.store[key]
while arr and arr[0] < window:
arr.pop(0)
if len(arr) < self.calls:
arr.append(now)
self.store[key] = arr
return True
return False


rate_limiter = SimpleRateLimiter(calls=20, period=60)