"""Customer domain entity — pure business logic, no framework dependencies.

Represents a customer with name and email contact information.
This is a DDD entity, not a database model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Customer:
    """Domain entity representing a customer.

    Equality is based on identity (id), not attributes.
    Customers are uniquely identified by their UUID, while the
    email serves as a business key for batch import deduplication.
    """

    name: str
    email: str
    id: UUID = field(default_factory=uuid4)
