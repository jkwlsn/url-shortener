import secrets
import string
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import create_tables, get_db
from exceptions import SelfReferencingURLError, URLTooLongError, URLTooShortError
from models import Link

app: FastAPI = FastAPI(title=settings.app_name)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    await create_tables()
    yield


"""Pydantic models"""


class LongUrlAccept(BaseModel):
    long_url: HttpUrl

    @field_validator("long_url", mode="before")
    @classmethod
    def validate_length(cls, long_url: str) -> str:
        if len(long_url) > settings.max_url_length:
            raise URLTooLongError(long_url, settings.max_url_length)
        if len(long_url) < settings.min_url_length:
            raise URLTooShortError(long_url, settings.min_url_length)
        return long_url

    @field_validator("long_url")
    @classmethod
    def validate_reject_same_domain(cls, long_url: HttpUrl) -> HttpUrl:
        if str(long_url.host) in str(settings.base_url):
            raise SelfReferencingURLError(str(long_url))
        return long_url


class LongUrlReturn(BaseModel):
    long_url: HttpUrl


class ShortUrlReturn(BaseModel):
    short_url: HttpUrl


""" Short url service """


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


async def create_short_url(db: AsyncSession, long_url: str) -> str:
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
    return str(result.long_url)


""" FastAPI Routes """


@app.get("/")
async def read_root() -> dict:
    return {"message": "Nice day for a picnic!"}


@app.post("/shorten")
async def return_short_url(
    payload: LongUrlAccept, db: AsyncSession = Depends(get_db)
) -> ShortUrlReturn:
    try:
        short_url: str = await create_short_url(db=db, long_url=str(payload.long_url))
        return ShortUrlReturn(short_url=short_url)  # type: ignore
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error") from e


@app.get("/{slug}")
async def return_long_url(
    slug: str, db: AsyncSession = Depends(get_db)
) -> RedirectResponse:
    try:
        long_url: str | None = await get_long_url(db=db, slug=slug)
        return RedirectResponse(long_url)
    except NoMatchingSlugError as e:
        raise HTTPException(status_code=404, detail="No link found") from e
