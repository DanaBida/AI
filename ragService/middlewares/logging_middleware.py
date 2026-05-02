"""Logging middleware for request/response logging."""

from __future__ import annotations

import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next):
        """
        Log incoming requests and outgoing responses.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or endpoint handler

        Returns:
            Response: The HTTP response
        """
        start_time = time.perf_counter()
        client_host = request.client.host if request.client else "unknown"

        logger.info("Incoming request %s %s from %s", request.method, request.url.path, client_host)

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        logger.info(
            "Completed request %s %s with status %s in %.3fs",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )

        return response
