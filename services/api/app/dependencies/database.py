"""FastAPI dependency for acquiring database sessions."""

from typing import Generator, Optional
from sqlalchemy.orm import Session
from ..core.database import get_db

__all__ = ["get_db"]
