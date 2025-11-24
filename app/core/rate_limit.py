"""Rate limiting utilities with FastAPI-Limiter + in-memory fallback.

If `REDIS_URL` is provided the application will use `fastapi-limiter` with Redis.
Otherwise a simple in-memory rate limiter is used (per-IP + route) suitable for development.
"""
import os
import time
import threading
from typing import Callable, Tuple
from fastapi import Request, HTTPException

_lock = threading.Lock()
_memory_store = {}  # key -> (count, reset_timestamp)
_use_memory = True

def _parse_rate(value: str, default_times: int, default_seconds: int) -> Tuple[int, int]:
    if not value:
        return default_times, default_seconds
    try:
        times_part, window_part = value.split('/')
        times = int(times_part.strip())
        window_part = window_part.strip().lower()
        if window_part.startswith('min'):
            seconds = 60
        elif window_part.startswith('hour'):
            seconds = 3600
        else:
            seconds = default_seconds
        return times, seconds
    except Exception:
        return default_times, default_seconds

def init_config():
    global _use_memory
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            from redis import asyncio as aioredis  # type: ignore
            from fastapi_limiter import FastAPILimiter  # type: ignore
            # Defer actual connection to async init
            _use_memory = False
        except Exception:
            _use_memory = True
    else:
        _use_memory = True

async def init_rate_limiter():
    """Async initialization. Establish Redis connection if configured."""
    init_config()
    if not _use_memory:
        from redis import asyncio as aioredis  # type: ignore
        from fastapi_limiter import FastAPILimiter  # type: ignore
        redis = aioredis.from_url(os.getenv("REDIS_URL"), encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis)

def make_rate_limiter(times: int, seconds: int) -> Callable:
    """Create a dependency callable enforcing the given rate."""
    async def dependency(request: Request):
        if _use_memory:
            now = time.time()
            ip = request.client.host if request.client else 'unknown'
            route = request.url.path
            key = f"{ip}:{route}"
            with _lock:
                count, reset_ts = _memory_store.get(key, (0, now + seconds))
                if now > reset_ts:
                    count = 0
                    reset_ts = now + seconds
                count += 1
                _memory_store[key] = (count, reset_ts)
                if count > times:
                    remaining = int(reset_ts - now)
                    raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Try again in {remaining}s")
        else:
            from fastapi_limiter.depends import RateLimiter  # type: ignore
            # Delegate to fastapi-limiter internal dependency
            limiter = RateLimiter(times=times, seconds=seconds)
            await limiter(request)
    return dependency

# Predefined limit factories using env configuration
def login_rate_limiter():
    times, seconds = _parse_rate(os.getenv("RATE_LIMIT_LOGIN"), 5, 60)
    return make_rate_limiter(times, seconds)

def user_create_rate_limiter():
    times, seconds = _parse_rate(os.getenv("RATE_LIMIT_USER_CREATE"), 10, 3600)
    return make_rate_limiter(times, seconds)

def verify_request_rate_limiter():
    times, seconds = _parse_rate(os.getenv("RATE_LIMIT_VERIFY_REQUEST"), 10, 3600)
    return make_rate_limiter(times, seconds)
