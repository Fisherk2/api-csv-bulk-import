"""Rate limiter configuration for slowapi.

Provides the global ``Limiter`` instance and a custom IP extraction
function that works behind reverse proxies (Nginx).

The ``Limiter`` is module-level so the ``@limiter.limit()`` decorator
can be applied to endpoint functions at definition time (before routes
are registered with Starlette's router). This is the only reliable
way to apply per-route rate limits with slowapi + Starlette 1.x.
"""

from __future__ import annotations

from fastapi import Request
from slowapi import Limiter

from app.config import settings


def get_real_ip(request: Request) -> str:
    """Extract the real client IP behind a reverse proxy.

    Reads the ``X-Forwarded-For`` header set by Nginx (or any upstream proxy).
    Falls back to ``request.client.host`` for direct connections.

    Returns:
        The client IP address as a string.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "127.0.0.1"


# Module-level limiter instance — used by both main.py (app.state.limiter)
# and auth.py (@limiter.limit() decorator).
# Global limits are only applied when RATE_LIMIT_PER_MINUTE > 0.
limits: list[str] = []
if settings.RATE_LIMIT_PER_MINUTE > 0:
    limits.append(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")

limiter = Limiter(
    key_func=get_real_ip,
    default_limits=limits,  # type: ignore[arg-type]
    headers_enabled=True,
)
