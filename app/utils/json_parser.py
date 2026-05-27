"""JSON parser for batch upload body.

Normalizes JSON input into a list of dictionaries compatible
with Pydantic schema validation.
"""

from __future__ import annotations

import json
from typing import Any


def parse_json(content: str | dict[str, Any]) -> list[dict[str, Any]]:
    """Parse JSON content into a list of dictionaries.

    Args:
        content: JSON string or already-parsed dict.

    Returns:
        List of order dictionaries from the 'orders' key.

    Raises:
        ValueError: If JSON is malformed, missing 'orders' key,
                    or orders is not a list.
    """
    if isinstance(content, str):
        try:
            data: dict[str, Any] = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON: {exc}") from exc
    else:
        data = content

    if not isinstance(data, dict):
        raise ValueError("JSON body must be an object")

    if "orders" not in data:
        raise ValueError("JSON body must contain 'orders' key")

    orders = data["orders"]
    if not isinstance(orders, list):
        raise ValueError("'orders' must be a list")

    return orders
