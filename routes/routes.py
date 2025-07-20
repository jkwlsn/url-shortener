"""FastAPI Routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from exceptions.exceptions import LinkExpiredError, NoMatchingSlugError
from schemas.schemas import LongUrlAccept, ShortUrlReturn
from services.url import UrlService

router = APIRouter()


@router.get("/")
async def read_root() -> dict:
    return {"message": "Nice day for a picnic!"}


@router.post("/shorten")
async def return_short_url(
    payload: LongUrlAccept, db: Annotated[AsyncSession, Depends(get_db)]
) -> ShortUrlReturn:
    try:
        short_url: str = await UrlService().create_short_url(
            db=db, long_url=str(payload.long_url)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error") from e
    return ShortUrlReturn(short_url=short_url)  # type: ignore


@router.get("/{slug}")
async def return_long_url(
    slug: str, db: Annotated[AsyncSession, Depends(get_db)]
) -> RedirectResponse:
    try:
        long_url: str | None = await UrlService().get_long_url(db=db, slug=slug)
    except NoMatchingSlugError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except LinkExpiredError as e:
        raise HTTPException(status_code=410, detail=str(e)) from e
    return RedirectResponse(url=long_url if long_url else "/")
