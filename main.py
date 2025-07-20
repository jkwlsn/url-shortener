import secrets
import string

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, HttpUrl, SecretStr, field_validator
from pydantic_core import Url
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Identity, Integer, String, select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = FastAPI()


""" Pydantic settings """


class Settings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(env_file=".env", frozen=True)
    app_name: str = "Jake's URL Shortener"
    base_url: HttpUrl = "https://jkwlsn.dev/"  # type: ignore
    slug_length: int = 7
    max_url_length: int = 2048
    min_url_length: int = 15
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str


settings: Settings = Settings()

""" Database Connection String """

DATABASE_URL: str = f"postgresql+psycopg_async://{settings.postgres_user}:{settings.postgres_password.get_secret_value()}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

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
        String(length=settings.max_url_length), unique=True, nullable=False
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
        if len(long_url) > settings.max_url_length:
            raise ValueError(too_long)
        if len(long_url) < settings.min_url_length:
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
        slug: str = generate_slug(settings.slug_length)
        slug_exists: Link | None = await db.scalar(
            select(Link).where(Link.slug == slug)
        )
        if not slug_exists:
            return slug


async def generate_short_url(db: AsyncSession, long_url: str) -> str:
    slug: str = await generate_unique_slug(db)
    link = Link(slug=slug, long_url=long_url)
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return f"{settings.base_url}{slug}"


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


@app.post("/shorten")
async def create_short_url(payload: LongUrlAccept) -> ShortUrlReturn:
    async with async_session() as session:
        short_url: str = await generate_short_url(
            db=session, long_url=str(payload.long_url)
        )
    return ShortUrlReturn(short_url=short_url)  # type: ignore


@app.get("/{slug}")
async def return_long_url(slug: str) -> RedirectResponse:
    async with async_session() as session:
        try:
            long_url: str | None = await get_long_url(db=session, slug=slug)
            return RedirectResponse(long_url)
        except NoMatchingSlugError as e:
            raise HTTPException(status_code=404, detail="No link found") from e


def main() -> None:
    pass


if __name__ == "__main__":
    main()
