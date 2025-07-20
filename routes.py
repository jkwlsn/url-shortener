"""FastAPI Routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from exceptions import NoMatchingSlugError
from schemas import LongUrlAccept, LongUrlReturn, ShortUrlReturn
from services.long_url import get_long_url
from services.short_url import create_short_url

router = APIRouter()


@router.get("/")
async def read_root() -> dict:
    return {"message": "Nice day for a picnic!"}


@router.post("/shorten")
async def return_short_url(
    payload: LongUrlAccept, db: Annotated[AsyncSession, Depends(get_db)]
) -> ShortUrlReturn:
    try:
        short_url: str = await create_short_url(db=db, long_url=str(payload.long_url))
        return ShortUrlReturn(short_url=short_url)  # type: ignore
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error") from e


@router.get("/{slug}")
async def return_long_url(
    slug: str, db: Annotated[AsyncSession, Depends(get_db)]
) -> RedirectResponse:
    try:
        long_url: str | None = await get_long_url(db=db, slug=slug)
        return RedirectResponse(long_url)
    except NoMatchingSlugError as e:
        raise HTTPException(status_code=404, detail="No link found") from e
