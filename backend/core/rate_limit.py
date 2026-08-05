from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request, status


class InMemoryRateLimiter:
    """单进程保护层；公网部署仍需在网关/WAF配置共享限流。"""

    def __init__(self) -> None:
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = monotonic()
        cutoff = now - window_seconds
        with self._lock:
            bucket = self._requests[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                retry_after = max(1, int(bucket[0] + window_seconds - now))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="请求过于频繁，请稍后再试",
                    headers={"Retry-After": str(retry_after)},
                )
            bucket.append(now)


auth_rate_limiter = InMemoryRateLimiter()
external_rate_limiter = InMemoryRateLimiter()


def auth_request_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    endpoint = request.url.path.rsplit("/", 1)[-1]
    if endpoint == "register":
        auth_rate_limiter.check(f"register:{client_ip}", limit=20, window_seconds=300)
    else:
        auth_rate_limiter.check(f"login:{client_ip}", limit=20, window_seconds=60)


def external_request_limit(request: Request) -> None:
    """限制会消耗高德配额的入口，公网多实例部署需在网关使用共享限流。"""
    client_ip = request.client.host if request.client else "unknown"
    external_rate_limiter.check(f"external:{client_ip}", limit=30, window_seconds=60)
