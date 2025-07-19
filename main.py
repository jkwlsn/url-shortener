import asyncio

from dotenv import dotenv_values
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import Identity, Integer, String
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

"""Get settings from .env"""
SETTINGS: dict[str, str | None] = {**dotenv_values(dotenv_path=".env")}

"""Construct database connection string"""
db: dict[str, str | None] = {
    "host": SETTINGS["POSTGRES_HOST"],
    "port": SETTINGS["POSTGRES_PORT"],
    "user": SETTINGS["POSTGRES_USER"],
    "password": SETTINGS["POSTGRES_PASSWORD"],
    "dbname": SETTINGS["POSTGRES_DB"],
}

DATABASE_URL: str = f"postgresql+psycopg_async://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['dbname']}"

""" Establish async connection to database """
asyncio_engine: AsyncEngine = create_async_engine(url=DATABASE_URL, echo=True)

async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=asyncio_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

"""SQLAlchemy models"""


class Base(DeclarativeBase):
    pass


class Link(Base):
    __tablename__ = "links"

    link_id: Mapped[int] = mapped_column(
        Integer, Identity(always=True), primary_key=True
    )
    slug: Mapped[str] = mapped_column(String(), unique=True, index=True, nullable=False)
    long_url: Mapped[str] = mapped_column(String(), unique=True, nullable=False)

    def __repr__(self) -> str:
        return (
            f"Link(link_id={self.link_id}, slug={self.slug}, long_url={self.long_url})"
        )


"""Pydantic models"""


class LongUrlAccept(BaseModel):
    long_url: HttpUrl = Field(min_length=15)


class SlugAccept(BaseModel):
    slug: str = Field(pattern=r"^[A-Za-z0-9]{7}$")


class LongUrlReturn(BaseModel):
    long_url: HttpUrl


class ShortUrlReturn(BaseModel):
    short_url: HttpUrl


def main() -> None:
    pass


if __name__ == "__main__":
    main()
