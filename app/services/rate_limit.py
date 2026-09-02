from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from app.config import settings


_events: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()


def reset_rate_limits() -> None:
    with _lock:
        _events.clear()


def is_rate_limited(key: str) -> bool:
    now = monotonic()
    cutoff = now - settings.rate_limit_window_seconds
    with _lock:
        bucket = _events[key]
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= settings.rate_limit_requests:
            return True
        bucket.append(now)
        return False
