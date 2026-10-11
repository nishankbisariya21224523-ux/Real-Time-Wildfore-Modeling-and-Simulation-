"""Centralized domain exceptions and structured error models."""

from typing import Any, Dict, Optional
from fastapi import status


class ForestFireAppException(Exception):
    """Base application exception for all domain and operational errors."""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ResourceNotFoundException(ForestFireAppException):
    """Raised when a requested resource does not exist."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ValidationException(ForestFireAppException):
    """Raised when request payload or parameter validation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class ConflictException(ForestFireAppException):
    """Raised when an operation conflicts with existing system state."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="CONFLICT_ERROR",
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class DatabaseException(ForestFireAppException):
    """Raised when database operations encounter persistence or integrity errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class InvalidGeometryException(ForestFireAppException):
    """Raised when spatial geometry coordinates or WKT/GeoJSON is malformed."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="INVALID_GEOMETRY",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class InvalidParameterException(ForestFireAppException):
    """Raised when a query or path parameter is invalid."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="INVALID_PARAMETER",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class ServiceUnavailableException(ForestFireAppException):
    """Raised when a downstream service (Database, Redis, Celery) is unavailable."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SERVICE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


class NotImplementedException(ForestFireAppException):
    """Raised for future phase endpoints invoked prematurely."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="NOT_IMPLEMENTED",
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            details=details
        )


class ModelUnavailableException(ForestFireAppException):
    """Raised when the requested risk prediction machine learning model is unavailable."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="MODEL_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


class FeatureDataUnavailableException(ForestFireAppException):
    """Raised when model-ready environmental observations are missing for a region/date."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="DATA_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class IgnitionOutsideRegionException(ForestFireAppException):
    """Raised when specified ignition coordinates lie outside the requested region boundary."""
    def __init__(
        self,
        message: str = "Ignition point lies outside the specified region boundary.",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="IGNITION_OUTSIDE_REGION",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


