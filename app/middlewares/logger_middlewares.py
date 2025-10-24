from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
import uuid

from app.utils.logger import log


class LogCorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        incoming_id = request.headers.get("X-Correlation-ID")
        if not incoming_id:
            log.info("No incoming correlation ID found; generating a new one.")
        correlation_id = incoming_id or str(uuid.uuid4())

        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
            path=request.url.path,
            method=request.method
        )

        log.info("request_received")

        try:
            response = await call_next(request)
        except Exception:
            log.error("unhandled_exception", exc_info=True)
            from starlette.responses import JSONResponse
            response = JSONResponse({"detail": "Internal Server Error"}, status_code=500)
            response.headers["X-Correlation-ID"] = correlation_id
            raise
        finally:
            if 'response' in locals():
                response.headers["X-Correlation-ID"] = correlation_id
                log.info("request_completed", status_code=response.status_code)
            structlog.contextvars.clear_contextvars()

        response.headers["X-Correlation-ID"] = correlation_id
        return response
