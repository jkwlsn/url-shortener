import asyncio
import secrets
import string

from dotenv import dotenv_values
from fastapi import FastAPI
from pydantic import BaseModel, Field, HttpUrl, field_validator
from sqlalchemy import Identity, Integer, String, select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = FastAPI()


"""Get settings from .env"""
SETTINGS: dict[str, str | None] = {**dotenv_values(dotenv_path=".env")}

BASE_URL: str = SETTINGS.get("BASE_URL")
SLUG_LENGTH: int = int(SETTINGS.get("SLUG_LENGTH"))
MAX_URL_LENGTH: int = int(SETTINGS.get("MAX_URL_LENGTH"))
MIN_URL_LENGTH: int = int(SETTINGS.get("MIN_URL_LENGTH"))

"""Construct database connection string"""
DB_CONFIG: dict[str, str | None] = {
    "host": SETTINGS["POSTGRES_HOST"],
    "port": SETTINGS["POSTGRES_PORT"],
    "user": SETTINGS["POSTGRES_USER"],
    "password": SETTINGS["POSTGRES_PASSWORD"],
    "dbname": SETTINGS["POSTGRES_DB"],
}

DATABASE_URL: str = f"postgresql+psycopg_async://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

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
    long_url: Mapped[str] = mapped_column(
        String(length=MAX_URL_LENGTH), unique=True, nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"Link(link_id={self.link_id}, slug={self.slug}, long_url={self.long_url})"
        )


"""Pydantic models"""


class LongUrlAccept(BaseModel):
    long_url: HttpUrl

    @field_validator("long_url", mode="before")
    @classmethod
    def validate_length(cls, long_url: str) -> str:
        too_long: str = "URL too long"
        too_short: str = "URL too short"
        if len(long_url) > MAX_URL_LENGTH:
            raise ValueError(too_long)
        if len(long_url) < MIN_URL_LENGTH:
            raise ValueError(too_short)
        return long_url


class SlugAccept(BaseModel):
    slug: str = Field(pattern=r"^[A-Za-z0-9]{7}$")


class LongUrlReturn(BaseModel):
    long_url: HttpUrl


class ShortUrlReturn(BaseModel):
    short_url: HttpUrl


""" Slug / short link service """


def generate_slug(length: int) -> str:
    base62: str = string.ascii_letters + string.digits
    return "".join(secrets.choice(seq=base62) for _ in range(length))


async def generate_unique_slug(db: AsyncSession) -> str:
    while True:
        slug: str = generate_slug(SLUG_LENGTH)
        slug_exists: Link | None = await db.scalar(
            select(Link).where(Link.slug == slug)
        )
        if not slug_exists:
            return slug


async def generate_short_url(db: AsyncSession, long_url: HttpUrl) -> str:
    slug: str = await generate_unique_slug(db)
    link = Link(slug=slug, long_url=long_url)
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return f"{BASE_URL}/{slug}"


class NoMatchingSlugError(Exception):
    def __init__(self, slug: str) -> None:
        super().__init__(f"{slug} does not exist")


async def get_long_url(db: AsyncSession, slug: str) -> str:
    result: Link | None = await db.scalar(select(Link).where(Link.slug == slug))
    if not result:
        raise NoMatchingSlugError(slug)
    return result.long_url


""" FastAPI Routes """


@app.get("/")
async def read_root() -> dict:
    return {"message": "Nice day for a picnic!"}


def main() -> None:
    pass


if __name__ == "__main__":
    main()
