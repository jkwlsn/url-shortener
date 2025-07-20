"""Services for getting long URLs"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import NoMatchingSlugError
from models import Link


async def get_long_url(db: AsyncSession, slug: str) -> str:
    result: Link | None = await db.scalar(select(Link).where(Link.slug == slug))
    if not result:
        raise NoMatchingSlugError(slug)
    return str(result.long_url)
