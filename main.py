from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import create_tables, get_db
from exceptions import NoMatchingSlugError
from schemas import LongUrlAccept, LongUrlReturn, ShortUrlReturn
from services.long_url import get_long_url
from services.short_url import create_short_url

app: FastAPI = FastAPI(title=settings.app_name)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    await create_tables()
    yield


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
