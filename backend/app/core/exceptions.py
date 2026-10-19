"""Custom application exceptions mapped to HTTP responses."""
from __future__ import annotations

from fastapi import HTTPException, status


class AutomataException(HTTPException):
    """Base for all Automata-specific HTTP errors."""


class UnauthorizedException(AutomataException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(AutomataException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(AutomataException):
    def __init__(self, detail: str = "Not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictException(AutomataException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class PlanLimitException(AutomataException):
    """Raised when a user has reached their plan limit."""
    def __init__(self, detail: str = "Plan limit reached"):
        super().__init__(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=detail)


class UsageLimitException(AutomataException):
    """Raised when monthly post quota is exhausted."""
    def __init__(self, detail: str = "Monthly post limit reached"):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)
