"""SQLAlchemy Models"""

from datetime import datetime

from sqlalchemy import DateTime, Identity, Integer, String
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from config.config import settings


class Base(DeclarativeBase):
    pass


class Link(Base):
    __tablename__ = "links"

    link_id: Mapped[int] = mapped_column(
        Integer, Identity(always=True), primary_key=True
    )
    slug: Mapped[TEXT] = mapped_column(
        String(), unique=True, index=True, nullable=False
    )
    long_url: Mapped[TEXT] = mapped_column(
        String(length=settings.max_url_length), nullable=False
    )
    created_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"Link(link_id={self.link_id}, slug={self.slug}, long_url={self.long_url})"
        )
