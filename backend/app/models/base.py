"""Base model with common fields"""
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, func


Base = declarative_base()


class BaseModel(Base):
    """Base model class with common fields"""

    __abstract__ = True

    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
