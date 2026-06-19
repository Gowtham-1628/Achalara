"""Strategy model"""
from sqlalchemy import Column, String, Text, Index, func
from sqlalchemy.orm import relationship
import uuid
from app.models.base import BaseModel


class Strategy(BaseModel):
    """Firm-wide investment strategy definition.

    A reusable way of investing (e.g. "Growth", "Income"). Applied to an account
    via a Sleeve; trades and positions hang off the sleeve, not the strategy.

    Names are unique case-insensitively (see ``uq_strategy_name_lower``) so that
    "Growth" and "growth" resolve to a single definition.
    """

    __tablename__ = "strategies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)

    __table_args__ = (Index("uq_strategy_name_lower", func.lower(name), unique=True),)

    sleeves = relationship("Sleeve", back_populates="strategy")

    def __repr__(self):
        return f"<Strategy(id={self.id}, name={self.name})>"
