"""Core HTTP middlewares for request tracking and logging."""

import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .logging import logger


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware attaching a unique request ID to each incoming request,
    measuring response duration, and setting X-Request-ID response header.
    """
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.time()
        logger.debug(f"Request started: {request.method} {request.url.path} [ID: {request_id}]")

        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            response.headers["X-Request-ID"] = request_id
            logger.debug(
                f"Request completed: {request.method} {request.url.path} "
                f"Status: {response.status_code} Duration: {duration_ms}ms [ID: {request_id}]"
            )
            return response
        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"Error: {exc} Duration: {duration_ms}ms [ID: {request_id}]"
            )
            raise
