"""Batch validation error value object — pure domain, no framework deps.

Represents a single validation error from batch processing
with row number and error message.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BatchValidationError:
    """Domain value object for a batch validation error.

    Contains the 1-indexed row number and a descriptive error message.
    This is a pure domain object — infrastructure layer converts it
    to the appropriate HTTP schema (BatchErrorDetailSchema).
    """

    row_number: int
    message: str
