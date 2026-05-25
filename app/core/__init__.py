"""Core domain layer — pure business logic with zero external dependencies.

This layer MUST NOT import from SQLAlchemy, FastAPI, or any HTTP library.
It contains entities, repository interfaces (ports), and domain services.
"""
