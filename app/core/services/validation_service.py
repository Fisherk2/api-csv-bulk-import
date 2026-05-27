"""ValidationService — pure domain service for batch validation.

Validates raw data dicts against a Pydantic schema and returns tuples of
(valid_items, validation_errors) for partial processing support.
ZERO external dependencies — imports only from stdlib and app/core/.
"""

from __future__ import annotations

from typing import Any

from app.core.entities.validation import BatchValidationError


class ValidationService:
    """Domain service for batch data validation.

    Validates each item in a batch independently against a schema.
    Valid items are collected; invalid items produce batch validation
    errors with row_number for client-side identification.

    The schema parameter is any object with a model_validate(data) method
    (typically a Pydantic BaseModel subclass). ValidationErrors (which
    inherit from ValueError in Pydantic v2) are caught and converted.
    """

    @staticmethod
    def validate_batch(
        data: list[dict[str, Any]],
        schema: Any,
    ) -> tuple[list[Any], list[BatchValidationError]]:
        """Validate a batch of raw data dicts against a schema.

        Args:
            data: List of raw dicts to validate.
            schema: Object with model_validate(data) method (e.g., Pydantic schema).

        Returns:
            Tuple of (valid_items, validation_errors). Row numbers are 1-indexed.
        """
        valid: list[Any] = []
        errors: list[BatchValidationError] = []

        for row_number, item_data in enumerate(data, start=1):
            try:
                validated = schema.model_validate(item_data)
                valid.append(validated)
            except ValueError as exc:
                # Pydantic ValidationError inherits from ValueError in v2
                errors.append(
                    BatchValidationError(
                        row_number=row_number,
                        message=str(exc),
                    )
                )

        return valid, errors
