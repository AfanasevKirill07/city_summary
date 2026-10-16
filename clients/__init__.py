"""Clients for external APIs."""

from .http import (
    ExternalServiceError,
    ExternalServiceUnavailable,
    NotFoundError,
    get_json,
)

__all__ = [
    "ExternalServiceError",
    "ExternalServiceUnavailable",
    "NotFoundError",
    "get_json",
]