from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
import uuid

from app.utils.logger import log


# Middleware for correlation ID
class LogCorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
            path=request.url.path
        )
        log.info("request_received")
        try:
            response = await call_next(request)
        except Exception as exc:
            log.error("unhandled_exception", exc_info=True)
            raise
        log.info("request_completed", status_code=response.status_code)
        structlog.contextvars.clear_contextvars()
        return response