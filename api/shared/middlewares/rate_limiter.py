from fastapi.responses import JSONResponse
from fastapi import Request, status
from redis.asyncio import Redis
from dotenv import load_dotenv
import time
import os

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
CALLS = int(os.getenv("RATE_LIMIT_CALLS", 5))
PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", 60))

redis = Redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


async def rate_limit_middleware(request: Request, call_next):
    """
    Currently, this is a simple rate limiter that uses Redis to track requests.
    It limits the number of requests per client per method and route within a specified period. (So that when frontend calls the API for multiple rates, it does not get rate limited)
    """
    if (
        request.url.path.startswith(("/docs", "/redoc", "/openapi.json", "/ws"))
        or request.headers.get("upgrade") == "websocket"
    ):
        return await call_next(request)

    client = request.client.host
    method = request.method
    route = request.url.path
    window = int(time.time() // PERIOD)
    key = f"rate:{client}:{window}:{method}:{route}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, PERIOD)

    if count > CALLS:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": f"Too many requests to {method} {route}"},
        )

    response = await call_next(request)
    reset_ts = (window + 1) * PERIOD
    remaining = max(CALLS - count, 0)
    response.headers.update(
        {
            "X-RateLimit-Limit": str(CALLS),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_ts),
        }
    )
    return response
