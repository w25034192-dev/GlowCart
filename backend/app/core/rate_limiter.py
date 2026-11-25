from collections import defaultdict, deque
import threading
import time
from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, max_requests: int, window_seconds: int = 60) -> None:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            bucket = self._buckets[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again shortly.",
                )
            bucket.append(now)

    def reset(self) -> None:
        with self._lock:
            self._buckets.clear()


rate_limiter = SlidingWindowRateLimiter()


def enforce_rate_limit(scope: str, max_requests: int):
    def _dependency(request: Request) -> None:
        client_host = request.client.host if request.client else "unknown"
        rate_limiter.check(f"{scope}:{client_host}", max_requests=max_requests)

    return _dependency

