"""RFC 7807 Problem Details schema for standardized error reporting.

All API error responses follow this format for consistency and
interoperability with HTTP clients.
"""

from __future__ import annotations

from pydantic import BaseModel


class ProblemDetailSchema(BaseModel):
    """RFC 7807 Problem Details for HTTP APIs.

    Provides a standardized error response format with machine-readable
    type, human-readable title/details, and optional tracking instance.
    """

    type: str = "about:blank"
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
