import logging
import time

from fastapi import Request

logger = logging.getLogger("lmi.auth")


async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    logger.info("%s %s — %s (%.2fs)", request.method, request.url.path, response.status_code, elapsed)
    return response
