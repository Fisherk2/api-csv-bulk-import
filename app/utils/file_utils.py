"""File utility functions for size validation."""

from __future__ import annotations


def validate_file_size(size: int, max_mb: int = 10) -> bool:
    """Validate that file size does not exceed the maximum.

    Args:
        size: File size in bytes.
        max_mb: Maximum allowed file size in megabytes (default: 10).

    Returns:
        True if file size is within limit, False otherwise.
    """
    return size <= max_mb * 1024 * 1024
