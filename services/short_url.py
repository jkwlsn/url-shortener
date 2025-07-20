import secrets
import string

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models import Link

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
